from datetime import date, datetime, timedelta, timezone

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
    Gamificacao,
    LandingAnalyticsEvent,
    Lead,
    LeadReconhecimentoToken,
    StatusEvento,
    TipoEvento,
    Usuario,
)
from app.services.reconhecimento import gerar_token
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


def seed_lead(session: Session, *, evento: Evento) -> Lead:
    lead = Lead(
        nome="Maria",
        email="maria@example.com",
        cpf="52998224725",
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
    return lead


def seed_conversao_ativacao(
    session: Session,
    *,
    ativacao_id: int,
    lead_id: int,
    cpf: str = "52998224725",
) -> ConversaoAtivacao:
    conversao = ConversaoAtivacao(
        ativacao_id=ativacao_id,
        lead_id=lead_id,
        cpf=cpf,
    )
    session.add(conversao)
    session.commit()
    session.refresh(conversao)
    return conversao


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_public_landing_por_ativacao_retorna_payload_resolvido_form_only(client, engine):
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
            descricao_curta="Conteudo executivo e networking com o BB.",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ativacao_id"] == ativacao_id
    assert payload["evento"]["nome"] == "BB Summit 2026"
    assert payload["evento"]["cta_personalizado"] == "Fazer inscricao"
    assert payload["evento"]["descricao_curta"] == "Conteudo executivo e networking com o BB."
    assert payload["template"]["categoria"] == "corporativo"
    assert payload["template"]["cta_text"] == "Fazer inscricao"
    assert payload["marca"] == {"tagline": "Banco do Brasil. Pra tudo que voce imaginar."}
    assert "url_hero_image" not in payload["marca"]
    assert "hero_alt" not in payload["marca"]
    assert "versao_logo" not in payload["marca"]
    assert payload["formulario"]["event_id"] == payload["evento"]["id"]
    assert payload["formulario"]["ativacao_id"] == ativacao_id
    assert payload["formulario"]["submit_url"] == "/leads"
    assert payload["formulario"]["campos_obrigatorios"] == ["nome", "email"]
    assert payload["acesso"]["landing_url"] == f"http://testserver/landing/ativacoes/{ativacao_id}"
    assert payload["acesso"]["url_promotor"] == f"http://testserver/landing/ativacoes/{ativacao_id}"
    assert payload["acesso"]["qr_code_url"].startswith("data:image/svg+xml;base64,")
    assert payload["template"]["cta_experiment_enabled"] is False
    assert payload["template"]["cta_variants"] == []
    assert payload["ativacao"]["nome"] == "Captacao Principal"
    assert payload["ativacao"]["conversao_unica"] is False


def test_public_landing_por_evento_e_ativacao_expoe_regra_de_conversao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session)
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="BB Summit Multipla",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id, checkin_unico=True)
        evento_id = evento.id
        ativacao_id = ativacao.id

    resp = client.get(f"/eventos/{evento_id}/ativacoes/{ativacao_id}/landing")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ativacao_id"] == ativacao_id
    assert payload["ativacao"]["id"] == ativacao_id
    assert payload["ativacao"]["conversao_unica"] is True


def test_public_landing_por_evento_retorna_marca_minima_e_ativacao_nula_quando_nao_customizado(
    client, engine
):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Corporativo")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Forum BB Sem Hero",
            cta_personalizado=None,
        )
        evento_id = evento.id

    resp = client.get(f"/eventos/{evento_id}/landing")
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["ativacao_id"] is None
    assert payload["ativacao"] is None
    assert payload["evento"]["cta_personalizado"] is None
    assert payload["marca"] == {"tagline": "Banco do Brasil. Pra tudo que voce imaginar."}
    assert "url_hero_image" not in payload["marca"]


