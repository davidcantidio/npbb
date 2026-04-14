"""Tests for F3 Gold pipeline endpoints.

GET  /leads/batches/{id}
POST /leads/batches/{id}/executar-pipeline
"""

from __future__ import annotations

import asyncio
import io
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.models import (
    Agencia,
    Ativacao,
    AtivacaoLead,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    StatusEvento,
    TipoLead,
    TipoResponsavel,
    Usuario,
)
from app.utils.security import hash_password


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    eng = _make_engine()
    SQLModel.metadata.create_all(eng)
    return eng


@pytest.fixture
def client(engine):
    def override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="gold@npbb.com.br",
        password_hash=hash_password("senha123"),
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_status(session: Session) -> StatusEvento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    if not status:
        status = StatusEvento(nome="Previsto")
        session.add(status)
        session.commit()
        session.refresh(status)
    return status


def _seed_evento(session: Session, *, agencia_id: int | None = None) -> Evento:
    ev_status = _seed_status(session)
    evento = Evento(
        nome="Park Challenge 2025",
        cidade="SP",
        estado="SP",
        status_id=ev_status.id,
        agencia_id=agencia_id,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _seed_agencia(session: Session) -> Agencia:
    ag = Agencia(nome="Agencia Teste", dominio="ag-teste-import.npbb", lote=1)
    session.add(ag)
    session.commit()
    session.refresh(ag)
    return ag


def _auth_header(client: TestClient, session: Session) -> dict[str, str]:
    _seed_user(session)
    resp = client.post("/auth/login", json={"email": "gold@npbb.com.br", "password": "senha123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


CSV_CONTENT = b"nome,cpf,email,telefone\nAlice,12345678901,alice@ex.com,11999990000\n"


def _upload_batch(
    client: TestClient,
    auth: dict,
    plataforma: str = "email",
    *,
    evento_id: int | None = None,
    origem_lote: str | None = None,
    ativacao_id: int | None = None,
    tipo_lead_proponente: str | None = None,
) -> int:
    data: dict[str, str] = {
        "plataforma_origem": plataforma,
        "data_envio": "2026-03-05T10:00:00",
    }
    if evento_id is not None:
        data["evento_id"] = str(evento_id)
    if origem_lote is not None:
        data["origem_lote"] = origem_lote
    if ativacao_id is not None:
        data["ativacao_id"] = str(ativacao_id)
    if tipo_lead_proponente is not None:
        data["tipo_lead_proponente"] = tipo_lead_proponente

    resp = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
        data=data,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _promote_to_silver(engine, batch_id: int, evento_id: int) -> None:
    """Directly set batch to silver stage and add a silver row."""
    with Session(engine) as s:
        batch = s.get(LeadBatch, batch_id)
        batch.stage = BatchStage.SILVER
        batch.evento_id = evento_id
        s.add(batch)
        silver = LeadSilver(
            batch_id=batch_id,
            row_index=0,
            evento_id=evento_id,
            dados_brutos={
                "nome": "Alice",
                "cpf": "12345678901",
                "email": "alice@ex.com",
                "telefone": "11999990000",
                "evento": "Park Challenge 2025",
                "tipo_evento": "ESPORTE",
                "local": "Sao Paulo-SP",
                "data_evento": "2026-06-08",
                "data_nascimento": "1990-01-15",
            },
        )
        s.add(silver)
        s.commit()


class TestGetBatch:
    def test_returns_batch_info(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth)
        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == batch_id
        assert body["stage"] == "bronze"
        assert body["pipeline_status"] == "pending"

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.get("/leads/batches/9999", headers=auth)
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.get("/leads/batches/1")
        assert resp.status_code == 401

    def test_returns_pipeline_report_when_present(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        fake_report = {"gate": {"status": "PASS", "decision": "promote", "fail_reasons": [], "warnings": []}}
        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            batch.pipeline_report = fake_report
            batch.pipeline_status = PipelineStatus.PASS
            batch.stage = BatchStage.GOLD
            s.add(batch)
            s.commit()

        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_report"]["gate"]["status"] == "PASS"
        assert body["stage"] == "gold"


class TestExecutarPipeline:
    def test_returns_400_if_stage_not_silver(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth)
        resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)
        assert resp.status_code == 400
        body = resp.json()
        assert body["detail"]["code"] == "INVALID_STAGE"

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.post("/leads/batches/9999/executar-pipeline", headers=auth)
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.post("/leads/batches/1/executar-pipeline")
        assert resp.status_code == 401

    def test_queues_pipeline_for_silver_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        with patch(
            "app.routers.leads.executar_pipeline_gold",
            new_callable=AsyncMock,
        ):
            resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert resp.status_code == 202, resp.text
        body = resp.json()
        assert body["batch_id"] == batch_id
        assert body["status"] == "queued"


class TestLeadEventoInGoldPipeline:
    """Guarantee LeadEvento creation and idempotency in the Gold pipeline."""

    def test_promote_to_gold_creates_lead_evento(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id)).all()
            assert len(leads) > 0, "Deve ter criado pelo menos um Lead Gold"

            for lead in leads:
                lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
                assert len(lead_eventos) == 1, f"Lead {lead.id} deve ter exatamente 1 LeadEvento"
                lead_evento = lead_eventos[0]
                assert lead_evento.evento_id == evento.id
                assert lead_evento.source_kind == LeadEventoSourceKind.LEAD_BATCH
                assert lead_evento.source_ref_id == batch_id
                assert lead_evento.tipo_lead == TipoLead.ENTRADA_EVENTO
                assert lead_evento.responsavel_tipo == TipoResponsavel.PROPONENTE
                assert lead_evento.responsavel_nome == evento.nome
                assert lead_evento.responsavel_agencia_id is None

    def test_promote_to_gold_activation_batch_creates_ativacao_lead_and_lead_evento(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            agencia = _seed_agencia(s)
            evento = _seed_evento(s, agencia_id=agencia.id)
            ativacao = Ativacao(nome="Stand import", evento_id=evento.id)
            s.add(ativacao)
            s.commit()
            s.refresh(ativacao)
            evento_id = evento.id
            ativacao_id = ativacao.id

        batch_id = _upload_batch(
            client,
            auth,
            evento_id=evento_id,
            origem_lote="ativacao",
            ativacao_id=ativacao_id,
        )
        _promote_to_silver(engine, batch_id, evento_id)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id)).all()
            assert len(leads) > 0
            for lead in leads:
                al = s.exec(
                    select(AtivacaoLead)
                    .where(AtivacaoLead.ativacao_id == ativacao_id)
                    .where(AtivacaoLead.lead_id == lead.id)
                ).first()
                assert al is not None
                lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
                assert len(lead_eventos) == 1
                le = lead_eventos[0]
                assert le.evento_id == evento_id
                assert le.source_kind == LeadEventoSourceKind.ACTIVATION
                assert le.source_ref_id == al.id
                assert le.tipo_lead == TipoLead.ATIVACAO
                assert le.responsavel_tipo == TipoResponsavel.AGENCIA

    def test_reprocess_does_not_duplicate_lead_evento(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))
        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id)).all()
            for lead in leads:
                lead_eventos = s.exec(
                    select(LeadEvento)
                    .where(LeadEvento.lead_id == lead.id)
                    .where(LeadEvento.evento_id == evento.id)
                ).all()
                assert len(lead_eventos) == 1, "Nao deve duplicar LeadEvento"
