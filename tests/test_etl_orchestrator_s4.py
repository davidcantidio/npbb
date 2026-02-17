"""Unit tests for ORQ Sprint 4 scaffold and service contracts."""

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
    S4OrchestratorServiceError,
    build_s4_orchestrator_error_detail,
    execute_s4_orchestrator_service,
)
from etl.orchestrator.s4_scaffold import (  # noqa: E402
    S4OrchestratorScaffoldError,
    S4OrchestratorScaffoldRequest,
    build_s4_scaffold_contract,
)


def test_s4_orchestrator_scaffold_success_returns_telemetry_governance_plan() -> None:
    request = S4OrchestratorScaffoldRequest(
        source_id="src pdf tmj 2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        decisao_telemetria_habilitada=True,
        custo_estimado_usd=0.25,
        custo_orcamento_usd=1.0,
        latencia_estimada_ms=1800,
        latencia_sla_ms=4000,
        telemetria_amostragem=1.0,
        correlation_id="orq-s4-test-001",
    )

    output = build_s4_scaffold_contract(request)

    assert output.contrato_versao == "orq.s4.v1"
    assert output.correlation_id == "orq-s4-test-001"
    assert output.status == "ready"
    assert output.source_id == "SRC_PDF_TMJ_2025"
    assert output.rota_selecionada == "agent_first_extract"
    assert output.plano_telemetria["decisao_telemetria_habilitada"] is True
    assert output.governanca_custo_latencia["custo_status"] == "within_budget"
    assert output.pontos_integracao["orq_s4_prepare_endpoint"] == "/internal/etl/orchestrator/s4/telemetry"


def test_s4_orchestrator_scaffold_rejects_cost_above_budget() -> None:
    request = S4OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        custo_estimado_usd=2.0,
        custo_orcamento_usd=1.0,
        correlation_id="orq-s4-invalid-cost",
    )

    with pytest.raises(S4OrchestratorScaffoldError) as exc:
        build_s4_scaffold_contract(request)

    error = exc.value
    assert error.code == "COST_ESTIMATE_EXCEEDS_BUDGET"
    assert "reduzir custo" in error.action.lower()


def test_s4_orchestrator_service_success_returns_contract_and_observability() -> None:
    request = S4OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        rota_selecionada="agent_tabular_extract",
        decisao_telemetria_habilitada=True,
        custo_estimado_usd=0.15,
        custo_orcamento_usd=1.0,
        latencia_estimada_ms=1200,
        latencia_sla_ms=3000,
        telemetria_amostragem=0.75,
        correlation_id="orq-s4-service-001",
    )

    output = execute_s4_orchestrator_service(request).to_dict()

    assert output["contrato_versao"] == "orq.s4.service.v1"
    assert output["correlation_id"] == "orq-s4-service-001"
    assert output["status"] == "ready"
    assert output["rota_selecionada"] == "agent_tabular_extract"
    assert output["plano_telemetria"]["telemetria_amostragem"] == 0.75
    assert output["governanca_custo_latencia"]["latencia_status"] == "within_sla"
    assert output["observabilidade"]["flow_started_event_id"].startswith("orqs4evt-")
    assert output["observabilidade"]["telemetry_plan_event_id"].startswith("orqs4evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("orqs4evt-")


def test_s4_orchestrator_service_raises_actionable_error_for_invalid_sampling() -> None:
    request = S4OrchestratorScaffoldRequest(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        decisao_telemetria_habilitada=False,
        telemetria_amostragem=1.0,
        correlation_id="orq-s4-invalid-sampling",
    )

    with pytest.raises(S4OrchestratorServiceError) as exc:
        execute_s4_orchestrator_service(request)

    error = exc.value
    assert error.code == "TELEMETRY_DISABLED_REQUIRES_ZERO_SAMPLING"
    assert "amostragem=0" in error.action.lower()
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("orqs4evt-")


def test_s4_orchestrator_error_detail_contract() -> None:
    detail = build_s4_orchestrator_error_detail(
        code="TELEMETRY_DISABLED_REQUIRES_ZERO_SAMPLING",
        message="telemetria_amostragem invalida para telemetria desabilitada",
        action="Defina telemetria_amostragem=0 ou habilite telemetria.",
        correlation_id="orq-s4-error-001",
        event_id="orqs4evt-abc123",
        stage="scaffold",
        context={"telemetria_amostragem": 1.0},
    )

    assert detail["code"] == "TELEMETRY_DISABLED_REQUIRES_ZERO_SAMPLING"
    assert detail["correlation_id"] == "orq-s4-error-001"
    assert detail["event_id"] == "orqs4evt-abc123"
    assert detail["stage"] == "scaffold"
    assert detail["context"]["telemetria_amostragem"] == 1.0
