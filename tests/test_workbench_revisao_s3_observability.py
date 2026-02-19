"""Unit tests for WORK Sprint 3 frontend observability contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.revisao_humana.s3_observability import (  # noqa: E402
    S3WorkbenchObservabilityError,
    S3WorkbenchObservabilityInput,
    build_s3_workbench_actionable_error,
    build_s3_workbench_observability_event,
    get_s3_workbench_observability_integration_points,
)


def _build_valid_payload() -> S3WorkbenchObservabilityInput:
    return S3WorkbenchObservabilityInput(
        event_name="workbench_revisao_s3_main_flow_completed",
        correlation_id="work-s3-observability-001",
        event_message="Fluxo WORK S3 concluido com sucesso",
        severity="info",
        workflow_id="WORK_REVIEW_LEAD_S3",
        dataset_name="leads_capture",
        entity_kind="LEAD",
        schema_version="V3",
        owner_team="ETL",
        status="COMPLETED",
        stage="approval",
        approval_mode="DUAL_CONTROL",
        required_approvers=2,
        approver_roles_count=2,
        batch_size=200,
        max_pending_batches=2000,
        approval_sla_hours=24,
        batches_received=150,
        batches_approved=90,
        batches_rejected=20,
        batches_escalated=40,
        pending_batches=0,
        approvals_recorded=200,
        conflicts_detected=10,
        auto_locked_batches=10,
        partial_approvals=0,
        justifications_missing=0,
        approval_queue_capacity=2000,
        approval_overflow_detected=False,
        require_justification=True,
        allow_partial_approval=False,
        auto_lock_on_conflict=True,
        context={"ticket": "TMJ-ETL-218"},
    )


def test_build_s3_workbench_observability_event_success() -> None:
    event = build_s3_workbench_observability_event(_build_valid_payload())

    assert event.observability_event_id.startswith("works3obsevt-")
    assert event.correlation_id == "work-s3-observability-001"
    assert event.entity_kind == "lead"
    assert event.approval_mode == "dual_control"
    assert event.schema_version == "v3"
    assert event.owner_team == "etl"
    assert event.context["ticket"] == "TMJ-ETL-218"


def test_build_s3_workbench_observability_event_rejects_partial_approval_without_flag() -> None:
    payload = replace(_build_valid_payload(), partial_approvals=1, allow_partial_approval=False)

    with pytest.raises(S3WorkbenchObservabilityError) as exc:
        build_s3_workbench_observability_event(payload)

    assert exc.value.code == "INVALID_WORK_S3_OBSERVABILITY_PARTIAL_APPROVALS"


def test_s3_workbench_observability_integration_points_and_actionable_error() -> None:
    points = get_s3_workbench_observability_integration_points()
    detail = build_s3_workbench_actionable_error(
        code="WORK_S3_APPROVAL_FAILED",
        message="Falha de aprovacao em lote",
        action="Revisar logs operacionais da sprint.",
        correlation_id="work-s3-observability-001",
        observability_event_id="works3obsevt-abc123",
        stage="approval",
        context={"workflow_id": "WORK_REVIEW_LEAD_S3"},
    )

    assert "workbench_revisao_s3_observability_module" in points
    assert "workbench_revisao_s3_backend_telemetry_module" in points
    assert detail["observability_event_id"] == "works3obsevt-abc123"
    assert detail["context"]["workflow_id"] == "WORK_REVIEW_LEAD_S3"
