from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.etl_registry import IngestionRun as RegistryIngestionRun
from app.models.etl_registry import IngestionStatus as RegistryIngestionStatus
from app.models.etl_registry import Source as RegistrySource
from app.models.etl_registry import SourceKind as RegistrySourceKind
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


def seed_user(engine, *, email: str, password: str, tipo_usuario: str):
    with Session(engine) as session:
        user = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario=tipo_usuario,
            ativo=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def login(client: TestClient, *, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def seed_catalog_data(engine) -> None:
    with Session(engine) as session:
        src_a = RegistrySource(
            source_id="SRC_A_PDF",
            kind=RegistrySourceKind.PDF,
            uri="file:///tmp/a.pdf",
            display_name="a.pdf",
        )
        src_b = RegistrySource(
            source_id="SRC_B_XLSX",
            kind=RegistrySourceKind.XLSX,
            uri="file:///tmp/b.xlsx",
            display_name="b.xlsx",
        )
        src_c = RegistrySource(
            source_id="SRC_C_CSV",
            kind=RegistrySourceKind.CSV,
            uri="file:///tmp/c.csv",
            display_name="c.csv",
        )
        session.add(src_a)
        session.add(src_b)
        session.add(src_c)
        session.commit()
        session.refresh(src_a)
        session.refresh(src_b)

        t0 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
        t1 = datetime(2025, 12, 12, 21, 0, tzinfo=timezone.utc)
        t2 = datetime(2025, 12, 12, 22, 0, tzinfo=timezone.utc)

        session.add(
            RegistryIngestionRun(
                source_pk=src_a.id,
                status=RegistryIngestionStatus.PARTIAL,
                started_at=t0,
                finished_at=t0,
                extractor_name="extract_pdf_old",
                notes="partial old",
            )
        )
        session.add(
            RegistryIngestionRun(
                source_pk=src_a.id,
                status=RegistryIngestionStatus.SUCCESS,
                started_at=t1,
                finished_at=t1,
                extractor_name="extract_pdf_new",
                notes="success new",
            )
        )
        session.add(
            RegistryIngestionRun(
                source_pk=src_b.id,
                status=RegistryIngestionStatus.FAILED,
                started_at=t2,
                finished_at=t2,
                extractor_name="extract_xlsx",
                notes="failed xlsx",
            )
        )
        session.commit()


def test_internal_catalog_requires_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    resp = client.get("/internal/catalog/sources", headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.get("/internal/catalog/ingestions", headers=auth_headers(token))
    assert resp.status_code == 403


def test_internal_catalog_sources_and_ingestions_with_filters(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_catalog_data(engine)

    resp = client.get("/internal/catalog/sources", headers=auth_headers(token))
    assert resp.status_code == 200
    sources = resp.json()
    assert [item["source_id"] for item in sources] == ["SRC_A_PDF", "SRC_B_XLSX", "SRC_C_CSV"]
    by_source = {item["source_id"]: item for item in sources}
    assert by_source["SRC_A_PDF"]["latest_status"] == "success"
    assert by_source["SRC_A_PDF"]["latest_extractor_name"] == "extract_pdf_new"
    assert by_source["SRC_C_CSV"]["latest_ingestion_id"] is None

    resp = client.get(
        "/internal/catalog/sources?status=success",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert [item["source_id"] for item in resp.json()] == ["SRC_A_PDF"]

    resp = client.get(
        "/internal/catalog/sources?source_type=xlsx",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert [item["source_id"] for item in resp.json()] == ["SRC_B_XLSX"]

    resp = client.get("/internal/catalog/ingestions", headers=auth_headers(token))
    assert resp.status_code == 200
    ingestions = resp.json()
    assert [item["source_id"] for item in ingestions] == ["SRC_B_XLSX", "SRC_A_PDF", "SRC_A_PDF"]
    assert ingestions[0]["status"] == "failed"
    assert ingestions[0]["ingestion_id"] is not None
    assert ingestions[0]["started_at"] is not None
    assert ingestions[0]["created_at"] is not None

    resp = client.get(
        "/internal/catalog/ingestions?status=failed",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    failed_only = resp.json()
    assert len(failed_only) == 1
    assert failed_only[0]["source_id"] == "SRC_B_XLSX"
    assert failed_only[0]["status"] == "failed"

    resp = client.get(
        "/internal/catalog/ingestions?source_type=pdf",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    pdf_runs = resp.json()
    assert len(pdf_runs) == 2
    assert {item["status"] for item in pdf_runs} == {"success", "partial"}

    resp = client.get(
        "/internal/catalog/ingestions?source_id=SRC_A_PDF&limit=1&offset=1",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    page = resp.json()
    assert len(page) == 1
    assert page[0]["source_id"] == "SRC_A_PDF"
    assert page[0]["status"] == "partial"
