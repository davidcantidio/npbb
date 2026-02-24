"""Unit tests for ORQ Sprint 2 scaffold and service contracts."""

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
    S2OrchestratorServiceError,
    build_s2_orchestrator_error_detail,
    execute_s2_orchestrator_service,
)
from etl.orchestrator.s2_core import (  # noqa: E402
    S2OrchestratorCoreError,
    S2OrchestratorCoreInput,
    execute_s2_orchestrator_main_flow,
)
from etl.orchestrator.s2_scaffold import (  # noqa: E402
    S2OrchestratorScaffoldError,
    S2OrchestratorScaffoldRequest,
    build_s2_scaffold_contract,
)


def test_s2_orchestrator_scaffold_success_returns_execution_plan() -> None:
    request = S2OrchestratorScaffoldRequest(
        source_id="src pdf tmj 2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        retry_attempts=1,
        timeout_seconds=240,
        correlation_id="orq-s2-test-001",
    )

    output = build_s2_scaffold_contract(request)

    assert output.contrato_versao == "orq.s2.v1"
    assert output.correlation_id == "orq-s2-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_PDF_TMJ_2025"
    assert output.rota_selecionada == "hybrid_pdf_extract"
    assert output.plano_execucao["executor_strategy"] == "hibrido"
    assert output.plano_execucao["queue_name"] == "orq_s2_hybrid_pdf"
    assert output.pontos_integracao["orq_s2_prepare_endpoint"] == "/internal/etl/orchestrator/s2/prepare"


def test_s2_orchestrator_scaffold_rejects_invalid_route_for_source_kind() -> None:
    request = S2OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        rota_selecionada="hybrid_pdf_extract",
        correlation_id="orq-s2-invalid-route",
    )

    with pytest.raises(S2OrchestratorScaffoldError) as exc:
        build_s2_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_ROUTE_FOR_SOURCE_KIND"
    assert "Ajuste rota_selecionada" in error.action


def test_s2_orchestrator_core_success_runs_deterministic_first() -> None:
    flow_input = S2OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        retry_attempts=1,
        timeout_seconds=240,
        correlation_id="orq-s2-core-001",
    )

    output = execute_s2_orchestrator_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "orq.s2.core.v1"
    assert output["correlation_id"] == "orq-s2-core-001"
    assert output["status"] == "completed"
    assert output["rota_selecionada"] == "deterministic_pdf_extract"
    assert output["execucao"]["route_chain"][0] == "deterministic_pdf_extract"
    assert output["execucao"]["fallback_activated"] is False
    assert output["observabilidade"]["flow_started_event_id"].startswith("orqs2coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("orqs2coreevt-")


def test_s2_orchestrator_core_uses_fallback_when_deterministic_route_fails() -> None:
    flow_input = S2OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        retry_attempts=0,
        timeout_seconds=240,
        correlation_id="orq-s2-core-fallback",
    )

    def fake_executor(route_name: str, route_context: dict[str, object]) -> dict[str, object]:
        if route_name == "deterministic_pdf_extract":
            return {"status": "failed", "message": "deterministic failed"}
        return {"status": "succeeded", "message": f"{route_name} succeeded", "ctx": route_context}

    output = execute_s2_orchestrator_main_flow(flow_input, execute_route=fake_executor).to_dict()

    assert output["status"] == "completed"
    assert output["rota_selecionada"] == "hybrid_pdf_extract"
    assert output["execucao"]["fallback_activated"] is True
    assert output["execucao"]["route_chain"][0] == "deterministic_pdf_extract"
    assert output["execucao"]["route_chain"][1] == "hybrid_pdf_extract"
    assert len(output["execucao"]["attempts_trace"]) >= 2


def test_s2_orchestrator_core_raises_error_when_route_chain_is_exhausted() -> None:
    flow_input = S2OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        ia_habilitada=True,
        permitir_fallback_manual=True,
        retry_attempts=0,
        timeout_seconds=240,
        correlation_id="orq-s2-core-exhausted",
    )

    def fail_executor(route_name: str, route_context: dict[str, object]) -> dict[str, object]:
        return {"status": "failed", "message": f"{route_name} failed", "ctx": route_context}

    with pytest.raises(S2OrchestratorCoreError) as exc:
        execute_s2_orchestrator_main_flow(flow_input, execute_route=fail_executor)

    error = exc.value
    assert error.code == "ORQ_S2_ROUTE_CHAIN_EXHAUSTED"
    assert "fallback/retry" in error.action
    assert error.stage == "route_execution"
    assert (error.event_id or "").startswith("orqs2coreevt-")


def test_s2_orchestrator_service_success_returns_contract_and_observability() -> None:
    request = S2OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        rota_selecionada="deterministic_tabular_extract",
        ia_habilitada=False,
        permitir_fallback_manual=True,
        retry_attempts=0,
        timeout_seconds=180,
        correlation_id="orq-s2-service-001",
    )

    output = execute_s2_orchestrator_service(request).to_dict()

    assert output["contrato_versao"] == "orq.s2.service.v1"
    assert output["correlation_id"] == "orq-s2-service-001"
    assert output["status"] == "completed"
    assert output["rota_selecionada"] == "deterministic_tabular_extract"
    assert output["observabilidade"]["scaffold_started_event_id"].startswith("orqs2evt-")
    assert output["observabilidade"]["route_decision_event_id"].startswith("orqs2evt-")
    assert output["observabilidade"]["scaffold_completed_event_id"].startswith("orqs2evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("orqs2coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("orqs2coreevt-")


def test_s2_orchestrator_service_raises_actionable_error_for_invalid_timeout() -> None:
    request = S2OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        timeout_seconds=10,
        correlation_id="orq-s2-invalid-timeout",
    )

    with pytest.raises(S2OrchestratorServiceError) as exc:
        execute_s2_orchestrator_service(request)

    error = exc.value
    assert error.code == "INVALID_TIMEOUT_SECONDS"
    assert "Ajuste timeout_seconds" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("orqs2evt-")


def test_s2_orchestrator_error_detail_contract() -> None:
    detail = build_s2_orchestrator_error_detail(
        code="INVALID_TIMEOUT_SECONDS",
        message="timeout_seconds invalido",
        action="Ajuste timeout_seconds.",
        correlation_id="orq-s2-error-001",
        event_id="orqs2evt-abc123",
        stage="scaffold",
        context={"timeout_seconds": 10},
    )

    assert detail["code"] == "INVALID_TIMEOUT_SECONDS"
    assert detail["correlation_id"] == "orq-s2-error-001"
    assert detail["event_id"] == "orqs2evt-abc123"
    assert detail["stage"] == "scaffold"
    assert detail["context"]["timeout_seconds"] == 10
