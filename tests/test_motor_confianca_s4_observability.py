"""Unit tests for CONF Sprint 4 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.confidence.s4_observability import (  # noqa: E402
    S4ConfidenceObservabilityError,
    S4ConfidenceObservabilityInput,
    build_s4_confidence_actionable_error,
    build_s4_confidence_observability_event,
)


def test_build_s4_confidence_observability_event_success() -> None:
    payload = S4ConfidenceObservabilityInput(
        event_name="confidence_policy_s4_main_flow_completed",
        correlation_id="conf-s4-correlation-001",
        event_message="Fluxo principal CONF S4 concluido",
        severity="info",
        policy_id="CONF_REPORT_POLICY_V4",
        dataset_name="event_report_lines",
        entity_kind="EVENTO",
        schema_version="V4",
        decision_mode="FEEDBACK_ADJUSTED_THRESHOLDS",
        confidence_score=0.86,
        decision="AUTO_APPROVE",
        manual_review_queue_size=11,
        max_manual_review_queue=500,
        gap_escalation_triggered=False,
        critical_fields_present_count=3,
        min_critical_fields_present=2,
        critical_violation_triggered=False,
        critical_violation_route="MANUAL_REVIEW",
        feedback_samples_count=240,
        min_feedback_samples=200,
        threshold_delta_applied=0.02,
        tuned_thresholds={"auto_approve": 0.83, "manual_review": 0.58, "gap": 0.38},
        quality_drop_value=0.03,
        quality_drop_detected=False,
        anomaly_detected=False,
        calibration_frozen=False,
        stage="main_flow",
        context={"owner_team": "etl"},
    )
    event = build_s4_confidence_observability_event(payload)

    assert event.observability_event_id.startswith("confs4coreevt-")
    assert event.correlation_id == "conf-s4-correlation-001"
    assert event.entity_kind == "evento"
    assert event.schema_version == "v4"
    assert event.decision_mode == "feedback_adjusted_thresholds"
    assert event.confidence_score == 0.86
    assert event.decision == "auto_approve"
    assert event.threshold_delta_applied == 0.02
    assert event.tuned_thresholds == {
        "auto_approve": 0.83,
        "manual_review": 0.58,
        "gap": 0.38,
    }


def test_build_s4_confidence_observability_event_rejects_invalid_tuned_thresholds_order() -> None:
    payload = S4ConfidenceObservabilityInput(
        event_name="confidence_policy_s4_main_flow_completed",
        correlation_id="conf-s4-correlation-001",
        event_message="Fluxo principal CONF S4 concluido",
        severity="warning",
        tuned_thresholds={"auto_approve": 0.60, "manual_review": 0.70, "gap": 0.40},
    )

    with pytest.raises(S4ConfidenceObservabilityError) as exc:
        build_s4_confidence_observability_event(payload)

    assert exc.value.code == "INVALID_CONF_S4_OBSERVABILITY_TUNED_THRESHOLDS"


def test_build_s4_confidence_actionable_error_includes_context() -> None:
    detail = build_s4_confidence_actionable_error(
        code="CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED",
        message="Quality drop acima do limite",
        action="Revisar calibracao do threshold e feedback real.",
        correlation_id="conf-s4-correlation-001",
        observability_event_id="confs4coreevt-abc123",
        stage="threshold_adjustment_engine",
        context={"policy_id": "CONF_REPORT_POLICY_V4"},
    )

    assert detail["code"] == "CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED"
    assert detail["observability_event_id"] == "confs4coreevt-abc123"
    assert detail["stage"] == "threshold_adjustment_engine"
    assert detail["context"]["policy_id"] == "CONF_REPORT_POLICY_V4"
