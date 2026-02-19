"""Unit tests for CONF Sprint 4 backend telemetry helpers."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

telemetry = importlib.import_module(
    "app.services.motor-de-confian-a-e-pol-tica-de-decis-o_telemetry"
)


def test_build_s4_confidence_telemetry_event_success() -> None:
    payload = telemetry.S4ConfidenceTelemetryInput(
        event_name="confidence_policy_s4_profile_ready",
        correlation_id="conf-s4-correlation-001",
        event_message="Perfil de confianca CONF S4 pronto",
        severity="info",
        policy_id="CONF_REPORT_POLICY_V4",
        dataset_name="event_report_lines",
        entity_kind="EVENTO",
        schema_version="V4",
        decision_mode="FEEDBACK_ADJUSTED_THRESHOLDS",
        confidence_score=0.84,
        decision="MANUAL_REVIEW",
        manual_review_queue_size=18,
        max_manual_review_queue=500,
        gap_escalation_triggered=False,
        critical_fields_present_count=2,
        min_critical_fields_present=2,
        critical_violation_triggered=False,
        critical_violation_route="MANUAL_REVIEW",
        feedback_samples_count=235,
        min_feedback_samples=200,
        threshold_delta_applied=0.01,
        tuned_thresholds={"auto_approve": 0.84, "manual_review": 0.59, "gap": 0.39},
        quality_drop_value=0.02,
        quality_drop_detected=False,
        anomaly_detected=False,
        calibration_frozen=False,
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s4_confidence_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("confs4evt-")
    assert event.correlation_id == "conf-s4-correlation-001"
    assert event.entity_kind == "evento"
    assert event.schema_version == "v4"
    assert event.decision_mode == "feedback_adjusted_thresholds"
    assert event.confidence_score == 0.84
    assert event.decision == "manual_review"
    assert event.threshold_delta_applied == 0.01
    assert event.tuned_thresholds == {
        "auto_approve": 0.84,
        "manual_review": 0.59,
        "gap": 0.39,
    }


def test_build_s4_confidence_telemetry_event_rejects_invalid_tuned_thresholds() -> None:
    payload = telemetry.S4ConfidenceTelemetryInput(
        event_name="confidence_policy_s4_profile_ready",
        correlation_id="conf-s4-correlation-001",
        event_message="Perfil de confianca CONF S4 pronto",
        severity="warning",
        tuned_thresholds={"auto_approve": 0.50, "manual_review": 0.70, "gap": 0.40},
    )

    with pytest.raises(telemetry.S4ConfidenceTelemetryContractError) as exc:
        telemetry.build_s4_confidence_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONF_S4_TELEMETRY_TUNED_THRESHOLDS"


def test_build_s4_confidence_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s4_confidence_error_detail(
        code="CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED",
        message="Quality drop acima do limite",
        action="Revisar calibracao do threshold e feedback real.",
        correlation_id="conf-s4-correlation-001",
        telemetry_event_id="confs4evt-abc123",
        stage="threshold_adjustment_engine",
        context={"policy_id": "CONF_REPORT_POLICY_V4"},
    )

    assert detail["code"] == "CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED"
    assert detail["telemetry_event_id"] == "confs4evt-abc123"
    assert detail["stage"] == "threshold_adjustment_engine"
    assert detail["context"]["policy_id"] == "CONF_REPORT_POLICY_V4"
