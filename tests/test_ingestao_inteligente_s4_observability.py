"""Unit tests for Sprint 4 frontend observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s4_observability import (  # noqa: E402
    S4ObservabilityError,
    S4ObservabilityInput,
    build_s4_actionable_error,
    build_s4_observability_event,
)


def test_build_s4_observability_event_success() -> None:
    payload = S4ObservabilityInput(
        event_name="ingestao_inteligente_s4_main_flow_started",
        correlation_id="s4-correlation-001",
        event_message="Fluxo principal da Sprint 4 iniciado",
        severity="info",
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="LOT-ABC123",
        status_processamento="PROCESSING",
        proxima_acao="monitorar_status_lote",
        codigo_mensagem="S4_MONITORING_IN_PROGRESS",
        severidade_mensagem="WARNING",
        destino_acao_principal="manter_monitoramento_status",
        context={"fase": "ux_dispatch"},
    )
    event = build_s4_observability_event(payload)

    assert event.observability_event_id.startswith("obs-")
    assert event.event_name == payload.event_name
    assert event.correlation_id == payload.correlation_id
    assert event.lote_id == payload.lote_id
    assert event.lote_upload_id == "lot-abc123"
    assert event.status_processamento == "processing"
    assert event.severidade_mensagem == "warning"
    assert event.destino_acao_principal == "manter_monitoramento_status"
    assert event.context == {"fase": "ux_dispatch"}
    assert event.to_response_dict()["correlation_id"] == "s4-correlation-001"


def test_build_s4_observability_event_rejects_invalid_severity() -> None:
    payload = S4ObservabilityInput(
        event_name="ingestao_inteligente_s4_main_flow_started",
        correlation_id="s4-correlation-001",
        event_message="Fluxo principal da Sprint 4 iniciado",
        severity="debug",
    )

    with pytest.raises(S4ObservabilityError) as exc:
        build_s4_observability_event(payload)

    assert exc.value.code == "INVALID_S4_OBSERVABILITY_SEVERITY"


def test_build_s4_observability_event_rejects_invalid_message_severity() -> None:
    payload = S4ObservabilityInput(
        event_name="ingestao_inteligente_s4_main_flow_started",
        correlation_id="s4-correlation-001",
        event_message="Fluxo principal da Sprint 4 iniciado",
        severity="warning",
        severidade_mensagem="critical",
    )

    with pytest.raises(S4ObservabilityError) as exc:
        build_s4_observability_event(payload)

    assert exc.value.code == "INVALID_S4_MESSAGE_SEVERITY"


def test_build_s4_actionable_error_returns_context() -> None:
    payload = build_s4_actionable_error(
        code="S4_MAIN_FLOW_FAILED",
        message="Falha no fluxo principal da sprint 4",
        action="Revisar logs operacionais com correlation_id.",
        correlation_id="s4-correlation-001",
        observability_event_id="obs-abc123",
        context={"stage": "ux_response_validation", "lote_id": "lote_tmj_2025_001"},
    )

    assert payload["code"] == "S4_MAIN_FLOW_FAILED"
    assert payload["correlation_id"] == "s4-correlation-001"
    assert payload["observability_event_id"] == "obs-abc123"
    assert payload["context"]["stage"] == "ux_response_validation"
