"""Rotas de preparo e execucao para o workbench de revisao humana."""

from __future__ import annotations

import logging
from pathlib import Path
import sys
from uuid import uuid4

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.utils.http_errors import raise_http_error

try:  # pragma: no cover - import style depends on execution cwd
    from frontend.src.features.revisao_humana.s1_core import (
        S1WorkbenchCoreError,
        S1WorkbenchCoreInput,
        execute_workbench_revisao_s1_main_flow,
    )
    from frontend.src.features.revisao_humana.s2_core import (
        S2WorkbenchCoreError,
        S2WorkbenchCoreInput,
        execute_workbench_revisao_s2_main_flow,
    )
    from frontend.src.features.revisao_humana.s3_core import (
        S3WorkbenchCoreError,
        S3WorkbenchCoreInput,
        execute_workbench_revisao_s3_main_flow,
    )
    from frontend.src.features.revisao_humana.s1_scaffold import (
        S1WorkbenchScaffoldError,
        S1WorkbenchScaffoldRequest,
        build_s1_workbench_scaffold,
    )
    from frontend.src.features.revisao_humana.s2_scaffold import (
        S2WorkbenchScaffoldError,
        S2WorkbenchScaffoldRequest,
        build_s2_workbench_scaffold,
    )
    from frontend.src.features.revisao_humana.s3_scaffold import (
        S3WorkbenchScaffoldError,
        S3WorkbenchScaffoldRequest,
        build_s3_workbench_scaffold,
    )
    from frontend.src.features.revisao_humana.s4_scaffold import (
        S4WorkbenchScaffoldError,
        S4WorkbenchScaffoldRequest,
        build_s4_workbench_scaffold,
    )
except ModuleNotFoundError:  # pragma: no cover
    npbb_root = Path(__file__).resolve().parents[3]
    if str(npbb_root) not in sys.path:
        sys.path.insert(0, str(npbb_root))
    from frontend.src.features.revisao_humana.s1_core import (
        S1WorkbenchCoreError,
        S1WorkbenchCoreInput,
        execute_workbench_revisao_s1_main_flow,
    )
    from frontend.src.features.revisao_humana.s2_core import (
        S2WorkbenchCoreError,
        S2WorkbenchCoreInput,
        execute_workbench_revisao_s2_main_flow,
    )
    from frontend.src.features.revisao_humana.s3_core import (
        S3WorkbenchCoreError,
        S3WorkbenchCoreInput,
        execute_workbench_revisao_s3_main_flow,
    )
    from frontend.src.features.revisao_humana.s1_scaffold import (
        S1WorkbenchScaffoldError,
        S1WorkbenchScaffoldRequest,
        build_s1_workbench_scaffold,
    )
    from frontend.src.features.revisao_humana.s2_scaffold import (
        S2WorkbenchScaffoldError,
        S2WorkbenchScaffoldRequest,
        build_s2_workbench_scaffold,
    )
    from frontend.src.features.revisao_humana.s3_scaffold import (
        S3WorkbenchScaffoldError,
        S3WorkbenchScaffoldRequest,
        build_s3_workbench_scaffold,
    )
    from frontend.src.features.revisao_humana.s4_scaffold import (
        S4WorkbenchScaffoldError,
        S4WorkbenchScaffoldRequest,
        build_s4_workbench_scaffold,
    )


router = APIRouter(prefix="/internal/revisao-humana", tags=["revisao_humana"])
logger = logging.getLogger(__name__)


class RevisaoHumanaS1PrepareBody(BaseModel):
    """Body contract for WORK Sprint 1 scaffold preparation endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v1"
    owner_team: str = "etl"
    required_fields: list[str] | None = None
    evidence_sources: list[str] | None = None
    default_priority: str = "media"
    sla_hours: int = 24
    max_queue_size: int = 1000
    auto_assignment_enabled: bool = True
    reviewer_roles: list[str] | None = None
    correlation_id: str | None = None


class RevisaoHumanaS1ExecuteBody(BaseModel):
    """Body contract for WORK Sprint 1 main-flow execution endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v1"
    owner_team: str = "etl"
    required_fields: list[str] | None = None
    evidence_sources: list[str] | None = None
    default_priority: str = "media"
    sla_hours: int = 24
    max_queue_size: int = 1000
    auto_assignment_enabled: bool = True
    reviewer_roles: list[str] | None = None
    correlation_id: str | None = None


