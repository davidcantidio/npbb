"""Unit tests for XIA Sprint 4 backend telemetry helpers."""

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


def test_build_s4_extract_ai_telemetry_event_success() -> None:
    payload = telemetry.S4ExtractAITelemetryInput(
        event_name="etl_extract_ai_s4_plan_ready",
        correlation_id="xia-s4-correlation-001",
        event_message="Plano de extracao XIA S4 pronto",
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
        stage="service",
        context={"max_tokens_output": 4096},
    )
    event = telemetry.build_s4_extract_ai_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("xias4evt-")
    assert event.correlation_id == "xia-s4-correlation-001"
    assert event.source_kind == "pdf"
    assert event.model_provider == "openai"
    assert event.quality_profile_hint == "strict_textual"
    assert event.consolidation_scope == "cross_format_event"
    assert event.output_normalization_profile == "canonical_fields_v1"
    assert event.chunk_count == 2


def test_build_s4_extract_ai_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S4ExtractAITelemetryInput(
        event_name="etl_extract_ai_s4_plan_ready",
        correlation_id="xia-s4-correlation-001",
        event_message="Plano de extracao XIA S4 pronto",
        severity="debug",
    )

    with pytest.raises(telemetry.S4ExtractAITelemetryContractError) as exc:
        telemetry.build_s4_extract_ai_telemetry_event(payload)

    assert exc.value.code == "INVALID_XIA_S4_TELEMETRY_SEVERITY"


def test_build_s4_extract_ai_telemetry_event_rejects_invalid_chunk_count() -> None:
    payload = telemetry.S4ExtractAITelemetryInput(
        event_name="etl_extract_ai_s4_plan_ready",
        correlation_id="xia-s4-correlation-001",
        event_message="Plano de extracao XIA S4 pronto",
        severity="warning",
        chunk_count=0,
    )

    with pytest.raises(telemetry.S4ExtractAITelemetryContractError) as exc:
        telemetry.build_s4_extract_ai_telemetry_event(payload)

    assert exc.value.code == "INVALID_XIA_S4_TELEMETRY_CHUNK_COUNT"


def test_build_s4_extract_ai_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s4_extract_ai_error_detail(
        code="XIA_S4_EXTRACTION_FAILED",
        message="Execucao de extracao falhou",
        action="Revisar logs de execucao.",
        correlation_id="xia-s4-correlation-001",
        telemetry_event_id="xias4evt-abc123",
        stage="extraction",
        context={"model_provider": "openai"},
    )

    assert detail["code"] == "XIA_S4_EXTRACTION_FAILED"
    assert detail["telemetry_event_id"] == "xias4evt-abc123"
    assert detail["stage"] == "extraction"
    assert detail["context"]["model_provider"] == "openai"
