from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import (
    Agencia,
    Ativacao,
    Cupom,
    Evento,
    Gamificacao,
    StatusEvento,
    TipoEvento,
    Usuario,
)
from app.schemas.ativacao import AtivacaoCreate, AtivacaoUpdate
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


def seed_user(
    session: Session, email: str, password: str, tipo: str, agencia_id: int | None = None
) -> Usuario:
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


def seed_gamificacao(session: Session, *, evento_id: int, nome: str = "G1") -> Gamificacao:
    gamificacao = Gamificacao(
        evento_id=evento_id,
        nome=nome,
        descricao="Descricao",
        premio="Premio",
        titulo_feedback="Titulo",
        texto_feedback="Texto",
    )
    session.add(gamificacao)
    session.commit()
    session.refresh(gamificacao)
    return gamificacao


def seed_ativacao(
    session: Session,
    *,
    evento_id: int,
    nome: str = "Ativacao",
    descricao: str | None = None,
    gamificacao_id: int | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> Ativacao:
    base_dt = datetime.now(timezone.utc)
    ativacao = Ativacao(
        evento_id=evento_id,
        nome=nome,
        descricao=descricao,
        gamificacao_id=gamificacao_id,
        valor=Decimal("0.00"),
        created_at=created_at or base_dt,
        updated_at=updated_at or created_at or base_dt,
    )
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)
    return ativacao


def seed_cupom(session: Session, *, ativacao_id: int, codigo: str = "CUPOM1") -> Cupom:
    cupom = Cupom(
        ativacao_id=ativacao_id,
        codigo=codigo,
    )
    session.add(cupom)
    session.commit()
    session.refresh(cupom)
    return cupom


def test_ativacao_create_schema_aceita_conversao_unica_e_normaliza_nome():
    payload = AtivacaoCreate.model_validate(
        {
            "nome": "  Ativacao QR  ",
            "descricao": "  Mensagem  ",
            "conversao_unica": False,
        }
    )

    assert payload.nome == "Ativacao QR"
    assert payload.descricao == "Mensagem"
    assert payload.conversao_unica is False
    assert payload.checkin_unico is False


def test_ativacao_update_schema_rejeita_aliases_divergentes():
    with pytest.raises(ValidationError):
        AtivacaoUpdate.model_validate({"conversao_unica": True, "checkin_unico": False})


