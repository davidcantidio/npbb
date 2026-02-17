"""Unit tests for XIA Sprint 4 scaffold and service contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.etl_extract_ai_service import (  # noqa: E402
    S4AIExtractServiceError,
    execute_s4_extract_ai_service,
)
from etl.extract.ai.s4_scaffold import (  # noqa: E402
    S4AIExtractScaffoldError,
    S4AIExtractScaffoldRequest,
    build_s4_ai_extract_scaffold_contract,
)


def test_xia_s4_scaffold_success_returns_ready_plan() -> None:
    request = S4AIExtractScaffoldRequest(
        source_id="src sprint4 tmj 2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        quality_profile_hint="strict_textual",
        consolidation_scope="cross_format_event",
        output_normalization_profile="canonical_fields_v1",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="section",
        max_tokens_output=4096,
        temperature=0.1,
        correlation_id="xia-s4-test-001",
    )

    output = build_s4_ai_extract_scaffold_contract(request)

    assert output.contrato_versao == "xia.s4.v1"
    assert output.correlation_id == "xia-s4-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_SPRINT4_TMJ_2025"
    assert output.extraction_plan["consolidation_scope"] == "cross_format_event"
    assert output.pontos_integracao["xia_s4_prepare_endpoint"] == "/internal/etl/extract/ai/s4/prepare"


def test_xia_s4_scaffold_rejects_invalid_quality_profile_hint() -> None:
    request = S4AIExtractScaffoldRequest(
        source_id="SRC_TMJ_S4_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        quality_profile_hint="invalid_hint",
        correlation_id="xia-s4-invalid-quality",
    )

    with pytest.raises(S4AIExtractScaffoldError) as exc:
        build_s4_ai_extract_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_QUALITY_PROFILE_HINT"
    assert "quality_profile_hint valido" in error.action


def test_xia_s4_service_success_returns_contract_and_observability() -> None:
    request = S4AIExtractScaffoldRequest(
        source_id="SRC_TMJ_S4_PPTX_2025",
        source_kind="pptx",
        source_uri="file:///tmp/tmj_2025.pptx",
        quality_profile_hint="table_sensitive",
        consolidation_scope="batch_session",
        output_normalization_profile="canonical_fields_v2",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="slide",
        max_tokens_output=3072,
        temperature=0.0,
        correlation_id="xia-s4-service-001",
    )

    output = execute_s4_extract_ai_service(request).to_dict()

    assert output["contrato_versao"] == "xia.s4.service.v1"
    assert output["correlation_id"] == "xia-s4-service-001"
    assert output["status"] == "ready"
    assert output["source_kind"] == "pptx"
    assert output["extraction_plan"]["quality_profile_hint"] == "table_sensitive"
    assert output["execucao"]["status"] == "not_started"
    assert output["observabilidade"]["flow_started_event_id"].startswith("xias4evt-")
    assert output["observabilidade"]["plan_ready_event_id"].startswith("xias4evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("xias4evt-")


def test_xia_s4_service_raises_actionable_error_for_invalid_chunk_strategy() -> None:
    request = S4AIExtractScaffoldRequest(
        source_id="SRC_TMJ_S4_PDFSCAN_2025",
        source_kind="pdf_scan",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        quality_profile_hint="ocr_resilient",
        chunk_strategy="image",
        correlation_id="xia-s4-invalid-chunk",
    )

    with pytest.raises(S4AIExtractServiceError) as exc:
        execute_s4_extract_ai_service(request)

    error = exc.value
    assert error.code == "INVALID_CHUNK_STRATEGY_FOR_SOURCE_KIND"
    assert "source_kind=pdf_scan" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("xias4evt-")
