"""Service for Gold pipeline: Silver -> run_pipeline -> insert Gold leads."""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import re
import shutil
from datetime import date as date_type, datetime as datetime_type, time as time_type, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from lead_pipeline.constants import ALL_COLUMNS
from lead_pipeline.normalization import strip_accents
from lead_pipeline.pipeline import PipelineConfig, PipelineProgressEvent, run_pipeline
from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.lead_public_models import TipoLead
from app.models.models import Ativacao, AtivacaoLead, Evento, Lead, LeadEventoSourceKind, TipoEvento
from app.services.lead_event_service import ensure_lead_event

logger = logging.getLogger(__name__)

TMP_ROOT = Path("/tmp/npbb_pipeline")

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


def _evento_lookup_por_ids(db: Session, event_ids: set[int]) -> dict[int, tuple[str, str | None]]:
    """Nome do evento e nome do tipo (lookup) para enriquecer linhas Silver sem evento/tipo no arquivo."""
    if not event_ids:
        return {}
    eventos = db.exec(select(Evento).where(Evento.id.in_(event_ids))).all()
    tipo_ids = {e.tipo_id for e in eventos if e.tipo_id is not None}
    tipo_nomes: dict[int, str] = {}
    if tipo_ids:
        for tipo in db.exec(select(TipoEvento).where(TipoEvento.id.in_(tipo_ids))).all():
            tipo_nomes[int(tipo.id)] = tipo.nome
    out: dict[int, tuple[str, str | None]] = {}
    for ev in eventos:
        tid = ev.tipo_id
        tipo_nome = tipo_nomes.get(int(tid)) if tid is not None else None
        out[int(ev.id)] = (ev.nome, tipo_nome)
    return out


def materializar_silver_como_csv(batch_id: int, db: Session) -> Path:
    """Le `leads_silver` do lote e escreve CSV temporario com o contrato Gold."""
    tmp_dir = TMP_ROOT / str(batch_id)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    silver_rows = db.exec(
        select(LeadSilver).where(LeadSilver.batch_id == batch_id)
    ).all()

    event_ids = {int(r.evento_id) for r in silver_rows if r.evento_id is not None}
    evento_por_id = _evento_lookup_por_ids(db, event_ids)

    csv_path = tmp_dir / "silver_input.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ALL_COLUMNS)
        writer.writeheader()
        for row in silver_rows:
            dados = row.dados_brutos or {}
            out_row = {col: str(dados.get(col, "") or "") for col in ALL_COLUMNS}
            nome_ev, nome_tipo = evento_por_id.get(int(row.evento_id), ("", None))
            if not out_row["evento"].strip() and nome_ev:
                out_row["evento"] = nome_ev
            if not out_row["tipo_evento"].strip() and nome_tipo:
                out_row["tipo_evento"] = nome_tipo
            writer.writerow(out_row)

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
) -> dict[str, Any]:
    return {
        "step": step,
        "label": label or PIPELINE_PROGRESS_LABELS.get(step, step),
        "pct": pct,
        "updated_at": _pipeline_progress_updated_at(),
    }


def set_pipeline_progress(
    batch: LeadBatch,
    *,
    step: str,
    pct: int | None = None,
    label: str | None = None,
) -> None:
    batch.pipeline_progress = _build_pipeline_progress_payload(step=step, pct=pct, label=label)


def queue_pipeline_batch(batch: LeadBatch) -> None:
    batch.pipeline_status = PipelineStatus.PENDING
    _clear_gold_pipeline_snapshot(batch)
    set_pipeline_progress(batch, step="queued")


def _persist_pipeline_progress(engine: Any, batch_id: int, event: PipelineProgressEvent) -> None:
    with Session(engine) as db:
        batch = db.get(LeadBatch, batch_id)
        if not batch:
            logger.warning("Batch %s nao encontrado para atualizar progresso da pipeline.", batch_id)
            return
        set_pipeline_progress(
            batch,
            step=event.step,
            pct=event.pct,
            label=event.label,
        )
        db.add(batch)
        db.commit()


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
    for field, value in payload.items():
        if not _has_value(value):
            continue
        current = getattr(lead, field, None)
        if _has_value(current):
            continue
        setattr(lead, field, value)


def _find_existing_lead(db: Session, payload: dict[str, Any]) -> Lead | None:
    id_salesforce = payload.get("id_salesforce")
    if _has_value(id_salesforce):
        lead = db.exec(select(Lead).where(Lead.id_salesforce == id_salesforce)).first()
        if lead is not None:
            return lead

    return db.exec(
        select(Lead)
        .where(Lead.email == payload.get("email"))
        .where(Lead.cpf == payload.get("cpf"))
        .where(Lead.evento_nome == payload.get("evento_nome"))
        .where(Lead.sessao == payload.get("sessao"))
    ).first()


