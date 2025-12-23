from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import Agencia, Evento, StatusEvento, TipoEvento, Usuario
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
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "http://localhost:5173")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for nome in ["Previsto", "A Confirmar", "Confirmado", "Realizado", "Cancelado"]:
            exists = session.exec(select(StatusEvento).where(StatusEvento.nome == nome)).first()
            if not exists:
                session.add(StatusEvento(nome=nome))
        session.commit()

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
    status_nome: str = "Previsto",
) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == status_nome)).first()
    assert status and status.id
    evento = Evento(
        nome=nome,
        descricao="descricao",
        concorrencia=False,
        cidade=cidade,
        estado=estado,
        agencia_id=agencia_id,
        tipo_id=tipo_id,
        status_id=status.id,
        data_inicio_prevista=inicio,
        data_fim_prevista=fim,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def test_evento_gamificacoes_get_retorna_lista_vazia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.get(f"/evento/{evento_id}/gamificacoes", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_evento_gamificacoes_post_cria_e_get_retorna_ordenado(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_create_2 = client.post(
        f"/evento/{evento_id}/gamificacoes",
        json={
            "nome": "G2",
            "descricao": "Descricao 2",
            "premio": "Premio 2",
            "titulo_feedback": "Titulo 2",
            "texto_feedback": "Texto 2",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_create_2.status_code == 201
    assert resp_create_2.json()["evento_id"] == evento_id

    resp_create_1 = client.post(
        f"/evento/{evento_id}/gamificacoes",
        json={
            "nome": "G1",
            "descricao": "Descricao 1",
            "premio": "Premio 1",
            "titulo_feedback": "Titulo 1",
            "texto_feedback": "Texto 1",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_create_1.status_code == 201
    assert resp_create_1.json()["evento_id"] == evento_id

    resp_list = client.get(f"/evento/{evento_id}/gamificacoes", headers={"Authorization": f"Bearer {token}"})
    assert resp_list.status_code == 200
    payload = resp_list.json()
    assert len(payload) == 2
    ids = [item["id"] for item in payload]
    assert ids == sorted(ids)


def test_evento_gamificacoes_aplica_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag2.id)
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")

    resp_get = client.get(f"/evento/{evento_id}/gamificacoes", headers={"Authorization": f"Bearer {token}"})
    assert resp_get.status_code == 404
    assert resp_get.json()["detail"]["code"] == "EVENTO_NOT_FOUND"

    resp_post = client.post(
        f"/evento/{evento_id}/gamificacoes",
        json={
            "nome": "G1",
            "descricao": "Descricao",
            "premio": "Premio",
            "titulo_feedback": "Titulo",
            "texto_feedback": "Texto",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_post.status_code == 404
    assert resp_post.json()["detail"]["code"] == "EVENTO_NOT_FOUND"


def test_gamificacao_put_atualiza_e_delete_remove(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_create = client.post(
        f"/evento/{evento_id}/gamificacoes",
        json={
            "nome": "G1",
            "descricao": "Descricao 1",
            "premio": "Premio 1",
            "titulo_feedback": "Titulo 1",
            "texto_feedback": "Texto 1",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_create.status_code == 201
    gamificacao_id = resp_create.json()["id"]

    resp_update = client.put(
        f"/gamificacao/{gamificacao_id}",
        json={"premio": "Premio atualizado", "texto_feedback": "Texto atualizado"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["premio"] == "Premio atualizado"
    assert resp_update.json()["texto_feedback"] == "Texto atualizado"

    resp_delete = client.delete(
        f"/gamificacao/{gamificacao_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_delete.status_code == 204

    resp_list = client.get(f"/evento/{evento_id}/gamificacoes", headers={"Authorization": f"Bearer {token}"})
    assert resp_list.status_code == 200
    assert resp_list.json() == []


def test_gamificacao_put_delete_aplica_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag2.id)
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token_npbb = login_and_get_token(client, "user@example.com", "Senha123!")
    resp_create = client.post(
        f"/evento/{evento_id}/gamificacoes",
        json={
            "nome": "G1",
            "descricao": "Descricao 1",
            "premio": "Premio 1",
            "titulo_feedback": "Titulo 1",
            "texto_feedback": "Texto 1",
        },
        headers={"Authorization": f"Bearer {token_npbb}"},
    )
    assert resp_create.status_code == 201
    gamificacao_id = resp_create.json()["id"]

    token_agencia = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")
    resp_update = client.put(
        f"/gamificacao/{gamificacao_id}",
        json={"premio": "X"},
        headers={"Authorization": f"Bearer {token_agencia}"},
    )
    assert resp_update.status_code == 404
    assert resp_update.json()["detail"]["code"] == "GAMIFICACAO_NOT_FOUND"

    resp_delete = client.delete(
        f"/gamificacao/{gamificacao_id}",
        headers={"Authorization": f"Bearer {token_agencia}"},
    )
    assert resp_delete.status_code == 404
    assert resp_delete.json()["detail"]["code"] == "GAMIFICACAO_NOT_FOUND"
