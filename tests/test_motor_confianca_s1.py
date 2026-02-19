"""Unit tests for CONF Sprint 1 scaffold, core, and service contracts."""

from __future__ import annotations

from dataclasses import replace
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

from app.services.confidence_policy_service import (  # noqa: E402
    S1ConfidencePolicyServiceError,
    execute_s1_confidence_policy_service,
)
from core.confidence.s1_core import (  # noqa: E402
    S1ConfidenceCoreError,
    S1ConfidenceCoreInput,
    execute_s1_confidence_policy_main_flow,
)
from core.confidence.s1_scaffold import (  # noqa: E402
    S1ConfidenceScaffoldError,
    S1ConfidenceScaffoldRequest,
    build_s1_confidence_scaffold,
)
from core.confidence.s1_validation import (  # noqa: E402
    S1ConfidenceValidationError,
    S1ConfidenceValidationInput,
    validate_s1_confidence_input_contract,
    validate_s1_confidence_output_contract,
)


def _build_valid_request(*, correlation_id: str) -> S1ConfidenceScaffoldRequest:
    return S1ConfidenceScaffoldRequest(
        policy_id="conf lead quality v1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id=correlation_id,
    )


def _build_valid_validation_input(*, correlation_id: str) -> S1ConfidenceValidationInput:
    return S1ConfidenceValidationInput(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id=correlation_id,
    )


def test_conf_s1_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_request(correlation_id="conf-s1-test-001")

    output = build_s1_confidence_scaffold(request)

    assert output.contrato_versao == "conf.s1.v1"
    assert output.correlation_id == "conf-s1-test-001"
    assert output.status == "ready"
    assert output.policy_id == "CONF_LEAD_QUALITY_V1"
    assert output.confidence_policy["scoring_scope"] == "field_level"
    assert output.confidence_policy["field_weights_count"] == 4
    assert output.confidence_policy["thresholds"]["auto_approve"] == 0.85
    assert output.pontos_integracao["conf_s1_prepare_endpoint"] == "/internal/confidence/s1/prepare"


def test_conf_s1_scaffold_rejects_inverted_thresholds() -> None:
    request = _build_valid_request(correlation_id="conf-s1-invalid-thresholds")
    request = replace(request, manual_review_threshold=0.9, auto_approve_threshold=0.8)

    with pytest.raises(S1ConfidenceScaffoldError) as exc:
        build_s1_confidence_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_CONFIDENCE_THRESHOLDS"
    assert "manual_review_threshold" in error.action


