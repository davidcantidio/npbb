"""Unit tests for XIA Sprint 3 backend telemetry helpers."""

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
    "app.services.extra-o-ia-por-formato-delimitado_telemetry"
)


def test_build_s3_extract_ai_telemetry_event_success() -> None:
    payload = telemetry.S3ExtractAITelemetryInput(
        event_name="etl_extract_ai_s3_plan_ready",
        correlation_id="xia-s3-correlation-001",
        event_message="Plano de extracao XIA S3 pronto",
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
        stage="service",
        context={"max_tokens_output": 4096},
    )
    event = telemetry.build_s3_extract_ai_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("xias3evt-")
    assert event.correlation_id == "xia-s3-correlation-001"
    assert event.source_kind == "pdf_scan"
    assert event.model_provider == "openai"
    assert event.image_preprocess_hint == "ocr_enhanced"
    assert event.chunk_count == 2


def test_build_s3_extract_ai_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S3ExtractAITelemetryInput(
        event_name="etl_extract_ai_s3_plan_ready",
        correlation_id="xia-s3-correlation-001",
        event_message="Plano de extracao XIA S3 pronto",
        severity="debug",
    )

    with pytest.raises(telemetry.S3ExtractAITelemetryContractError) as exc:
        telemetry.build_s3_extract_ai_telemetry_event(payload)

    assert exc.value.code == "INVALID_XIA_S3_TELEMETRY_SEVERITY"


def test_build_s3_extract_ai_telemetry_event_rejects_invalid_chunk_count() -> None:
    payload = telemetry.S3ExtractAITelemetryInput(
        event_name="etl_extract_ai_s3_plan_ready",
        correlation_id="xia-s3-correlation-001",
        event_message="Plano de extracao XIA S3 pronto",
        severity="warning",
        chunk_count=0,
    )

    with pytest.raises(telemetry.S3ExtractAITelemetryContractError) as exc:
        telemetry.build_s3_extract_ai_telemetry_event(payload)

    assert exc.value.code == "INVALID_XIA_S3_TELEMETRY_CHUNK_COUNT"


def test_build_s3_extract_ai_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s3_extract_ai_error_detail(
        code="XIA_S3_EXTRACTION_FAILED",
        message="Execucao de extracao falhou",
        action="Revisar logs de execucao.",
        correlation_id="xia-s3-correlation-001",
        telemetry_event_id="xias3evt-abc123",
        stage="extraction",
        context={"model_provider": "openai"},
    )

    assert detail["code"] == "XIA_S3_EXTRACTION_FAILED"
    assert detail["telemetry_event_id"] == "xias3evt-abc123"
    assert detail["stage"] == "extraction"
    assert detail["context"]["model_provider"] == "openai"
