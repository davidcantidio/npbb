from __future__ import annotations

import sys
import types
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


def _install_scraping_schema_stub() -> None:
    module_name = "app.schemas.scraping_ingestion"
    if module_name in sys.modules:
        return

    module = types.ModuleType(module_name)

    class ScrapingIngestionCountsOut(BaseModel):
        posts_inserted: int = 0
        posts_updated: int = 0
        profiles_upserted: int = 0
        hashtags_inserted: int = 0
        mentions_inserted: int = 0
        coauthors_inserted: int = 0
        indicators_upserted: int = 0
        monthly_rows_upserted: int = 0

    class ScrapingIngestionPayload(BaseModel):
        sponsor_slug: str
        run_meta: dict[str, Any]
        platforms: dict[str, Any] | None = None
        summary: dict[str, Any] | None = None

    class ScrapingIngestionResponse(BaseModel):
        status: str
        sponsor_slug: str
        counts: ScrapingIngestionCountsOut
        model_config = ConfigDict(extra="allow")

    module.ScrapingIngestionCountsOut = ScrapingIngestionCountsOut
    module.ScrapingIngestionPayload = ScrapingIngestionPayload
    module.ScrapingIngestionResponse = ScrapingIngestionResponse
    sys.modules[module_name] = module


_install_scraping_schema_stub()

from app.db.database import get_session
from app.main import app
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


def test_internal_scraping_health_returns_ok(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")

    response = client.get("/internal/scraping/health", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_internal_scraping_ingestion_accepts_minimal_payload(client: TestClient, engine, monkeypatch) -> None:
    npbb_user = seed_user(engine, email="npbb2@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")

    def fake_ingest_scraping_payload(*, session, payload):
        return {
            "status": "ok",
            "sponsor_slug": payload.sponsor_slug,
            "counts": {
                "posts_inserted": 1,
                "posts_updated": 0,
                "profiles_upserted": 0,
                "hashtags_inserted": 0,
                "mentions_inserted": 0,
                "coauthors_inserted": 0,
                "indicators_upserted": 0,
                "monthly_rows_upserted": 0,
            },
        }

    monkeypatch.setattr(
        "app.routers.internal_scraping.ingest_scraping_payload",
        fake_ingest_scraping_payload,
    )

    payload = {
        "sponsor_slug": "maria-eduarda-surf",
        "run_meta": {"handle": "run_maria_001"},
        "platforms": {
            "instagramPosts": [
                {
                    "post_url": "https://www.instagram.com/p/ABC123/",
                    "shortcode": "ABC123",
                }
            ]
        },
        "summary": {"total_posts": 1},
    }

    response = client.post(
        "/internal/scraping/ingestions",
        headers=auth_headers(token),
        json=payload,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ok"
    assert body["sponsor_slug"] == "maria-eduarda-surf"
    assert isinstance(body.get("counts"), dict)
    assert body["counts"]["posts_inserted"] == 1


def test_internal_scraping_ingestion_rejects_invalid_payload(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb3@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")

    response = client.post(
        "/internal/scraping/ingestions",
        headers=auth_headers(token),
        json={"run_meta": {"handle": "missing-sponsor-slug"}},
    )

    assert response.status_code in (400, 422)
