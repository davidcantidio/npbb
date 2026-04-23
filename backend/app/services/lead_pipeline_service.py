"""Service for Gold pipeline: Silver -> run_pipeline -> insert Gold leads."""

from __future__ import annotations

import asyncio
import contextlib
import csv
from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
import logging
import os
import re
import shutil
import tempfile
import time as time_module
from urllib.parse import urlparse
from datetime import date as date_type, datetime as datetime_type, time as time_type, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only
from sqlmodel import Session, select

import app.db.database as database_module
from app.db.database import build_worker_engine, set_internal_service_db_context
from lead_pipeline.constants import ALL_COLUMNS, TIPO_EVENTO_PADRAO
from lead_pipeline.geo_normalize import normalize_brazilian_locality
from lead_pipeline.normalization import strip_accents
from lead_pipeline.pipeline import (
    PipelineConfig,
    PipelineProgressEvent,
    PipelineResult,
    QualityMetrics,
    run_pipeline,
)
from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.lead_public_models import TipoLead, TipoResponsavel
from app.models.models import (
    Agencia,
    Ativacao,
    AtivacaoLead,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    TipoEvento,
)
from app.modules.leads_publicidade.application.lead_merge_policy import merge_lead_payload_fill_missing
from app.modules.leads_publicidade.application.etl_import.persistence import (
    LeadLookupContext,
    _load_lead_lookup_context,
    find_existing_lead_from_lookup,
    find_lead_by_ticketing_dedupe_key,
    is_ticketing_dedupe_integrity_error,
    merge_lead_lookup_context,
)
from app.services.lead_event_service import ensure_lead_event
from app.services.imports.payload_storage import read_batch_payload
from app.observability.import_events import log_import_event
from app.observability.prometheus_leads_import import observe_gold_stage_duration_seconds
from app.services.imports.file_reader import read_raw_file_rows

logger = logging.getLogger(__name__)


def _resolve_pipeline_tmp_root() -> Path:
    raw = os.getenv("NPBB_PIPELINE_TMP_ROOT", "").strip()
    if raw:
        return Path(raw)
    return Path(tempfile.gettempdir()) / "npbb_pipeline"


TMP_ROOT = _resolve_pipeline_tmp_root()
SOURCE_METADATA_COLUMNS = ("source_file", "source_sheet", "source_row")
DEFAULT_GOLD_INSERT_COMMIT_BATCH_SIZE = 100
DEFAULT_GOLD_INSERT_LOOKUP_CHUNK_SIZE = 1500
DEFAULT_GOLD_INSERT_PROGRESS_HEARTBEAT_SECONDS = 20
DEFAULT_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543 = 25
DEFAULT_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543 = 15.0
DEFAULT_GOLD_OBSERVABILITY_ENABLED = "1"
DEFAULT_GOLD_SQL_OBSERVABILITY_ENABLED = "1"
DEFAULT_PIPELINE_STALE_AFTER_SECONDS = 420
DEFAULT_PIPELINE_HEARTBEAT_DURING_RUN_SECONDS = 15

PIPELINE_PROGRESS_LABELS: dict[str, str] = {
    "queued": "Na fila para processamento",
    "silver_csv": "Gerando CSV a partir do Silver",
    "source_adapt": "Lendo e adaptando arquivos de origem",
    "event_taxonomy": "Classificando tipo de evento",
    "normalize_rows": "Normalizando campos (CPF, datas, telefone, local…)",
    "dedupe": "Removendo duplicidades CPF + evento",
    "contract_check": "Validando contrato dos dados",
    "write_outputs": "Gravando relatório e CSV consolidado",
    "insert_leads": "Inserindo leads Gold no banco",
}

PIPELINE_FAILURE_STAGE_LABELS: dict[str, str] = {
    **PIPELINE_PROGRESS_LABELS,
    "run_pipeline": "Executando pipeline Gold",
    "persist_result": "Persistindo resultado final",
}

LEAD_BATCH_LOAD_FIELDS_WITHOUT_BRONZE = (
    LeadBatch.id,
    LeadBatch.enviado_por,
    LeadBatch.plataforma_origem,
    LeadBatch.data_envio,
    LeadBatch.data_upload,
    LeadBatch.nome_arquivo_original,
    LeadBatch.arquivo_sha256,
    LeadBatch.bronze_storage_bucket,
    LeadBatch.bronze_storage_key,
    LeadBatch.bronze_content_type,
    LeadBatch.bronze_size_bytes,
    LeadBatch.bronze_uploaded_at,
    LeadBatch.stage,
    LeadBatch.evento_id,
    LeadBatch.origem_lote,
    LeadBatch.tipo_lead_proponente,
    LeadBatch.ativacao_id,
    LeadBatch.pipeline_status,
    LeadBatch.pipeline_report,
    LeadBatch.pipeline_progress,
    LeadBatch.gold_dq_discarded_rows,
    LeadBatch.gold_dq_issue_counts,
    LeadBatch.gold_dq_invalid_records_total,
    LeadBatch.created_at,
    LeadBatch.updated_at,
)


def _resolve_worker_engine():
    if os.getenv("TESTING", "").strip().lower() == "true":
        return database_module.engine
    return build_worker_engine()


def _log_pipeline_event(level: int, event_name: str, **context: Any) -> None:
    log_import_event(logger, f"gold.{event_name}", level=level, **context)
    elapsed_ms = context.get("elapsed_ms")
    total_elapsed_ms = context.get("total_elapsed_ms")
    if event_name == "run_pipeline.completed" and isinstance(elapsed_ms, (int, float)):
        observe_gold_stage_duration_seconds("run_pipeline", float(elapsed_ms) / 1000.0)
    elif event_name == "insert.completed" and isinstance(elapsed_ms, (int, float)):
        observe_gold_stage_duration_seconds("insert_leads", float(elapsed_ms) / 1000.0)
    elif event_name == "execution.metrics" and isinstance(total_elapsed_ms, (int, float)):
        observe_gold_stage_duration_seconds("execution_total", float(total_elapsed_ms) / 1000.0)


def _lead_batch_file_sha256(batch: LeadBatch | None) -> str | None:
    if batch is None:
        return None
    # `arquivo_sha256` ainda nao existe em alguns bancos remotos; ler via __dict__
    # evita lazy-load de uma coluna ausente no schema.
    return _normalize_sha256(batch.__dict__.get("arquivo_sha256"))


def load_batch_without_bronze(
    db: Session,
    batch_id: int,
    *,
    owner_user_id: int | None = None,
) -> LeadBatch | None:
    stmt = (
        select(LeadBatch)
        .options(load_only(*LEAD_BATCH_LOAD_FIELDS_WITHOUT_BRONZE))
        .where(LeadBatch.id == batch_id)
    )
    if owner_user_id is not None:
        stmt = stmt.where(LeadBatch.enviado_por == owner_user_id)
    return db.exec(stmt).first()


def load_batch_without_bronze_for_update(
    db: Session,
    batch_id: int,
    *,
    owner_user_id: int | None = None,
) -> LeadBatch | None:
    """Carrega o lote sem blob Bronze com bloqueio de linha para despacho seguro da pipeline."""
    stmt = (
        select(LeadBatch)
        .options(load_only(*LEAD_BATCH_LOAD_FIELDS_WITHOUT_BRONZE))
        .where(LeadBatch.id == batch_id)
        .with_for_update()
    )
    if owner_user_id is not None:
        stmt = stmt.where(LeadBatch.enviado_por == owner_user_id)
    return db.exec(stmt).first()


def pipeline_stale_after_seconds() -> int:
    raw = os.getenv("NPBB_PIPELINE_STALE_AFTER_SECONDS", str(DEFAULT_PIPELINE_STALE_AFTER_SECONDS)).strip()
    try:
        n = int(raw)
    except ValueError:
        return DEFAULT_PIPELINE_STALE_AFTER_SECONDS
    return max(60, min(n, 86_400))


def pipeline_heartbeat_during_run_seconds() -> float:
    raw = os.getenv(
        "NPBB_PIPELINE_HEARTBEAT_DURING_RUN_SECONDS",
        str(DEFAULT_PIPELINE_HEARTBEAT_DURING_RUN_SECONDS),
    ).strip()
    try:
        n = float(raw)
    except ValueError:
        return float(DEFAULT_PIPELINE_HEARTBEAT_DURING_RUN_SECONDS)
    return max(5.0, min(n, 300.0))


def _parse_pipeline_progress_updated_at(batch: LeadBatch) -> datetime_type | None:
    progress = batch.pipeline_progress
    if not isinstance(progress, dict):
        return None
    raw = progress.get("updated_at")
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip().replace("Z", "+00:00")
    try:
        dt = datetime_type.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def is_gold_pipeline_progress_stale(batch: LeadBatch, *, now: datetime_type | None = None) -> bool:
    """True se progresso Gold parece orfao (pending + progresso sem atualizacao recente)."""
    if batch.pipeline_status != PipelineStatus.PENDING:
        return False
    if batch.pipeline_progress is None:
        return False
    parsed = _parse_pipeline_progress_updated_at(batch)
    if parsed is None:
        return False
    clock = now or datetime_type.now(timezone.utc)
    age = (clock - parsed).total_seconds()
    return age > float(pipeline_stale_after_seconds())


