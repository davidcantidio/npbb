import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db.database import get_session
from app.main import app
from app.models.models import Usuario
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
            tipo_usuario="bb",
            ativo=ativo,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def test_login_success(client, engine):
    user = seed_user(engine)
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["id"] == user.id
    assert data["user"]["email"] == user.email
    assert data["access_token"]


def test_login_invalid_credentials(client, engine):
    user = seed_user(engine)
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "errada"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client, engine):
    user = seed_user(engine, email="inactive@example.com", ativo=False)
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    assert response.status_code == 401


def test_me_with_valid_token(client, engine):
    user = seed_user(engine)
    login_resp = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    token = login_resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["id"] == user.id
    assert data["email"] == user.email


def test_me_without_token(client):
    me_resp = client.get("/auth/me")
    assert me_resp.status_code == 401