def test_public_landing_por_evento_aceita_template_override_transitorio_sem_persistir(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Corporativo")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Forum BB Preview",
            template_override="corporativo",
        )
        evento_id = evento.id

    resp = client.get(f"/eventos/{evento_id}/landing?template_override=show_musical")
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["template"]["categoria"] == "show_musical"
    assert payload["template"]["tema"] == "Show"
    assert payload["template"]["color_primary"] == "#735CC6"

    with Session(engine) as session:
        persisted = session.get(Evento, evento_id)
        assert persisted is not None
        assert persisted.template_override == "corporativo"


def test_public_landing_por_ativacao_normaliza_descricao_e_mensagem_qrcode(client, engine):
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
        ativacao.descricao = "  Ponto principal de captacao.  "
        ativacao.mensagem_qrcode = "  Escaneie o QR para validar o cadastro.  "
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing")
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["ativacao"]["descricao"] == "Ponto principal de captacao."
    assert payload["ativacao"]["mensagem_qrcode"] == "Escaneie o QR para validar o cadastro."


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
            "cpf": "529.982.247-25",
            "telefone": "(61) 99999-0000",
            "consentimento_lgpd": True,
        },
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["event_id"] == evento_id
    assert payload["ativacao_id"] == ativacao_id
    assert payload["lead_id"] > 0
    assert payload["lead_reconhecido"] is True
    assert payload["conversao_registrada"] is True
    assert payload["bloqueado_cpf_duplicado"] is False
    assert payload["token_reconhecimento"]
    assert resp.cookies.get("lp_lead_token") == payload["token_reconhecimento"]
    assert "lp_lead_token=" in (resp.headers.get("set-cookie") or "")

    with Session(engine) as session:
        lead = session.get(Lead, payload["lead_id"])
        assert lead is not None
        assert lead.email == "maria@example.com"
        assert lead.cpf == "52998224725"
        link = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == ativacao_id)
            .where(AtivacaoLead.lead_id == payload["lead_id"])
        ).first()
        assert link is not None
        conversao = session.exec(
            select(ConversaoAtivacao)
            .where(ConversaoAtivacao.ativacao_id == ativacao_id)
            .where(ConversaoAtivacao.lead_id == payload["lead_id"])
        ).first()
        assert conversao is not None
        assert conversao.cpf == "52998224725"


def test_public_submit_wrapper_mantem_contrato_do_endpoint_canonico(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Paridade",
        )
        ativacao_canonica = seed_ativacao(session, evento_id=evento.id, nome="Canonica")
        ativacao_wrapper = seed_ativacao(session, evento_id=evento.id, nome="Wrapper")
        evento_id = evento.id
        ativacao_canonica_id = ativacao_canonica.id
        ativacao_wrapper_id = ativacao_wrapper.id

    canonical_resp = client.post(
        "/leads",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "ativacao_id": ativacao_canonica_id,
            "consentimento_lgpd": True,
        },
    )
    wrapper_resp = client.post(
        f"/landing/ativacoes/{ativacao_wrapper_id}/submit",
        json={
            "nome": "Joao",
            "email": "joao@example.com",
            "cpf": "111.444.777-35",
            "consentimento_lgpd": True,
        },
    )

    assert canonical_resp.status_code == 201
    assert wrapper_resp.status_code == 201

    expected_keys = {
        "lead_id",
        "event_id",
        "ativacao_id",
        "ativacao_lead_id",
        "mensagem_sucesso",
        "lead_reconhecido",
        "conversao_registrada",
        "bloqueado_cpf_duplicado",
        "token_reconhecimento",
    }
    for payload, expected_ativacao_id in (
        (canonical_resp.json(), ativacao_canonica_id),
        (wrapper_resp.json(), ativacao_wrapper_id),
    ):
        assert set(payload.keys()) == expected_keys
        assert payload["event_id"] == evento_id
        assert payload["ativacao_id"] == expected_ativacao_id
        assert payload["lead_reconhecido"] is True
        assert payload["conversao_registrada"] is True
        assert payload["bloqueado_cpf_duplicado"] is False
        assert payload["token_reconhecimento"]