class RevisaoHumanaS2PrepareBody(BaseModel):
    """Body contract for WORK Sprint 2 scaffold preparation endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v2"
    owner_team: str = "etl"
    missing_fields: list[str] | None = None
    candidate_sources: list[str] | None = None
    correspondence_mode: str = "manual_confirm"
    match_strategy: str = "fuzzy"
    min_similarity_score: float = 0.70
    auto_apply_threshold: float = 0.95
    max_suggestions_per_field: int = 5
    require_evidence_for_suggestion: bool = True
    reviewer_roles: list[str] | None = None
    correlation_id: str | None = None


class RevisaoHumanaS2ExecuteBody(BaseModel):
    """Body contract for WORK Sprint 2 main-flow execution endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v2"
    owner_team: str = "etl"
    missing_fields: list[str] | None = None
    candidate_sources: list[str] | None = None
    correspondence_mode: str = "manual_confirm"
    match_strategy: str = "fuzzy"
    min_similarity_score: float = 0.70
    auto_apply_threshold: float = 0.95
    max_suggestions_per_field: int = 5
    require_evidence_for_suggestion: bool = True
    reviewer_roles: list[str] | None = None
    correlation_id: str | None = None


class RevisaoHumanaS3PrepareBody(BaseModel):
    """Body contract for WORK Sprint 3 scaffold preparation endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v3"
    owner_team: str = "etl"
    batch_size: int = 200
    max_pending_batches: int = 2000
    approval_mode: str = "dual_control"
    required_approvers: int = 2
    approver_roles: list[str] | None = None
    approval_sla_hours: int = 24
    require_justification: bool = True
    allow_partial_approval: bool = False
    auto_lock_on_conflict: bool = True
    correlation_id: str | None = None


class RevisaoHumanaS3ExecuteBody(BaseModel):
    """Body contract for WORK Sprint 3 main-flow execution endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v3"
    owner_team: str = "etl"
    batch_size: int = 200
    max_pending_batches: int = 2000
    approval_mode: str = "dual_control"
    required_approvers: int = 2
    approver_roles: list[str] | None = None
    approval_sla_hours: int = 24
    require_justification: bool = True
    allow_partial_approval: bool = False
    auto_lock_on_conflict: bool = True
    correlation_id: str | None = None


class RevisaoHumanaS4PrepareBody(BaseModel):
    """Body contract for WORK Sprint 4 scaffold preparation endpoint."""

    workflow_id: str = Field(..., min_length=1)
    dataset_name: str = Field(..., min_length=1)
    entity_kind: str = "lead"
    schema_version: str = "v4"
    owner_team: str = "etl"
    audit_dimensions: list[str] | None = None
    change_channels: list[str] | None = None
    audit_mode: str = "full_trace"
    sla_target_minutes: int = 120
    sla_warning_threshold_minutes: int = 90
    sla_breach_grace_minutes: int = 15
    productivity_window_hours: int = 8
    minimum_actions_per_window: int = 10
    require_change_reason: bool = True
    capture_before_after_state: bool = True
    enable_anomaly_alerts: bool = True
    reviewer_roles: list[str] | None = None
    correlation_id: str | None = None


@router.post("/s1/prepare")
def prepare_workbench_revisao_s1(payload: RevisaoHumanaS1PrepareBody) -> dict[str, object]:
    """Prepare WORK Sprint 1 review-queue scaffold contract.

    Args:
        payload: Workbench queue-policy input contract.

    Returns:
        dict[str, object]: Stable scaffold output contract for Sprint 1.

    Raises:
        HTTPException: If scaffold validation fails or payload is inconsistent.
    """

    correlation_id = payload.correlation_id or f"work-s1-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s1_prepare_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
        },
    )

    try:
        scaffold_request = S1WorkbenchScaffoldRequest(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            required_fields=(
                tuple(payload.required_fields)
                if payload.required_fields is not None
                else None
            ),
            evidence_sources=(
                tuple(payload.evidence_sources)
                if payload.evidence_sources is not None
                else None
            ),
            default_priority=payload.default_priority,
            sla_hours=payload.sla_hours,
            max_queue_size=payload.max_queue_size,
            auto_assignment_enabled=payload.auto_assignment_enabled,
            reviewer_roles=(
                tuple(payload.reviewer_roles)
                if payload.reviewer_roles is not None
                else None
            ),
            correlation_id=correlation_id,
        )
        scaffold = build_s1_workbench_scaffold(scaffold_request)
    except S1WorkbenchScaffoldError as exc:
        logger.warning(
            "workbench_revisao_s1_prepare_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": "scaffold_validation",
            },
        )

    result = scaffold.to_dict()
    logger.info(
        "workbench_revisao_s1_prepare_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
        },
    )
    return result


