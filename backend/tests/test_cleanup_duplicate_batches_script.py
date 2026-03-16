from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.models import Evento, Lead, StatusEvento, Usuario
from scripts import cleanup_duplicate_batches


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _seed_status(session: Session) -> StatusEvento:
    status = StatusEvento(nome="Previsto")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def _seed_evento(session: Session, *, evento_id: int = 85) -> Evento:
    status = _seed_status(session)
    evento = Evento(
        id=evento_id,
        nome="TAMO JUNTO BB",
        cidade="Brasilia",
        estado="DF",
        status_id=int(status.id),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="cleanup@npbb.com.br",
        password_hash="hash",
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_batch(
    session: Session,
    *,
    user_id: int,
    evento_id: int,
    created_at: datetime,
    filename: str,
) -> LeadBatch:
    batch = LeadBatch(
        enviado_por=user_id,
        plataforma_origem="manual",
        data_envio=created_at,
        data_upload=created_at,
        nome_arquivo_original=filename,
        arquivo_bronze=b"csv",
        stage=BatchStage.SILVER,
        evento_id=evento_id,
        pipeline_status=PipelineStatus.PENDING,
        created_at=created_at,
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


def _seed_silver_rows(session: Session, *, batch_id: int, evento_id: int, count: int) -> None:
    for row_index in range(count):
        session.add(
            LeadSilver(
                batch_id=batch_id,
                row_index=row_index,
                evento_id=evento_id,
                dados_brutos={"cpf": f"{row_index:011d}", "email": f"user{row_index}@example.com"},
            )
        )
    session.commit()


def _seed_lead(session: Session, *, batch_id: int) -> Lead:
    lead = Lead(
        nome="Lead Batch",
        email="lead@example.com",
        cpf="12345678901",
        evento_nome="TAMO JUNTO BB",
        sessao="Sala 1",
        batch_id=batch_id,
    )
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


def _build_two_batch_fixture(engine) -> tuple[int, int, int]:
    with Session(engine) as session:
        evento = _seed_evento(session)
        user = _seed_user(session)
        batch_old = _seed_batch(
            session,
            user_id=int(user.id),
            evento_id=int(evento.id),
            created_at=datetime(2026, 3, 7, 20, 3, 55, tzinfo=timezone.utc),
            filename="old.xlsx",
        )
        batch_new = _seed_batch(
            session,
            user_id=int(user.id),
            evento_id=int(evento.id),
            created_at=datetime(2026, 3, 8, 19, 26, 49, tzinfo=timezone.utc),
            filename="new.xlsx",
        )
        _seed_silver_rows(session, batch_id=int(batch_new.id), evento_id=int(evento.id), count=3)
        lead = _seed_lead(session, batch_id=int(batch_new.id))
        return int(evento.id), int(batch_old.id), int(lead.id)


def test_cleanup_duplicate_batches_dry_run_rolls_back() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    evento_id, batch_kept_id, lead_id = _build_two_batch_fixture(engine)

    with Session(engine) as session:
        result = cleanup_duplicate_batches.cleanup_duplicate_batches_for_event(
            session,
            evento_id=evento_id,
            apply=False,
        )

    assert result.status_label == "DRY-RUN"
    assert result.kept_batch is not None
    assert result.kept_batch.id == batch_kept_id
    assert [batch.id for batch in result.removed_batches] == [batch.id for batch in result.batches_found[1:]]
    assert result.leads_unlinked == 1
    assert result.silver_deleted == 3
    assert result.batches_deleted == 1

    with Session(engine) as session:
        assert session.exec(select(LeadBatch).where(LeadBatch.evento_id == evento_id)).all()
        lead = session.get(Lead, lead_id)
        assert lead is not None
        assert lead.batch_id is not None
        assert session.exec(select(LeadSilver)).all()


def test_cleanup_duplicate_batches_apply_persists_changes() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    evento_id, batch_kept_id, lead_id = _build_two_batch_fixture(engine)

    with Session(engine) as session:
        result = cleanup_duplicate_batches.cleanup_duplicate_batches_for_event(
            session,
            evento_id=evento_id,
            apply=True,
        )

    assert result.status_label == "APPLY"
    assert result.kept_batch is not None
    assert result.kept_batch.id == batch_kept_id
    assert result.leads_unlinked == 1
    assert result.silver_deleted == 3
    assert result.batches_deleted == 1

    with Session(engine) as session:
        remaining_batches = session.exec(
            select(LeadBatch).where(LeadBatch.evento_id == evento_id).order_by(LeadBatch.id)
        ).all()
        assert [batch.id for batch in remaining_batches] == [batch_kept_id]
        lead = session.get(Lead, lead_id)
        assert lead is not None
        assert lead.batch_id is None
        assert session.exec(select(LeadSilver)).all() == []


def test_cleanup_duplicate_batches_noop_for_single_batch() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        evento = _seed_evento(session)
        user = _seed_user(session)
        batch = _seed_batch(
            session,
            user_id=int(user.id),
            evento_id=int(evento.id),
            created_at=datetime(2026, 3, 7, 20, 3, 55, tzinfo=timezone.utc),
            filename="single.xlsx",
        )
        evento_id = int(evento.id)
        batch_id = int(batch.id)

    with Session(engine) as session:
        result = cleanup_duplicate_batches.cleanup_duplicate_batches_for_event(
            session,
            evento_id=evento_id,
            apply=False,
        )

    assert result.changed is False
    assert result.kept_batch is not None
    assert result.kept_batch.id == batch_id
    assert result.removed_batches == []
    assert result.leads_unlinked == 0
    assert result.silver_deleted == 0
    assert result.batches_deleted == 0


def test_cleanup_duplicate_batches_main_uses_dry_run_by_default(monkeypatch, capsys) -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    evento_id, batch_kept_id, _lead_id = _build_two_batch_fixture(engine)

    monkeypatch.setattr(cleanup_duplicate_batches, "load_env", lambda: None)
    monkeypatch.setattr(cleanup_duplicate_batches, "get_engine_for_scripts", lambda: engine)

    exit_code = cleanup_duplicate_batches.main(["--evento-id", str(evento_id)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[DRY-RUN]" in captured.out
    assert f"id={batch_kept_id}" in captured.out
    assert "Nenhuma alteracao foi persistida" in captured.out
