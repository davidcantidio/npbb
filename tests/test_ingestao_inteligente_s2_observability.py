"""Unit tests for Sprint 2 frontend observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s2_observability import (  # noqa: E402
    S2ObservabilityError,
    S2ObservabilityInput,
    build_s2_actionable_error,
    build_s2_observability_event,
)


def test_build_s2_observability_event_success() -> None:
    payload = S2ObservabilityInput(
        event_name="ingestao_inteligente_s2_main_flow_started",
        correlation_id="s2-correlation-001",
        event_message="Fluxo principal da Sprint 2 iniciado",
        severity="info",
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123",
        context={"total_arquivos_lote": 2},
    )
    event = build_s2_observability_event(payload)

    assert event.observability_event_id.startswith("obs-")
    assert event.event_name == payload.event_name
    assert event.correlation_id == payload.correlation_id
    assert event.lote_id == payload.lote_id
    assert event.lote_upload_id == payload.lote_upload_id
    assert event.context == {"total_arquivos_lote": 2}
    assert event.to_response_dict()["correlation_id"] == "s2-correlation-001"


def test_build_s2_observability_event_rejects_invalid_severity() -> None:
    payload = S2ObservabilityInput(
        event_name="ingestao_inteligente_s2_main_flow_started",
        correlation_id="s2-correlation-001",
        event_message="Fluxo principal da Sprint 2 iniciado",
        severity="debug",
    )

    with pytest.raises(S2ObservabilityError) as exc:
        build_s2_observability_event(payload)

    assert exc.value.code == "INVALID_S2_OBSERVABILITY_SEVERITY"


def test_build_s2_actionable_error_returns_context() -> None:
    payload = build_s2_actionable_error(
        code="S2_MAIN_FLOW_FAILED",
        message="Falha no fluxo principal da sprint 2",
        action="Revisar logs operacionais com correlation_id.",
        correlation_id="s2-correlation-001",
        observability_event_id="obs-abc123",
        context={"stage": "response_validation", "lote_id": "lote_tmj_2025_001"},
    )

    assert payload["code"] == "S2_MAIN_FLOW_FAILED"
    assert payload["correlation_id"] == "s2-correlation-001"
    assert payload["observability_event_id"] == "obs-abc123"
    assert payload["context"]["stage"] == "response_validation"
