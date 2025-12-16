import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta, timezone

from app.db.database import get_session
from app.main import app
from app.models.models import PasswordResetToken, Usuario
from app.utils.security import hash_password


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    monkeypatch.setenv("EMAIL_BACKEND", "console")
    monkeypatch.setenv("PASSWORD_RESET_DEBUG", "true")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_user(engine, email="user@example.com", password="senha123", ativo=True):
    with Session(engine) as session:
        user = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario="npbb",
            ativo=ativo,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def test_forgot_password_returns_debug_token_and_allows_reset(client, engine):
    user = seed_user(engine, password="Senha123!")

    forgot_resp = client.post("/usuarios/forgot-password", json={"email": user.email})
    assert forgot_resp.status_code == 200
    data = forgot_resp.json()
    assert data["message"]
    assert data["token"]

    token = data["token"]
    new_password = "Nova123"

    reset_resp = client.post(
        "/usuarios/reset-password",
        json={"token": token, "password": new_password},
    )
    assert reset_resp.status_code == 200

    login_resp = client.post(
        "/auth/login",
        json={"email": user.email, "password": new_password},
    )
    assert login_resp.status_code == 200


def test_reset_password_rejects_invalid_token(client):
    resp = client.post(
        "/usuarios/reset-password",
        json={"token": "invalid-token", "password": "Nova123"},
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "TOKEN_INVALID"


def test_forgot_password_returns_404_when_email_not_found(client):
    resp = client.post("/usuarios/forgot-password", json={"email": "missing@example.com"})
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert detail["code"] == "USER_NOT_FOUND"


def test_reset_password_rejects_expired_token(client, engine):
    user = seed_user(engine, password="Senha123!")

    forgot_resp = client.post("/usuarios/forgot-password", json={"email": user.email})
    assert forgot_resp.status_code == 200
    token = forgot_resp.json()["token"]

    with Session(engine) as session:
        record = session.exec(
            select(PasswordResetToken).where(PasswordResetToken.usuario_id == user.id)
        ).first()
        assert record is not None
        record.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)
        session.add(record)
        session.commit()

    resp = client.post("/usuarios/reset-password", json={"token": token, "password": "Nova123"})
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "TOKEN_EXPIRED"


def test_reset_password_rejects_used_token(client, engine):
    user = seed_user(engine, password="Senha123!")

    forgot_resp = client.post("/usuarios/forgot-password", json={"email": user.email})
    assert forgot_resp.status_code == 200
    token = forgot_resp.json()["token"]

    with Session(engine) as session:
        record = session.exec(
            select(PasswordResetToken).where(PasswordResetToken.usuario_id == user.id)
        ).first()
        assert record is not None
        record.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(record)
        session.commit()

    resp = client.post("/usuarios/reset-password", json={"token": token, "password": "Nova123"})
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "TOKEN_USED"

def test_reset_password_rejects_weak_password(client, engine):
    user = seed_user(engine, password="Senha123!")

    forgot_resp = client.post("/usuarios/forgot-password", json={"email": user.email})
    token = forgot_resp.json()["token"]

    resp = client.post("/usuarios/reset-password", json={"token": token, "password": "abc"})
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "PASSWORD_POLICY"
