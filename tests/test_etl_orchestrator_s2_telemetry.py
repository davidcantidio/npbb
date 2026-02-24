"""Unit tests for ORQ Sprint 2 backend telemetry helpers."""

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


def test_build_s2_orchestrator_telemetry_event_success() -> None:
    payload = telemetry.S2OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s2_route_decision",
        correlation_id="orq-s2-correlation-001",
        event_message="Rota confirmada no servico",
        severity="info",
        source_id="SRC_TMJ_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        route_name="deterministic_pdf_extract",
        attempt=1,
        stage="service",
        context={"fallback_activated": False},
    )
    event = telemetry.build_s2_orchestrator_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("orqs2evt-")
    assert event.correlation_id == "orq-s2-correlation-001"
    assert event.source_kind == "pdf"
    assert event.route_name == "deterministic_pdf_extract"
    assert event.attempt == 1
    assert event.stage == "service"
    assert event.context == {"fallback_activated": False}
    assert event.to_response_dict()["telemetry_event_id"].startswith("orqs2evt-")


def test_build_s2_orchestrator_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S2OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s2_route_decision",
        correlation_id="orq-s2-correlation-001",
        event_message="Rota confirmada no servico",
        severity="debug",
    )

    with pytest.raises(telemetry.S2OrchestratorTelemetryContractError) as exc:
        telemetry.build_s2_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S2_TELEMETRY_SEVERITY"


def test_build_s2_orchestrator_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s2_orchestrator_error_detail(
        code="ORQ_S2_ROUTE_CHAIN_EXHAUSTED",
        message="Nenhuma rota teve sucesso",
        action="Ajustar fallback e revisar executor.",
        correlation_id="orq-s2-correlation-001",
        telemetry_event_id="orqs2evt-abc123",
        stage="route_execution",
        context={"source_kind": "pdf"},
    )

    assert detail["code"] == "ORQ_S2_ROUTE_CHAIN_EXHAUSTED"
    assert detail["telemetry_event_id"] == "orqs2evt-abc123"
    assert detail["stage"] == "route_execution"
    assert detail["context"]["source_kind"] == "pdf"
