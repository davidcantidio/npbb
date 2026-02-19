"""Unit tests for CONF Sprint 3 backend telemetry helpers."""

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


def test_build_s3_confidence_telemetry_event_success() -> None:
    payload = telemetry.S3ConfidenceTelemetryInput(
        event_name="confidence_policy_s3_profile_ready",
        correlation_id="conf-s3-correlation-001",
        event_message="Perfil de confianca CONF S3 pronto",
        severity="info",
        policy_id="CONF_REPORT_POLICY_V3",
        dataset_name="event_report_lines",
        entity_kind="EVENTO",
        schema_version="V3",
        decision_mode="CRITICAL_FIELDS_GUARDRAILS",
        confidence_score=0.81,
        decision="MANUAL_REVIEW",
        manual_review_queue_size=12,
        max_manual_review_queue=500,
        gap_escalation_triggered=False,
        critical_fields_present_count=2,
        min_critical_fields_present=3,
        critical_violation_triggered=True,
        critical_violation_route="GAP",
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s3_confidence_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("confs3evt-")
    assert event.correlation_id == "conf-s3-correlation-001"
    assert event.entity_kind == "evento"
    assert event.schema_version == "v3"
    assert event.decision_mode == "critical_fields_guardrails"
    assert event.confidence_score == 0.81
    assert event.decision == "manual_review"
    assert event.critical_violation_route == "gap"


def test_build_s3_confidence_telemetry_event_rejects_invalid_critical_violation_route() -> None:
    payload = telemetry.S3ConfidenceTelemetryInput(
        event_name="confidence_policy_s3_profile_ready",
        correlation_id="conf-s3-correlation-001",
        event_message="Perfil de confianca CONF S3 pronto",
        severity="warning",
        critical_violation_route="queue",
    )

    with pytest.raises(telemetry.S3ConfidenceTelemetryContractError) as exc:
        telemetry.build_s3_confidence_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONF_S3_TELEMETRY_CRITICAL_VIOLATION_ROUTE"


def test_build_s3_confidence_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s3_confidence_error_detail(
        code="CONF_S3_DECISION_EXECUTION_FAILED",
        message="Execucao de decisao falhou",
        action="Revisar logs do executor de decisao.",
        correlation_id="conf-s3-correlation-001",
        telemetry_event_id="confs3evt-abc123",
        stage="decision_engine",
        context={"policy_id": "CONF_REPORT_POLICY_V3"},
    )

    assert detail["code"] == "CONF_S3_DECISION_EXECUTION_FAILED"
    assert detail["telemetry_event_id"] == "confs3evt-abc123"
    assert detail["stage"] == "decision_engine"
    assert detail["context"]["policy_id"] == "CONF_REPORT_POLICY_V3"
