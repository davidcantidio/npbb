"""Unit tests for CONF Sprint 1 backend telemetry helpers."""

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


def test_build_s1_confidence_telemetry_event_success() -> None:
    payload = telemetry.S1ConfidenceTelemetryInput(
        event_name="confidence_policy_s1_profile_ready",
        correlation_id="conf-s1-correlation-001",
        event_message="Perfil de confianca CONF S1 pronto",
        severity="info",
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="LEAD",
        schema_version="V1",
        decision_mode="WEIGHTED_THRESHOLD",
        confidence_score=0.88,
        decision="AUTO_APPROVE",
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s1_confidence_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("confs1evt-")
    assert event.correlation_id == "conf-s1-correlation-001"
    assert event.entity_kind == "lead"
    assert event.schema_version == "v1"
    assert event.decision_mode == "weighted_threshold"
    assert event.confidence_score == 0.88
    assert event.decision == "auto_approve"


def test_build_s1_confidence_telemetry_event_rejects_invalid_confidence_score() -> None:
    payload = telemetry.S1ConfidenceTelemetryInput(
        event_name="confidence_policy_s1_profile_ready",
        correlation_id="conf-s1-correlation-001",
        event_message="Perfil de confianca CONF S1 pronto",
        severity="info",
        confidence_score=-0.1,
    )

    with pytest.raises(telemetry.S1ConfidenceTelemetryContractError) as exc:
        telemetry.build_s1_confidence_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONF_S1_TELEMETRY_CONFIDENCE_SCORE"


def test_build_s1_confidence_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s1_confidence_error_detail(
        code="CONF_S1_SCORING_FAILED",
        message="Execucao de score falhou",
        action="Revisar logs de scoring.",
        correlation_id="conf-s1-correlation-001",
        telemetry_event_id="confs1evt-abc123",
        stage="scoring",
        context={"policy_id": "CONF_LEAD_QUALITY_V1"},
    )

    assert detail["code"] == "CONF_S1_SCORING_FAILED"
    assert detail["telemetry_event_id"] == "confs1evt-abc123"
    assert detail["stage"] == "scoring"
    assert detail["context"]["policy_id"] == "CONF_LEAD_QUALITY_V1"