def _build_worker_lost_stall_report(
    *,
    batch_id: int,
    silver_row_count: int,
    last_step: str | None,
    resume_context: dict[str, Any] | None,
    reason_code: str,
) -> dict[str, Any]:
    base = _build_contextual_pipeline_report(
        batch_id=batch_id,
        silver_row_count=silver_row_count,
        fail_reasons=[reason_code],
    )
    gate = base.setdefault("gate", {})
    gate["status"] = "FAIL"
    gate["decision"] = "hold"
    msgs = [str(x) for x in (gate.get("fail_reasons") or []) if str(x).strip()]
    extra = (
        f"Execucao Gold interrompida ({reason_code})"
        + (f" na etapa '{last_step}'." if last_step else ".")
    )
    if extra not in msgs:
        msgs.append(extra)
    gate["fail_reasons"] = msgs
    base["exit_code"] = 3
    fc: dict[str, Any] = {
        "step": last_step or "unknown",
        "stage": PIPELINE_FAILURE_STAGE_LABELS.get(last_step or "", last_step or ""),
        "exception_type": reason_code,
        "detail": reason_code,
        "message": extra,
    }
    normalized_resume_context = _normalize_insert_resume_context(resume_context)
    if normalized_resume_context is not None:
        fc["resume_context"] = normalized_resume_context
    base["failure_context"] = fc
    return base


def mark_gold_pipeline_batch_stalled_worker_lost(
    db: Session,
    batch: LeadBatch,
    *,
    batch_id: int,
    reason_code: str = "WORKER_LOST",
) -> None:
    """Marca stalled com relatorio minimo; `queue_pipeline_batch` pode retomar usando resume em failure_context."""
    silver_row_count = _silver_row_count(db, batch_id=batch_id)
    resume_context = _resume_context_from_batch(batch)
    last_step = None
    if isinstance(batch.pipeline_progress, dict):
        last_step = str(batch.pipeline_progress.get("step") or "").strip() or None
    report = _build_worker_lost_stall_report(
        batch_id=batch_id,
        silver_row_count=silver_row_count,
        last_step=last_step,
        resume_context=resume_context,
        reason_code=reason_code,
    )
    batch.pipeline_status = PipelineStatus.STALLED
    batch.pipeline_report = report
    _clear_pipeline_progress(batch)
    disc, issues, inv_n = _gold_dq_snapshot_from_report(report)
    batch.gold_dq_discarded_rows = disc
    batch.gold_dq_issue_counts = issues
    batch.gold_dq_invalid_records_total = inv_n
    db.add(batch)


@dataclass(frozen=True)
class EventoPipelineContext:
    nome: str
    tipo_nome: str | None
    data_evento_canonica: str | None
    local_evento: str | None


@dataclass(frozen=True)
class ActivationInsertContext:
    ativacao_id: int
    evento_id: int
    nome_ativacao: str | None
    responsavel_nome: str
    responsavel_agencia_id: int


@dataclass
class GoldInsertMetrics:
    total_rows: int = 0
    created_rows: int = 0
    updated_rows: int = 0
    chunks_committed: int = 0
    flush_calls: int = 0
    fallback_lookup_calls: int = 0
    lead_event_calls: int = 0
    ativacao_link_calls: int = 0
    bytes_total: int = 0
    avg_row_bytes: float = 0.0
    avg_chunk_rows: float = 0.0
    estimated_chunk_bytes: float = 0.0
    rows_per_second: float = 0.0
    time_in_insert_total_ms: int = 0
    time_in_payload_build_ms: int = 0
    time_in_lookup_context_ms: int = 0
    time_in_lookup_ms: int = 0
    time_in_flush_ms: int = 0
    time_in_commit_ms: int = 0
    time_in_lead_event_ms: int = 0
    time_in_ativacao_link_ms: int = 0


@dataclass
class SqlStatementMetrics:
    count: int = 0
    total_ms: int = 0


def _duration_ms(started_at: float, ended_at: float | None = None) -> int:
    end = time_module.perf_counter() if ended_at is None else ended_at
    return max(round((end - started_at) * 1000), 0)


def _gold_observability_enabled() -> bool:
    return os.getenv("LEAD_GOLD_OBSERVABILITY_ENABLED", DEFAULT_GOLD_OBSERVABILITY_ENABLED).strip().lower() not in {
        "0",
        "false",
        "no",
    }


def _gold_sql_observability_enabled() -> bool:
    return os.getenv(
        "LEAD_GOLD_SQL_OBSERVABILITY_ENABLED",
        DEFAULT_GOLD_SQL_OBSERVABILITY_ENABLED,
    ).strip().lower() not in {"0", "false", "no"}


def _classify_sql_statement(statement: str) -> str:
    normalized = " ".join(statement.strip().lower().split())
    if not normalized:
        return "unknown"
    if normalized.startswith("commit"):
        return "commit"
    if normalized.startswith("set local statement_timeout"):
        return "set_local_statement_timeout"
    if " lead_evento " in f" {normalized} ":
        if normalized.startswith("select"):
            return "select_lead_evento"
        if normalized.startswith("insert"):
            return "insert_lead_evento"
        if normalized.startswith("update"):
            return "update_lead_evento"
    if " ativacao_lead " in f" {normalized} ":
        if normalized.startswith("select"):
            return "select_ativacao_lead"
        if normalized.startswith("insert"):
            return "insert_ativacao_lead"
        if normalized.startswith("update"):
            return "update_ativacao_lead"
    if " lead " in f" {normalized} ":
        if normalized.startswith("select"):
            return "select_lead"
        if normalized.startswith("insert"):
            return "insert_lead"
        if normalized.startswith("update"):
            return "update_lead"
    if normalized.startswith("select"):
        return "select_other"
    if normalized.startswith("insert"):
        return "insert_other"
    if normalized.startswith("update"):
        return "update_other"
    if normalized.startswith("delete"):
        return "delete_other"
    return "other"


class _SqlObservabilityCollector:
    def __init__(self, engine: Any):
        self.engine = engine
        self.enabled = _gold_observability_enabled() and _gold_sql_observability_enabled()
        self.metrics: dict[str, SqlStatementMetrics] = {}
        self._before = None
        self._after = None

    def __enter__(self) -> "_SqlObservabilityCollector":
        if not self.enabled:
            return self

        def before_cursor_execute(_conn, cursor, statement, parameters, context, executemany):  # noqa: ARG001
            context._lead_gold_sql_started_at = time_module.perf_counter()

        def after_cursor_execute(_conn, cursor, statement, parameters, context, executemany):  # noqa: ARG001
            started_at = getattr(context, "_lead_gold_sql_started_at", None)
            if started_at is None:
                return
            bucket = _classify_sql_statement(statement)
            metric = self.metrics.setdefault(bucket, SqlStatementMetrics())
            metric.count += 1
            metric.total_ms += _duration_ms(started_at)

        self._before = before_cursor_execute
        self._after = after_cursor_execute
        event.listen(self.engine, "before_cursor_execute", self._before)
        event.listen(self.engine, "after_cursor_execute", self._after)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        if not self.enabled:
            return
        if self._before is not None:
            event.remove(self.engine, "before_cursor_execute", self._before)
        if self._after is not None:
            event.remove(self.engine, "after_cursor_execute", self._after)

    def summary(self) -> dict[str, dict[str, int]]:
        return {
            key: {"count": value.count, "total_ms": value.total_ms}
            for key, value in sorted(self.metrics.items())
        }


def _canonical_event_date_iso(evento: Evento) -> str | None:
    canonical_date = evento.data_inicio_realizada or evento.data_inicio_prevista
    if canonical_date is None:
        return None
    return canonical_date.isoformat()


def _canonical_event_local(evento: Evento) -> str | None:
    locality = normalize_brazilian_locality(cidade=evento.cidade, estado=evento.estado)
    if locality.issue_code is not None or not locality.local:
        return None
    return locality.local


def _event_local_from_model(evento: Evento) -> str | None:
    canonical = _canonical_event_local(evento)
    if canonical:
        return canonical

    cidade = _clean_text(evento.cidade)
    estado = _clean_text(evento.estado)
    if cidade and estado:
        return f"{cidade}-{estado}"
    return cidade or estado


def _build_evento_pipeline_context(evento: Evento, tipo_nome: str | None) -> EventoPipelineContext:
    return EventoPipelineContext(
        nome=evento.nome,
        tipo_nome=tipo_nome,
        data_evento_canonica=_canonical_event_date_iso(evento),
        local_evento=_event_local_from_model(evento),
    )


def _evento_lookup_por_ids(db: Session, event_ids: set[int]) -> dict[int, EventoPipelineContext]:
    """Contexto canonico do Evento para enriquecer linhas Silver ancoradas em evento_id."""
    if not event_ids:
        return {}
    eventos = db.exec(select(Evento).where(Evento.id.in_(event_ids))).all()
    tipo_ids = {e.tipo_id for e in eventos if e.tipo_id is not None}
    tipo_nomes: dict[int, str] = {}
    if tipo_ids:
        for tipo in db.exec(select(TipoEvento).where(TipoEvento.id.in_(tipo_ids))).all():
            tipo_nomes[int(tipo.id)] = tipo.nome
    out: dict[int, EventoPipelineContext] = {}
    for ev in eventos:
        tid = ev.tipo_id
        tipo_nome = tipo_nomes.get(int(tid)) if tid is not None else None
        out[int(ev.id)] = _build_evento_pipeline_context(ev, tipo_nome)
    return out


def _build_contextual_pipeline_report(
    *,
    batch_id: int,
    silver_row_count: int,
    fail_reasons: list[str],
) -> dict[str, Any]:
    return {
        "lote_id": str(batch_id),
        "run_timestamp": datetime_type.now(timezone.utc).isoformat(),
        "input_files": [],
        "input_files_scanned": [],
        "input_files_processed": [],
        "input_files_skipped": [],
        "source_profiles_detected": {},
        "mapping_version": "",
        "totals": {
            "raw_rows": silver_row_count,
            "valid_rows": silver_row_count,
            "discarded_rows": 0,
        },
        "quality_metrics": asdict(QualityMetrics()),
        "gate": {
            "status": "FAIL",
            "decision": "hold",
            "fail_reasons": fail_reasons,
            "warnings": [],
        },
        "data_nascimento_controle": [],
        "localidade_controle": [],
        "cidade_fora_mapeamento_controle": [],
        "invalid_records": [],
        "exit_code": 2,
    }


