"""Unit tests for XIA Sprint 4 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.extract.ai.s4_observability import (  # noqa: E402
    S4ExtractAIObservabilityError,
    S4ExtractAIObservabilityInput,
    build_s4_extract_ai_actionable_error,
    build_s4_extract_ai_observability_event,
)


def test_build_s4_extract_ai_observability_event_success() -> None:
    payload = S4ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s4_main_flow_completed",
        correlation_id="xia-s4-correlation-001",
        event_message="Fluxo principal XIA S4 concluido",
        severity="info",
        source_id="SRC_TMJ_S4_PDF_2025",
        source_kind="PDF",
        source_uri="file:///tmp/tmj_2025.pdf",
        model_provider="OPENAI",
        model_name="gpt-4.1-mini",
        chunk_strategy="PAGE",
        quality_profile_hint="STRICT_TEXTUAL",
        consolidation_scope="CROSS_FORMAT_EVENT",
        output_normalization_profile="CANONICAL_FIELDS_V1",
        chunk_count=2,
        decision_reason="dry_run_main_flow",
        stage="main_flow",
        context={"max_tokens_output": 4096},
    )
    event = build_s4_extract_ai_observability_event(payload)

    assert event.observability_event_id.startswith("xias4coreevt-")
    assert event.correlation_id == "xia-s4-correlation-001"
    assert event.source_kind == "pdf"
    assert event.model_provider == "openai"
    assert event.quality_profile_hint == "strict_textual"
    assert event.consolidation_scope == "cross_format_event"
    assert event.output_normalization_profile == "canonical_fields_v1"
    assert event.chunk_count == 2


def test_build_s4_extract_ai_observability_event_rejects_invalid_severity() -> None:
    payload = S4ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s4_main_flow_completed",
        correlation_id="xia-s4-correlation-001",
        event_message="Fluxo principal XIA S4 concluido",
        severity="debug",
    )

    with pytest.raises(S4ExtractAIObservabilityError) as exc:
        build_s4_extract_ai_observability_event(payload)

    assert exc.value.code == "INVALID_XIA_S4_OBSERVABILITY_SEVERITY"


def test_build_s4_extract_ai_observability_event_rejects_invalid_chunk_count() -> None:
    payload = S4ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s4_main_flow_completed",
        correlation_id="xia-s4-correlation-001",
        event_message="Fluxo principal XIA S4 concluido",
        severity="warning",
        chunk_count=0,
    )

    with pytest.raises(S4ExtractAIObservabilityError) as exc:
        build_s4_extract_ai_observability_event(payload)

    assert exc.value.code == "INVALID_XIA_S4_OBSERVABILITY_CHUNK_COUNT"


def test_build_s4_extract_ai_actionable_error_includes_context() -> None:
    detail = build_s4_extract_ai_actionable_error(
        code="XIA_S4_EXTRACTION_FAILED",
        message="Execucao de extracao falhou",
        action="Revisar logs de execucao.",
        correlation_id="xia-s4-correlation-001",
        observability_event_id="xias4coreevt-abc123",
        stage="extraction",
        context={"model_provider": "openai"},
    )

    assert detail["code"] == "XIA_S4_EXTRACTION_FAILED"
    assert detail["observability_event_id"] == "xias4coreevt-abc123"
    assert detail["stage"] == "extraction"
    assert detail["context"]["model_provider"] == "openai"
