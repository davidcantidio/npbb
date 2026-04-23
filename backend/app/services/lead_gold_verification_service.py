from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import math
import numbers
import re
from typing import Any, Iterable
from uuid import uuid4

from sqlalchemy import delete
from sqlmodel import Session, select

from app.db.database import build_worker_engine, set_internal_service_db_context
from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.lead_public_models import (
    Lead,
    LeadEvento,
    LeadGoldVerificationResult,
    LeadGoldVerificationRun,
    LeadImportEtlStagingRow,
)
from app.models.models import Evento, Usuario
from app.services.lead_event_service import EventNameResolution, resolve_unique_evento_by_name
from app.utils.cpf import is_valid_cpf, normalize_cpf


class BirthDateIssue(str):
    MISSING = "missing"
    UNPARSEABLE = "unparseable"
    FUTURE = "future"
    BEFORE_MIN = "before_min"

RULES_VERSION = "gold_verification_v1"
REPROCESS_KIND = "gold_verification"
_BIRTH_DATE_MIN = date(1900, 1, 1)
_EVENT_SOURCE_PRIORITY = {
    "manual_reconciled": 5,
    "ativacao": 4,
    "event_id_direct": 3,
    "lead_batch": 2,
    "evento_nome_backfill": 1,
}


@dataclass(frozen=True)
class GoldVerificationRunResult:
    run_id: str
    technical_batch_ids: list[int]
    analyzed_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int


@dataclass
class _Candidate:
    lead: Lead
    source_batch: LeadBatch | None
    source_file: str
    source_sheet: str
    source_row: int
    source_row_ref: str
    resolved_evento_id: int | None
    resolved_evento_nome: str
    canonical_event_date: str | None
    normalized_cpf: str
    normalized_phone: str
    birth_date_issue: BirthDateIssue | None
    reason_codes: list[str]
    dedupe_key: tuple[str, str] | None = None
    dedupe_rank: int = 1
    duplicate_of_lead_id: int | None = None
    outcome: str = "valid"

    @property
    def source_batch_id(self) -> int | None:
        return int(self.source_batch.id) if self.source_batch and self.source_batch.id is not None else None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _event_priority(source_kind: Any) -> int:
    return _EVENT_SOURCE_PRIORITY.get(str(source_kind or ""), 0)


