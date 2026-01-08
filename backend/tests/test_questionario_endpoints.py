from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import (
    Agencia,
    Evento,
    QuestionarioOpcao,
    QuestionarioPagina,
    QuestionarioPergunta,
    StatusEvento,
    TipoEvento,
    TipoPergunta,
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


def test_questionario_get_retorna_vazio(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp = client.get(f"/evento/{evento_id}/questionario", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["evento_id"] == evento_id
    assert payload["paginas"] == []


def test_questionario_get_retorna_ordenado(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

        pagina_b = QuestionarioPagina(evento_id=evento_id, ordem=2, titulo="Pagina 2", descricao=None)
        pagina_a = QuestionarioPagina(evento_id=evento_id, ordem=1, titulo="Pagina 1", descricao=None)
        session.add(pagina_b)
        session.add(pagina_a)
        session.commit()
        session.refresh(pagina_b)
        session.refresh(pagina_a)

        pergunta_b = QuestionarioPergunta(
            pagina_id=pagina_a.id,
            ordem=2,
            tipo=TipoPergunta.ABERTA_TEXTO_SIMPLES,
            texto="Pergunta 2",
            obrigatoria=False,
        )
        pergunta_a = QuestionarioPergunta(
            pagina_id=pagina_a.id,
            ordem=1,
            tipo=TipoPergunta.ABERTA_TEXTO_SIMPLES,
            texto="Pergunta 1",
            obrigatoria=False,
        )
        session.add(pergunta_b)
        session.add(pergunta_a)
        session.commit()
        session.refresh(pergunta_b)
        session.refresh(pergunta_a)

        opcao_b = QuestionarioOpcao(pergunta_id=pergunta_a.id, ordem=2, texto="Opcao 2")
        opcao_a = QuestionarioOpcao(pergunta_id=pergunta_a.id, ordem=1, texto="Opcao 1")
        session.add(opcao_b)
        session.add(opcao_a)
        session.commit()

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp = client.get(f"/evento/{evento_id}/questionario", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    payload = resp.json()
    assert [pagina["ordem"] for pagina in payload["paginas"]] == [1, 2]
    assert payload["paginas"][0]["perguntas"][0]["ordem"] == 1
    assert payload["paginas"][0]["perguntas"][1]["ordem"] == 2
    assert [opcao["ordem"] for opcao in payload["paginas"][0]["perguntas"][0]["opcoes"]] == [1, 2]


def test_questionario_put_salva_minimo(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    payload = {
        "paginas": [
            {
                "ordem": 1,
                "titulo": "Pagina 1",
                "descricao": None,
                "perguntas": [
                    {
                        "ordem": 1,
                        "tipo": "aberta_texto_simples",
                        "texto": "Pergunta 1",
                        "obrigatoria": False,
                        "opcoes": [],
                    }
                ],
            }
        ]
    }

    resp = client.put(
        f"/evento/{evento_id}/questionario",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    saved = resp.json()
    assert saved["evento_id"] == evento_id
    assert len(saved["paginas"]) == 1
    assert len(saved["paginas"][0]["perguntas"]) == 1


def test_questionario_put_objetiva_sem_opcoes_retorna_erro(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    payload = {
        "paginas": [
            {
                "ordem": 1,
                "titulo": "Pagina 1",
                "descricao": None,
                "perguntas": [
                    {
                        "ordem": 1,
                        "tipo": "objetiva_unica",
                        "texto": "Pergunta 1",
                        "obrigatoria": False,
                        "opcoes": [],
                    }
                ],
            }
        ]
    }

    resp = client.put(
        f"/evento/{evento_id}/questionario",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "QUESTIONARIO_INVALID_STRUCTURE"


def test_questionario_put_get_roundtrip(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    payload = {
        "paginas": [
            {
                "ordem": 1,
                "titulo": "Pagina 1",
                "descricao": "Descricao",
                "perguntas": [
                    {
                        "ordem": 1,
                        "tipo": "aberta_texto_simples",
                        "texto": "Pergunta 1",
                        "obrigatoria": True,
                        "opcoes": [],
                    },
                    {
                        "ordem": 2,
                        "tipo": "objetiva_unica",
                        "texto": "Pergunta 2",
                        "obrigatoria": False,
                        "opcoes": [
                            {"ordem": 1, "texto": "Opcao 1"},
                            {"ordem": 2, "texto": "Opcao 2"},
                        ],
                    },
                ],
            }
        ]
    }

    resp_put = client.put(
        f"/evento/{evento_id}/questionario",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_put.status_code == 200

    resp_get = client.get(
        f"/evento/{evento_id}/questionario",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_get.status_code == 200
    data = resp_get.json()
    assert data["evento_id"] == evento_id
    assert len(data["paginas"]) == 1
    assert len(data["paginas"][0]["perguntas"]) == 2
    assert data["paginas"][0]["perguntas"][1]["opcoes"][0]["texto"] == "Opcao 1"


def test_questionario_aplica_visibilidade_agencia(client, engine):
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

    resp_get = client.get(f"/evento/{evento_id}/questionario", headers={"Authorization": f"Bearer {token}"})
    assert resp_get.status_code == 404
    assert resp_get.json()["detail"]["code"] == "EVENTO_NOT_FOUND"

    resp_put = client.put(
        f"/evento/{evento_id}/questionario",
        json={"paginas": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_put.status_code == 404
    assert resp_put.json()["detail"]["code"] == "EVENTO_NOT_FOUND"
