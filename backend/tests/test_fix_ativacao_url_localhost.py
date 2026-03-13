from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.models import Ativacao, Evento, StatusEvento
from app.services.qr_code import build_qr_code_data_url
from scripts import fix_ativacao_url_localhost as fix_script


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


def seed_status(session: Session) -> StatusEvento:
    status = StatusEvento(nome="Previsto")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def seed_evento(session: Session, *, status_id: int) -> Evento:
    evento = Evento(
        nome="Evento QR",
        descricao="Evento de teste",
        concorrencia=False,
        cidade="Sao Paulo",
        estado="SP",
        status_id=status_id,
        data_inicio_prevista=date(2026, 1, 1),
        data_fim_prevista=date(2026, 1, 2),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def seed_ativacao(
    session: Session,
    *,
    evento_id: int,
    landing_url: str | None,
    url_promotor: str | None,
    qr_code_url: str | None,
) -> Ativacao:
    ativacao = Ativacao(
        evento_id=evento_id,
        nome="Ativacao QR",
        descricao="Descricao",
        landing_url=landing_url,
        url_promotor=url_promotor,
        qr_code_url=qr_code_url,
    )
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)
    return ativacao


def test_execute_fix_dry_run_nao_persiste_alteracoes(engine, monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "https://app.npbb.com.br")

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        ativacao = seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="http://localhost:5173/landing/ativacoes/1",
            url_promotor="http://127.0.0.1:5173/landing/ativacoes/1",
            qr_code_url="data:image/svg+xml;base64,old",
        )
        ativacao_id = ativacao.id

    with Session(engine) as session:
        summary, updates = fix_script.execute_fix(session, dry_run=True)

    assert summary.dry_run is True
    assert summary.candidates == 1
    assert summary.updates == 1
    assert len(updates) == 1
    assert updates[0].ativacao_id == ativacao_id

    with Session(engine) as session:
        persisted = session.get(Ativacao, ativacao_id)

    assert persisted is not None
    assert persisted.landing_url == "http://localhost:5173/landing/ativacoes/1"
    assert persisted.url_promotor == "http://127.0.0.1:5173/landing/ativacoes/1"
    assert persisted.qr_code_url == "data:image/svg+xml;base64,old"


def test_execute_fix_atualiza_registros_com_public_app_base_url(engine, monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "https://app.npbb.com.br")

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        ativacao = seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="http://localhost:5173/landing/ativacoes/2",
            url_promotor="http://localhost:5173/landing/ativacoes/2",
            qr_code_url="data:image/svg+xml;base64,old",
        )
        ativacao_id = ativacao.id

    with Session(engine) as session:
        summary, updates = fix_script.execute_fix(session, dry_run=False)

    expected_landing_url = f"https://app.npbb.com.br/landing/ativacoes/{ativacao_id}"
    assert summary.dry_run is False
    assert summary.candidates == 1
    assert summary.updates == 1
    assert len(updates) == 1

    with Session(engine) as session:
        persisted = session.get(Ativacao, ativacao_id)

    assert persisted is not None
    assert persisted.landing_url == expected_landing_url
    assert persisted.url_promotor == expected_landing_url
    assert persisted.qr_code_url == build_qr_code_data_url(expected_landing_url)


def test_execute_fix_reexecucao_idempotente_retorna_zero_pendencias(engine, monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "https://app.npbb.com.br")

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="http://localhost:5173/landing/ativacoes/3",
            url_promotor="http://localhost:5173/landing/ativacoes/3",
            qr_code_url="data:image/svg+xml;base64,old",
        )

    with Session(engine) as session:
        first_summary, first_updates = fix_script.execute_fix(session, dry_run=False)

    with Session(engine) as session:
        second_summary, second_updates = fix_script.execute_fix(session, dry_run=False)

    assert first_summary.updates == 1
    assert len(first_updates) == 1
    assert second_summary.candidates == 0
    assert second_summary.updates == 0
    assert second_updates == []


def test_execute_fix_falha_sem_public_app_base_url(engine, monkeypatch):
    monkeypatch.delenv("PUBLIC_APP_BASE_URL", raising=False)

    with Session(engine) as session:
        with pytest.raises(RuntimeError, match="PUBLIC_APP_BASE_URL precisa estar configurada"):
            fix_script.execute_fix(session, dry_run=True)


def test_execute_fix_faz_rollback_quando_commit_falha(engine, monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "https://app.npbb.com.br")

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        ativacao = seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="http://localhost:5173/landing/ativacoes/4",
            url_promotor="http://localhost:5173/landing/ativacoes/4",
            qr_code_url="data:image/svg+xml;base64,old",
        )
        ativacao_id = ativacao.id

    with Session(engine) as session:
        def fail_commit():
            raise RuntimeError("commit failure")

        monkeypatch.setattr(session, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="commit failure"):
            fix_script.execute_fix(session, dry_run=False)

    with Session(engine) as session:
        persisted = session.get(Ativacao, ativacao_id)

    assert persisted is not None
    assert persisted.landing_url == "http://localhost:5173/landing/ativacoes/4"
    assert persisted.url_promotor == "http://localhost:5173/landing/ativacoes/4"
    assert persisted.qr_code_url == "data:image/svg+xml;base64,old"
