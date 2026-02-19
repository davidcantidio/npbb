"""Unit tests for CONF Sprint 2 backend telemetry helpers."""

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


def test_build_s2_confidence_telemetry_event_success() -> None:
    payload = telemetry.S2ConfidenceTelemetryInput(
        event_name="confidence_policy_s2_profile_ready",
        correlation_id="conf-s2-correlation-001",
        event_message="Perfil de confianca CONF S2 pronto",
        severity="info",
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="leads_capture",
        entity_kind="LEAD",
        schema_version="V2",
        decision_mode="AUTO_REVIEW_GAP",
        confidence_score=0.83,
        decision="AUTO_APPROVE",
        manual_review_queue_size=80,
        max_manual_review_queue=500,
        gap_escalation_triggered=False,
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s2_confidence_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("confs2evt-")
    assert event.correlation_id == "conf-s2-correlation-001"
    assert event.entity_kind == "lead"
    assert event.schema_version == "v2"
    assert event.decision_mode == "auto_review_gap"
    assert event.confidence_score == 0.83
    assert event.decision == "auto_approve"
    assert event.manual_review_queue_size == 80


def test_build_s2_confidence_telemetry_event_rejects_invalid_manual_review_queue_size() -> None:
    payload = telemetry.S2ConfidenceTelemetryInput(
        event_name="confidence_policy_s2_profile_ready",
        correlation_id="conf-s2-correlation-001",
        event_message="Perfil de confianca CONF S2 pronto",
        severity="warning",
        manual_review_queue_size=-1,
    )

    with pytest.raises(telemetry.S2ConfidenceTelemetryContractError) as exc:
        telemetry.build_s2_confidence_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONF_S2_TELEMETRY_MANUAL_REVIEW_QUEUE_SIZE"


def test_build_s2_confidence_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s2_confidence_error_detail(
        code="CONF_S2_DECISION_EXECUTION_FAILED",
        message="Execucao de decisao falhou",
        action="Revisar logs do executor de decisao.",
        correlation_id="conf-s2-correlation-001",
        telemetry_event_id="confs2evt-abc123",
        stage="decision_engine",
        context={"policy_id": "CONF_LEAD_POLICY_V2"},
    )

    assert detail["code"] == "CONF_S2_DECISION_EXECUTION_FAILED"
    assert detail["telemetry_event_id"] == "confs2evt-abc123"
    assert detail["stage"] == "decision_engine"
    assert detail["context"]["policy_id"] == "CONF_LEAD_POLICY_V2"
