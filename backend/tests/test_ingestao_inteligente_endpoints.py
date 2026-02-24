from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.main import app
from app.models.models import Evento, StatusEvento, Usuario
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


def seed_event(engine, *, evento_id: int) -> Evento:
    with Session(engine) as session:
        status = StatusEvento(nome=f"Status S1 {evento_id}")
        session.add(status)
        session.commit()
        session.refresh(status)
        assert status.id is not None

        evento = Evento(
            id=evento_id,
            nome=f"Evento Sprint 1 {evento_id}",
            cidade="Fortaleza",
            estado="CE",
            status_id=int(status.id),
            data_inicio_prevista=date(2025, 12, 12),
        )
        session.add(evento)
        session.commit()
        session.refresh(evento)
        return evento


def login(client: TestClient, *, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _valid_payload() -> dict[str, int | str]:
    return {
        "evento_id": 2025,
        "nome_arquivo": "tmj_eventos.xlsx",
        "tamanho_arquivo_bytes": 2048,
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }


def _valid_s2_payload() -> dict[str, object]:
    return {
        "evento_id": 2025,
        "lote_id": "lote_tmj_2025_001",
        "lote_nome": "Lote TMJ 2025 001",
        "origem_lote": "upload_manual",
        "total_arquivos_lote": 2,
        "total_bytes_lote": 3072,
        "total_registros_estimados": 500,
        "arquivos": [
            {
                "nome_arquivo": "tmj_eventos.csv",
                "tamanho_arquivo_bytes": 1024,
                "content_type": "text/csv",
            },
            {
                "nome_arquivo": "tmj_eventos.xlsx",
                "tamanho_arquivo_bytes": 2048,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        ],
    }


def _valid_s3_payload() -> dict[str, object]:
    return {
        "evento_id": 2025,
        "lote_id": "lote_tmj_2025_001",
        "lote_upload_id": "lot-abc123def456",
        "status_processamento": "failed",
        "tentativas_reprocessamento": 1,
        "reprocessamento_habilitado": True,
    }


def _valid_s3_reprocess_payload() -> dict[str, object]:
    payload = _valid_s3_payload()
    payload["motivo_reprocessamento"] = "Falha de processamento detectada no lote"
    return payload


def test_s1_scaffold_requires_authentication(client: TestClient) -> None:
    response = client.post("/internal/ingestao-inteligente/s1/scaffold", json=_valid_payload())
    assert response.status_code == 401


def test_s1_scaffold_requires_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    response = client.post(
        "/internal/ingestao-inteligente/s1/scaffold",
        json=_valid_payload(),
        headers=auth_headers(token),
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


def test_s1_scaffold_success_returns_contract(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_payload()
    payload["correlation_id"] = "s1-contract-2025"

    response = client.post(
        "/internal/ingestao-inteligente/s1/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 200

    body = response.json()
    assert body["contrato_versao"] == "s1.v1"
    assert body["correlation_id"] == "s1-contract-2025"
    assert body["status"] == "ready"
    assert body["evento_id"] == 2025
    assert body["proxima_acao"] == "upload_arquivo"
    assert body["limites_upload"]["tamanho_maximo_bytes"] == 25 * 1024 * 1024
    assert "application/pdf" in body["limites_upload"]["content_types_aceitos"]
    assert body["pontos_integracao"]["scaffold_endpoint"] == "/internal/ingestao-inteligente/s1/scaffold"
    assert body["pontos_integracao"]["eventos_endpoint"] == "/evento"
    assert body["pontos_integracao"]["upload_endpoint"] == "/internal/ingestao-inteligente/s1/upload"
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["ready_event_id"].startswith("tel-")


def test_s1_scaffold_rejects_large_files_with_actionable_error(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb2@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_payload()
    payload["tamanho_arquivo_bytes"] = (25 * 1024 * 1024) + 1

    response = client.post(
        "/internal/ingestao-inteligente/s1/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["code"] == "FILE_TOO_LARGE"
    assert "Reduza o tamanho do arquivo" in detail["action"]
    assert detail["context"]["tamanho_arquivo_bytes"] == payload["tamanho_arquivo_bytes"]
    assert detail["correlation_id"].startswith("s1-")
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s1_scaffold_rejects_extension_content_type_mismatch(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb3@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_payload()
    payload["nome_arquivo"] = "upload_tmj.csv"
    payload["content_type"] = "application/pdf"

    response = client.post(
        "/internal/ingestao-inteligente/s1/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400

    detail = response.json()["detail"]
    assert detail["code"] == "FILE_EXTENSION_CONTENT_TYPE_MISMATCH"
    assert "Ajuste o content_type" in detail["action"]
    assert detail["context"]["file_extension"] == ".csv"
    assert detail["context"]["expected_content_type"] == "text/csv"
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s2_scaffold_requires_authentication(client: TestClient) -> None:
    response = client.post("/internal/ingestao-inteligente/s2/scaffold", json=_valid_s2_payload())
    assert response.status_code == 401


def test_s2_scaffold_requires_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb-s2@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    response = client.post(
        "/internal/ingestao-inteligente/s2/scaffold",
        json=_valid_s2_payload(),
        headers=auth_headers(token),
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


def test_s2_scaffold_success_returns_contract(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s2@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s2_payload()
    payload["correlation_id"] = "s2-contract-2025"

    response = client.post(
        "/internal/ingestao-inteligente/s2/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()

    assert body["contrato_versao"] == "s2.v1"
    assert body["correlation_id"] == "s2-contract-2025"
    assert body["status"] == "ready"
    assert body["evento_id"] == 2025
    assert body["lote_id"] == payload["lote_id"]
    assert body["proxima_acao"] == "receber_arquivos_lote"
    assert body["limites_lote"]["max_arquivos_lote"] == 100
    assert body["limites_lote"]["max_bytes_lote"] == 300 * 1024 * 1024
    assert "application/pdf" in body["limites_lote"]["content_types_aceitos"]
    assert body["pontos_integracao"]["s2_scaffold_endpoint"] == "/internal/ingestao-inteligente/s2/scaffold"
    assert body["pontos_integracao"]["s2_lote_upload_endpoint"] == "/internal/ingestao-inteligente/s2/lote/upload"
    assert body["recepcao_lote"]["total_arquivos_lote"] == 2
    assert body["recepcao_lote"]["total_bytes_lote"] == 3072
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["ready_event_id"].startswith("tel-")


def test_s2_scaffold_rejects_invalid_lote_id_with_actionable_error(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s2b@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s2_payload()
    payload["lote_id"] = "lote@2025"

    response = client.post(
        "/internal/ingestao-inteligente/s2/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "INVALID_LOTE_ID"
    assert "identificador de lote estavel" in detail["action"]
    assert detail["correlation_id"].startswith("s2-")
    assert detail["telemetry_event_id"].startswith("tel-")
    assert detail["context"]["lote_id"] == "lote@2025"


def test_s2_scaffold_rejects_file_count_mismatch(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s2c@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s2_payload()
    payload["total_arquivos_lote"] = 3

    response = client.post(
        "/internal/ingestao-inteligente/s2/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "BATCH_FILE_COUNT_MISMATCH"
    assert "Sincronize contagem de arquivos" in detail["action"]
    assert detail["context"]["total_arquivos_lote"] == 3
    assert detail["context"]["arquivos_recebidos"] == 2
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s2_scaffold_rejects_total_bytes_mismatch(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s2d@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s2_payload()
    payload["total_bytes_lote"] = 999

    response = client.post(
        "/internal/ingestao-inteligente/s2/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "BATCH_TOTAL_BYTES_MISMATCH"
    assert "Recalcule total_bytes_lote" in detail["action"]
    assert detail["context"]["total_bytes_lote"] == 999
    assert detail["context"]["total_bytes_calculado"] == 3072
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s3_scaffold_requires_authentication(client: TestClient) -> None:
    response = client.post("/internal/ingestao-inteligente/s3/scaffold", json=_valid_s3_payload())
    assert response.status_code == 401


def test_s3_scaffold_requires_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb-s3@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    response = client.post(
        "/internal/ingestao-inteligente/s3/scaffold",
        json=_valid_s3_payload(),
        headers=auth_headers(token),
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


def test_s3_scaffold_success_returns_contract(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s3@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_payload()
    payload["correlation_id"] = "s3-contract-2025"

    response = client.post(
        "/internal/ingestao-inteligente/s3/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()

    assert body["contrato_versao"] == "s3.v1"
    assert body["correlation_id"] == "s3-contract-2025"
    assert body["status"] == "ready"
    assert body["evento_id"] == 2025
    assert body["lote_id"] == payload["lote_id"]
    assert body["lote_upload_id"] == payload["lote_upload_id"]
    assert body["status_processamento"] == "failed"
    assert body["proxima_acao"] == "avaliar_reprocessamento_lote"
    assert body["limites_reprocessamento"]["max_tentativas_reprocessamento"] == 5
    assert "failed" in body["limites_reprocessamento"]["status_reprocessaveis"]
    assert body["monitoramento_status"]["status_atual"] == "failed"
    assert body["monitoramento_status"]["polling_interval_seconds"] == 30
    assert body["pontos_integracao"]["s3_scaffold_endpoint"] == "/internal/ingestao-inteligente/s3/scaffold"
    assert body["pontos_integracao"]["s3_reprocess_endpoint"] == "/internal/ingestao-inteligente/s3/reprocessar"
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["ready_event_id"].startswith("tel-")


def test_s3_scaffold_rejects_invalid_status_with_actionable_error(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s3b@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_payload()
    payload["status_processamento"] = "unknown_status"

    response = client.post(
        "/internal/ingestao-inteligente/s3/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "INVALID_STATUS_PROCESSAMENTO"
    assert "Use status aceitos" in detail["action"]
    assert detail["telemetry_event_id"].startswith("tel-")
    assert detail["context"]["status_processamento"] == "unknown_status"


def test_s3_scaffold_rejects_reprocess_attempts_exceeded(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s3c@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_payload()
    payload["tentativas_reprocessamento"] = 9

    response = client.post(
        "/internal/ingestao-inteligente/s3/scaffold",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "REPROCESS_ATTEMPTS_EXCEEDED"
    assert "analise manual" in detail["action"]
    assert detail["context"]["tentativas_reprocessamento"] == 9
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s3_status_requires_authentication(client: TestClient) -> None:
    response = client.post("/internal/ingestao-inteligente/s3/status", json=_valid_s3_payload())
    assert response.status_code == 401


def test_s3_status_success_returns_contract(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb-s3-status@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_payload()
    payload["status_processamento"] = "processing"
    payload["correlation_id"] = "s3-status-2025"

    response = client.post(
        "/internal/ingestao-inteligente/s3/status",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()

    assert body["contrato_versao"] == "s3.v1"
    assert body["correlation_id"] == "s3-status-2025"
    assert body["status"] == "ready"
    assert body["evento_id"] == 2025
    assert body["lote_id"] == payload["lote_id"]
    assert body["lote_upload_id"] == payload["lote_upload_id"]
    assert body["status_processamento"] == "processing"
    assert body["proxima_acao"] == "monitorar_status_lote"
    assert body["monitoramento_status"]["status_atual"] == "processing"
    assert body["monitoramento_status"]["polling_interval_seconds"] == 30
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["ready_event_id"].startswith("tel-")


def test_s3_reprocess_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/internal/ingestao-inteligente/s3/reprocessar",
        json=_valid_s3_reprocess_payload(),
    )
    assert response.status_code == 401


def test_s3_reprocess_accepts_when_eligible(client: TestClient, engine) -> None:
    npbb_user = seed_user(
        engine,
        email="npbb-s3-reprocess@example.com",
        password="senha123",
        tipo_usuario="npbb",
    )
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_reprocess_payload()
    payload["correlation_id"] = "s3-reprocess-2025"

    response = client.post(
        "/internal/ingestao-inteligente/s3/reprocessar",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 202
    body = response.json()

    assert body["contrato_versao"] == "s3.v1"
    assert body["correlation_id"] == "s3-reprocess-2025"
    assert body["status"] == "accepted"
    assert body["evento_id"] == 2025
    assert body["lote_id"] == payload["lote_id"]
    assert body["lote_upload_id"] == payload["lote_upload_id"]
    assert body["status_anterior"] == "failed"
    assert body["status_reprocessamento"] == "queued"
    assert body["tentativas_reprocessamento"] == 2
    assert body["reprocessamento_id"].startswith("rep-")
    assert body["proxima_acao"] == "monitorar_status_lote"
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["accepted_event_id"].startswith("tel-")


def test_s3_reprocess_rejects_non_reprocessable_status(client: TestClient, engine) -> None:
    npbb_user = seed_user(
        engine,
        email="npbb-s3-reprocess2@example.com",
        password="senha123",
        tipo_usuario="npbb",
    )
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_reprocess_payload()
    payload["status_processamento"] = "processing"

    response = client.post(
        "/internal/ingestao-inteligente/s3/reprocessar",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "STATUS_NOT_REPROCESSABLE"
    assert "Solicite reprocessamento apenas" in detail["action"]
    assert detail["context"]["status_processamento"] == "processing"
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s3_reprocess_rejects_when_disabled(client: TestClient, engine) -> None:
    npbb_user = seed_user(
        engine,
        email="npbb-s3-reprocess3@example.com",
        password="senha123",
        tipo_usuario="npbb",
    )
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s3_reprocess_payload()
    payload["reprocessamento_habilitado"] = False

    response = client.post(
        "/internal/ingestao-inteligente/s3/reprocessar",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "REPROCESS_DISABLED"
    assert "Habilite reprocessamento" in detail["action"]
    assert detail["context"]["status_processamento"] == "failed"
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s2_lote_upload_requires_authentication(client: TestClient) -> None:
    response = client.post("/internal/ingestao-inteligente/s2/lote/upload", json=_valid_s2_payload())
    assert response.status_code == 401


def test_s2_lote_upload_requires_npbb_user(client: TestClient, engine) -> None:
    bb = seed_user(engine, email="bb-s2-upload@example.com", password="senha123", tipo_usuario="bb")
    token = login(client, email=bb.email, password="senha123")

    response = client.post(
        "/internal/ingestao-inteligente/s2/lote/upload",
        json=_valid_s2_payload(),
        headers=auth_headers(token),
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


def test_s2_lote_upload_accepts_payload_when_event_exists(client: TestClient, engine) -> None:
    npbb_user = seed_user(
        engine,
        email="npbb-s2-upload@example.com",
        password="senha123",
        tipo_usuario="npbb",
    )
    token = login(client, email=npbb_user.email, password="senha123")
    seed_event(engine, evento_id=2025)
    payload = _valid_s2_payload()
    payload["correlation_id"] = "s2-upload-2025"

    response = client.post(
        "/internal/ingestao-inteligente/s2/lote/upload",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 202
    body = response.json()

    assert body["contrato_versao"] == "s2.v1"
    assert body["correlation_id"] == "s2-upload-2025"
    assert body["status"] == "accepted"
    assert body["evento_id"] == 2025
    assert body["lote_id"] == payload["lote_id"]
    assert body["lote_upload_id"].startswith("lot-")
    assert body["proxima_acao"] == "aguardar_processamento_lote"
    assert body["recepcao_lote"]["total_arquivos_lote"] == 2
    assert body["recepcao_lote"]["total_bytes_lote"] == 3072
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["accepted_event_id"].startswith("tel-")


def test_s2_lote_upload_rejects_unknown_event_with_actionable_error(client: TestClient, engine) -> None:
    npbb_user = seed_user(
        engine,
        email="npbb-s2-upload2@example.com",
        password="senha123",
        tipo_usuario="npbb",
    )
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_s2_payload()
    payload["evento_id"] = 9999
    payload["correlation_id"] = "s2-upload-missing-event"

    response = client.post(
        "/internal/ingestao-inteligente/s2/lote/upload",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 404
    detail = response.json()["detail"]

    assert detail["code"] == "EVENTO_NOT_FOUND"
    assert "Selecione um evento existente" in detail["action"]
    assert detail["correlation_id"] == "s2-upload-missing-event"
    assert detail["telemetry_event_id"].startswith("tel-")
    assert detail["context"]["evento_id"] == 9999
    assert detail["context"]["lote_id"] == payload["lote_id"]


def test_s1_upload_accepts_payload_when_event_exists(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb4@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_event(engine, evento_id=2025)
    payload = _valid_payload()
    payload["correlation_id"] = "s1-upload-2025"
    payload["checksum_sha256"] = "a" * 64

    response = client.post(
        "/internal/ingestao-inteligente/s1/upload",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 202

    body = response.json()
    assert body["contrato_versao"] == "s1.v1"
    assert body["correlation_id"] == "s1-upload-2025"
    assert body["status"] == "accepted"
    assert body["evento_id"] == 2025
    assert body["upload_id"].startswith("upl-")
    assert body["arquivo"]["nome_arquivo"] == payload["nome_arquivo"]
    assert body["arquivo"]["tamanho_arquivo_bytes"] == payload["tamanho_arquivo_bytes"]
    assert body["arquivo"]["checksum_sha256"] == payload["checksum_sha256"]
    assert body["proxima_acao"] == "aguardar_processamento_upload"
    assert body["observabilidade"]["received_event_id"].startswith("tel-")
    assert body["observabilidade"]["accepted_event_id"].startswith("tel-")


def test_s1_upload_rejects_unknown_event_with_actionable_error(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb5@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    payload = _valid_payload()
    payload["evento_id"] = 9999

    response = client.post(
        "/internal/ingestao-inteligente/s1/upload",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 404

    detail = response.json()["detail"]
    assert detail["code"] == "EVENTO_NOT_FOUND"
    assert "Selecione um evento existente" in detail["action"]
    assert detail["context"]["evento_id"] == 9999
    assert detail["correlation_id"].startswith("s1-")
    assert detail["telemetry_event_id"].startswith("tel-")


def test_s1_upload_rejects_invalid_checksum(client: TestClient, engine) -> None:
    npbb_user = seed_user(engine, email="npbb6@example.com", password="senha123", tipo_usuario="npbb")
    token = login(client, email=npbb_user.email, password="senha123")
    seed_event(engine, evento_id=2025)
    payload = _valid_payload()
    payload["checksum_sha256"] = "123"

    response = client.post(
        "/internal/ingestao-inteligente/s1/upload",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_CHECKSUM_SHA256"
    assert "Recalcule o checksum SHA-256" in detail["action"]
    assert detail["telemetry_event_id"].startswith("tel-")
