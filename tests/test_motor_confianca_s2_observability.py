"""Unit tests for CONF Sprint 2 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.confidence.s2_observability import (  # noqa: E402
    S2ConfidenceObservabilityError,
    S2ConfidenceObservabilityInput,
    build_s2_confidence_actionable_error,
    build_s2_confidence_observability_event,
)


def test_build_s2_confidence_observability_event_success() -> None:
    payload = S2ConfidenceObservabilityInput(
        event_name="confidence_policy_s2_main_flow_completed",
        correlation_id="conf-s2-correlation-001",
        event_message="Fluxo principal CONF S2 concluido",
        severity="info",
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="leads_capture",
        entity_kind="LEAD",
        schema_version="V2",
        decision_mode="AUTO_REVIEW_GAP",
        confidence_score=0.78,
        decision="MANUAL_REVIEW",
        manual_review_queue_size=125,
        max_manual_review_queue=500,
        gap_escalation_triggered=False,
        stage="main_flow",
        context={"field_weights_count": 4},
    )
    event = build_s2_confidence_observability_event(payload)

    assert event.observability_event_id.startswith("confs2coreevt-")
    assert event.correlation_id == "conf-s2-correlation-001"
    assert event.entity_kind == "lead"
    assert event.schema_version == "v2"
    assert event.decision_mode == "auto_review_gap"
    assert event.confidence_score == 0.78
    assert event.decision == "manual_review"
    assert event.manual_review_queue_size == 125


def test_build_s2_confidence_observability_event_rejects_invalid_manual_review_queue_size() -> None:
    payload = S2ConfidenceObservabilityInput(
        event_name="confidence_policy_s2_main_flow_completed",
        correlation_id="conf-s2-correlation-001",
        event_message="Fluxo principal CONF S2 concluido",
        severity="warning",
        manual_review_queue_size=-1,
    )

    with pytest.raises(S2ConfidenceObservabilityError) as exc:
        build_s2_confidence_observability_event(payload)

    assert exc.value.code == "INVALID_CONF_S2_OBSERVABILITY_MANUAL_REVIEW_QUEUE_SIZE"


def test_build_s2_confidence_actionable_error_includes_context() -> None:
    detail = build_s2_confidence_actionable_error(
        code="CONF_S2_DECISION_EXECUTION_FAILED",
        message="Execucao de decisao falhou",
        action="Revisar logs do executor de decisao.",
        correlation_id="conf-s2-correlation-001",
        observability_event_id="confs2coreevt-abc123",
        stage="decision_engine",
        context={"policy_id": "CONF_LEAD_POLICY_V2"},
    )

    assert detail["code"] == "CONF_S2_DECISION_EXECUTION_FAILED"
    assert detail["observability_event_id"] == "confs2coreevt-abc123"
    assert detail["stage"] == "decision_engine"
    assert detail["context"]["policy_id"] == "CONF_LEAD_POLICY_V2"
