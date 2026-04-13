import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from app.db.database import get_session
from app.main import app
from app.models.models import (
    CotaCortesia,
    Diretoria,
    Evento,
    Funcionario,
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


def seed_user_with_diretoria(
    session: Session,
    email: str,
    password: str,
    diretoria_id: int,
    matricula: str | None = None,
    status_aprovacao: str | None = "APROVADO",
) -> Usuario:
    matricula_value = matricula or f"c{abs(hash(email)) % 100000}"
    funcionario = Funcionario(
        nome="Funcionario",
        chave_c=matricula_value,
        diretoria_id=diretoria_id,
        email=email,
    )
    session.add(funcionario)
    session.commit()
    session.refresh(funcionario)

    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario="bb",
        funcionario_id=int(funcionario.id),
        matricula=matricula_value,
        status_aprovacao=status_aprovacao,
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


def test_ingressos_bb_nao_aprovado_bloqueia(client, engine):
    """BB com status explicitamente nao-APROVADO continua bloqueado (ex.: legado REJEITADO)."""
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="pendente")
        user = seed_user_with_diretoria(
            session,
            email="pendente@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
            status_aprovacao="REJEITADO",
        )
        token = login_and_get_token(client, user.email, "Senha123!")

    resp = client.get(
        "/ingressos/ativos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    detail = resp.json().get("detail", {})
    assert detail.get("code") == "USER_NOT_APPROVED"


def test_solicitacao_disponibilidade_bloqueia(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session)
        user = seed_user_with_diretoria(
            session,
            email="user@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
        )
        user_email = user.email
        ocupante = seed_user_with_diretoria(
            session,
            email="ocupante@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
        )
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
        session.add(
            SolicitacaoIngresso(
                cota_id=int(cota.id),
                evento_id=int(evento.id),
                diretoria_id=int(diretoria.id),
                solicitante_usuario_id=int(ocupante.id),
                solicitante_email=ocupante.email,
                tipo=SolicitacaoIngressoTipo.SELF,
                indicado_email=ocupante.email,
                status=SolicitacaoIngressoStatus.SOLICITADO,
            )
        )
        session.commit()

        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.post(
        "/ingressos/solicitacoes",
        json={"cota_id": cota_id, "tipo": "SELF"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409
    detail = resp.json().get("detail", {})
    assert detail.get("code") == "COTA_EMPTY"


def test_solicitacao_duplicidade_bloqueia(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="dir2")
        user = seed_user_with_diretoria(
            session,
            email="user2@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
        )
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=2,
        )
        session.add(cota)
        session.commit()
        session.refresh(cota)
        cota_id = int(cota.id)

        token = login_and_get_token(client, user_email, "Senha123!")

    resp1 = client.post(
        "/ingressos/solicitacoes",
        json={"cota_id": cota_id, "tipo": "SELF"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        "/ingressos/solicitacoes",
        json={"cota_id": cota_id, "tipo": "SELF"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 409
    detail = resp2.json().get("detail", {})
    assert detail.get("code") == "DUPLICATE_REQUEST"


def test_solicitacao_self_ok(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="dir_self")
        user = seed_user_with_diretoria(
            session,
            email="self@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
        )
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=3,
        )
        session.add(cota)
        session.commit()
        session.refresh(cota)
        cota_id = int(cota.id)
        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.post(
        "/ingressos/solicitacoes",
        json={"cota_id": cota_id, "tipo": "SELF"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["cota_id"] == cota_id
    assert payload["status"] == "SOLICITADO"
    assert payload["solicitante_email"] == "self@bb.com.br"
    assert payload["indicado_email"] == "self@bb.com.br"


def test_solicitacao_terceiro_ok(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="dir_terc")
        user = seed_user_with_diretoria(
            session,
            email="terc@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
        )
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=3,
        )
        session.add(cota)
        session.commit()
        session.refresh(cota)
        cota_id = int(cota.id)
        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.post(
        "/ingressos/solicitacoes",
        json={"cota_id": cota_id, "tipo": "TERCEIRO", "indicado_email": "alvo@bb.com.br"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["cota_id"] == cota_id
    assert payload["status"] == "SOLICITADO"
    assert payload["solicitante_email"] == "terc@bb.com.br"
    assert payload["indicado_email"] == "alvo@bb.com.br"


def test_ingressos_ativos_ignora_cancelado(client, engine):
    with Session(engine) as session:
        diretoria = seed_diretoria(session, nome="dir3")
        user = seed_user_with_diretoria(
            session,
            email="user3@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
        )
        user_email = user.email
        evento = seed_evento(session, diretoria_id=int(diretoria.id))
        cota = CotaCortesia(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            quantidade=2,
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
                status=SolicitacaoIngressoStatus.CANCELADO,
            )
        )
        session.commit()

        token = login_and_get_token(client, user_email, "Senha123!")

    resp = client.get(
        "/ingressos/ativos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data
    assert data[0]["usados"] == 0
