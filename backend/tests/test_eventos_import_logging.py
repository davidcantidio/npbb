import logging

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.core.auth import get_current_user
from app.db.database import get_session
from app.main import app
from app.models.models import Usuario, UsuarioTipo
from app.utils.security import hash_password
from app.routers import eventos as eventos_router


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


def seed_user(session: Session, email: str) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password("Senha123!"),
        tipo_usuario=UsuarioTipo.NPBB,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def client(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    with Session(engine) as session:
        user = seed_user(session, "user@example.com")

    def override_get_current_user():
        return user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_import_logs_sanitized_error(client, monkeypatch, caplog):
    def boom(*_args, **_kwargs):
        raise ValueError("email usuario@bb.com.br cpf 123.456.789-10 tel 11999998888")

    monkeypatch.setattr(eventos_router, "_build_evento_payload_from_row", boom)

    csv_content = "nome,cidade,estado,data_inicio_prevista\nEvento,Sao Paulo,SP,2025-01-01\n"
    caplog.set_level(logging.WARNING, logger="app.telemetry")

    resp = client.post(
        "/evento/import/csv",
        files={"file": ("eventos.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 200

    record = next((r for r in caplog.records if r.name == "app.telemetry"), None)
    assert record is not None
    detail = getattr(record, "detail", "")

    assert "usuario@bb.com.br" not in detail
    assert "123.456.789-10" not in detail
    assert "11999998888" not in detail
    assert record.error_code == "UNEXPECTED_ERROR"
    assert record.row_number == 2