def test_public_landing_por_ativacao_reconhece_via_token_query(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Token Query",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        lead = seed_lead(session, evento=evento)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
        session.commit()
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing?token={token}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["lead_reconhecido"] is True
    assert payload["lead_ja_converteu_nesta_ativacao"] is False
    assert payload["token"] == token


def test_public_landing_por_ativacao_sinaliza_quando_lead_ja_converteu_nesta_ativacao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Conversao Atual",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        lead = seed_lead(session, evento=evento)
        seed_conversao_ativacao(session, ativacao_id=ativacao.id, lead_id=lead.id)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
        session.commit()
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing?token={token}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["lead_reconhecido"] is True
    assert payload["lead_ja_converteu_nesta_ativacao"] is True


def test_public_landing_por_ativacao_distingue_lead_reconhecido_sem_conversao_nesta_ativacao(
    client, engine
):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Conversao Outra Ativacao",
        )
        ativacao_origem = seed_ativacao(session, evento_id=evento.id, nome="Origem")
        ativacao_destino = seed_ativacao(session, evento_id=evento.id, nome="Destino")
        lead = seed_lead(session, evento=evento)
        seed_conversao_ativacao(session, ativacao_id=ativacao_origem.id, lead_id=lead.id)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
        session.commit()
        ativacao_destino_id = ativacao_destino.id

    resp = client.get(f"/ativacoes/{ativacao_destino_id}/landing?token={token}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["lead_reconhecido"] is True
    assert payload["lead_ja_converteu_nesta_ativacao"] is False


def test_public_landing_submit_bloqueia_cpf_duplicado_em_ativacao_unica(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Unique Landing",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id, checkin_unico=True)
        ativacao_id = ativacao.id

    body = {
        "nome": "Maria",
        "email": "maria@example.com",
        "cpf": "529.982.247-25",
        "consentimento_lgpd": True,
    }

    resp1 = client.post(f"/landing/ativacoes/{ativacao_id}/submit", json=body)
    resp2 = client.post(f"/landing/ativacoes/{ativacao_id}/submit", json=body)

    assert resp1.status_code == 201
    assert resp1.json()["lead_reconhecido"] is True
    assert resp1.json()["conversao_registrada"] is True
    assert resp1.json()["bloqueado_cpf_duplicado"] is False
    assert resp1.json()["token_reconhecimento"]

    assert resp2.status_code == 201
    payload = resp2.json()
    assert payload["lead_reconhecido"] is True
    assert payload["conversao_registrada"] is False
    assert payload["bloqueado_cpf_duplicado"] is True
    assert payload["lead_id"] == resp1.json()["lead_id"]
    assert payload["ativacao_lead_id"] == resp1.json()["ativacao_lead_id"]
    assert payload["token_reconhecimento"]
    assert resp2.cookies.get("lp_lead_token") == payload["token_reconhecimento"]
    assert "lp_lead_token=" in (resp2.headers.get("set-cookie") or "")

    with Session(engine) as session:
        conversoes = session.exec(
            select(ConversaoAtivacao).where(ConversaoAtivacao.ativacao_id == ativacao_id)
        ).all()
        assert len(conversoes) == 1


def test_public_landing_submit_sem_cpf_permanece_compativel_sem_registrar_conversao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Sem CPF",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Laura",
            "email": "laura@example.com",
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["lead_reconhecido"] is False
    assert payload["conversao_registrada"] is False
    assert payload["token_reconhecimento"] is None
    assert resp.cookies.get("lp_lead_token") is None
    assert resp.headers.get("set-cookie") is None

    with Session(engine) as session:
        conversoes = session.exec(
            select(ConversaoAtivacao).where(ConversaoAtivacao.ativacao_id == ativacao_id)
        ).all()
        assert conversoes == []


def test_public_landing_por_evento_reconhece_via_cookie_emitido_no_submit(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Cookie",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        evento_id = evento.id
        ativacao_id = ativacao.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "consentimento_lgpd": True,
        },
    )
    assert submit_resp.status_code == 201
    assert submit_resp.cookies.get("lp_lead_token") == submit_resp.json()["token_reconhecimento"]

    landing_resp = client.get(f"/eventos/{evento_id}/landing")

    assert landing_resp.status_code == 200
    payload = landing_resp.json()
    assert payload["lead_reconhecido"] is True
    assert payload["lead_ja_converteu_nesta_ativacao"] is False
    assert payload["token"] is None


def test_public_landing_faz_fallback_para_cookie_quando_token_query_invalido(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Cookie Fallback",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        evento_id = evento.id
        ativacao_id = ativacao.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Maria",
            "email": "maria@example.com",
            "cpf": "529.982.247-25",
            "consentimento_lgpd": True,
        },
    )
    assert submit_resp.status_code == 201
    assert submit_resp.cookies.get("lp_lead_token") == submit_resp.json()["token_reconhecimento"]

    landing_resp = client.get(f"/eventos/{evento_id}/landing?token=token-invalido")

    assert landing_resp.status_code == 200
    payload = landing_resp.json()
    assert payload["lead_reconhecido"] is True
    assert payload["lead_ja_converteu_nesta_ativacao"] is False
    assert payload["token"] == "token-invalido"


