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
    ConversaoAtivacao,
    Evento,
    Lead,
    StatusEvento,
    TipoEvento,
)


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


def seed_evento(
    session: Session,
    *,
    agencia_id: int,
    tipo_id: int,
    nome: str,
) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    assert status and status.id
    evento = Evento(
        nome=nome,
        descricao="Descricao longa do evento.",
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


def seed_ativacao(
    session: Session,
    *,
    evento_id: int,
    nome: str = "Captacao Principal",
    checkin_unico: bool = False,
) -> Ativacao:
    ativacao = Ativacao(
        evento_id=evento_id,
        nome=nome,
        descricao="Ponto de captacao no evento.",
        checkin_unico=checkin_unico,
        valor=0,
    )
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)
    return ativacao


def test_post_leads_com_ativacao_registra_conversao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB")
        ativacao = seed_ativacao(session, evento_id=evento.id)
        event_id = evento.id
        ativacao_id = ativacao.id

    resp = client.post(
        "/leads",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "ativacao_id": ativacao_id,
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["ativacao_id"] == ativacao_id
    assert payload["event_id"] == event_id
    assert payload["conversao_registrada"] is True
    assert payload["bloqueado_cpf_duplicado"] is False
    assert isinstance(payload["ativacao_lead_id"], int)

    with Session(engine) as session:
        lead = session.get(Lead, payload["lead_id"])
        assert lead is not None
        assert lead.cpf == "52998224725"
        ativacao_lead = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == ativacao_id)
            .where(AtivacaoLead.lead_id == lead.id)
        ).first()
        assert ativacao_lead is not None
        conversoes = session.exec(
            select(ConversaoAtivacao)
            .where(ConversaoAtivacao.ativacao_id == ativacao_id)
            .where(ConversaoAtivacao.lead_id == lead.id)
        ).all()
        assert len(conversoes) == 1
        assert conversoes[0].cpf == "52998224725"


