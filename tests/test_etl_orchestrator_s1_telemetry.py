"""Unit tests for ORQ Sprint 1 backend telemetry helpers."""

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


def test_build_s1_orchestrator_telemetry_event_success() -> None:
    payload = telemetry.S1OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s1_flow_started",
        correlation_id="orq-s1-correlation-001",
        event_message="Fluxo do servico iniciado",
        severity="info",
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="XLSX",
        source_uri="file:///tmp/tmj_2025.xlsx",
        stage="service",
        context={"flag": True},
    )
    event = telemetry.build_s1_orchestrator_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("orqs1evt-")
    assert event.correlation_id == "orq-s1-correlation-001"
    assert event.source_kind == "xlsx"
    assert event.stage == "service"
    assert event.context == {"flag": True}
    assert event.to_response_dict()["telemetry_event_id"].startswith("orqs1evt-")


def test_build_s1_orchestrator_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S1OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s1_flow_started",
        correlation_id="orq-s1-correlation-001",
        event_message="Fluxo do servico iniciado",
        severity="debug",
    )

    with pytest.raises(telemetry.S1OrchestratorTelemetryContractError) as exc:
        telemetry.build_s1_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S1_TELEMETRY_SEVERITY"


def test_build_s1_orchestrator_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s1_orchestrator_error_detail(
        code="ROUTE_UNAVAILABLE",
        message="Nao existe rota disponivel",
        action="Habilite fallback manual.",
        correlation_id="orq-s1-correlation-001",
        telemetry_event_id="orqs1evt-abc123",
        stage="scaffold",
        context={"source_kind": "pdf"},
    )

    assert detail["code"] == "ROUTE_UNAVAILABLE"
    assert detail["telemetry_event_id"] == "orqs1evt-abc123"
    assert detail["stage"] == "scaffold"
    assert detail["context"]["source_kind"] == "pdf"
