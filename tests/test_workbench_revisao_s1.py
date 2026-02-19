"""Unit tests for WORK Sprint 1 scaffold, core, and validation contracts."""

from __future__ import annotations

from dataclasses import replace
import logging
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from frontend.src.features.revisao_humana.s1_core import (  # noqa: E402
    S1WorkbenchCoreError,
    S1WorkbenchCoreInput,
    execute_workbench_revisao_s1_main_flow,
)
from frontend.src.features.revisao_humana.s1_scaffold import (  # noqa: E402
    S1WorkbenchScaffoldError,
    S1WorkbenchScaffoldRequest,
    build_s1_workbench_scaffold,
)
from frontend.src.features.revisao_humana.s1_validation import (  # noqa: E402
    S1WorkbenchValidationError,
    S1WorkbenchValidationInput,
    validate_workbench_revisao_s1_input_contract,
    validate_workbench_revisao_s1_output_contract,
)


def _build_valid_request(*, correlation_id: str) -> S1WorkbenchScaffoldRequest:
    return S1WorkbenchScaffoldRequest(
        workflow_id="WORK_REVIEW_LEAD_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        required_fields=("nome", "email", "telefone"),
        evidence_sources=("crm", "formulario"),
        default_priority="media",
        sla_hours=24,
        max_queue_size=1000,
        auto_assignment_enabled=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id=correlation_id,
    )


def _build_valid_validation_input(*, correlation_id: str) -> S1WorkbenchValidationInput:
    return S1WorkbenchValidationInput(
        workflow_id="WORK_REVIEW_LEAD_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        required_fields=("nome", "email", "telefone"),
        evidence_sources=("crm", "formulario"),
        default_priority="media",
        sla_hours=24,
        max_queue_size=1000,
        auto_assignment_enabled=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id=correlation_id,
    )


def test_work_s1_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_request(correlation_id="work-s1-test-001")

    output = build_s1_workbench_scaffold(request)

    assert output.contrato_versao == "work.s1.v1"
    assert output.correlation_id == "work-s1-test-001"
    assert output.status == "ready"
    assert output.workflow_id == "WORK_REVIEW_LEAD_V1"
    assert output.review_queue_policy["queue_scope"] == "campo_faltante_com_evidencia"
    assert output.review_queue_policy["required_fields_count"] == 3
    assert output.pontos_integracao["work_s1_prepare_endpoint"] == "/internal/revisao-humana/s1/prepare"
    assert "workbench_revisao_s1_validation_module" in output.pontos_integracao


def test_work_s1_scaffold_rejects_invalid_default_priority() -> None:
    request = _build_valid_request(correlation_id="work-s1-invalid-priority")
    request = replace(request, default_priority="urgente")

    with pytest.raises(S1WorkbenchScaffoldError) as exc:
        build_s1_workbench_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_DEFAULT_PRIORITY"
    assert "prioridade suportada" in error.action


def test_work_s1_core_success_runs_main_flow() -> None:
    flow_input = S1WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        required_fields=("nome", "email", "telefone"),
        evidence_sources=("crm", "formulario"),
        default_priority="media",
        sla_hours=24,
        max_queue_size=1000,
        auto_assignment_enabled=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id="work-s1-core-001",
    )

    output = execute_workbench_revisao_s1_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "work.s1.core.v1"
    assert output["correlation_id"] == "work-s1-core-001"
    assert output["status"] == "completed"
    assert output["workflow_id"] == "WORK_REVIEW_LEAD_V1"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["queue_build_result_id"].startswith("works1queue-")
    assert output["observabilidade"]["flow_started_event_id"].startswith("works1coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("works1coreevt-")
    assert output["pontos_integracao"]["work_s1_execute_endpoint"] == "/internal/revisao-humana/s1/execute"


def test_work_s1_core_raises_actionable_error_for_failed_queue_builder() -> None:
    flow_input = S1WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        required_fields=("nome", "email", "telefone"),
        evidence_sources=("crm", "formulario"),
        default_priority="media",
        sla_hours=24,
        max_queue_size=1000,
        auto_assignment_enabled=False,
        reviewer_roles=("operador",),
        correlation_id="work-s1-core-failed",
    )

    def fail_queue_builder(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "generated_items": 2,
            "critical_items": 0,
            "assigned_items": 0,
            "pending_fields_count": 2,
            "overflow_detected": False,
            "queue_build_result_id": "works1queue-failcase",
            "decision_reason": "forced_failure_for_test",
        }

    with pytest.raises(S1WorkbenchCoreError) as exc:
        execute_workbench_revisao_s1_main_flow(
            flow_input,
            execute_queue_builder=fail_queue_builder,
        )

    error = exc.value
    assert error.code == "WORK_S1_QUEUE_BUILD_FAILED"
    assert error.stage == "queue_build"
    assert (error.event_id or "").startswith("works1coreevt-")


def test_work_s1_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="work-s1-validation-001")

    result = validate_workbench_revisao_s1_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "work.s1.validation.v1"
    assert result.correlation_id == "work-s1-validation-001"
    assert "workflow_id" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "workbench_revisao_s1"
    assert result.observabilidade["validation_started_event_id"].startswith("works1obsevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("works1obsevt-")


def test_work_s1_validation_input_rejects_empty_dataset_name() -> None:
    payload = S1WorkbenchValidationInput(
        workflow_id="WORK_REVIEW_LEAD_V1",
        dataset_name="",
        entity_kind="lead",
        correlation_id="work-s1-validation-error-dataset",
    )

    with pytest.raises(S1WorkbenchValidationError) as exc:
        validate_workbench_revisao_s1_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "work-s1-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("works1obsevt-")


def test_work_s1_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.frontend.revisao_humana.s1.validation")
    payload = S1WorkbenchValidationInput(
        workflow_id="",
        dataset_name="leads_capture",
        entity_kind="lead",
        correlation_id="work-s1-validation-log-error",
    )

    with pytest.raises(S1WorkbenchValidationError):
        validate_workbench_revisao_s1_input_contract(payload)

    records = [
        record for record in caplog.records if record.message == "workbench_revisao_s1_validation_error"
    ]
    assert records
    assert records[-1].correlation_id == "work-s1-validation-log-error"
    assert records[-1].error_code == "EMPTY_WORKFLOW_ID"


def test_work_s1_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="work-s1-validation-core-integration")
    validation = validate_workbench_revisao_s1_input_contract(payload)
    core_output = execute_workbench_revisao_s1_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_workbench_revisao_s1_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("works1coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("works1coreevt-")


def test_work_s1_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S1WorkbenchValidationError) as exc:
        validate_workbench_revisao_s1_output_contract(
            {"status": "completed"},
            correlation_id="work-s1-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"