@router.post("/s2/prepare")
def prepare_workbench_revisao_s2(payload: RevisaoHumanaS2PrepareBody) -> dict[str, object]:
    """Prepare WORK Sprint 2 correspondence scaffold contract.

    Args:
        payload: Workbench correspondence-policy input contract.

    Returns:
        dict[str, object]: Stable scaffold output contract for Sprint 2.

    Raises:
        HTTPException: If scaffold validation fails or payload is inconsistent.
    """

    correlation_id = payload.correlation_id or f"work-s2-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s2_prepare_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
            "correspondence_mode": payload.correspondence_mode,
            "match_strategy": payload.match_strategy,
        },
    )

    try:
        scaffold_request = S2WorkbenchScaffoldRequest(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            missing_fields=(
                tuple(payload.missing_fields)
                if payload.missing_fields is not None
                else None
            ),
            candidate_sources=(
                tuple(payload.candidate_sources)
                if payload.candidate_sources is not None
                else None
            ),
            correspondence_mode=payload.correspondence_mode,
            match_strategy=payload.match_strategy,
            min_similarity_score=payload.min_similarity_score,
            auto_apply_threshold=payload.auto_apply_threshold,
            max_suggestions_per_field=payload.max_suggestions_per_field,
            require_evidence_for_suggestion=payload.require_evidence_for_suggestion,
            reviewer_roles=(
                tuple(payload.reviewer_roles)
                if payload.reviewer_roles is not None
                else None
            ),
            correlation_id=correlation_id,
        )
        scaffold = build_s2_workbench_scaffold(scaffold_request)
    except S2WorkbenchScaffoldError as exc:
        logger.warning(
            "workbench_revisao_s2_prepare_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": "scaffold_validation",
            },
        )

    result = scaffold.to_dict()
    logger.info(
        "workbench_revisao_s2_prepare_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
            "correspondence_mode": result.get("correspondence_policy", {}).get("correspondence_mode"),
        },
    )
    return result


@router.post("/s3/prepare")
def prepare_workbench_revisao_s3(payload: RevisaoHumanaS3PrepareBody) -> dict[str, object]:
    """Prepare WORK Sprint 3 batch-approval scaffold contract.

    Args:
        payload: Workbench batch-approval input contract.

    Returns:
        dict[str, object]: Stable scaffold output contract for Sprint 3.

    Raises:
        HTTPException: If scaffold validation fails or payload is inconsistent.
    """

    correlation_id = payload.correlation_id or f"work-s3-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s3_prepare_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
            "approval_mode": payload.approval_mode,
            "required_approvers": payload.required_approvers,
            "batch_size": payload.batch_size,
        },
    )

    try:
        scaffold_request = S3WorkbenchScaffoldRequest(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            batch_size=payload.batch_size,
            max_pending_batches=payload.max_pending_batches,
            approval_mode=payload.approval_mode,
            required_approvers=payload.required_approvers,
            approver_roles=(
                tuple(payload.approver_roles)
                if payload.approver_roles is not None
                else None
            ),
            approval_sla_hours=payload.approval_sla_hours,
            require_justification=payload.require_justification,
            allow_partial_approval=payload.allow_partial_approval,
            auto_lock_on_conflict=payload.auto_lock_on_conflict,
            correlation_id=correlation_id,
        )
        scaffold = build_s3_workbench_scaffold(scaffold_request)
    except S3WorkbenchScaffoldError as exc:
        logger.warning(
            "workbench_revisao_s3_prepare_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": "scaffold_validation",
            },
        )

    result = scaffold.to_dict()
    logger.info(
        "workbench_revisao_s3_prepare_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
            "approval_mode": result.get("batch_approval_policy", {}).get("approval_mode"),
        },
    )
    return result


