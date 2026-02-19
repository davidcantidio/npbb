"""Unit tests for WORK Sprint 4 scaffold contracts."""

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
