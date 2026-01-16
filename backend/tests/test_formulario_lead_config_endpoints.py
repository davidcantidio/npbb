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
    FormularioLandingTemplate,
    FormularioLeadConfig,
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


def test_form_config_get_retorna_default_quando_nao_existe(client, engine):
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
    resp = client.get(f"/evento/{evento_id}/form-config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["evento_id"] == evento_id
    assert payload["template_id"] is None
    assert payload["campos"] == [
        {"nome_campo": "CPF", "obrigatorio": True, "ordem": 0},
        {"nome_campo": "Nome", "obrigatorio": True, "ordem": 1},
        {"nome_campo": "Sobrenome", "obrigatorio": False, "ordem": 2},
        {"nome_campo": "Email", "obrigatorio": True, "ordem": 4},
        {"nome_campo": "Data de nascimento", "obrigatorio": True, "ordem": 5},
    ]
    assert payload["urls"]["url_landing"] == f"http://testserver/landing/eventos/{evento_id}"
    assert payload["urls"]["url_checkin_sem_qr"] == f"http://testserver/checkin-sem-qr/eventos/{evento_id}"
    assert payload["urls"]["url_questionario"] == f"http://testserver/questionario/eventos/{evento_id}"
    assert payload["urls"]["url_api"] == "http://testserver/docs"
    assert "url_landing" not in payload


def test_form_config_get_respeita_public_api_doc_url(client, engine, monkeypatch):
    monkeypatch.setenv("PUBLIC_API_DOC_URL", "https://docs.example.com")
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
    resp = client.get(f"/evento/{evento_id}/form-config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["urls"]["url_api"] == "https://docs.example.com"


def test_form_config_put_cria_config(client, engine):
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

        template = FormularioLandingTemplate(nome="Padrao", html_conteudo="<html></html>")
        session.add(template)
        session.commit()
        session.refresh(template)
        template_id = template.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": template_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["template_id"] == template_id

    with Session(engine) as session:
        configs = session.exec(select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)).all()
        assert len(configs) == 1


def test_form_config_put_atualiza_template_id(client, engine):
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

        template_a = FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>")
        template_b = FormularioLandingTemplate(nome="Padrao", html_conteudo="<html></html>")
        session.add(template_a)
        session.add(template_b)
        session.commit()
        session.refresh(template_a)
        session.refresh(template_b)
        template_a_id = template_a.id
        template_b_id = template_b.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_create = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": template_a_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_create.status_code == 200
    assert resp_create.json()["template_id"] == template_a_id

    resp_update = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": template_b_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["template_id"] == template_b_id

    with Session(engine) as session:
        configs = session.exec(select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)).all()
        assert len(configs) == 1
        assert configs[0].template_id == template_b_id


def test_form_config_put_omitir_template_id_mantem_template(client, engine):
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

        template = FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>")
        session.add(template)
        session.commit()
        session.refresh(template)
        template_id = template.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    payload_inicial = {
        "template_id": template_id,
        "campos": [{"nome_campo": "Nome", "obrigatorio": True, "ordem": 0}],
    }
    resp_create = client.put(f"/evento/{evento_id}/form-config", json=payload_inicial, headers=headers)
    assert resp_create.status_code == 200
    assert resp_create.json()["template_id"] == template_id

    payload_campos = {
        "campos": [
            {"nome_campo": "Nome", "obrigatorio": True, "ordem": 0},
            {"nome_campo": "Email", "obrigatorio": True, "ordem": 1},
        ]
    }
    resp_update = client.put(f"/evento/{evento_id}/form-config", json=payload_campos, headers=headers)
    assert resp_update.status_code == 200
    assert resp_update.json()["template_id"] == template_id
    assert resp_update.json()["campos"] == payload_campos["campos"]


def test_form_config_put_salva_campos_e_get_retorna_igual(client, engine):
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

        template = FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>")
        session.add(template)
        session.commit()
        session.refresh(template)
        template_id = template.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    payload = {
        "template_id": template_id,
        "campos": [
            {"nome_campo": "Nome", "obrigatorio": True, "ordem": 0},
            {"nome_campo": "Email", "obrigatorio": True, "ordem": 1},
        ],
    }
    resp = client.put(
        f"/evento/{evento_id}/form-config",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    get_resp = client.get(f"/evento/{evento_id}/form-config", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    assert get_resp.json()["template_id"] == template_id
    assert get_resp.json()["campos"] == payload["campos"]


def test_form_config_permissoes_usuario_agencia_so_acessa_eventos_da_agencia(client, engine):
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

        template = FormularioLandingTemplate(nome="Padrao", html_conteudo="<html></html>")
        session.add(template)
        session.commit()
        session.refresh(template)
        template_id = template.id

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    resp_get = client.get(f"/evento/{evento_id}/form-config", headers=headers)
    assert resp_get.status_code == 404

    resp_put = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": template_id},
        headers=headers,
    )
    assert resp_put.status_code == 404