def _persist_contextual_pipeline_failure(
    db: Session,
    *,
    batch: LeadBatch,
    report_data: dict[str, Any],
) -> None:
    batch.stage = BatchStage.SILVER
    batch.pipeline_status = PipelineStatus.FAIL
    batch.pipeline_report = report_data
    disc, issues, inv_n = _gold_dq_snapshot_from_report(report_data)
    batch.gold_dq_discarded_rows = disc
    batch.gold_dq_issue_counts = issues
    batch.gold_dq_invalid_records_total = inv_n
    _clear_pipeline_progress(batch)
    db.add(batch)
    db.commit()


def _silver_row_count(db: Session, *, batch_id: int) -> int:
    return len(db.exec(select(LeadSilver.id).where(LeadSilver.batch_id == batch_id)).all())


def _compact_exception_detail(exc: Exception) -> str:
    lines = [line.strip() for line in str(exc).splitlines() if line.strip()]
    detail = lines[0] if lines else ""
    if not detail:
        return exc.__class__.__name__
    if not detail.startswith(f"{exc.__class__.__name__}:"):
        detail = f"{exc.__class__.__name__}: {detail}"
    if len(detail) > 280:
        return detail[:277] + "..."
    return detail


def _build_pipeline_exception_report(
    *,
    batch_id: int,
    silver_row_count: int,
    failure_step: str,
    exc: Exception,
    report_data: dict[str, Any] | None,
    resume_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if report_data:
        base = deepcopy(report_data)
    else:
        base = _build_contextual_pipeline_report(
            batch_id=batch_id,
            silver_row_count=silver_row_count,
            fail_reasons=[],
        )

    gate = base.setdefault("gate", {})
    gate["status"] = "FAIL"
    gate["decision"] = "hold"

    fail_reasons = [str(reason) for reason in (gate.get("fail_reasons") or []) if str(reason).strip()]
    detail = _compact_exception_detail(exc)
    stage_label = PIPELINE_FAILURE_STAGE_LABELS.get(failure_step, failure_step)
    failure_message = f"Falha interna em '{stage_label}': {detail}"
    if failure_message not in fail_reasons:
        fail_reasons.append(failure_message)
    gate["fail_reasons"] = fail_reasons
    gate["warnings"] = [str(warning) for warning in (gate.get("warnings") or []) if str(warning).strip()]

    base.setdefault("invalid_records", [])
    base.setdefault("data_nascimento_controle", [])
    base.setdefault("localidade_controle", [])
    base.setdefault("cidade_fora_mapeamento_controle", [])
    base["exit_code"] = 1
    base["failure_context"] = {
        "step": failure_step,
        "stage": stage_label,
        "exception_type": exc.__class__.__name__,
        "detail": detail,
        "message": failure_message,
    }
    normalized_resume_context = _normalize_insert_resume_context(resume_context)
    if normalized_resume_context is not None:
        base["failure_context"]["resume_context"] = normalized_resume_context
    return base


def materializar_silver_como_csv(batch_id: int, db: Session) -> Path:
    """Le `leads_silver` do lote e escreve CSV temporario com o contrato Gold."""
    started_at = time_module.perf_counter()
    tmp_dir = TMP_ROOT / str(batch_id)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    batch = load_batch_without_bronze(db, batch_id)

    silver_rows = db.exec(
        select(LeadSilver)
        .where(LeadSilver.batch_id == batch_id)
        .order_by(LeadSilver.row_index, LeadSilver.id)
    ).all()

    event_ids = {int(r.evento_id) for r in silver_rows if r.evento_id is not None}
    evento_por_id = _evento_lookup_por_ids(db, event_ids)
    fallback_source_file = _clean_text(batch.nome_arquivo_original if batch is not None else "")
    batch_is_xlsx = Path(fallback_source_file or "").suffix.lower() == ".xlsx"
    fallback_source_sheet = ""
    fallback_source_row_offset = 2
    fallback_physical_lines_by_row_index: dict[int, int] = {}
    needs_source_sheet_fallback = batch_is_xlsx and any(
        not _clean_text((row.dados_brutos or {}).get("source_sheet")) for row in silver_rows
    )
    needs_source_row_fallback = any(
        _parse_int_value((row.dados_brutos or {}).get("source_row")) is None
        and _parse_int_value((row.dados_brutos or {}).get("source_row_original")) is None
        for row in silver_rows
    )
    needs_source_metadata_fallback = needs_source_sheet_fallback or needs_source_row_fallback
    if batch is not None and needs_source_metadata_fallback and fallback_source_file:
        try:
            payload = read_batch_payload(batch)
            if not payload:
                raise ValueError("arquivo Bronze indisponivel")
            extracted = read_raw_file_rows(payload, filename=fallback_source_file)
        except Exception:  # noqa: BLE001
            logger.warning(
                "Nao foi possivel reconstruir metadados de origem do batch %s para a pipeline Gold.",
                batch_id,
            )
        else:
            fallback_source_sheet = extracted.sheet_name or ""
            fallback_source_row_offset = extracted.start_index + 2
            fallback_physical_lines_by_row_index = {
                row_index: int(physical_line)
                for row_index, physical_line in enumerate(extracted.physical_line_numbers)
            }

    csv_path = tmp_dir / "silver_input.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[*ALL_COLUMNS, *SOURCE_METADATA_COLUMNS])
        writer.writeheader()
        for row in silver_rows:
            dados = row.dados_brutos or {}
            out_row = {col: str(dados.get(col, "") or "") for col in ALL_COLUMNS}
            source_file = _clean_text(dados.get("source_file")) or fallback_source_file
            source_sheet = _clean_text(dados.get("source_sheet"))
            if source_sheet is None and batch_is_xlsx:
                source_sheet = fallback_source_sheet
            source_row = _parse_int_value(dados.get("source_row_original"))
            if source_row is None:
                source_row = _parse_int_value(dados.get("source_row"))
            if source_row is None:
                source_row = fallback_physical_lines_by_row_index.get(int(row.row_index))
            if source_row is None:
                source_row = int(row.row_index) + fallback_source_row_offset
            out_row["source_file"] = source_file or ""
            out_row["source_sheet"] = source_sheet or ""
            out_row["source_row"] = str(source_row)
            if row.evento_id is None:
                writer.writerow(out_row)
                continue
            contexto_evento = evento_por_id.get(int(row.evento_id))
            # O lote Silver já fixa `evento_id` no mapeamento: o cadastro de Evento manda sobre
            # colunas vazias ou ruído da planilha (evita taxonomia falhar com texto espúrio).
            if contexto_evento is None:
                writer.writerow(out_row)
                continue
            if contexto_evento.nome:
                out_row["evento"] = contexto_evento.nome
            if contexto_evento.tipo_nome:
                out_row["tipo_evento"] = contexto_evento.tipo_nome
            elif contexto_evento.nome and not out_row["tipo_evento"].strip():
                out_row["tipo_evento"] = TIPO_EVENTO_PADRAO
            if contexto_evento.data_evento_canonica:
                out_row["data_evento"] = contexto_evento.data_evento_canonica
            if contexto_evento.local_evento:
                out_row["local"] = contexto_evento.local_evento
            writer.writerow(out_row)

    csv_size_bytes = csv_path.stat().st_size if csv_path.exists() else 0
    _log_pipeline_event(
        logging.INFO,
        "silver_csv.materialized_stats",
        batch_id=batch_id,
        silver_rows=len(silver_rows),
        csv_size_bytes=csv_size_bytes,
        elapsed_ms=_duration_ms(started_at),
    )
    return csv_path


def _get_or_create_ativacao_lead(session: Session, *, ativacao_id: int, lead_id: int) -> AtivacaoLead:
    existing = session.exec(
        select(AtivacaoLead)
        .where(AtivacaoLead.ativacao_id == ativacao_id)
        .where(AtivacaoLead.lead_id == lead_id)
    ).first()
    if existing is not None:
        return existing
    ativacao = session.get(Ativacao, ativacao_id)
    nome_raw = (ativacao.nome or "").strip() if ativacao else ""
    nome_ativacao = nome_raw or None
    link = AtivacaoLead(ativacao_id=ativacao_id, lead_id=lead_id, nome_ativacao=nome_ativacao)
    try:
        with session.begin_nested():
            session.add(link)
            session.flush()
    except IntegrityError:
        found = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == ativacao_id)
            .where(AtivacaoLead.lead_id == lead_id)
        ).first()
        if found is None:
            raise
        return found
    return link


def _load_activation_insert_context(
    session: Session,
    *,
    batch: LeadBatch,
) -> ActivationInsertContext | None:
    if batch.ativacao_id is None or batch.evento_id is None:
        return None

    ativacao = session.get(Ativacao, int(batch.ativacao_id))
    evento = session.get(Evento, int(batch.evento_id))
    if ativacao is None or evento is None:
        return None
    if ativacao.evento_id is not None and int(ativacao.evento_id) != int(batch.evento_id):
        return None
    if evento.agencia_id is None:
        return None

    agencia_nome = _clean_text(getattr(getattr(evento, "agencia", None), "nome", None))
    if agencia_nome is None:
        agencia = session.get(Agencia, int(evento.agencia_id))
        if agencia is None:
            return None
        agencia_nome = _clean_text(agencia.nome)
    if agencia_nome is None:
        return None

    return ActivationInsertContext(
        ativacao_id=int(batch.ativacao_id),
        evento_id=int(batch.evento_id),
        nome_ativacao=_clean_text(ativacao.nome),
        responsavel_nome=agencia_nome,
        responsavel_agencia_id=int(evento.agencia_id),
    )