@router.post("/s4/prepare")
def prepare_workbench_revisao_s4(payload: RevisaoHumanaS4PrepareBody) -> dict[str, object]:
    """Prepare WORK Sprint 4 operational-audit scaffold contract.

    Args:
        payload: Workbench audit/SLA/productivity policy input contract.

    Returns:
        dict[str, object]: Stable scaffold output contract for Sprint 4.

    Raises:
        HTTPException: If scaffold validation fails or payload is inconsistent.
    """

    correlation_id = payload.correlation_id or f"work-s4-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s4_prepare_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
            "audit_mode": payload.audit_mode,
            "sla_target_minutes": payload.sla_target_minutes,
            "productivity_window_hours": payload.productivity_window_hours,
        },
    )

    try:
        scaffold_request = S4WorkbenchScaffoldRequest(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            audit_dimensions=(
                tuple(payload.audit_dimensions)
                if payload.audit_dimensions is not None
                else None
            ),
            change_channels=(
                tuple(payload.change_channels)
                if payload.change_channels is not None
                else None
            ),
            audit_mode=payload.audit_mode,
            sla_target_minutes=payload.sla_target_minutes,
            sla_warning_threshold_minutes=payload.sla_warning_threshold_minutes,
            sla_breach_grace_minutes=payload.sla_breach_grace_minutes,
            productivity_window_hours=payload.productivity_window_hours,
            minimum_actions_per_window=payload.minimum_actions_per_window,
            require_change_reason=payload.require_change_reason,
            capture_before_after_state=payload.capture_before_after_state,
            enable_anomaly_alerts=payload.enable_anomaly_alerts,
            reviewer_roles=(
                tuple(payload.reviewer_roles)
                if payload.reviewer_roles is not None
                else None
            ),
            correlation_id=correlation_id,
        )
        scaffold = build_s4_workbench_scaffold(scaffold_request)
    except S4WorkbenchScaffoldError as exc:
        logger.warning(
            "workbench_revisao_s4_prepare_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": "scaffold_validation",
            },
        )

    result = scaffold.to_dict()
    logger.info(
        "workbench_revisao_s4_prepare_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
            "audit_mode": result.get("operational_audit_policy", {}).get("audit_mode"),
        },
    )
    return result


@router.post("/s3/execute")
def execute_workbench_revisao_s3(payload: RevisaoHumanaS3ExecuteBody) -> dict[str, object]:
    """Execute WORK Sprint 3 main flow and return stable output contract.

    Args:
        payload: Workbench batch-approval input contract for Sprint 3
            execution.

    Returns:
        dict[str, object]: Stable main-flow output contract for Sprint 3.

    Raises:
        HTTPException: If flow validation or execution fails.
    """

    correlation_id = payload.correlation_id or f"work-s3-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s3_execute_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
            "approval_mode": payload.approval_mode,
            "required_approvers": payload.required_approvers,
            "batch_size": payload.batch_size,
        },
    )

    try:
        core_input = S3WorkbenchCoreInput(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            batch_size=payload.batch_size,
            max_pending_batches=payload.max_pending_batches,
            approval_mode=payload.approval_mode,
            required_approvers=payload.required_approvers,
            approver_roles=(
                tuple(payload.approver_roles)
                if payload.approver_roles is not None
                else None
            ),
            approval_sla_hours=payload.approval_sla_hours,
            require_justification=payload.require_justification,
            allow_partial_approval=payload.allow_partial_approval,
            auto_lock_on_conflict=payload.auto_lock_on_conflict,
            correlation_id=correlation_id,
        )
        result = execute_workbench_revisao_s3_main_flow(core_input).to_dict()
    except S3WorkbenchCoreError as exc:
        logger.warning(
            "workbench_revisao_s3_execute_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "stage": exc.stage,
                "event_id": exc.event_id,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": exc.stage,
                "event_id": exc.event_id,
            },
        )

    logger.info(
        "workbench_revisao_s3_execute_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
            "execution_status": result.get("execucao", {}).get("status"),
        },
    )
    return result


