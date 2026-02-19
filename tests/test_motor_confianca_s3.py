"""Unit tests for CONF Sprint 3 scaffold, core, and service contracts."""

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
    S3ConfidencePolicyServiceError,
    execute_s3_confidence_policy_service,
)
from core.confidence.s3_core import (  # noqa: E402
    S3ConfidenceCoreError,
    S3ConfidenceCoreInput,
    execute_s3_confidence_policy_main_flow,
)
from core.confidence.s3_scaffold import (  # noqa: E402
    S3ConfidenceScaffoldError,
    S3ConfidenceScaffoldRequest,
    build_s3_confidence_scaffold,
)


def _build_valid_s3_request(*, correlation_id: str) -> S3ConfidenceScaffoldRequest:
    return S3ConfidenceScaffoldRequest(
        policy_id="conf report policy v3",
        dataset_name="event_report_lines",
        entity_kind="evento",
        schema_version="v3",
        owner_team="etl",
        field_weights={
            "nome_evento": 0.30,
            "data_evento": 0.30,
            "local_evento": 0.20,
            "diretoria": 0.20,
        },
        default_weight=0.10,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="critical_fields_guardrails",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        critical_fields=("nome_evento", "data_evento", "local_evento"),
        min_critical_fields_present=2,
        critical_field_penalty=0.25,
        critical_violation_route="manual_review",
        critical_override_required=True,
        correlation_id=correlation_id,
    )


def test_conf_s3_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_s3_request(correlation_id="conf-s3-test-001")

    output = build_s3_confidence_scaffold(request)

    assert output.contrato_versao == "conf.s3.v1"
    assert output.correlation_id == "conf-s3-test-001"
    assert output.status == "ready"
    assert output.policy_id == "CONF_REPORT_POLICY_V3"
    assert output.decision_policy["decision_mode"] == "critical_fields_guardrails"
    assert output.decision_policy["critical_fields_policy"]["critical_fields_count"] == 3
    assert output.decision_policy["critical_fields_policy"]["critical_violation_route"] == (
        "manual_review"
    )
    assert output.pontos_integracao["conf_s3_prepare_endpoint"] == "/internal/confidence/s3/prepare"


def test_conf_s3_scaffold_rejects_invalid_critical_field_threshold() -> None:
    request = _build_valid_s3_request(correlation_id="conf-s3-invalid-critical-threshold")
    request = replace(request, min_critical_fields_present=4)

    with pytest.raises(S3ConfidenceScaffoldError) as exc:
        build_s3_confidence_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_MIN_CRITICAL_FIELDS_PRESENT"
    assert "critical_fields" in error.action


def test_conf_s3_service_success_returns_decision_policy_and_observability() -> None:
    request = _build_valid_s3_request(correlation_id="conf-s3-service-001")

    output = execute_s3_confidence_policy_service(request).to_dict()

    assert output["contrato_versao"] == "conf.s3.service.v1"
    assert output["correlation_id"] == "conf-s3-service-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_REPORT_POLICY_V3"
    assert output["decision_policy"]["decision_mode"] == "critical_fields_guardrails"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["decision"] in {"auto_approve", "manual_review", "gap", "reject"}
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs3evt-")
    assert output["observabilidade"]["policy_profile_ready_event_id"].startswith("confs3evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs3evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("confs3coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("confs3coreevt-")
    assert output["scaffold"]["contrato_versao"] == "conf.s3.v1"


def test_conf_s3_service_raises_actionable_error_for_invalid_critical_route() -> None:
    request = _build_valid_s3_request(correlation_id="conf-s3-invalid-route")
    request = replace(request, critical_violation_route="queue")

    with pytest.raises(S3ConfidencePolicyServiceError) as exc:
        execute_s3_confidence_policy_service(request)

    error = exc.value
    assert error.code == "INVALID_CRITICAL_VIOLATION_ROUTE"
    assert "critical_violation_route" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("confs3evt-")


def test_conf_s3_core_success_runs_main_flow() -> None:
    flow_input = S3ConfidenceCoreInput(
        policy_id="CONF_REPORT_POLICY_V3",
        dataset_name="event_report_lines",
        entity_kind="evento",
        schema_version="v3",
        owner_team="etl",
        field_weights={
            "nome_evento": 0.30,
            "data_evento": 0.30,
            "local_evento": 0.20,
            "diretoria": 0.20,
        },
        default_weight=0.10,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="critical_fields_guardrails",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        critical_fields=("nome_evento", "data_evento", "local_evento"),
        min_critical_fields_present=2,
        critical_field_penalty=0.25,
        critical_violation_route="manual_review",
        critical_override_required=True,
        correlation_id="conf-s3-core-001",
    )

    output = execute_s3_confidence_policy_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "conf.s3.core.v1"
    assert output["correlation_id"] == "conf-s3-core-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_REPORT_POLICY_V3"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["decision"] in {"auto_approve", "manual_review", "gap", "reject"}
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs3coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs3coreevt-")


def test_conf_s3_core_raises_actionable_error_for_failed_decision_execution() -> None:
    flow_input = S3ConfidenceCoreInput(
        policy_id="CONF_REPORT_POLICY_V3",
        dataset_name="event_report_lines",
        entity_kind="evento",
        schema_version="v3",
        owner_team="etl",
        field_weights={
            "nome_evento": 0.30,
            "data_evento": 0.30,
            "local_evento": 0.20,
            "diretoria": 0.20,
        },
        default_weight=0.10,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="critical_fields_guardrails",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        critical_fields=("nome_evento", "data_evento", "local_evento"),
        min_critical_fields_present=2,
        critical_field_penalty=0.25,
        critical_violation_route="manual_review",
        critical_override_required=True,
        correlation_id="conf-s3-core-failed",
    )

    def fail_decision_executor(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "confidence_score": 0.55,
            "decision": "manual_review",
            "decision_reason": "decision_engine_down",
            "manual_review_queue_size": 0,
            "critical_fields_present_count": 3,
        }

    with pytest.raises(S3ConfidenceCoreError) as exc:
        execute_s3_confidence_policy_main_flow(
            flow_input,
            execute_decision=fail_decision_executor,
        )

    error = exc.value
    assert error.code == "CONF_S3_DECISION_EXECUTION_FAILED"
    assert error.stage == "decision_engine"
    assert (error.event_id or "").startswith("confs3coreevt-")
