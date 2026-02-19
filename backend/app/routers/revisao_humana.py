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
    from frontend.src.features.revisao_humana.s1_scaffold import (
        S1WorkbenchScaffoldError,
        S1WorkbenchScaffoldRequest,
        build_s1_workbench_scaffold,
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
    from frontend.src.features.revisao_humana.s1_scaffold import (
        S1WorkbenchScaffoldError,
        S1WorkbenchScaffoldRequest,
        build_s1_workbench_scaffold,
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