def _load_existing_ativacao_leads(
    session: Session,
    *,
    ativacao_id: int,
    lead_ids: set[int],
) -> dict[int, AtivacaoLead]:
    if not lead_ids:
        return {}
    rows = session.exec(
        select(AtivacaoLead)
        .where(AtivacaoLead.ativacao_id == ativacao_id)
        .where(AtivacaoLead.lead_id.in_(sorted(lead_ids)))
    ).all()
    return {int(link.lead_id): link for link in rows}


def _load_existing_lead_eventos(
    session: Session,
    *,
    evento_id: int,
    lead_ids: set[int],
) -> dict[int, LeadEvento]:
    if not lead_ids:
        return {}
    rows = session.exec(
        select(LeadEvento)
        .where(LeadEvento.evento_id == evento_id)
        .where(LeadEvento.lead_id.in_(sorted(lead_ids)))
    ).all()
    return {int(link.lead_id): link for link in rows}


def _get_or_create_ativacao_lead_fast(
    session: Session,
    *,
    lead_id: int,
    context: ActivationInsertContext,
    existing_links_by_lead_id: dict[int, AtivacaoLead],
) -> tuple[AtivacaoLead, int]:
    existing = existing_links_by_lead_id.get(lead_id)
    if existing is not None:
        return existing, 0

    link = AtivacaoLead(
        ativacao_id=context.ativacao_id,
        lead_id=lead_id,
        nome_ativacao=context.nome_ativacao,
    )
    session.add(link)
    flush_started_at = time_module.perf_counter()
    session.flush()
    flush_ms = _duration_ms(flush_started_at)
    existing_links_by_lead_id[lead_id] = link
    return link, flush_ms


def _ensure_activation_lead_event_fast(
    session: Session,
    *,
    lead_id: int,
    source_ref_id: int,
    context: ActivationInsertContext,
    existing_events_by_lead_id: dict[int, LeadEvento],
) -> LeadEvento:
    existing = existing_events_by_lead_id.get(lead_id)
    if existing is None:
        lead_event = LeadEvento(
            lead_id=lead_id,
            evento_id=context.evento_id,
            source_kind=LeadEventoSourceKind.ACTIVATION,
            source_ref_id=source_ref_id,
            tipo_lead=TipoLead.ATIVACAO,
            responsavel_tipo=TipoResponsavel.AGENCIA,
            responsavel_nome=context.responsavel_nome,
            responsavel_agencia_id=context.responsavel_agencia_id,
        )
        session.add(lead_event)
        existing_events_by_lead_id[lead_id] = lead_event
        return lead_event

    if existing.source_kind == LeadEventoSourceKind.MANUAL_RECONCILED:
        result = ensure_lead_event(
            session,
            lead_id=lead_id,
            evento_id=context.evento_id,
            source_kind=LeadEventoSourceKind.ACTIVATION,
            source_ref_id=source_ref_id,
        )
        existing_events_by_lead_id[lead_id] = result.lead_evento
        return result.lead_evento

    changed = False
    if existing.source_kind != LeadEventoSourceKind.ACTIVATION:
        existing.source_kind = LeadEventoSourceKind.ACTIVATION
        changed = True
    if existing.source_ref_id != source_ref_id:
        existing.source_ref_id = source_ref_id
        changed = True
    if existing.tipo_lead != TipoLead.ATIVACAO:
        existing.tipo_lead = TipoLead.ATIVACAO
        changed = True
    if existing.responsavel_tipo != TipoResponsavel.AGENCIA:
        existing.responsavel_tipo = TipoResponsavel.AGENCIA
        changed = True
    if existing.responsavel_nome != context.responsavel_nome:
        existing.responsavel_nome = context.responsavel_nome
        changed = True
    if existing.responsavel_agencia_id != context.responsavel_agencia_id:
        existing.responsavel_agencia_id = context.responsavel_agencia_id
        changed = True
    if changed:
        session.add(existing)
    return existing


def _pipeline_status_from_str(status: str) -> PipelineStatus:
    mapping: dict[str, PipelineStatus] = {
        "PASS": PipelineStatus.PASS,
        "PASS_WITH_WARNINGS": PipelineStatus.PASS_WITH_WARNINGS,
        "FAIL": PipelineStatus.FAIL,
    }
    return mapping.get(status.upper(), PipelineStatus.FAIL)


def _gold_dq_snapshot_from_report(report_data: dict[str, Any]) -> tuple[int | None, dict[str, int] | None, int | None]:
    """Extrai totais do relatorio Gold para colunas indexaveis em `lead_batches`."""
    if not report_data:
        return None, None, None

    totals = report_data.get("totals") or {}
    discarded_raw = totals.get("discarded_rows")
    discarded: int | None
    if discarded_raw is None:
        discarded = None
    else:
        discarded = int(discarded_raw)

    qm = report_data.get("quality_metrics")
    parsed: dict[str, int] = {}
    if isinstance(qm, dict):
        for key, val in qm.items():
            if isinstance(val, bool):
                continue
            if isinstance(val, (int, float)):
                parsed[str(key)] = int(val)
    issue_counts: dict[str, int] | None = parsed

    inv = report_data.get("invalid_records")
    inv_total: int | None
    if isinstance(inv, list):
        inv_total = len(inv)
    else:
        inv_total = None

    return discarded, issue_counts, inv_total


def _clear_gold_pipeline_snapshot(batch: LeadBatch) -> None:
    batch.pipeline_report = None
    batch.gold_dq_discarded_rows = None
    batch.gold_dq_issue_counts = None
    batch.gold_dq_invalid_records_total = None


def _clear_pipeline_progress(batch: LeadBatch) -> None:
    batch.pipeline_progress = None


def _pipeline_progress_updated_at() -> str:
    return datetime_type.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_pipeline_progress_payload(
    *,
    step: str,
    pct: int | None = None,
    label: str | None = None,
    resume_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "step": step,
        "label": label or PIPELINE_PROGRESS_LABELS.get(step, step),
        "pct": pct,
        "updated_at": _pipeline_progress_updated_at(),
    }
    normalized_resume_context = _normalize_insert_resume_context(resume_context)
    if normalized_resume_context is not None:
        payload["resume_step"] = normalized_resume_context["step"]
        payload["committed_rows"] = normalized_resume_context["committed_rows"]
        if "total_rows" in normalized_resume_context:
            payload["total_rows"] = normalized_resume_context["total_rows"]
        if "content_hash" in normalized_resume_context:
            payload["content_hash"] = normalized_resume_context["content_hash"]
        if "arquivo_sha256" in normalized_resume_context:
            payload["arquivo_sha256"] = normalized_resume_context["arquivo_sha256"]
    return payload


def set_pipeline_progress(
    batch: LeadBatch,
    *,
    step: str,
    pct: int | None = None,
    label: str | None = None,
    resume_context: dict[str, Any] | None = None,
) -> None:
    batch.pipeline_progress = _build_pipeline_progress_payload(
        step=step,
        pct=pct,
        label=label,
        resume_context=resume_context,
    )


def _normalize_sha256(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    if not text:
        return None
    if re.fullmatch(r"[0-9a-f]{64}", text) is None:
        return None
    return text


def _normalize_insert_resume_context(resume_context: Any) -> dict[str, Any] | None:
    if not isinstance(resume_context, dict):
        return None

    step = str(resume_context.get("resume_step") or resume_context.get("step") or "").strip()
    if step != "insert_leads":
        return None

    committed_rows = _parse_int_value(resume_context.get("committed_rows"))
    if committed_rows is None or committed_rows < 0:
        return None

    normalized: dict[str, Any] = {
        "step": "insert_leads",
        "committed_rows": committed_rows,
    }
    total_rows = _parse_int_value(resume_context.get("total_rows"))
    if total_rows is not None and total_rows >= committed_rows:
        normalized["total_rows"] = total_rows
    content_hash = _normalize_sha256(resume_context.get("content_hash"))
    if content_hash is not None:
        normalized["content_hash"] = content_hash
    arquivo_sha256 = _normalize_sha256(
        resume_context.get("arquivo_sha256") or resume_context.get("file_sha256")
    )
    if arquivo_sha256 is not None:
        normalized["arquivo_sha256"] = arquivo_sha256
    return normalized


def _resume_context_from_batch(batch: LeadBatch | None) -> dict[str, Any] | None:
    if batch is None:
        return None

    if isinstance(batch.pipeline_progress, dict):
        from_progress = _normalize_insert_resume_context(batch.pipeline_progress)
        if from_progress is not None:
            return from_progress

    report = batch.pipeline_report
    if not isinstance(report, dict):
        return None
    failure_context = report.get("failure_context")
    if not isinstance(failure_context, dict):
        return None
    return _normalize_insert_resume_context(failure_context.get("resume_context"))


def _resume_context_from_progress_event(event: PipelineProgressEvent) -> dict[str, Any] | None:
    meta = getattr(event, "meta", None)
    if not isinstance(meta, dict):
        return None
    return _normalize_insert_resume_context(
        {
            "step": event.step,
            "committed_rows": meta.get("committed_rows"),
            "total_rows": meta.get("total_rows"),
            "content_hash": meta.get("content_hash"),
            "arquivo_sha256": meta.get("arquivo_sha256"),
        }
    )


def queue_pipeline_batch(batch: LeadBatch) -> None:
    resume_context = _resume_context_from_batch(batch)
    batch.pipeline_status = PipelineStatus.PENDING
    _clear_gold_pipeline_snapshot(batch)
    set_pipeline_progress(batch, step="queued", resume_context=resume_context)


def claim_next_gold_pipeline_batch(db: Session) -> int | None:
    batch = db.exec(
        select(LeadBatch)
        .options(load_only(*LEAD_BATCH_LOAD_FIELDS_WITHOUT_BRONZE))
        .where(LeadBatch.stage == BatchStage.SILVER)
        .where(LeadBatch.pipeline_status == PipelineStatus.PENDING)
        .where(LeadBatch.pipeline_progress["step"].as_string() == "queued")
        .order_by(LeadBatch.created_at.asc(), LeadBatch.id.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    ).first()
    if batch is None:
        return None
    set_pipeline_progress(batch, step="silver_csv", resume_context=_resume_context_from_batch(batch))
    claimed_batch_id = int(batch.id)
    db.add(batch)
    db.commit()
    return claimed_batch_id


def _persist_pipeline_progress(engine: Any, batch_id: int, event: PipelineProgressEvent) -> None:
    with Session(engine, expire_on_commit=False) as db:
        set_internal_service_db_context(db)
        batch = load_batch_without_bronze(db, batch_id)
        if not batch:
            logger.warning("Batch %s nao encontrado para atualizar progresso da pipeline.", batch_id)
            return
        set_pipeline_progress(
            batch,
            step=event.step,
            pct=event.pct,
            label=event.label,
            resume_context=_resume_context_from_progress_event(event),
        )
        db.add(batch)
        db.commit()
    _log_pipeline_event(
        logging.INFO,
        "progress",
        batch_id=batch_id,
        step=event.step,
        pct=event.pct,
        label=event.label,
    )


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _parse_timestamp(value: Any) -> pd.Timestamp | None:
    text = str(value or "").strip()
    if not text:
        return None
    iso_like = re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[ T].*)?", text) is not None
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=not iso_like)
    if pd.isna(parsed):
        return None
    return parsed