def test_post_leads_com_ativacao_unica_bloqueia_cpf_duplicado(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB Unique")
        ativacao = seed_ativacao(session, evento_id=evento.id, checkin_unico=True)
        ativacao_id = ativacao.id

    body = {
        "nome": "Maria",
        "email": "maria@example.com",
        "cpf": "529.982.247-25",
        "ativacao_id": ativacao_id,
        "consentimento_lgpd": True,
    }

    resp1 = client.post("/leads", json=body)
    resp2 = client.post("/leads", json=body)

    assert resp1.status_code == 201
    assert resp1.json()["conversao_registrada"] is True
    assert resp1.json()["bloqueado_cpf_duplicado"] is False

    assert resp2.status_code == 201
    payload = resp2.json()
    assert payload["conversao_registrada"] is False
    assert payload["bloqueado_cpf_duplicado"] is True
    assert payload["lead_id"] == resp1.json()["lead_id"]
    assert payload["ativacao_lead_id"] == resp1.json()["ativacao_lead_id"]

    with Session(engine) as session:
        conversoes = session.exec(
            select(ConversaoAtivacao).where(ConversaoAtivacao.ativacao_id == ativacao_id)
        ).all()
        assert len(conversoes) == 1


def test_post_leads_retorna_404_para_ativacao_inexistente(client):
    resp = client.post(
        "/leads",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "ativacao_id": 999999,
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "ATIVACAO_NOT_FOUND"


@pytest.mark.parametrize(
    ("cpf", "expected_code"),
    [
        (None, "CPF_REQUIRED"),
        ("529.982.247-26", "CPF_INVALID"),
    ],
)
def test_post_leads_com_ativacao_exige_cpf_valido(client, engine, cpf, expected_code):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB")
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    body = {
        "nome": "Maria",
        "email": "maria@example.com",
        "ativacao_id": ativacao_id,
        "consentimento_lgpd": True,
    }
    if cpf is not None:
        body["cpf"] = cpf

    resp = client.post("/leads", json=body)

    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == expected_code


def test_post_leads_reaproveita_lead_existente_sem_duplicar_vinculo(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB")
        ativacao = seed_ativacao(session, evento_id=evento.id, checkin_unico=False)
        lead = Lead(
            nome="Maria",
            email="maria@example.com",
            evento_nome=evento.nome,
            cidade=evento.cidade,
            estado=evento.estado,
            fonte_origem="landing_publica",
            opt_in="aceito",
            opt_in_flag=True,
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        original_lead_id = lead.id
        ativacao_id = ativacao.id

    body = {
        "nome": "Maria",
        "email": "maria@example.com",
        "cpf": "529.982.247-25",
        "ativacao_id": ativacao_id,
        "consentimento_lgpd": True,
    }

    resp1 = client.post("/leads", json=body)
    resp2 = client.post("/leads", json=body)

    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["lead_id"] == original_lead_id
    assert resp2.json()["lead_id"] == original_lead_id
    assert resp1.json()["ativacao_lead_id"] == resp2.json()["ativacao_lead_id"]
    assert resp1.json()["bloqueado_cpf_duplicado"] is False
    assert resp2.json()["bloqueado_cpf_duplicado"] is False
    assert resp1.json()["conversao_registrada"] is True
    assert resp2.json()["conversao_registrada"] is True

    with Session(engine) as session:
        links = session.exec(
            select(AtivacaoLead).where(AtivacaoLead.ativacao_id == ativacao_id)
        ).all()
        assert len(links) == 1
        conversoes = session.exec(
            select(ConversaoAtivacao).where(ConversaoAtivacao.ativacao_id == ativacao_id)
        ).all()
        assert len(conversoes) == 2
        assert all(conversao.lead_id == original_lead_id for conversao in conversoes)


def test_post_leads_nao_reaproveita_mesmo_email_quando_cpf_conflita(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB")
        ativacao = seed_ativacao(session, evento_id=evento.id)
        lead = Lead(
            nome="Maria",
            email="maria@example.com",
            cpf="11144477735",
            evento_nome=evento.nome,
            cidade=evento.cidade,
            estado=evento.estado,
            fonte_origem="landing_publica",
            opt_in="aceito",
            opt_in_flag=True,
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        original_lead_id = lead.id
        ativacao_id = ativacao.id

    resp = client.post(
        "/leads",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "ativacao_id": ativacao_id,
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["lead_id"] != original_lead_id
    assert payload["conversao_registrada"] is True

    with Session(engine) as session:
        original = session.get(Lead, original_lead_id)
        assert original is not None
        assert original.cpf == "11144477735"

        new_lead = session.get(Lead, payload["lead_id"])
        assert new_lead is not None
        assert new_lead.cpf == "52998224725"

        conversao = session.exec(
            select(ConversaoAtivacao)
            .where(ConversaoAtivacao.ativacao_id == ativacao_id)
            .where(ConversaoAtivacao.lead_id == payload["lead_id"])
        ).first()
        assert conversao is not None
        assert conversao.cpf == "52998224725"


def test_post_leads_sem_ativacao_exige_event_id_e_nao_registra_conversao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Corporativo")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Forum BB")
        event_id = evento.id

    resp = client.post(
        "/leads",
        json={
            "nome": "Joao",
            "email": "joao@example.com",
            "event_id": event_id,
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["event_id"] == event_id
    assert payload["ativacao_id"] is None
    assert payload["conversao_registrada"] is False

    with Session(engine) as session:
        conversoes = session.exec(select(ConversaoAtivacao)).all()
        assert conversoes == []


def test_post_leads_retorna_400_quando_event_id_diverge_da_ativacao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento_a = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Evento A")
        evento_b = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Evento B")
        ativacao = seed_ativacao(session, evento_id=evento_a.id)
        evento_b_id = evento_b.id
        ativacao_id = ativacao.id

    resp = client.post(
        "/leads",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "event_id": evento_b_id,
            "ativacao_id": ativacao_id,
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "EVENTO_ATIVACAO_MISMATCH"
