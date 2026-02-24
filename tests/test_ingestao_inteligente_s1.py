"""Validation tests for Sprint 1 smart-ingestion interface contracts."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s1_core import execute_s1_main_flow  # noqa: E402
from frontend.src.features.ingestao_inteligente.s1_validation import (  # noqa: E402
    S1ValidationError,
    S1ValidationInput,
    validate_s1_flow_output_contract,
    validate_s1_input_contract,
)


def test_s1_validation_input_success_returns_contract() -> None:
    payload = S1ValidationInput(
        evento_id=2025,
        nome_arquivo="tmj_eventos.xlsx",
        tamanho_arquivo_bytes=1024,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        checksum_sha256="a" * 64,
        correlation_id="s1-validation-2025",
    )

    result = validate_s1_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "s1.validation.v1"
    assert result.correlation_id == "s1-validation-2025"
    assert "evento_id" in result.checks
    assert "content_type" in result.checks
    assert result.observabilidade["validation_started_event_id"].startswith("obs-")
    assert result.observabilidade["validation_completed_event_id"].startswith("obs-")


def test_s1_validation_input_rejects_unsupported_extension() -> None:
    payload = S1ValidationInput(
        evento_id=2025,
        nome_arquivo="tmj_eventos.txt",
        tamanho_arquivo_bytes=1024,
        content_type="text/plain",
        correlation_id="s1-validation-error-ext",
    )

    with pytest.raises(S1ValidationError) as exc:
        validate_s1_input_contract(payload)

    error = exc.value
    assert error.code == "UNSUPPORTED_FILE_EXTENSION"
    assert "Use arquivos .pdf, .xlsx ou .csv" in error.action
    assert error.correlation_id == "s1-validation-error-ext"
    assert (error.observability_event_id or "").startswith("obs-")


def test_s1_validation_input_rejects_invalid_checksum() -> None:
    payload = S1ValidationInput(
        evento_id=2025,
        nome_arquivo="tmj_eventos.pdf",
        tamanho_arquivo_bytes=1024,
        content_type="application/pdf",
        checksum_sha256="invalido",
        correlation_id="s1-validation-error-checksum",
    )

    with pytest.raises(S1ValidationError) as exc:
        validate_s1_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_CHECKSUM_SHA256"
    assert "Recalcule o checksum SHA-256" in error.action
    assert (error.observability_event_id or "").startswith("obs-")


def test_s1_validation_logs_actionable_warning_on_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.ingestao_inteligente.s1")
    payload = S1ValidationInput(
        evento_id=0,
        nome_arquivo="tmj_eventos.pdf",
        tamanho_arquivo_bytes=1024,
        content_type="application/pdf",
        correlation_id="s1-validation-log-error",
    )

    with pytest.raises(S1ValidationError):
        validate_s1_input_contract(payload)

    assert any(
        record.message == "ingestao_inteligente_s1_validation_error"
        and getattr(record, "error_code", "") == "INVALID_EVENTO_ID"
        for record in caplog.records
    )


def test_s1_validation_and_core_flow_contract_integration() -> None:
    payload = S1ValidationInput(
        evento_id=2025,
        nome_arquivo="tmj_eventos.xlsx",
        tamanho_arquivo_bytes=2048,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        correlation_id="s1-validation-integration-2025",
    )
    validation_result = validate_s1_input_contract(payload)

    def fake_send_backend(endpoint: str, upload_payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s1/upload"
        return {
            "status": "accepted",
            "upload_id": "upl-integration-001",
            "evento_id": int(upload_payload["evento_id"]),
            "proxima_acao": "aguardar_processamento_upload",
        }

    core_output = execute_s1_main_flow(
        payload.to_core_input(),
        send_backend=fake_send_backend,
    ).to_dict()

    output_validation = validate_s1_flow_output_contract(
        core_output,
        correlation_id=validation_result.correlation_id,
    )

    assert output_validation.status == "valid"
    assert "upload_id" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_start_event_id"].startswith("obs-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("obs-")


def test_s1_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S1ValidationError) as exc:
        validate_s1_flow_output_contract(
            {"status": "accepted"},
            correlation_id="s1-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert (error.observability_event_id or "").startswith("obs-")
