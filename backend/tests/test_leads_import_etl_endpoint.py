from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import Evento, Lead, StatusEvento, Usuario
from app.schemas.lead_import_etl import ImportEtlPreviewResponse, ImportEtlResult
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


def seed_user(engine, email="etl@example.com", password="Senha123!") -> Usuario:
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


def seed_event(engine, nome="ETL-EVENTO-TESTE") -> Evento:
    with Session(engine) as session:
        status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
        assert status is not None
        evento = Evento(
            nome=nome,
            cidade="Brasilia",
            estado="DF",
            concorrencia=False,
            data_inicio_prevista=date(2099, 1, 1),
            status_id=status.id,
        )
        session.add(evento)
        session.commit()
        session.refresh(evento)
        return evento


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def make_xlsx_payload(rows: list[list[object]]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    output = BytesIO()
    wb.save(output)
    return output.getvalue()


def test_preview_etl_returns_session_token_and_dq_report(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    fixture_path = Path(__file__).parent / "fixtures" / "lead_import_sample.xlsx"
    with fixture_path.open("rb") as fh:
        res = client.post(
            "/leads/import/etl/preview",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("lead_import_sample.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"evento_id": str(evento.id), "strict": "false"},
        )

    assert res.status_code == 200
    payload = ImportEtlPreviewResponse.model_validate(res.json())
    assert payload.session_token
    assert payload.total_rows >= 1
    assert payload.valid_rows >= 1
    assert payload.invalid_rows >= 0
    assert {item.severity for item in payload.dq_report} <= {"info", "warning", "error"}


def test_preview_etl_invalid_extension_uses_router_error_shape(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    res = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("lead_import_sample.csv", b"email\nfoo@example.com\n", "text/csv")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert res.status_code == 400
    detail = res.json()["detail"]
    assert detail["code"] == "ETL_INVALID_INPUT"
    assert "xlsx" in detail["message"].lower()


def test_commit_etl_blocks_warnings_until_force_confirmation(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    warning_xlsx = make_xlsx_payload(
        [
            ["Email", "CPF", "Data Nascimento"],
            ["warning@example.com", "12345678901", "01/01/1990"],
            ["warning@example.com", "12345678901", "01/01/1990"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("warning.xlsx", warning_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert preview.status_code == 200
    session_token = preview.json()["session_token"]

    blocked = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": False},
    )

    assert blocked.status_code == 409
    assert blocked.json()["detail"]["code"] == "ETL_COMMIT_BLOCKED"

    forced = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert forced.status_code == 200
    payload = ImportEtlResult.model_validate(forced.json())
    assert payload.status == "committed"
    assert payload.created + payload.updated >= 1


def test_commit_etl_serializes_public_schema(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    fixture_path = Path(__file__).parent / "fixtures" / "lead_import_sample.xlsx"
    with fixture_path.open("rb") as fh:
        preview = client.post(
            "/leads/import/etl/preview",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("lead_import_sample.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"evento_id": str(evento.id), "strict": "false"},
        )

    assert preview.status_code == 200
    session_token = preview.json()["session_token"]

    commit = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )
    assert commit.status_code == 200
    payload = ImportEtlResult.model_validate(commit.json())
    assert payload.status == "committed"
    assert payload.created + payload.updated >= 1
    assert {item.severity for item in payload.dq_report} <= {"info", "warning", "error"}

    with Session(engine) as session:
        assert len(session.exec(select(Lead)).all()) >= 1


def test_commit_etl_reuses_committed_result_idempotently(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    fixture_path = Path(__file__).parent / "fixtures" / "lead_import_sample.xlsx"
    with fixture_path.open("rb") as fh:
        preview = client.post(
            "/leads/import/etl/preview",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("lead_import_sample.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"evento_id": str(evento.id), "strict": "false"},
        )

    session_token = preview.json()["session_token"]
    first = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )
    second = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()


def test_commit_etl_rejects_unknown_session_token(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    res = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": "missing-token", "evento_id": evento.id, "force_warnings": True},
    )

    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "ETL_SESSION_NOT_FOUND"


def test_commit_etl_strict_blocks_preview_with_validation_errors(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine, nome="ETL-EVENTO-STRICT")
    token = login_and_get_token(client, user.email, "Senha123!")

    invalid_xlsx = make_xlsx_payload(
        [
            ["Email", "CPF", "Nome Completo", "Sessao"],
            ["strict@example.com", "12345678901", "Lead Invalido", "Show 1"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("invalid.xlsx", invalid_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "true"},
    )

    assert preview.status_code == 200
    payload = ImportEtlPreviewResponse.model_validate(preview.json())
    assert payload.invalid_rows == 1
    session_token = payload.session_token

    res = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert res.status_code == 409
    assert res.json()["detail"]["code"] == "ETL_COMMIT_BLOCKED"


def test_commit_etl_blocks_validation_errors_even_with_force_warnings(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine, nome="ETL-EVENTO-VALIDATION-BLOCK")
    token = login_and_get_token(client, user.email, "Senha123!")

    invalid_xlsx = make_xlsx_payload(
        [
            ["Email", "CPF", "Nome Completo", "Sessao"],
            ["strict@example.com", "12345678901", "Lead Invalido", "Show 1"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("invalid.xlsx", invalid_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "true"},
    )

    assert preview.status_code == 200
    payload = ImportEtlPreviewResponse.model_validate(preview.json())
    assert payload.invalid_rows == 1

    commit = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_token": payload.session_token,
            "evento_id": evento.id,
            "force_warnings": True,
        },
    )

    assert commit.status_code == 409
    assert commit.json()["detail"]["code"] == "ETL_COMMIT_BLOCKED"