@router.post("/s2/execute")
def execute_workbench_revisao_s2(payload: RevisaoHumanaS2ExecuteBody) -> dict[str, object]:
    """Execute WORK Sprint 2 main flow and return stable output contract.

    Args:
        payload: Workbench correspondence-policy input contract for Sprint 2
            execution.

    Returns:
        dict[str, object]: Stable main-flow output contract for Sprint 2.

    Raises:
        HTTPException: If flow validation or execution fails.
    """

    correlation_id = payload.correlation_id or f"work-s2-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s2_execute_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
            "correspondence_mode": payload.correspondence_mode,
            "match_strategy": payload.match_strategy,
        },
    )

    try:
        core_input = S2WorkbenchCoreInput(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            missing_fields=(
                tuple(payload.missing_fields)
                if payload.missing_fields is not None
                else None
            ),
            candidate_sources=(
                tuple(payload.candidate_sources)
                if payload.candidate_sources is not None
                else None
            ),
            correspondence_mode=payload.correspondence_mode,
            match_strategy=payload.match_strategy,
            min_similarity_score=payload.min_similarity_score,
            auto_apply_threshold=payload.auto_apply_threshold,
            max_suggestions_per_field=payload.max_suggestions_per_field,
            require_evidence_for_suggestion=payload.require_evidence_for_suggestion,
            reviewer_roles=(
                tuple(payload.reviewer_roles)
                if payload.reviewer_roles is not None
                else None
            ),
            correlation_id=correlation_id,
        )
        result = execute_workbench_revisao_s2_main_flow(core_input).to_dict()
    except S2WorkbenchCoreError as exc:
        logger.warning(
            "workbench_revisao_s2_execute_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "stage": exc.stage,
                "event_id": exc.event_id,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": exc.stage,
                "event_id": exc.event_id,
            },
        )

    logger.info(
        "workbench_revisao_s2_execute_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
            "execution_status": result.get("execucao", {}).get("status"),
        },
    )
    return result


@router.post("/s1/execute")
def execute_workbench_revisao_s1(payload: RevisaoHumanaS1ExecuteBody) -> dict[str, object]:
    """Execute WORK Sprint 1 main flow and return stable output contract.

    Args:
        payload: Workbench queue-policy input contract for Sprint 1 execution.

    Returns:
        dict[str, object]: Stable main-flow output contract for Sprint 1.

    Raises:
        HTTPException: If flow validation or execution fails.
    """

    correlation_id = payload.correlation_id or f"work-s1-api-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s1_execute_requested",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "schema_version": payload.schema_version,
        },
    )

    try:
        core_input = S1WorkbenchCoreInput(
            workflow_id=payload.workflow_id,
            dataset_name=payload.dataset_name,
            entity_kind=payload.entity_kind,
            schema_version=payload.schema_version,
            owner_team=payload.owner_team,
            required_fields=(
                tuple(payload.required_fields)
                if payload.required_fields is not None
                else None
            ),
            evidence_sources=(
                tuple(payload.evidence_sources)
                if payload.evidence_sources is not None
                else None
            ),
            default_priority=payload.default_priority,
            sla_hours=payload.sla_hours,
            max_queue_size=payload.max_queue_size,
            auto_assignment_enabled=payload.auto_assignment_enabled,
            reviewer_roles=(
                tuple(payload.reviewer_roles)
                if payload.reviewer_roles is not None
                else None
            ),
            correlation_id=correlation_id,
        )
        result = execute_workbench_revisao_s1_main_flow(core_input).to_dict()
    except S1WorkbenchCoreError as exc:
        logger.warning(
            "workbench_revisao_s1_execute_failed",
            extra={
                "correlation_id": correlation_id,
                "workflow_id": payload.workflow_id,
                "dataset_name": payload.dataset_name,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "stage": exc.stage,
                "event_id": exc.event_id,
            },
        )
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=exc.code,
            message=exc.message,
            extra={
                "action": exc.action,
                "correlation_id": correlation_id,
                "stage": exc.stage,
                "event_id": exc.event_id,
            },
        )

    logger.info(
        "workbench_revisao_s1_execute_completed",
        extra={
            "correlation_id": result["correlation_id"],
            "workflow_id": result["workflow_id"],
            "dataset_name": result["dataset_name"],
            "status": result["status"],
            "execution_status": result.get("execucao", {}).get("status"),
        },
    )
    return result
