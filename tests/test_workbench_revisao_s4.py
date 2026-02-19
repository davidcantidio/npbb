"""Unit tests for WORK Sprint 4 scaffold and core contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from frontend.src.features.revisao_humana.s4_core import (  # noqa: E402
    S4WorkbenchCoreError,
    S4WorkbenchCoreInput,
    execute_workbench_revisao_s4_main_flow,
)
from frontend.src.features.revisao_humana.s4_scaffold import (  # noqa: E402
    S4WorkbenchScaffoldError,
    S4WorkbenchScaffoldRequest,
    build_s4_workbench_scaffold,
)


def _build_valid_request(*, correlation_id: str) -> S4WorkbenchScaffoldRequest:
    return S4WorkbenchScaffoldRequest(
        workflow_id="WORK_REVIEW_OPERACIONAL_S4",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v4",
        owner_team="etl",
        audit_dimensions=("edicao", "sla", "produtividade"),
        change_channels=("ui", "api", "batch"),
        audit_mode="full_trace",
        sla_target_minutes=120,
        sla_warning_threshold_minutes=90,
        sla_breach_grace_minutes=15,
        productivity_window_hours=8,
        minimum_actions_per_window=10,
        require_change_reason=True,
        capture_before_after_state=True,
        enable_anomaly_alerts=True,
        reviewer_roles=("operador", "supervisor", "auditoria"),
        correlation_id=correlation_id,
    )


def test_work_s4_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_request(correlation_id="work-s4-test-001")

    output = build_s4_workbench_scaffold(request)

    assert output.contrato_versao == "work.s4.v1"
    assert output.correlation_id == "work-s4-test-001"
    assert output.status == "ready"
    assert output.workflow_id == "WORK_REVIEW_OPERACIONAL_S4"
    assert output.operational_audit_policy["page_scope"] == "auditoria_edicao_sla_produtividade_operacional"
    assert output.operational_audit_policy["audit_dimensions_count"] == 3
    assert output.pontos_integracao["work_s4_prepare_endpoint"] == "/internal/revisao-humana/s4/prepare"
    assert "workbench_revisao_s4_validation_module" in output.pontos_integracao


def test_work_s4_scaffold_rejects_invalid_audit_mode() -> None:
    request = _build_valid_request(correlation_id="work-s4-invalid-mode")
    request = replace(request, audit_mode="automatico")

    with pytest.raises(S4WorkbenchScaffoldError) as exc:
        build_s4_workbench_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_AUDIT_MODE"
    assert "audit_mode suportado" in error.action


def test_work_s4_scaffold_rejects_invalid_sla_thresholds() -> None:
    request = _build_valid_request(correlation_id="work-s4-invalid-sla")
    request = replace(request, sla_target_minutes=60, sla_warning_threshold_minutes=60)

    with pytest.raises(S4WorkbenchScaffoldError) as exc:
        build_s4_workbench_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_SLA_THRESHOLDS"
    assert "warning estritamente abaixo do target" in error.action


def test_work_s4_core_success_runs_main_flow() -> None:
    flow_input = S4WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_OPERACIONAL_S4",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v4",
        owner_team="etl",
        audit_dimensions=("edicao", "sla", "produtividade"),
        change_channels=("ui", "api", "batch"),
        audit_mode="full_trace",
        sla_target_minutes=120,
        sla_warning_threshold_minutes=90,
        sla_breach_grace_minutes=15,
        productivity_window_hours=8,
        minimum_actions_per_window=10,
        require_change_reason=True,
        capture_before_after_state=True,
        enable_anomaly_alerts=True,
        reviewer_roles=("operador", "supervisor", "auditoria"),
        correlation_id="work-s4-core-001",
    )

    output = execute_workbench_revisao_s4_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "work.s4.core.v1"
    assert output["correlation_id"] == "work-s4-core-001"
    assert output["status"] == "completed"
    assert output["workflow_id"] == "WORK_REVIEW_OPERACIONAL_S4"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["operational_audit_result_id"].startswith("works4audit-")
    assert output["observabilidade"]["flow_started_event_id"].startswith("works4coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("works4coreevt-")
    assert output["pontos_integracao"]["work_s4_execute_endpoint"] == "/internal/revisao-humana/s4/execute"


def test_work_s4_core_raises_actionable_error_for_failed_operational_audit() -> None:
    flow_input = S4WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_OPERACIONAL_S4",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v4",
        owner_team="etl",
        audit_dimensions=("edicao", "sla", "produtividade"),
        change_channels=("ui", "api"),
        audit_mode="sampled_trace",
        sla_target_minutes=120,
        sla_warning_threshold_minutes=90,
        sla_breach_grace_minutes=15,
        productivity_window_hours=8,
        minimum_actions_per_window=10,
        require_change_reason=True,
        capture_before_after_state=True,
        enable_anomaly_alerts=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id="work-s4-core-failed",
    )

    def fail_operational_audit(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "operational_audit_result_id": "works4audit-failcase",
            "actions_received": 100,
            "actions_audited": 80,
            "pending_audit_items": 20,
            "sla_warning_breaches": 12,
            "sla_violations_detected": 4,
            "productivity_alerts": 0,
            "anomaly_alerts_triggered": 0,
            "change_reasons_missing": 0,
            "before_after_missing": 0,
            "productivity_rate_per_hour": 10.0,
            "audit_overflow_detected": False,
            "decision_reason": "forced_failure_for_test",
        }

    with pytest.raises(S4WorkbenchCoreError) as exc:
        execute_workbench_revisao_s4_main_flow(
            flow_input,
            execute_operational_audit=fail_operational_audit,
        )

    error = exc.value
    assert error.code == "WORK_S4_OPERATIONAL_AUDIT_FAILED"
    assert error.stage == "operational_audit"
    assert (error.event_id or "").startswith("works4coreevt-")
