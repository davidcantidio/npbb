"""Unit tests for WORK Sprint 3 scaffold, core, and validation contracts."""

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

from frontend.src.features.revisao_humana.s3_core import (  # noqa: E402
    S3WorkbenchCoreError,
    S3WorkbenchCoreInput,
    execute_workbench_revisao_s3_main_flow,
)
from frontend.src.features.revisao_humana.s3_scaffold import (  # noqa: E402
    S3WorkbenchScaffoldError,
    S3WorkbenchScaffoldRequest,
    build_s3_workbench_scaffold,
)
from frontend.src.features.revisao_humana.s3_validation import (  # noqa: E402
    S3WorkbenchValidationError,
    S3WorkbenchValidationInput,
    validate_workbench_revisao_s3_input_contract,
    validate_workbench_revisao_s3_output_contract,
)


def _build_valid_request(*, correlation_id: str) -> S3WorkbenchScaffoldRequest:
    return S3WorkbenchScaffoldRequest(
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v3",
        owner_team="etl",
        batch_size=200,
        max_pending_batches=2000,
        approval_mode="dual_control",
        required_approvers=2,
        approver_roles=("supervisor", "coordenador"),
        approval_sla_hours=24,
        require_justification=True,
        allow_partial_approval=False,
        auto_lock_on_conflict=True,
        correlation_id=correlation_id,
    )


def _build_valid_validation_input(*, correlation_id: str) -> S3WorkbenchValidationInput:
    return S3WorkbenchValidationInput(
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v3",
        owner_team="etl",
        batch_size=200,
        max_pending_batches=2000,
        approval_mode="dual_control",
        required_approvers=2,
        approver_roles=("supervisor", "coordenador"),
        approval_sla_hours=24,
        require_justification=True,
        allow_partial_approval=False,
        auto_lock_on_conflict=True,
        correlation_id=correlation_id,
    )


def test_work_s3_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_request(correlation_id="work-s3-test-001")

    output = build_s3_workbench_scaffold(request)

    assert output.contrato_versao == "work.s3.v1"
    assert output.correlation_id == "work-s3-test-001"
    assert output.status == "ready"
    assert output.workflow_id == "WORK_REVIEW_LEAD_S3"
    assert output.batch_approval_policy["page_scope"] == "operacoes_em_lote_fluxo_aprovacao"
    assert output.batch_approval_policy["approver_roles_count"] == 2
    assert output.pontos_integracao["work_s3_prepare_endpoint"] == "/internal/revisao-humana/s3/prepare"
    assert "workbench_revisao_s3_validation_module" in output.pontos_integracao


def test_work_s3_scaffold_rejects_invalid_approval_mode() -> None:
    request = _build_valid_request(correlation_id="work-s3-invalid-mode")
    request = replace(request, approval_mode="automatico")

    with pytest.raises(S3WorkbenchScaffoldError) as exc:
        build_s3_workbench_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_APPROVAL_MODE"
    assert "approval_mode suportado" in error.action


