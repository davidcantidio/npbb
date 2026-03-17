from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.models.models import (
    Agencia,
    Ativacao,
    AtivacaoLead,
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
    from app.main import app

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_models_aggregate_exports_lead_event_symbols():
    assert LeadEvento.__name__ == "LeadEvento"
    assert LeadEventoSourceKind.EVENT_DIRECT.value == "event_id_direct"


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


def seed_dashboard_data(session: Session):
    agencia = Agencia(nome="Agencia 1", dominio="ag1.com.br", lote=1)
    status = StatusEvento(nome="Ativo")
    session.add_all([agencia, status])
    session.commit()
    session.refresh(agencia)
    session.refresh(status)

    evento_sp = Evento(
        nome="Evento SP",
        descricao="Desc",
        concorrencia=False,
        cidade="Sao Paulo",
        estado="SP",
        agencia_id=agencia.id,
        status_id=status.id,
    )
    evento_rj = Evento(
        nome="Evento RJ",
        descricao="Desc",
        concorrencia=False,
        cidade="Rio",
        estado="RJ",
        agencia_id=agencia.id,
        status_id=status.id,
    )
    session.add_all([evento_sp, evento_rj])
    session.commit()
    session.refresh(evento_sp)
    session.refresh(evento_rj)

    ativacao_sp = Ativacao(nome="Ativacao SP", evento_id=evento_sp.id)
    ativacao_rj = Ativacao(nome="Ativacao RJ", evento_id=evento_rj.id)
    session.add_all([ativacao_sp, ativacao_rj])
    session.commit()
    session.refresh(ativacao_sp)
    session.refresh(ativacao_rj)

    lead_sp = Lead(
        nome="Joao",
        sobrenome="Silva",
        cpf="00000000001",
        data_nascimento=date(1990, 1, 1),
        data_criacao=datetime(2026, 1, 5, tzinfo=timezone.utc),
    )
    lead_rj = Lead(
        nome="Maria",
        sobrenome="Souza",
        cpf="00000000002",
        data_nascimento=date(1991, 2, 2),
        data_criacao=datetime(2026, 1, 10, tzinfo=timezone.utc),
    )
    session.add_all([lead_sp, lead_rj])
    session.commit()
    session.refresh(lead_sp)
    session.refresh(lead_rj)

    session.add_all(
        [
            AtivacaoLead(ativacao_id=ativacao_sp.id, lead_id=lead_sp.id),
            AtivacaoLead(ativacao_id=ativacao_rj.id, lead_id=lead_rj.id),
        ]
    )
    session.commit()

    return {
        "evento_sp_id": evento_sp.id,
        "evento_rj_id": evento_rj.id,
        "ativacao_sp_id": ativacao_sp.id,
        "ativacao_rj_id": ativacao_rj.id,
    }


def get_auth_header(client: TestClient, session: Session) -> dict[str, str]:
    user = seed_user(session)
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_leads_ok(client, engine):
    with Session(engine) as session:
        seed_dashboard_data(session)
        headers = get_auth_header(client, session)

    response = client.get("/dashboard/leads", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"]["leads_total"] == 2
    assert data["kpis"]["eventos_total"] == 2


def test_dashboard_leads_filter_estado(client, engine):
    with Session(engine) as session:
        seed_dashboard_data(session)
        headers = get_auth_header(client, session)

    response = client.get("/dashboard/leads?estado=SP", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"]["leads_total"] == 1
    assert data["rankings"]["por_estado"][0]["estado"] == "SP"


def test_dashboard_leads_filter_evento_id(client, engine):
    with Session(engine) as session:
        ids = seed_dashboard_data(session)
        headers = get_auth_header(client, session)

    response = client.get(f"/dashboard/leads?evento_id={ids['evento_sp_id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"]["leads_total"] == 1


def test_dashboard_leads_filter_evento_nome(client, engine):
    with Session(engine) as session:
        seed_dashboard_data(session)
        headers = get_auth_header(client, session)

    response = client.get("/dashboard/leads?evento_nome=Evento SP", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"]["leads_total"] == 1


def test_dashboard_leads_rankings_order(client, engine):
    with Session(engine) as session:
        ids = seed_dashboard_data(session)
        lead_extra = Lead(
            nome="Pedro",
            sobrenome="Souza",
            cpf="00000000003",
            data_nascimento=date(1992, 3, 3),
            data_criacao=datetime(2026, 1, 12, tzinfo=timezone.utc),
        )
        session.add(lead_extra)
        session.commit()
        session.refresh(lead_extra)
        session.add(
            AtivacaoLead(
                ativacao_id=ids["ativacao_sp_id"],
                lead_id=lead_extra.id,
            )
        )
        session.commit()
        headers = get_auth_header(client, session)

    response = client.get("/dashboard/leads", headers=headers)
    assert response.status_code == 200
    data = response.json()
    ranking = data["rankings"]["por_estado"]
    assert ranking[0]["estado"] == "SP"
    assert ranking[0]["total"] == 2
    assert ranking[1]["estado"] == "RJ"


def test_dashboard_leads_requires_auth(client, engine):
    with Session(engine) as session:
        seed_dashboard_data(session)

    response = client.get("/dashboard/leads")
    assert response.status_code == 401
