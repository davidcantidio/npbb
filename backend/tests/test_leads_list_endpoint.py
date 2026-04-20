from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import LeadBatch
from app.models.models import (
    Agencia,
    Evento,
    Lead,
    LeadConversao,
    LeadConversaoTipo,
    StatusEvento,
    TipoEvento,
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
    uploader = Usuario(
        email="batch@npbb.com.br",
        password_hash=hash_password("senha123"),
        tipo_usuario="npbb",
        ativo=True,
    )
    agencia = Agencia(nome="Agencia 1", dominio="ag1.com.br", lote=1)
    status = StatusEvento(nome="Ativo")
    tipo_evento = TipoEvento(nome="Esporte")
    session.add_all([uploader, agencia, status, tipo_evento])
    session.commit()
    session.refresh(uploader)
    session.refresh(agencia)
    session.refresh(status)
    session.refresh(tipo_evento)

    evento_a = Evento(
        nome="Evento A",
        descricao="Desc A",
        concorrencia=False,
        cidade="Sao Paulo",
        estado="SP",
        data_inicio_prevista=date(2026, 2, 10),
        agencia_id=agencia.id,
        status_id=status.id,
        tipo_id=tipo_evento.id,
    )
    evento_b = Evento(
        nome="Evento B",
        descricao="Desc B",
        concorrencia=False,
        cidade="Rio de Janeiro",
        estado="RJ",
        data_inicio_prevista=date(2026, 3, 11),
        agencia_id=agencia.id,
        status_id=status.id,
    )
    evento_c = Evento(
        nome="Evento C",
        descricao="Desc C",
        concorrencia=False,
        cidade="Navegantes",
        estado="SC",
        data_inicio_prevista=date(2026, 4, 2),
        agencia_id=agencia.id,
        status_id=status.id,
    )
    evento_d = Evento(
        nome="Evento D",
        descricao="Desc D",
        concorrencia=False,
        cidade="Recife",
        estado="PE",
        data_inicio_prevista=date(2026, 5, 3),
        agencia_id=agencia.id,
        status_id=status.id,
        tipo_id=tipo_evento.id,
    )
    session.add_all([evento_a, evento_b, evento_c, evento_d])
    session.commit()
    session.refresh(evento_a)
    session.refresh(evento_b)
    session.refresh(evento_c)
    session.refresh(evento_d)

    batch_lead_3 = LeadBatch(
        enviado_por=uploader.id,
        plataforma_origem="Meta Ads",
        data_envio=datetime(2026, 1, 8, tzinfo=timezone.utc),
        nome_arquivo_original="lead-3.csv",
        arquivo_bronze=b"csv",
        evento_id=evento_c.id,
    )
    batch_lead_4 = LeadBatch(
        enviado_por=uploader.id,
        plataforma_origem="Meta Ads",
        data_envio=datetime(2026, 1, 7, tzinfo=timezone.utc),
        nome_arquivo_original="lead-4.csv",
        arquivo_bronze=b"csv",
        evento_id=evento_d.id,
    )
    session.add_all([batch_lead_3, batch_lead_4])
    session.commit()
    session.refresh(batch_lead_3)
    session.refresh(batch_lead_4)

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
        data_nascimento=date(2000, 6, 20),
        data_criacao=datetime(2026, 1, 8, tzinfo=timezone.utc),
        batch_id=batch_lead_3.id,
    )
    lead_4 = Lead(
        nome="Davi",
        sobrenome="Santos",
        email="davi@example.com",
        cpf="00000000004",
        data_nascimento=date(1995, 1, 10),
        data_criacao=datetime(2026, 1, 7, tzinfo=timezone.utc),
        batch_id=batch_lead_4.id,
    )
    session.add_all([lead_1, lead_2, lead_3, lead_4])
    session.commit()
    session.refresh(lead_1)
    session.refresh(lead_2)
    session.refresh(lead_3)
    session.refresh(lead_4)

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
    assert data["total"] == 4

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
    assert data_1["total"] == 4
    assert len(data_1["items"]) == 2

    page_2 = client.get("/leads?page=2&page_size=2", headers=headers)
    assert page_2.status_code == 200
    data_2 = page_2.json()
    assert data_2["total"] == 4
    assert len(data_2["items"]) == 2


def test_listar_leads_requer_autenticacao(client, engine):
    with Session(engine) as session:
        seed_leads(session)

    response = client.get("/leads")
    assert response.status_code == 401


