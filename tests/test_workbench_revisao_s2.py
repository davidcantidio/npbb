"""Unit tests for WORK Sprint 2 scaffold, core, and validation contracts."""

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

from frontend.src.features.revisao_humana.s2_core import (  # noqa: E402
    S2WorkbenchCoreError,
    S2WorkbenchCoreInput,
    execute_workbench_revisao_s2_main_flow,
)
from frontend.src.features.revisao_humana.s2_scaffold import (  # noqa: E402
    S2WorkbenchScaffoldError,
    S2WorkbenchScaffoldRequest,
    build_s2_workbench_scaffold,
)
from frontend.src.features.revisao_humana.s2_validation import (  # noqa: E402
    S2WorkbenchValidationError,
    S2WorkbenchValidationInput,
    validate_workbench_revisao_s2_input_contract,
    validate_workbench_revisao_s2_output_contract,
)


def _build_valid_request(*, correlation_id: str) -> S2WorkbenchScaffoldRequest:
    return S2WorkbenchScaffoldRequest(
        workflow_id="WORK_REVIEW_LEAD_S2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        missing_fields=("nome", "email", "telefone"),
        candidate_sources=("crm", "formulario", "ocr"),
        correspondence_mode="manual_confirm",
        match_strategy="fuzzy",
        min_similarity_score=0.70,
        auto_apply_threshold=0.95,
        max_suggestions_per_field=5,
        require_evidence_for_suggestion=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id=correlation_id,
    )


def _build_valid_validation_input(*, correlation_id: str) -> S2WorkbenchValidationInput:
    return S2WorkbenchValidationInput(
        workflow_id="WORK_REVIEW_LEAD_S2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        missing_fields=("nome", "email", "telefone"),
        candidate_sources=("crm", "formulario", "ocr"),
        correspondence_mode="manual_confirm",
        match_strategy="fuzzy",
        min_similarity_score=0.70,
        auto_apply_threshold=0.95,
        max_suggestions_per_field=5,
        require_evidence_for_suggestion=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id=correlation_id,
    )


def test_work_s2_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_request(correlation_id="work-s2-test-001")

    output = build_s2_workbench_scaffold(request)

    assert output.contrato_versao == "work.s2.v1"
    assert output.correlation_id == "work-s2-test-001"
    assert output.status == "ready"
    assert output.workflow_id == "WORK_REVIEW_LEAD_S2"
    assert output.correspondence_policy["page_scope"] == "correspondencia_campos_nao_encontrados"
    assert output.correspondence_policy["missing_fields_count"] == 3
    assert output.pontos_integracao["work_s2_prepare_endpoint"] == "/internal/revisao-humana/s2/prepare"
    assert "workbench_revisao_s2_validation_module" in output.pontos_integracao


def test_work_s2_scaffold_rejects_invalid_correspondence_mode() -> None:
    request = _build_valid_request(correlation_id="work-s2-invalid-mode")
    request = replace(request, correspondence_mode="auto")

    with pytest.raises(S2WorkbenchScaffoldError) as exc:
        build_s2_workbench_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_CORRESPONDENCE_MODE"
    assert "modo suportado" in error.action


def test_work_s2_core_success_runs_main_flow() -> None:
    flow_input = S2WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_S2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        missing_fields=("nome", "email", "telefone"),
        candidate_sources=("crm", "formulario", "ocr"),
        correspondence_mode="manual_confirm",
        match_strategy="fuzzy",
        min_similarity_score=0.70,
        auto_apply_threshold=0.95,
        max_suggestions_per_field=5,
        require_evidence_for_suggestion=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id="work-s2-core-001",
    )

    output = execute_workbench_revisao_s2_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "work.s2.core.v1"
    assert output["correlation_id"] == "work-s2-core-001"
    assert output["status"] == "completed"
    assert output["workflow_id"] == "WORK_REVIEW_LEAD_S2"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["correspondence_result_id"].startswith("works2corr-")
    assert output["observabilidade"]["flow_started_event_id"].startswith("works2coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("works2coreevt-")
    assert output["pontos_integracao"]["work_s2_execute_endpoint"] == "/internal/revisao-humana/s2/execute"


def test_work_s2_core_raises_actionable_error_for_failed_correspondence() -> None:
    flow_input = S2WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_S2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        missing_fields=("nome", "email", "telefone"),
        candidate_sources=("crm", "formulario"),
        correspondence_mode="manual_confirm",
        match_strategy="fuzzy",
        min_similarity_score=0.70,
        auto_apply_threshold=0.95,
        max_suggestions_per_field=5,
        require_evidence_for_suggestion=True,
        reviewer_roles=("operador",),
        correlation_id="work-s2-core-failed",
    )

    def fail_correspondence(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "correspondence_result_id": "works2corr-failcase",
            "suggested_matches": 2,
            "reviewed_matches": 1,
            "auto_applied_matches": 0,
            "unresolved_fields_count": 2,
            "candidate_pairs_evaluated": 4,
            "suggestion_overflow_detected": False,
            "evidence_links_count": 2,
            "decision_reason": "forced_failure_for_test",
        }

    with pytest.raises(S2WorkbenchCoreError) as exc:
        execute_workbench_revisao_s2_main_flow(
            flow_input,
            execute_correspondence=fail_correspondence,
        )

    error = exc.value
    assert error.code == "WORK_S2_CORRESPONDENCE_FAILED"
    assert error.stage == "correspondence"
    assert (error.event_id or "").startswith("works2coreevt-")


