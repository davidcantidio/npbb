"""Unit tests for ORQ Sprint 1 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.orchestrator.s1_observability import (  # noqa: E402
    S1OrchestratorObservabilityError,
    S1OrchestratorObservabilityInput,
    build_s1_orchestrator_actionable_error,
    build_s1_orchestrator_observability_event,
)


def test_build_s1_orchestrator_observability_event_success() -> None:
    payload = S1OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s1_main_flow_started",
        correlation_id="orq-s1-correlation-001",
        event_message="Fluxo iniciado",
        severity="info",
        source_id="SRC_TMJ_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        stage="main_flow",
        context={"flag": True},
    )

    event = build_s1_orchestrator_observability_event(payload)

    assert event.observability_event_id.startswith("orqs1coreevt-")
    assert event.correlation_id == "orq-s1-correlation-001"
    assert event.source_kind == "pdf"
    assert event.stage == "main_flow"
    assert event.context == {"flag": True}
    assert event.to_response_dict()["observability_event_id"].startswith("orqs1coreevt-")


def test_build_s1_orchestrator_observability_event_rejects_invalid_severity() -> None:
    payload = S1OrchestratorObservabilityInput(
        event_name="etl_orchestrator_s1_main_flow_started",
        correlation_id="orq-s1-correlation-001",
        event_message="Fluxo iniciado",
        severity="debug",
    )

    with pytest.raises(S1OrchestratorObservabilityError) as exc:
        build_s1_orchestrator_observability_event(payload)

    assert exc.value.code == "INVALID_ORQ_S1_OBSERVABILITY_SEVERITY"


def test_build_s1_orchestrator_actionable_error_includes_context() -> None:
    detail = build_s1_orchestrator_actionable_error(
        code="ROUTE_UNAVAILABLE",
        message="Nao existe rota disponivel",
        action="Habilite IA ou fallback manual.",
        correlation_id="orq-s1-correlation-001",
        observability_event_id="orqs1coreevt-abc123",
        stage="scaffold",
        context={"source_kind": "pdf"},
    )

    assert detail["code"] == "ROUTE_UNAVAILABLE"
    assert detail["observability_event_id"] == "orqs1coreevt-abc123"
    assert detail["stage"] == "scaffold"
    assert detail["context"]["source_kind"] == "pdf"
