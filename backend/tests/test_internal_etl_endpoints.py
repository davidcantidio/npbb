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
        src = RegistrySource(
            source_id="SRC_ETL_PDF",
            kind=RegistrySourceKind.PDF,
            uri="file:///tmp/a.pdf",
            display_name="a.pdf",
        )
        session.add(src)
        session.commit()
        session.refresh(src)

        t0 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
        session.add(
            RegistryIngestionRun(
                source_pk=src.id,
                status=RegistryIngestionStatus.SUCCESS,
                started_at=t0,
                finished_at=t0,
                extractor_name="extract_pdf",
                notes="ok",
            )
        )
        session.commit()


def test_internal_etl_requires_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    resp = client.get("/internal/etl/sources", headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.get("/internal/etl/ingestions", headers=auth_headers(token))
    assert resp.status_code == 403


def test_internal_etl_sources_and_ingestions(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_catalog_data(engine)

    sources_resp = client.get("/internal/etl/sources", headers=auth_headers(token))
    assert sources_resp.status_code == 200
    sources = sources_resp.json()
    assert len(sources) == 1
    assert sources[0]["source_id"] == "SRC_ETL_PDF"
    assert sources[0]["latest_status"] == "success"

    ingestions_resp = client.get("/internal/etl/ingestions", headers=auth_headers(token))
    assert ingestions_resp.status_code == 200
    ingestions = ingestions_resp.json()
    assert len(ingestions) == 1
    assert ingestions[0]["source_id"] == "SRC_ETL_PDF"
    assert ingestions[0]["status"] == "success"
