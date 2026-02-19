"""Unit tests for CONF Sprint 3 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.confidence.s3_observability import (  # noqa: E402
    S3ConfidenceObservabilityError,
    S3ConfidenceObservabilityInput,
    build_s3_confidence_actionable_error,
    build_s3_confidence_observability_event,
)


def test_build_s3_confidence_observability_event_success() -> None:
    payload = S3ConfidenceObservabilityInput(
        event_name="confidence_policy_s3_main_flow_completed",
        correlation_id="conf-s3-correlation-001",
        event_message="Fluxo principal CONF S3 concluido",
        severity="info",
        policy_id="CONF_REPORT_POLICY_V3",
        dataset_name="event_report_lines",
        entity_kind="EVENTO",
        schema_version="V3",
        decision_mode="CRITICAL_FIELDS_GUARDRAILS",
        confidence_score=0.82,
        decision="MANUAL_REVIEW",
        manual_review_queue_size=23,
        max_manual_review_queue=500,
        gap_escalation_triggered=False,
        critical_fields_present_count=2,
        min_critical_fields_present=3,
        critical_violation_triggered=True,
        critical_violation_route="GAP",
        stage="main_flow",
        context={"critical_fields_count": 3},
    )
    event = build_s3_confidence_observability_event(payload)

    assert event.observability_event_id.startswith("confs3coreevt-")
    assert event.correlation_id == "conf-s3-correlation-001"
    assert event.entity_kind == "evento"
    assert event.schema_version == "v3"
    assert event.decision_mode == "critical_fields_guardrails"
    assert event.confidence_score == 0.82
    assert event.decision == "manual_review"
    assert event.critical_violation_route == "gap"


def test_build_s3_confidence_observability_event_rejects_invalid_critical_fields_present_count() -> None:
    payload = S3ConfidenceObservabilityInput(
        event_name="confidence_policy_s3_main_flow_completed",
        correlation_id="conf-s3-correlation-001",
        event_message="Fluxo principal CONF S3 concluido",
        severity="warning",
        critical_fields_present_count=-1,
    )

    with pytest.raises(S3ConfidenceObservabilityError) as exc:
        build_s3_confidence_observability_event(payload)

    assert exc.value.code == "INVALID_CONF_S3_OBSERVABILITY_CRITICAL_FIELDS_PRESENT_COUNT"


def test_build_s3_confidence_actionable_error_includes_context() -> None:
    detail = build_s3_confidence_actionable_error(
        code="CONF_S3_DECISION_EXECUTION_FAILED",
        message="Execucao de decisao falhou",
        action="Revisar logs do executor de decisao.",
        correlation_id="conf-s3-correlation-001",
        observability_event_id="confs3coreevt-abc123",
        stage="decision_engine",
        context={"policy_id": "CONF_REPORT_POLICY_V3"},
    )

    assert detail["code"] == "CONF_S3_DECISION_EXECUTION_FAILED"
    assert detail["observability_event_id"] == "confs3coreevt-abc123"
    assert detail["stage"] == "decision_engine"
    assert detail["context"]["policy_id"] == "CONF_REPORT_POLICY_V3"
