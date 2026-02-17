"""Unit tests for ORQ Sprint 4 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.orchestrator.s4_observability import (  # noqa: E402
    S4OrchestratorObservabilityError,
    S4OrchestratorObservabilityInput,
    build_s4_orchestrator_actionable_error,
    build_s4_orchestrator_observability_event,
)


def test_build_s4_orchestrator_observability_event_success() -> None:
    payload = S4OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s4_route_decision_recorded",
        correlation_id="orq-s4-correlation-001",
        event_message="Decisao de rota registrada",
        severity="info",
        source_id="SRC_TMJ_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        route_name="agent_first_extract",
        attempt=1,
        decision_reason="dry_run_main_flow",
        latency_ms=1200,
        cost_usd=0.2,
        custo_status="WITHIN_BUDGET",
        latencia_status="WITHIN_SLA",
        stage="route_execution",
        context={"telemetria_amostragem": 1.0},
    )

    event = build_s4_orchestrator_observability_event(payload)

    assert event.observability_event_id.startswith("orqs4coreevt-")
    assert event.correlation_id == "orq-s4-correlation-001"
    assert event.source_kind == "pdf"
    assert event.custo_status == "within_budget"
    assert event.latencia_status == "within_sla"
    assert event.to_response_dict()["observability_event_id"].startswith("orqs4coreevt-")


def test_build_s4_orchestrator_observability_event_rejects_invalid_severity() -> None:
    payload = S4OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s4_route_decision_recorded",
        correlation_id="orq-s4-correlation-001",
        event_message="Decisao de rota registrada",
        severity="debug",
    )

    with pytest.raises(S4OrchestratorObservabilityError) as exc:
        build_s4_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S4_OBSERVABILITY_SEVERITY"


def test_build_s4_orchestrator_observability_event_rejects_invalid_latencia_status() -> None:
    payload = S4OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s4_route_decision_recorded",
        correlation_id="orq-s4-correlation-001",
        event_message="Decisao de rota registrada",
        severity="warning",
        latencia_status="unknown",
    )

    with pytest.raises(S4OrchestratorObservabilityError) as exc:
        build_s4_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S4_OBSERVABILITY_LATENCIA_STATUS"


def test_build_s4_orchestrator_actionable_error_includes_context() -> None:
    detail = build_s4_orchestrator_actionable_error(
        code="ORQ_S4_ROUTE_EXECUTION_FAILED",
        message="Execucao da rota S4 falhou",
        action="Revisar telemetry decision logs.",
        correlation_id="orq-s4-correlation-001",
        observability_event_id="orqs4coreevt-abc123",
        stage="route_execution",
        context={"route_name": "agent_first_extract"},
    )

    assert detail["code"] == "ORQ_S4_ROUTE_EXECUTION_FAILED"
    assert detail["observability_event_id"] == "orqs4coreevt-abc123"
    assert detail["stage"] == "route_execution"
    assert detail["context"]["route_name"] == "agent_first_extract"
