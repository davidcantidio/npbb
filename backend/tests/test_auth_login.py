import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db.database import get_session
from app.main import app
from app.models.models import Usuario
from app.routers.auth import STATUS_APROVADO
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


def seed_user(
    engine,
    email="user@example.com",
    password="senha123",
    ativo=True,
    matricula=None,
    status_aprovacao=None,
    tipo_usuario="bb",
):
    with Session(engine) as session:
        user = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario=tipo_usuario,
            ativo=ativo,
            matricula=matricula,
            status_aprovacao=status_aprovacao,
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


def test_login_bb_pendente_retorna_403(client, engine):
    user = seed_user(
        engine,
        email="bb@bb.com.br",
        matricula="123",
        status_aprovacao="PENDENTE",
    )
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Usuário BB pendente de aprovação"


def test_login_bb_aprovado_ok(client, engine):
    user = seed_user(
        engine,
        email="bb_aprovado@bb.com.br",
        matricula="456",
        status_aprovacao=STATUS_APROVADO,
    )
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    assert response.status_code == 200


def test_login_nao_bb_pendente_ok(client, engine):
    user = seed_user(
        engine,
        email="user@npbb.com.br",
        matricula="999",
        status_aprovacao="PENDENTE",
        tipo_usuario="npbb",
    )
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    assert response.status_code == 200


def test_login_bb_sem_matricula_valida_ok(client, engine):
    user = seed_user(
        engine,
        email="bb_sem_matricula@bb.com.br",
        matricula="   ",
        status_aprovacao="PENDENTE",
    )
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    assert response.status_code == 200


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
