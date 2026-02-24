"""Validation and core-flow tests for Sprint 3 smart-ingestion contracts."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s3_core import (  # noqa: E402
    S3CoreFlowError,
    S3CoreInput,
    execute_s3_main_flow,
)
from frontend.src.features.ingestao_inteligente.s3_validation import (  # noqa: E402
    S3ValidationError,
    S3ValidationInput,
    validate_s3_flow_output_contract,
    validate_s3_input_contract,
)


def _valid_s3_core_input() -> S3CoreInput:
    return S3CoreInput(
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123def456",
        status_processamento="processing",
        tentativas_reprocessamento=1,
        reprocessamento_habilitado=True,
        motivo_reprocessamento="Falha de processamento detectada no lote",
        correlation_id="s3-core-2025",
    )


def _valid_s3_validation_input() -> S3ValidationInput:
    return S3ValidationInput(
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123def456",
        status_processamento="processing",
        tentativas_reprocessamento=1,
        reprocessamento_habilitado=True,
        motivo_reprocessamento="Falha de processamento detectada no lote",
        correlation_id="s3-validation-2025",
    )


def test_s3_validation_input_success_returns_contract() -> None:
    payload = _valid_s3_validation_input()
    result = validate_s3_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "s3.validation.v1"
    assert result.correlation_id == "s3-validation-2025"
    assert "evento_id" in result.checks
    assert "lote_upload_id" in result.checks
    assert result.resumo_monitoramento["status_processamento"] == "processing"
    assert result.resumo_monitoramento["tentativas_reprocessamento"] == 1
    assert result.observabilidade["validation_started_event_id"].startswith("obs-")
    assert result.observabilidade["validation_completed_event_id"].startswith("obs-")


def test_s3_validation_input_rejects_invalid_lote_upload_id() -> None:
    payload = _valid_s3_validation_input()
    payload = S3ValidationInput(
        evento_id=payload.evento_id,
        lote_id=payload.lote_id,
        lote_upload_id="id-invalido",
        status_processamento=payload.status_processamento,
        tentativas_reprocessamento=payload.tentativas_reprocessamento,
        reprocessamento_habilitado=payload.reprocessamento_habilitado,
        motivo_reprocessamento=payload.motivo_reprocessamento,
        correlation_id="s3-validation-invalid-upload-id",
    )

    with pytest.raises(S3ValidationError) as exc:
        validate_s3_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_LOTE_UPLOAD_ID"
    assert "identificador retornado pelo endpoint /s2/lote/upload" in error.action
    assert error.correlation_id == "s3-validation-invalid-upload-id"
    assert (error.observability_event_id or "").startswith("obs-")


def test_s3_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.ingestao_inteligente.s3")
    payload = _valid_s3_validation_input()
    payload = S3ValidationInput(
        evento_id=0,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        tentativas_reprocessamento=payload.tentativas_reprocessamento,
        reprocessamento_habilitado=payload.reprocessamento_habilitado,
        motivo_reprocessamento=payload.motivo_reprocessamento,
        correlation_id="s3-validation-log-error",
    )

    with pytest.raises(S3ValidationError):
        validate_s3_input_contract(payload)

    assert any(
        record.message == "ingestao_inteligente_s3_validation_error"
        and getattr(record, "error_code", "") == "INVALID_EVENTO_ID"
        for record in caplog.records
    )


def test_s3_validation_and_core_flow_contract_integration() -> None:
    payload = _valid_s3_validation_input()
    validation_result = validate_s3_input_contract(payload)

    def fake_send_backend(endpoint: str, status_payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s3/status"
        return {
            "status": "ready",
            "evento_id": int(status_payload["evento_id"]),
            "lote_id": str(status_payload["lote_id"]),
            "lote_upload_id": str(status_payload["lote_upload_id"]),
            "status_processamento": "processing",
            "proxima_acao": "monitorar_status_lote",
        }

    core_output = execute_s3_main_flow(
        payload.to_core_input(),
        send_backend=fake_send_backend,
    ).to_dict()

    output_validation = validate_s3_flow_output_contract(
        core_output,
        correlation_id=validation_result.correlation_id,
    )

    assert output_validation.status == "valid"
    assert "status_monitoramento" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("s3evt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("s3evt-")


def test_s3_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S3ValidationError) as exc:
        validate_s3_flow_output_contract(
            {"status": "ready"},
            correlation_id="s3-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint 3" in error.action
    assert (error.observability_event_id or "").startswith("obs-")


def test_s3_core_main_flow_success_monitor_only() -> None:
    flow_input = _valid_s3_core_input()

    def fake_send_backend(endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s3/status"
        assert payload["lote_upload_id"] == "lot-abc123def456"
        return {
            "status": "ready",
            "evento_id": int(payload["evento_id"]),
            "lote_id": str(payload["lote_id"]),
            "lote_upload_id": str(payload["lote_upload_id"]),
            "status_processamento": "processing",
            "proxima_acao": "monitorar_status_lote",
        }

    output = execute_s3_main_flow(flow_input, send_backend=fake_send_backend).to_dict()

    assert output["contrato_versao"] == "s3.v1"
    assert output["correlation_id"] == "s3-core-2025"
    assert output["status"] == "ready"
    assert output["evento_id"] == 2025
    assert output["lote_id"] == "lote_tmj_2025_001"
    assert output["lote_upload_id"] == "lot-abc123def456"
    assert output["status_processamento"] == "processing"
    assert output["proxima_acao"] == "monitorar_status_lote"
    assert output["reprocessamento"] is None
    assert output["observabilidade"]["flow_started_event_id"].startswith("s3evt-")
    assert output["observabilidade"]["status_dispatch_event_id"].startswith("s3evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("s3evt-")


def test_s3_core_main_flow_success_with_reprocess() -> None:
    flow_input = _valid_s3_core_input()
    flow_input = S3CoreInput(
        evento_id=flow_input.evento_id,
        lote_id=flow_input.lote_id,
        lote_upload_id=flow_input.lote_upload_id,
        status_processamento="failed",
        tentativas_reprocessamento=1,
        reprocessamento_habilitado=True,
        motivo_reprocessamento=flow_input.motivo_reprocessamento,
        correlation_id="s3-core-reprocess-2025",
    )

    def fake_send_backend(endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        if endpoint == "/internal/ingestao-inteligente/s3/status":
            return {
                "status": "ready",
                "evento_id": int(payload["evento_id"]),
                "lote_id": str(payload["lote_id"]),
                "lote_upload_id": str(payload["lote_upload_id"]),
                "status_processamento": "failed",
                "proxima_acao": "avaliar_reprocessamento_lote",
            }
        assert endpoint == "/internal/ingestao-inteligente/s3/reprocessar"
        return {
            "status": "accepted",
            "reprocessamento_id": "rep-abc123def456",
            "evento_id": int(payload["evento_id"]),
            "lote_id": str(payload["lote_id"]),
            "lote_upload_id": str(payload["lote_upload_id"]),
            "status_anterior": "failed",
            "status_reprocessamento": "queued",
            "tentativas_reprocessamento": 2,
            "proxima_acao": "monitorar_status_lote",
        }

    output = execute_s3_main_flow(flow_input, send_backend=fake_send_backend).to_dict()

    assert output["correlation_id"] == "s3-core-reprocess-2025"
    assert output["status"] == "accepted"
    assert output["status_processamento"] == "queued"
    assert output["proxima_acao"] == "monitorar_status_lote"
    assert output["reprocessamento"] is not None
    assert output["reprocessamento"]["reprocessamento_id"] == "rep-abc123def456"
    assert output["observabilidade"]["reprocess_dispatch_event_id"].startswith("s3evt-")


def test_s3_core_main_flow_rejects_incomplete_status_response() -> None:
    flow_input = _valid_s3_core_input()

    def fake_send_backend(_endpoint: str, _payload: dict[str, object]) -> dict[str, object]:
        return {"status": "ready"}

    with pytest.raises(S3CoreFlowError) as exc:
        execute_s3_main_flow(flow_input, send_backend=fake_send_backend)

    error = exc.value
    assert error.code == "INCOMPLETE_S3_STATUS_RESPONSE"
    assert "endpoint /s3/status" in error.action
    assert error.stage == "status_response_validation"


def test_s3_core_main_flow_rejects_incomplete_reprocess_response() -> None:
    flow_input = _valid_s3_core_input()
    flow_input = S3CoreInput(
        evento_id=flow_input.evento_id,
        lote_id=flow_input.lote_id,
        lote_upload_id=flow_input.lote_upload_id,
        status_processamento="failed",
        tentativas_reprocessamento=1,
        reprocessamento_habilitado=True,
        motivo_reprocessamento=flow_input.motivo_reprocessamento,
        correlation_id=flow_input.correlation_id,
    )

    def fake_send_backend(endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        if endpoint == "/internal/ingestao-inteligente/s3/status":
            return {
                "status": "ready",
                "evento_id": int(payload["evento_id"]),
                "lote_id": str(payload["lote_id"]),
                "lote_upload_id": str(payload["lote_upload_id"]),
                "status_processamento": "failed",
                "proxima_acao": "avaliar_reprocessamento_lote",
            }
        return {"status": "accepted"}

    with pytest.raises(S3CoreFlowError) as exc:
        execute_s3_main_flow(flow_input, send_backend=fake_send_backend)

    error = exc.value
    assert error.code == "INCOMPLETE_S3_REPROCESS_RESPONSE"
    assert "endpoint /s3/reprocessar" in error.action
    assert error.stage == "reprocess_response_validation"


def test_s3_core_main_flow_raises_actionable_error_for_invalid_scaffold_input() -> None:
    flow_input = _valid_s3_core_input()
    flow_input = S3CoreInput(
        evento_id=flow_input.evento_id,
        lote_id=flow_input.lote_id,
        lote_upload_id="invalid-id",
        status_processamento=flow_input.status_processamento,
        tentativas_reprocessamento=flow_input.tentativas_reprocessamento,
        reprocessamento_habilitado=flow_input.reprocessamento_habilitado,
        motivo_reprocessamento=flow_input.motivo_reprocessamento,
        correlation_id="s3-core-invalid-scaffold",
    )

    with pytest.raises(S3CoreFlowError) as exc:
        execute_s3_main_flow(flow_input, send_backend=lambda _endpoint, _payload: {})

    error = exc.value
    assert error.code == "INVALID_LOTE_UPLOAD_ID"
    assert "identificador retornado pelo endpoint /s2/lote/upload" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("s3evt-")