def _inserir_leads_gold(batch: LeadBatch, consolidated_path: Path, db: Session) -> int:
    """Le o CSV validado e insere leads na tabela `lead`."""
    if not consolidated_path.exists():
        return 0

    with consolidated_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        return 0

    origem = (batch.origem_lote or "proponente").strip().lower()
    is_ativacao_batch = origem == "ativacao" and batch.ativacao_id is not None

    raw_tipo_prop = (batch.tipo_lead_proponente or "").strip().lower() or "entrada_evento"
    tipo_lead_proponente = (
        TipoLead.BILHETERIA if raw_tipo_prop == "bilheteria" else TipoLead.ENTRADA_EVENTO
    )

    count = 0
    for row in rows:
        lead_payload = _build_lead_payload(row, batch)
        lead = _find_existing_lead(db, lead_payload)
        if lead is None:
            lead = Lead(**lead_payload, batch_id=batch.id)
            db.add(lead)
            db.flush()
            count += 1
        else:
            _merge_lead_payload_if_missing(lead, lead_payload)
            db.add(lead)
            db.flush()
        if lead.id is not None and batch.evento_id is not None:
            if is_ativacao_batch:
                ativacao_lead = _get_or_create_ativacao_lead(
                    db,
                    ativacao_id=int(batch.ativacao_id),
                    lead_id=int(lead.id),
                )
                ensure_lead_event(
                    db,
                    lead_id=lead.id,
                    evento_id=batch.evento_id,
                    source_kind=LeadEventoSourceKind.ACTIVATION,
                    source_ref_id=ativacao_lead.id,
                )
            else:
                ensure_lead_event(
                    db,
                    lead_id=lead.id,
                    evento_id=batch.evento_id,
                    source_kind=LeadEventoSourceKind.LEAD_BATCH,
                    source_ref_id=batch.id,
                    tipo_lead=tipo_lead_proponente,
                )

    db.commit()
    return count


async def executar_pipeline_gold(batch_id: int) -> None:
    """Background task: materializa Silver CSV -> run_pipeline -> promove Gold."""
    from app.db.database import engine  # import local para evitar ciclo na inicializacao

    tmp_dir = TMP_ROOT / str(batch_id)

    def on_progress(event: PipelineProgressEvent) -> None:
        _persist_pipeline_progress(engine, batch_id, event)

    try:
        with Session(engine) as db:
            batch = db.get(LeadBatch, batch_id)
            if not batch:
                logger.error("Batch %s nao encontrado para execucao do pipeline.", batch_id)
                return

            queue_pipeline_batch(batch)
            db.add(batch)
            db.commit()

            set_pipeline_progress(batch, step="silver_csv")
            db.add(batch)
            db.commit()

            csv_path = materializar_silver_como_csv(batch_id, db)

        output_root = tmp_dir / "output"
        config = PipelineConfig(
            lote_id=str(batch_id),
            input_files=[csv_path],
            output_root=output_root,
            on_progress=on_progress,
        )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_pipeline, config)

        report_data: dict[str, Any] = {}
        if result.report_path.exists():
            report_data = json.loads(result.report_path.read_text(encoding="utf-8"))

        pipeline_status = _pipeline_status_from_str(result.status)

        with Session(engine) as db:
            batch = db.get(LeadBatch, batch_id)
            if not batch:
                logger.error("Batch %s nao encontrado para finalizar pipeline.", batch_id)
                return

            if result.decision == "promote":
                set_pipeline_progress(batch, step="insert_leads")
                db.add(batch)
                db.commit()
                _inserir_leads_gold(batch, result.consolidated_path, db)
                batch.stage = BatchStage.GOLD
            else:
                batch.stage = BatchStage.SILVER

            batch.pipeline_report = report_data
            batch.pipeline_status = pipeline_status
            disc, issues, inv_n = _gold_dq_snapshot_from_report(report_data)
            batch.gold_dq_discarded_rows = disc
            batch.gold_dq_issue_counts = issues
            batch.gold_dq_invalid_records_total = inv_n
            _clear_pipeline_progress(batch)

            db.add(batch)
            db.commit()

        logger.info(
            "Pipeline batch %s concluido: status=%s decision=%s",
            batch_id,
            result.status,
            result.decision,
        )

    except Exception:
        logger.exception("Falha na execucao do pipeline para batch %s.", batch_id)
        try:
            with Session(engine) as db:
                batch = db.get(LeadBatch, batch_id)
                if batch is None:
                    return
                batch.pipeline_status = PipelineStatus.FAIL
                _clear_gold_pipeline_snapshot(batch)
                _clear_pipeline_progress(batch)
                db.add(batch)
                db.commit()
        except Exception:
            logger.exception("Falha ao persistir status FAIL para batch %s.", batch_id)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
