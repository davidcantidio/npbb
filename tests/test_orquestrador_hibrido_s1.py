"""Validation tests for ORQ Sprint 1 hybrid orchestrator contracts."""

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

from app.services.etl_orchestrator_service import execute_s1_orchestrator_service  # noqa: E402
from etl.orchestrator.s1_core import execute_s1_orchestrator_main_flow  # noqa: E402
from etl.orchestrator.s1_validation import (  # noqa: E402
    S1OrchestratorValidationError,
    S1OrchestratorValidationInput,
    validate_s1_orchestrator_flow_output_contract,
    validate_s1_orchestrator_input_contract,
)


def _build_valid_validation_input(*, correlation_id: str) -> S1OrchestratorValidationInput:
    return S1OrchestratorValidationInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        profile_strategy_hint="hybrid",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        correlation_id=correlation_id,
    )


def test_orq_s1_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="orq-s1-validation-001")

    result = validate_s1_orchestrator_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "orq.s1.validation.v1"
    assert result.correlation_id == "orq-s1-validation-001"
    assert "source_kind" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "hybrid_pdf_extract"
    assert result.observabilidade["validation_started_event_id"].startswith("orqs1coreevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("orqs1coreevt-")


def test_orq_s1_validation_input_rejects_invalid_source_uri() -> None:
    payload = S1OrchestratorValidationInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="x",
        profile_strategy_hint="hybrid",
        correlation_id="orq-s1-validation-error-uri",
    )

    with pytest.raises(S1OrchestratorValidationError) as exc:
        validate_s1_orchestrator_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_SOURCE_URI"
    assert "Forneca o caminho/URI" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "orq-s1-validation-error-uri"
    assert (error.observability_event_id or "").startswith("orqs1coreevt-")


def test_orq_s1_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.etl.orchestrator.s1.validation")
    payload = S1OrchestratorValidationInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        ia_habilitada="sim",  # type: ignore[arg-type]
        correlation_id="orq-s1-validation-log-error",
    )

    with pytest.raises(S1OrchestratorValidationError):
        validate_s1_orchestrator_input_contract(payload)

    assert any(
        record.message == "etl_orchestrator_s1_validation_error"
        and getattr(record, "error_code", "") == "INVALID_IA_HABILITADA_FLAG"
        for record in caplog.records
    )


def test_orq_s1_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="orq-s1-validation-core-integration")
    validation = validate_s1_orchestrator_input_contract(payload)
    core_output = execute_s1_orchestrator_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s1_orchestrator_flow_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "rota_selecionada" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("orqs1coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("orqs1coreevt-")


def test_orq_s1_validation_with_service_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="orq-s1-validation-service-integration")
    validation = validate_s1_orchestrator_input_contract(payload)
    service_output = execute_s1_orchestrator_service(
        payload.to_scaffold_request(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s1_orchestrator_flow_output_contract(
        service_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "service"
    assert "observabilidade" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("orqs1evt-")
    assert output_validation.observabilidade["main_flow_started_event_id"].startswith("orqs1coreevt-")


def test_orq_s1_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S1OrchestratorValidationError) as exc:
        validate_s1_orchestrator_flow_output_contract(
            {"status": "ready"},
            correlation_id="orq-s1-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"
    assert (error.observability_event_id or "").startswith("orqs1coreevt-")


def test_orq_s1_validation_flow_output_rejects_unsupported_contract_version() -> None:
    invalid_output = {
        "contrato_versao": "orq.s1.unknown.v0",
        "correlation_id": "orq-s1-output-unknown-contract",
        "status": "ready",
        "source_id": "SRC_TMJ_PDF_2025",
        "source_kind": "pdf",
        "source_uri": "file:///tmp/tmj_2025.pdf",
        "rota_selecionada": "hybrid_pdf_extract",
        "politica_roteamento": {"rota_selecionada": "hybrid_pdf_extract"},
        "pontos_integracao": {},
        "observabilidade": {},
        "scaffold": {},
    }
    with pytest.raises(S1OrchestratorValidationError) as exc:
        validate_s1_orchestrator_flow_output_contract(
            invalid_output,
            correlation_id="orq-s1-output-unknown-contract",
        )

    error = exc.value
    assert error.code == "UNSUPPORTED_OUTPUT_CONTRACT_VERSION"
    assert "orq.s1.core.v1 ou orq.s1.service.v1" in error.action
    assert error.stage == "validation_output"
