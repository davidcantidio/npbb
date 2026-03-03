"""Authz matrix tests for internal revisao humana endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

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


def seed_user(engine, *, email: str, password: str, tipo_usuario: str) -> Usuario:
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


def payload_for(endpoint: str, *, include_actor_context: bool) -> dict[str, object]:
    payload: dict[str, object] = {
        "workflow_id": "WF_WORKBENCH_NPBB",
        "dataset_name": "dataset_npbb_test",
    }
    if include_actor_context:
        payload["actor_context"] = {"actor_id": "user_npbb", "actor_role": "npbb_reviewer"}
    return payload


ENDPOINTS = [
    "/internal/revisao-humana/s1/prepare",
    "/internal/revisao-humana/s1/execute",
    "/internal/revisao-humana/s2/prepare",
    "/internal/revisao-humana/s2/execute",
    "/internal/revisao-humana/s3/prepare",
    "/internal/revisao-humana/s3/execute",
    "/internal/revisao-humana/s4/prepare",
    "/internal/revisao-humana/s4/execute",
]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_revisao_humana_requires_authentication(client: TestClient, endpoint: str) -> None:
    response = client.post(endpoint, json=payload_for(endpoint, include_actor_context=True))
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_revisao_humana_requires_npbb_user(client: TestClient, engine, endpoint: str) -> None:
    bb_user = seed_user(engine, email="bb-revisao@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb_user.email, password="senha123")
    response = client.post(
        endpoint,
        json=payload_for(endpoint, include_actor_context=True),
        headers=auth_headers(token),
    )
    assert response.status_code == 403


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_revisao_humana_requires_actor_context(client: TestClient, engine, endpoint: str) -> None:
    npbb_user = seed_user(engine, email="npbb-revisao@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    response = client.post(
        endpoint,
        json=payload_for(endpoint, include_actor_context=False),
        headers=auth_headers(token),
    )
    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_revisao_humana_npbb_success(client: TestClient, engine, endpoint: str) -> None:
    npbb_user = seed_user(engine, email="npbb-ok-revisao@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    response = client.post(
        endpoint,
        json=payload_for(endpoint, include_actor_context=True),
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("correlation_id")
