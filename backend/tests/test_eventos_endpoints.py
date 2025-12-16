import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from datetime import date
from decimal import Decimal

from app.db.database import get_session
from app.main import app
from app.models.models import Agencia, Ativacao, CotaCortesia, Diretoria, Evento, TipoEvento, Usuario
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


def seed_agencia(session: Session, nome: str, dominio: str) -> Agencia:
    agencia = Agencia(nome=nome, dominio=dominio, lote=1)
    session.add(agencia)
    session.commit()
    session.refresh(agencia)
    return agencia


def seed_tipo(session: Session, nome: str = "Congresso") -> TipoEvento:
    tipo = TipoEvento(nome=nome)
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo


def seed_user(session: Session, email: str, password: str, tipo: str, agencia_id: int | None = None) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario=tipo,
        agencia_id=agencia_id,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def seed_evento(
    session: Session,
    *,
    agencia_id: int,
    tipo_id: int,
    nome: str,
    cidade: str,
    estado: str,
    inicio: date,
    fim: date,
) -> Evento:
    evento = Evento(
        nome=nome,
        descricao="descricao",
        concorrencia=False,
        cidade=cidade,
        estado=estado,
        agencia_id=agencia_id,
        tipo_id=tipo_id,
        status="Previsto",
        data_inicio_prevista=inicio,
        data_fim_prevista=fim,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def seed_diretoria(session: Session, nome: str = "dimac") -> Diretoria:
    diretoria = Diretoria(nome=nome)
    session.add(diretoria)
    session.commit()
    session.refresh(diretoria)
    return diretoria


def test_evento_list_paginado_e_filtros(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        user = seed_user(session, "user@example.com", "Senha123!", "npbb")

        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento Alpha",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 2),
        )
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento Beta",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 2, 10),
            fim=date(2025, 2, 12),
        )
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Outro",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 3, 1),
            fim=date(2025, 3, 1),
        )

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp = client.get("/evento?limit=2", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Total-Count") == "3"
    assert len(resp.json()) == 2

    resp_sp = client.get("/evento?estado=sp", headers={"Authorization": f"Bearer {token}"})
    assert resp_sp.status_code == 200
    assert resp_sp.headers.get("X-Total-Count") == "2"

    resp_city = client.get("/evento?cidade=sao%20paulo", headers={"Authorization": f"Bearer {token}"})
    assert resp_city.status_code == 200
    assert resp_city.headers.get("X-Total-Count") == "2"

    resp_search = client.get("/evento?search=beta", headers={"Authorization": f"Bearer {token}"})
    assert resp_search.status_code == 200
    assert resp_search.headers.get("X-Total-Count") == "1"
    assert resp_search.json()[0]["nome"] == "Evento Beta"

    resp_date = client.get("/evento?data=2025-02-11", headers={"Authorization": f"Bearer {token}"})
    assert resp_date.status_code == 200
    assert resp_date.headers.get("X-Total-Count") == "1"
    assert resp_date.json()[0]["nome"] == "Evento Beta"


def test_evento_dicionarios_cidades_estados(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento B",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 1, 2),
            fim=date(2025, 1, 2),
        )

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    cities = client.get("/evento/all/cidades", headers={"Authorization": f"Bearer {token}"}).json()
    states = client.get("/evento/all/estados", headers={"Authorization": f"Bearer {token}"}).json()
    assert "Sao Paulo" in cities
    assert "Rio de Janeiro" in cities
    assert "SP" in states
    assert "RJ" in states


def test_evento_get_por_id_e_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)

        evento_ag1 = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A1",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_ag2 = seed_evento(
            session,
            agencia_id=ag2.id,
            tipo_id=tipo.id,
            nome="Evento A2",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 1, 2),
            fim=date(2025, 1, 2),
        )
        evento_ag1_id = evento_ag1.id
        evento_ag2_id = evento_ag2.id

        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag1.id)

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")

    ok = client.get(f"/evento/{evento_ag1_id}", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
    assert ok.json()["id"] == evento_ag1_id

    forbidden = client.get(f"/evento/{evento_ag2_id}", headers={"Authorization": f"Bearer {token}"})
    assert forbidden.status_code == 404


def test_evento_criar_atualizar_e_excluir(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        ag1_id = ag1.id
        tipo_id = tipo.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    create_resp = client.post(
        "/evento",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Evento Novo",
            "descricao": "descricao",
            "cidade": "Sao Paulo",
            "estado": "sp",
            "agencia_id": ag1_id,
            "tipo_id": tipo_id,
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"]
    assert created["nome"] == "Evento Novo"
    assert created["estado"] == "SP"

    evento_id = created["id"]

    update_resp = client.put(
        f"/evento/{evento_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"cidade": "Rio de Janeiro", "estado": "rj"},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["cidade"] == "Rio de Janeiro"
    assert updated["estado"] == "RJ"

    delete_resp = client.delete(
        f"/evento/{evento_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/evento/{evento_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404


def test_evento_delete_bloqueado_por_dependencias(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")

        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento Bloqueado",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id
        ativacao = Ativacao(
            nome="Ativacao",
            descricao="desc",
            evento_id=evento_id,
            valor=Decimal("10.00"),
        )
        session.add(ativacao)
        session.commit()

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.delete(f"/evento/{evento_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert detail["code"] == "EVENTO_DELETE_BLOCKED"
    assert "ativacoes" in detail["dependencies"]