def test_conf_s1_service_success_returns_policy_and_observability() -> None:
    request = _build_valid_request(correlation_id="conf-s1-service-001")

    output = execute_s1_confidence_policy_service(request).to_dict()

    assert output["contrato_versao"] == "conf.s1.service.v1"
    assert output["correlation_id"] == "conf-s1-service-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_LEAD_QUALITY_V1"
    assert output["confidence_policy"]["decision_mode"] == "weighted_threshold"
    assert output["execucao"]["status"] == "succeeded"
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs1evt-")
    assert output["observabilidade"]["policy_profile_ready_event_id"].startswith("confs1evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs1evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("confs1coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("confs1coreevt-")
    assert output["scaffold"]["contrato_versao"] == "conf.s1.v1"


def test_conf_s1_service_raises_actionable_error_for_invalid_entity_kind() -> None:
    request = _build_valid_request(correlation_id="conf-s1-invalid-entity")
    request = replace(request, entity_kind="campanha")

    with pytest.raises(S1ConfidencePolicyServiceError) as exc:
        execute_s1_confidence_policy_service(request)

    error = exc.value
    assert error.code == "INVALID_ENTITY_KIND"
    assert "entity_kind suportado" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("confs1evt-")


def test_conf_s1_core_success_runs_main_flow() -> None:
    flow_input = S1ConfidenceCoreInput(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id="conf-s1-core-001",
    )

    output = execute_s1_confidence_policy_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "conf.s1.core.v1"
    assert output["correlation_id"] == "conf-s1-core-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_LEAD_QUALITY_V1"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["decision"] in {"auto_approve", "manual_review", "reject"}
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs1coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs1coreevt-")


def test_conf_s1_core_raises_actionable_error_for_failed_scoring() -> None:
    flow_input = S1ConfidenceCoreInput(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id="conf-s1-core-failed",
    )

    def fail_scorer(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "confidence_score": 0.42,
            "decision_reason": "missing_required_fields",
        }

    with pytest.raises(S1ConfidenceCoreError) as exc:
        execute_s1_confidence_policy_main_flow(flow_input, execute_scoring=fail_scorer)

    error = exc.value
    assert error.code == "CONF_S1_SCORING_FAILED"
    assert error.stage == "scoring"
    assert (error.event_id or "").startswith("confs1coreevt-")


def test_conf_s1_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="conf-s1-validation-001")

    result = validate_s1_confidence_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "conf.s1.validation.v1"
    assert result.correlation_id == "conf-s1-validation-001"
    assert "policy_id" in result.checks
    assert "decision_mode" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "confidence_policy_s1"
    assert result.observabilidade["validation_started_event_id"].startswith("confs1coreevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("confs1coreevt-")


def test_conf_s1_validation_input_rejects_empty_dataset_name() -> None:
    payload = S1ConfidenceValidationInput(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="",
        entity_kind="lead",
        correlation_id="conf-s1-validation-error-dataset",
    )

    with pytest.raises(S1ConfidenceValidationError) as exc:
        validate_s1_confidence_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "conf-s1-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("confs1coreevt-")


def test_conf_s1_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.core.confidence.s1.validation")
    payload = S1ConfidenceValidationInput(
        policy_id="",
        dataset_name="leads_capture",
        entity_kind="lead",
        correlation_id="conf-s1-validation-log-error",
    )

    with pytest.raises(S1ConfidenceValidationError):
        validate_s1_confidence_input_contract(payload)

    assert any(
        record.message == "confidence_policy_s1_validation_error"
        and getattr(record, "error_code", "") == "EMPTY_POLICY_ID"
        for record in caplog.records
    )


def test_conf_s1_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="conf-s1-validation-core-integration")
    validation = validate_s1_confidence_input_contract(payload)
    core_output = execute_s1_confidence_policy_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s1_confidence_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("confs1coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("confs1coreevt-")


def test_conf_s1_validation_with_service_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="conf-s1-validation-service-integration")
    validation = validate_s1_confidence_input_contract(payload)
    service_output = execute_s1_confidence_policy_service(
        payload.to_scaffold_request(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s1_confidence_output_contract(
        service_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "service"
    assert "observabilidade" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("confs1evt-")
    assert output_validation.observabilidade["main_flow_started_event_id"].startswith("confs1coreevt-")


def test_conf_s1_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S1ConfidenceValidationError) as exc:
        validate_s1_confidence_output_contract(
            {"status": "completed"},
            correlation_id="conf-s1-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"
    assert (error.observability_event_id or "").startswith("confs1coreevt-")


def test_conf_s1_validation_flow_output_rejects_unsupported_contract_version() -> None:
    invalid_output = {
        "contrato_versao": "conf.s1.unknown.v0",
        "correlation_id": "conf-s1-output-unknown-contract",
        "status": "completed",
        "policy_id": "CONF_LEAD_QUALITY_V1",
        "dataset_name": "leads_capture",
        "confidence_policy": {"schema_version": "v1"},
        "execucao": {
            "status": "succeeded",
            "decision": "auto_approve",
            "confidence_score": 0.9,
            "score_result_id": "confs1score-x",
        },
        "pontos_integracao": {},
        "observabilidade": {},
        "scaffold": {},
    }
    with pytest.raises(S1ConfidenceValidationError) as exc:
        validate_s1_confidence_output_contract(
            invalid_output,
            correlation_id="conf-s1-output-unknown-contract",
        )

    error = exc.value
    assert error.code == "UNSUPPORTED_OUTPUT_CONTRACT_VERSION"
    assert "conf.s1.core.v1 ou conf.s1.service.v1" in error.action
    assert error.stage == "validation_output"