def _canonical_event_date_iso(evento: Evento | None) -> str | None:
    if evento is None:
        return None
    canonical = evento.data_inicio_realizada or evento.data_inicio_prevista
    return canonical.isoformat() if canonical is not None else None


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _digits_only(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        text = str(value).strip()
    elif isinstance(value, numbers.Integral):
        text = str(int(value))
    elif isinstance(value, numbers.Real):
        float_value = float(value)
        if not math.isfinite(float_value):
            return ""
        text = str(int(float_value)) if float_value.is_integer() else str(value).strip()
    else:
        text = str(value).strip()
    return re.sub(r"\D+", "", text)


def _normalize_phone(value: Any) -> str:
    return _digits_only(value)


def _normalize_data_nascimento(raw: str, *, ref_date: date) -> tuple[str, str | None]:
    text = _clean_text(raw)
    if not text:
        return "", BirthDateIssue.MISSING
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        return "", BirthDateIssue.UNPARSEABLE
    if parsed < _BIRTH_DATE_MIN:
        return "", BirthDateIssue.BEFORE_MIN
    if parsed > ref_date:
        return "", BirthDateIssue.FUTURE
    return parsed.isoformat(), None


def _gold_dq_snapshot_from_report(report_data: dict[str, Any]) -> tuple[int | None, dict[str, int] | None, int | None]:
    if not report_data:
        return None, None, None
    totals = report_data.get("totals") or {}
    discarded = totals.get("discarded_rows")
    quality_metrics = report_data.get("quality_metrics")
    invalid_records = report_data.get("invalid_records")
    parsed_quality_metrics = quality_metrics if isinstance(quality_metrics, dict) else None
    invalid_total = len(invalid_records) if isinstance(invalid_records, list) else None
    return int(discarded) if discarded is not None else None, parsed_quality_metrics, invalid_total


def _normalize_event_key(value: str) -> str:
    return _clean_text(value).casefold()


def _build_row_data(lead: Lead) -> dict[str, Any]:
    return {
        "lead_id": int(lead.id or 0),
        "batch_id": int(lead.batch_id) if lead.batch_id is not None else None,
        "cpf": _clean_text(lead.cpf),
        "email": _clean_text(lead.email),
        "telefone": _clean_text(lead.telefone),
        "evento_nome": _clean_text(lead.evento_nome),
        "sessao": _clean_text(lead.sessao),
        "data_nascimento": lead.data_nascimento.isoformat() if lead.data_nascimento is not None else "",
        "data_criacao": lead.data_criacao.isoformat() if lead.data_criacao is not None else "",
    }


def _zero_quality_metrics() -> dict[str, int]:
    return {
        "cpf_invalid_discarded": 0,
        "telefone_invalid": 0,
        "data_evento_invalid": 0,
        "data_nascimento_invalid": 0,
        "data_nascimento_missing": 0,
        "duplicidades_cpf_evento": 0,
        "cidade_fora_mapeamento": 0,
        "localidade_invalida": 0,
        "localidade_nao_resolvida": 0,
        "localidade_fora_brasil": 0,
        "localidade_cidade_uf_inconsistente": 0,
    }


def _increment_metrics_from_reason(reason: str, metrics: dict[str, int]) -> None:
    joined_upper = reason.upper()
    if "CPF_INVALIDO" in joined_upper:
        metrics["cpf_invalid_discarded"] += 1
    if "TELEFONE_INVALIDO" in joined_upper:
        metrics["telefone_invalid"] += 1
    if "DATA_EVENTO_INVALIDA" in joined_upper:
        metrics["data_evento_invalid"] += 1
    if "DUPLICIDADE_CPF_EVENTO" in joined_upper:
        metrics["duplicidades_cpf_evento"] += 1


def _gate_warnings_from_metrics(metrics: dict[str, int]) -> list[str]:
    warnings: list[str] = []
    if metrics["cpf_invalid_discarded"] > 0:
        warnings.append("CPF_INVALIDO_DESCARTADO")
    if metrics["telefone_invalid"] > 0:
        warnings.append("TELEFONE_INVALIDO")
    if metrics["data_evento_invalid"] > 0:
        warnings.append("DATA_EVENTO_INVALIDA")
    if metrics["duplicidades_cpf_evento"] > 0:
        warnings.append("DUPLICIDADE_CPF_EVENTO")
    if metrics["data_nascimento_missing"] > 0:
        warnings.append("DATA_NASCIMENTO_AUSENTE")
    if metrics["data_nascimento_invalid"] > 0:
        warnings.append("DATA_NASCIMENTO_INVALIDA")
    return warnings


def _resolve_requested_by(
    session: Session,
    *,
    requested_by: int | None,
    source_batches: dict[int, LeadBatch],
) -> int:
    if requested_by is not None:
        return int(requested_by)
    for batch in source_batches.values():
        if batch.enviado_por is not None:
            return int(batch.enviado_por)
    first_user = session.exec(select(Usuario).order_by(Usuario.id)).first()
    if first_user is None or first_user.id is None:
        raise RuntimeError("Nao existe usuario para assinar os batches tecnicos de gold verification.")
    return int(first_user.id)


def _load_scope_batch_ids(session: Session, batch_ids: list[int] | None) -> list[int]:
    if batch_ids:
        return sorted({int(batch_id) for batch_id in batch_ids})
    rows = session.exec(select(Lead.batch_id).where(Lead.batch_id.is_not(None))).all()
    return sorted({int(batch_id) for batch_id in rows if batch_id is not None})


def _load_source_batches(session: Session, batch_ids: list[int]) -> dict[int, LeadBatch]:
    if not batch_ids:
        return {}
    rows = session.exec(select(LeadBatch).where(LeadBatch.id.in_(batch_ids))).all()
    return {int(row.id): row for row in rows if row.id is not None}


def _load_staging_metadata(session: Session, lead_ids: list[int]) -> dict[int, LeadImportEtlStagingRow]:
    if not lead_ids:
        return {}
    rows = session.exec(
        select(LeadImportEtlStagingRow)
        .where(LeadImportEtlStagingRow.merged_lead_id.in_(lead_ids))
        .order_by(
            LeadImportEtlStagingRow.merged_lead_id.asc(),
            LeadImportEtlStagingRow.source_row_number.asc(),
            LeadImportEtlStagingRow.id.asc(),
        )
    ).all()
    out: dict[int, LeadImportEtlStagingRow] = {}
    for row in rows:
        if row.merged_lead_id is None:
            continue
        out.setdefault(int(row.merged_lead_id), row)
    return out


def _load_best_lead_eventos(session: Session, lead_ids: list[int]) -> dict[int, LeadEvento]:
    if not lead_ids:
        return {}
    rows = session.exec(
        select(LeadEvento)
        .where(LeadEvento.lead_id.in_(lead_ids))
        .order_by(LeadEvento.lead_id.asc(), LeadEvento.created_at.asc(), LeadEvento.id.asc())
    ).all()
    best_by_lead: dict[int, LeadEvento] = {}
    for row in rows:
        lead_id = int(row.lead_id)
        current = best_by_lead.get(lead_id)
        if current is None or _event_priority(row.source_kind) > _event_priority(current.source_kind):
            best_by_lead[lead_id] = row
    return best_by_lead


def _load_evento_maps(
    session: Session,
    *,
    source_batches: dict[int, LeadBatch],
    lead_eventos: dict[int, LeadEvento],
    leads: list[Lead],
) -> tuple[dict[int, Evento], dict[str, EventNameResolution]]:
    event_ids: set[int] = set()
    for batch in source_batches.values():
        if batch.evento_id is not None:
            event_ids.add(int(batch.evento_id))
    for lead_evento in lead_eventos.values():
        event_ids.add(int(lead_evento.evento_id))
    events = session.exec(select(Evento).where(Evento.id.in_(event_ids))).all() if event_ids else []
    event_map = {int(evento.id): evento for evento in events if evento.id is not None}

    names = sorted({_clean_text(lead.evento_nome) for lead in leads if _clean_text(lead.evento_nome)})
    name_resolution = {name: resolve_unique_evento_by_name(session, name) for name in names}
    return event_map, name_resolution


def _classify_candidates(
    session: Session,
    *,
    leads: list[Lead],
    source_batches: dict[int, LeadBatch],
    requested_by: int,
) -> list[_Candidate]:
    lead_ids = [int(lead.id) for lead in leads if lead.id is not None]
    staging = _load_staging_metadata(session, lead_ids)
    best_lead_eventos = _load_best_lead_eventos(session, lead_ids)
    event_map, name_resolution = _load_evento_maps(
        session,
        source_batches=source_batches,
        lead_eventos=best_lead_eventos,
        leads=leads,
    )

    candidates: list[_Candidate] = []
    ref_date = _now_utc().date()
    for lead in sorted(leads, key=lambda item: (item.data_criacao, item.id or 0)):
        lead_id = int(lead.id or 0)
        batch = source_batches.get(int(lead.batch_id)) if lead.batch_id is not None else None
        staging_row = staging.get(lead_id)

        resolved_evento_id: int | None = None
        resolved_evento_nome = ""
        lead_evento = best_lead_eventos.get(lead_id)
        if lead_evento is not None:
            resolved_evento_id = int(lead_evento.evento_id)
        elif batch is not None and batch.evento_id is not None:
            resolved_evento_id = int(batch.evento_id)
        else:
            resolution = name_resolution.get(_clean_text(lead.evento_nome))
            if resolution is not None and resolution.status == "resolved" and resolution.evento_id is not None:
                resolved_evento_id = int(resolution.evento_id)
        evento = event_map.get(resolved_evento_id) if resolved_evento_id is not None else None
        if evento is not None:
            resolved_evento_nome = _clean_text(evento.nome)
        elif _clean_text(lead.evento_nome):
            resolved_evento_nome = _clean_text(lead.evento_nome)

        normalized_cpf = normalize_cpf(lead.cpf)
        normalized_phone = _normalize_phone(lead.telefone)
        birth_raw = lead.data_nascimento.isoformat() if lead.data_nascimento is not None else ""
        _birth_normalized, birth_issue = _normalize_data_nascimento(birth_raw, ref_date=ref_date)

        reasons: list[str] = []
        if not is_valid_cpf(normalized_cpf):
            reasons.append("CPF_INVALIDO")
        if normalized_phone and len(normalized_phone) < 10:
            reasons.append("TELEFONE_INVALIDO")
        canonical_event_date = _canonical_event_date_iso(evento)
        if canonical_event_date is None:
            reasons.append("DATA_EVENTO_INVALIDA")

        source_file = (
            _clean_text(staging_row.source_file if staging_row is not None else "")
            or _clean_text(batch.nome_arquivo_original if batch is not None else "")
            or f"gold_verification_run_{requested_by}"
        )
        source_sheet = _clean_text(staging_row.source_sheet) if staging_row is not None else ""
        source_row = int(staging_row.source_row_number) if staging_row is not None else -lead_id
        source_row_ref = f"lead:{lead_id}"

        dedupe_key: tuple[str, str] | None = None
        if is_valid_cpf(normalized_cpf) and _normalize_event_key(resolved_evento_nome):
            dedupe_key = (normalized_cpf, _normalize_event_key(resolved_evento_nome))

        candidates.append(
            _Candidate(
                lead=lead,
                source_batch=batch,
                source_file=source_file,
                source_sheet=source_sheet,
                source_row=source_row,
                source_row_ref=source_row_ref,
                resolved_evento_id=resolved_evento_id,
                resolved_evento_nome=resolved_evento_nome,
                canonical_event_date=canonical_event_date,
                normalized_cpf=normalized_cpf,
                normalized_phone=normalized_phone,
                birth_date_issue=birth_issue,
                reason_codes=reasons,
                dedupe_key=dedupe_key,
            )
        )

    dedupe_groups: dict[tuple[str, str], list[_Candidate]] = {}
    for candidate in candidates:
        if candidate.dedupe_key is None or candidate.reason_codes:
            continue
        dedupe_groups.setdefault(candidate.dedupe_key, []).append(candidate)

    for group in dedupe_groups.values():
        group.sort(key=lambda item: (item.lead.data_criacao, item.lead.id or 0))
        winner = group[0]
        winner.dedupe_rank = 1
        for rank, candidate in enumerate(group[1:], start=2):
            candidate.dedupe_rank = rank
            candidate.duplicate_of_lead_id = int(winner.lead.id or 0)
            candidate.outcome = "duplicate"
            candidate.reason_codes = ["DUPLICIDADE_CPF_EVENTO"]

    for candidate in candidates:
        if candidate.outcome == "duplicate":
            continue
        candidate.outcome = "invalid" if candidate.reason_codes else "valid"
    return candidates


def _build_pipeline_report(batch: LeadBatch, candidates: list[_Candidate]) -> dict[str, Any]:
    raw_rows = len(candidates)
    invalid_records: list[dict[str, Any]] = []
    birth_controls: list[dict[str, Any]] = []
    metrics = _zero_quality_metrics()

    for candidate in candidates:
        if candidate.outcome in {"invalid", "duplicate"}:
            reason = ";".join(candidate.reason_codes)
            invalid_records.append(
                {
                    "source_file": candidate.source_file,
                    "source_sheet": candidate.source_sheet,
                    "source_row": candidate.source_row,
                    "source_row_ref": candidate.source_row_ref,
                    "motivo_rejeicao": reason,
                    "row_data": _build_row_data(candidate.lead),
                }
            )
            _increment_metrics_from_reason(reason, metrics)
            continue

        if candidate.birth_date_issue is None:
            continue
        if candidate.birth_date_issue is BirthDateIssue.MISSING:
            metrics["data_nascimento_missing"] += 1
        else:
            metrics["data_nascimento_invalid"] += 1
        birth_controls.append(
                {
                    "source_file": candidate.source_file,
                    "source_sheet": candidate.source_sheet,
                    "source_row": candidate.source_row,
                    "source_row_ref": candidate.source_row_ref,
                    "issue": str(candidate.birth_date_issue),
                    "row_data": _build_row_data(candidate.lead),
                }
            )

    valid_rows = sum(1 for candidate in candidates if candidate.outcome == "valid")
    discarded_rows = raw_rows - valid_rows
    warnings = _gate_warnings_from_metrics(metrics)
    status = "PASS_WITH_WARNINGS" if warnings else "PASS"

    report = {
        "lote_id": str(batch.id or ""),
        "run_timestamp": _now_utc().isoformat(),
        "input_files": sorted({candidate.source_file for candidate in candidates if candidate.source_file}),
        "input_files_scanned": sorted({candidate.source_file for candidate in candidates if candidate.source_file}),
        "input_files_processed": sorted({candidate.source_file for candidate in candidates if candidate.source_file}),
        "input_files_skipped": [],
        "source_profiles_detected": {},
        "mapping_version": RULES_VERSION,
        "totals": {
            "raw_rows": raw_rows,
            "valid_rows": valid_rows,
            "discarded_rows": discarded_rows,
        },
        "quality_metrics": metrics,
        "gate": {
            "status": status,
            "decision": "promote",
            "fail_reasons": [],
            "warnings": warnings,
        },
        "data_nascimento_controle": birth_controls,
        "localidade_controle": [],
        "cidade_fora_mapeamento_controle": [],
        "invalid_records": invalid_records,
        "exit_code": 0,
    }
    return report


def _get_or_create_run(
    session: Session,
    *,
    idempotency_key: str,
    scope_json: dict[str, Any],
    requested_by: int | None,
    force_new_run: bool,
) -> LeadGoldVerificationRun:
    if not force_new_run:
        existing = session.exec(
            select(LeadGoldVerificationRun).where(LeadGoldVerificationRun.idempotency_key == idempotency_key)
        ).first()
        if existing is not None:
            existing.status = "running"
            existing.scope_json = scope_json
            existing.completed_at = None
            session.add(existing)
            session.flush()
            return existing
    run = LeadGoldVerificationRun(
        run_id=str(uuid4()),
        idempotency_key=idempotency_key,
        rules_version=RULES_VERSION,
        scope_json=scope_json,
        status="running",
        requested_by=requested_by,
        started_at=_now_utc(),
    )
    session.add(run)
    session.flush()
    return run


def _clear_previous_run_outputs(session: Session, *, run_id: str) -> None:
    session.exec(delete(LeadGoldVerificationResult).where(LeadGoldVerificationResult.run_id == run_id))
    session.flush()
    technical_batches = session.exec(
        select(LeadBatch).where(LeadBatch.reprocess_run_id == run_id)
    ).all()
    for batch in technical_batches:
        session.delete(batch)
    session.flush()


def _create_technical_batch(
    session: Session,
    *,
    source_batch: LeadBatch | None,
    run_id: str,
    uploader_id: int,
    scope_label: str,
) -> LeadBatch:
    batch = LeadBatch(
        enviado_por=uploader_id,
        plataforma_origem="gold_verification",
        data_envio=_now_utc(),
        nome_arquivo_original=scope_label,
        arquivo_sha256=None,
        stage=BatchStage.GOLD,
        evento_id=source_batch.evento_id if source_batch is not None else None,
        origem_lote=source_batch.origem_lote if source_batch is not None else "proponente",
        tipo_lead_proponente=source_batch.tipo_lead_proponente if source_batch is not None else None,
        ativacao_id=source_batch.ativacao_id if source_batch is not None else None,
        pipeline_status=PipelineStatus.PENDING,
        reprocess_kind=REPROCESS_KIND,
        reprocess_run_id=run_id,
        reprocess_source_batch_id=int(source_batch.id) if source_batch and source_batch.id is not None else None,
    )
    session.add(batch)
    session.flush()
    return batch


def _persist_group(
    session: Session,
    *,
    run_id: str,
    source_batch: LeadBatch | None,
    candidates: list[_Candidate],
    uploader_id: int,
) -> LeadBatch:
    scope_label = (
        f"gold_verification::{int(source_batch.id)}::{_clean_text(source_batch.nome_arquivo_original)}"
        if source_batch is not None and source_batch.id is not None
        else f"gold_verification::null_batch::{run_id}"
    )
    technical_batch = _create_technical_batch(
        session,
        source_batch=source_batch,
        run_id=run_id,
        uploader_id=uploader_id,
        scope_label=scope_label,
    )
    report = _build_pipeline_report(technical_batch, candidates)
    discarded, issues, invalid_total = _gold_dq_snapshot_from_report(report)
    technical_batch.pipeline_report = report
    technical_batch.gold_dq_discarded_rows = discarded
    technical_batch.gold_dq_issue_counts = issues
    technical_batch.gold_dq_invalid_records_total = invalid_total
    technical_batch.pipeline_status = (
        PipelineStatus.PASS_WITH_WARNINGS
        if report["gate"]["status"] == "PASS_WITH_WARNINGS"
        else PipelineStatus.PASS
    )
    session.add(technical_batch)
    session.flush()

    for candidate in candidates:
        result = LeadGoldVerificationResult(
            run_id=run_id,
            verification_batch_id=int(technical_batch.id or 0),
            source_batch_id=candidate.source_batch_id,
            source_lead_id=int(candidate.lead.id or 0),
            resolved_evento_id=candidate.resolved_evento_id,
            resolved_evento_nome=candidate.resolved_evento_nome or None,
            outcome=candidate.outcome,
            motivo_rejeicao=";".join(candidate.reason_codes) or None,
            reason_codes_json=list(candidate.reason_codes) or None,
            row_data_json=_build_row_data(candidate.lead),
            source_file=candidate.source_file or None,
            source_sheet=candidate.source_sheet or None,
            source_row=candidate.source_row,
            source_row_ref=candidate.source_row_ref,
            dedupe_rank=candidate.dedupe_rank,
            duplicate_of_lead_id=candidate.duplicate_of_lead_id,
            created_at=_now_utc(),
        )
        session.add(result)

    session.flush()
    return technical_batch


def _group_candidates(candidates: Iterable[_Candidate]) -> dict[int | None, list[_Candidate]]:
    grouped: dict[int | None, list[_Candidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.source_batch_id, []).append(candidate)
    return grouped


def run_gold_verification(
    *,
    batch_ids: list[int] | None = None,
    include_null_batch: bool = True,
    requested_by: int | None = None,
    idempotency_key: str | None = None,
    force_new_run: bool = False,
    session: Session | None = None,
) -> GoldVerificationRunResult:
    own_session = session is None
    if session is None:
        engine = build_worker_engine()
        session = Session(engine)
        set_internal_service_db_context(session)

    try:
        scope_batch_ids = _load_scope_batch_ids(session, batch_ids)
        scope_json = {
            "batch_ids": scope_batch_ids,
            "include_null_batch": include_null_batch,
        }
        run = _get_or_create_run(
            session,
            idempotency_key=idempotency_key or str(uuid4()),
            scope_json=scope_json,
            requested_by=requested_by,
            force_new_run=force_new_run,
        )
        _clear_previous_run_outputs(session, run_id=run.run_id)

        stmt = select(Lead)
        if scope_batch_ids:
            if include_null_batch:
                stmt = stmt.where((Lead.batch_id.in_(scope_batch_ids)) | (Lead.batch_id.is_(None)))
            else:
                stmt = stmt.where(Lead.batch_id.in_(scope_batch_ids))
        elif not include_null_batch:
            stmt = stmt.where(Lead.batch_id.in_([-1]))
        leads = session.exec(stmt.order_by(Lead.data_criacao.asc(), Lead.id.asc())).all()

        source_batches = _load_source_batches(session, scope_batch_ids)
        uploader_id = _resolve_requested_by(session, requested_by=requested_by, source_batches=source_batches)
        candidates = _classify_candidates(
            session,
            leads=leads,
            source_batches=source_batches,
            requested_by=uploader_id,
        )
        grouped = _group_candidates(candidates)

        technical_batch_ids: list[int] = []
        for source_batch_id, group in grouped.items():
            if source_batch_id is None and not include_null_batch:
                continue
            technical_batch = _persist_group(
                session,
                run_id=run.run_id,
                source_batch=source_batches.get(source_batch_id) if source_batch_id is not None else None,
                candidates=group,
                uploader_id=uploader_id,
            )
            if technical_batch.id is not None:
                technical_batch_ids.append(int(technical_batch.id))

        run.status = "completed"
        run.completed_at = _now_utc()
        session.add(run)
        session.commit()

        return GoldVerificationRunResult(
            run_id=run.run_id,
            technical_batch_ids=technical_batch_ids,
            analyzed_rows=len(candidates),
            valid_rows=sum(1 for candidate in candidates if candidate.outcome == "valid"),
            invalid_rows=sum(1 for candidate in candidates if candidate.outcome == "invalid"),
            duplicate_rows=sum(1 for candidate in candidates if candidate.outcome == "duplicate"),
        )
    except Exception:
        if session is not None:
            session.rollback()
        raise
    finally:
        if own_session and session is not None:
            session.close()
