from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.models import Agencia, Ativacao, AtivacaoLead, Evento, Lead, StatusEvento, Usuario
from app.utils.security import hash_password


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def birthdate_for_age(age: int, reference_date: date) -> date:
    try:
        return reference_date.replace(year=reference_date.year - age)
    except ValueError:
        return reference_date.replace(month=2, day=28, year=reference_date.year - age)


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    monkeypatch.setenv("DASHBOARD_BB_COVERAGE_THRESHOLD_PCT", "80")
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
    session: Session,
    email: str = "user@npbb.com.br",
    password: str = "senha123",
    tipo_usuario: str = "npbb",
    agencia_id: int | None = None,
) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario=tipo_usuario,
        agencia_id=agencia_id,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_auth_header(
    client: TestClient,
    session: Session,
    *,
    email: str = "user@npbb.com.br",
    password: str = "senha123",
    tipo_usuario: str = "npbb",
    agencia_id: int | None = None,
) -> dict[str, str]:
    user = seed_user(
        session,
        email=email,
        password=password,
        tipo_usuario=tipo_usuario,
        agencia_id=agencia_id,
    )
    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_age_analysis_data(session: Session) -> dict[str, int]:
    today = date.today()

    agencia = Agencia(nome="Agencia 1", dominio="ag1.com.br", lote=1)
    status = StatusEvento(nome="Ativo")
    session.add_all([agencia, status])
    session.commit()
    session.refresh(agencia)
    session.refresh(status)

    eventos = [
        Evento(
            nome="Evento Alpha",
            descricao="Desc",
            concorrencia=False,
            cidade="Sao Paulo",
            estado="SP",
            agencia_id=agencia.id,
            status_id=status.id,
        ),
        Evento(
            nome="Evento Beta",
            descricao="Desc",
            concorrencia=False,
            cidade="Rio",
            estado="RJ",
            agencia_id=agencia.id,
            status_id=status.id,
        ),
        Evento(
            nome="Evento Gamma",
            descricao="Desc",
            concorrencia=False,
            cidade="Belo Horizonte",
            estado="MG",
            agencia_id=agencia.id,
            status_id=status.id,
        ),
        Evento(
            nome="Evento Delta",
            descricao="Desc",
            concorrencia=False,
            cidade="Brasilia",
            estado="DF",
            agencia_id=agencia.id,
            status_id=status.id,
        ),
    ]
    session.add_all(eventos)
    session.commit()
    for evento in eventos:
        session.refresh(evento)

    ativacoes = [Ativacao(nome=f"Ativacao {evento.nome}", evento_id=evento.id) for evento in eventos]
    session.add_all(ativacoes)
    session.commit()
    for ativacao in ativacoes:
        session.refresh(ativacao)

    leads_specs = [
        ("Evento Alpha", birthdate_for_age(18, today), True, datetime(2026, 1, 5, tzinfo=timezone.utc)),
        ("Evento Alpha", birthdate_for_age(25, today), False, datetime(2026, 1, 6, tzinfo=timezone.utc)),
        ("Evento Alpha", birthdate_for_age(41, today), True, datetime(2026, 1, 7, tzinfo=timezone.utc)),
        ("Evento Alpha", None, None, datetime(2026, 1, 8, tzinfo=timezone.utc)),
        ("Evento Beta", birthdate_for_age(26, today), True, datetime(2026, 1, 9, tzinfo=timezone.utc)),
        ("Evento Beta", birthdate_for_age(40, today), True, datetime(2026, 1, 10, tzinfo=timezone.utc)),
        ("Evento Beta", birthdate_for_age(17, today), False, datetime(2026, 1, 11, tzinfo=timezone.utc)),
        ("Evento Gamma", birthdate_for_age(19, today), True, datetime(2026, 1, 12, tzinfo=timezone.utc)),
        ("Evento Gamma", birthdate_for_age(45, today), False, datetime(2026, 1, 13, tzinfo=timezone.utc)),
        ("Evento Delta", birthdate_for_age(22, today), False, datetime(2026, 1, 14, tzinfo=timezone.utc)),
    ]

    evento_by_name = {evento.nome: evento for evento in eventos}
    ativacao_by_event_id = {ativacao.evento_id: ativacao for ativacao in ativacoes}

    created_leads: list[Lead] = []
    for index, (evento_nome, nascimento, is_cliente_bb, data_criacao) in enumerate(leads_specs, start=1):
        lead = Lead(
            nome=f"Lead {index}",
            sobrenome="Teste",
            cpf=f"{index:011d}",
            evento_nome=evento_nome,
            data_nascimento=nascimento,
            is_cliente_bb=is_cliente_bb,
            data_criacao=data_criacao,
        )
        session.add(lead)
        created_leads.append(lead)
    session.commit()
    for lead in created_leads:
        session.refresh(lead)

    for lead in created_leads:
        evento = evento_by_name[lead.evento_nome]
        ativacao = ativacao_by_event_id[evento.id]
        session.add(AtivacaoLead(ativacao_id=ativacao.id, lead_id=lead.id))
    session.commit()

    return {
        "evento_alpha_id": evento_by_name["Evento Alpha"].id,
        "evento_beta_id": evento_by_name["Evento Beta"].id,
        "evento_gamma_id": evento_by_name["Evento Gamma"].id,
        "evento_delta_id": evento_by_name["Evento Delta"].id,
    }


