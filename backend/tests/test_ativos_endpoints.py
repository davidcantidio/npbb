import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import (
    CotaCortesia,
    Diretoria,
    Evento,
    SolicitacaoIngresso,
    SolicitacaoIngressoStatus,
    SolicitacaoIngressoTipo,
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
    with Session(engine) as session:
        exists = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
        if not exists:
            session.add(StatusEvento(nome="Previsto"))
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


def seed_diretoria(session: Session, nome: str = "dimac") -> Diretoria:
    diretoria = Diretoria(nome=nome)
    session.add(diretoria)
    session.commit()
    session.refresh(diretoria)
    return diretoria


def seed_user(session: Session, email: str, password: str) -> Usuario:
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


def seed_evento(session: Session, diretoria_id: int) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    assert status and status.id
    evento = Evento(
        nome="Evento Teste",
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        status_id=status.id,
        diretoria_id=diretoria_id,
        data_inicio_prevista=date(2026, 1, 1),
        data_fim_prevista=date(2026, 1, 2),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_lista_ativos_com_usados(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session)
        user = seed_user(session, email="user@npbb.com", password="Senha123!")
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=10,
        )
        session.add(cota)
        session.commit()
        session.refresh(cota)
        session.add(
            SolicitacaoIngresso(
                cota_id=int(cota.id),
                evento_id=int(evento.id),
                diretoria_id=int(diretoria.id),
                solicitante_usuario_id=int(user.id),
                solicitante_email=user.email,
                tipo=SolicitacaoIngressoTipo.SELF,
                indicado_email=user.email,
                status=SolicitacaoIngressoStatus.SOLICITADO,
            )
        )
        session.commit()

        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.get("/ativos", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Total-Count") == "1"
    payload = resp.json()
    assert len(payload) == 1
    item = payload[0]
    assert item["total"] == 10
    assert item["usados"] == 1
    assert item["disponiveis"] == 9
    assert abs(item["percentual_usado"] - 0.1) < 0.0001


def test_atribuir_bloqueia_quando_abaixo_dos_usados(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="dir2")
        user = seed_user(session, email="user2@npbb.com", password="Senha123!")
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=5,
        )
        session.add(cota)
        session.commit()
        session.refresh(cota)
        session.add(
            SolicitacaoIngresso(
                cota_id=int(cota.id),
                evento_id=int(evento.id),
                diretoria_id=int(diretoria.id),
                solicitante_usuario_id=int(user.id),
                solicitante_email=user.email,
                tipo=SolicitacaoIngressoTipo.SELF,
                indicado_email=user.email,
                status=SolicitacaoIngressoStatus.SOLICITADO,
            )
        )
        session.commit()

        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.post(
        f"/ativos/{evento_id}/{diretoria_id}/atribuir",
        json={"quantidade": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409
    detail = resp.json().get("detail", {})
    assert detail.get("code") == "COTA_BELOW_USED"


def test_excluir_cota_quando_sem_usados(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="dir3")
        user = seed_user(session, email="user3@npbb.com", password="Senha123!")
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=1,
        )
        session.add(cota)
        session.commit()
        session.refresh(cota)
        cota_id = int(cota.id)
        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.delete(
        f"/ativos/{cota_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
