"""Tests for Lead Batch (Bronze) endpoints."""

from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import (
    Agencia,
    Ativacao,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    StatusEvento,
    Usuario,
)
from app.schemas.lead_batch import LeadBatchIntakeRequest
from app.services import lead_batch_intake_service
from app.services.imports.contracts import ImportPreviewResult
from app.services.imports.payload_storage import PayloadStorageError, persist_batch_payload_file
from app.services.imports.upload_spool import spool_upload_payload
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
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.delenv("PUBLIC_APP_BASE_URL", raising=False)
    monkeypatch.setenv("OBJECT_STORAGE_BACKEND", "local")
    monkeypatch.setenv(
        "OBJECT_STORAGE_LOCAL_ROOT",
        str(Path.cwd() / "test-object-storage" / uuid4().hex),
    )
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


def _seed_user(session: Session, email="batch@npbb.com.br", password="senha123") -> Usuario:
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


def _auth_header_for_user(
    client: TestClient,
    *,
    email: str,
    password: str,
) -> dict[str, str]:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _auth_header(client: TestClient, session: Session) -> dict[str, str]:
    _seed_user(session)
    return _auth_header_for_user(client, email="batch@npbb.com.br", password="senha123")


def _seed_agencia(session: Session) -> Agencia:
    ag = Agencia(nome="Agencia batch", dominio="ag-batch-test.npbb", lote=1)
    session.add(ag)
    session.commit()
    session.refresh(ag)
    return ag


def _seed_evento(session: Session, nome: str = "Evento batch test", agencia_id: int | None = None) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    if status is None:
        status = StatusEvento(nome="Previsto")
        session.add(status)
        session.commit()
        session.refresh(status)
    evento = Evento(nome=nome, cidade="SP", estado="SP", status_id=status.id, agencia_id=agencia_id)
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


CSV_CONTENT = b"nome,email,cpf\nAlice,alice@ex.com,12345678901\nBob,bob@ex.com,98765432100\n"
CSV_CONTENT_WITH_PREAMBLE = (
    b"linha solta 1,,\n"
    b"linha solta 2,,\n"
    b"linha solta 3,,\n"
    b"linha solta 4,,\n"
    b"linha solta 5,,\n"
    b"linha solta 6,,\n"
    b"linha solta 7,,\n"
    b"linha solta 8,,\n"
    b"nome,email,cpf\n"
    b"Alice,alice@ex.com,12345678901\n"
    b"Bob,bob@ex.com,98765432100\n"
)
INVALID_XLSX_CONTENT = b"nao-e-um-xlsx-valido"


class TrackingBytesIO(io.BytesIO):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes)
        self.read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        if size < 0:
            raise AssertionError("unbounded read() is not allowed in chunked upload spooling")
        return super().read(size)


def _make_non_xlsx_zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0" encoding="UTF-8"?>')
        zf.writestr("_rels/.rels", b'<?xml version="1.0" encoding="UTF-8"?>')
        zf.writestr("word/document.xml", b"<w:document />")
    return buf.getvalue()


