"""Service for Gold pipeline: Silver → run_pipeline → insert Gold leads."""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import shutil
from datetime import date as date_type
from pathlib import Path
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from lead_pipeline.pipeline import PipelineConfig, run_pipeline
from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.lead_public_models import TipoLead
from app.models.models import Ativacao, AtivacaoLead, Lead, LeadEventoSourceKind
from app.services.lead_event_service import ensure_lead_event

logger = logging.getLogger(__name__)

TMP_ROOT = Path("/tmp/npbb_pipeline")

_REQUIRED_COLUMNS = [
    "nome",
    "cpf",
    "data_nascimento",
    "email",
    "telefone",
    "evento",
    "tipo_evento",
    "local",
    "data_evento",
]


def materializar_silver_como_csv(batch_id: int, db: Session) -> Path:
    """Lê leads_silver do lote e escreve CSV temporário com REQUIRED_COLUMNS."""
    tmp_dir = TMP_ROOT / str(batch_id)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    silver_rows = db.exec(
        select(LeadSilver).where(LeadSilver.batch_id == batch_id)
    ).all()

    csv_path = tmp_dir / "silver_input.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_REQUIRED_COLUMNS)
        writer.writeheader()
        for row in silver_rows:
            dados = row.dados_brutos or {}
            writer.writerow({col: dados.get(col, "") for col in _REQUIRED_COLUMNS})

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


def _inserir_leads_gold(batch: LeadBatch, consolidated_path: Path, db: Session) -> int:
    """Lê o CSV validado e insere leads na tabela `lead`. Retorna quantidade inserida."""
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
        data_nasc: date_type | None = None
        raw_nasc = (row.get("data_nascimento") or "").strip()
        if raw_nasc:
            try:
                data_nasc = date_type.fromisoformat(raw_nasc)
            except ValueError:
                data_nasc = None

        email = row.get("email", "").strip() or None
        cpf = row.get("cpf", "").strip() or None
        evento_nome = row.get("evento", "").strip() or None
        sessao = row.get("local", "").strip() or None

        lead = db.exec(
            select(Lead)
            .where(Lead.email == email)
            .where(Lead.cpf == cpf)
            .where(Lead.evento_nome == evento_nome)
            .where(Lead.sessao == sessao)
        ).first()
        if lead is None:
            lead = Lead(
                nome=row.get("nome", "").strip() or None,
                email=email,
                telefone=row.get("telefone", "").strip() or None,
                cpf=cpf,
                data_nascimento=data_nasc,
                evento_nome=evento_nome,
                sessao=sessao,
                fonte_origem=batch.plataforma_origem,
                batch_id=batch.id,
            )
            db.add(lead)
            db.flush()
            count += 1
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
    """Background task: materializa Silver CSV → run_pipeline → promove leads Gold.

    Cria sua própria sessão de DB pois roda após o response ter sido enviado.
    """
    from app.db.database import engine  # import local para evitar ciclo na inicialização

    with Session(engine) as db:
        batch = db.get(LeadBatch, batch_id)
        if not batch:
            logger.error("Batch %s não encontrado para execução do pipeline.", batch_id)
            return

        tmp_dir = TMP_ROOT / str(batch_id)
        try:
            csv_path = materializar_silver_como_csv(batch_id, db)

            output_root = tmp_dir / "output"
            config = PipelineConfig(
                lote_id=str(batch_id),
                input_files=[csv_path],
                output_root=output_root,
            )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_pipeline, config)

            report_data: dict[str, Any] = {}
            if result.report_path.exists():
                report_data = json.loads(result.report_path.read_text(encoding="utf-8"))

            pipeline_status = _pipeline_status_from_str(result.status)
            batch.pipeline_report = report_data
            batch.pipeline_status = pipeline_status

            if result.decision == "promote":
                _inserir_leads_gold(batch, result.consolidated_path, db)
                batch.stage = BatchStage.GOLD
            else:
                batch.stage = BatchStage.SILVER

            db.add(batch)
            db.commit()
            logger.info(
                "Pipeline batch %s concluído: status=%s decision=%s",
                batch_id,
                result.status,
                result.decision,
            )

        except Exception:
            logger.exception("Falha na execução do pipeline para batch %s.", batch_id)
            try:
                batch.pipeline_status = PipelineStatus.FAIL
                db.add(batch)
                db.commit()
            except Exception:
                logger.exception("Falha ao persistir status FAIL para batch %s.", batch_id)

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
