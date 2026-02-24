from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.models import (
    DataQualityResult,
    DataQualityScope,
    DataQualitySeverity,
    DataQualityStatus,
    IngestionRun,
    IngestionStatus,
    Source,
    SourceKind,
    Usuario,
)
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


def test_quality_endpoints_require_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    resp = client.get("/internal/quality/results", headers=auth_headers(token))
    assert resp.status_code == 403


def test_quality_results_and_summary(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")

    with Session(engine) as session:
        src = Source(source_id="SRC_TEST_XLSX", kind=SourceKind.XLSX, uri="file:///tmp/a.xlsx")
        session.add(src)
        session.commit()

        run = IngestionRun(source_id="SRC_TEST_XLSX", pipeline="tmj", status=IngestionStatus.SUCCEEDED)
        session.add(run)
        session.commit()
        session.refresh(run)
        run_id = int(run.id)

        r = DataQualityResult(
            ingestion_id=run_id,
            source_id="SRC_TEST_XLSX",
            session_id=None,
            scope=DataQualityScope.CANONICAL,
            severity=DataQualitySeverity.ERROR,
            status=DataQualityStatus.FAIL,
            check_key="canonical.xlsx.rows_nonzero",
            message="XLSX sem carga",
        )
        session.add(r)
        session.commit()

    resp = client.get("/internal/quality/results", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert any(item["check_key"] == "canonical.xlsx.rows_nonzero" for item in data)

    resp = client.get(f"/internal/quality/summary?ingestion_id={run_id}", headers=auth_headers(token))
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["ingestion_id"] == run_id
    assert summary["gate_blocked"] is True