def _make_xlsx_bytes() -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.append(["nome", "email"])
    ws.append(["Alice", "alice@ex.com"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def _make_xlsx_bytes_with_preamble() -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    for idx in range(8):
        ws.append([f"linha solta {idx + 1}", "", ""])
    ws.append(["nome", "email", "cpf"])
    ws.append(["Alice", "alice@ex.com", "12345678901"])
    ws.append(["Bob", "bob@ex.com", "98765432100"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def _seed_lead_batch(
    session: Session,
    *,
    user_id: int,
    arquivo_sha256: str | None,
    plataforma_origem: str = "email",
    data_envio: datetime | None = None,
    created_at: datetime | None = None,
    nome_arquivo_original: str = "leads.csv",
    evento_id: int | None = None,
    origem_lote: str | None = "proponente",
    enrichment_only: bool = False,
    tipo_lead_proponente: str | None = "entrada_evento",
    ativacao_id: int | None = None,
) -> LeadBatch:
    batch = LeadBatch(
        enviado_por=user_id,
        plataforma_origem=plataforma_origem,
        data_envio=data_envio or datetime(2026, 3, 1, 10, 0, 0),
        nome_arquivo_original=nome_arquivo_original,
        arquivo_sha256=arquivo_sha256,
        arquivo_bronze=CSV_CONTENT,
        stage=BatchStage.BRONZE,
        evento_id=evento_id,
        origem_lote=origem_lote,
        enrichment_only=enrichment_only,
        tipo_lead_proponente=tipo_lead_proponente,
        ativacao_id=ativacao_id,
        pipeline_status=PipelineStatus.PENDING,
        created_at=created_at or datetime.now(timezone.utc),
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


class TestLeadBatchPayloadStorage:
    def test_spool_upload_payload_reads_in_bounded_chunks(self):
        payload = b"nome,email\n" + (b"Alice,alice@example.com\n" * 4)
        tracked_file = TrackingBytesIO(payload)
        upload = UploadFile(file=tracked_file, filename="leads.csv")

        spooled = spool_upload_payload(upload, max_bytes=1024, chunk_size=7)
        try:
            assert spooled.sha256 == hashlib.sha256(payload).hexdigest()
            assert spooled.size_bytes == len(payload)
            assert spooled.file.read() == payload
            assert tracked_file.read_sizes
            assert all(size == 7 for size in tracked_file.read_sizes[:-1])
            assert tracked_file.read_sizes[-1] == 7
        finally:
            spooled.close()

    def test_local_storage_backend_is_blocked_in_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("OBJECT_STORAGE_BACKEND", "local")
        monkeypatch.delenv("PUBLIC_APP_BASE_URL", raising=False)
        batch = LeadBatch(
            enviado_por=1,
            plataforma_origem="email",
            data_envio=datetime(2026, 3, 1, 10, 0, 0),
            nome_arquivo_original="leads.csv",
            arquivo_sha256=hashlib.sha256(CSV_CONTENT).hexdigest(),
            stage=BatchStage.BRONZE,
            pipeline_status=PipelineStatus.PENDING,
        )

        with pytest.raises(PayloadStorageError, match="OBJECT_STORAGE_BACKEND=local nao e permitido"):
            persist_batch_payload_file(
                batch,
                io.BytesIO(CSV_CONTENT),
                size_bytes=len(CSV_CONTENT),
                content_type="text/csv",
            )


class TestPostLeadsBatches:
    def test_batch_intake_creates_multiple_batches(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches/intake",
            headers=headers,
            data={
                "manifest_json": json.dumps(
                    {
                        "items": [
                            {
                                "client_row_id": "row-a",
                                "plataforma_origem": "email",
                                "data_envio": "2026-03-01T10:00:00",
                                "file_name": "leads-a.csv",
                            },
                            {
                                "client_row_id": "row-b",
                                "plataforma_origem": "manual",
                                "data_envio": "2026-03-02T11:30:00",
                                "file_name": "leads-b.csv",
                            },
                        ]
                    },
                    ensure_ascii=False,
                )
            },
            files=[
                ("files", ("leads-a.csv", io.BytesIO(CSV_CONTENT), "text/csv")),
                ("files", ("leads-b.csv", io.BytesIO(CSV_CONTENT), "text/csv")),
            ],
        )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert [item["client_row_id"] for item in body["items"]] == ["row-a", "row-b"]
        assert [item["batch"]["nome_arquivo_original"] for item in body["items"]] == [
            "leads-a.csv",
            "leads-b.csv",
        ]
        assert all(item["batch"]["id"] is not None for item in body["items"])
        assert all(item["preview"]["headers"] == ["nome", "email", "cpf"] for item in body["items"])

    def test_batch_intake_accepts_enrichment_only_manifest(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches/intake",
            headers=headers,
            data={
                "manifest_json": json.dumps(
                    {
                        "items": [
                            {
                                "client_row_id": "row-enrichment",
                                "plataforma_origem": "email",
                                "data_envio": "2026-03-01T10:00:00",
                                "file_name": "leads.csv",
                                "enrichment_only": True,
                            }
                        ]
                    },
                    ensure_ascii=False,
                )
            },
            files=[
                ("files", ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")),
            ],
        )

        assert resp.status_code == 201, resp.text
        item = resp.json()["items"][0]
        assert item["client_row_id"] == "row-enrichment"
        assert item["batch"]["enrichment_only"] is True
        assert item["batch"]["evento_id"] is None
        assert item["batch"]["origem_lote"] is None

    def test_batch_intake_accepts_enrichment_only_tipo_without_origem(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches/intake",
            headers=headers,
            data={
                "manifest_json": json.dumps(
                    {
                        "items": [
                            {
                                "client_row_id": "row-enrichment",
                                "plataforma_origem": "email",
                                "data_envio": "2026-03-01T10:00:00",
                                "file_name": "leads.csv",
                                "enrichment_only": True,
                                "tipo_lead_proponente": "bilheteria",
                            }
                        ]
                    },
                    ensure_ascii=False,
                )
            },
            files=[
                ("files", ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")),
            ],
        )

        assert resp.status_code == 201, resp.text
        item = resp.json()["items"][0]
        assert item["batch"]["origem_lote"] is None
        assert item["batch"]["tipo_lead_proponente"] == "bilheteria"

    def test_upload_csv_creates_batch(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["stage"] == "bronze"
        assert body["pipeline_status"] == "pending"
        assert body["pipeline_progress"] is None
        assert body["nome_arquivo_original"] == "leads.csv"
        assert body["arquivo_sha256"] == hashlib.sha256(CSV_CONTENT).hexdigest()
        assert body["plataforma_origem"] == "email"
        assert body["id"] is not None
        assert body.get("origem_lote") == "proponente"
        assert body.get("enrichment_only") is False
        assert body.get("ativacao_id") is None

        with Session(engine) as s:
            batch = s.get(LeadBatch, body["id"])
            assert batch is not None
            assert batch.arquivo_bronze is None
            assert batch.bronze_storage_bucket == "lead-imports"
            assert batch.bronze_storage_key
            assert batch.bronze_content_type == "text/csv"
            assert batch.bronze_size_bytes == len(CSV_CONTENT)
            stored_path = (
                Path(os.environ["OBJECT_STORAGE_LOCAL_ROOT"])
                / batch.bronze_storage_bucket
                / batch.bronze_storage_key
            )
            assert stored_path.read_bytes() == CSV_CONTENT

    def test_upload_enrichment_only_without_evento_is_accepted(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "enrichment_only": "true",
            },
        )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["evento_id"] is None
        assert body["enrichment_only"] is True
        assert body["origem_lote"] is None

    def test_upload_enrichment_only_keeps_explicit_legacy_proponente(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "origem_lote": "proponente",
                "enrichment_only": "true",
                "tipo_lead_proponente": "entrada_evento",
            },
        )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["enrichment_only"] is True
        assert body["origem_lote"] == "proponente"
        assert body["tipo_lead_proponente"] == "entrada_evento"

    def test_upload_enrichment_only_rejects_evento_id(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            evento = _seed_evento(s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": str(evento.id),
                "enrichment_only": "true",
            },
        )

        assert resp.status_code == 400
        assert resp.json()["detail"]["code"] == "ENRICHMENT_ONLY_EVENTO_NOT_ALLOWED"

    def test_upload_enrichment_only_rejects_origem_ativacao(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "origem_lote": "ativacao",
                "enrichment_only": "true",
            },
        )

        assert resp.status_code == 400
        assert resp.json()["detail"]["code"] == "ENRICHMENT_ONLY_ORIGEM_INVALIDA"

    def test_upload_enrichment_only_rejects_ativacao_id(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "enrichment_only": "true",
                "ativacao_id": "1",
            },
        )

        assert resp.status_code == 400
        assert resp.json()["detail"]["code"] == "ENRICHMENT_ONLY_ATIVACAO_NOT_ALLOWED"

    def test_upload_origem_ativacao_requires_ativacao_id(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ag = _seed_agencia(s)
            ev = _seed_evento(s, agencia_id=ag.id)
            evento_id = ev.id

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": str(evento_id),
                "origem_lote": "ativacao",
            },
        )
        assert resp.status_code == 400
        assert resp.json()["detail"].get("code") == "ATIVACAO_REQUIRED"

    def test_upload_origem_ativacao_rejects_evento_mismatch(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ag = _seed_agencia(s)
            ev1 = _seed_evento(s, nome="Ev1", agencia_id=ag.id)
            ev2 = _seed_evento(s, nome="Ev2", agencia_id=ag.id)
            ativ = Ativacao(nome="Stand", evento_id=ev1.id)
            s.add(ativ)
            s.commit()
            s.refresh(ativ)
            evento_id = ev2.id
            ativacao_id = ativ.id

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": str(evento_id),
                "origem_lote": "ativacao",
                "ativacao_id": str(ativacao_id),
            },
        )
        assert resp.status_code == 400
        assert resp.json()["detail"].get("code") == "ATIVACAO_EVENTO_MISMATCH"

    def test_upload_origem_ativacao_rejects_evento_without_agencia(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ev = _seed_evento(s, agencia_id=None)
            ativ = Ativacao(nome="Stand sem agencia", evento_id=ev.id)
            s.add(ativ)
            s.commit()
            s.refresh(ativ)
            evento_id = ev.id
            ativacao_id = ativ.id

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": str(evento_id),
                "origem_lote": "ativacao",
                "ativacao_id": str(ativacao_id),
            },
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert detail.get("code") == "EVENTO_AGENCIA_REQUIRED_FOR_ATIVACAO_IMPORT"
        assert detail.get("message") == "Vincule uma agencia ao evento antes de importar leads de ativacao."

    def test_upload_origem_ativacao_persists(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ag = _seed_agencia(s)
            ev = _seed_evento(s, agencia_id=ag.id)
            ativ = Ativacao(nome="Stand OK", evento_id=ev.id)
            s.add(ativ)
            s.commit()
            s.refresh(ativ)
            evento_id = ev.id
            ativacao_id = ativ.id

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": str(evento_id),
                "origem_lote": "ativacao",
                "ativacao_id": str(ativacao_id),
            },
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["origem_lote"] == "ativacao"
        assert body["ativacao_id"] == ativacao_id

    def test_upload_csv_with_evento_id_persists_on_batch(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ev = _seed_evento(s)
            evento_id = ev.id

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": str(evento_id),
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["evento_id"] == evento_id

        get_resp = client.get(f"/leads/batches/{body['id']}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["evento_id"] == evento_id

    def test_listar_referencia_eventos_includes_activation_import_metadata(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ag = _seed_agencia(s)
            evento_supported = _seed_evento(s, nome="Evento com agencia", agencia_id=ag.id)
            evento_blocked = _seed_evento(s, nome="Evento sem agencia", agencia_id=None)
            supported_evento_id = evento_supported.id
            blocked_evento_id = evento_blocked.id
            agencia_id = ag.id

        resp = client.get("/leads/referencias/eventos", headers=headers)
        assert resp.status_code == 200

        body = resp.json()
        by_id = {row["id"]: row for row in body}

        assert by_id[supported_evento_id]["agencia_id"] == agencia_id
        assert by_id[supported_evento_id]["supports_activation_import"] is True
        assert by_id[supported_evento_id]["activation_import_block_reason"] is None
        assert by_id[supported_evento_id]["leads_count"] == 0

        assert by_id[blocked_evento_id]["agencia_id"] is None
        assert by_id[blocked_evento_id]["supports_activation_import"] is False
        assert (
            by_id[blocked_evento_id]["activation_import_block_reason"]
            == "Vincule uma agencia ao evento antes de importar leads de ativacao."
        )
        assert by_id[blocked_evento_id]["leads_count"] == 0

    def test_listar_referencia_eventos_includes_leads_count_from_lead_evento(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)
            ev_with_lead = _seed_evento(s, nome="Evento com lead vinculado")
            ev_without_lead = _seed_evento(s, nome="Evento sem lead vinculado")
            lead = Lead()
            s.add(lead)
            s.commit()
            s.refresh(lead)
            s.add(
                LeadEvento(
                    lead_id=lead.id,
                    evento_id=ev_with_lead.id,
                    source_kind=LeadEventoSourceKind.EVENT_DIRECT,
                )
            )
            s.commit()
            with_lead_id = ev_with_lead.id
            without_lead_id = ev_without_lead.id

        resp = client.get("/leads/referencias/eventos", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        by_id = {row["id"]: row for row in body}
        assert by_id[with_lead_id]["leads_count"] == 1
        assert by_id[without_lead_id]["leads_count"] == 0

    def test_upload_rejects_unknown_evento_id(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={
                "plataforma_origem": "email",
                "data_envio": "2026-03-01T10:00:00",
                "evento_id": "99999",
            },
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert detail.get("code") == "EVENTO_NOT_FOUND"

    def test_upload_accepts_date_only_iso_string(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["stage"] == "bronze"
        assert body["data_envio"].startswith("2026-03-01")

    def test_upload_xlsx_creates_batch(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={
                "file": (
                    "leads.xlsx",
                    _make_xlsx_bytes(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            data={"plataforma_origem": "manual", "data_envio": "2026-03-01T10:00:00"},
        )
        assert resp.status_code == 201
        assert resp.json()["nome_arquivo_original"] == "leads.xlsx"

    def test_rejects_invalid_extension(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        assert resp.status_code == 400

    def test_rejects_empty_file(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        assert resp.status_code == 400

    def test_requires_auth(self, client):
        resp = client.post(
            "/leads/batches",
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        assert resp.status_code == 401


class TestGetLeadBatchImportHint:
    def test_returns_latest_match_for_same_user(self, client, engine):
        arquivo_sha256 = hashlib.sha256(CSV_CONTENT).hexdigest()
        older_created_at = datetime(2026, 3, 1, 8, 0, 0, tzinfo=timezone.utc)
        newer_created_at = datetime(2026, 3, 2, 9, 30, 0, tzinfo=timezone.utc)

        with Session(engine) as s:
            user = _seed_user(s)
            headers = _auth_header_for_user(client, email=user.email, password="senha123")
            ag = _seed_agencia(s)
            evento = _seed_evento(s, agencia_id=ag.id)
            evento_id = evento.id
            ativacao = Ativacao(nome="Stand hint", evento_id=evento.id)
            s.add(ativacao)
            s.commit()
            s.refresh(ativacao)
            ativacao_id = ativacao.id

            _seed_lead_batch(
                s,
                user_id=user.id,
                arquivo_sha256=arquivo_sha256,
                plataforma_origem="email",
                data_envio=datetime(2026, 3, 1, 10, 0, 0),
                created_at=older_created_at,
                evento_id=evento_id,
                origem_lote="proponente",
                tipo_lead_proponente="entrada_evento",
            )
            latest_batch = _seed_lead_batch(
                s,
                user_id=user.id,
                arquivo_sha256=arquivo_sha256,
                plataforma_origem="facebook",
                data_envio=datetime(2026, 3, 2, 15, 45, 0),
                created_at=newer_created_at,
                evento_id=evento_id,
                origem_lote="ativacao",
                tipo_lead_proponente=None,
                ativacao_id=ativacao_id,
            )

        resp = client.get(
            f"/leads/batches/import-hint?arquivo_sha256={arquivo_sha256.upper()}",
            headers=headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["arquivo_sha256"] == arquivo_sha256
        assert body["source_batch_id"] == latest_batch.id
        assert body["plataforma_origem"] == "facebook"
        assert body["origem_lote"] == "ativacao"
        assert body["enrichment_only"] is False
        assert body["tipo_lead_proponente"] is None
        assert body["evento_id"] == evento_id
        assert body["ativacao_id"] == ativacao_id
        assert body["confidence"] == "exact_hash_match"
        assert body["data_envio"].startswith("2026-03-02T15:45:00")
        assert body["source_created_at"].startswith("2026-03-02T09:30:00")

    def test_import_hint_preserves_null_origem_for_enrichment_only(self, client, engine):
        arquivo_sha256 = hashlib.sha256(CSV_CONTENT).hexdigest()
        created_at = datetime(2026, 3, 3, 9, 30, 0, tzinfo=timezone.utc)

        with Session(engine) as s:
            user = _seed_user(s)
            headers = _auth_header_for_user(client, email=user.email, password="senha123")
            batch = _seed_lead_batch(
                s,
                user_id=user.id,
                arquivo_sha256=arquivo_sha256,
                plataforma_origem="email",
                data_envio=datetime(2026, 3, 3, 15, 45, 0),
                created_at=created_at,
                evento_id=None,
                origem_lote=None,
                enrichment_only=True,
                tipo_lead_proponente="bilheteria",
            )

        resp = client.get(
            f"/leads/batches/import-hint?arquivo_sha256={arquivo_sha256}",
            headers=headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["source_batch_id"] == batch.id
        assert body["enrichment_only"] is True
        assert body["origem_lote"] is None
        assert body["tipo_lead_proponente"] == "bilheteria"
        assert body["evento_id"] is None
        assert body["ativacao_id"] is None

    def test_returns_204_when_no_match_exists(self, client, engine):
        arquivo_sha256 = hashlib.sha256(CSV_CONTENT).hexdigest()

        with Session(engine) as s:
            headers = _auth_header(client, s)
            user = s.exec(select(Usuario).where(Usuario.email == "batch@npbb.com.br")).one()
            _seed_lead_batch(
                s,
                user_id=user.id,
                arquivo_sha256=None,
                plataforma_origem="manual",
            )

        resp = client.get(
            f"/leads/batches/import-hint?arquivo_sha256={arquivo_sha256}",
            headers=headers,
        )

        assert resp.status_code == 204
        assert resp.content == b""

    def test_does_not_leak_match_from_other_user(self, client, engine):
        arquivo_sha256 = hashlib.sha256(CSV_CONTENT).hexdigest()

        with Session(engine) as s:
            user_a = _seed_user(s, email="user-a@npbb.com.br", password="senha-a")
            _seed_user(s, email="user-b@npbb.com.br", password="senha-b")
            headers = _auth_header_for_user(client, email="user-b@npbb.com.br", password="senha-b")
            _seed_lead_batch(
                s,
                user_id=user_a.id,
                arquivo_sha256=arquivo_sha256,
                plataforma_origem="email",
            )

        resp = client.get(
            f"/leads/batches/import-hint?arquivo_sha256={arquivo_sha256}",
            headers=headers,
        )

        assert resp.status_code == 204
        assert resp.content == b""

    def test_rejects_invalid_hash_with_400(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.get("/leads/batches/import-hint?arquivo_sha256=abc", headers=headers)

        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert detail["code"] == "INVALID_ARQUIVO_SHA256"
        assert detail["field"] == "arquivo_sha256"


class TestLeadBatchIntakeService:
    def test_execute_intake_materializes_batch_read_before_commit(self, engine, monkeypatch):
        with Session(engine) as s:
            user = _seed_user(s)
            manifest = LeadBatchIntakeRequest.model_validate(
                {
                    "items": [
                        {
                            "client_row_id": "row-1",
                            "plataforma_origem": "email",
                            "data_envio": "2026-03-01T10:00:00",
                            "file_name": "leads.csv",
                        }
                    ]
                }
            )
            upload = UploadFile(file=io.BytesIO(CSV_CONTENT), filename="leads.csv")

            commit_started = False
            original_commit = s.commit
            original_model_validate = lead_batch_intake_service.LeadBatchRead.model_validate

            def tracked_commit():
                nonlocal commit_started
                commit_started = True
                return original_commit()

            def guarded_model_validate(cls, obj, *args, **kwargs):
                assert commit_started is False
                return original_model_validate(obj, *args, **kwargs)

            monkeypatch.setattr(s, "commit", tracked_commit)
            monkeypatch.setattr(
                lead_batch_intake_service.LeadBatchRead,
                "model_validate",
                classmethod(guarded_model_validate),
            )

            response = lead_batch_intake_service.execute_lead_batch_intake(
                session=s,
                user_id=int(user.id),
                manifest=manifest,
                files=[upload],
                max_import_file_bytes=1024 * 1024,
            )

        assert response.items[0].client_row_id == "row-1"
        assert response.items[0].batch.nome_arquivo_original == "leads.csv"


class TestGetBatchArquivo:
    def test_download_returns_file(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/arquivo", headers=headers)
        assert resp.status_code == 200
        assert resp.content == CSV_CONTENT
        assert "leads.csv" in resp.headers.get("content-disposition", "")

    def test_download_not_found(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.get("/leads/batches/9999/arquivo", headers=headers)
        assert resp.status_code == 404

    def test_download_hides_batch_from_other_user(self, client, engine):
        with Session(engine) as s:
            _seed_user(s, email="owner@npbb.com.br", password="senha123")
            _seed_user(s, email="other@npbb.com.br", password="senha456")

        owner_headers = _auth_header_for_user(client, email="owner@npbb.com.br", password="senha123")
        other_headers = _auth_header_for_user(client, email="other@npbb.com.br", password="senha456")

        upload_resp = client.post(
            "/leads/batches",
            headers=owner_headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/arquivo", headers=other_headers)
        assert resp.status_code == 404

    def test_download_requires_auth(self, client):
        resp = client.get("/leads/batches/1/arquivo")
        assert resp.status_code == 401


class TestGetBatchPreview:
    def test_preview_uses_windowed_reader(self, monkeypatch, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT_WITH_PREAMBLE), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        called = {"count": 0}

        def fake_preview(raw: bytes, *, filename: str, sample_rows: int) -> ImportPreviewResult:
            called["count"] += 1
            assert filename == "leads.csv"
            assert sample_rows == 3
            return ImportPreviewResult(
                filename=filename,
                headers=["nome", "email", "cpf"],
                rows=[["Alice", "alice@ex.com", "12345678901"]],
                delimiter=",",
                start_index=8,
                physical_line_numbers=[10],
            )

        monkeypatch.setattr("app.routers.leads.read_raw_file_preview", fake_preview)

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=headers)
        assert resp.status_code == 200
        assert called["count"] == 1
        assert resp.json() == {
            "headers": ["nome", "email", "cpf"],
            "rows": [["Alice", "alice@ex.com", "12345678901"]],
            "total_rows": 1,
        }

    def test_csv_preview(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["headers"] == ["nome", "email", "cpf"]
        assert len(body["rows"]) == 2
        assert body["total_rows"] == 2

    def test_xlsx_preview(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={
                "file": (
                    "leads.xlsx",
                    _make_xlsx_bytes(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            data={"plataforma_origem": "manual", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["headers"] == ["nome", "email"]
        assert body["rows"] == [["Alice", "alice@ex.com"]]
        assert body["total_rows"] == 1

    def test_csv_preview_skips_preamble_rows(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT_WITH_PREAMBLE), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["headers"] == ["nome", "email", "cpf"]
        assert body["rows"] == [
            ["Alice", "alice@ex.com", "12345678901"],
            ["Bob", "bob@ex.com", "98765432100"],
        ]
        assert body["total_rows"] == 2

    def test_xlsx_preview_skips_preamble_rows(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={
                "file": (
                    "leads.xlsx",
                    _make_xlsx_bytes_with_preamble(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            data={"plataforma_origem": "manual", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["headers"] == ["nome", "email", "cpf"]
        assert body["rows"] == [
            ["Alice", "alice@ex.com", "12345678901"],
            ["Bob", "bob@ex.com", "98765432100"],
        ]
        assert body["total_rows"] == 2

    def test_invalid_xlsx_rejected_at_upload(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={
                "file": (
                    "corrompido.xlsx",
                    io.BytesIO(INVALID_XLSX_CONTENT),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            data={"plataforma_origem": "manual", "data_envio": "2026-03-01T10:00:00"},
        )
        assert upload_resp.status_code == 400
        detail = upload_resp.json()["detail"]
        assert detail.get("code") == "INVALID_FILE_CONTENT"

    def test_non_xlsx_zip_rejected_at_upload(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        upload_resp = client.post(
            "/leads/batches",
            headers=headers,
            files={
                "file": (
                    "fake.xlsx",
                    io.BytesIO(_make_non_xlsx_zip_bytes()),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            data={"plataforma_origem": "manual", "data_envio": "2026-03-01T10:00:00"},
        )
        assert upload_resp.status_code == 400
        detail = upload_resp.json()["detail"]
        assert detail.get("code") == "INVALID_FILE_CONTENT"

    def test_preview_not_found(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.get("/leads/batches/9999/preview", headers=headers)
        assert resp.status_code == 404

    def test_preview_hides_batch_from_other_user(self, client, engine):
        with Session(engine) as s:
            _seed_user(s, email="preview-owner@npbb.com.br", password="senha123")
            _seed_user(s, email="preview-other@npbb.com.br", password="senha456")

        owner_headers = _auth_header_for_user(client, email="preview-owner@npbb.com.br", password="senha123")
        other_headers = _auth_header_for_user(client, email="preview-other@npbb.com.br", password="senha456")

        upload_resp = client.post(
            "/leads/batches",
            headers=owner_headers,
            files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
            data={"plataforma_origem": "email", "data_envio": "2026-03-01T10:00:00"},
        )
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=other_headers)
        assert resp.status_code == 404

    def test_preview_requires_auth(self, client):
        resp = client.get("/leads/batches/1/preview")
        assert resp.status_code == 401
