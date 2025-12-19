import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db.database import get_session
from app.main import app
from app.models.models import Agencia


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine():
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


def seed_agencias(engine):
    with Session(engine) as session:
        session.add_all(
            [
                Agencia(nome="V3A", dominio="v3a.com.br", lote=1),
                Agencia(nome="Sherpa", dominio="sherpa.com.br", lote=1),
                Agencia(nome="Monumenta", dominio="monumenta.com.br", lote=2),
            ]
        )
        session.commit()


def test_agencias_list_paginado_e_search(client, engine):
    seed_agencias(engine)

    resp = client.get("/agencias/?limit=2")
    assert resp.status_code == 200
    assert resp.headers.get("X-Total-Count") == "3"
    data = resp.json()
    assert len(data) == 2
    assert {"id", "nome", "dominio"}.issubset(set(data[0].keys()))

    resp_search = client.get("/agencias/?search=v3a")
    assert resp_search.status_code == 200
    assert resp_search.headers.get("X-Total-Count") == "1"
    assert resp_search.json()[0]["nome"] == "V3A"


def test_agencias_rejeita_limit_maior_que_maximo(client):
    resp = client.get("/agencias/?limit=500")
    assert resp.status_code == 422

