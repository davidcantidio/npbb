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
