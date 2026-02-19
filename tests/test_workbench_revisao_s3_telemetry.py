"""Unit tests for WORK Sprint 3 backend telemetry helpers."""

from __future__ import annotations

from dataclasses import replace
import importlib
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

telemetry = importlib.import_module(
    "app.services.workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry"
)


def _build_valid_payload() -> telemetry.S3WorkbenchTelemetryInput:
    return telemetry.S3WorkbenchTelemetryInput(
        event_name="workbench_revisao_s3_main_flow_completed",
        correlation_id="work-s3-telemetry-001",
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


def test_build_s3_workbench_telemetry_event_success() -> None:
    event = telemetry.build_s3_workbench_telemetry_event(_build_valid_payload())

    assert event.telemetry_event_id.startswith("works3tmlevt-")
    assert event.correlation_id == "work-s3-telemetry-001"
    assert event.approval_mode == "dual_control"
    assert event.entity_kind == "lead"
    assert event.schema_version == "v3"
    assert event.owner_team == "etl"


def test_build_s3_workbench_telemetry_event_rejects_invalid_required_approvers() -> None:
    payload = replace(_build_valid_payload(), required_approvers=0)

    with pytest.raises(telemetry.S3WorkbenchTelemetryContractError) as exc:
        telemetry.build_s3_workbench_telemetry_event(payload)

    assert exc.value.code == "INVALID_WORK_S3_TELEMETRY_REQUIRED_APPROVERS"


def test_build_s3_workbench_error_detail_and_integration_points() -> None:
    detail = telemetry.build_s3_workbench_error_detail(
        code="WORK_S3_BATCH_APPROVAL_FAILED",
        message="Execucao de aprovacao em lote falhou",
        action="Revisar logs do executor de lote.",
        correlation_id="work-s3-telemetry-001",
        telemetry_event_id="works3tmlevt-abc123",
        stage="approval",
        context={"workflow_id": "WORK_REVIEW_LEAD_S3"},
    )
    points = telemetry.get_workbench_s3_telemetry_integration_points()

    assert detail["telemetry_event_id"] == "works3tmlevt-abc123"
    assert detail["context"]["workflow_id"] == "WORK_REVIEW_LEAD_S3"
    assert "workbench_revisao_s3_observability_module" in points
    assert "workbench_revisao_s3_core_module" in points
