"""Tests for Lead Batch (Bronze) endpoints."""

from __future__ import annotations

import hashlib
import io

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
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
from app.services.imports.contracts import ImportPreviewResult
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


def _auth_header(client: TestClient, session: Session) -> dict[str, str]:
    _seed_user(session)
    resp = client.post("/auth/login", json={"email": "batch@npbb.com.br", "password": "senha123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


class TestPostLeadsBatches:
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
        assert body.get("ativacao_id") is None

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

    def test_invalid_xlsx_preview_returns_parse_error(self, client, engine):
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
        batch_id = upload_resp.json()["id"]

        resp = client.get(f"/leads/batches/{batch_id}/preview", headers=headers)
        assert resp.status_code == 422
        assert resp.json()["detail"] == {
            "code": "PREVIEW_PARSE_ERROR",
            "message": "Nao foi possivel ler o arquivo do lote para gerar o preview.",
        }

    def test_preview_not_found(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.get("/leads/batches/9999/preview", headers=headers)
        assert resp.status_code == 404

    def test_preview_requires_auth(self, client):
        resp = client.get("/leads/batches/1/preview")
        assert resp.status_code == 401
