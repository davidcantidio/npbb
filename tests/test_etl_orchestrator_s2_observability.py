"""Unit tests for ORQ Sprint 2 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.orchestrator.s2_observability import (  # noqa: E402
    S2OrchestratorObservabilityError,
    S2OrchestratorObservabilityInput,
    build_s2_orchestrator_actionable_error,
    build_s2_orchestrator_observability_event,
)


def test_build_s2_orchestrator_observability_event_success() -> None:
    payload = S2OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s2_route_attempt_started",
        correlation_id="orq-s2-correlation-001",
        event_message="Tentativa de execucao iniciada",
        severity="info",
        source_id="SRC_TMJ_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        route_name="deterministic_pdf_extract",
        attempt=1,
        route_position=1,
        total_routes=3,
        stage="route_execution",
        context={"retry_policy": "default"},
    )

    event = build_s2_orchestrator_observability_event(payload)

    assert event.observability_event_id.startswith("orqs2coreevt-")
    assert event.correlation_id == "orq-s2-correlation-001"
    assert event.source_kind == "pdf"
    assert event.route_name == "deterministic_pdf_extract"
    assert event.attempt == 1
    assert event.route_position == 1
    assert event.total_routes == 3
    assert event.to_response_dict()["observability_event_id"].startswith("orqs2coreevt-")


def test_build_s2_orchestrator_observability_event_rejects_invalid_severity() -> None:
    payload = S2OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s2_route_attempt_started",
        correlation_id="orq-s2-correlation-001",
        event_message="Tentativa de execucao iniciada",
        severity="debug",
    )

    with pytest.raises(S2OrchestratorObservabilityError) as exc:
        build_s2_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S2_OBSERVABILITY_SEVERITY"


def test_build_s2_orchestrator_observability_event_rejects_invalid_attempt() -> None:
    payload = S2OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s2_route_attempt_started",
        correlation_id="orq-s2-correlation-001",
        event_message="Tentativa de execucao iniciada",
        severity="warning",
        attempt=0,
    )

    with pytest.raises(S2OrchestratorObservabilityError) as exc:
        build_s2_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S2_OBSERVABILITY_ATTEMPT"


def test_build_s2_orchestrator_actionable_error_includes_context() -> None:
    detail = build_s2_orchestrator_actionable_error(
        code="ORQ_S2_ROUTE_CHAIN_EXHAUSTED",
        message="Todas as rotas do ORQ S2 falharam",
        action="Revisar falhas de rota e politica de fallback.",
        correlation_id="orq-s2-correlation-001",
        observability_event_id="orqs2coreevt-abc123",
        stage="route_execution",
        context={"route_name": "hybrid_pdf_extract"},
    )

    assert detail["code"] == "ORQ_S2_ROUTE_CHAIN_EXHAUSTED"
    assert detail["observability_event_id"] == "orqs2coreevt-abc123"
    assert detail["stage"] == "route_execution"
    assert detail["context"]["route_name"] == "hybrid_pdf_extract"
