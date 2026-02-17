"""Unit tests for XIA Sprint 3 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from etl.extract.ai.s3_observability import (  # noqa: E402
    S3ExtractAIObservabilityError,
    S3ExtractAIObservabilityInput,
    build_s3_extract_ai_actionable_error,
    build_s3_extract_ai_observability_event,
)


def test_build_s3_extract_ai_observability_event_success() -> None:
    payload = S3ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s3_main_flow_completed",
        correlation_id="xia-s3-correlation-001",
        event_message="Fluxo principal XIA S3 concluido",
        severity="info",
        source_id="SRC_TMJ_PDFSCAN_2025",
        source_kind="PDF_SCAN",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        model_provider="OPENAI",
        model_name="gpt-4.1-mini",
        chunk_strategy="PAGE",
        image_preprocess_hint="OCR_ENHANCED",
        chunk_count=2,
        decision_reason="dry_run_main_flow",
        stage="main_flow",
        context={"max_tokens_output": 4096},
    )
    event = build_s3_extract_ai_observability_event(payload)

    assert event.observability_event_id.startswith("xias3coreevt-")
    assert event.correlation_id == "xia-s3-correlation-001"
    assert event.source_kind == "pdf_scan"
    assert event.model_provider == "openai"
    assert event.image_preprocess_hint == "ocr_enhanced"
    assert event.chunk_count == 2


def test_build_s3_extract_ai_observability_event_rejects_invalid_severity() -> None:
    payload = S3ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s3_main_flow_completed",
        correlation_id="xia-s3-correlation-001",
        event_message="Fluxo principal XIA S3 concluido",
        severity="debug",
    )

    with pytest.raises(S3ExtractAIObservabilityError) as exc:
        build_s3_extract_ai_observability_event(payload)

    assert exc.value.code == "INVALID_XIA_S3_OBSERVABILITY_SEVERITY"


def test_build_s3_extract_ai_observability_event_rejects_invalid_chunk_count() -> None:
    payload = S3ExtractAIObservabilityInput(
        event_name="etl_extract_ai_s3_main_flow_completed",
        correlation_id="xia-s3-correlation-001",
        event_message="Fluxo principal XIA S3 concluido",
        severity="warning",
        chunk_count=0,
    )

    with pytest.raises(S3ExtractAIObservabilityError) as exc:
        build_s3_extract_ai_observability_event(payload)

    assert exc.value.code == "INVALID_XIA_S3_OBSERVABILITY_CHUNK_COUNT"


def test_build_s3_extract_ai_actionable_error_includes_context() -> None:
    detail = build_s3_extract_ai_actionable_error(
        code="XIA_S3_EXTRACTION_FAILED",
        message="Execucao de extracao falhou",
        action="Revisar logs de execucao.",
        correlation_id="xia-s3-correlation-001",
        observability_event_id="xias3coreevt-abc123",
        stage="extraction",
        context={"model_provider": "openai"},
    )

    assert detail["code"] == "XIA_S3_EXTRACTION_FAILED"
    assert detail["observability_event_id"] == "xias3coreevt-abc123"
    assert detail["stage"] == "extraction"
    assert detail["context"]["model_provider"] == "openai"
