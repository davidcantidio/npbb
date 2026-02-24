from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.models import Usuario
from app.models.models import IngestionStatus, SourceKind
from app.services.ingestion_registry import finish_ingestion, register_source, start_ingestion
from app.services.metric_lineage import register_metric_lineage
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


def test_registry_endpoints_require_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    resp = client.get("/internal/registry/sources", headers=auth_headers(token))
    assert resp.status_code == 403


def test_registry_endpoints_list_sources_and_ingestions(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")

    with Session(engine) as session:
        register_source(
            session,
            source_id="SRC_TEST_PDF",
            kind=SourceKind.PDF,
            uri="file:///tmp/test.pdf",
        )
        run = start_ingestion(session, source_id="SRC_TEST_PDF", pipeline="tmj")
        finish_ingestion(session, ingestion_id=run.id, status=IngestionStatus.SUCCEEDED, log_text="ok")
        register_metric_lineage(
            session,
            metric_key="attendance.presentes",
            source_id="SRC_TEST_PDF",
            ingestion_id=run.id,
            location_raw="pagina 1",
            evidence="Tabela: Controle de acesso",
            docx_section="Publico do evento",
        )

    resp = client.get("/internal/registry/sources", headers=auth_headers(token))
    assert resp.status_code == 200
    sources = resp.json()
    assert any(s["source_id"] == "SRC_TEST_PDF" for s in sources)

    resp = client.get(
        "/internal/registry/ingestions?source_id=SRC_TEST_PDF",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    ingestions = resp.json()
    assert len(ingestions) == 1
    assert ingestions[0]["source_id"] == "SRC_TEST_PDF"
    assert ingestions[0]["status"] == IngestionStatus.SUCCEEDED

    ingestion_id = ingestions[0]["id"]
    resp = client.get(
        f"/internal/registry/ingestions/{ingestion_id}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["id"] == ingestion_id
    assert detail["log_text"] == "ok"

    resp = client.get(
        "/internal/registry/lineage?metric_key=attendance.presentes",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["metric_key"] == "attendance.presentes"
    assert items[0]["source_id"] == "SRC_TEST_PDF"