def test_work_s2_validation_input_success_returns_contract() -> None:
    payload = _build_valid_validation_input(correlation_id="work-s2-validation-001")

    result = validate_workbench_revisao_s2_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "work.s2.validation.v1"
    assert result.correlation_id == "work-s2-validation-001"
    assert "workflow_id" in result.checks
    assert "scaffold_contract" in result.checks
    assert result.route_preview == "workbench_revisao_s2"
    assert result.observabilidade["validation_started_event_id"].startswith("works2obsevt-")
    assert result.observabilidade["validation_completed_event_id"].startswith("works2obsevt-")


def test_work_s2_validation_input_rejects_empty_dataset_name() -> None:
    payload = S2WorkbenchValidationInput(
        workflow_id="WORK_REVIEW_LEAD_S2",
        dataset_name="",
        entity_kind="lead",
        correlation_id="work-s2-validation-error-dataset",
    )

    with pytest.raises(S2WorkbenchValidationError) as exc:
        validate_workbench_revisao_s2_input_contract(payload)

    error = exc.value
    assert error.code == "EMPTY_DATASET_NAME"
    assert "dataset_name" in error.action
    assert error.stage == "validation_input"
    assert error.correlation_id == "work-s2-validation-error-dataset"
    assert (error.observability_event_id or "").startswith("works2obsevt-")


def test_work_s2_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.frontend.revisao_humana.s2.validation")
    payload = S2WorkbenchValidationInput(
        workflow_id="",
        dataset_name="leads_capture",
        entity_kind="lead",
        correlation_id="work-s2-validation-log-error",
    )

    with pytest.raises(S2WorkbenchValidationError):
        validate_workbench_revisao_s2_input_contract(payload)

    records = [
        record for record in caplog.records if record.message == "workbench_revisao_s2_validation_error"
    ]
    assert records
    assert records[-1].correlation_id == "work-s2-validation-log-error"
    assert records[-1].error_code == "EMPTY_WORKFLOW_ID"


def test_work_s2_validation_with_core_flow_output_contract_integration() -> None:
    payload = _build_valid_validation_input(correlation_id="work-s2-validation-core-integration")
    validation = validate_workbench_revisao_s2_input_contract(payload)
    core_output = execute_workbench_revisao_s2_main_flow(
        payload.to_core_input(correlation_id=validation.correlation_id)
    ).to_dict()

    output_validation = validate_workbench_revisao_s2_output_contract(
        core_output,
        correlation_id=validation.correlation_id,
    )

    assert output_validation.status == "valid"
    assert output_validation.layer == "core"
    assert "execucao" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("works2coreevt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("works2coreevt-")


def test_work_s2_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S2WorkbenchValidationError) as exc:
        validate_workbench_revisao_s2_output_contract(
            {"status": "completed"},
            correlation_id="work-s2-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint" in error.action
    assert error.stage == "validation_output"


def test_work_s2_validation_output_rejects_invalid_integration_point() -> None:
    flow_input = S2WorkbenchCoreInput(
        workflow_id="WORK_REVIEW_LEAD_S2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        missing_fields=("nome", "email", "telefone"),
        candidate_sources=("crm", "formulario", "ocr"),
        correspondence_mode="manual_confirm",
        match_strategy="fuzzy",
        min_similarity_score=0.70,
        auto_apply_threshold=0.95,
        max_suggestions_per_field=5,
        require_evidence_for_suggestion=True,
        reviewer_roles=("operador", "supervisor"),
        correlation_id="work-s2-invalid-integrations",
    )
    output = execute_workbench_revisao_s2_main_flow(flow_input).to_dict()
    output["pontos_integracao"]["work_s2_execute_endpoint"] = "/internal/revisao-humana/s2/wrong"

    with pytest.raises(S2WorkbenchValidationError) as exc:
        validate_workbench_revisao_s2_output_contract(
            output,
            correlation_id="work-s2-invalid-integrations",
        )

    error = exc.value
    assert error.code == "INVALID_INTEGRATION_POINT"
    assert error.stage == "validation_output"
