"""API tests for internal ETL health endpoints."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.etl_lineage import LineageLocationType, LineageRef
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind
from app.models.models import EventSession, EventSessionType, Usuario
from app.models.stg_access_control import StgAccessControlSession
from app.models.stg_optin import StgOptinTransaction
from app.utils.security import hash_password


def make_engine():
    """Create isolated in-memory SQLite engine for internal health API tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    """Provide a fresh test database and auth secret."""

    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine):
    """Provide API client bound to the test database session dependency."""

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_user(engine, *, email: str, password: str, tipo_usuario: str) -> Usuario:
    """Create one authenticated test user."""

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
    """Authenticate user and return bearer token."""

    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    """Build Authorization header from bearer token."""

    return {"Authorization": f"Bearer {token}"}


def seed_health_and_coverage_data(engine) -> None:
    """Seed minimal source/runs/sessions/staging data for health endpoints."""

    with Session(engine) as session:
        session_show_12 = EventSession(
            event_id=10,
            session_key="TMJ2025_20251212_SHOW",
            session_name="Show 12/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 12),
        )
        session_show_14 = EventSession(
            event_id=20,
            session_key="TMJ2025_20251214_SHOW",
            session_name="Show 14/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 14),
        )
        session.add(session_show_12)
        session.add(session_show_14)
        session.commit()
        session.refresh(session_show_12)

        src_access = Source(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/access_12.pdf",
        )
        src_optin = Source(
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_12.xlsx",
        )
        src_no_run = Source(
            source_id="SRC_SEM_RUN_QUATORZE",
            kind=SourceKind.PPTX,
            uri="file:///tmp/no_run_14.pptx",
        )
        session.add(src_access)
        session.add(src_optin)
        session.add(src_no_run)
        session.commit()
        session.refresh(src_access)
        session.refresh(src_optin)

        run_access = IngestionRun(source_pk=src_access.id, status=IngestionStatus.SUCCESS)
        run_optin = IngestionRun(source_pk=src_optin.id, status=IngestionStatus.PARTIAL)
        session.add(run_access)
        session.add(run_optin)
        session.commit()
        session.refresh(run_access)
        session.refresh(run_optin)

        lineage_access = LineageRef(
            source_id=src_access.source_id,
            ingestion_id=run_access.id,
            location_type=LineageLocationType.PAGE,
            location_value="page:1",
            evidence_text="Tabela acesso show 12/12",
        )
        lineage_optin = LineageRef(
            source_id=src_optin.source_id,
            ingestion_id=run_optin.id,
            location_type=LineageLocationType.SHEET,
            location_value="sheet:OptIn",
            evidence_text="Planilha opt-in show 12/12",
        )
        session.add(lineage_access)
        session.add(lineage_optin)
        session.commit()
        session.refresh(lineage_access)
        session.refresh(lineage_optin)

        session.add(
            StgAccessControlSession(
                source_id=src_access.source_id,
                ingestion_id=run_access.id,
                lineage_ref_id=int(lineage_access.id),
                event_id=10,
                session_id=int(session_show_12.id),
                pdf_page=1,
                session_name="Show 12/12",
                raw_payload_json="{}",
            )
        )
        session.add(
            StgOptinTransaction(
                source_id=src_optin.source_id,
                ingestion_id=run_optin.id,
                lineage_ref_id=int(lineage_optin.id),
                event_id=10,
                session_id=int(session_show_12.id),
                sheet_name="OptIn",
                header_row=4,
                row_number=1,
                source_range="A6:I6",
                raw_payload_json="{}",
            )
        )
        session.commit()


