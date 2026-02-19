"""Unit tests for ORQ Sprint 4 backend telemetry helpers."""

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
    "app.services.orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry"
)


def test_build_s4_orchestrator_telemetry_event_success() -> None:
    payload = telemetry.S4OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s4_route_decision",
        correlation_id="orq-s4-correlation-001",
        event_message="Rota do ORQ S4 confirmada no servico",
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
        stage="service",
        context={"telemetry_enabled": True},
    )
    event = telemetry.build_s4_orchestrator_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("orqs4evt-")
    assert event.correlation_id == "orq-s4-correlation-001"
    assert event.source_kind == "pdf"
    assert event.custo_status == "within_budget"
    assert event.latencia_status == "within_sla"
    assert event.stage == "service"
    assert event.context == {"telemetry_enabled": True}
    assert event.to_response_dict()["telemetry_event_id"].startswith("orqs4evt-")


def test_build_s4_orchestrator_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S4OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s4_route_decision",
        correlation_id="orq-s4-correlation-001",
        event_message="Rota do ORQ S4 confirmada no servico",
        severity="debug",
    )

    with pytest.raises(telemetry.S4OrchestratorTelemetryContractError) as exc:
        telemetry.build_s4_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S4_TELEMETRY_SEVERITY"


def test_build_s4_orchestrator_telemetry_event_rejects_invalid_custo_status() -> None:
    payload = telemetry.S4OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s4_route_decision",
        correlation_id="orq-s4-correlation-001",
        event_message="Rota do ORQ S4 confirmada no servico",
        severity="warning",
        custo_status="unknown",
    )

    with pytest.raises(telemetry.S4OrchestratorTelemetryContractError) as exc:
        telemetry.build_s4_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S4_TELEMETRY_CUSTO_STATUS"


def test_build_s4_orchestrator_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s4_orchestrator_error_detail(
        code="ORQ_S4_ROUTE_EXECUTION_FAILED",
        message="Execucao da rota S4 falhou",
        action="Revisar telemetry decision logs.",
        correlation_id="orq-s4-correlation-001",
        telemetry_event_id="orqs4evt-abc123",
        stage="route_execution",
        context={"route_name": "agent_first_extract"},
    )

    assert detail["code"] == "ORQ_S4_ROUTE_EXECUTION_FAILED"
    assert detail["telemetry_event_id"] == "orqs4evt-abc123"
    assert detail["stage"] == "route_execution"
    assert detail["context"]["route_name"] == "agent_first_extract"
