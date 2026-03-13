from __future__ import annotations

from datetime import date

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.models import Ativacao, Evento, StatusEvento
from scripts import validate_no_localhost_urls as validation_script


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


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
) -> Ativacao:
    ativacao = Ativacao(
        evento_id=evento_id,
        nome="Ativacao QR",
        descricao="Descricao",
        landing_url=landing_url,
        url_promotor=url_promotor,
    )
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)
    return ativacao


def prepare_engine():
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


def test_main_retorna_zero_quando_nao_ha_localhost(monkeypatch, capsys):
    engine = prepare_engine()

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="https://app.npbb.com.br/landing/ativacoes/1",
            url_promotor="https://app.npbb.com.br/landing/ativacoes/1",
        )

    monkeypatch.setattr(validation_script, "get_engine_for_scripts", lambda: engine)

    exit_code = validation_script.main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "zero registros com localhost ou 127.0.0.1" in captured.out
    assert captured.err == ""


def test_main_retorna_um_quando_landing_url_tem_localhost(monkeypatch, capsys):
    engine = prepare_engine()

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        ativacao = seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="http://localhost:5173/landing/ativacoes/2",
            url_promotor="https://app.npbb.com.br/landing/ativacoes/2",
        )

    monkeypatch.setattr(validation_script, "get_engine_for_scripts", lambda: engine)

    exit_code = validation_script.main([])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Validacao falhou" in captured.err
    assert "Total de registros incorretos: 1." in captured.err
    assert f"ativacao_id={ativacao.id}" in captured.err
    assert "http://localhost:5173/landing/ativacoes/2" in captured.err


def test_main_retorna_um_quando_url_promotor_tem_loopback(monkeypatch, capsys):
    engine = prepare_engine()

    with Session(engine) as session:
        status = seed_status(session)
        evento = seed_evento(session, status_id=status.id)
        ativacao = seed_ativacao(
            session,
            evento_id=evento.id,
            landing_url="https://app.npbb.com.br/landing/ativacoes/3",
            url_promotor="http://127.0.0.1:5173/landing/ativacoes/3",
        )

    monkeypatch.setattr(validation_script, "get_engine_for_scripts", lambda: engine)

    exit_code = validation_script.main([])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "127.0.0.1" in captured.err
    assert f"ativacao_id={ativacao.id}" in captured.err