def test_work_s3_core_success_runs_main_flow() -> None:
    flow_input = S3WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v3",
        owner_team="etl",
        batch_size=200,
        max_pending_batches=2000,
        approval_mode="dual_control",
        required_approvers=2,
        approver_roles=("supervisor", "coordenador"),
        approval_sla_hours=24,
        require_justification=True,
        allow_partial_approval=False,
        auto_lock_on_conflict=True,
        correlation_id="work-s3-core-001",
    )

    output = execute_workbench_revisao_s3_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "work.s3.core.v1"
    assert output["correlation_id"] == "work-s3-core-001"
    assert output["status"] == "completed"
    assert output["workflow_id"] == "WORK_REVIEW_LEAD_S3"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["batch_approval_result_id"].startswith("works3batch-")
    assert output["observabilidade"]["flow_started_event_id"].startswith("works3coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("works3coreevt-")
    assert output["pontos_integracao"]["work_s3_execute_endpoint"] == "/internal/revisao-humana/s3/execute"


def test_work_s3_core_raises_actionable_error_for_failed_batch_approval() -> None:
    flow_input = S3WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v3",
        owner_team="etl",
        batch_size=100,
        max_pending_batches=1000,
        approval_mode="dual_control",
        required_approvers=2,
        approver_roles=("supervisor", "coordenador"),
        approval_sla_hours=24,
        require_justification=True,
        allow_partial_approval=False,
        auto_lock_on_conflict=True,
        correlation_id="work-s3-core-failed",
    )

    def fail_batch_approval(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "batch_approval_result_id": "works3batch-failcase",
            "batches_received": 10,
            "batches_approved": 4,
            "batches_rejected": 3,
            "batches_escalated": 3,
            "pending_batches": 0,
            "approvals_recorded": 8,
            "conflicts_detected": 2,
            "auto_locked_batches": 2,
            "partial_approvals": 0,
            "justifications_missing": 0,
            "approval_overflow_detected": False,
            "decision_reason": "forced_failure_for_test",
        }

    with pytest.raises(S3WorkbenchCoreError) as exc:
        execute_workbench_revisao_s3_main_flow(
            flow_input,
            execute_batch_approval=fail_batch_approval,
        )

    error = exc.value
    assert error.code == "WORK_S3_BATCH_APPROVAL_FAILED"
    assert error.stage == "approval"
    assert (error.event_id or "").startswith("works3coreevt-")


def test_work_s3_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="work-s3-validation-001")

    result = validate_workbench_revisao_s3_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "work.s3.validation.v1"
    assert result.correlation_id == "work-s3-validation-001"
    assert "workflow_id" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "workbench_revisao_s3"
    assert result.observabilidade["validation_started_event_id"].startswith("works3obsevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("works3obsevt-")


def test_work_s3_validation_input_rejects_empty_dataset_name() -> None:
    payload = S3WorkbenchValidationInput(
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="",
        entity_kind="lead",
        correlation_id="work-s3-validation-error-dataset",
    )

    with pytest.raises(S3WorkbenchValidationError) as exc:
        validate_workbench_revisao_s3_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "work-s3-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("works3obsevt-")


def test_work_s3_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.frontend.revisao_humana.s3.validation")
    payload = S3WorkbenchValidationInput(
        workflow_id="",
        dataset_name="leads_capture",
        entity_kind="lead",
        correlation_id="work-s3-validation-log-error",
    )

    with pytest.raises(S3WorkbenchValidationError):
        validate_workbench_revisao_s3_input_contract(payload)

    records = [
        record for record in caplog.records if record.message == "workbench_revisao_s3_validation_error"
    ]
    assert records
    assert records[-1].correlation_id == "work-s3-validation-log-error"
    assert records[-1].error_code == "EMPTY_WORKFLOW_ID"


def test_work_s3_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="work-s3-validation-core-integration")
    validation = validate_workbench_revisao_s3_input_contract(payload)
    core_output = execute_workbench_revisao_s3_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_workbench_revisao_s3_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("works3coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("works3coreevt-")


def test_work_s3_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S3WorkbenchValidationError) as exc:
        validate_workbench_revisao_s3_output_contract(
            {"status": "completed"},
            correlation_id="work-s3-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"


def test_work_s3_validation_output_rejects_invalid_integration_point() -> None:
    flow_input = S3WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v3",
        owner_team="etl",
        batch_size=200,
        max_pending_batches=2000,
        approval_mode="dual_control",
        required_approvers=2,
        approver_roles=("supervisor", "coordenador"),
        approval_sla_hours=24,
        require_justification=True,
        allow_partial_approval=False,
        auto_lock_on_conflict=True,
        correlation_id="work-s3-invalid-integrations",
    )
    output = execute_workbench_revisao_s3_main_flow(flow_input).to_dict()
    output["pontos_integracao"]["work_s3_execute_endpoint"] = "/internal/revisao-humana/s3/wrong"

    with pytest.raises(S3WorkbenchValidationError) as exc:
        validate_workbench_revisao_s3_output_contract(
            output,
            correlation_id="work-s3-invalid-integrations",
        )

    error = exc.value
    assert error.code == "INVALID_INTEGRATION_POINT"
    assert error.stage == "validation_output"