def _parse_date_value(value: Any) -> date_type | None:
    parsed = _parse_timestamp(value)
    return parsed.date() if parsed is not None else None


def _parse_datetime_value(value: Any) -> datetime_type | None:
    parsed = _parse_timestamp(value)
    return parsed.to_pydatetime() if parsed is not None else None


def _parse_time_value(value: Any) -> time_type | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return time_type.fromisoformat(text)
    except ValueError:
        parsed = _parse_timestamp(text)
        return parsed.time() if parsed is not None else None


def _parse_bool_value(value: Any) -> bool | None:
    text = str(value or "").strip()
    if not text:
        return None

    normalized = strip_accents(text).lower()
    true_values = {"1", "true", "t", "sim", "s", "yes", "y", "on"}
    false_values = {"0", "false", "f", "nao", "n", "no", "off"}
    if normalized in true_values:
        return True
    if normalized in false_values:
        return False
    return None


def _parse_int_value(value: Any) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        parsed = pd.to_numeric(text, errors="coerce")
        if pd.isna(parsed):
            return None
        return int(parsed)


def _build_lead_payload(row: dict[str, str], batch: LeadBatch) -> dict[str, Any]:
    fonte_origem = _clean_text(row.get("fonte_origem")) or batch.plataforma_origem
    return {
        "id_salesforce": _clean_text(row.get("id_salesforce")),
        "nome": _clean_text(row.get("nome")),
        "sobrenome": _clean_text(row.get("sobrenome")),
        "email": _clean_text(row.get("email")),
        "telefone": _clean_text(row.get("telefone")),
        "cpf": _clean_text(row.get("cpf")),
        "data_nascimento": _parse_date_value(row.get("data_nascimento")),
        "evento_nome": _clean_text(row.get("evento")),
        "sessao": _clean_text(row.get("sessao")) or _clean_text(row.get("local")),
        "data_compra": _parse_datetime_value(row.get("data_compra")),
        "data_compra_data": _parse_date_value(row.get("data_compra_data")),
        "data_compra_hora": _parse_time_value(row.get("data_compra_hora")),
        "opt_in": _clean_text(row.get("opt_in")),
        "opt_in_id": _clean_text(row.get("opt_in_id")),
        "opt_in_flag": _parse_bool_value(row.get("opt_in_flag")),
        "metodo_entrega": _clean_text(row.get("metodo_entrega")),
        "rg": _clean_text(row.get("rg")),
        "endereco_rua": _clean_text(row.get("endereco_rua")),
        "endereco_numero": _clean_text(row.get("endereco_numero")),
        "complemento": _clean_text(row.get("complemento")),
        "bairro": _clean_text(row.get("bairro")),
        "cep": _clean_text(row.get("cep")),
        "cidade": _clean_text(row.get("cidade")),
        "estado": _clean_text(row.get("estado")),
        "genero": _clean_text(row.get("genero")),
        "codigo_promocional": _clean_text(row.get("codigo_promocional")),
        "ingresso_tipo": _clean_text(row.get("ingresso_tipo")),
        "ingresso_qtd": _parse_int_value(row.get("ingresso_qtd")),
        "fonte_origem": fonte_origem,
        "is_cliente_bb": _parse_bool_value(row.get("is_cliente_bb")),
        "is_cliente_estilo": _parse_bool_value(row.get("is_cliente_estilo")),
    }


def _merge_lead_payload_if_missing(lead: Lead, payload: dict[str, Any]) -> None:
    merge_lead_payload_fill_missing(lead, payload)


def _find_lead_by_canonical_event(
    db: Session,
    payload: dict[str, Any],
    *,
    anchored_evento_id: int,
) -> Lead | None:
    id_salesforce = payload.get("id_salesforce")
    if _has_value(id_salesforce):
        lead = db.exec(
            select(Lead)
            .join(LeadEvento, LeadEvento.lead_id == Lead.id)
            .where(Lead.id_salesforce == id_salesforce)
            .where(LeadEvento.evento_id == anchored_evento_id)
        ).first()
        if lead is not None:
            return lead

    return db.exec(
        select(Lead)
        .join(LeadEvento, LeadEvento.lead_id == Lead.id)
        .where(Lead.email == payload.get("email"))
        .where(Lead.cpf == payload.get("cpf"))
        .where(Lead.sessao == payload.get("sessao"))
        .where(LeadEvento.evento_id == anchored_evento_id)
    ).first()


def _legacy_lead_candidates(db: Session, payload: dict[str, Any]) -> list[Lead]:
    candidates: list[Lead] = []
    seen_ids: set[int] = set()

    def _append_candidate(candidate: Lead | None) -> None:
        if candidate is None or candidate.id is None:
            return
        candidate_id = int(candidate.id)
        if candidate_id in seen_ids:
            return
        seen_ids.add(candidate_id)
        candidates.append(candidate)

    id_salesforce = payload.get("id_salesforce")
    if _has_value(id_salesforce):
        _append_candidate(
            db.exec(select(Lead).where(Lead.id_salesforce == id_salesforce)).first()
        )

    for candidate in db.exec(
        select(Lead)
        .where(Lead.email == payload.get("email"))
        .where(Lead.cpf == payload.get("cpf"))
        .where(Lead.evento_nome == payload.get("evento_nome"))
        .where(Lead.sessao == payload.get("sessao"))
    ).all():
        _append_candidate(candidate)

    return candidates


def _lead_has_any_event_link(db: Session, lead_id: int | None) -> bool:
    if lead_id is None:
        return False
    return db.exec(select(LeadEvento.id).where(LeadEvento.lead_id == lead_id)).first() is not None


def _find_existing_lead(
    db: Session,
    payload: dict[str, Any],
    *,
    anchored_evento_id: int | None = None,
) -> Lead | None:
    if anchored_evento_id is not None:
        lead = _find_lead_by_canonical_event(
            db,
            payload,
            anchored_evento_id=anchored_evento_id,
        )
        if lead is not None:
            return lead

    candidates = _legacy_lead_candidates(db, payload)
    if anchored_evento_id is None:
        return candidates[0] if candidates else None

    for candidate in candidates:
        if not _lead_has_any_event_link(db, candidate.id):
            return candidate
    return None


def _configure_lead_gold_statement_timeout(db: Session) -> None:
    bind = db.get_bind()
    if bind is None or bind.dialect.name == "sqlite":
        return

    timeout_ms = max(int(os.getenv("LEAD_GOLD_STATEMENT_TIMEOUT_MS", "600000")), 0)
    db.exec(text(f"SET LOCAL statement_timeout = {timeout_ms}"))


def _lead_gold_bind_url(db: Session) -> str | None:
    bind = db.get_bind()
    if bind is None:
        return None
    url = getattr(bind, "url", None)
    if url is None:
        return None
    return str(url)


def _is_supabase_transaction_pooler_url(url: str | None) -> bool:
    if not url:
        return False
    raw = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    try:
        parsed = urlparse(raw)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    return parsed.port == 6543 and "supabase" in host


def _lead_gold_uses_supabase_transaction_pooler(db: Session) -> bool:
    return _is_supabase_transaction_pooler_url(_lead_gold_bind_url(db))


