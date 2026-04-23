from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.lead_public_models import (
    Lead,
    LeadEvento,
    LeadGoldVerificationResult,
    LeadGoldVerificationRun,
    LeadImportEtlPreviewSession,
    LeadImportEtlStagingRow,
    LeadEventoSourceKind,
)
from app.models.models import Evento, StatusEvento, Usuario
from app.services.lead_gold_verification_service import REPROCESS_KIND, run_gold_verification
from app.utils.security import hash_password


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="gold-verification@test.npbb",
        password_hash=hash_password("senha123"),
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_status(session: Session) -> StatusEvento:
    status = StatusEvento(nome="Planejado")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def _seed_event(session: Session, *, status_id: int, nome: str, data_inicio: date | None) -> Evento:
    evento = Evento(
        nome=nome,
        cidade="Sao Paulo",
        estado="SP",
        data_inicio_prevista=data_inicio,
        status_id=status_id,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _seed_batch(session: Session, *, user_id: int, evento_id: int | None, file_name: str) -> LeadBatch:
    batch = LeadBatch(
        enviado_por=user_id,
        plataforma_origem="manual",
        data_envio=datetime(2026, 4, 22, tzinfo=timezone.utc),
        nome_arquivo_original=file_name,
        stage=BatchStage.SILVER,
        evento_id=evento_id,
        pipeline_status=PipelineStatus.PENDING,
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


def _seed_preview_session(session: Session, *, evento_id: int, requested_by: int) -> LeadImportEtlPreviewSession:
    preview = LeadImportEtlPreviewSession(
        session_token="session-token",
        idempotency_key="preview-key",
        evento_id=evento_id,
        requested_by=requested_by,
        evento_nome="Evento Válido",
        filename="origem.xlsx",
        approved_rows_json="[]",
        rejected_rows_json="[]",
        dq_report_json="{}",
    )
    session.add(preview)
    session.commit()
    session.refresh(preview)
    return preview


def test_run_gold_verification_persists_dq_snapshot_and_reconciles_counts() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = _seed_user(session)
        status = _seed_status(session)
        evento_valido = _seed_event(session, status_id=int(status.id), nome="Evento Válido", data_inicio=date(2026, 6, 10))
        evento_sem_data = _seed_event(session, status_id=int(status.id), nome="Evento Sem Data", data_inicio=None)
        batch_ok = _seed_batch(session, user_id=int(user.id), evento_id=int(evento_valido.id), file_name="origem.xlsx")
        batch_bad_date = _seed_batch(session, user_id=int(user.id), evento_id=int(evento_sem_data.id), file_name="origem-sem-data.xlsx")
        preview = _seed_preview_session(session, evento_id=int(evento_valido.id), requested_by=int(user.id))

        valid_lead = Lead(
            nome="Valido",
            email="valido@example.com",
            cpf="52998224725",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 0, 0),
            batch_id=int(batch_ok.id),
        )
        invalid_cpf = Lead(
            nome="Cpf Invalido",
            email="cpf@example.com",
            cpf="52998224724",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 1, 0),
            batch_id=int(batch_ok.id),
        )
        empty_cpf = Lead(
            nome="Cpf Vazio",
            email="vazio@example.com",
            cpf="",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 2, 0),
            batch_id=int(batch_ok.id),
        )
        duplicate_a = Lead(
            nome="Duplicado A",
            email="dup-a@example.com",
            cpf="39053344705",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 3, 0),
            batch_id=int(batch_ok.id),
        )
        duplicate_b = Lead(
            nome="Duplicado B",
            email="dup-b@example.com",
            cpf="39053344705",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 4, 0),
            batch_id=int(batch_ok.id),
        )
        invalid_event_date = Lead(
            nome="Sem Data Evento",
            email="sem-data@example.com",
            cpf="11144477735",
            telefone="11999999999",
            evento_nome="Evento Sem Data",
            data_criacao=datetime(2026, 4, 20, 10, 5, 0),
            batch_id=int(batch_bad_date.id),
        )
        session.add_all([valid_lead, invalid_cpf, empty_cpf, duplicate_a, duplicate_b, invalid_event_date])
        session.commit()
        for lead in [valid_lead, invalid_cpf, empty_cpf, duplicate_a, duplicate_b, invalid_event_date]:
            session.refresh(lead)

        session.add(
            LeadEvento(
                lead_id=int(valid_lead.id),
                evento_id=int(evento_valido.id),
                source_kind=LeadEventoSourceKind.LEAD_BATCH,
            )
        )
        session.add(
            LeadImportEtlStagingRow(
                session_token=preview.session_token,
                requested_by=int(user.id),
                evento_id=int(evento_valido.id),
                source_file="origem.xlsx",
                source_sheet="Planilha 1",
                source_row_number=7,
                row_hash="hash-1",
                raw_payload_json={"cpf": invalid_cpf.cpf},
                merged_lead_id=int(invalid_cpf.id),
            )
        )
        session.commit()

        result = run_gold_verification(
            batch_ids=[int(batch_ok.id), int(batch_bad_date.id)],
            include_null_batch=False,
            requested_by=int(user.id),
            idempotency_key="gold-check-1",
            session=session,
        )

        assert result.analyzed_rows == 6
        assert result.valid_rows == 2
        assert result.invalid_rows == 3
        assert result.duplicate_rows == 1

        tech_batches = session.exec(
            select(LeadBatch)
            .where(LeadBatch.reprocess_kind == REPROCESS_KIND)
            .order_by(LeadBatch.reprocess_source_batch_id.asc())
        ).all()
        assert len(tech_batches) == 2

        batch_ok_tech = next(batch for batch in tech_batches if batch.reprocess_source_batch_id == int(batch_ok.id))
        report = batch_ok_tech.pipeline_report
        assert report is not None
        assert report["totals"] == {"raw_rows": 5, "valid_rows": 2, "discarded_rows": 3}
        assert batch_ok_tech.gold_dq_discarded_rows == 3
        assert batch_ok_tech.gold_dq_invalid_records_total == 3
        assert batch_ok_tech.gold_dq_issue_counts is not None
        assert batch_ok_tech.gold_dq_issue_counts["cpf_invalid_discarded"] == 2
        assert batch_ok_tech.gold_dq_issue_counts["duplicidades_cpf_evento"] == 1

        invalid_records = report["invalid_records"]
        reasons = {item["motivo_rejeicao"] for item in invalid_records}
        assert "CPF_INVALIDO" in reasons
        assert "DUPLICIDADE_CPF_EVENTO" in reasons
        cpf_record = next(item for item in invalid_records if item["motivo_rejeicao"] == "CPF_INVALIDO" and item["row_data"]["email"] == "cpf@example.com")
        assert cpf_record["source_sheet"] == "Planilha 1"
        assert cpf_record["source_row"] == 7

        batch_bad_date_tech = next(batch for batch in tech_batches if batch.reprocess_source_batch_id == int(batch_bad_date.id))
        assert batch_bad_date_tech.pipeline_report is not None
        assert batch_bad_date_tech.pipeline_report["invalid_records"][0]["motivo_rejeicao"] == "DATA_EVENTO_INVALIDA"

        persisted_results = session.exec(select(LeadGoldVerificationResult)).all()
        assert len(persisted_results) == 6
        assert sum(1 for row in persisted_results if row.outcome == "duplicate") == 1


