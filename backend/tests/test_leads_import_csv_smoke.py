from __future__ import annotations

from io import BytesIO
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import Lead, StatusEvento, Usuario
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


def seed_user(engine, email="smoke@example.com", password="Senha123!") -> Usuario:
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


def seed_statuses(engine) -> None:
    with Session(engine) as session:
        for nome in ["Previsto", "A Confirmar", "Confirmado", "Realizado", "Cancelado"]:
            exists = session.exec(select(StatusEvento).where(StatusEvento.nome == nome)).first()
            if not exists:
                session.add(StatusEvento(nome=nome))
        session.commit()


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_leads_import_csv_smoke_flow(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    token = login_and_get_token(client, user.email, "Senha123!")
    auth = {"Authorization": f"Bearer {token}"}

    event_name = "SMOKE-EVENTO-TESTE"
    create_event = client.post(
        "/evento/",
        headers=auth,
        json={
            "nome": event_name,
            "cidade": "Brasilia",
            "estado": "DF",
            "concorrencia": False,
            "data_inicio_prevista": "2099-01-01",
        },
    )
    assert create_event.status_code == 201

    csv_content = "Email;CPF;Nome;Evento\nsmoke@example.com;52998224725;Smoke Lead;SMOKE-EVENTO-TESTE\n"

    preview = client.post(
        "/leads/import/preview",
        headers=auth,
        files={"file": ("smoke.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
        data={"sample_rows": "5"},
    )
    assert preview.status_code == 200
    assert preview.json()["headers"][:4] == ["Email", "CPF", "Nome", "Evento"]

    mappings = [
        {"coluna": "Email", "campo": "email", "confianca": 1},
        {"coluna": "CPF", "campo": "cpf", "confianca": 1},
        {"coluna": "Nome", "campo": "nome", "confianca": 1},
        {"coluna": "Evento", "campo": "evento_nome", "confianca": 1},
    ]

    validate = client.post("/leads/import/validate", headers=auth, json=mappings)
    assert validate.status_code == 200
    assert validate.json()["ok"] is True

    import_resp = client.post(
        "/leads/import",
        headers=auth,
        files={"file": ("smoke.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
        data={"mappings_json": json.dumps(mappings)},
    )
    assert import_resp.status_code == 200
    first = import_resp.json()
    assert first["total"] == 1
    assert first["created"] + first["updated"] >= 1

    second_resp = client.post(
        "/leads/import",
        headers=auth,
        files={"file": ("smoke.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
        data={"mappings_json": json.dumps(mappings)},
    )
    assert second_resp.status_code == 200
    second = second_resp.json()
    assert second["total"] == 1
    assert second["created"] == 0
    assert second["updated"] >= 1

    with Session(engine) as session:
        leads_count = session.exec(select(Lead)).all()
        assert len(leads_count) == 1


def test_leads_import_validate_rejects_mapping_without_cpf_column(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    token = login_and_get_token(client, user.email, "Senha123!")
    auth = {"Authorization": f"Bearer {token}"}

    email_only_mappings = [
        {"coluna": "Email", "campo": "email", "confianca": 1},
        {"coluna": "Nome", "campo": "nome", "confianca": 1},
        {"coluna": "Evento", "campo": "evento_nome", "confianca": 1},
    ]
    validate_no_cpf = client.post("/leads/import/validate", headers=auth, json=email_only_mappings)
    assert validate_no_cpf.status_code == 400
    detail = validate_no_cpf.json()["detail"]
    assert detail["code"] == "MAPPING_MISSING_ESSENTIAL"
    assert "CPF" in detail["message"]
