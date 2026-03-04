"""Tests for Lead Batch (Bronze) endpoints."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.models import Usuario
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


CSV_CONTENT = b"nome,email,cpf\nAlice,alice@ex.com,12345678901\nBob,bob@ex.com,98765432100\n"


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
        assert body["nome_arquivo_original"] == "leads.csv"
        assert body["plataforma_origem"] == "email"
        assert body["id"] is not None

    def test_upload_xlsx_creates_batch(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["nome", "email"])
        ws.append(["Alice", "alice@ex.com"])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        resp = client.post(
            "/leads/batches",
            headers=headers,
            files={"file": ("leads.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
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

    def test_preview_not_found(self, client, engine):
        with Session(engine) as s:
            headers = _auth_header(client, s)

        resp = client.get("/leads/batches/9999/preview", headers=headers)
        assert resp.status_code == 404

    def test_preview_requires_auth(self, client):
        resp = client.get("/leads/batches/1/preview")
        assert resp.status_code == 401
