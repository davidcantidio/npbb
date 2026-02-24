"""Unit tests for ORQ Sprint 1 scaffold and service contracts."""

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

from app.services.etl_orchestrator_service import (  # noqa: E402
    S1OrchestratorServiceError,
    build_s1_orchestrator_error_detail,
    execute_s1_orchestrator_service,
)
from etl.orchestrator.s1_core import (  # noqa: E402
    S1OrchestratorCoreError,
    S1OrchestratorCoreInput,
    execute_s1_orchestrator_main_flow,
)
from etl.orchestrator.s1_scaffold import (  # noqa: E402
    S1OrchestratorRequest,
    S1OrchestratorScaffoldError,
    build_s1_scaffold_contract,
)


def test_s1_orchestrator_scaffold_success_for_pdf_hybrid_route() -> None:
    request = S1OrchestratorRequest(
        source_id="src pdf tmj 2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        profile_strategy_hint="hybrid",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        correlation_id="orq-s1-test-001",
    )

    result = build_s1_scaffold_contract(request)

    assert result.contrato_versao == "orq.s1.v1"
    assert result.correlation_id == "orq-s1-test-001"
    assert result.status == "ready"
    assert result.source_id == "SRC_PDF_TMJ_2025"
    assert result.rota_selecionada == "hybrid_pdf_extract"
    assert result.politica_roteamento["modo_roteamento"] == "hibrido"
    assert result.pontos_integracao["orq_s1_route_endpoint"] == "/internal/etl/orchestrator/s1/route"


def test_s1_orchestrator_scaffold_rejects_invalid_source_kind() -> None:
    request = S1OrchestratorRequest(
        source_id="SRC_TMJ_INVALID_KIND",
        source_kind="json",
        source_uri="file:///tmp/data.json",
        profile_strategy_hint=None,
        correlation_id="orq-s1-test-invalid-kind",
    )

    with pytest.raises(S1OrchestratorScaffoldError) as exc:
        build_s1_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_SOURCE_KIND"
    assert "source_kind suportado" in error.action


def test_s1_orchestrator_core_success_returns_contract_and_observability() -> None:
    flow_input = S1OrchestratorCoreInput(
        source_id="SRC_TMJ_DOCX_2025",
        source_kind="docx",
        source_uri="file:///tmp/tmj_2025.docx",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        correlation_id="orq-s1-core-001",
    )

    output = execute_s1_orchestrator_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "orq.s1.core.v1"
    assert output["correlation_id"] == "orq-s1-core-001"
    assert output["status"] == "ready"
    assert output["rota_selecionada"] == "hybrid_document_extract"
    assert output["observabilidade"]["flow_started_event_id"].startswith("orqs1coreevt-")
    assert output["observabilidade"]["route_resolved_event_id"].startswith("orqs1coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("orqs1coreevt-")


def test_s1_orchestrator_core_raises_actionable_error_for_route_unavailable() -> None:
    flow_input = S1OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        profile_strategy_hint="ocr_or_assisted",
        ia_habilitada=False,
        permitir_fallback_manual=False,
        correlation_id="orq-s1-core-route-unavailable",
    )

    with pytest.raises(S1OrchestratorCoreError) as exc:
        execute_s1_orchestrator_main_flow(flow_input)

    error = exc.value
    assert error.code == "ROUTE_UNAVAILABLE"
    assert error.stage == "scaffold"
    assert "Habilite IA ou fallback manual" in error.action
    assert (error.event_id or "").startswith("orqs1coreevt-")


def test_s1_orchestrator_service_success_returns_contract_and_observability() -> None:
    request = S1OrchestratorRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        ia_habilitada=False,
        permitir_fallback_manual=True,
        correlation_id="orq-s1-service-001",
    )

    output = execute_s1_orchestrator_service(request).to_dict()

    assert output["contrato_versao"] == "orq.s1.service.v1"
    assert output["correlation_id"] == "orq-s1-service-001"
    assert output["status"] == "ready"
    assert output["rota_selecionada"] == "deterministic_tabular_extract"
    assert output["observabilidade"]["flow_started_event_id"].startswith("orqs1evt-")
    assert output["observabilidade"]["route_decision_event_id"].startswith("orqs1evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("orqs1evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("orqs1coreevt-")
    assert output["observabilidade"]["main_flow_route_event_id"].startswith("orqs1coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("orqs1coreevt-")


def test_s1_orchestrator_service_raises_actionable_error_for_route_unavailable() -> None:
    request = S1OrchestratorRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        profile_strategy_hint="ocr_or_assisted",
        ia_habilitada=False,
        permitir_fallback_manual=False,
        correlation_id="orq-s1-service-route-unavailable",
    )

    with pytest.raises(S1OrchestratorServiceError) as exc:
        execute_s1_orchestrator_service(request)

    error = exc.value
    assert error.code == "ROUTE_UNAVAILABLE"
    assert "Habilite IA ou fallback manual" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("orqs1evt-")


def test_s1_orchestrator_error_detail_contract() -> None:
    payload = build_s1_orchestrator_error_detail(
        code="ROUTE_UNAVAILABLE",
        message="Nao existe rota disponivel",
        action="Habilite fallback manual.",
        correlation_id="orq-s1-error-001",
        event_id="orqs1evt-abc123",
        stage="scaffold",
        context={"source_id": "SRC_TMJ_PDF_2025"},
    )

    assert payload["code"] == "ROUTE_UNAVAILABLE"
    assert payload["correlation_id"] == "orq-s1-error-001"
    assert payload["event_id"] == "orqs1evt-abc123"
    assert payload["telemetry_event_id"] == "orqs1evt-abc123"
    assert payload["stage"] == "scaffold"
    assert payload["context"]["source_id"] == "SRC_TMJ_PDF_2025"
