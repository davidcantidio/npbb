"""Unit tests for ORQ Sprint 3 scaffold, core, and service contracts."""

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
    S3OrchestratorServiceError,
    build_s3_orchestrator_error_detail,
    execute_s3_orchestrator_service,
)
from etl.orchestrator.s3_core import (  # noqa: E402
    S3OrchestratorCoreError,
    S3OrchestratorCoreInput,
    execute_s3_orchestrator_main_flow,
)
from etl.orchestrator.s3_scaffold import (  # noqa: E402
    S3OrchestratorScaffoldError,
    S3OrchestratorScaffoldRequest,
    build_s3_scaffold_contract,
)


def test_s3_orchestrator_scaffold_success_returns_agent_first_plan() -> None:
    request = S3OrchestratorScaffoldRequest(
        source_id="src pdf tmj 2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        agent_habilitado=True,
        permitir_fallback_deterministico=True,
        permitir_fallback_manual=True,
        retry_attempts=1,
        timeout_seconds=240,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_reset_timeout_seconds=180,
        correlation_id="orq-s3-test-001",
    )

    output = build_s3_scaffold_contract(request)

    assert output.contrato_versao == "orq.s3.v1"
    assert output.correlation_id == "orq-s3-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_PDF_TMJ_2025"
    assert output.rota_selecionada == "agent_first_extract"
    assert output.plano_execucao["executor_strategy"] == "agent_first"
    assert output.plano_execucao["queue_name"] == "orq_s3_agent_pdf"
    assert output.circuit_breaker["failure_threshold"] == 3
    assert output.pontos_integracao["orq_s3_prepare_endpoint"] == "/internal/etl/orchestrator/s3/prepare"


def test_s3_orchestrator_scaffold_rejects_invalid_circuit_breaker_threshold() -> None:
    request = S3OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        circuit_breaker_failure_threshold=0,
        correlation_id="orq-s3-invalid-cb-threshold",
    )

    with pytest.raises(S3OrchestratorScaffoldError) as exc:
        build_s3_scaffold_contract(request)

    error = exc.value
    assert error.code == "INVALID_CIRCUIT_BREAKER_FAILURE_THRESHOLD"
    assert "circuit breaker" in error.action.lower()


def test_s3_orchestrator_core_success_runs_agent_first_route() -> None:
    flow_input = S3OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        agent_habilitado=True,
        permitir_fallback_deterministico=True,
        permitir_fallback_manual=True,
        retry_attempts=1,
        timeout_seconds=240,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_reset_timeout_seconds=180,
        correlation_id="orq-s3-core-001",
    )

    output = execute_s3_orchestrator_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "orq.s3.core.v1"
    assert output["correlation_id"] == "orq-s3-core-001"
    assert output["status"] == "completed"
    assert output["rota_selecionada"] == "agent_first_extract"
    assert output["execucao"]["route_chain"][0] == "agent_first_extract"
    assert output["circuit_breaker"]["state"] == "closed"
    assert output["observabilidade"]["flow_started_event_id"].startswith("orqs3coreevt-")
    assert output["observabilidade"]["route_resolved_event_id"].startswith("orqs3coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("orqs3coreevt-")


def test_s3_orchestrator_core_uses_fallback_when_agent_route_fails() -> None:
    flow_input = S3OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        agent_habilitado=True,
        permitir_fallback_deterministico=True,
        permitir_fallback_manual=True,
        retry_attempts=0,
        timeout_seconds=240,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_reset_timeout_seconds=180,
        correlation_id="orq-s3-core-fallback",
    )

    def fake_executor(route_name: str, route_context: dict[str, object]) -> dict[str, object]:
        if route_name == "agent_first_extract":
            return {"status": "failed", "message": "agent failed"}
        return {"status": "succeeded", "message": f"{route_name} succeeded", "ctx": route_context}

    output = execute_s3_orchestrator_main_flow(flow_input, execute_route=fake_executor).to_dict()

    assert output["status"] == "completed"
    assert output["rota_selecionada"] == "deterministic_pdf_extract"
    assert output["execucao"]["fallback_activated"] is True
    assert output["execucao"]["route_chain"][0] == "agent_first_extract"
    assert output["execucao"]["route_chain"][1] == "deterministic_pdf_extract"
    assert len(output["execucao"]["attempts_trace"]) >= 2