def test_run_gold_verification_is_idempotent_for_same_key() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = _seed_user(session)
        status = _seed_status(session)
        evento = _seed_event(session, status_id=int(status.id), nome="Evento Válido", data_inicio=date(2026, 6, 10))
        batch = _seed_batch(session, user_id=int(user.id), evento_id=int(evento.id), file_name="origem.xlsx")
        lead = Lead(
            nome="Lead",
            email="lead@example.com",
            cpf="52998224725",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 0, 0),
            batch_id=int(batch.id),
        )
        session.add(lead)
        session.commit()

        first = run_gold_verification(
            batch_ids=[int(batch.id)],
            include_null_batch=False,
            requested_by=int(user.id),
            idempotency_key="gold-idempotent",
            session=session,
        )
        second = run_gold_verification(
            batch_ids=[int(batch.id)],
            include_null_batch=False,
            requested_by=int(user.id),
            idempotency_key="gold-idempotent",
            session=session,
        )

        assert first.run_id == second.run_id
        runs = session.exec(select(LeadGoldVerificationRun)).all()
        assert len(runs) == 1
        tech_batches = session.exec(select(LeadBatch).where(LeadBatch.reprocess_kind == REPROCESS_KIND)).all()
        results = session.exec(select(LeadGoldVerificationResult)).all()
        assert len(tech_batches) == 1
        assert len(results) == 1


def test_run_gold_verification_creates_technical_batch_for_null_batch_scope() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = _seed_user(session)
        status = _seed_status(session)
        _seed_event(session, status_id=int(status.id), nome="Evento Válido", data_inicio=date(2026, 6, 10))
        lead = Lead(
            nome="Sem Lote",
            email="sem-lote@example.com",
            cpf="52998224725",
            telefone="11999999999",
            evento_nome="Evento Válido",
            data_criacao=datetime(2026, 4, 20, 10, 0, 0),
            batch_id=None,
        )
        session.add(lead)
        session.commit()

        result = run_gold_verification(
            batch_ids=[],
            include_null_batch=True,
            requested_by=int(user.id),
            idempotency_key="gold-null-batch",
            session=session,
        )

        assert result.analyzed_rows == 1
        tech_batch = session.exec(
            select(LeadBatch).where(
                LeadBatch.reprocess_kind == REPROCESS_KIND,
                LeadBatch.reprocess_source_batch_id.is_(None),
            )
        ).first()
        assert tech_batch is not None
        assert tech_batch.pipeline_report is not None
        assert tech_batch.pipeline_report["totals"]["raw_rows"] == 1
