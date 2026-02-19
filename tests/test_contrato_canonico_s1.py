"""Validation tests for CONT Sprint 1 canonical contract flow."""

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

from app.services.contract_validation_service import execute_s1_contract_validation_service  # noqa: E402
from core.contracts.s1_core import execute_s1_contract_validation_main_flow  # noqa: E402
from core.contracts.s1_validation import (  # noqa: E402
    S1CanonicalContractValidationError,
    S1CanonicalContractValidationInput,
    validate_s1_contract_flow_output_contract,
    validate_s1_contract_input_contract,
)


def _build_valid_validation_input(*, correlation_id: str) -> S1CanonicalContractValidationInput:
    return S1CanonicalContractValidationInput(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v1",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        correlation_id=correlation_id,
    )


def test_cont_s1_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="cont-s1-validation-001")

    result = validate_s1_contract_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "cont.s1.validation.v1"
    assert result.correlation_id == "cont-s1-validation-001"
    assert "contract_id" in result.checks
    assert "strict_validation" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "canonical_contract_s1"
    assert result.observabilidade["validation_started_event_id"].startswith("conts1coreevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("conts1coreevt-")


def test_cont_s1_validation_input_rejects_empty_dataset_name() -> None:
    payload = S1CanonicalContractValidationInput(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="",
        source_kind="csv",
        correlation_id="cont-s1-validation-error-dataset",
    )

    with pytest.raises(S1CanonicalContractValidationError) as exc:
        validate_s1_contract_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "cont-s1-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("conts1coreevt-")


def test_cont_s1_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.core.contracts.s1.validation")
    payload = S1CanonicalContractValidationInput(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        strict_validation="yes",  # type: ignore[arg-type]
        correlation_id="cont-s1-validation-log-error",
    )

    with pytest.raises(S1CanonicalContractValidationError):
        validate_s1_contract_input_contract(payload)

    assert any(
        record.message == "contract_validation_s1_validation_error"
        and getattr(record, "error_code", "") == "INVALID_STRICT_VALIDATION_FLAG_TYPE"
        for record in caplog.records
    )


def test_cont_s1_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="cont-s1-validation-core-integration")
    validation = validate_s1_contract_input_contract(payload)
    core_output = execute_s1_contract_validation_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s1_contract_flow_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("conts1coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("conts1coreevt-")


def test_cont_s1_validation_with_service_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="cont-s1-validation-service-integration")
    validation = validate_s1_contract_input_contract(payload)
    service_output = execute_s1_contract_validation_service(
        payload.to_scaffold_request(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s1_contract_flow_output_contract(
        service_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "service"
    assert "observabilidade" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("conts1evt-")
    assert output_validation.observabilidade["main_flow_started_event_id"].startswith("conts1coreevt-")


def test_cont_s1_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S1CanonicalContractValidationError) as exc:
        validate_s1_contract_flow_output_contract(
            {"status": "completed"},
            correlation_id="cont-s1-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"
    assert (error.observability_event_id or "").startswith("conts1coreevt-")


def test_cont_s1_validation_flow_output_rejects_unsupported_contract_version() -> None:
    invalid_output = {
        "contrato_versao": "cont.s1.unknown.v0",
        "correlation_id": "cont-s1-output-unknown-contract",
        "status": "completed",
        "contract_id": "CONT_STG_OPTIN_V1",
        "dataset_name": "stg_optin_events",
        "canonical_contract": {"schema_version": "v1"},
        "execucao": {"status": "succeeded", "validation_result_id": "dryrun-x"},
        "pontos_integracao": {},
        "observabilidade": {},
        "scaffold": {},
    }
    with pytest.raises(S1CanonicalContractValidationError) as exc:
        validate_s1_contract_flow_output_contract(
            invalid_output,
            correlation_id="cont-s1-output-unknown-contract",
        )

    error = exc.value
    assert error.code == "UNSUPPORTED_OUTPUT_CONTRACT_VERSION"
    assert "cont.s1.core.v1 ou cont.s1.service.v1" in error.action
    assert error.stage == "validation_output"