def test_s3_orchestrator_core_opens_circuit_breaker_on_consecutive_failures() -> None:
    flow_input = S3OrchestratorCoreInput(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        agent_habilitado=True,
        permitir_fallback_deterministico=True,
        permitir_fallback_manual=True,
        retry_attempts=0,
        timeout_seconds=240,
        circuit_breaker_failure_threshold=2,
        circuit_breaker_reset_timeout_seconds=180,
        correlation_id="orq-s3-core-circuit-open",
    )

    def fail_executor(route_name: str, route_context: dict[str, object]) -> dict[str, object]:
        return {"status": "failed", "message": f"{route_name} failed", "ctx": route_context}

    with pytest.raises(S3OrchestratorCoreError) as exc:
        execute_s3_orchestrator_main_flow(flow_input, execute_route=fail_executor)

    error = exc.value
    assert error.code == "ORQ_S3_CIRCUIT_BREAKER_OPEN"
    assert "circuit breaker" in error.message.lower()
    assert error.stage == "circuit_breaker"
    assert (error.event_id or "").startswith("orqs3coreevt-")


def test_s3_orchestrator_service_success_returns_contract_and_observability() -> None:
    request = S3OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        rota_selecionada="agent_first_extract",
        agent_habilitado=True,
        permitir_fallback_deterministico=True,
        permitir_fallback_manual=True,
        retry_attempts=0,
        timeout_seconds=240,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_reset_timeout_seconds=180,
        correlation_id="orq-s3-service-001",
    )

    output = execute_s3_orchestrator_service(request).to_dict()

    assert output["contrato_versao"] == "orq.s3.service.v1"
    assert output["correlation_id"] == "orq-s3-service-001"
    assert output["status"] == "completed"
    assert output["rota_selecionada"] == "agent_first_extract"
    assert output["observabilidade"]["flow_started_event_id"].startswith("orqs3evt-")
    assert output["observabilidade"]["route_decision_event_id"].startswith("orqs3evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("orqs3evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("orqs3coreevt-")
    assert output["observabilidade"]["main_flow_route_event_id"].startswith("orqs3coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("orqs3coreevt-")


def test_s3_orchestrator_service_raises_actionable_error_for_invalid_threshold() -> None:
    request = S3OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        circuit_breaker_failure_threshold=0,
        correlation_id="orq-s3-invalid-threshold",
    )

    with pytest.raises(S3OrchestratorServiceError) as exc:
        execute_s3_orchestrator_service(request)

    error = exc.value
    assert error.code == "INVALID_CIRCUIT_BREAKER_FAILURE_THRESHOLD"
    assert "circuit breaker" in error.action.lower()
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("orqs3evt-")


def test_s3_orchestrator_error_detail_contract() -> None:
    detail = build_s3_orchestrator_error_detail(
        code="ORQ_S3_CIRCUIT_BREAKER_OPEN",
        message="Circuit breaker aberto",
        action="Aguardar reset e revisar falhas.",
        correlation_id="orq-s3-error-001",
        event_id="orqs3evt-abc123",
        stage="circuit_breaker",
        context={"failure_threshold": 2},
    )

    assert detail["code"] == "ORQ_S3_CIRCUIT_BREAKER_OPEN"
    assert detail["correlation_id"] == "orq-s3-error-001"
    assert detail["event_id"] == "orqs3evt-abc123"
    assert detail["stage"] == "circuit_breaker"
    assert detail["context"]["failure_threshold"] == 2
