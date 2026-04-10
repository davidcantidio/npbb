from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.ingressos_v2_models import (
    AuditoriaIngressoEvento,
    ConfiguracaoIngressoEvento,
    ConfiguracaoIngressoEventoTipo,
    PrevisaoIngresso,
)
from app.models.models import Agencia, Diretoria, Evento, Funcionario, StatusEvento, Usuario
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


def seed_agencia(session: Session, nome: str, dominio: str) -> Agencia:
    agencia = Agencia(nome=nome, dominio=dominio, lote=1)
    session.add(agencia)
    session.commit()
    session.refresh(agencia)
    session.expunge(agencia)
    return agencia


def seed_diretoria(session: Session, nome: str) -> Diretoria:
    diretoria = Diretoria(nome=nome)
    session.add(diretoria)
    session.commit()
    session.refresh(diretoria)
    session.expunge(diretoria)
    return diretoria


def seed_evento(
    session: Session,
    *,
    agencia_id: int,
    diretoria_id: int,
    nome: str = "Evento Ingressos V2",
) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    assert status and status.id
    evento = Evento(
        nome=nome,
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        agencia_id=agencia_id,
        diretoria_id=diretoria_id,
        status_id=status.id,
        data_inicio_prevista=date(2026, 5, 1),
        data_fim_prevista=date(2026, 5, 2),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    session.expunge(evento)
    return evento


def seed_npbb_user(session: Session, email: str, password: str) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.expunge(user)
    return user


def seed_agencia_user(
    session: Session, *, email: str, password: str, agencia_id: int
) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario="agencia",
        agencia_id=agencia_id,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.expunge(user)
    return user


def seed_bb_user(
    session: Session,
    *,
    email: str,
    password: str,
    diretoria_id: int,
    matricula: str,
) -> Usuario:
    funcionario = Funcionario(
        nome="Funcionario BB",
        chave_c=matricula,
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
        matricula=matricula,
        status_aprovacao="APROVADO",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.expunge(user)
    return user


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_cria_e_ler_configuracao_ingresso_v2(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "V3A", "v3a.com.br")
        diretoria = seed_diretoria(session, "dir-v2-cria")
        evento = seed_evento(session, agencia_id=int(agencia.id), diretoria_id=int(diretoria.id))
        user = seed_npbb_user(session, "npbb-v2-create@example.com", "Senha123!")
        evento_id = int(evento.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        json={
            "modo_fornecimento": "externo_recebido",
            "tipos_ingresso": ["camarote", "pista"],
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    payload = create_resp.json()
    assert payload["evento_id"] == evento_id
    assert payload["modo_fornecimento"] == "externo_recebido"
    assert payload["tipos_ingresso"] == ["camarote", "pista"]

    read_resp = client.get(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        headers=headers,
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["tipos_ingresso"] == ["camarote", "pista"]

    with Session(engine) as session:
        config = session.exec(
            select(ConfiguracaoIngressoEvento).where(
                ConfiguracaoIngressoEvento.evento_id == evento_id
            )
        ).first()
        assert config is not None
        tipos = session.exec(
            select(ConfiguracaoIngressoEventoTipo.tipo_ingresso).where(
                ConfiguracaoIngressoEventoTipo.configuracao_id == config.id
            )
        ).all()
        assert sorted(tipos) == ["camarote", "pista"]


def test_criar_configuracao_duplicada_retorna_conflito(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Sherpa", "sherpa.com.br")
        diretoria = seed_diretoria(session, "dir-v2-dup")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Duplicado",
        )
        user = seed_npbb_user(session, "npbb-v2-dup@example.com", "Senha123!")
        evento_id = int(evento.id)
        session.add(
            ConfiguracaoIngressoEvento(
                evento_id=evento_id,
                modo_fornecimento="interno_emitido_com_qr",
            )
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        json={
            "modo_fornecimento": "externo_recebido",
            "tipos_ingresso": ["pista"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "CONFIGURACAO_INGRESSO_DUPLICATE"


def test_get_configuracao_inexistente_retorna_404(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Monumenta", "monumenta.com.br")
        diretoria = seed_diretoria(session, "dir-v2-miss")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Sem Config",
        )
        user = seed_npbb_user(session, "npbb-v2-miss@example.com", "Senha123!")
        evento_id = int(evento.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.get(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "CONFIGURACAO_INGRESSO_NOT_FOUND"


def test_patch_configuracao_tipos_sem_auditoria(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Terrua", "terrua.com.br")
        diretoria = seed_diretoria(session, "dir-v2-patch-tipos")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Patch Tipos",
        )
        user = seed_npbb_user(session, "npbb-v2-patch-tipos@example.com", "Senha123!")
        evento_id = int(evento.id)
        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        session.refresh(config)
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=int(config.id),
                tipo_ingresso="pista",
            )
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.patch(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        json={"tipos_ingresso": ["camarote", "pista_premium"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["tipos_ingresso"] == ["camarote", "pista_premium"]

    with Session(engine) as session:
        audits = session.exec(
            select(AuditoriaIngressoEvento).where(AuditoriaIngressoEvento.evento_id == evento_id)
        ).all()
        assert audits == []


def test_patch_configuracao_modo_gera_auditoria(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Audit", "audit.com.br")
        diretoria = seed_diretoria(session, "dir-v2-audit")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Auditado",
        )
        user = seed_npbb_user(session, "npbb-v2-audit@example.com", "Senha123!")
        evento_id = int(evento.id)
        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        session.refresh(config)
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=int(config.id),
                tipo_ingresso="pista",
            )
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.patch(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        json={"modo_fornecimento": "interno_emitido_com_qr"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["modo_fornecimento"] == "interno_emitido_com_qr"

    with Session(engine) as session:
        audits = session.exec(
            select(AuditoriaIngressoEvento).where(AuditoriaIngressoEvento.evento_id == evento_id)
        ).all()
        assert len(audits) == 1
        assert audits[0].modo_fornecimento_anterior == "externo_recebido"
        assert audits[0].modo_fornecimento_novo == "interno_emitido_com_qr"
        assert audits[0].usuario_id == user.id


def test_patch_configuracao_sem_payload_retorna_400(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Empty", "empty.com.br")
        diretoria = seed_diretoria(session, "dir-v2-empty")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Patch Empty",
        )
        user = seed_npbb_user(session, "npbb-v2-empty@example.com", "Senha123!")
        evento_id = int(evento.id)
        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.patch(
        f"/ingressos/v2/eventos/{evento_id}/configuracao",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "VALIDATION_ERROR_NO_FIELDS"


def test_previsao_upsert_e_listagem_com_filtros(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Prev", "prev.com.br")
        diretoria_a = seed_diretoria(session, "dir-v2-prev-a")
        diretoria_b = seed_diretoria(session, "dir-v2-prev-b")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria_a.id),
            nome="Evento Previsoes",
        )
        user = seed_npbb_user(session, "npbb-v2-prev@example.com", "Senha123!")
        evento_id = int(evento.id)
        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        session.refresh(config)
        session.add_all(
            [
                ConfiguracaoIngressoEventoTipo(
                    configuracao_id=int(config.id),
                    tipo_ingresso="pista",
                ),
                ConfiguracaoIngressoEventoTipo(
                    configuracao_id=int(config.id),
                    tipo_ingresso="camarote",
                ),
            ]
        )
        session.commit()
        diretoria_a_id = int(diretoria_a.id)
        diretoria_b_id = int(diretoria_b.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": diretoria_a_id,
            "tipo_ingresso": "pista",
            "quantidade": 10,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["quantidade"] == 10

    update_resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": diretoria_a_id,
            "tipo_ingresso": "pista",
            "quantidade": 25,
        },
        headers=headers,
    )
    assert update_resp.status_code == 201
    assert update_resp.json()["quantidade"] == 25

    other_resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": diretoria_b_id,
            "tipo_ingresso": "camarote",
            "quantidade": 5,
        },
        headers=headers,
    )
    assert other_resp.status_code == 201

    list_resp = client.get(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        headers=headers,
    )
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert [(item["diretoria_id"], item["tipo_ingresso"], item["quantidade"]) for item in payload] == [
        (diretoria_a_id, "pista", 25),
        (diretoria_b_id, "camarote", 5),
    ]

    filtered_resp = client.get(
        f"/ingressos/v2/eventos/{evento_id}/previsoes?diretoria_id={diretoria_b_id}",
        headers=headers,
    )
    assert filtered_resp.status_code == 200
    assert len(filtered_resp.json()) == 1
    assert filtered_resp.json()[0]["diretoria_id"] == diretoria_b_id


def test_previsao_rejeita_tipo_inativo(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Tipo", "tipo.com.br")
        diretoria = seed_diretoria(session, "dir-v2-inativo")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Tipo Inativo",
        )
        user = seed_npbb_user(session, "npbb-v2-inativo@example.com", "Senha123!")
        evento_id = int(evento.id)
        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        session.refresh(config)
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=int(config.id),
                tipo_ingresso="pista",
            )
        )
        session.commit()
        diretoria_id = int(diretoria.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "camarote",
            "quantidade": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "TIPO_INGRESSO_INVALID_FOR_EVENT"


def test_previsao_retorna_404_para_diretoria_inexistente(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Dir Missing", "dirmissing.com.br")
        diretoria = seed_diretoria(session, "dir-v2-dir-missing")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Diretoria Missing",
        )
        user = seed_npbb_user(session, "npbb-v2-dir-missing@example.com", "Senha123!")
        evento_id = int(evento.id)
        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        session.refresh(config)
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=int(config.id),
                tipo_ingresso="pista",
            )
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": 999999,
            "tipo_ingresso": "pista",
            "quantidade": 2,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "DIRETORIA_NOT_FOUND"


def test_previsao_sem_configuracao_retorna_404(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia No Config", "noconfig.com.br")
        diretoria = seed_diretoria(session, "dir-v2-no-config")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento No Config",
        )
        user = seed_npbb_user(session, "npbb-v2-no-config@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "CONFIGURACAO_INGRESSO_NOT_FOUND"


def test_escrita_v2_exige_usuario_npbb(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Auth", "auth.com.br")
        diretoria = seed_diretoria(session, "dir-v2-auth")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Auth",
        )
        agencia_user = seed_agencia_user(
            session,
            email="agency-v2-auth@auth.com.br",
            password="Senha123!",
            agencia_id=int(agencia.id),
        )
        bb_user = seed_bb_user(
            session,
            email="bb-v2-auth@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
            matricula="AUTH001",
        )
        evento_id = int(evento.id)

    agency_token = login_and_get_token(client, agencia_user.email, "Senha123!")
    bb_token = login_and_get_token(client, bb_user.email, "Senha123!")

    for token in (agency_token, bb_token):
        config_resp = client.post(
            f"/ingressos/v2/eventos/{evento_id}/configuracao",
            json={
                "modo_fornecimento": "externo_recebido",
                "tipos_ingresso": ["pista"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert config_resp.status_code == 403
        assert config_resp.json()["detail"]["code"] == "FORBIDDEN"

        previsao_resp = client.post(
            f"/ingressos/v2/eventos/{evento_id}/previsoes",
            json={
                "diretoria_id": int(diretoria.id),
                "tipo_ingresso": "pista",
                "quantidade": 1,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert previsao_resp.status_code == 403
        assert previsao_resp.json()["detail"]["code"] == "FORBIDDEN"


def test_leitura_v2_respeita_visibilidade_da_agencia(client, engine):
    with Session(engine) as session:
        agencia_a = seed_agencia(session, "Agencia A", "ag-a.com.br")
        agencia_b = seed_agencia(session, "Agencia B", "ag-b.com.br")
        diretoria = seed_diretoria(session, "dir-v2-vis")
        evento_a = seed_evento(
            session,
            agencia_id=int(agencia_a.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Agencia A",
        )
        evento_b = seed_evento(
            session,
            agencia_id=int(agencia_b.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Agencia B",
        )
        config = ConfiguracaoIngressoEvento(
            evento_id=int(evento_a.id),
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        session.refresh(config)
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=int(config.id),
                tipo_ingresso="pista",
            )
        )
        session.commit()
        agency_user = seed_agencia_user(
            session,
            email="agency-v2-read@ag-a.com.br",
            password="Senha123!",
            agencia_id=int(agencia_a.id),
        )

    token = login_and_get_token(client, agency_user.email, "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    ok_resp = client.get(
        f"/ingressos/v2/eventos/{int(evento_a.id)}/configuracao",
        headers=headers,
    )
    assert ok_resp.status_code == 200

    hidden_resp = client.get(
        f"/ingressos/v2/eventos/{int(evento_b.id)}/configuracao",
        headers=headers,
    )
    assert hidden_resp.status_code == 404
    assert hidden_resp.json()["detail"]["code"] == "EVENTO_NOT_FOUND"
