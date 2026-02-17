"""Validation tests for CONT Sprint 2 canonical contract flow."""

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

from app.services.contract_validation_service import execute_s2_contract_validation_service  # noqa: E402
from core.contracts.s2_core import execute_s2_contract_validation_main_flow  # noqa: E402
from core.contracts.s2_validation import (  # noqa: E402
    S2CanonicalContractValidationError,
    S2CanonicalContractValidationInput,
    validate_s2_contract_flow_output_contract,
    validate_s2_contract_input_contract,
)


def _build_valid_validation_input(*, correlation_id: str) -> S2CanonicalContractValidationInput:
    return S2CanonicalContractValidationInput(
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v2",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        schema_required_fields=("record_id", "event_ts", "source_id", "payload_checksum"),
        domain_constraints={
            "record_id": ("not_null",),
            "source_id": ("crm", "app"),
        },
        correlation_id=correlation_id,
    )


def test_cont_s2_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="cont-s2-validation-001")

    result = validate_s2_contract_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "cont.s2.validation.v1"
    assert result.correlation_id == "cont-s2-validation-001"
    assert "contract_id" in result.checks
    assert "schema_required_fields" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "canonical_contract_s2_schema_domain"
    assert result.observabilidade["validation_started_event_id"].startswith("conts2coreevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("conts2coreevt-")


def test_cont_s2_validation_input_rejects_empty_dataset_name() -> None:
    payload = S2CanonicalContractValidationInput(
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="",
        source_kind="csv",
        correlation_id="cont-s2-validation-error-dataset",
    )

    with pytest.raises(S2CanonicalContractValidationError) as exc:
        validate_s2_contract_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "cont-s2-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("conts2coreevt-")


def test_cont_s2_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.core.contracts.s2.validation")
    payload = S2CanonicalContractValidationInput(
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="csv",
        strict_validation="yes",  # type: ignore[arg-type]
        correlation_id="cont-s2-validation-log-error",
    )

    with pytest.raises(S2CanonicalContractValidationError):
        validate_s2_contract_input_contract(payload)

    assert any(
        record.message == "contract_validation_s2_validation_error"
        and getattr(record, "error_code", "") == "INVALID_STRICT_VALIDATION_FLAG_TYPE"
        for record in caplog.records
    )


def test_cont_s2_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="cont-s2-validation-core-integration")
    validation = validate_s2_contract_input_contract(payload)
    core_output = execute_s2_contract_validation_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s2_contract_flow_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("conts2coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("conts2coreevt-")


def test_cont_s2_validation_with_service_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="cont-s2-validation-service-integration")
    validation = validate_s2_contract_input_contract(payload)
    service_output = execute_s2_contract_validation_service(
        payload.to_scaffold_request(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s2_contract_flow_output_contract(
        service_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "service"
    assert "observabilidade" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("conts2evt-")
    assert output_validation.observabilidade["main_flow_started_event_id"].startswith("conts2coreevt-")


def test_cont_s2_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S2CanonicalContractValidationError) as exc:
        validate_s2_contract_flow_output_contract(
            {"status": "completed"},
            correlation_id="cont-s2-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"
    assert (error.observability_event_id or "").startswith("conts2coreevt-")


def test_cont_s2_validation_flow_output_rejects_unsupported_contract_version() -> None:
    invalid_output = {
        "contrato_versao": "cont.s2.unknown.v0",
        "correlation_id": "cont-s2-output-unknown-contract",
        "status": "completed",
        "contract_id": "CONT_STG_OPTIN_V2",
        "dataset_name": "stg_optin_events",
        "validation_profile": {"schema_version": "v2"},
        "execucao": {"status": "succeeded", "validation_result_id": "dryrun-x"},
        "pontos_integracao": {},
        "observabilidade": {},
        "scaffold": {},
    }
    with pytest.raises(S2CanonicalContractValidationError) as exc:
        validate_s2_contract_flow_output_contract(
            invalid_output,
            correlation_id="cont-s2-output-unknown-contract",
        )

    error = exc.value
    assert error.code == "UNSUPPORTED_OUTPUT_CONTRACT_VERSION"
    assert "cont.s2.core.v1 ou cont.s2.service.v1" in error.action
    assert error.stage == "validation_output"
