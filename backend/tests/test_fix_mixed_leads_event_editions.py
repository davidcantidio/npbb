from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.lead_public_models import LeadEventoSourceKind
from app.models.models import Evento, Lead, LeadEvento, StatusEvento, Usuario, UsuarioTipo
from scripts import fix_mixed_leads_event_editions as fix_script


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


def _seed_status(session: Session) -> StatusEvento:
    status = StatusEvento(nome="Previsto")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="fix-event-editions@npbb.com.br",
        password_hash="hash",
        tipo_usuario=UsuarioTipo.NPBB,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_event(session: Session) -> Evento:
    status = _seed_status(session)
    event = Evento(
        id=4,
        nome="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto",
        cidade="Navegantes",
        estado="SC",
        status_id=int(status.id),
        data_inicio_prevista=date(2026, 2, 4),
        data_fim_prevista=date(2026, 2, 8),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def _seed_batch(
    session: Session,
    *,
    user_id: int,
    evento_id: int,
    batch_id: int,
    nome_arquivo_original: str,
    arquivo_sha256: str | None,
    stage: BatchStage,
    pipeline_status: PipelineStatus,
) -> LeadBatch:
    batch = LeadBatch(
        id=batch_id,
        enviado_por=user_id,
        plataforma_origem="manual",
        data_envio=datetime(2026, 4, 20, tzinfo=timezone.utc),
        data_upload=datetime(2026, 4, 20, tzinfo=timezone.utc),
        nome_arquivo_original=nome_arquivo_original,
        arquivo_sha256=arquivo_sha256,
        arquivo_bronze=b"xlsx",
        evento_id=evento_id,
        stage=stage,
        pipeline_status=pipeline_status,
        origem_lote="proponente",
        tipo_lead_proponente="entrada_evento",
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


def _seed_lead(
    session: Session,
    *,
    lead_id: int,
    batch_id: int,
    email: str,
    cpf: str,
) -> Lead:
    lead = Lead(
        id=lead_id,
        nome=f"Lead {lead_id}",
        email=email,
        cpf=cpf,
        evento_nome="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto",
        sessao="Navegantes-SC",
        batch_id=batch_id,
    )
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


def _create_input_file(tmp_path: Path) -> Path:
    path = tmp_path / "cbvp-2026.xlsx"
    path.write_bytes(b"conteudo-planilha-2026")
    return path


def _seed_fixture(session: Session, *, arquivo_sha256: str) -> None:
    user = _seed_user(session)
    old_event = _seed_event(session)
    _seed_batch(
        session,
        user_id=int(user.id),
        evento_id=int(old_event.id),
        batch_id=55,
        nome_arquivo_original="1ª Etapa CBVP Navegantes.xlsx",
        arquivo_sha256=None,
        stage=BatchStage.SILVER,
        pipeline_status=PipelineStatus.PENDING,
    )
    _seed_batch(
        session,
        user_id=int(user.id),
        evento_id=int(old_event.id),
        batch_id=100,
        nome_arquivo_original="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto.xlsx",
        arquivo_sha256=arquivo_sha256,
        stage=BatchStage.GOLD,
        pipeline_status=PipelineStatus.PASS_WITH_WARNINGS,
    )
    _seed_batch(
        session,
        user_id=int(user.id),
        evento_id=int(old_event.id),
        batch_id=188,
        nome_arquivo_original="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto.xlsx",
        arquivo_sha256=arquivo_sha256,
        stage=BatchStage.GOLD,
        pipeline_status=PipelineStatus.PASS_WITH_WARNINGS,
    )
    _seed_batch(
        session,
        user_id=int(user.id),
        evento_id=int(old_event.id),
        batch_id=225,
        nome_arquivo_original="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto.xlsx",
        arquivo_sha256=arquivo_sha256,
        stage=BatchStage.BRONZE,
        pipeline_status=PipelineStatus.PENDING,
    )
    lead_2025 = _seed_lead(
        session,
        lead_id=1,
        batch_id=55,
        email="lead-2025@example.com",
        cpf="11111111111",
    )
    lead_2026 = _seed_lead(
        session,
        lead_id=2,
        batch_id=100,
        email="lead-2026@example.com",
        cpf="22222222222",
    )
    session.add(
        LeadSilver(
            batch_id=100,
            row_index=0,
            evento_id=int(old_event.id),
            dados_brutos={"cpf": lead_2026.cpf},
        )
    )
    session.add(
        LeadEvento(
            lead_id=int(lead_2025.id),
            evento_id=int(old_event.id),
            source_kind=LeadEventoSourceKind.LEAD_BATCH,
            source_ref_id=188,
        )
    )
    session.add(
        LeadEvento(
            lead_id=int(lead_2026.id),
            evento_id=int(old_event.id),
            source_kind=LeadEventoSourceKind.LEAD_BATCH,
            source_ref_id=188,
        )
    )
    session.commit()


def test_repair_event_editions_dry_run_rolls_back(engine, tmp_path: Path) -> None:
    input_file = _create_input_file(tmp_path)
    arquivo_sha256 = fix_script._hash_file(input_file)

    with Session(engine) as session:
        _seed_fixture(session, arquivo_sha256=arquivo_sha256)

    artifact_dir = tmp_path / "artifacts"
    with Session(engine) as session:
        summary = fix_script.repair_event_editions(
            session,
            old_event_id=4,
            input_file=input_file,
            old_start_date=date(2025, 2, 5),
            old_end_date=date(2025, 2, 9),
            new_start_date=None,
            new_end_date=None,
            apply=False,
            artifact_dir=artifact_dir,
        )

    assert summary.dry_run is True
    assert summary.new_event_id is not None
    assert summary.batches_moved == 3
    assert summary.lead_events_moved == 2
    assert summary.restored_old_event_links == 1
    assert summary.ambiguous_leads == []
    assert Path(summary.artifact_path or "").exists()

    with Session(engine) as session:
        old_event = session.get(Evento, 4)
        assert old_event is not None
        assert old_event.data_inicio_prevista == date(2026, 2, 4)
        assert session.exec(select(Evento).where(Evento.id != 4)).all() == []
        moved_batches = session.exec(select(LeadBatch).where(LeadBatch.evento_id != 4)).all()
        assert moved_batches == []
        old_links = session.exec(select(LeadEvento).where(LeadEvento.evento_id == 4)).all()
        assert len(old_links) == 2


def test_repair_event_editions_apply_persists_changes(engine, tmp_path: Path) -> None:
    input_file = _create_input_file(tmp_path)
    arquivo_sha256 = fix_script._hash_file(input_file)

    with Session(engine) as session:
        _seed_fixture(session, arquivo_sha256=arquivo_sha256)

    artifact_dir = tmp_path / "artifacts"
    with Session(engine) as session:
        summary = fix_script.repair_event_editions(
            session,
            old_event_id=4,
            input_file=input_file,
            old_start_date=date(2025, 2, 5),
            old_end_date=date(2025, 2, 9),
            new_start_date=None,
            new_end_date=None,
            apply=True,
            artifact_dir=artifact_dir,
        )

    assert summary.dry_run is False
    assert summary.new_event_id is not None
    new_event_id = int(summary.new_event_id)
    assert Path(summary.artifact_path or "").exists()
    assert summary.validation["remaining_old_event_hash_batches"] == 0
    assert summary.validation["remaining_old_event_contaminated_links"] == 0

    with Session(engine) as session:
        old_event = session.get(Evento, 4)
        new_event = session.get(Evento, new_event_id)
        assert old_event is not None
        assert new_event is not None
        assert old_event.data_inicio_prevista == date(2025, 2, 5)
        assert old_event.data_fim_prevista == date(2025, 2, 9)
        assert new_event.data_inicio_prevista == date(2026, 2, 4)
        assert new_event.data_fim_prevista == date(2026, 2, 8)

        moved_batches = session.exec(
            select(LeadBatch).where(LeadBatch.id.in_([100, 188, 225])).order_by(LeadBatch.id)
        ).all()
        assert [int(batch.evento_id) for batch in moved_batches] == [new_event_id, new_event_id, new_event_id]

        silver = session.exec(select(LeadSilver).where(LeadSilver.batch_id == 100)).first()
        assert silver is not None
        assert int(silver.evento_id) == new_event_id

        old_event_links = session.exec(
            select(LeadEvento).where(LeadEvento.evento_id == 4).order_by(LeadEvento.lead_id)
        ).all()
        assert len(old_event_links) == 1
        assert int(old_event_links[0].lead_id) == 1
        assert int(old_event_links[0].source_ref_id or 0) == 55

        new_event_links = session.exec(
            select(LeadEvento).where(LeadEvento.evento_id == new_event_id).order_by(LeadEvento.lead_id)
        ).all()
        assert len(new_event_links) == 2
        assert [int(link.lead_id) for link in new_event_links] == [1, 2]
        assert all(int(link.source_ref_id or 0) == 188 for link in new_event_links)


def test_repair_event_editions_apply_refuses_ambiguous_restoration(engine, tmp_path: Path) -> None:
    input_file = _create_input_file(tmp_path)
    arquivo_sha256 = fix_script._hash_file(input_file)

    with Session(engine) as session:
        user = _seed_user(session)
        old_event = _seed_event(session)
        _seed_batch(
            session,
            user_id=int(user.id),
            evento_id=int(old_event.id),
            batch_id=188,
            nome_arquivo_original="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto.xlsx",
            arquivo_sha256=arquivo_sha256,
            stage=BatchStage.GOLD,
            pipeline_status=PipelineStatus.PASS_WITH_WARNINGS,
        )
        lead = Lead(
            id=99,
            nome="Lead Ambiguo",
            email="ambiguous@example.com",
            cpf="99999999999",
            evento_nome=old_event.nome,
            sessao="Navegantes-SC",
            batch_id=None,
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        session.add(
            LeadEvento(
                lead_id=int(lead.id),
                evento_id=int(old_event.id),
                source_kind=LeadEventoSourceKind.LEAD_BATCH,
                source_ref_id=188,
            )
        )
        session.commit()

    with Session(engine) as session:
        with pytest.raises(ValueError, match="leads ambiguos"):
            fix_script.repair_event_editions(
                session,
                old_event_id=4,
                input_file=input_file,
                old_start_date=date(2025, 2, 5),
                old_end_date=date(2025, 2, 9),
                new_start_date=None,
                new_end_date=None,
                apply=True,
                artifact_dir=tmp_path / "artifacts",
            )