def test_listar_leads_filtra_por_data_evento(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/leads?data_inicio=2026-03-11&data_fim=2026-03-11&page_size=10",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "ana@example.com"


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


def test_listar_leads_filtra_por_evento_id_de_origem_do_lote_sem_conversao(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        evento_c = session.exec(select(Evento).where(Evento.nome == "Evento C")).first()
        assert evento_c is not None
        evento_c_id = evento_c.id
        headers = get_auth_header(client, session)

    response = client.get(f"/leads?evento_id={evento_c_id}&page_size=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "carla@example.com"
    assert data["items"][0]["evento_convertido_nome"] is None


def test_listar_leads_faz_fallback_do_evento_de_origem_para_exportacao(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get("/leads?page=1&page_size=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    items_by_email = {item["email"]: item for item in data["items"]}

    lead_carla = items_by_email["carla@example.com"]
    assert lead_carla["evento_convertido_nome"] is None
    assert lead_carla["data_evento"] == "2026-04-02 00:00:00"
    assert lead_carla["tipo_evento"] == "ESPORTE"
    assert lead_carla["local_evento"] == "Navegantes-SC"
    assert lead_carla["soma_de_ano_evento"] == 2026
    assert lead_carla["soma_de_idade"] == 25


def test_listar_leads_faz_fallback_do_tipo_evento_de_origem_quando_existir_no_banco(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get("/leads?page=1&page_size=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    items_by_email = {item["email"]: item for item in data["items"]}

    lead_davi = items_by_email["davi@example.com"]
    assert lead_davi["evento_convertido_nome"] is None
    assert lead_davi["tipo_evento"] == "Esporte"
    assert lead_davi["local_evento"] == "Recife-PE"
    assert lead_davi["data_evento"] == "2026-05-03 00:00:00"


def test_listar_leads_total_e_paginacao_com_filtro_de_data(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/leads?data_inicio=2026-04-01&data_fim=2026-05-31&page=1&page_size=1",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1

    page_2 = client.get(
        "/leads?data_inicio=2026-04-01&data_fim=2026-05-31&page=2&page_size=1",
        headers=headers,
    )
    assert page_2.status_code == 200
    data_2 = page_2.json()
    assert data_2["total"] == 2
    assert len(data_2["items"]) == 1
    emails = {data["items"][0]["email"], data_2["items"][0]["email"]}
    assert emails == {"carla@example.com", "davi@example.com"}


def test_listar_leads_aceita_flag_long_running_sem_alterar_payload(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get("/leads?page=1&page_size=10&long_running=true", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4


def test_listar_leads_timeout_helper_ignora_sqlite(monkeypatch, engine):
    from app.routers.leads import LeadListQuery, _configure_listar_leads_statement_timeout

    monkeypatch.setenv("LEADS_EXPORT_STATEMENT_TIMEOUT_MS", "900000")
    with Session(engine) as session:
        _configure_listar_leads_statement_timeout(session, LeadListQuery(long_running=True))


def test_listar_leads_timeout_helper_aplica_set_local_em_postgres(monkeypatch):
    from app.routers.leads import LeadListQuery, _configure_listar_leads_statement_timeout

    monkeypatch.setenv("LEADS_EXPORT_STATEMENT_TIMEOUT_MS", "900000")

    class FakeDialect:
        name = "postgresql"

    class FakeBind:
        dialect = FakeDialect()

    class FakeSession:
        def __init__(self):
            self.executed = []

        def get_bind(self):
            return FakeBind()

        def exec(self, statement):
            self.executed.append(str(statement))

    session = FakeSession()
    _configure_listar_leads_statement_timeout(session, LeadListQuery(long_running=True))

    assert session.executed == ["SET LOCAL statement_timeout = 900000"]


def test_exportar_leads_csv_retorna_arquivo_e_aplica_filtros(client, engine):
    with Session(engine) as session:
        seed_leads(session)
        headers = get_auth_header(client, session)

    response = client.get(
        "/leads/export/csv?data_inicio=2026-03-11&data_fim=2026-03-11",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith('attachment; filename="leads-')
    assert response.headers["content-type"].startswith("text/csv")

    content = response.content.decode("utf-8-sig")
    lines = [line for line in content.split("\r\n") if line]
    assert (
        lines[0]
        == "nome,cpf,data_nascimento,email,telefone,origem,evento,tipo_evento,local,data_evento"
    )
    assert "ana@example.com" in lines[1]
    assert "bruno@example.com" not in content


def test_exportar_leads_csv_retorna_204_quando_nao_existirem_leads(client, engine):
    with Session(engine) as session:
        headers = get_auth_header(client, session)

    response = client.get("/leads/export/csv", headers=headers)
    assert response.status_code == 204
    assert response.content == b""