def test_internal_health_endpoints_require_npbb_user(client: TestClient, engine) -> None:
    """Internal health endpoints must deny non-NPBB users."""

    bb_user = seed_user(engine, email="bb_health@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb_user.email, password="senha123")

    resp_sources = client.get("/internal/health/sources", headers=auth_headers(token))
    resp_coverage = client.get("/internal/health/coverage", headers=auth_headers(token))

    assert resp_sources.status_code == 403
    assert resp_coverage.status_code == 403


def test_internal_health_sources_endpoint_supports_filters_and_pagination(
    client: TestClient,
    engine,
) -> None:
    """Sources endpoint should return summary/items and apply filters/pagination."""

    npbb_user = seed_user(engine, email="npbb_health@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_health_and_coverage_data(engine)

    resp = client.get("/internal/health/sources", headers=auth_headers(token))
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["summary"]["total_sources"] == 3
    assert payload["total"] == 3
    assert isinstance(payload["alerts"], list)
    assert any(item["code"] == "ALERT_PARTIAL_INGESTION" for item in payload["alerts"])
    assert [row["source_id"] for row in payload["items"]] == [
        "SRC_ACESSO_NOTURNO_DOZE",
        "SRC_OPTIN_NOTURNO_DOZE",
        "SRC_SEM_RUN_QUATORZE",
    ]

    resp_success = client.get(
        "/internal/health/sources?status=success",
        headers=auth_headers(token),
    )
    assert resp_success.status_code == 200
    success_payload = resp_success.json()
    assert success_payload["total"] == 1
    assert [row["source_id"] for row in success_payload["items"]] == ["SRC_ACESSO_NOTURNO_DOZE"]

    resp_type = client.get(
        "/internal/health/sources?source_type=xlsx",
        headers=auth_headers(token),
    )
    assert resp_type.status_code == 200
    type_payload = resp_type.json()
    assert type_payload["total"] == 1
    assert type_payload["items"][0]["source_id"] == "SRC_OPTIN_NOTURNO_DOZE"

    resp_page = client.get(
        "/internal/health/sources?limit=1&offset=1",
        headers=auth_headers(token),
    )
    assert resp_page.status_code == 200
    page_payload = resp_page.json()
    assert page_payload["total"] == 3
    assert len(page_payload["items"]) == 1
    assert page_payload["items"][0]["source_id"] == "SRC_OPTIN_NOTURNO_DOZE"


def test_internal_health_coverage_endpoint_supports_event_and_status_filters(
    client: TestClient,
    engine,
) -> None:
    """Coverage endpoint should support `event_id` and coverage status filters."""

    npbb_user = seed_user(engine, email="npbb_cov@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_health_and_coverage_data(engine)

    resp_event = client.get(
        "/internal/health/coverage?event_id=10",
        headers=auth_headers(token),
    )
    assert resp_event.status_code == 200
    event_payload = resp_event.json()
    assert event_payload["event_id"] == 10
    assert event_payload["status"] == "ok"
    assert event_payload["total"] == 1
    assert len(event_payload["sessions"]) == 1
    assert event_payload["sessions"][0]["session_key"] == "TMJ2025_20251212_SHOW"
    assert event_payload["sessions"][0]["status"] == "gap"
    assert "ticket_sales" in event_payload["sessions"][0]["missing_datasets"]
    assert any(
        row["dataset"] == "ticket_sales" and row["status"] == "gap"
        for row in event_payload["matrix"]
    )
    assert isinstance(event_payload["alerts"], list)
    assert any(item["code"] == "ALERT_MISSING_REQUIRED_DATASET" for item in event_payload["alerts"])

    resp_status = client.get(
        "/internal/health/coverage?event_id=10&status=gap",
        headers=auth_headers(token),
    )
    assert resp_status.status_code == 200
    status_payload = resp_status.json()
    assert status_payload["total"] == 1
    assert status_payload["summary"]["gap_sessions"] == 1
    assert status_payload["summary"]["ok_sessions"] == 0

    resp_other_event = client.get(
        "/internal/health/coverage?event_id=20",
        headers=auth_headers(token),
    )
    assert resp_other_event.status_code == 200
    other_payload = resp_other_event.json()
    assert other_payload["total"] == 1
    assert other_payload["sessions"][0]["session_key"] == "TMJ2025_20251214_SHOW"
    assert other_payload["sessions"][0]["status"] == "gap"
