from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.lead_batch import LeadBatch
from app.models.models import Evento, Lead, LeadEvento, LeadEventoSourceKind, StatusEvento, Usuario
from scripts import fix_contaminated_lead_event_names as fix_script


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


def _seed_status(session: Session) -> StatusEvento:
    status = StatusEvento(nome="Previsto")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def _seed_evento(session: Session, *, nome: str) -> Evento:
    status = session.get(StatusEvento, 1) or _seed_status(session)
    evento = Evento(
        nome=nome,
        cidade="Brasilia",
        estado="DF",
        status_id=int(status.id),
        data_inicio_prevista=date(2026, 1, 1),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="script@npbb.com.br",
        password_hash="hash",
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_batch(session: Session, *, evento_id: int) -> LeadBatch:
    user = _seed_user(session)
    batch = LeadBatch(
        enviado_por=int(user.id),
        plataforma_origem="manual",
        data_envio=datetime(2026, 4, 20, tzinfo=timezone.utc),
        nome_arquivo_original="contaminated.xlsx",
        arquivo_bronze=b"xlsx",
        evento_id=evento_id,
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


def test_execute_fix_dry_run_nao_persiste_alteracoes_e_prioriza_lead_evento(engine) -> None:
    with Session(engine) as session:
        _seed_status(session)
        evento_baixa = _seed_evento(session, nome="Evento Backfill")
        evento_alta = _seed_evento(session, nome="Evento Canonico")
        lead = Lead(
            nome="Lead Contaminado",
            email="dry-run@example.com",
            cpf="52998224725",
            evento_nome="Ativação",
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        lead_id = int(lead.id)

        session.add(
            LeadEvento(
                lead_id=lead_id,
                evento_id=int(evento_baixa.id),
                source_kind=LeadEventoSourceKind.EVENT_NAME_BACKFILL,
            )
        )
        session.add(
            LeadEvento(
                lead_id=lead_id,
                evento_id=int(evento_alta.id),
                source_kind=LeadEventoSourceKind.EVENT_DIRECT,
            )
        )
        session.commit()

    with Session(engine) as session:
        summary, fixes, manual_reviews = fix_script.execute_fix(session, dry_run=True)

    assert summary.dry_run is True
    assert summary.candidates == 1
    assert summary.fixed == 1
    assert summary.manual_review == 0
    assert manual_reviews == []
    assert len(fixes) == 1
    assert fixes[0].lead_id == lead_id
    assert fixes[0].new_evento_nome == "Evento Canonico"
    assert fixes[0].source == f"lead_evento:{LeadEventoSourceKind.EVENT_DIRECT.value}"

    with Session(engine) as session:
        persisted = session.get(Lead, lead_id)

    assert persisted is not None
    assert persisted.evento_nome == "Ativação"


def test_execute_fix_apply_faz_fallback_para_evento_do_lote(engine) -> None:
    with Session(engine) as session:
        _seed_status(session)
        evento = _seed_evento(session, nome="Evento do Lote")
        batch = _seed_batch(session, evento_id=int(evento.id))
        lead = Lead(
            nome="Lead Batch",
            email="batch@example.com",
            cpf="39053344705",
            evento_nome="Proponente",
            batch_id=int(batch.id),
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        lead_id = int(lead.id)

    with Session(engine) as session:
        summary, fixes, manual_reviews = fix_script.execute_fix(session, dry_run=False)

    assert summary.dry_run is False
    assert summary.candidates == 1
    assert summary.fixed == 1
    assert summary.manual_review == 0
    assert len(fixes) == 1
    assert fixes[0].source == "lead_batch"
    assert manual_reviews == []

    with Session(engine) as session:
        persisted = session.get(Lead, lead_id)

    assert persisted is not None
    assert persisted.evento_nome == "Evento do Lote"


def test_execute_fix_marca_para_revisao_manual_quando_nao_ha_origem_resolvida(engine) -> None:
    with Session(engine) as session:
        _seed_status(session)
        lead = Lead(
            nome="Lead Sem Origem",
            email="review@example.com",
            cpf="11144477735",
            evento_nome="Ativação",
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        lead_id = int(lead.id)

    with Session(engine) as session:
        summary, fixes, manual_reviews = fix_script.execute_fix(session, dry_run=False)

    assert summary.candidates == 1
    assert summary.fixed == 0
    assert summary.manual_review == 1
    assert fixes == []
    assert len(manual_reviews) == 1
    assert manual_reviews[0].lead_id == lead_id

    with Session(engine) as session:
        persisted = session.get(Lead, lead_id)

    assert persisted is not None
    assert persisted.evento_nome == "Ativação"


def test_main_usa_dry_run_por_padrao(engine, monkeypatch, capsys) -> None:
    with Session(engine) as session:
        _seed_status(session)
        evento = _seed_evento(session, nome="Evento Main")
        lead = Lead(
            nome="Lead Main",
            email="main@example.com",
            cpf="99765432100",
            evento_nome="Proponente",
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        lead_id = int(lead.id)
        session.add(
            LeadEvento(
                lead_id=lead_id,
                evento_id=int(evento.id),
                source_kind=LeadEventoSourceKind.EVENT_DIRECT,
            )
        )
        session.commit()

    monkeypatch.setattr(fix_script, "get_engine_for_scripts", lambda: engine)

    exit_code = fix_script.main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[DRY-RUN]" in captured.out
    assert "Nenhuma alteracao foi persistida." in captured.out

    with Session(engine) as session:
        persisted = session.get(Lead, lead_id)

    assert persisted is not None
    assert persisted.evento_nome == "Proponente"
