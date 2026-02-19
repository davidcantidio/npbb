"""Unit tests for CONF Sprint 2 scaffold, core, and service contracts."""

from __future__ import annotations

from dataclasses import replace
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
    S2ConfidencePolicyServiceError,
    execute_s2_confidence_policy_service,
)
from core.confidence.s2_core import (  # noqa: E402
    S2ConfidenceCoreError,
    S2ConfidenceCoreInput,
    execute_s2_confidence_policy_main_flow,
)
from core.confidence.s2_scaffold import (  # noqa: E402
    S2ConfidenceScaffoldError,
    S2ConfidenceScaffoldRequest,
    build_s2_confidence_scaffold,
)
from core.confidence.s2_validation import (  # noqa: E402
    S2ConfidenceValidationError,
    S2ConfidenceValidationInput,
    validate_s2_confidence_input_contract,
    validate_s2_confidence_output_contract,
)


def _build_valid_s2_request(*, correlation_id: str) -> S2ConfidenceScaffoldRequest:
    return S2ConfidenceScaffoldRequest(
        policy_id="conf lead policy v2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="auto_review_gap",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        correlation_id=correlation_id,
    )


def _build_valid_s2_validation_input(*, correlation_id: str) -> S2ConfidenceValidationInput:
    return S2ConfidenceValidationInput(
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="auto_review_gap",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        correlation_id=correlation_id,
    )


def test_conf_s2_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_s2_request(correlation_id="conf-s2-test-001")

    output = build_s2_confidence_scaffold(request)

    assert output.contrato_versao == "conf.s2.v1"
    assert output.correlation_id == "conf-s2-test-001"
    assert output.status == "ready"
    assert output.policy_id == "CONF_LEAD_POLICY_V2"
    assert output.decision_policy["decision_mode"] == "auto_review_gap"
    assert output.decision_policy["thresholds"]["gap"] == 0.4
    assert output.decision_policy["operational_policy"]["gap_escalation_required"] is True
    assert output.pontos_integracao["conf_s2_prepare_endpoint"] == "/internal/confidence/s2/prepare"


def test_conf_s2_scaffold_rejects_invalid_threshold_order() -> None:
    request = _build_valid_s2_request(correlation_id="conf-s2-invalid-threshold-order")
    request = replace(request, manual_review_threshold=0.5, gap_threshold=0.7)

    with pytest.raises(S2ConfidenceScaffoldError) as exc:
        build_s2_confidence_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_DECISION_THRESHOLDS"
    assert "limiares" in error.message


def test_conf_s2_service_success_returns_decision_policy_and_observability() -> None:
    request = _build_valid_s2_request(correlation_id="conf-s2-service-001")

    output = execute_s2_confidence_policy_service(request).to_dict()

    assert output["contrato_versao"] == "conf.s2.service.v1"
    assert output["correlation_id"] == "conf-s2-service-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_LEAD_POLICY_V2"
    assert output["decision_policy"]["decision_mode"] == "auto_review_gap"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["decision"] in {"auto_approve", "manual_review", "gap", "reject"}
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs2evt-")
    assert output["observabilidade"]["policy_profile_ready_event_id"].startswith("confs2evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs2evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("confs2coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("confs2coreevt-")
    assert output["scaffold"]["contrato_versao"] == "conf.s2.v1"


def test_conf_s2_service_raises_actionable_error_for_invalid_decision_mode() -> None:
    request = _build_valid_s2_request(correlation_id="conf-s2-invalid-mode")
    request = replace(request, decision_mode="legacy")

    with pytest.raises(S2ConfidencePolicyServiceError) as exc:
        execute_s2_confidence_policy_service(request)

    error = exc.value
    assert error.code == "INVALID_DECISION_MODE"
    assert "decision_mode suportado" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("confs2evt-")


def test_conf_s2_core_success_runs_main_flow() -> None:
    flow_input = S2ConfidenceCoreInput(
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="auto_review_gap",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        correlation_id="conf-s2-core-001",
    )

    output = execute_s2_confidence_policy_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "conf.s2.core.v1"
    assert output["correlation_id"] == "conf-s2-core-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_LEAD_POLICY_V2"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["decision"] in {"auto_approve", "manual_review", "gap", "reject"}
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs2coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs2coreevt-")


def test_conf_s2_core_raises_actionable_error_for_failed_decision_execution() -> None:
    flow_input = S2ConfidenceCoreInput(
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="auto_review_gap",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        correlation_id="conf-s2-core-failed",
    )

    def fail_decision_executor(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "confidence_score": 0.55,
            "decision": "manual_review",
            "decision_reason": "manual_queue_down",
            "manual_review_queue_size": 0,
        }

    with pytest.raises(S2ConfidenceCoreError) as exc:
        execute_s2_confidence_policy_main_flow(
            flow_input,
            execute_decision=fail_decision_executor,
        )

    error = exc.value
    assert error.code == "CONF_S2_DECISION_EXECUTION_FAILED"
    assert error.stage == "decision_engine"
    assert (error.event_id or "").startswith("confs2coreevt-")


def test_conf_s2_validation_input_success_returns_contract() -> None:
    payload = _build_valid_s2_validation_input(correlation_id="conf-s2-validation-001")

    result = validate_s2_confidence_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "conf.s2.validation.v1"
    assert result.correlation_id == "conf-s2-validation-001"
    assert "policy_id" in result.checks
    assert "decision_mode" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "confidence_policy_s2"
    assert result.observabilidade["validation_started_event_id"].startswith("confs2coreevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("confs2coreevt-")


def test_conf_s2_validation_input_rejects_empty_dataset_name() -> None:
    payload = S2ConfidenceValidationInput(
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="",
        entity_kind="lead",
        correlation_id="conf-s2-validation-error-dataset",
    )

    with pytest.raises(S2ConfidenceValidationError) as exc:
        validate_s2_confidence_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "conf-s2-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("confs2coreevt-")


def test_conf_s2_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_s2_validation_input(correlation_id="conf-s2-validation-core-integration")
    validation = validate_s2_confidence_input_contract(payload)
    core_output = execute_s2_confidence_policy_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s2_confidence_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("confs2coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("confs2coreevt-")


def test_conf_s2_validation_with_service_flow_output_contract_integration() -> None:
    payload = _build_valid_s2_validation_input(
        correlation_id="conf-s2-validation-service-integration"
    )
    validation = validate_s2_confidence_input_contract(payload)
    service_output = execute_s2_confidence_policy_service(
        payload.to_scaffold_request(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_s2_confidence_output_contract(
        service_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "service"
    assert "observabilidade" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("confs2evt-")
    assert output_validation.observabilidade["main_flow_started_event_id"].startswith(
        "confs2coreevt-"
    )


def test_conf_s2_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S2ConfidenceValidationError) as exc:
        validate_s2_confidence_output_contract(
            {"status": "completed"},
            correlation_id="conf-s2-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"
