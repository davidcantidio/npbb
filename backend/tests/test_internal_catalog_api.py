"""API tests for internal operational catalog endpoints."""

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
    """Create isolated in-memory SQLite engine for catalog API tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    """Provide isolated database engine for each test with auth secret configured."""
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine):
    """Provide API client bound to test database session dependency."""

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_user(engine, *, email: str, password: str, tipo_usuario: str):
    """Create one test user and return persisted model."""
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
    """Authenticate test user and return bearer token."""
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    """Build Authorization header for API calls."""
    return {"Authorization": f"Bearer {token}"}


def seed_catalog(engine) -> None:
    """Seed catalog sources and ingestions for filter/ordering assertions."""
    with Session(engine) as session:
        src_pdf = RegistrySource(
            source_id="SRC_PDF_01",
            kind=RegistrySourceKind.PDF,
            uri="file:///tmp/a.pdf",
            display_name="a.pdf",
        )
        src_xlsx = RegistrySource(
            source_id="SRC_XLSX_01",
            kind=RegistrySourceKind.XLSX,
            uri="file:///tmp/b.xlsx",
            display_name="b.xlsx",
        )
        src_csv = RegistrySource(
            source_id="SRC_CSV_01",
            kind=RegistrySourceKind.CSV,
            uri="file:///tmp/c.csv",
            display_name="c.csv",
        )
        session.add(src_pdf)
        session.add(src_xlsx)
        session.add(src_csv)
        session.commit()
        session.refresh(src_pdf)
        session.refresh(src_xlsx)

        t0 = datetime(2025, 12, 12, 19, 0, tzinfo=timezone.utc)
        t1 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
        t2 = datetime(2025, 12, 12, 21, 0, tzinfo=timezone.utc)

        session.add(
            RegistryIngestionRun(
                source_pk=src_pdf.id,
                status=RegistryIngestionStatus.PARTIAL,
                started_at=t0,
                extractor_name="extract_pdf_old",
                notes="partial",
            )
        )
        session.add(
            RegistryIngestionRun(
                source_pk=src_pdf.id,
                status=RegistryIngestionStatus.SUCCESS,
                started_at=t1,
                extractor_name="extract_pdf_new",
                notes="success",
            )
        )
        session.add(
            RegistryIngestionRun(
                source_pk=src_xlsx.id,
                status=RegistryIngestionStatus.FAILED,
                started_at=t2,
                extractor_name="extract_xlsx",
                notes="failed",
            )
        )
        session.commit()


def test_internal_catalog_api_requires_npbb_user(client: TestClient, engine) -> None:
    """Catalog API must reject authenticated users that are not NPBB."""
    bb = seed_user(engine, email="bb@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    resp_sources = client.get("/internal/catalog/sources", headers=auth_headers(token))
    resp_ingestions = client.get("/internal/catalog/ingestions", headers=auth_headers(token))

    assert resp_sources.status_code == 403
    assert resp_ingestions.status_code == 403


def test_internal_catalog_api_filters_ordering_and_response_format(client: TestClient, engine) -> None:
    """Catalog API must support filters and deterministic ordering with audit fields."""
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_catalog(engine)

    resp = client.get("/internal/catalog/sources", headers=auth_headers(token))
    assert resp.status_code == 200
    sources = resp.json()
    assert [item["source_id"] for item in sources] == ["SRC_CSV_01", "SRC_PDF_01", "SRC_XLSX_01"]
    assert sources[1]["latest_status"] == "success"
    assert sources[1]["latest_ingestion_id"] is not None
    assert "latest_started_at" in sources[1]

    resp = client.get("/internal/catalog/sources?status=success", headers=auth_headers(token))
    assert resp.status_code == 200
    assert [item["source_id"] for item in resp.json()] == ["SRC_PDF_01"]

    resp = client.get("/internal/catalog/sources?source_type=xlsx", headers=auth_headers(token))
    assert resp.status_code == 200
    assert [item["source_id"] for item in resp.json()] == ["SRC_XLSX_01"]

    resp = client.get("/internal/catalog/ingestions", headers=auth_headers(token))
    assert resp.status_code == 200
    ingestions = resp.json()
    assert [item["source_id"] for item in ingestions] == ["SRC_XLSX_01", "SRC_PDF_01", "SRC_PDF_01"]
    assert ingestions[0]["status"] == "failed"
    assert "ingestion_id" in ingestions[0]
    assert "started_at" in ingestions[0]
    assert "created_at" in ingestions[0]

    resp = client.get("/internal/catalog/ingestions?status=failed", headers=auth_headers(token))
    assert resp.status_code == 200
    assert [item["source_id"] for item in resp.json()] == ["SRC_XLSX_01"]

    resp = client.get("/internal/catalog/ingestions?source_type=pdf", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp = client.get(
        "/internal/catalog/ingestions?source_id=SRC_PDF_01&limit=1&offset=1",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    page = resp.json()
    assert len(page) == 1
    assert page[0]["source_id"] == "SRC_PDF_01"
    assert page[0]["status"] == "partial"

    bad_limit = client.get("/internal/catalog/ingestions?limit=0", headers=auth_headers(token))
    bad_offset = client.get("/internal/catalog/sources?offset=-1", headers=auth_headers(token))
    assert bad_limit.status_code == 400
    assert bad_offset.status_code == 400
