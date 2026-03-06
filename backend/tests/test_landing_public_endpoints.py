from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import (
    Agencia,
    Ativacao,
    AtivacaoLead,
    Evento,
    Lead,
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
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "http://testserver")
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


def seed_agencia(session: Session, nome: str = "V3A") -> Agencia:
    agencia = Agencia(nome=nome, dominio=f"{nome.lower()}.com.br", lote=1)
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


def seed_evento(
    session: Session,
    *,
    agencia_id: int,
    tipo_id: int,
    nome: str,
    template_override: str | None = None,
    cta_personalizado: str | None = None,
    hero_image_url: str | None = None,
    descricao_curta: str | None = None,
) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    assert status and status.id
    evento = Evento(
        nome=nome,
        descricao="Descricao longa do evento.",
        descricao_curta=descricao_curta,
        template_override=template_override,
        cta_personalizado=cta_personalizado,
        hero_image_url=hero_image_url,
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        agencia_id=agencia_id,
        tipo_id=tipo_id,
        status_id=status.id,
        data_inicio_prevista=date(2026, 4, 10),
        data_fim_prevista=date(2026, 4, 12),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def seed_ativacao(session: Session, *, evento_id: int, nome: str = "Captacao Principal") -> Ativacao:
    ativacao = Ativacao(
        evento_id=evento_id,
        nome=nome,
        descricao="Ponto de captacao no evento.",
        valor=0,
    )
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)
    return ativacao


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_public_landing_por_ativacao_retorna_payload_resolvido(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session)
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="BB Summit 2026",
            template_override="corporativo",
            cta_personalizado="Fazer inscricao",
            hero_image_url="https://example.com/hero-corp.webp",
            descricao_curta="Conteudo executivo e networking com o BB.",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ativacao_id"] == ativacao_id
    assert payload["evento"]["nome"] == "BB Summit 2026"
    assert payload["evento"]["descricao_curta"] == "Conteudo executivo e networking com o BB."
    assert payload["template"]["categoria"] == "corporativo"
    assert payload["template"]["cta_text"] == "Fazer inscricao"
    assert payload["marca"]["url_hero_image"] == "https://example.com/hero-corp.webp"
    assert payload["formulario"]["event_id"] == payload["evento"]["id"]
    assert payload["formulario"]["ativacao_id"] == ativacao_id
    assert payload["formulario"]["campos_obrigatorios"] == ["nome", "email"]
    assert payload["acesso"]["landing_url"] == f"http://testserver/landing/ativacoes/{ativacao_id}"
    assert payload["acesso"]["url_promotor"] == f"http://testserver/landing/ativacoes/{ativacao_id}"
    assert payload["acesso"]["qr_code_url"].startswith("data:image/svg+xml;base64,")


def test_public_landing_submit_cria_lead_e_vinculo_com_ativacao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        evento_id = evento.id
        ativacao_id = ativacao.id

    resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "123.456.789-01",
            "telefone": "(61) 99999-0000",
            "consentimento_lgpd": True,
        },
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["event_id"] == evento_id
    assert payload["ativacao_id"] == ativacao_id
    assert payload["lead_id"] > 0

    with Session(engine) as session:
        lead = session.get(Lead, payload["lead_id"])
        assert lead is not None
        assert lead.email == "maria@example.com"
        assert lead.cpf == "12345678901"
        link = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == ativacao_id)
            .where(AtivacaoLead.lead_id == payload["lead_id"])
        ).first()
        assert link is not None


def test_public_template_config_e_qr_code_endpoint(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Corporativo")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Forum de Lideranca BB",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        evento_id = evento.id
        ativacao_id = ativacao.id

    template_resp = client.get(f"/eventos/{evento_id}/template-config")
    assert template_resp.status_code == 200
    assert template_resp.json()["categoria"] == "corporativo"

    qr_resp = client.get(f"/ativacoes/{ativacao_id}/qr-code")
    assert qr_resp.status_code == 200
    assert qr_resp.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in qr_resp.text


def test_evento_create_update_e_get_expoem_campos_da_fase_1(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        seed_user(session, "user@example.com", "[REDACTED]")
        agencia_id = agencia.id
        tipo_id = tipo.id

    token = login_and_get_token(client, "user@example.com", "[REDACTED]")
    create_resp = client.post(
        "/evento",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Demo Day BB",
            "descricao": "Descricao principal",
            "descricao_curta": "Resumo curto",
            "template_override": "tecnologia",
            "hero_image_url": "https://example.com/hero-tech.webp",
            "cta_personalizado": "Quero participar",
            "cidade": "Brasilia",
            "estado": "DF",
            "agencia_id": agencia_id,
            "tipo_id": tipo_id,
            "data_inicio_prevista": "2026-05-10",
            "data_fim_prevista": "2026-05-11",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["template_override"] == "tecnologia"
    assert created["hero_image_url"] == "https://example.com/hero-tech.webp"
    assert created["cta_personalizado"] == "Quero participar"
    assert created["descricao_curta"] == "Resumo curto"

    evento_id = created["id"]
    update_resp = client.put(
        f"/evento/{evento_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_override": "corporativo",
            "cta_personalizado": "Confirmar presenca",
            "descricao_curta": "Resumo revisado",
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["template_override"] == "corporativo"
    assert updated["cta_personalizado"] == "Confirmar presenca"
    assert updated["descricao_curta"] == "Resumo revisado"

    get_resp = client.get(f"/evento/{evento_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["template_override"] == "corporativo"
    assert fetched["hero_image_url"] == "https://example.com/hero-tech.webp"
    assert fetched["descricao_curta"] == "Resumo revisado"
