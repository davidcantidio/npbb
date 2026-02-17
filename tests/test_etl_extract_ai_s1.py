"""Unit tests for XIA Sprint 1 scaffold and service contracts."""

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
    S1AIExtractServiceError,
    build_s1_extract_ai_error_detail,
    execute_s1_extract_ai_service,
)
from etl.extract.ai.s1_scaffold import (  # noqa: E402
    S1AIExtractScaffoldError,
    S1AIExtractScaffoldRequest,
    build_s1_ai_extract_scaffold_contract,
)


def test_xia_s1_scaffold_success_returns_ready_plan() -> None:
    request = S1AIExtractScaffoldRequest(
        source_id="src pdf tmj 2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        document_profile_hint="pdf_digital",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="page",
        max_tokens_output=2048,
        temperature=0.1,
        correlation_id="xia-s1-test-001",
    )

    output = build_s1_ai_extract_scaffold_contract(request)

    assert output.contrato_versao == "xia.s1.v1"
    assert output.correlation_id == "xia-s1-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_PDF_TMJ_2025"
    assert output.extraction_plan["ia_model_provider"] == "openai"
    assert output.extraction_plan["chunk_strategy"] == "page"
    assert output.pontos_integracao["xia_s1_prepare_endpoint"] == "/internal/etl/extract/ai/s1/prepare"


def test_xia_s1_scaffold_rejects_invalid_source_kind() -> None:
    request = S1AIExtractScaffoldRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        correlation_id="xia-s1-invalid-kind",
    )

    with pytest.raises(S1AIExtractScaffoldError) as exc:
        build_s1_ai_extract_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_SOURCE_KIND"
    assert "pdf ou docx" in error.action


def test_xia_s1_service_success_returns_contract_and_observability() -> None:
    request = S1AIExtractScaffoldRequest(
        source_id="SRC_TMJ_DOCX_2025",
        source_kind="docx",
        source_uri="file:///tmp/tmj_2025.docx",
        document_profile_hint="docx_textual",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="section",
        max_tokens_output=1536,
        temperature=0.0,
        correlation_id="xia-s1-service-001",
    )

    output = execute_s1_extract_ai_service(request).to_dict()

    assert output["contrato_versao"] == "xia.s1.service.v1"
    assert output["correlation_id"] == "xia-s1-service-001"
    assert output["status"] == "ready"
    assert output["source_kind"] == "docx"
    assert output["extraction_plan"]["ia_model_name"] == "gpt-4.1-mini"
    assert output["observabilidade"]["flow_started_event_id"].startswith("xias1evt-")
    assert output["observabilidade"]["plan_ready_event_id"].startswith("xias1evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("xias1evt-")


def test_xia_s1_service_raises_actionable_error_for_invalid_temperature() -> None:
    request = S1AIExtractScaffoldRequest(
        source_id="SRC_TMJ_DOCX_2025",
        source_kind="docx",
        source_uri="file:///tmp/tmj_2025.docx",
        document_profile_hint="docx_textual",
        temperature=1.5,
        correlation_id="xia-s1-invalid-temperature",
    )

    with pytest.raises(S1AIExtractServiceError) as exc:
        execute_s1_extract_ai_service(request)

    error = exc.value
    assert error.code == "INVALID_TEMPERATURE"
    assert "entre 0 e 1" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("xias1evt-")


def test_xia_s1_error_detail_contract() -> None:
    detail = build_s1_extract_ai_error_detail(
        code="INVALID_TEMPERATURE",
        message="temperature invalida: 1.5",
        action="Use temperature entre 0 e 1.",
        correlation_id="xia-s1-error-001",
        event_id="xias1evt-abc123",
        stage="scaffold",
        context={"temperature": 1.5},
    )

    assert detail["code"] == "INVALID_TEMPERATURE"
    assert detail["correlation_id"] == "xia-s1-error-001"
    assert detail["event_id"] == "xias1evt-abc123"
    assert detail["stage"] == "scaffold"
    assert detail["context"]["temperature"] == 1.5
