from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.models.ingressos_v2_models import (
    AuditoriaDesbloqueioInventario,
    AuditoriaIngressoEvento,
    ConfiguracaoIngressoEvento,
    ConfiguracaoIngressoEventoTipo,
    DesbloqueioManualInventario,
    InventarioIngresso,
    PrevisaoIngresso,
    RecebimentoIngresso,
)
from app.models.models import Agencia, Diretoria, Evento, Funcionario, StatusEvento, TipoIngresso, Usuario
from app.routers.auth import router as auth_router
from app.routers.ingressos_v2 import router as ingressos_v2_router
from app.services.inventario_ingressos import calcular_inventario
from app.utils.security import hash_password


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(ingressos_v2_router)
    return app


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
    app = create_test_app()

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


def test_patch_configuracao_modo_igual_nao_cria_auditoria(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Same", "same.com.br")
        diretoria = seed_diretoria(session, "dir-v2-same")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Same Mode",
        )
        user = seed_npbb_user(session, "npbb-v2-same@example.com", "Senha123!")
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
        json={"modo_fornecimento": "externo_recebido"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["modo_fornecimento"] == "externo_recebido"

    with Session(engine) as session:
        audits = session.exec(
            select(AuditoriaIngressoEvento).where(
                AuditoriaIngressoEvento.evento_id == evento_id
            )
        ).all()
        assert audits == []


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


def test_post_previsao_recalcula_snapshot_e_liberta_surplus(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Surplus", "surplus.com.br")
        diretoria = seed_diretoria(session, "dir-v2-surplus")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Surplus",
        )
        user = seed_npbb_user(session, "npbb-v2-surplus@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)

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

        session.add(
            PrevisaoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso="pista",
                quantidade=100,
            )
        )
        session.commit()
        session.add(
            RecebimentoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso="pista",
                quantidade=120,
            )
        )
        session.commit()

        inventario = calcular_inventario(
            session,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        session.commit()

        assert inventario.bloqueado == 20
        assert inventario.disponivel == 100
        inventario_id = int(inventario.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/previsoes",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 120,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    assert resp.json()["quantidade"] == 120

    with Session(engine) as session:
        inventario = session.exec(
            select(InventarioIngresso).where(
                InventarioIngresso.evento_id == evento_id,
                InventarioIngresso.diretoria_id == diretoria_id,
                InventarioIngresso.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).first()

        assert inventario is not None
        assert int(inventario.id) == inventario_id
        assert inventario.planejado == 120
        assert inventario.recebido_confirmado == 120
        assert inventario.bloqueado == 0
        assert inventario.disponivel == 120


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


def test_post_recebimento_retorna_recebimento_e_inventario_atualizado(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Receb", "receb.com.br")
        diretoria = seed_diretoria(session, "dir-v2-receb")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Recebimento",
        )
        user = seed_npbb_user(session, "npbb-v2-receb@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)
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
        session.add(
            PrevisaoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso="pista",
                quantidade=100,
            )
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/recebimentos",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 50,
            "artifact_link": "https://drive.example/recibo",
            "correlation_id": "99999999-8888-7777-6666-555555555555",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["recebimento"]["quantidade"] == 50
    assert payload["recebimento"]["artifact_link"] == "https://drive.example/recibo"
    assert payload["recebimento"]["correlation_id"] == "99999999-8888-7777-6666-555555555555"
    assert payload["inventario"]["planejado"] == 100
    assert payload["inventario"]["recebido_confirmado"] == 50
    assert payload["inventario"]["bloqueado"] == 50
    assert payload["inventario"]["disponivel"] == 50


def test_recebimento_sem_configuracao_retorna_404(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Receb No Config", "recebnoconfig.com.br")
        diretoria = seed_diretoria(session, "dir-v2-receb-no-config")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Receb Sem Config",
        )
        user = seed_npbb_user(session, "npbb-v2-receb-no-config@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/recebimentos",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "CONFIGURACAO_INGRESSO_NOT_FOUND"


def test_recebimento_rejeita_tipo_inativo(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Receb Tipo", "recebtipo.com.br")
        diretoria = seed_diretoria(session, "dir-v2-receb-tipo")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Receb Tipo Inativo",
        )
        user = seed_npbb_user(session, "npbb-v2-receb-tipo@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)
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
        f"/ingressos/v2/eventos/{evento_id}/recebimentos",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "camarote",
            "quantidade": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "TIPO_INGRESSO_INVALID_FOR_EVENT"


def test_listar_inventario_retorna_snapshots_e_aplica_filtros(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Inv", "inventario.com.br")
        diretoria_a = seed_diretoria(session, "dir-v2-inv-a")
        diretoria_b = seed_diretoria(session, "dir-v2-inv-b")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria_a.id),
            nome="Evento Inventario",
        )
        user = seed_npbb_user(session, "npbb-v2-inventario@example.com", "Senha123!")
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
        session.add_all(
            [
                PrevisaoIngresso(
                    evento_id=evento_id,
                    diretoria_id=int(diretoria_a.id),
                    tipo_ingresso="pista",
                    quantidade=100,
                ),
                PrevisaoIngresso(
                    evento_id=evento_id,
                    diretoria_id=int(diretoria_b.id),
                    tipo_ingresso="pista",
                    quantidade=40,
                ),
                RecebimentoIngresso(
                    evento_id=evento_id,
                    diretoria_id=int(diretoria_a.id),
                    tipo_ingresso="pista",
                    quantidade=80,
                ),
                RecebimentoIngresso(
                    evento_id=evento_id,
                    diretoria_id=int(diretoria_b.id),
                    tipo_ingresso="pista",
                    quantidade=40,
                ),
            ]
        )
        session.commit()

        calcular_inventario(
            session,
            evento_id=evento_id,
            diretoria_id=int(diretoria_a.id),
            tipo_ingresso=TipoIngresso.PISTA,
        )
        calcular_inventario(
            session,
            evento_id=evento_id,
            diretoria_id=int(diretoria_b.id),
            tipo_ingresso=TipoIngresso.PISTA,
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(f"/ingressos/v2/eventos/{evento_id}/inventario", headers=headers)
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload) == 2

    filtered = client.get(
        f"/ingressos/v2/eventos/{evento_id}/inventario",
        params={"diretoria_id": int(diretoria_b.id), "tipo_ingresso": "pista"},
        headers=headers,
    )
    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert len(filtered_payload) == 1
    assert filtered_payload[0]["diretoria_id"] == int(diretoria_b.id)
    assert filtered_payload[0]["bloqueado"] == 0
    assert filtered_payload[0]["disponivel"] == 40


def test_listar_inventario_sem_configuracao_retorna_404(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Inv No Config", "invnoconfig.com.br")
        diretoria = seed_diretoria(session, "dir-v2-inv-no-config")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Inventario Sem Config",
        )
        user = seed_npbb_user(session, "npbb-v2-inv-no-config@example.com", "Senha123!")
        evento_id = int(evento.id)

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.get(
        f"/ingressos/v2/eventos/{evento_id}/inventario",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "CONFIGURACAO_INGRESSO_NOT_FOUND"


def test_post_desbloqueio_manual_atualiza_inventario_e_grava_auditoria(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia Desbloq", "desbloq.com.br")
        diretoria = seed_diretoria(session, "dir-v2-desbloq")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Desbloqueio",
        )
        user = seed_npbb_user(session, "npbb-v2-desbloq@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)
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
        session.add(
            PrevisaoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso="pista",
                quantidade=100,
            )
        )
        session.add(
            RecebimentoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso="pista",
                quantidade=50,
            )
        )
        session.commit()
        calcular_inventario(
            session,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        session.commit()

    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 20,
            "motivo": "Liberacao controlada",
            "correlation_id": "12121212-3434-5656-7878-909090909090",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["quantidade"] == 20
    assert payload["bloqueado_antes"] == 50
    assert payload["bloqueado_depois"] == 30
    assert payload["correlation_id"] == "12121212-3434-5656-7878-909090909090"
    assert payload["inventario"]["bloqueado"] == 30
    assert payload["inventario"]["disponivel"] == 70

    with Session(engine) as session:
        audit = session.exec(
            select(AuditoriaDesbloqueioInventario).where(
                AuditoriaDesbloqueioInventario.evento_id == evento_id
            )
        ).first()
        assert audit is not None
        assert audit.quantidade == 20
        assert audit.usuario_id == int(user.id)

        override = session.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
                DesbloqueioManualInventario.diretoria_id == diretoria_id,
                DesbloqueioManualInventario.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).first()
        assert override is not None
        assert override.quantidade_restante == 20


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

        recebimento_resp = client.post(
            f"/ingressos/v2/eventos/{evento_id}/recebimentos",
            json={
                "diretoria_id": int(diretoria.id),
                "tipo_ingresso": "pista",
                "quantidade": 1,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert recebimento_resp.status_code == 403
        assert recebimento_resp.json()["detail"]["code"] == "FORBIDDEN"

        desbloqueio_resp = client.post(
            f"/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual",
            json={
                "diretoria_id": int(diretoria.id),
                "tipo_ingresso": "pista",
                "quantidade": 1,
                "motivo": "Nao autorizado",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert desbloqueio_resp.status_code == 403
        assert desbloqueio_resp.json()["detail"]["code"] == "FORBIDDEN"


def test_patch_configuracao_exige_usuario_npbb(client, engine):
    with Session(engine) as session:
        agencia = seed_agencia(session, "Agencia PatchAuth", "patchauth.com.br")
        diretoria = seed_diretoria(session, "dir-v2-patch-auth")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome="Evento Patch RBAC",
        )
        config = ConfiguracaoIngressoEvento(
            evento_id=int(evento.id),
            modo_fornecimento="externo_recebido",
        )
        session.add(config)
        session.commit()
        agencia_user = seed_agencia_user(
            session,
            email="agency-v2-patch@patchauth.com.br",
            password="Senha123!",
            agencia_id=int(agencia.id),
        )
        bb_user = seed_bb_user(
            session,
            email="bb-v2-patch@bb.com.br",
            password="Senha123!",
            diretoria_id=int(diretoria.id),
            matricula="PATCH01",
        )
        evento_id = int(evento.id)

    for user in (agencia_user, bb_user):
        token = login_and_get_token(client, user.email, "Senha123!")
        resp = client.patch(
            f"/ingressos/v2/eventos/{evento_id}/configuracao",
            json={"modo_fornecimento": "interno_emitido_com_qr"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert resp.json()["detail"]["code"] == "FORBIDDEN"


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


def _setup_desbloqueio_scenario(engine, *, modo="externo_recebido", recebimento_qty=50):
    """Helper: cria evento com config, previsao=100, recebimento opcional, e retorna ids."""
    with Session(engine) as session:
        agencia = seed_agencia(session, f"Ag-{modo[:6]}-{recebimento_qty}", f"desbloq-{modo[:6]}-{recebimento_qty}.com.br")
        diretoria = seed_diretoria(session, f"dir-desbloq-{modo[:6]}-{recebimento_qty}")
        evento = seed_evento(
            session,
            agencia_id=int(agencia.id),
            diretoria_id=int(diretoria.id),
            nome=f"Evento Desbloq {modo[:6]} {recebimento_qty}",
        )
        user = seed_npbb_user(session, f"npbb-desbloq-{modo[:6]}-{recebimento_qty}@example.com", "Senha123!")
        evento_id = int(evento.id)
        diretoria_id = int(diretoria.id)

        config = ConfiguracaoIngressoEvento(
            evento_id=evento_id,
            modo_fornecimento=modo,
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
        session.add(
            PrevisaoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso="pista",
                quantidade=100,
            )
        )
        session.commit()

        if modo == "externo_recebido" and recebimento_qty > 0:
            session.add(
                RecebimentoIngresso(
                    evento_id=evento_id,
                    diretoria_id=diretoria_id,
                    tipo_ingresso="pista",
                    quantidade=recebimento_qty,
                )
            )
            session.commit()
            calcular_inventario(
                session,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
            )
            session.commit()

    return evento_id, diretoria_id, user


def test_desbloqueio_manual_modo_interno_retorna_400(client, engine):
    evento_id, diretoria_id, user = _setup_desbloqueio_scenario(
        engine, modo="interno_emitido_com_qr", recebimento_qty=0
    )
    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 1,
            "motivo": "Nao deveria funcionar",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "DESBLOQUEIO_MANUAL_INVALID_MODE"


def test_desbloqueio_manual_sem_bloqueio_retorna_409(client, engine):
    evento_id, diretoria_id, user = _setup_desbloqueio_scenario(
        engine, recebimento_qty=100
    )
    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 1,
            "motivo": "Sem bloqueio ativo",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "DESBLOQUEIO_MANUAL_SEM_BLOQUEIO"


def test_desbloqueio_manual_excede_bloqueio_retorna_409(client, engine):
    evento_id, diretoria_id, user = _setup_desbloqueio_scenario(
        engine, recebimento_qty=50
    )
    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 999,
            "motivo": "Excede o bloqueado",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "DESBLOQUEIO_MANUAL_EXCEDE_BLOQUEIO"


def test_desbloqueio_manual_motivo_vazio_retorna_422(client, engine):
    evento_id, diretoria_id, user = _setup_desbloqueio_scenario(
        engine, recebimento_qty=50
    )
    token = login_and_get_token(client, user.email, "Senha123!")
    resp = client.post(
        f"/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual",
        json={
            "diretoria_id": diretoria_id,
            "tipo_ingresso": "pista",
            "quantidade": 10,
            "motivo": "",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
