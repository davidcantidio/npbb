"""Unit tests for ORQ Sprint 3 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.orchestrator.s3_observability import (  # noqa: E402
    S3OrchestratorObservabilityError,
    S3OrchestratorObservabilityInput,
    build_s3_orchestrator_actionable_error,
    build_s3_orchestrator_observability_event,
)


def test_build_s3_orchestrator_observability_event_success() -> None:
    payload = S3OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s3_route_attempt_started",
        correlation_id="orq-s3-correlation-001",
        event_message="Tentativa de execucao de rota iniciada",
        severity="info",
        source_id="SRC_TMJ_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        route_name="agent_first_extract",
        attempt=1,
        route_position=1,
        total_routes=3,
        circuit_state="OPEN",
        consecutive_failures=2,
        failure_threshold=3,
        stage="route_execution",
        context={"retry_policy": "default"},
    )

    event = build_s3_orchestrator_observability_event(payload)

    assert event.observability_event_id.startswith("orqs3coreevt-")
    assert event.correlation_id == "orq-s3-correlation-001"
    assert event.source_kind == "pdf"
    assert event.circuit_state == "open"
    assert event.attempt == 1
    assert event.failure_threshold == 3
    assert event.to_response_dict()["observability_event_id"].startswith("orqs3coreevt-")


def test_build_s3_orchestrator_observability_event_rejects_invalid_severity() -> None:
    payload = S3OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s3_route_attempt_started",
        correlation_id="orq-s3-correlation-001",
        event_message="Tentativa de execucao de rota iniciada",
        severity="debug",
    )

    with pytest.raises(S3OrchestratorObservabilityError) as exc:
        build_s3_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S3_OBSERVABILITY_SEVERITY"


def test_build_s3_orchestrator_observability_event_rejects_invalid_circuit_state() -> None:
    payload = S3OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s3_route_attempt_started",
        correlation_id="orq-s3-correlation-001",
        event_message="Tentativa de execucao de rota iniciada",
        severity="warning",
        circuit_state="paused",
    )

    with pytest.raises(S3OrchestratorObservabilityError) as exc:
        build_s3_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S3_OBSERVABILITY_CIRCUIT_STATE"


def test_build_s3_orchestrator_actionable_error_includes_context() -> None:
    detail = build_s3_orchestrator_actionable_error(
        code="ORQ_S3_CIRCUIT_BREAKER_OPEN",
        message="Circuit breaker aberto",
        action="Aguardar janela de reset e revisar falhas por rota.",
        correlation_id="orq-s3-correlation-001",
        observability_event_id="orqs3coreevt-abc123",
        stage="circuit_breaker",
        context={"failure_threshold": 3},
    )

    assert detail["code"] == "ORQ_S3_CIRCUIT_BREAKER_OPEN"
    assert detail["observability_event_id"] == "orqs3coreevt-abc123"
    assert detail["stage"] == "circuit_breaker"
    assert detail["context"]["failure_threshold"] == 3
