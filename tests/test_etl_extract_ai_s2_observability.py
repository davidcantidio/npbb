"""Unit tests for XIA Sprint 2 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.extract.ai.s2_observability import (  # noqa: E402
    S2ExtractAIObservabilityError,
    S2ExtractAIObservabilityInput,
    build_s2_extract_ai_actionable_error,
    build_s2_extract_ai_observability_event,
)


def test_build_s2_extract_ai_observability_event_success() -> None:
    payload = S2ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s2_main_flow_completed",
        correlation_id="xia-s2-correlation-001",
        event_message="Fluxo principal XIA S2 concluido",
        severity="info",
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="XLSX",
        source_uri="file:///tmp/tmj_2025.xlsx",
        model_provider="OPENAI",
        model_name="gpt-4.1-mini",
        chunk_strategy="SHEET",
        tabular_layout_hint="HEADER_SHIFTED",
        chunk_count=2,
        decision_reason="dry_run_main_flow",
        stage="main_flow",
        context={"max_tokens_output": 3072},
    )
    event = build_s2_extract_ai_observability_event(payload)

    assert event.observability_event_id.startswith("xias2coreevt-")
    assert event.correlation_id == "xia-s2-correlation-001"
    assert event.source_kind == "xlsx"
    assert event.model_provider == "openai"
    assert event.tabular_layout_hint == "header_shifted"
    assert event.chunk_count == 2


def test_build_s2_extract_ai_observability_event_rejects_invalid_severity() -> None:
    payload = S2ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s2_main_flow_completed",
        correlation_id="xia-s2-correlation-001",
        event_message="Fluxo principal XIA S2 concluido",
        severity="debug",
    )

    with pytest.raises(S2ExtractAIObservabilityError) as exc:
        build_s2_extract_ai_observability_event(payload)

    assert exc.value.code == "INVALID_XIA_S2_OBSERVABILITY_SEVERITY"


def test_build_s2_extract_ai_observability_event_rejects_invalid_chunk_count() -> None:
    payload = S2ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s2_main_flow_completed",
        correlation_id="xia-s2-correlation-001",
        event_message="Fluxo principal XIA S2 concluido",
        severity="warning",
        chunk_count=0,
    )

    with pytest.raises(S2ExtractAIObservabilityError) as exc:
        build_s2_extract_ai_observability_event(payload)

    assert exc.value.code == "INVALID_XIA_S2_OBSERVABILITY_CHUNK_COUNT"


def test_build_s2_extract_ai_actionable_error_includes_context() -> None:
    detail = build_s2_extract_ai_actionable_error(
        code="XIA_S2_EXTRACTION_FAILED",
        message="Execucao de extracao falhou",
        action="Revisar logs de execucao.",
        correlation_id="xia-s2-correlation-001",
        observability_event_id="xias2coreevt-abc123",
        stage="extraction",
        context={"model_provider": "openai"},
    )

    assert detail["code"] == "XIA_S2_EXTRACTION_FAILED"
    assert detail["observability_event_id"] == "xias2coreevt-abc123"
    assert detail["stage"] == "extraction"
    assert detail["context"]["model_provider"] == "openai"
