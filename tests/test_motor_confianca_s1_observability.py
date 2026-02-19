"""Unit tests for CONF Sprint 1 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.confidence.s1_observability import (  # noqa: E402
    S1ConfidenceObservabilityError,
    S1ConfidenceObservabilityInput,
    build_s1_confidence_actionable_error,
    build_s1_confidence_observability_event,
)


def test_build_s1_confidence_observability_event_success() -> None:
    payload = S1ConfidenceObservabilityInput(
        event_name="confidence_policy_s1_main_flow_completed",
        correlation_id="conf-s1-correlation-001",
        event_message="Fluxo principal CONF S1 concluido",
        severity="info",
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="LEAD",
        schema_version="V1",
        decision_mode="WEIGHTED_THRESHOLD",
        confidence_score=0.91,
        decision="AUTO_APPROVE",
        stage="main_flow",
        context={"field_weights_count": 4},
    )
    event = build_s1_confidence_observability_event(payload)

    assert event.observability_event_id.startswith("confs1coreevt-")
    assert event.correlation_id == "conf-s1-correlation-001"
    assert event.entity_kind == "lead"
    assert event.schema_version == "v1"
    assert event.decision_mode == "weighted_threshold"
    assert event.confidence_score == 0.91
    assert event.decision == "auto_approve"


def test_build_s1_confidence_observability_event_rejects_invalid_confidence_score() -> None:
    payload = S1ConfidenceObservabilityInput(
        event_name="confidence_policy_s1_main_flow_completed",
        correlation_id="conf-s1-correlation-001",
        event_message="Fluxo principal CONF S1 concluido",
        severity="info",
        confidence_score=1.2,
    )

    with pytest.raises(S1ConfidenceObservabilityError) as exc:
        build_s1_confidence_observability_event(payload)

    assert exc.value.code == "INVALID_CONF_S1_OBSERVABILITY_CONFIDENCE_SCORE"


def test_build_s1_confidence_actionable_error_includes_context() -> None:
    detail = build_s1_confidence_actionable_error(
        code="CONF_S1_SCORING_FAILED",
        message="Execucao de score falhou",
        action="Revisar logs de scoring.",
        correlation_id="conf-s1-correlation-001",
        observability_event_id="confs1coreevt-abc123",
        stage="scoring",
        context={"policy_id": "CONF_LEAD_QUALITY_V1"},
    )

    assert detail["code"] == "CONF_S1_SCORING_FAILED"
    assert detail["observability_event_id"] == "confs1coreevt-abc123"
    assert detail["stage"] == "scoring"
    assert detail["context"]["policy_id"] == "CONF_LEAD_QUALITY_V1"
