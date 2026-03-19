from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.models import (
    Agencia,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
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


def add_direct_canonical_link(session: Session, *, evento: Evento, lead: Lead) -> None:
    session.add(
        LeadEvento(
            lead_id=lead.id,
            evento_id=evento.id,
            source_kind=LeadEventoSourceKind.EVENT_DIRECT,
            source_ref_id=evento.id,
        )
    )


def seed_report_data(session: Session):
    agencia = Agencia(nome="Agencia 1", dominio="ag1.com.br", lote=1)
    status = StatusEvento(nome="Ativo")
    session.add_all([agencia, status])
    session.commit()
    session.refresh(agencia)
    session.refresh(status)

    evento = Evento(
        nome="Festival TMJ 2025",
        descricao="Desc",
        concorrencia=False,
        cidade="Sao Paulo",
        estado="SP",
        agencia_id=agencia.id,
        status_id=status.id,
        data_inicio_realizada=date(2025, 3, 15),
        publico_realizado=15000,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)

    lead_1 = Lead(
        nome="Ana",
        sobrenome="Silva",
        cpf="00000000001",
        data_nascimento=date(1990, 1, 1),
        genero="F",
        evento_nome="Festival TMJ 2025",
        data_compra=datetime(2025, 2, 1, tzinfo=timezone.utc),
        ingresso_qtd=1,
    )
    lead_2 = Lead(
        nome="Joao",
        sobrenome="Souza",
        cpf="00000000002",
        evento_nome="Festival TMJ 2025",
        data_compra=datetime(2025, 3, 1, tzinfo=timezone.utc),
        ingresso_qtd=1,
    )
    lead_outro = Lead(
        nome="Outro",
        sobrenome="Evento",
        cpf="00000000003",
        evento_nome="Outro Evento",
        data_compra=datetime(2025, 2, 5, tzinfo=timezone.utc),
    )
    session.add_all([lead_1, lead_2, lead_outro])
    session.commit()
    session.refresh(lead_1)
    session.refresh(lead_2)

    add_direct_canonical_link(session, evento=evento, lead=lead_1)
    add_direct_canonical_link(session, evento=evento, lead=lead_2)
    session.commit()

    return {"evento_id": evento.id, "evento_nome": evento.nome}


def get_auth_header(client: TestClient, session: Session) -> dict[str, str]:
    user = seed_user(session)
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_leads_relatorio_ok(client, engine):
    with Session(engine) as session:
        ids = seed_report_data(session)
        headers = get_auth_header(client, session)

    response = client.get(f"/dashboard/leads/relatorio?evento_id={ids['evento_id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["big_numbers"]["total_leads"] == 2
    assert data["big_numbers"]["total_compras"] == 2
    assert data["big_numbers"]["total_publico"] == 15000
    assert data["filters"]["evento_id"] == ids["evento_id"]


def test_dashboard_leads_relatorio_fallback_evento_nome(client, engine):
    with Session(engine) as session:
        ids = seed_report_data(session)
        headers = get_auth_header(client, session)

    response = client.get(
        f"/dashboard/leads/relatorio?evento_nome={ids['evento_nome']}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["big_numbers"]["total_leads"] == 2
    assert data["filters"]["evento_nome"] == "festival tmj 2025"


def test_dashboard_leads_relatorio_requires_auth(client, engine):
    with Session(engine) as session:
        ids = seed_report_data(session)

    response = client.get(f"/dashboard/leads/relatorio?evento_id={ids['evento_id']}")
    assert response.status_code == 401
