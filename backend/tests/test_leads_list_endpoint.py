from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import (
    Agencia,
    Evento,
    Lead,
    LeadConversao,
    LeadConversaoTipo,
    StatusEvento,
    Usuario,
)
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


def seed_user(session: Session, email="user@npbb.com.br", password="senha123") -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_auth_header(client: TestClient, session: Session) -> dict[str, str]:
    user = seed_user(session)
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_leads(session: Session):
    agencia = Agencia(nome="Agencia 1", dominio="ag1.com.br", lote=1)
    status = StatusEvento(nome="Ativo")
    session.add_all([agencia, status])
    session.commit()
    session.refresh(agencia)
    session.refresh(status)

    evento_a = Evento(
        nome="Evento A",
        descricao="Desc A",
        concorrencia=False,
        cidade="Sao Paulo",
        estado="SP",
        agencia_id=agencia.id,
        status_id=status.id,
    )
    evento_b = Evento(
        nome="Evento B",
        descricao="Desc B",
        concorrencia=False,
        cidade="Rio de Janeiro",
        estado="RJ",
        agencia_id=agencia.id,
        status_id=status.id,
    )
    session.add_all([evento_a, evento_b])
    session.commit()
    session.refresh(evento_a)
    session.refresh(evento_b)

    lead_1 = Lead(
        nome="Ana",
        sobrenome="Silva",
        email="ana@example.com",
        cpf="00000000001",
        evento_nome="Evento Ticketing",
        cidade="Sao Paulo",
        estado="SP",
        data_criacao=datetime(2026, 1, 10, tzinfo=timezone.utc),
        is_cliente_bb=True,
        is_cliente_estilo=False,
    )
    lead_2 = Lead(
        nome="Bruno",
        sobrenome="Souza",
        email="bruno@example.com",
        cpf="00000000002",
        evento_nome="Outro Evento",
        cidade="Rio de Janeiro",
        estado="RJ",
        data_criacao=datetime(2026, 1, 9, tzinfo=timezone.utc),
    )
    lead_3 = Lead(
        nome="Carla",
        sobrenome="Oliveira",
        email="carla@example.com",
        cpf="00000000003",
        data_criacao=datetime(2026, 1, 8, tzinfo=timezone.utc),
    )
    session.add_all([lead_1, lead_2, lead_3])
    session.commit()
    session.refresh(lead_1)
    session.refresh(lead_2)
    session.refresh(lead_3)

    conv_1 = LeadConversao(
        lead_id=lead_1.id,
        tipo=LeadConversaoTipo.COMPRA_INGRESSO,
        evento_id=evento_a.id,
        created_at=datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
    )
    conv_2 = LeadConversao(
        lead_id=lead_1.id,
        tipo=LeadConversaoTipo.ACAO_EVENTO,
        evento_id=evento_b.id,
        created_at=datetime(2026, 1, 11, 10, 0, tzinfo=timezone.utc),
    )
    session.add_all([conv_1, conv_2])
    session.commit()


def test_listar_leads_retorna_evento_convertido_mais_recente(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get("/leads?page=1&page_size=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3

    items_by_email = {item["email"]: item for item in data["items"]}
    lead_ana = items_by_email["ana@example.com"]
    assert lead_ana["evento_convertido_nome"] == "Evento B"
    assert lead_ana["tipo_conversao"] == "ACAO_EVENTO"
    assert lead_ana["is_cliente_bb"] is True
    assert lead_ana["is_cliente_estilo"] is False

    lead_carla = items_by_email["carla@example.com"]
    assert lead_carla["evento_convertido_nome"] is None
    assert lead_carla["tipo_conversao"] is None
    assert lead_carla["is_cliente_bb"] is None
    assert lead_carla["is_cliente_estilo"] is None


def test_listar_leads_paginacao(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    page_1 = client.get("/leads?page=1&page_size=2", headers=headers)
    assert page_1.status_code == 200
    data_1 = page_1.json()
    assert data_1["total"] == 3
    assert len(data_1["items"]) == 2

    page_2 = client.get("/leads?page=2&page_size=2", headers=headers)
    assert page_2.status_code == 200
    data_2 = page_2.json()
    assert data_2["total"] == 3
    assert len(data_2["items"]) == 1


def test_listar_leads_requer_autenticacao(client, engine):
    with Session(engine) as session:
        seed_leads(session)

    response = client.get("/leads")
    assert response.status_code == 401


def test_listar_leads_filtra_por_data_criacao(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/leads?data_inicio=2026-01-09&data_fim=2026-01-09&page_size=10",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "bruno@example.com"


def test_listar_leads_filtra_por_evento_id_conversao_mais_recente(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        evento_b = session.exec(select(Evento).where(Evento.nome == "Evento B")).first()
        assert evento_b is not None
        evento_b_id = evento_b.id
        headers = get_auth_header(client, session)

    response = client.get(f"/leads?evento_id={evento_b_id}&page_size=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "ana@example.com"
    assert data["items"][0]["evento_convertido_nome"] == "Evento B"


def test_listar_leads_total_e_paginacao_com_filtro_de_data(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/leads?data_inicio=2026-01-08&data_fim=2026-01-09&page=1&page_size=1",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1

    page_2 = client.get(
        "/leads?data_inicio=2026-01-08&data_fim=2026-01-09&page=2&page_size=1",
        headers=headers,
    )
    assert page_2.status_code == 200
    data_2 = page_2.json()
    assert data_2["total"] == 2
    assert len(data_2["items"]) == 1
    emails = {data["items"][0]["email"], data_2["items"][0]["email"]}
    assert emails == {"carla@example.com", "bruno@example.com"}