def test_public_landing_por_ativacao_nao_reconhece_token_expirado(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB Token Expirado",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        lead = seed_lead(session, evento=evento)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
        session.commit()
        record = session.exec(select(LeadReconhecimentoToken)).one()
        record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        session.add(record)
        session.commit()
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing?token={token}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["lead_reconhecido"] is False
    assert payload["lead_ja_converteu_nesta_ativacao"] is False
    assert payload["token"] == token


def test_public_landing_por_ativacao_nao_reconhece_token_de_outro_evento(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento_a = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB A",
        )
        evento_b = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB B",
        )
        ativacao_b = seed_ativacao(session, evento_id=evento_b.id)
        lead = seed_lead(session, evento=evento_a)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento_a.id)
        session.commit()
        ativacao_b_id = ativacao_b.id

    resp = client.get(f"/ativacoes/{ativacao_b_id}/landing?token={token}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["lead_reconhecido"] is False
    assert payload["lead_ja_converteu_nesta_ativacao"] is False
    assert payload["token"] == token


def test_public_landing_submit_por_ativacao_rejeita_cpf_invalido(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Hackathon BB CPF Invalido",
        )
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Laura",
            "email": "laura@example.com",
            "cpf": "529.982.247-26",
            "consentimento_lgpd": True,
        },
    )

    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "CPF_INVALID"

    with Session(engine) as session:
        leads = session.exec(select(Lead).where(Lead.email == "laura@example.com")).all()
        assert leads == []
        conversoes = session.exec(
            select(ConversaoAtivacao).where(ConversaoAtivacao.ativacao_id == ativacao_id)
        ).all()
        assert conversoes == []


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


