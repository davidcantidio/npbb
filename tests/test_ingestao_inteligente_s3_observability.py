"""Unit tests for Sprint 3 frontend observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s3_observability import (  # noqa: E402
    S3ObservabilityError,
    S3ObservabilityInput,
    build_s3_actionable_error,
    build_s3_observability_event,
)


def test_build_s3_observability_event_success() -> None:
    payload = S3ObservabilityInput(
        event_name="ingestao_inteligente_s3_main_flow_started",
        correlation_id="s3-correlation-001",
        event_message="Fluxo principal da Sprint 3 iniciado",
        severity="info",
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="LOT-ABC123",
        status_processamento="FAILED",
        tentativas_reprocessamento=1,
        context={"proxima_acao": "avaliar_reprocessamento_lote"},
    )
    event = build_s3_observability_event(payload)

    assert event.observability_event_id.startswith("obs-")
    assert event.event_name == payload.event_name
    assert event.correlation_id == payload.correlation_id
    assert event.lote_id == payload.lote_id
    assert event.lote_upload_id == "lot-abc123"
    assert event.status_processamento == "failed"
    assert event.tentativas_reprocessamento == 1
    assert event.context == {"proxima_acao": "avaliar_reprocessamento_lote"}
    assert event.to_response_dict()["correlation_id"] == "s3-correlation-001"


def test_build_s3_observability_event_rejects_invalid_severity() -> None:
    payload = S3ObservabilityInput(
        event_name="ingestao_inteligente_s3_main_flow_started",
        correlation_id="s3-correlation-001",
        event_message="Fluxo principal da Sprint 3 iniciado",
        severity="debug",
    )

    with pytest.raises(S3ObservabilityError) as exc:
        build_s3_observability_event(payload)

    assert exc.value.code == "INVALID_S3_OBSERVABILITY_SEVERITY"


def test_build_s3_observability_event_rejects_negative_reprocess_attempts() -> None:
    payload = S3ObservabilityInput(
        event_name="ingestao_inteligente_s3_main_flow_started",
        correlation_id="s3-correlation-001",
        event_message="Fluxo principal da Sprint 3 iniciado",
        severity="warning",
        tentativas_reprocessamento=-1,
    )

    with pytest.raises(S3ObservabilityError) as exc:
        build_s3_observability_event(payload)

    assert exc.value.code == "INVALID_S3_OBSERVABILITY_REPROCESS_ATTEMPTS"


def test_build_s3_actionable_error_returns_context() -> None:
    payload = build_s3_actionable_error(
        code="S3_MAIN_FLOW_FAILED",
        message="Falha no fluxo principal da sprint 3",
        action="Revisar logs operacionais com correlation_id.",
        correlation_id="s3-correlation-001",
        observability_event_id="obs-abc123",
        context={"stage": "status_response_validation", "lote_id": "lote_tmj_2025_001"},
    )

    assert payload["code"] == "S3_MAIN_FLOW_FAILED"
    assert payload["correlation_id"] == "s3-correlation-001"
    assert payload["observability_event_id"] == "obs-abc123"
    assert payload["context"]["stage"] == "status_response_validation"