def _lead_gold_insert_commit_batch_size(db: Session) -> int:
    configured = max(
        int(os.getenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", str(DEFAULT_GOLD_INSERT_COMMIT_BATCH_SIZE))),
        1,
    )
    if not _lead_gold_uses_supabase_transaction_pooler(db):
        return configured

    supabase_cap = max(
        int(
            os.getenv(
                "LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543",
                str(DEFAULT_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543),
            )
        ),
        1,
    )
    return min(configured, supabase_cap)


def _lead_gold_insert_max_transaction_seconds(db: Session) -> float:
    if not _lead_gold_uses_supabase_transaction_pooler(db):
        return 0.0
    raw = os.getenv(
        "LEAD_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543",
        str(DEFAULT_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543),
    )
    try:
        return max(float(raw), 0.0)
    except ValueError:
        return DEFAULT_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543


def _lead_gold_progress_heartbeat_seconds() -> float:
    raw = os.getenv(
        "LEAD_GOLD_PROGRESS_HEARTBEAT_SECONDS",
        str(DEFAULT_GOLD_INSERT_PROGRESS_HEARTBEAT_SECONDS),
    )
    try:
        return max(float(raw), 0.0)
    except ValueError:
        return float(DEFAULT_GOLD_INSERT_PROGRESS_HEARTBEAT_SECONDS)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _count_consolidated_csv_data_rows(path: Path) -> int:
    """Conta linhas de dados (exclui cabecalho) sem materializar o CSV inteiro."""
    with path.open(encoding="utf-8") as fh:
        reader = csv.reader(fh)
        if next(reader, None) is None:
            return 0
        return sum(1 for _ in reader)


def _lead_gold_insert_lookup_chunk_size() -> int:
    raw = os.getenv(
        "NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE",
        str(DEFAULT_GOLD_INSERT_LOOKUP_CHUNK_SIZE),
    )
    try:
        return max(min(int(raw), 50_000), 50)
    except ValueError:
        return DEFAULT_GOLD_INSERT_LOOKUP_CHUNK_SIZE


def _build_insert_leads_progress_event(
    processed_rows: int,
    total_rows: int,
    *,
    committed_rows: int,
    content_hash: str | None = None,
    arquivo_sha256: str | None = None,
) -> PipelineProgressEvent:
    pct = 100 if total_rows <= 0 else min(int((processed_rows / total_rows) * 100), 100)
    meta: dict[str, Any] = {
        "committed_rows": committed_rows,
        "total_rows": total_rows,
    }
    if content_hash is not None:
        meta["content_hash"] = content_hash
    if arquivo_sha256 is not None:
        meta["arquivo_sha256"] = arquivo_sha256
    return PipelineProgressEvent(
        step="insert_leads",
        label=f"Inserindo leads Gold no banco ({processed_rows}/{total_rows})",
        pct=pct,
        meta=meta,
    )


def _inserir_leads_gold(
    batch: LeadBatch,
    consolidated_path: Path,
    db: Session,
    *,
    on_progress: Callable[[PipelineProgressEvent], None] | None = None,
    resume_context: dict[str, Any] | None = None,
) -> int:
    """Le o CSV validado e insere leads na tabela `lead`."""
    if not consolidated_path.exists():
        raise FileNotFoundError(
            f"CSV consolidado da pipeline Gold nao encontrado: {consolidated_path}"
        )
    content_hash = _sha256_file(consolidated_path)
    batch_file_hash = _lead_batch_file_sha256(batch)

    total_rows = _count_consolidated_csv_data_rows(consolidated_path)
    if total_rows <= 0:
        raise ValueError(
            f"CSV consolidado da pipeline Gold vazio para o batch {batch.id}"
        )

    origem = (batch.origem_lote or "proponente").strip().lower()
    is_ativacao_batch = origem == "ativacao" and batch.ativacao_id is not None

    raw_tipo_prop = (batch.tipo_lead_proponente or "").strip().lower() or "entrada_evento"
    tipo_lead_proponente = (
        TipoLead.BILHETERIA if raw_tipo_prop == "bilheteria" else TipoLead.ENTRADA_EVENTO
    )

    count = 0
    updated_count = 0
    normalized_resume_context = _normalize_insert_resume_context(resume_context)
    pending_since_commit = 0
    commit_batch_size = _lead_gold_insert_commit_batch_size(db)
    max_transaction_seconds = _lead_gold_insert_max_transaction_seconds(db)
    heartbeat_interval = _lead_gold_progress_heartbeat_seconds()
    resume_from_rows = 0
    if normalized_resume_context is not None:
        resume_content_hash = _normalize_sha256(normalized_resume_context.get("content_hash"))
        if resume_content_hash is not None and resume_content_hash != content_hash:
            _log_pipeline_event(
                logging.WARNING,
                "insert.resume_ignored",
                batch_id=batch.id,
                reason="content_hash_mismatch",
                resume_content_hash=resume_content_hash,
                current_content_hash=content_hash,
            )
            normalized_resume_context = None
        resume_batch_file_hash = (
            _normalize_sha256(normalized_resume_context.get("arquivo_sha256"))
            if normalized_resume_context is not None
            else None
        )
        if (
            normalized_resume_context is not None
            and resume_batch_file_hash is not None
            and resume_batch_file_hash != batch_file_hash
        ):
            _log_pipeline_event(
                logging.WARNING,
                "insert.resume_ignored",
                batch_id=batch.id,
                reason="batch_file_hash_mismatch",
                resume_batch_file_hash=resume_batch_file_hash,
                current_batch_file_hash=batch_file_hash,
            )
            normalized_resume_context = None
    if normalized_resume_context is not None:
        resume_total_rows = normalized_resume_context.get("total_rows")
        if resume_total_rows is not None and resume_total_rows != total_rows:
            _log_pipeline_event(
                logging.WARNING,
                "insert.resume_ignored",
                batch_id=batch.id,
                resume_from_rows=normalized_resume_context["committed_rows"],
                resume_total_rows=resume_total_rows,
                current_total_rows=total_rows,
            )
            normalized_resume_context = None
        else:
            resume_from_rows = min(normalized_resume_context["committed_rows"], total_rows)

    processed_rows = resume_from_rows
    last_committed_rows = resume_from_rows
    started_at = time_module.perf_counter()
    last_progress_emit_at = started_at
    chunk_started_at = started_at
    metrics = GoldInsertMetrics(total_rows=total_rows)
    chunk_row_sizes: list[int] = []

    _log_pipeline_event(
        logging.INFO,
        "insert.start",
        batch_id=batch.id,
        evento_id=batch.evento_id,
        origem_lote=origem,
        total_rows=total_rows,
        resume_from_rows=resume_from_rows or None,
        commit_batch_size=commit_batch_size,
        max_transaction_seconds=max_transaction_seconds or None,
        uses_supabase_pooler_6543=_lead_gold_uses_supabase_transaction_pooler(db),
        consolidated_path=str(consolidated_path),
        lookup_chunk_size=_lead_gold_insert_lookup_chunk_size(),
    )
    if on_progress is not None:
        on_progress(
            _build_insert_leads_progress_event(
                processed_rows=processed_rows,
                total_rows=total_rows,
                committed_rows=last_committed_rows,
                content_hash=content_hash,
                arquivo_sha256=batch_file_hash,
            )
        )

    lookup_chunk_size = _lead_gold_insert_lookup_chunk_size()
    lookup_context = LeadLookupContext([], set(), set())
    candidate_lead_ids: set[int] = set()
    activation_insert_context: ActivationInsertContext | None = None
    if is_ativacao_batch and batch.evento_id is not None:
        activation_insert_context = _load_activation_insert_context(db, batch=batch)
    activation_relation_cache_loaded_ids: set[int] = set()
    existing_ativacao_links_by_lead_id: dict[int, AtivacaoLead] = {}
    existing_lead_events_by_lead_id: dict[int, LeadEvento] = {}
    first_ativacao_bulk = True

    with consolidated_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for _ in range(resume_from_rows):
            if next(reader, None) is None:
                break

        window: list[dict[str, Any]] = []

        def _refill_lookup_window() -> bool:
            window.clear()
            while len(window) < lookup_chunk_size:
                try:
                    window.append(next(reader))
                except StopIteration:
                    break
            return bool(window)

        while _refill_lookup_window():
            payload_build_started_at = time_module.perf_counter()
            lead_payloads = [_build_lead_payload(row, batch) for row in window]
            metrics.time_in_payload_build_ms += _duration_ms(payload_build_started_at)

            lookup_context_started_at = time_module.perf_counter()
            pending_offset = processed_rows - resume_from_rows
            batch_tuples = [
                (lead_payloads[i], resume_from_rows + pending_offset + i + 1)
                for i in range(len(window))
            ]
            chunk_lookup = _load_lead_lookup_context(
                db,
                batch_tuples,
                canonical_evento_id=batch.evento_id,
            )
            merge_lead_lookup_context(lookup_context, chunk_lookup)
            metrics.time_in_lookup_context_ms += _duration_ms(lookup_context_started_at)

            for c in chunk_lookup.candidates:
                lid = getattr(c, "id", None)
                if lid is not None:
                    candidate_lead_ids.add(int(lid))

            if (
                activation_insert_context is not None
                and first_ativacao_bulk
                and candidate_lead_ids
            ):
                activation_relation_cache_loaded_ids = set(candidate_lead_ids)
                existing_ativacao_links_by_lead_id = _load_existing_ativacao_leads(
                    db,
                    ativacao_id=activation_insert_context.ativacao_id,
                    lead_ids=candidate_lead_ids,
                )
                existing_lead_events_by_lead_id = _load_existing_lead_eventos(
                    db,
                    evento_id=activation_insert_context.evento_id,
                    lead_ids=candidate_lead_ids,
                )
                first_ativacao_bulk = False

            for row, lead_payload in zip(window, lead_payloads, strict=False):
                row_bytes = len(json.dumps(row, ensure_ascii=False).encode("utf-8"))
                metrics.bytes_total += row_bytes
                chunk_row_sizes.append(row_bytes)

                if pending_since_commit == 0:
                    _configure_lead_gold_statement_timeout(db)

                lookup_started_at = time_module.perf_counter()
                lead = find_existing_lead_from_lookup(
                    lead_payload,
                    lookup_context,
                    canonical_evento_id=batch.evento_id,
                )
                metrics.time_in_lookup_ms += _duration_ms(lookup_started_at)
                if lead is None:
                    metrics.fallback_lookup_calls += 1
                    fallback_lookup_started_at = time_module.perf_counter()
                    lead = _find_existing_lead(
                        db,
                        lead_payload,
                        anchored_evento_id=batch.evento_id,
                    )
                    metrics.time_in_lookup_ms += _duration_ms(fallback_lookup_started_at)
                lead_was_created = False
                if lead is None:
                    flush_started_at = time_module.perf_counter()
                    try:
                        with db.begin_nested():
                            lead = Lead(**lead_payload, batch_id=batch.id)
                            db.add(lead)
                            db.flush()
                    except IntegrityError as exc:
                        if not is_ticketing_dedupe_integrity_error(exc):
                            raise
                        lead = find_lead_by_ticketing_dedupe_key(db, lead_payload)
                        if lead is None:
                            raise RuntimeError(
                                "Ticketing dedupe conflict without resolvable row"
                            ) from exc
                        _merge_lead_payload_if_missing(lead, lead_payload)
                        db.add(lead)
                        db.flush()
                        metrics.time_in_flush_ms += _duration_ms(flush_started_at)
                        metrics.flush_calls += 2
                        updated_count += 1
                        lead_was_created = False
                    else:
                        metrics.time_in_flush_ms += _duration_ms(flush_started_at)
                        metrics.flush_calls += 1
                        count += 1
                        lead_was_created = True
                else:
                    _merge_lead_payload_if_missing(lead, lead_payload)
                    db.add(lead)
                    updated_count += 1
                if lead.id is not None and int(lead.id) not in candidate_lead_ids:
                    lookup_context.candidates.append(lead)
                    candidate_lead_ids.add(int(lead.id))
                if lead.id is not None and activation_insert_context is not None and lead_was_created:
                    activation_relation_cache_loaded_ids.add(int(lead.id))
                if lead.id is not None and batch.evento_id is not None:
                    if is_ativacao_batch:
                        if (
                            activation_insert_context is not None
                            and not lead_was_created
                            and int(lead.id) not in activation_relation_cache_loaded_ids
                        ):
                            existing_ativacao_links_by_lead_id.update(
                                _load_existing_ativacao_leads(
                                    db,
                                    ativacao_id=activation_insert_context.ativacao_id,
                                    lead_ids={int(lead.id)},
                                )
                            )
                            existing_lead_events_by_lead_id.update(
                                _load_existing_lead_eventos(
                                    db,
                                    evento_id=activation_insert_context.evento_id,
                                    lead_ids={int(lead.id)},
                                )
                            )
                            activation_relation_cache_loaded_ids.add(int(lead.id))
                        metrics.ativacao_link_calls += 1
                        ativacao_link_started_at = time_module.perf_counter()
                        if activation_insert_context is None:
                            ativacao_lead = _get_or_create_ativacao_lead(
                                db,
                                ativacao_id=int(batch.ativacao_id),
                                lead_id=int(lead.id),
                            )
                        else:
                            ativacao_lead, ativacao_link_flush_ms = _get_or_create_ativacao_lead_fast(
                                db,
                                lead_id=int(lead.id),
                                context=activation_insert_context,
                                existing_links_by_lead_id=existing_ativacao_links_by_lead_id,
                            )
                            metrics.time_in_flush_ms += ativacao_link_flush_ms
                            if ativacao_link_flush_ms > 0:
                                metrics.flush_calls += 1
                        metrics.time_in_ativacao_link_ms += _duration_ms(ativacao_link_started_at)
                        metrics.lead_event_calls += 1
                        lead_event_started_at = time_module.perf_counter()
                        if activation_insert_context is None or ativacao_lead.id is None:
                            ensure_lead_event(
                                db,
                                lead_id=lead.id,
                                evento_id=batch.evento_id,
                                source_kind=LeadEventoSourceKind.ACTIVATION,
                                source_ref_id=ativacao_lead.id,
                            )
                        else:
                            _ensure_activation_lead_event_fast(
                                db,
                                lead_id=int(lead.id),
                                source_ref_id=int(ativacao_lead.id),
                                context=activation_insert_context,
                                existing_events_by_lead_id=existing_lead_events_by_lead_id,
                            )
                        lookup_context.lead_ids_with_any_event_link.add(int(lead.id))
                        lookup_context.lead_ids_with_target_event_link.add(int(lead.id))
                        metrics.time_in_lead_event_ms += _duration_ms(lead_event_started_at)
                    else:
                        metrics.lead_event_calls += 1
                        lead_event_started_at = time_module.perf_counter()
                        ensure_lead_event(
                            db,
                            lead_id=lead.id,
                            evento_id=batch.evento_id,
                            source_kind=LeadEventoSourceKind.LEAD_BATCH,
                            source_ref_id=batch.id,
                            tipo_lead=tipo_lead_proponente,
                        )
                        metrics.time_in_lead_event_ms += _duration_ms(lead_event_started_at)
                processed_rows += 1
                pending_since_commit += 1
                now: float | None = None
                if (
                    on_progress is not None
                    and heartbeat_interval > 0
                    and 0 < pending_since_commit < commit_batch_size
                ):
                    now = time_module.perf_counter()
                    if (now - last_progress_emit_at) >= heartbeat_interval:
                        event = _build_insert_leads_progress_event(
                            processed_rows=processed_rows,
                            total_rows=total_rows,
                            committed_rows=last_committed_rows,
                            content_hash=content_hash,
                            arquivo_sha256=batch_file_hash,
                        )
                        on_progress(event)
                        last_progress_emit_at = now
                        _log_pipeline_event(
                            logging.INFO,
                            "insert.heartbeat",
                            batch_id=batch.id,
                            processed_rows=processed_rows,
                            total_rows=total_rows,
                            pct=event.pct,
                            pending_since_commit=pending_since_commit,
                            heartbeat_interval_seconds=heartbeat_interval,
                            elapsed_ms=round((now - started_at) * 1000),
                        )
                commit_check_at = now if now is not None else time_module.perf_counter()
                commit_due_to_time_budget = (
                    max_transaction_seconds > 0
                    and pending_since_commit > 0
                    and (commit_check_at - chunk_started_at) >= max_transaction_seconds
                )
                if pending_since_commit >= commit_batch_size or commit_due_to_time_budget:
                    commit_started_at = time_module.perf_counter()
                    db.commit()
                    metrics.time_in_commit_ms += _duration_ms(commit_started_at)
                    metrics.chunks_committed += 1
                    pending_since_commit = 0
                    commit_at = commit_check_at
                    last_committed_rows = processed_rows
                    event = _build_insert_leads_progress_event(
                        processed_rows=processed_rows,
                        total_rows=total_rows,
                        committed_rows=last_committed_rows,
                        content_hash=content_hash,
                        arquivo_sha256=batch_file_hash,
                    )
                    if on_progress is not None:
                        on_progress(event)
                    last_progress_emit_at = commit_at
                    chunk_started_at = commit_at
                    _log_pipeline_event(
                        logging.INFO,
                        "insert.chunk_committed",
                        batch_id=batch.id,
                        processed_rows=processed_rows,
                        total_rows=total_rows,
                        pct=event.pct,
                        commit_batch_size=commit_batch_size,
                        commit_reason="transaction_seconds" if commit_due_to_time_budget else "batch_size",
                        max_transaction_seconds=max_transaction_seconds or None,
                        elapsed_ms=round((commit_at - started_at) * 1000),
                    )
    
        if pending_since_commit > 0:
            commit_started_at = time_module.perf_counter()
            db.commit()
            metrics.time_in_commit_ms += _duration_ms(commit_started_at)
            metrics.chunks_committed += 1
            commit_at = time_module.perf_counter()
            last_committed_rows = processed_rows
            event = _build_insert_leads_progress_event(
                processed_rows=processed_rows,
                total_rows=total_rows,
                committed_rows=last_committed_rows,
                content_hash=content_hash,
                arquivo_sha256=batch_file_hash,
            )
            if on_progress is not None:
                on_progress(event)
            last_progress_emit_at = commit_at
            _log_pipeline_event(
                logging.INFO,
                "insert.chunk_committed",
                batch_id=batch.id,
                processed_rows=processed_rows,
                total_rows=total_rows,
                pct=event.pct,
                commit_batch_size=commit_batch_size,
                elapsed_ms=round((commit_at - started_at) * 1000),
            )
    metrics.created_rows = count
    metrics.updated_rows = updated_count
    metrics.time_in_insert_total_ms = _duration_ms(started_at)
    processed_in_run = processed_rows - resume_from_rows
    pending_row_count = max(0, total_rows - resume_from_rows)
    metrics.avg_row_bytes = round(metrics.bytes_total / pending_row_count, 2) if pending_row_count else 0.0
    metrics.avg_chunk_rows = round(processed_in_run / metrics.chunks_committed, 2) if metrics.chunks_committed else 0.0
    metrics.estimated_chunk_bytes = (
        round(metrics.avg_row_bytes * metrics.avg_chunk_rows, 2) if metrics.avg_chunk_rows else 0.0
    )
    metrics.rows_per_second = (
        round(processed_in_run / (metrics.time_in_insert_total_ms / 1000), 2)
        if metrics.time_in_insert_total_ms > 0
        else 0.0
    )
    _log_pipeline_event(
        logging.INFO,
        "insert.metrics",
        batch_id=batch.id,
        metrics=asdict(metrics),
    )
    _log_pipeline_event(
        logging.INFO,
        "insert.completed",
        batch_id=batch.id,
        created_rows=count,
        updated_rows=updated_count,
        processed_rows=processed_rows,
        total_rows=total_rows,
        elapsed_ms=round((time_module.perf_counter() - started_at) * 1000),
    )
    return count


async def executar_pipeline_gold(batch_id: int) -> None:
    """Background task: materializa Silver CSV -> run_pipeline -> promove Gold."""
    worker_engine = _resolve_worker_engine()
    tmp_dir = TMP_ROOT / str(batch_id)
    report_data: dict[str, Any] | None = None
    failure_step = "queued"

    last_pipeline_event: dict[str, PipelineProgressEvent | None] = {"ev": None}

    def on_progress(event: PipelineProgressEvent) -> None:
        last_pipeline_event["ev"] = event
        _persist_pipeline_progress(worker_engine, batch_id, event)

    async def _run_pipeline_with_heartbeat(cfg: PipelineConfig) -> PipelineResult:
        stop = asyncio.Event()
        interval = pipeline_heartbeat_during_run_seconds()

        async def heartbeat_loop() -> None:
            while not stop.is_set():
                try:
                    await asyncio.wait_for(stop.wait(), timeout=interval)
                    return
                except asyncio.TimeoutError:
                    ev = last_pipeline_event["ev"]
                    try:
                        if ev is not None:
                            await asyncio.to_thread(_persist_pipeline_progress, worker_engine, batch_id, ev)
                        else:
                            await asyncio.to_thread(
                                _persist_pipeline_progress,
                                worker_engine,
                                batch_id,
                                PipelineProgressEvent(
                                    step="normalize_rows",
                                    label=PIPELINE_PROGRESS_LABELS["normalize_rows"],
                                    pct=None,
                                    meta=None,
                                ),
                            )
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(
                            "lead_gold_pipeline.heartbeat.failed batch_id=%r err=%r",
                            batch_id,
                            exc,
                        )

        hb = asyncio.create_task(heartbeat_loop())
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, run_pipeline, cfg)
        finally:
            stop.set()
            hb.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await hb

    try:
        _log_pipeline_event(logging.INFO, "execution.start", batch_id=batch_id)
        execution_started_at = time_module.perf_counter()
        with _SqlObservabilityCollector(worker_engine) as sql_observability:
            with Session(worker_engine, expire_on_commit=False) as db:
                set_internal_service_db_context(db)
                batch = load_batch_without_bronze(db, batch_id)
                if not batch:
                    logger.error("Batch %s nao encontrado para execucao do pipeline.", batch_id)
                    return

                _log_pipeline_event(
                    logging.INFO,
                    "batch.loaded",
                    batch_id=batch_id,
                    stage=batch.stage,
                    pipeline_status=batch.pipeline_status,
                    evento_id=batch.evento_id,
                    origem_lote=batch.origem_lote,
                )

                current_step = None
                if isinstance(batch.pipeline_progress, dict):
                    current_step = str(batch.pipeline_progress.get("step") or "").strip() or None
                if current_step == "queued":
                    queue_pipeline_batch(batch)
                    resume_context = _resume_context_from_batch(batch)
                    db.add(batch)
                    db.commit()
                    _log_pipeline_event(
                        logging.INFO,
                        "queued",
                        batch_id=batch_id,
                        stage=batch.stage,
                        pipeline_status=batch.pipeline_status,
                    )
                else:
                    resume_context = _resume_context_from_batch(batch)
                    failure_step = current_step or "silver_csv"
                if current_step in {None, "queued"}:
                    failure_step = "silver_csv"
                    set_pipeline_progress(batch, step="silver_csv", resume_context=resume_context)
                    db.add(batch)
                    db.commit()

                if batch.evento_id is not None:
                    evento = db.get(Evento, batch.evento_id)
                    fail_reasons: list[str] = []
                    if evento is not None and _canonical_event_date_iso(evento) is None:
                        fail_reasons.append("EVENTO_SEM_DATA_CANONICA")
                    if fail_reasons:
                        silver_row_count = _silver_row_count(db, batch_id=batch_id)
                        report_data = _build_contextual_pipeline_report(
                            batch_id=batch_id,
                            silver_row_count=silver_row_count,
                            fail_reasons=fail_reasons,
                        )
                        _persist_contextual_pipeline_failure(db, batch=batch, report_data=report_data)
                        _log_pipeline_event(
                            logging.WARNING,
                            "blocked",
                            batch_id=batch_id,
                            failure_step=failure_step,
                            fail_reasons=fail_reasons,
                        )
                        logger.info(
                            "Pipeline batch %s bloqueado por contexto: %s",
                            batch_id,
                            ",".join(fail_reasons),
                        )
                        return

                csv_path = materializar_silver_como_csv(batch_id, db)
                _log_pipeline_event(
                    logging.INFO,
                    "silver_csv.materialized",
                    batch_id=batch_id,
                    csv_path=str(csv_path),
                )

            output_root = tmp_dir / "output"
            config = PipelineConfig(
                lote_id=str(batch_id),
                input_files=[csv_path],
                output_root=output_root,
                anchored_on_evento_id=batch.evento_id is not None,
                on_progress=on_progress,
            )

            failure_step = "run_pipeline"
            _log_pipeline_event(
                logging.INFO,
                "run_pipeline.start",
                batch_id=batch_id,
                input_files=[str(path) for path in config.input_files],
                output_root=str(output_root),
                anchored_on_evento_id=config.anchored_on_evento_id,
            )
            run_pipeline_started_at = time_module.perf_counter()
            result = await _run_pipeline_with_heartbeat(config)
            _log_pipeline_event(
                logging.INFO,
                "run_pipeline.completed",
                batch_id=batch_id,
                status=result.status,
                decision=result.decision,
                report_path=str(result.report_path),
                consolidated_path=str(result.consolidated_path),
                elapsed_ms=_duration_ms(run_pipeline_started_at),
            )

            report_data = {}
            if result.report_path.exists():
                report_data = json.loads(result.report_path.read_text(encoding="utf-8"))

            pipeline_status = _pipeline_status_from_str(result.status)

            with Session(worker_engine, expire_on_commit=False) as db:
                set_internal_service_db_context(db)
                batch = load_batch_without_bronze(db, batch_id)
                if not batch:
                    logger.error("Batch %s nao encontrado para finalizar pipeline.", batch_id)
                    return

                if result.decision == "promote":
                    failure_step = "insert_leads"
                    set_pipeline_progress(batch, step="insert_leads", resume_context=resume_context)
                    db.add(batch)
                    db.commit()
                    _log_pipeline_event(
                        logging.INFO,
                        "insert.dispatch",
                        batch_id=batch_id,
                        consolidated_path=str(result.consolidated_path),
                    )
                    _inserir_leads_gold(
                        batch,
                        result.consolidated_path,
                        db,
                        on_progress=on_progress,
                        resume_context=resume_context,
                    )
                    batch.stage = BatchStage.GOLD
                else:
                    batch.stage = BatchStage.SILVER

                failure_step = "persist_result"
                batch.pipeline_report = report_data
                batch.pipeline_status = pipeline_status
                disc, issues, inv_n = _gold_dq_snapshot_from_report(report_data)
                batch.gold_dq_discarded_rows = disc
                batch.gold_dq_issue_counts = issues
                batch.gold_dq_invalid_records_total = inv_n
                _clear_pipeline_progress(batch)

                db.add(batch)
                db.commit()
                _log_pipeline_event(
                    logging.INFO,
                    "persist_result.completed",
                    batch_id=batch_id,
                    stage=batch.stage,
                    pipeline_status=batch.pipeline_status,
                    discarded_rows=disc,
                    invalid_records_total=inv_n,
                )

            _log_pipeline_event(
                logging.INFO,
                "execution.metrics",
                batch_id=batch_id,
                total_elapsed_ms=_duration_ms(execution_started_at),
                sql_summary=sql_observability.summary(),
            )

        logger.info(
            "Pipeline batch %s concluido: status=%s decision=%s",
            batch_id,
            result.status,
            result.decision,
        )

    except Exception as exc:
        _log_pipeline_event(
            logging.ERROR,
            "execution.failed",
            batch_id=batch_id,
            failure_step=failure_step,
            exception_type=exc.__class__.__name__,
            detail=_compact_exception_detail(exc),
        )
        logger.exception("Falha na execucao do pipeline para batch %s.", batch_id)
        try:
            with Session(worker_engine, expire_on_commit=False) as db:
                set_internal_service_db_context(db)
                batch = load_batch_without_bronze(db, batch_id)
                if batch is None:
                    return
                silver_row_count = _silver_row_count(db, batch_id=batch_id)
                failure_report = _build_pipeline_exception_report(
                    batch_id=batch_id,
                    silver_row_count=silver_row_count,
                    failure_step=failure_step,
                    exc=exc,
                    report_data=report_data,
                    resume_context=_resume_context_from_batch(batch),
                )
                batch.pipeline_status = PipelineStatus.FAIL
                batch.pipeline_report = failure_report
                disc, issues, inv_n = _gold_dq_snapshot_from_report(failure_report)
                batch.gold_dq_discarded_rows = disc
                batch.gold_dq_issue_counts = issues
                batch.gold_dq_invalid_records_total = inv_n
                _clear_pipeline_progress(batch)
                db.add(batch)
                db.commit()
                _log_pipeline_event(
                    logging.INFO,
                    "failure_persisted",
                    batch_id=batch_id,
                    failure_step=failure_step,
                    pipeline_status=batch.pipeline_status,
                )
        except Exception:
            _log_pipeline_event(
                logging.ERROR,
                "failure_persist_failed",
                batch_id=batch_id,
                failure_step=failure_step,
            )
            logger.exception("Falha ao persistir status FAIL para batch %s.", batch_id)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def executar_pipeline_gold_em_thread(batch_id: int) -> None:
    """Executa a pipeline Gold em thread separada para nao bloquear o event loop da API."""
    asyncio.run(executar_pipeline_gold(batch_id))
