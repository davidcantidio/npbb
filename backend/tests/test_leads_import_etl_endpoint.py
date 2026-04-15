from __future__ import annotations

from datetime import date
from io import BytesIO
import json
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_public_models import LeadEventoSourceKind
from app.models.models import Evento, ImportAlias, Lead, LeadEvento, StatusEvento, Usuario
from app.routers.leads import _map_etl_import_error
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


def rename_event(engine, *, evento_id: int, nome: str) -> None:
    with Session(engine) as session:
        evento = session.get(Evento, evento_id)
        assert evento is not None
        evento.nome = nome
        session.add(evento)
        session.commit()


def seed_homonymous_event(engine, *, nome: str) -> Evento:
    return seed_event(engine, nome=nome)


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


def test_preview_etl_accepts_csv_with_semicolon_delimiter(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    res = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "lead_import_sample.csv",
                b"Email;CPF;Nome;Sessao\ncsv@example.com;529.982.247-25;Lead CSV;Show 1\n",
                "text/csv",
            )
        },
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert res.status_code == 200
    payload = ImportEtlPreviewResponse.model_validate(res.json())
    assert payload.status == "previewed"
    assert payload.total_rows == 1
    assert payload.valid_rows == 1


def test_preview_etl_import_file_error_maps_to_400_with_exception_message(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    res = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("leads.txt", b"email\nfoo@example.com\n", "text/plain")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert res.status_code == 400
    detail = res.json()["detail"]
    assert detail["code"] == "INVALID_FILE_TYPE"
    assert detail["field"] == "file"
    assert ".txt" in detail["message"]


def test_map_etl_import_error_value_error_maps_to_400_with_exception_message() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _map_etl_import_error(ValueError("campo invalido"))

    err = exc_info.value
    assert err.status_code == 400
    assert err.detail == {
        "code": "ETL_INVALID_INPUT",
        "message": "campo invalido",
    }


def test_preview_etl_requests_header_row_when_cpf_header_is_not_detected(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    xlsx_payload = make_xlsx_payload(
        [
            ["Relatorio de Leads"],
            ["Nome", "Documento", "Sessao"],
            ["Alice", "529.982.247-25", "Show 1"],
        ]
    )

    res = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("sem-cpf.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "header_required"
    assert "session_token" not in payload
    assert payload["required_fields"] == ["cpf"]


def test_preview_etl_accepts_forced_header_row_with_cpf(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    xlsx_payload = make_xlsx_payload(
        [
            ["Relatorio de Leads"],
            ["Nome", "CPF", "Sessao"],
            ["Alice", "529.982.247-25", "Show 1"],
        ]
    )

    res = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("cpf-forcado.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false", "header_row": "2"},
    )

    assert res.status_code == 200
    payload = ImportEtlPreviewResponse.model_validate(res.json())
    assert payload.status == "previewed"
    assert payload.session_token
    assert payload.total_rows == 1


def test_preview_etl_forced_header_row_without_cpf_returns_columns(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    xlsx_payload = make_xlsx_payload(
        [
            ["Relatorio de Leads"],
            ["Nome", "Documento", "Sessao"],
            ["Alice", "529.982.247-25", "Show 1"],
        ]
    )

    res = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("cpf-a-mapear.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false", "header_row": "2"},
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "cpf_column_required"
    assert payload["header_row"] == 2
    assert payload["columns"][1] == {
        "column_index": 2,
        "column_letter": "B",
        "source_value": "Documento",
    }


def test_preview_etl_persists_cpf_header_alias_and_reuses_it(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    xlsx_payload = make_xlsx_payload(
        [
            ["Relatorio de Leads"],
            ["Nome", "Documento", "Sessao"],
            ["Alice", "529.982.247-25", "Show 1"],
        ]
    )

    first = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("alias-cpf.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={
            "evento_id": str(evento.id),
            "strict": "false",
            "header_row": "2",
            "field_aliases_json": json.dumps({"cpf": {"column_index": 2, "source_value": "Documento"}}),
        },
    )

    assert first.status_code == 200
    first_payload = ImportEtlPreviewResponse.model_validate(first.json())
    assert first_payload.status == "previewed"

    with Session(engine) as session:
        alias = session.exec(
            select(ImportAlias).where(
                ImportAlias.domain == "lead_import_etl_header",
                ImportAlias.field_name == "cpf",
                ImportAlias.source_value == "Documento",
            )
        ).first()
        assert alias is not None
        assert alias.canonical_value == "cpf"

    second = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("alias-cpf.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert second.status_code == 200
    second_payload = ImportEtlPreviewResponse.model_validate(second.json())
    assert second_payload.status == "previewed"

    commit = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": second_payload.session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert commit.status_code == 200
    assert ImportEtlResult.model_validate(commit.json()).status == "committed"


def test_commit_etl_blocks_warnings_until_force_confirmation(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine)
    token = login_and_get_token(client, user.email, "Senha123!")

    warning_xlsx = make_xlsx_payload(
        [
            ["Email", "CPF", "Data Nascimento"],
            ["warning@example.com", "52998224725", "01/01/1990"],
            ["warning@example.com", "52998224725", "01/01/1990"],
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


def test_commit_etl_keeps_canonical_event_link_when_event_is_renamed_after_preview(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine, nome="ETL-EVENTO-RENAME-ORIGINAL")
    token = login_and_get_token(client, user.email, "Senha123!")

    xlsx_payload = make_xlsx_payload(
        [
            ["Email", "CPF", "Nome", "Sessao"],
            ["rename@example.com", "52998224725", "Lead Rename", "Show 1"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("rename.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert preview.status_code == 200
    session_token = preview.json()["session_token"]

    rename_event(engine, evento_id=evento.id, nome="ETL-EVENTO-RENAMED")

    commit = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert commit.status_code == 200
    payload = ImportEtlResult.model_validate(commit.json())
    assert payload.status == "committed"

    with Session(engine) as session:
        lead = session.exec(select(Lead).where(Lead.email == "rename@example.com")).first()
        assert lead is not None
        lead_eventos = session.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
        assert len(lead_eventos) == 1
        assert lead_eventos[0].evento_id == evento.id
        assert lead_eventos[0].source_kind == LeadEventoSourceKind.EVENT_DIRECT


def test_commit_etl_links_canonical_event_by_snapshot_evento_id_even_with_homonymous_events(
    client: TestClient,
    engine,
) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine, nome="ETL-EVENTO-HOMONIMO")
    outro_evento = seed_homonymous_event(engine, nome="ETL-EVENTO-HOMONIMO")
    token = login_and_get_token(client, user.email, "Senha123!")

    xlsx_payload = make_xlsx_payload(
        [
            ["Email", "CPF", "Nome", "Sessao"],
            ["homonimo@example.com", "52998224725", "Lead Homonimo", "Show 1"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("homonimo.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert preview.status_code == 200
    session_token = preview.json()["session_token"]
    assert outro_evento.id != evento.id

    commit = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert commit.status_code == 200

    with Session(engine) as session:
        lead = session.exec(select(Lead).where(Lead.email == "homonimo@example.com")).first()
        assert lead is not None
        lead_eventos = session.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
        assert len(lead_eventos) == 1
        assert lead_eventos[0].evento_id == evento.id
        assert lead_eventos[0].evento_id != outro_evento.id
        assert lead_eventos[0].source_kind == LeadEventoSourceKind.EVENT_DIRECT


def test_commit_etl_updates_existing_lead_by_snapshot_evento_id_after_event_rename(
    client: TestClient,
    engine,
) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine, nome="ETL-EVENTO-RENOMEAR-UPDATE")
    token = login_and_get_token(client, user.email, "Senha123!")

    with Session(engine) as session:
        existing = Lead(
            email="rename-existing@example.com",
            cpf="52998224725",
            nome="Lead Original",
            evento_nome="ETL-EVENTO-LEGADO",
            sessao="Show 1",
        )
        session.add(existing)
        session.commit()
        session.refresh(existing)
        existing_id = existing.id
        session.add(
            LeadEvento(
                lead_id=existing_id,
                evento_id=evento.id,
                source_kind=LeadEventoSourceKind.EVENT_DIRECT,
            )
        )
        session.commit()

    xlsx_payload = make_xlsx_payload(
        [
            ["Email", "CPF", "Nome", "Sessao"],
            ["rename-existing@example.com", "52998224725", "Lead Atualizado", "Show 1"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("rename-update.xlsx", xlsx_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "false"},
    )

    assert preview.status_code == 200
    session_token = preview.json()["session_token"]

    rename_event(engine, evento_id=evento.id, nome="ETL-EVENTO-RENOMEADO-DEPOIS-DO-PREVIEW")

    commit = client.post(
        "/leads/import/etl/commit",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_token": session_token, "evento_id": evento.id, "force_warnings": True},
    )

    assert commit.status_code == 200
    payload = ImportEtlResult.model_validate(commit.json())
    assert payload.created == 0
    assert payload.updated == 1
    assert payload.status == "committed"

    with Session(engine) as session:
        leads = session.exec(select(Lead).where(Lead.email == "rename-existing@example.com")).all()
        assert len(leads) == 1
        assert leads[0].id == existing_id
        assert leads[0].nome == "Lead Atualizado"

        lead_eventos = session.exec(select(LeadEvento).where(LeadEvento.lead_id == existing_id)).all()
        assert len(lead_eventos) == 1
        assert lead_eventos[0].evento_id == evento.id
        assert lead_eventos[0].source_kind == LeadEventoSourceKind.EVENT_DIRECT


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


def test_preview_etl_reports_invalid_email_and_cpf_validation_errors(client: TestClient, engine) -> None:
    seed_statuses(engine)
    user = seed_user(engine)
    evento = seed_event(engine, nome="ETL-EVENTO-VALIDATORS")
    token = login_and_get_token(client, user.email, "Senha123!")

    invalid_xlsx = make_xlsx_payload(
        [
            ["Email", "CPF", "Nome", "Sessao"],
            ["mal formado", "11111111111", "Lead Invalido", "Show 1"],
        ]
    )
    preview = client.post(
        "/leads/import/etl/preview",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("invalid-fields.xlsx", invalid_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"evento_id": str(evento.id), "strict": "true"},
    )

    assert preview.status_code == 200
    payload = ImportEtlPreviewResponse.model_validate(preview.json())
    assert payload.valid_rows == 0
    assert payload.invalid_rows == 1

    rejected_rows = [
        item for item in payload.dq_report if item.check_id == "dq.preview.rejected_rows"
    ]
    assert rejected_rows
    assert rejected_rows[0].sample == [
        {
            "row_number": 2,
            "errors": ["email malformado", "CPF inválido"],
        }
    ]


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