def test_dashboard_age_analysis_ok(client, engine):
    with Session(engine) as session:
        ids = seed_age_analysis_data(session)
        headers = get_auth_header(client, session)

    response = client.get("/dashboard/leads/analise-etaria", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["filters"]["evento_id"] is None
    assert [item["evento_nome"] for item in data["por_evento"]] == [
        "Evento Alpha",
        "Evento Beta",
        "Evento Gamma",
        "Evento Delta",
    ]

    alpha = data["por_evento"][0]
    assert alpha["evento_id"] == ids["evento_alpha_id"]
    assert alpha["base_leads"] == 4
    assert alpha["clientes_bb_volume"] is None
    assert alpha["clientes_bb_pct"] is None
    assert alpha["cobertura_bb_pct"] == 75.0
    assert alpha["faixa_dominante"] == "faixa_18_25"
    assert alpha["faixas"]["faixa_18_25"]["volume"] == 2
    assert alpha["faixas"]["faixa_18_25"]["pct"] == 66.67
    assert alpha["faixas"]["fora_18_40"]["volume"] == 1
    assert alpha["faixas"]["sem_info_volume"] == 1
    assert alpha["faixas"]["sem_info_pct_da_base"] == 25.0

    beta = data["por_evento"][1]
    assert beta["evento_id"] == ids["evento_beta_id"]
    assert beta["base_leads"] == 3
    assert beta["clientes_bb_volume"] == 2
    assert beta["clientes_bb_pct"] == 66.67
    assert beta["cobertura_bb_pct"] == 100.0
    assert beta["faixa_dominante"] == "faixa_26_40"

    consolidado = data["consolidado"]
    assert consolidado["base_total"] == 10
    assert consolidado["clientes_bb_volume"] == 5
    assert consolidado["clientes_bb_pct"] == 50.0
    assert consolidado["cobertura_bb_pct"] == 90.0
    assert consolidado["faixas"]["faixa_18_25"]["volume"] == 4
    assert consolidado["faixas"]["faixa_26_40"]["volume"] == 2
    assert consolidado["faixas"]["fora_18_40"]["volume"] == 3
    assert consolidado["faixas"]["sem_info_volume"] == 1
    assert [item["evento_nome"] for item in consolidado["top_eventos"]] == [
        "Evento Alpha",
        "Evento Beta",
        "Evento Gamma",
    ]
    assert consolidado["media_por_evento"] == 2.5
    assert consolidado["mediana_por_evento"] == 2.5
    assert consolidado["concentracao_top3_pct"] == 90.0


def test_dashboard_age_analysis_filter_evento_id(client, engine):
    with Session(engine) as session:
        ids = seed_age_analysis_data(session)
        headers = get_auth_header(client, session)

    response = client.get(
        f"/dashboard/leads/analise-etaria?evento_id={ids['evento_beta_id']}",
        headers=headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["filters"]["evento_id"] == ids["evento_beta_id"]
    assert len(data["por_evento"]) == 1
    assert data["por_evento"][0]["evento_nome"] == "Evento Beta"
    assert data["consolidado"]["base_total"] == 3
    assert data["consolidado"]["top_eventos"][0]["evento_nome"] == "Evento Beta"


def test_dashboard_age_analysis_filter_data_intervalo_inclusivo(client, engine):
    with Session(engine) as session:
        seed_age_analysis_data(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/dashboard/leads/analise-etaria?data_inicio=2026-01-10&data_fim=2026-01-10",
        headers=headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["por_evento"]) == 1
    assert data["por_evento"][0]["evento_nome"] == "Evento Beta"
    assert data["por_evento"][0]["base_leads"] == 1
    assert data["consolidado"]["base_total"] == 1


def test_dashboard_age_analysis_empty_response(client, engine):
    with Session(engine) as session:
        headers = get_auth_header(client, session)

    response = client.get("/dashboard/leads/analise-etaria?evento_id=999999", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["por_evento"] == []
    assert data["consolidado"]["base_total"] == 0
    assert data["consolidado"]["clientes_bb_volume"] is None
    assert data["consolidado"]["clientes_bb_pct"] is None
    assert data["consolidado"]["top_eventos"] == []
    assert data["consolidado"]["media_por_evento"] == 0.0
    assert data["consolidado"]["mediana_por_evento"] == 0.0
    assert data["consolidado"]["concentracao_top3_pct"] == 0.0


def test_dashboard_age_analysis_requires_auth(client, engine):
    with Session(engine) as session:
        seed_age_analysis_data(session)

    response = client.get("/dashboard/leads/analise-etaria")
    assert response.status_code == 401


def test_dashboard_age_analysis_invalid_date_range_returns_422(client, engine):
    with Session(engine) as session:
        seed_age_analysis_data(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/dashboard/leads/analise-etaria?data_inicio=2026-01-31&data_fim=2026-01-01",
        headers=headers,
    )
    assert response.status_code == 422
    assert "data_fim deve ser maior/igual a data_inicio" in response.text


def test_dashboard_age_analysis_agencia_sem_agencia_id_retorna_403(client, engine):
    with Session(engine) as session:
        seed_age_analysis_data(session)
        headers = get_auth_header(
            client,
            session,
            email="agencia-sem-id@npbb.com.br",
            tipo_usuario="agencia",
            agencia_id=None,
        )

    response = client.get("/dashboard/leads/analise-etaria", headers=headers)
    assert response.status_code == 403
    payload = response.json()
    assert payload["detail"]["code"] == "FORBIDDEN"


def test_dashboard_age_analysis_agencia_ve_apenas_sua_agencia(client, engine):
    with Session(engine) as session:
        today = date.today()
        agencia_a = Agencia(nome="Agencia A", dominio="ag-a.com.br", lote=1)
        agencia_b = Agencia(nome="Agencia B", dominio="ag-b.com.br", lote=2)
        status = StatusEvento(nome="Ativo")
        session.add_all([agencia_a, agencia_b, status])
        session.commit()
        session.refresh(agencia_a)
        session.refresh(agencia_b)
        session.refresh(status)

        evento_a = Evento(
            nome="Evento Agencia A",
            descricao="Desc",
            concorrencia=False,
            cidade="Sao Paulo",
            estado="SP",
            agencia_id=agencia_a.id,
            status_id=status.id,
        )
        evento_b = Evento(
            nome="Evento Agencia B",
            descricao="Desc",
            concorrencia=False,
            cidade="Rio",
            estado="RJ",
            agencia_id=agencia_b.id,
            status_id=status.id,
        )
        session.add_all([evento_a, evento_b])
        session.commit()
        session.refresh(evento_a)
        session.refresh(evento_b)

        ativacao_a = Ativacao(nome="Ativacao A", evento_id=evento_a.id)
        ativacao_b = Ativacao(nome="Ativacao B", evento_id=evento_b.id)
        session.add_all([ativacao_a, ativacao_b])
        session.commit()
        session.refresh(ativacao_a)
        session.refresh(ativacao_b)

        lead_a = Lead(
            nome="Lead A",
            cpf="20000000001",
            evento_nome=evento_a.nome,
            data_nascimento=birthdate_for_age(23, today),
            is_cliente_bb=True,
            data_criacao=datetime(2026, 1, 10, tzinfo=timezone.utc),
        )
        lead_b = Lead(
            nome="Lead B",
            cpf="20000000002",
            evento_nome=evento_b.nome,
            data_nascimento=birthdate_for_age(30, today),
            is_cliente_bb=True,
            data_criacao=datetime(2026, 1, 10, tzinfo=timezone.utc),
        )
        session.add_all([lead_a, lead_b])
        session.commit()
        session.refresh(lead_a)
        session.refresh(lead_b)

        session.add_all(
            [
                AtivacaoLead(ativacao_id=ativacao_a.id, lead_id=lead_a.id),
                AtivacaoLead(ativacao_id=ativacao_b.id, lead_id=lead_b.id),
            ]
        )
        session.commit()

        headers = get_auth_header(
            client,
            session,
            email="agencia-a@npbb.com.br",
            tipo_usuario="agencia",
            agencia_id=agencia_a.id,
        )

    response = client.get("/dashboard/leads/analise-etaria", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["por_evento"]) == 1
    assert data["por_evento"][0]["evento_nome"] == "Evento Agencia A"
    assert data["consolidado"]["base_total"] == 1


def test_dashboard_age_analysis_consolidado_conta_vinculos_mesmo_lead(client, engine):
    with Session(engine) as session:
        today = date.today()
        agencia = Agencia(nome="Agencia 1", dominio="ag-vinculo.com.br", lote=1)
        status = StatusEvento(nome="Ativo")
        session.add_all([agencia, status])
        session.commit()
        session.refresh(agencia)
        session.refresh(status)

        evento_a = Evento(
            nome="Evento Link A",
            descricao="Desc",
            concorrencia=False,
            cidade="Cidade A",
            estado="SP",
            agencia_id=agencia.id,
            status_id=status.id,
        )
        evento_b = Evento(
            nome="Evento Link B",
            descricao="Desc",
            concorrencia=False,
            cidade="Cidade B",
            estado="RJ",
            agencia_id=agencia.id,
            status_id=status.id,
        )
        session.add_all([evento_a, evento_b])
        session.commit()
        session.refresh(evento_a)
        session.refresh(evento_b)

        ativacao_a = Ativacao(nome="Ativacao Link A", evento_id=evento_a.id)
        ativacao_b = Ativacao(nome="Ativacao Link B", evento_id=evento_b.id)
        session.add_all([ativacao_a, ativacao_b])
        session.commit()
        session.refresh(ativacao_a)
        session.refresh(ativacao_b)

        lead = Lead(
            nome="Lead Unico",
            cpf="30000000001",
            evento_nome=evento_a.nome,
            data_nascimento=birthdate_for_age(24, today),
            is_cliente_bb=True,
            data_criacao=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)

        session.add_all(
            [
                AtivacaoLead(ativacao_id=ativacao_a.id, lead_id=lead.id),
                AtivacaoLead(ativacao_id=ativacao_b.id, lead_id=lead.id),
            ]
        )
        session.commit()
        headers = get_auth_header(client, session, email="vinculo@npbb.com.br")

    response = client.get("/dashboard/leads/analise-etaria", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["por_evento"]) == 2
    assert all(item["base_leads"] == 1 for item in data["por_evento"])
    assert data["consolidado"]["base_total"] == 2
    assert data["consolidado"]["faixas"]["faixa_18_25"]["volume"] == 2
