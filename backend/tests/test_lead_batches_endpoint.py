from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Usuario
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


def seed_user(engine, email="batch@example.com", password="[REDACTED]") -> Usuario:
    with Session(engine) as session:
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


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _make_xlsx_bytes() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["Email", "CPF"])
    ws.append(["xlsx@example.com", "12345678901"])
    output = BytesIO()
    wb.save(output)
    return output.getvalue()


def test_post_lead_batch_csv_and_get_raw_file(client: TestClient, engine) -> None:
    user = seed_user(engine)
    token = login_and_get_token(client, user.email, "[REDACTED]")
    auth = {"Authorization": f"Bearer {token}"}

    csv_bytes = b"Email;CPF\ncsv@example.com;12345678901\n"
    upload = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", BytesIO(csv_bytes), "text/csv")},
        data={"plataforma_origem": "email", "data_envio": "2026-03-04T10:15:00Z"},
    )

    assert upload.status_code == 201
    payload = upload.json()
    assert payload["batch_id"]
    assert payload["stage"] == "bronze"
    assert payload["pipeline_status"] == "pending"

    batch_id = payload["batch_id"]
    raw = client.get(f"/leads/batches/{batch_id}/arquivo", headers=auth)
    assert raw.status_code == 200
    assert raw.content == csv_bytes
    assert "attachment;" in raw.headers.get("content-disposition", "")

    with Session(engine) as session:
        batch = session.get(LeadBatch, batch_id)
        assert batch is not None
        assert batch.stage == BatchStage.BRONZE
        assert batch.pipeline_status == PipelineStatus.PENDING
        assert batch.nome_arquivo_original == "leads.csv"
        assert batch.arquivo_bronze == csv_bytes


def test_post_lead_batch_xlsx_returns_bronze_pending(client: TestClient, engine) -> None:
    user = seed_user(engine, email="xlsx@example.com")
    token = login_and_get_token(client, user.email, "[REDACTED]")
    auth = {"Authorization": f"Bearer {token}"}
    xlsx_bytes = _make_xlsx_bytes()

    upload = client.post(
        "/leads/batches",
        headers=auth,
        files={
            "file": (
                "leads.xlsx",
                BytesIO(xlsx_bytes),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        data={"plataforma_origem": "manual", "data_envio": "2026-03-04T10:15:00Z"},
    )

    assert upload.status_code == 201
    payload = upload.json()
    assert payload["stage"] == "bronze"
    assert payload["pipeline_status"] == "pending"


def test_lead_batch_endpoints_require_auth(client: TestClient, engine) -> None:
    csv_bytes = b"Email;CPF\nanon@example.com;12345678901\n"
    upload = client.post(
        "/leads/batches",
        files={"file": ("leads.csv", BytesIO(csv_bytes), "text/csv")},
        data={"plataforma_origem": "email", "data_envio": "2026-03-04T10:15:00Z"},
    )
    assert upload.status_code == 401

    user = seed_user(engine, email="authget@example.com")
    token = login_and_get_token(client, user.email, "[REDACTED]")
    auth = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", BytesIO(csv_bytes), "text/csv")},
        data={"plataforma_origem": "email", "data_envio": "2026-03-04T10:15:00Z"},
    )
    batch_id = created.json()["batch_id"]

    client.cookies.clear()
    raw = client.get(f"/leads/batches/{batch_id}/arquivo")
    assert raw.status_code == 401