def test_public_landing_supports_cta_variants_and_analytics_tracking(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Show")
        evento = seed_evento(
            session,
            agencia_id=agencia.id,
            tipo_id=tipo.id,
            nome="Festival BB",
            template_override="show_musical",
        )
        evento_id = evento.id

    landing_resp = client.get(f"/eventos/{evento_id}/landing")
    assert landing_resp.status_code == 200
    payload = landing_resp.json()
    assert payload["template"]["categoria"] == "show_musical"
    assert payload["template"]["cta_experiment_enabled"] is True
    assert len(payload["template"]["cta_variants"]) >= 2

    analytics_resp = client.post(
        "/landing/analytics",
        json={
            "event_id": evento_id,
            "categoria": "show_musical",
            "tema": "Show",
            "event_name": "page_view",
            "cta_variant_id": "show_a",
            "landing_session_id": "sessao-a",
        },
    )
    assert analytics_resp.status_code == 200

    with Session(engine) as session:
        events = session.exec(select(LandingAnalyticsEvent)).all()
        assert len(events) == 1
        assert events[0].cta_variant_id == "show_a"


def test_evento_create_update_e_get_expoem_campos_form_only_sem_hero_image(client, engine):
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
    assert created["cta_personalizado"] == "Quero participar"
    assert created["descricao_curta"] == "Resumo curto"
    assert "hero_image_url" not in created

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
    assert fetched["descricao_curta"] == "Resumo revisado"
    assert "hero_image_url" not in fetched


def test_evento_create_e_update_rejeitam_hero_image_url_como_campo_extra(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        seed_user(session, "strict-schema@example.com", "[REDACTED]")
        agencia_id = agencia.id
        tipo_id = tipo.id

    token = login_and_get_token(client, "strict-schema@example.com", "[REDACTED]")
    base_payload = {
        "nome": "Evento Strict",
        "descricao": "Descricao principal",
        "cidade": "Brasilia",
        "estado": "DF",
        "agencia_id": agencia_id,
        "tipo_id": tipo_id,
        "data_inicio_prevista": "2026-05-10",
        "data_fim_prevista": "2026-05-11",
    }

    create_resp = client.post(
        "/evento",
        headers={"Authorization": f"Bearer {token}"},
        json={
            **base_payload,
            "hero_image_url": "https://example.com/hero-tech.webp",
        },
    )
    assert create_resp.status_code == 422
    assert any(item["loc"] == ["body", "hero_image_url"] for item in create_resp.json()["detail"])

    valid_create_resp = client.post(
        "/evento",
        headers={"Authorization": f"Bearer {token}"},
        json=base_payload,
    )
    assert valid_create_resp.status_code == 201
    evento_id = valid_create_resp.json()["id"]

    update_resp = client.put(
        f"/evento/{evento_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"hero_image_url": "https://example.com/hero-tech.webp"},
    )
    assert update_resp.status_code == 422
    assert any(item["loc"] == ["body", "hero_image_url"] for item in update_resp.json()["detail"])


# ---------------------------------------------------------------------------
# EPIC-F2-02 — Extensão payload landing + endpoint gamificação
# ---------------------------------------------------------------------------


def seed_gamificacao(session: Session, *, evento_id: int) -> Gamificacao:
    gam = Gamificacao(
        evento_id=evento_id,
        nome="Roleta da Sorte",
        descricao="Gire a roleta e ganhe premios.",
        premio="Copo BB exclusivo",
        titulo_feedback="Parabens!",
        texto_feedback="Voce ganhou um copo BB exclusivo. Retire no stand.",
    )
    session.add(gam)
    session.commit()
    session.refresh(gam)
    return gam


def test_landing_payload_inclui_gamificacoes_quando_ativacao_tem_gamificacao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Esporte")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="BB Run")
        gam = seed_gamificacao(session, evento_id=evento.id)
        ativacao = seed_ativacao(session, evento_id=evento.id, nome="Stand BB")
        ativacao.gamificacao_id = gam.id
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing")
    assert resp.status_code == 200
    payload = resp.json()

    assert "gamificacoes" in payload
    assert len(payload["gamificacoes"]) == 1
    g = payload["gamificacoes"][0]
    assert g["nome"] == "Roleta da Sorte"
    assert g["descricao"] == "Gire a roleta e ganhe premios."
    assert g["premio"] == "Copo BB exclusivo"
    assert g["titulo_feedback"] == "Parabens!"
    assert g["texto_feedback"] == "Voce ganhou um copo BB exclusivo. Retire no stand."

    assert payload["ativacao"]["nome"] == "Stand BB"
    assert payload["evento"]["nome"] == "BB Run"
    assert payload["template"] is not None
    assert payload["formulario"] is not None
    assert payload["marca"] is not None
    assert payload["acesso"] is not None


def test_landing_payload_gamificacoes_vazio_quando_ativacao_sem_gamificacao(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Corporativo")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="BB Forum")
        ativacao = seed_ativacao(session, evento_id=evento.id, nome="Balcao")
        ativacao_id = ativacao.id

    resp = client.get(f"/ativacoes/{ativacao_id}/landing")
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["gamificacoes"] == []
    assert payload["ativacao"]["nome"] == "Balcao"


def test_submit_retorna_ativacao_lead_id(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB 2")
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Joao",
            "email": "joao@example.com",
            "consentimento_lgpd": True,
        },
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert "ativacao_lead_id" in payload
    assert isinstance(payload["ativacao_lead_id"], int)
    assert payload["ativacao_lead_id"] > 0


def test_submit_repetido_nao_duplica_ativacao_lead(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tecnologia")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Hackathon BB 3")
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id

    body = {
        "nome": "Laura",
        "email": "laura@example.com",
        "consentimento_lgpd": True,
    }
    resp1 = client.post(f"/landing/ativacoes/{ativacao_id}/submit", json=body)
    resp2 = client.post(f"/landing/ativacoes/{ativacao_id}/submit", json=body)

    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["ativacao_lead_id"] == resp2.json()["ativacao_lead_id"]

    with Session(engine) as session:
        links = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == ativacao_id)
        ).all()
        assert len(links) == 1


def test_gamificacao_complete_sucesso(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Show")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Festival BB 2")
        gam = seed_gamificacao(session, evento_id=evento.id)
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao.gamificacao_id = gam.id
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
        ativacao_id = ativacao.id
        gam_id = gam.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Ana",
            "email": "ana@example.com",
            "consentimento_lgpd": True,
        },
    )
    assert submit_resp.status_code == 201
    ativacao_lead_id = submit_resp.json()["ativacao_lead_id"]

    resp = client.post(
        f"/ativacao-leads/{ativacao_lead_id}/gamificacao",
        json={"gamificacao_id": gam_id, "gamificacao_completed": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ativacao_lead_id"] == ativacao_lead_id
    assert data["gamificacao_id"] == gam_id
    assert data["gamificacao_completed"] is True
    assert data["gamificacao_completed_at"] is not None

    with Session(engine) as session:
        al = session.get(AtivacaoLead, ativacao_lead_id)
        assert al is not None
        assert al.gamificacao_id == gam_id
        assert al.gamificacao_completed is True
        assert al.gamificacao_completed_at is not None


def test_gamificacao_complete_404_quando_ativacao_lead_inexistente(client, engine):
    resp = client.post(
        "/ativacao-leads/999999/gamificacao",
        json={"gamificacao_id": 1, "gamificacao_completed": True},
    )
    assert resp.status_code == 404


def test_gamificacao_complete_400_quando_gamificacao_id_invalido(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Cultura")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="CCBB Exp")
        ativacao = seed_ativacao(session, evento_id=evento.id)
        lead = Lead(
            nome="Pedro",
            email="pedro@example.com",
            evento_nome=evento.nome,
            cidade="Brasilia",
            estado="DF",
            fonte_origem="landing_publica",
            opt_in="aceito",
            opt_in_flag=True,
        )
        session.add(lead)
        session.flush()
        al = AtivacaoLead(ativacao_id=ativacao.id, lead_id=lead.id)
        session.add(al)
        session.commit()
        session.refresh(al)
        al_id = al.id

    resp = client.post(
        f"/ativacao-leads/{al_id}/gamificacao",
        json={"gamificacao_id": 999999, "gamificacao_completed": True},
    )
    assert resp.status_code == 400


def test_gamificacao_complete_400_quando_ativacao_sem_gamificacao_configurada(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Cultura")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="CCBB Exp 2")
        gam = seed_gamificacao(session, evento_id=evento.id)
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao_id = ativacao.id
        gam_id = gam.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Pedro",
            "email": "pedro2@example.com",
            "consentimento_lgpd": True,
        },
    )
    assert submit_resp.status_code == 201
    ativacao_lead_id = submit_resp.json()["ativacao_lead_id"]

    resp = client.post(
        f"/ativacao-leads/{ativacao_lead_id}/gamificacao",
        json={"gamificacao_id": gam_id, "gamificacao_completed": True},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "GAMIFICACAO_OUT_OF_SCOPE"


def test_gamificacao_complete_idempotente(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Tech")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="BB Inova")
        gam = seed_gamificacao(session, evento_id=evento.id)
        ativacao = seed_ativacao(session, evento_id=evento.id)
        ativacao.gamificacao_id = gam.id
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
        ativacao_id = ativacao.id
        gam_id = gam.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Carlos",
            "email": "carlos@example.com",
            "consentimento_lgpd": True,
        },
    )
    ativacao_lead_id = submit_resp.json()["ativacao_lead_id"]

    body = {"gamificacao_id": gam_id, "gamificacao_completed": True}
    resp1 = client.post(f"/ativacao-leads/{ativacao_lead_id}/gamificacao", json=body)
    resp2 = client.post(f"/ativacao-leads/{ativacao_lead_id}/gamificacao", json=body)

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["gamificacao_id"] == resp2.json()["gamificacao_id"]
    assert resp1.json()["gamificacao_completed_at"] == resp2.json()["gamificacao_completed_at"]

    with Session(engine) as session:
        links = session.exec(
            select(AtivacaoLead).where(AtivacaoLead.id == ativacao_lead_id)
        ).all()
        assert len(links) == 1


def test_gamificacao_complete_400_quando_gamificacao_de_outro_evento(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Esporte")
        evento_a = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Evento A")
        evento_b = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Evento B")

        gam_a = seed_gamificacao(session, evento_id=evento_a.id)
        gam_b = seed_gamificacao(session, evento_id=evento_b.id)

        ativacao_a = seed_ativacao(session, evento_id=evento_a.id, nome="Ativacao A")
        ativacao_a.gamificacao_id = gam_a.id
        session.add(ativacao_a)
        session.commit()
        session.refresh(ativacao_a)
        ativacao_a_id = ativacao_a.id
        gam_b_id = gam_b.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_a_id}/submit",
        json={
            "nome": "Julia",
            "email": "julia@example.com",
            "consentimento_lgpd": True,
        },
    )
    assert submit_resp.status_code == 201
    ativacao_lead_id = submit_resp.json()["ativacao_lead_id"]

    resp = client.post(
        f"/ativacao-leads/{ativacao_lead_id}/gamificacao",
        json={"gamificacao_id": gam_b_id, "gamificacao_completed": True},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "GAMIFICACAO_OUT_OF_SCOPE"


def test_gamificacao_complete_limpa_timestamp_quando_completed_false(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session)
        tipo = seed_tipo(session, "Cultura")
        evento = seed_evento(session, agencia_id=agencia.id, tipo_id=tipo.id, nome="Festival Cultural")
        gam = seed_gamificacao(session, evento_id=evento.id)
        ativacao = seed_ativacao(session, evento_id=evento.id, nome="Ativacao Cultura")
        ativacao.gamificacao_id = gam.id
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
        ativacao_id = ativacao.id
        gam_id = gam.id

    submit_resp = client.post(
        f"/landing/ativacoes/{ativacao_id}/submit",
        json={
            "nome": "Marina",
            "email": "marina@example.com",
            "consentimento_lgpd": True,
        },
    )
    assert submit_resp.status_code == 201
    ativacao_lead_id = submit_resp.json()["ativacao_lead_id"]

    complete_resp = client.post(
        f"/ativacao-leads/{ativacao_lead_id}/gamificacao",
        json={"gamificacao_id": gam_id, "gamificacao_completed": True},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["gamificacao_completed_at"] is not None

    uncomplete_resp = client.post(
        f"/ativacao-leads/{ativacao_lead_id}/gamificacao",
        json={"gamificacao_id": gam_id, "gamificacao_completed": False},
    )
    assert uncomplete_resp.status_code == 200
    assert uncomplete_resp.json()["gamificacao_completed"] is False
    assert uncomplete_resp.json()["gamificacao_completed_at"] is None
