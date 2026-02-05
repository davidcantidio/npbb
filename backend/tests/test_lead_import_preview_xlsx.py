from pathlib import Path

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


def seed_user(engine, email="user@example.com", password="senha123"):
    with Session(engine) as session:
        user = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario="bb",
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


def test_preview_xlsx_detects_start_index(client, engine):
    user = seed_user(engine)
    token = login_and_get_token(client, user.email, "senha123")

    fixture_path = Path(__file__).parent / "fixtures" / "lead_import_sample.xlsx"
    with fixture_path.open("rb") as fh:
        res = client.post(
            "/leads/import/preview",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("lead_import_sample.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"sample_rows": "5"},
        )

    assert res.status_code == 200
    payload = res.json()
    assert payload["start_index"] == 2
    assert payload["headers"][:3] == ["Email", "CPF", "Data Nascimento"]
    assert payload["samples_by_column"][0][0] == "teste@exemplo.com"
