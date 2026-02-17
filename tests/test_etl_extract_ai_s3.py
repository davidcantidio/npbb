"""Unit tests for XIA Sprint 3 scaffold and service contracts."""

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
    S3AIExtractServiceError,
    execute_s3_extract_ai_service,
)
from etl.extract.ai.s3_scaffold import (  # noqa: E402
    S3AIExtractScaffoldError,
    S3AIExtractScaffoldRequest,
    build_s3_ai_extract_scaffold_contract,
)


def test_xia_s3_scaffold_success_returns_ready_plan() -> None:
    request = S3AIExtractScaffoldRequest(
        source_id="src pdfscan tmj 2025",
        source_kind="pdf_scan",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        document_profile_hint="pdf_scan_document",
        image_preprocess_hint="ocr_enhanced",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="page",
        max_tokens_output=4096,
        temperature=0.1,
        correlation_id="xia-s3-test-001",
    )

    output = build_s3_ai_extract_scaffold_contract(request)

    assert output.contrato_versao == "xia.s3.v1"
    assert output.correlation_id == "xia-s3-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_PDFSCAN_TMJ_2025"
    assert output.extraction_plan["ia_model_provider"] == "openai"
    assert output.extraction_plan["chunk_strategy"] == "page"
    assert output.pontos_integracao["xia_s3_prepare_endpoint"] == "/internal/etl/extract/ai/s3/prepare"


def test_xia_s3_scaffold_rejects_invalid_chunk_strategy_for_pdf_scan() -> None:
    request = S3AIExtractScaffoldRequest(
        source_id="SRC_TMJ_PDFSCAN_2025",
        source_kind="pdf_scan",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        image_preprocess_hint="deskew",
        chunk_strategy="region",
        correlation_id="xia-s3-invalid-chunk-pdfscan",
    )

    with pytest.raises(S3AIExtractScaffoldError) as exc:
        build_s3_ai_extract_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_CHUNK_STRATEGY_FOR_PDF_SCAN"
    assert "chunk_strategy=page" in error.action


def test_xia_s3_service_success_returns_contract_and_observability() -> None:
    request = S3AIExtractScaffoldRequest(
        source_id="SRC_TMJ_JPG_2025",
        source_kind="jpg",
        source_uri="file:///tmp/tmj_2025.jpg",
        document_profile_hint="image_document",
        image_preprocess_hint="denoise",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="image",
        max_tokens_output=2048,
        temperature=0.0,
        correlation_id="xia-s3-service-001",
    )

    output = execute_s3_extract_ai_service(request).to_dict()

    assert output["contrato_versao"] == "xia.s3.service.v1"
    assert output["correlation_id"] == "xia-s3-service-001"
    assert output["status"] == "ready"
    assert output["source_kind"] == "jpg"
    assert output["extraction_plan"]["image_preprocess_hint"] == "denoise"
    assert output["observabilidade"]["flow_started_event_id"].startswith("xias3evt-")
    assert output["observabilidade"]["plan_ready_event_id"].startswith("xias3evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("xias3evt-")


def test_xia_s3_service_raises_actionable_error_for_invalid_preprocess_hint() -> None:
    request = S3AIExtractScaffoldRequest(
        source_id="SRC_TMJ_PNG_2025",
        source_kind="png",
        source_uri="file:///tmp/tmj_2025.png",
        image_preprocess_hint="invalid_hint",
        correlation_id="xia-s3-invalid-preprocess",
    )

    with pytest.raises(S3AIExtractServiceError) as exc:
        execute_s3_extract_ai_service(request)

    error = exc.value
    assert error.code == "INVALID_IMAGE_PREPROCESS_HINT"
    assert "image_preprocess_hint valido" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("xias3evt-")
