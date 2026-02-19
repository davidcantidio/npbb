"""Validation tests for XIA Sprint 3 extraction contracts."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.etl_extract_ai_service import execute_s3_extract_ai_service  # noqa: E402
from etl.extract.ai.s3_core import execute_s3_ai_extract_main_flow  # noqa: E402
from etl.extract.ai.s3_validation import (  # noqa: E402
    S3AIExtractValidationError,
    S3AIExtractValidationInput,
    validate_s3_extract_ai_flow_output_contract,
    validate_s3_extract_ai_input_contract,
)


def _build_valid_validation_input(*, correlation_id: str) -> S3AIExtractValidationInput:
    return S3AIExtractValidationInput(
        source_id="SRC_TMJ_PDFSCAN_2025",
        source_kind="pdf_scan",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        document_profile_hint="pdf_scan_document",
        image_preprocess_hint="ocr_enhanced",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="page",
        max_tokens_output=4096,
        temperature=0.1,
        correlation_id=correlation_id,
    )


def test_xia_s3_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="xia-s3-validation-001")

    result = validate_s3_extract_ai_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "xia.s3.validation.v1"
    assert result.correlation_id == "xia-s3-validation-001"
    assert "source_id" in result.checks
    assert "max_tokens_output" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "ai_documento_scan_s3"
    assert result.observabilidade["validation_started_event_id"].startswith("xias3coreevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("xias3coreevt-")


def test_xia_s3_validation_input_rejects_invalid_source_uri() -> None:
    payload = S3AIExtractValidationInput(
        source_id="SRC_TMJ_PDFSCAN_2025",
        source_kind="pdf_scan",
        source_uri="x",
        correlation_id="xia-s3-validation-error-uri",
    )

    with pytest.raises(S3AIExtractValidationError) as exc:
        validate_s3_extract_ai_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_SOURCE_URI"
    assert "Forneca o caminho/URI" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "xia-s3-validation-error-uri"
    assert (error.observability_event_id or "").startswith("xias3coreevt-")


def test_xia_s3_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.etl.extract.ai.s3.validation")
    payload = S3AIExtractValidationInput(
        source_id="SRC_TMJ_PDFSCAN_2025",
        source_kind="pdf_scan",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        max_tokens_output="mil",  # type: ignore[arg-type]
        correlation_id="xia-s3-validation-log-error",
    )

    with pytest.raises(S3AIExtractValidationError):
        validate_s3_extract_ai_input_contract(payload)

    assert any(
        record.message == "etl_extract_ai_s3_validation_error"
        and getattr(record, "error_code", "") == "INVALID_MAX_TOKENS_OUTPUT_TYPE"
        for record in caplog.records
    )


def test_xia_s3_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="xia-s3-validation-core-integration")
    validation = validate_s3_extract_ai_input_contract(payload)
    core_output = execute_s3_ai_extract_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s3_extract_ai_flow_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("xias3coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("xias3coreevt-")


def test_xia_s3_validation_with_service_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="xia-s3-validation-service-integration")
    validation = validate_s3_extract_ai_input_contract(payload)
    service_output = execute_s3_extract_ai_service(
        payload.to_scaffold_request(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s3_extract_ai_flow_output_contract(
        service_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "service"
    assert "observabilidade" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("xias3evt-")
    assert output_validation.observabilidade["main_flow_started_event_id"].startswith("xias3coreevt-")


def test_xia_s3_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S3AIExtractValidationError) as exc:
        validate_s3_extract_ai_flow_output_contract(
            {"status": "completed"},
            correlation_id="xia-s3-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"
    assert (error.observability_event_id or "").startswith("xias3coreevt-")


def test_xia_s3_validation_flow_output_rejects_unsupported_contract_version() -> None:
    invalid_output = {
        "contrato_versao": "xia.s3.unknown.v0",
        "correlation_id": "xia-s3-output-unknown-contract",
        "status": "completed",
        "source_id": "SRC_TMJ_PDFSCAN_2025",
        "source_kind": "pdf_scan",
        "source_uri": "file:///tmp/tmj_2025_scan.pdf",
        "extraction_plan": {"chunk_strategy": "page"},
        "execucao": {"status": "succeeded", "chunk_count": 1},
        "pontos_integracao": {},
        "observabilidade": {},
        "scaffold": {},
    }
    with pytest.raises(S3AIExtractValidationError) as exc:
        validate_s3_extract_ai_flow_output_contract(
            invalid_output,
            correlation_id="xia-s3-output-unknown-contract",
        )

    error = exc.value
    assert error.code == "UNSUPPORTED_OUTPUT_CONTRACT_VERSION"
    assert "xia.s3.core.v1 ou xia.s3.service.v1" in error.action
    assert error.stage == "validation_output"
