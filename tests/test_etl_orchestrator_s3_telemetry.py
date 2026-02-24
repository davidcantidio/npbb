"""Unit tests for ORQ Sprint 3 backend telemetry helpers."""

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


def test_build_s3_orchestrator_telemetry_event_success() -> None:
    payload = telemetry.S3OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s3_route_decision",
        correlation_id="orq-s3-correlation-001",
        event_message="Rota do ORQ S3 confirmada no servico",
        severity="info",
        source_id="SRC_TMJ_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        route_name="agent_first_extract",
        attempt=1,
        circuit_state="OPEN",
        failure_threshold=3,
        stage="service",
        context={"fallback_activated": False},
    )
    event = telemetry.build_s3_orchestrator_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("orqs3evt-")
    assert event.correlation_id == "orq-s3-correlation-001"
    assert event.source_kind == "pdf"
    assert event.circuit_state == "open"
    assert event.failure_threshold == 3
    assert event.stage == "service"
    assert event.context == {"fallback_activated": False}
    assert event.to_response_dict()["telemetry_event_id"].startswith("orqs3evt-")


def test_build_s3_orchestrator_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S3OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s3_route_decision",
        correlation_id="orq-s3-correlation-001",
        event_message="Rota do ORQ S3 confirmada no servico",
        severity="debug",
    )

    with pytest.raises(telemetry.S3OrchestratorTelemetryContractError) as exc:
        telemetry.build_s3_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S3_TELEMETRY_SEVERITY"


def test_build_s3_orchestrator_telemetry_event_rejects_invalid_failure_threshold() -> None:
    payload = telemetry.S3OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s3_route_decision",
        correlation_id="orq-s3-correlation-001",
        event_message="Rota do ORQ S3 confirmada no servico",
        severity="warning",
        failure_threshold=0,
    )

    with pytest.raises(telemetry.S3OrchestratorTelemetryContractError) as exc:
        telemetry.build_s3_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S3_TELEMETRY_FAILURE_THRESHOLD"


def test_build_s3_orchestrator_telemetry_event_rejects_invalid_circuit_state() -> None:
    payload = telemetry.S3OrchestratorTelemetryInput(
        event_name="etl_orchestrator_s3_route_decision",
        correlation_id="orq-s3-correlation-001",
        event_message="Rota do ORQ S3 confirmada no servico",
        severity="warning",
        circuit_state="paused",
    )

    with pytest.raises(telemetry.S3OrchestratorTelemetryContractError) as exc:
        telemetry.build_s3_orchestrator_telemetry_event(payload)

    assert exc.value.code == "INVALID_ORQ_S3_TELEMETRY_CIRCUIT_STATE"


def test_build_s3_orchestrator_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s3_orchestrator_error_detail(
        code="ORQ_S3_CIRCUIT_BREAKER_OPEN",
        message="Circuit breaker aberto",
        action="Aguardar reset e revisar falhas.",
        correlation_id="orq-s3-correlation-001",
        telemetry_event_id="orqs3evt-abc123",
        stage="circuit_breaker",
        context={"failure_threshold": 3},
    )

    assert detail["code"] == "ORQ_S3_CIRCUIT_BREAKER_OPEN"
    assert detail["telemetry_event_id"] == "orqs3evt-abc123"
    assert detail["stage"] == "circuit_breaker"
    assert detail["context"]["failure_threshold"] == 3
