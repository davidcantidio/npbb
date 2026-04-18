from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.models import Ativacao, Evento, StatusEvento
from app.services.default_event_activation import (
    ATIVACAO_BB_ALREADY_EXISTS,
    ATIVACAO_BB_REQUIRED,
    ensure_bb_activation,
    guard_bb_invariant_on_activation_write,
)


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "http://localhost:5173")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        status = StatusEvento(nome="Previsto")
        session.add(status)
        session.commit()
    return engine


def seed_evento(session: Session, *, nome: str = "Evento BB") -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    assert status is not None and status.id is not None

    evento = Evento(
        nome=nome,
        descricao="descricao",
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        status_id=status.id,
        data_inicio_prevista=date(2026, 4, 17),
        data_fim_prevista=date(2026, 4, 18),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _load_migration_module():
    backend_dir = Path(__file__).resolve().parents[1]
    migration_path = (
        backend_dir / "alembic" / "versions" / "fa1b2c3d4e5f_ensure_bb_activation_per_event.py"
    )
    spec = importlib.util.spec_from_file_location("test_bb_migration_module", migration_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_migration_schema(connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE evento (
                id INTEGER PRIMARY KEY,
                nome TEXT
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE ativacao (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT NULL,
                evento_id INTEGER NOT NULL,
                gamificacao_id INTEGER NULL,
                landing_url TEXT NULL,
                qr_code_url TEXT NULL,
                url_promotor TEXT NULL,
                valor NUMERIC NULL,
                mensagem_qrcode TEXT NULL,
                redireciona_pesquisa BOOLEAN NOT NULL DEFAULT FALSE,
                checkin_unico BOOLEAN NOT NULL DEFAULT FALSE,
                termo_uso BOOLEAN NOT NULL DEFAULT FALSE,
                gera_cupom BOOLEAN NOT NULL DEFAULT FALSE,
                created_at DATETIME NULL,
                updated_at DATETIME NULL
            )
            """
        )
    )


def test_ensure_bb_activation_is_idempotent_and_normalizes_existing_name(engine):
    with Session(engine) as session:
        evento = seed_evento(session)
        ativacao = Ativacao(
            evento_id=evento.id,
            nome=" bb ",
            valor=0,
        )
        session.add(ativacao)
        session.commit()

        first = ensure_bb_activation(session, evento_id=evento.id)
        session.commit()
        second = ensure_bb_activation(session, evento_id=evento.id)
        session.commit()

        ativacoes = session.exec(select(Ativacao).where(Ativacao.evento_id == evento.id)).all()
        assert len(ativacoes) == 1
        assert first.id == second.id == ativacoes[0].id
        assert ativacoes[0].nome == "BB"


def test_guard_bb_invariant_rejects_duplicate_rename_and_delete(engine):
    with Session(engine) as session:
        evento = seed_evento(session, nome="Evento Guard")
        bb = ensure_bb_activation(session, evento_id=evento.id)
        extra = Ativacao(evento_id=evento.id, nome="Stand", valor=0)
        session.add(extra)
        session.commit()
        session.refresh(extra)

        with pytest.raises(HTTPException) as duplicate_exc:
            guard_bb_invariant_on_activation_write(session, evento_id=evento.id, nome=" bb ")
        assert duplicate_exc.value.status_code == 409
        assert duplicate_exc.value.detail["code"] == ATIVACAO_BB_ALREADY_EXISTS

        with pytest.raises(HTTPException) as rename_exc:
            guard_bb_invariant_on_activation_write(
                session,
                evento_id=evento.id,
                ativacao_id=bb.id,
                nome="Outro nome",
            )
        assert rename_exc.value.status_code == 409
        assert rename_exc.value.detail["code"] == ATIVACAO_BB_REQUIRED

        with pytest.raises(HTTPException) as delete_exc:
            guard_bb_invariant_on_activation_write(
                session,
                evento_id=evento.id,
                ativacao_id=bb.id,
                deleting=True,
            )
        assert delete_exc.value.status_code == 409
        assert delete_exc.value.detail["code"] == ATIVACAO_BB_REQUIRED

        normalized = guard_bb_invariant_on_activation_write(
            session,
            evento_id=evento.id,
            ativacao_id=bb.id,
            nome=" bb ",
        )
        assert normalized == "BB"

        with pytest.raises(HTTPException) as promote_exc:
            guard_bb_invariant_on_activation_write(
                session,
                evento_id=evento.id,
                ativacao_id=extra.id,
                nome="BB",
            )
        assert promote_exc.value.status_code == 409
        assert promote_exc.value.detail["code"] == ATIVACAO_BB_ALREADY_EXISTS


def test_bb_migration_repairs_missing_and_duplicate_rows():
    migration_module = _load_migration_module()
    engine = make_engine()

    with engine.begin() as connection:
        _create_migration_schema(connection)
        connection.execute(
            text(
                """
                INSERT INTO evento (id, nome) VALUES
                    (1, 'Evento 1'),
                    (2, 'Evento 2'),
                    (3, 'Evento 3')
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO ativacao (
                    id,
                    nome,
                    evento_id,
                    valor,
                    redireciona_pesquisa,
                    checkin_unico,
                    termo_uso,
                    gera_cupom,
                    created_at,
                    updated_at
                ) VALUES
                    (10, ' bb ', 1, 0.00, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                    (20, 'BB', 2, 0.00, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                    (21, ' bb ', 2, 0.00, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
        )

        migration_module.repair_bb_activations(connection)
        rows = connection.execute(
            text(
                """
                SELECT evento_id, id, nome
                FROM ativacao
                ORDER BY evento_id, id
                """
            )
        ).fetchall()

        assert rows == [
            (1, 10, "BB"),
            (2, 20, "BB"),
            (2, 21, "BB (legado 21)"),
            (3, 22, "BB"),
        ]

        inserted = connection.execute(
            text(
                """
                SELECT
                    nome,
                    descricao,
                    gamificacao_id,
                    landing_url,
                    qr_code_url,
                    url_promotor,
                    valor,
                    mensagem_qrcode,
                    redireciona_pesquisa,
                    checkin_unico,
                    termo_uso,
                    gera_cupom
                FROM ativacao
                WHERE evento_id = 3
                """
            )
        ).one()
        assert inserted == (
            "BB",
            None,
            None,
            None,
            None,
            None,
            0,
            None,
            0,
            0,
            0,
            0,
        )

        migration_module.repair_bb_activations(connection)
        rerun_rows = connection.execute(
            text(
                """
                SELECT evento_id, id, nome
                FROM ativacao
                ORDER BY evento_id, id
                """
            )
        ).fetchall()
        assert rerun_rows == rows
