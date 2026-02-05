import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db.database import get_session
from app.main import app
from app.models.models import Agencia, Diretoria, Funcionario, Usuario


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


def seed_agencia(engine, nome="V3A", dominio="v3a.com.br"):
    with Session(engine) as session:
        ag = Agencia(nome=nome, dominio=dominio, lote=1)
        session.add(ag)
        session.commit()
        session.refresh(ag)
        return ag


def seed_funcionario(engine, *, email: str, chave_c: str | None = None):
    with Session(engine) as session:
        diretoria = Diretoria(nome="dimac")
        session.add(diretoria)
        session.commit()
        session.refresh(diretoria)

        func = Funcionario(
            nome="Funcionario",
            chave_c=(chave_c or "c123"),
            diretoria_id=diretoria.id,
            email=email,
            telefone=None,
        )
        session.add(func)
        session.commit()
        session.refresh(func)
        return func


def test_usuarios_create_npbb_sucesso_e_link_por_email(client, engine):
    funcionario = seed_funcionario(engine, email="user@npbb.com.br", chave_c="c1351833")

    resp = client.post(
        "/usuarios/",
        json={
            "email": "user@npbb.com.br",
            "password": "Senha123",
            "tipo_usuario": "npbb",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "user@npbb.com.br"
    assert data["tipo_usuario"] == "npbb"
    assert data["funcionario_id"] == funcionario.id


def test_usuarios_create_bb_sucesso_e_link_por_matricula(client, engine):
    funcionario = seed_funcionario(engine, email="bb@bb.com.br", chave_c="c1351833")

    resp = client.post(
        "/usuarios/",
        json={
            "email": "teste@bb.com.br",
            "password": "Senha123",
            "tipo_usuario": "bb",
            "matricula": "c1351833",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tipo_usuario"] == "bb"
    assert data["matricula"] == "c1351833"
    assert data["funcionario_id"] == funcionario.id


def test_usuarios_create_agencia_sucesso(client, engine):
    ag = seed_agencia(engine, dominio="v3a.com.br")

    resp = client.post(
        "/usuarios/",
        json={
            "email": "user@v3a.com.br",
            "password": "Senha123",
            "tipo_usuario": "agencia",
            "agencia_id": ag.id,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tipo_usuario"] == "agencia"
    assert data["agencia_id"] == ag.id


def test_usuarios_create_rejeita_senha_fraca(client):
    resp = client.post(
        "/usuarios/",
        json={"email": "user@npbb.com.br", "password": "abc", "tipo_usuario": "npbb"},
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "PASSWORD_POLICY"
    assert detail["field"] == "password"


def test_usuarios_create_rejeita_domain_invalido(client):
    resp = client.post(
        "/usuarios/",
        json={"email": "user@gmail.com", "password": "Senha123", "tipo_usuario": "npbb"},
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "EMAIL_DOMAIN_INVALID"
    assert detail["field"] == "email"


def test_usuarios_create_rejeita_matricula_invalida_bb(client):
    resp = client.post(
        "/usuarios/",
        json={
            "email": "teste@bb.com.br",
            "password": "Senha123",
            "tipo_usuario": "bb",
            "matricula": "123",
        },
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "MATRICULA_INVALID"
    assert detail["field"] == "matricula"


def test_usuarios_create_rejeita_agencia_domain_mismatch(client, engine):
    ag = seed_agencia(engine, dominio="v3a.com.br")

    resp = client.post(
        "/usuarios/",
        json={
            "email": "user@outra.com.br",
            "password": "Senha123",
            "tipo_usuario": "agencia",
            "agencia_id": ag.id,
        },
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "EMAIL_DOMAIN_MISMATCH"
    assert detail["field"] == "email"


def test_usuarios_create_rejeita_agencia_sem_agencia_id_422(client):
    resp = client.post(
        "/usuarios/",
        json={
            "email": "user@v3a.com.br",
            "password": "Senha123",
            "tipo_usuario": "agencia",
        },
    )
    assert resp.status_code == 422


def test_usuarios_create_rejeita_email_duplicado(client, engine):
    with Session(engine) as session:
        session.add(
            Usuario(
                email="user@npbb.com.br",
                password_hash="hashed",
                tipo_usuario="npbb",
                ativo=True,
            )
        )
        session.commit()

    resp = client.post(
        "/usuarios/",
        json={"email": "user@npbb.com.br", "password": "Senha123", "tipo_usuario": "npbb"},
    )
    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert detail["code"] == "EMAIL_ALREADY_REGISTERED"


def test_usuarios_create_rejeita_matricula_duplicada(client, engine):
    resp_1 = client.post(
        "/usuarios/",
        json={
            "email": "a@bb.com.br",
            "password": "Senha123",
            "tipo_usuario": "bb",
            "matricula": "c999",
        },
    )
    assert resp_1.status_code == 201

    resp_2 = client.post(
        "/usuarios/",
        json={
            "email": "b@bb.com.br",
            "password": "Senha123",
            "tipo_usuario": "bb",
            "matricula": "c999",
        },
    )
    assert resp_2.status_code == 409
    detail = resp_2.json()["detail"]
    assert detail["code"] == "MATRICULA_ALREADY_REGISTERED"