def test_eventos_ativacoes_get_retorna_lista_vazia(client, engine):
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
    resp = client.get(
        f"/eventos/{evento_id}/ativacoes", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json() == []


def test_eventos_ativacoes_post_cria_lista_e_get_by_id(client, engine):
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
        gamificacao = seed_gamificacao(session, evento_id=evento_id)
        gamificacao_id = gamificacao.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_create = client.post(
        f"/eventos/{evento_id}/ativacoes",
        json={
            "nome": "Ativacao 1",
            "descricao": "Mensagem",
            "conversao_unica": False,
            "mensagem_qrcode": "QR Code",
            "gamificacao_id": gamificacao_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_create.status_code == 201
    created = resp_create.json()
    assert created["evento_id"] == evento_id
    assert created["nome"] == "Ativacao 1"
    assert created["descricao"] == "Mensagem"
    assert created["mensagem_qrcode"] == "QR Code"
    assert created["gamificacao_id"] == gamificacao_id
    assert created["conversao_unica"] is False
    assert created["checkin_unico"] is False
    assert created["redireciona_pesquisa"] is False
    assert created["termo_uso"] is False
    assert created["gera_cupom"] is False

    resp_list = client.get(
        f"/eventos/{evento_id}/ativacoes", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_list.status_code == 200
    payload = resp_list.json()
    assert len(payload) == 1
    assert payload[0]["id"] == created["id"]
    assert payload[0]["conversao_unica"] is False

    resp_get_by_id = client.get(
        f"/eventos/{evento_id}/ativacoes/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_get_by_id.status_code == 200
    by_id_payload = resp_get_by_id.json()
    assert by_id_payload["id"] == created["id"]
    assert by_id_payload["evento_id"] == evento_id
    assert by_id_payload["nome"] == "Ativacao 1"
    assert by_id_payload["conversao_unica"] is False


def test_eventos_ativacoes_patch_atualiza_campos(client, engine):
    old_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)

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
        ativacao = seed_ativacao(
            session, evento_id=evento_id, nome="Ativacao", created_at=old_dt, updated_at=old_dt
        )
        ativacao_id = ativacao.id
        gamificacao = seed_gamificacao(session, evento_id=evento_id, nome="G2")
        gamificacao_id = gamificacao.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_update = client.patch(
        f"/eventos/{evento_id}/ativacoes/{ativacao_id}",
        json={
            "nome": "Ativacao Editada",
            "descricao": "Nova mensagem",
            "conversao_unica": True,
            "mensagem_qrcode": "Novo QR",
            "gamificacao_id": gamificacao_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["id"] == ativacao_id
    assert updated["evento_id"] == evento_id
    assert updated["nome"] == "Ativacao Editada"
    assert updated["descricao"] == "Nova mensagem"
    assert updated["mensagem_qrcode"] == "Novo QR"
    assert updated["gamificacao_id"] == gamificacao_id
    assert updated["conversao_unica"] is True
    assert updated["checkin_unico"] is True

    updated_at = datetime.fromisoformat(updated["updated_at"])
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    assert updated_at > old_dt


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/eventos/1/ativacoes"),
        ("post", "/eventos/1/ativacoes"),
        ("get", "/eventos/1/ativacoes/1"),
        ("patch", "/eventos/1/ativacoes/1"),
    ],
)
def test_eventos_ativacoes_sem_token_retorna_401(client, method, path):
    payload = {"nome": "Ativacao sem token", "conversao_unica": True}
    kwargs = {"json": payload} if method in {"post", "patch"} else {}
    response = getattr(client, method)(path, **kwargs)

    assert response.status_code == 401


def test_eventos_ativacoes_post_retorna_404_quando_evento_nao_existe(client, engine):
    with Session(engine) as session:
        seed_user(session, "user@example.com", "Senha123!", "npbb")

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    response = client.post(
        "/eventos/9999/ativacoes",
        json={"nome": "Ativacao", "conversao_unica": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "EVENTO_NOT_FOUND"


def test_ativacao_delete_remove(client, engine):
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
        ativacao = seed_ativacao(session, evento_id=evento_id, nome="Ativacao")
        ativacao_id = ativacao.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_delete = client.delete(
        f"/ativacao/{ativacao_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_delete.status_code == 204

    resp_list = client.get(
        f"/eventos/{evento_id}/ativacoes", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_list.status_code == 200
    assert resp_list.json() == []


def test_ativacao_delete_bloqueado_quando_existe_dependencia(client, engine):
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
        ativacao = seed_ativacao(session, evento_id=evento.id, nome="Ativacao")
        ativacao_id = ativacao.id
        seed_cupom(session, ativacao_id=ativacao_id, codigo="CUPOM-1")

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.delete(f"/ativacao/{ativacao_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert detail["code"] == "ATIVACAO_DELETE_BLOCKED"
    assert "cupons" in detail["dependencies"]


def test_ativacoes_aplica_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)

        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag1.id)
        evento_out = seed_evento(
            session,
            agencia_id=ag2.id,
            tipo_id=tipo.id,
            nome="Evento Outro",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_out_id = evento_out.id
        ativacao_out = seed_ativacao(session, evento_id=evento_out_id, nome="Ativacao")
        ativacao_out_id = ativacao_out.id

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")

    resp_list = client.get(
        f"/eventos/{evento_out_id}/ativacoes", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_list.status_code == 404
    assert resp_list.json()["detail"]["code"] == "EVENTO_NOT_FOUND"

    resp_update = client.patch(
        f"/eventos/{evento_out_id}/ativacoes/{ativacao_out_id}",
        json={"nome": "Nao pode"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 404
    assert resp_update.json()["detail"]["code"] == "EVENTO_NOT_FOUND"
