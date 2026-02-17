"""Unit tests for XIA Sprint 2 scaffold and service contracts."""

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
    S2AIExtractServiceError,
    execute_s2_extract_ai_service,
)
from etl.extract.ai.s2_scaffold import (  # noqa: E402
    S2AIExtractScaffoldError,
    S2AIExtractScaffoldRequest,
    build_s2_ai_extract_scaffold_contract,
)


def test_xia_s2_scaffold_success_returns_ready_plan() -> None:
    request = S2AIExtractScaffoldRequest(
        source_id="src pptx tmj 2025",
        source_kind="pptx",
        source_uri="file:///tmp/tmj_2025.pptx",
        document_profile_hint="pptx_social_metrics",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="slide",
        max_tokens_output=3072,
        temperature=0.1,
        correlation_id="xia-s2-test-001",
    )

    output = build_s2_ai_extract_scaffold_contract(request)

    assert output.contrato_versao == "xia.s2.v1"
    assert output.correlation_id == "xia-s2-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_PPTX_TMJ_2025"
    assert output.extraction_plan["ia_model_provider"] == "openai"
    assert output.extraction_plan["chunk_strategy"] == "slide"
    assert output.pontos_integracao["xia_s2_prepare_endpoint"] == "/internal/etl/extract/ai/s2/prepare"


def test_xia_s2_scaffold_rejects_invalid_chunk_strategy_for_pptx() -> None:
    request = S2AIExtractScaffoldRequest(
        source_id="SRC_TMJ_PPTX_2025",
        source_kind="pptx",
        source_uri="file:///tmp/tmj_2025.pptx",
        chunk_strategy="sheet",
        correlation_id="xia-s2-invalid-chunk-pptx",
    )

    with pytest.raises(S2AIExtractScaffoldError) as exc:
        build_s2_ai_extract_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_CHUNK_STRATEGY_FOR_PPTX"
    assert "chunk_strategy=slide" in error.action


def test_xia_s2_service_success_returns_contract_and_observability() -> None:
    request = S2AIExtractScaffoldRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        document_profile_hint="xlsx_non_standard",
        tabular_layout_hint="header_shifted",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="sheet",
        max_tokens_output=2048,
        temperature=0.0,
        correlation_id="xia-s2-service-001",
    )

    output = execute_s2_extract_ai_service(request).to_dict()

    assert output["contrato_versao"] == "xia.s2.service.v1"
    assert output["correlation_id"] == "xia-s2-service-001"
    assert output["status"] == "ready"
    assert output["source_kind"] == "xlsx"
    assert output["extraction_plan"]["tabular_layout_hint"] == "header_shifted"
    assert output["observabilidade"]["flow_started_event_id"].startswith("xias2evt-")
    assert output["observabilidade"]["plan_ready_event_id"].startswith("xias2evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("xias2evt-")


def test_xia_s2_service_raises_actionable_error_for_invalid_tabular_hint() -> None:
    request = S2AIExtractScaffoldRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        tabular_layout_hint="invalid_hint",
        correlation_id="xia-s2-invalid-layout-hint",
    )

    with pytest.raises(S2AIExtractServiceError) as exc:
        execute_s2_extract_ai_service(request)

    error = exc.value
    assert error.code == "INVALID_TABULAR_LAYOUT_HINT"
    assert "layout hint valido" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("xias2evt-")
