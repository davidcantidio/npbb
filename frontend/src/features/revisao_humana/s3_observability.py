"""Observability contracts for WORK Sprint 3 batch approval flow.

This module standardizes operational observability events for Sprint 3 of the
human-review workbench. It validates payload contracts, emits structured logs,
and builds actionable diagnostics for incident triage.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.frontend.revisao_humana.s3.observability")

COMPONENT_NAME = "workbench_revisao_humana_s3_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_ENTITY_KINDS = {"lead", "evento", "ingresso", "generic"}
ALLOWED_STATUSES = {
    "ready",
    "queued",
    "succeeded",
    "completed",
    "success",
    "failed",
    "fatal_error",
    "timeout",
    "transient_error",
    "retryable_failure",
}
ALLOWED_APPROVAL_MODES = {"single_reviewer", "dual_control", "committee"}

S3_OBSERVABILITY_INTEGRATION_POINTS = {
    "workbench_revisao_s3_core_module": (
        "frontend.src.features.revisao_humana.s3_core.execute_workbench_revisao_s3_main_flow"
    ),
    "workbench_revisao_s3_observability_module": (
        "frontend.src.features.revisao_humana.s3_observability.build_s3_workbench_observability_event"
    ),
    "workbench_revisao_s3_backend_telemetry_module": (
        "backend.app.services.workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry"
    ),
}


class S3WorkbenchObservabilityError(ValueError):
    """Raised when WORK S3 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3WorkbenchObservabilityInput:
    """Input contract used to create one WORK Sprint 3 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    workflow_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    owner_team: str | None = None
    status: str | None = None
    stage: str | None = None
    approval_mode: str | None = None
    required_approvers: int | None = None
    approver_roles_count: int | None = None
    batch_size: int | None = None
    max_pending_batches: int | None = None
    approval_sla_hours: int | None = None
    batches_received: int | None = None
    batches_approved: int | None = None
    batches_rejected: int | None = None
    batches_escalated: int | None = None
    pending_batches: int | None = None
    approvals_recorded: int | None = None
    conflicts_detected: int | None = None
    auto_locked_batches: int | None = None
    partial_approvals: int | None = None
    justifications_missing: int | None = None
    approval_queue_capacity: int | None = None
    approval_overflow_detected: bool | None = None
    require_justification: bool | None = None
    allow_partial_approval: bool | None = None
    auto_lock_on_conflict: bool | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3WorkbenchObservabilityEvent:
    """Output contract for one WORK Sprint 3 observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    workflow_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    owner_team: str | None = None
    status: str | None = None
    stage: str | None = None
    approval_mode: str | None = None
    required_approvers: int | None = None
    approver_roles_count: int | None = None
    batch_size: int | None = None
    max_pending_batches: int | None = None
    approval_sla_hours: int | None = None
    batches_received: int | None = None
    batches_approved: int | None = None
    batches_rejected: int | None = None
    batches_escalated: int | None = None
    pending_batches: int | None = None
    approvals_recorded: int | None = None
    conflicts_detected: int | None = None
    auto_locked_batches: int | None = None
    partial_approvals: int | None = None
    justifications_missing: int | None = None
    approval_queue_capacity: int | None = None
    approval_overflow_detected: bool | None = None
    require_justification: bool | None = None
    allow_partial_approval: bool | None = None
    auto_lock_on_conflict: bool | None = None
    context: dict[str, Any] | None = None

    def to_log_extra(self) -> dict[str, Any]:
        """Return safe dictionary for Python logger `extra` field."""

        return {
            "observability_event_id": self.observability_event_id,
            "timestamp_utc": self.timestamp_utc,
            "component": self.component,
            "event_name": self.event_name,
            "correlation_id": self.correlation_id,
            "event_message": self.event_message,
            "severity": self.severity,
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "owner_team": self.owner_team,
            "status": self.status,
            "stage": self.stage,
            "approval_mode": self.approval_mode,
            "required_approvers": self.required_approvers,
            "approver_roles_count": self.approver_roles_count,
            "batch_size": self.batch_size,
            "max_pending_batches": self.max_pending_batches,
            "approval_sla_hours": self.approval_sla_hours,
            "batches_received": self.batches_received,
            "batches_approved": self.batches_approved,
            "batches_rejected": self.batches_rejected,
            "batches_escalated": self.batches_escalated,
            "pending_batches": self.pending_batches,
            "approvals_recorded": self.approvals_recorded,
            "conflicts_detected": self.conflicts_detected,
            "auto_locked_batches": self.auto_locked_batches,
            "partial_approvals": self.partial_approvals,
            "justifications_missing": self.justifications_missing,
            "approval_queue_capacity": self.approval_queue_capacity,
            "approval_overflow_detected": self.approval_overflow_detected,
            "require_justification": self.require_justification,
            "allow_partial_approval": self.allow_partial_approval,
            "auto_lock_on_conflict": self.auto_lock_on_conflict,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability references for contract outputs."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s3_workbench_observability_event(
    payload: S3WorkbenchObservabilityInput,
) -> S3WorkbenchObservabilityEvent:
    """Build one validated WORK Sprint 3 observability event.

    Args:
        payload: Input contract with operational metadata, approval policy, and
            batch-approval execution metrics for Sprint 3.

    Returns:
        S3WorkbenchObservabilityEvent: Structured event ready for logging.

    Raises:
        S3WorkbenchObservabilityError: If one or more contract fields are
            invalid or inconsistent.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade WORK S3 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade WORK S3 nao pode ser vazio",
            action="Propague correlation_id no fluxo de aprovacao em lote da sprint.",
        )
    if not event_message:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade WORK S3 nao pode ser vazio",
            action="Forneca descricao diagnostica para o evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    entity_kind = _normalize_optional_text(
        field_name="entity_kind",
        value=payload.entity_kind,
        lower=True,
    )
    if entity_kind is not None and entity_kind not in ALLOWED_ENTITY_KINDS:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_ENTITY_KIND",
            message=f"entity_kind de observabilidade invalido: {payload.entity_kind}",
            action="Use entity_kind suportado: lead, evento, ingresso ou generic.",
        )

    status = _normalize_optional_text(field_name="status", value=payload.status, lower=True)
    if status is not None and status not in ALLOWED_STATUSES:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_STATUS",
            message=f"status de observabilidade invalido: {payload.status}",
            action=(
                "Use status valido: ready, queued, succeeded, completed, success, failed, "
                "fatal_error, timeout, transient_error ou retryable_failure."
            ),
        )

    approval_mode = _normalize_optional_text(
        field_name="approval_mode",
        value=payload.approval_mode,
        lower=True,
    )
    if approval_mode is not None and approval_mode not in ALLOWED_APPROVAL_MODES:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_MODE",
            message=f"approval_mode de observabilidade invalido: {payload.approval_mode}",
            action="Use approval_mode valido: single_reviewer, dual_control ou committee.",
        )

    required_approvers = _validate_non_negative_int(
        field_name="required_approvers",
        value=payload.required_approvers,
        error_code="INVALID_WORK_S3_OBSERVABILITY_REQUIRED_APPROVERS",
    )
    approver_roles_count = _validate_non_negative_int(
        field_name="approver_roles_count",
        value=payload.approver_roles_count,
        error_code="INVALID_WORK_S3_OBSERVABILITY_APPROVER_ROLES_COUNT",
    )
    batch_size = _validate_non_negative_int(
        field_name="batch_size",
        value=payload.batch_size,
        error_code="INVALID_WORK_S3_OBSERVABILITY_BATCH_SIZE",
    )
    max_pending_batches = _validate_non_negative_int(
        field_name="max_pending_batches",
        value=payload.max_pending_batches,
        error_code="INVALID_WORK_S3_OBSERVABILITY_MAX_PENDING_BATCHES",
    )
    approval_sla_hours = _validate_non_negative_int(
        field_name="approval_sla_hours",
        value=payload.approval_sla_hours,
        error_code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_SLA_HOURS",
    )
    batches_received = _validate_non_negative_int(
        field_name="batches_received",
        value=payload.batches_received,
        error_code="INVALID_WORK_S3_OBSERVABILITY_BATCHES_RECEIVED",
    )
    batches_approved = _validate_non_negative_int(
        field_name="batches_approved",
        value=payload.batches_approved,
        error_code="INVALID_WORK_S3_OBSERVABILITY_BATCHES_APPROVED",
    )
    batches_rejected = _validate_non_negative_int(
        field_name="batches_rejected",
        value=payload.batches_rejected,
        error_code="INVALID_WORK_S3_OBSERVABILITY_BATCHES_REJECTED",
    )
    batches_escalated = _validate_non_negative_int(
        field_name="batches_escalated",
        value=payload.batches_escalated,
        error_code="INVALID_WORK_S3_OBSERVABILITY_BATCHES_ESCALATED",
    )
    pending_batches = _validate_non_negative_int(
        field_name="pending_batches",
        value=payload.pending_batches,
        error_code="INVALID_WORK_S3_OBSERVABILITY_PENDING_BATCHES",
    )
    approvals_recorded = _validate_non_negative_int(
        field_name="approvals_recorded",
        value=payload.approvals_recorded,
        error_code="INVALID_WORK_S3_OBSERVABILITY_APPROVALS_RECORDED",
    )
    conflicts_detected = _validate_non_negative_int(
        field_name="conflicts_detected",
        value=payload.conflicts_detected,
        error_code="INVALID_WORK_S3_OBSERVABILITY_CONFLICTS_DETECTED",
    )
    auto_locked_batches = _validate_non_negative_int(
        field_name="auto_locked_batches",
        value=payload.auto_locked_batches,
        error_code="INVALID_WORK_S3_OBSERVABILITY_AUTO_LOCKED_BATCHES",
    )
    partial_approvals = _validate_non_negative_int(
        field_name="partial_approvals",
        value=payload.partial_approvals,
        error_code="INVALID_WORK_S3_OBSERVABILITY_PARTIAL_APPROVALS",
    )
    justifications_missing = _validate_non_negative_int(
        field_name="justifications_missing",
        value=payload.justifications_missing,
        error_code="INVALID_WORK_S3_OBSERVABILITY_JUSTIFICATIONS_MISSING",
    )
    approval_queue_capacity = _validate_non_negative_int(
        field_name="approval_queue_capacity",
        value=payload.approval_queue_capacity,
        error_code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_QUEUE_CAPACITY",
    )
    approval_overflow_detected = _validate_optional_bool(
        field_name="approval_overflow_detected",
        value=payload.approval_overflow_detected,
        error_code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_OVERFLOW_DETECTED",
    )
    require_justification = _validate_optional_bool(
        field_name="require_justification",
        value=payload.require_justification,
        error_code="INVALID_WORK_S3_OBSERVABILITY_REQUIRE_JUSTIFICATION",
    )
    allow_partial_approval = _validate_optional_bool(
        field_name="allow_partial_approval",
        value=payload.allow_partial_approval,
        error_code="INVALID_WORK_S3_OBSERVABILITY_ALLOW_PARTIAL_APPROVAL",
    )
    auto_lock_on_conflict = _validate_optional_bool(
        field_name="auto_lock_on_conflict",
        value=payload.auto_lock_on_conflict,
        error_code="INVALID_WORK_S3_OBSERVABILITY_AUTO_LOCK_ON_CONFLICT",
    )

    context: dict[str, Any] = payload.context or {}
    if not isinstance(context, dict):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_CONTEXT",
            message="context deve ser objeto/dicionario quando informado",
            action="Propague context como dict serializavel.",
        )

    _validate_metrics_consistency(
        approval_mode=approval_mode,
        required_approvers=required_approvers,
        approver_roles_count=approver_roles_count,
        batch_size=batch_size,
        max_pending_batches=max_pending_batches,
        approval_sla_hours=approval_sla_hours,
        batches_received=batches_received,
        batches_approved=batches_approved,
        batches_rejected=batches_rejected,
        batches_escalated=batches_escalated,
        pending_batches=pending_batches,
        approvals_recorded=approvals_recorded,
        conflicts_detected=conflicts_detected,
        auto_locked_batches=auto_locked_batches,
        partial_approvals=partial_approvals,
        justifications_missing=justifications_missing,
        approval_queue_capacity=approval_queue_capacity,
        approval_overflow_detected=approval_overflow_detected,
        require_justification=require_justification,
        allow_partial_approval=allow_partial_approval,
        auto_lock_on_conflict=auto_lock_on_conflict,
    )

    return S3WorkbenchObservabilityEvent(
        observability_event_id=f"works3obsevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        workflow_id=_normalize_optional_text(field_name="workflow_id", value=payload.workflow_id),
        dataset_name=_normalize_optional_text(field_name="dataset_name", value=payload.dataset_name),
        entity_kind=entity_kind,
        schema_version=_normalize_optional_text(
            field_name="schema_version",
            value=payload.schema_version,
            lower=True,
        ),
        owner_team=_normalize_optional_text(
            field_name="owner_team",
            value=payload.owner_team,
            lower=True,
        ),
        status=status,
        stage=_normalize_optional_text(field_name="stage", value=payload.stage),
        approval_mode=approval_mode,
        required_approvers=required_approvers,
        approver_roles_count=approver_roles_count,
        batch_size=batch_size,
        max_pending_batches=max_pending_batches,
        approval_sla_hours=approval_sla_hours,
        batches_received=batches_received,
        batches_approved=batches_approved,
        batches_rejected=batches_rejected,
        batches_escalated=batches_escalated,
        pending_batches=pending_batches,
        approvals_recorded=approvals_recorded,
        conflicts_detected=conflicts_detected,
        auto_locked_batches=auto_locked_batches,
        partial_approvals=partial_approvals,
        justifications_missing=justifications_missing,
        approval_queue_capacity=approval_queue_capacity,
        approval_overflow_detected=approval_overflow_detected,
        require_justification=require_justification,
        allow_partial_approval=allow_partial_approval,
        auto_lock_on_conflict=auto_lock_on_conflict,
        context=context,
    )


def log_s3_workbench_observability_event(event: S3WorkbenchObservabilityEvent) -> None:
    """Emit one WORK Sprint 3 observability event to operational logger.

    Args:
        event: Validated observability event contract.
    """

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def build_s3_workbench_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable WORK Sprint 3 diagnostics with observability references.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error description.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        observability_event_id: Event identifier used to locate logs.
        stage: Flow stage where the error was detected.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable error detail with observability references.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "observability_event_id": observability_event_id,
        "stage": stage,
        "context": context or {},
    }


def get_s3_workbench_observability_integration_points() -> dict[str, str]:
    """Return stable WORK Sprint 3 observability integration points.

    Returns:
        dict[str, str]: Module paths that compose the Sprint 3 observability
            and telemetry pipeline.
    """

    return dict(S3_OBSERVABILITY_INTEGRATION_POINTS)


def _normalize_optional_text(
    *,
    field_name: str,
    value: str | None,
    lower: bool = False,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise S3WorkbenchObservabilityError(
            code=f"INVALID_WORK_S3_OBSERVABILITY_{field_name.upper()}",
            message=f"{field_name} deve ser texto quando informado",
            action=f"Propague {field_name} como string valida.",
        )
    normalized = value.strip()
    if not normalized:
        return None
    return normalized.lower() if lower else normalized


def _validate_non_negative_int(
    *,
    field_name: str,
    value: int | None,
    error_code: str,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise S3WorkbenchObservabilityError(
            code=error_code,
            message=f"{field_name} deve ser inteiro >= 0 quando informado",
            action=f"Propague {field_name} com valor inteiro nao negativo.",
        )
    return int(value)


def _validate_optional_bool(
    *,
    field_name: str,
    value: bool | None,
    error_code: str,
) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise S3WorkbenchObservabilityError(
            code=error_code,
            message=f"{field_name} deve ser booleano quando informado",
            action=f"Propague {field_name} com true/false.",
        )
    return value


def _validate_metrics_consistency(
    *,
    approval_mode: str | None,
    required_approvers: int | None,
    approver_roles_count: int | None,
    batch_size: int | None,
    max_pending_batches: int | None,
    approval_sla_hours: int | None,
    batches_received: int | None,
    batches_approved: int | None,
    batches_rejected: int | None,
    batches_escalated: int | None,
    pending_batches: int | None,
    approvals_recorded: int | None,
    conflicts_detected: int | None,
    auto_locked_batches: int | None,
    partial_approvals: int | None,
    justifications_missing: int | None,
    approval_queue_capacity: int | None,
    approval_overflow_detected: bool | None,
    require_justification: bool | None,
    allow_partial_approval: bool | None,
    auto_lock_on_conflict: bool | None,
) -> None:
    if required_approvers is not None and required_approvers <= 0:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_REQUIRED_APPROVERS",
            message="required_approvers deve ser maior que zero",
            action="Ajuste required_approvers para inteiro >= 1.",
        )
    if approver_roles_count is not None and approver_roles_count <= 0:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVER_ROLES_COUNT",
            message="approver_roles_count deve ser maior que zero",
            action="Propague approver_roles_count >= 1 para o fluxo de aprovacao.",
        )
    if batch_size is not None and batch_size <= 0:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_BATCH_SIZE",
            message="batch_size deve ser maior que zero",
            action="Ajuste batch_size para inteiro >= 1.",
        )
    if max_pending_batches is not None and max_pending_batches <= 0:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_MAX_PENDING_BATCHES",
            message="max_pending_batches deve ser maior que zero",
            action="Ajuste max_pending_batches para inteiro >= 1.",
        )
    if approval_sla_hours is not None and approval_sla_hours <= 0:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_SLA_HOURS",
            message="approval_sla_hours deve ser maior que zero",
            action="Ajuste approval_sla_hours para inteiro >= 1.",
        )
    if approval_queue_capacity is not None and approval_queue_capacity <= 0:
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_QUEUE_CAPACITY",
            message="approval_queue_capacity deve ser maior que zero",
            action="Ajuste approval_queue_capacity para inteiro >= 1.",
        )
    if (
        approval_mode == "single_reviewer"
        and required_approvers is not None
        and required_approvers != 1
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_MODE_CONFIGURATION",
            message="approval_mode single_reviewer exige required_approvers=1",
            action="Ajuste required_approvers para 1 ou use outro approval_mode.",
        )
    if (
        approval_mode in {"dual_control", "committee"}
        and required_approvers is not None
        and required_approvers < 2
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_MODE_CONFIGURATION",
            message=f"approval_mode {approval_mode} exige ao menos 2 aprovadores",
            action="Ajuste required_approvers para valor >= 2.",
        )
    if (
        approver_roles_count is not None
        and required_approvers is not None
        and approver_roles_count < required_approvers
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVER_ROLES_CONFIGURATION",
            message="approver_roles_count menor que required_approvers",
            action="Ajuste approver_roles_count ou required_approvers para manter consistencia.",
        )
    if (
        max_pending_batches is not None
        and batch_size is not None
        and max_pending_batches < batch_size
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_PENDING_BATCH_CAPACITY",
            message="max_pending_batches nao pode ser menor que batch_size",
            action="Ajuste max_pending_batches para valor >= batch_size.",
        )
    if (
        approval_queue_capacity is not None
        and max_pending_batches is not None
        and approval_queue_capacity != max_pending_batches
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_QUEUE_CAPACITY_MAPPING",
            message="approval_queue_capacity deve ser igual a max_pending_batches",
            action="Sincronize approval_queue_capacity com max_pending_batches no contrato.",
        )
    if (
        batches_received is not None
        and batches_approved is not None
        and batches_rejected is not None
        and batches_escalated is not None
        and (batches_approved + batches_rejected + batches_escalated) > batches_received
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_BATCH_OUTCOME_COUNTS",
            message="soma de approved/rejected/escalated excede batches_received",
            action="Ajuste metricas para approved+rejected+escalated <= batches_received.",
        )
    if (
        pending_batches is not None
        and batches_received is not None
        and pending_batches > batches_received
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_PENDING_BATCHES",
            message="pending_batches nao pode ser maior que batches_received",
            action="Ajuste pending_batches para refletir batches pendentes reais.",
        )
    if (
        approval_queue_capacity is not None
        and pending_batches is not None
        and pending_batches > approval_queue_capacity
        and approval_overflow_detected is False
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_OVERFLOW_FLAG",
            message="pending_batches excede approval_queue_capacity sem approval_overflow_detected=true",
            action="Defina approval_overflow_detected=true quando pending_batches > approval_queue_capacity.",
        )
    if (
        allow_partial_approval is False
        and partial_approvals is not None
        and partial_approvals > 0
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_PARTIAL_APPROVALS",
            message="partial_approvals deve ser zero quando allow_partial_approval=false",
            action="Retorne partial_approvals=0 ou habilite allow_partial_approval.",
        )
    if (
        allow_partial_approval is True
        and partial_approvals is not None
        and batches_received is not None
        and partial_approvals > batches_received
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_PARTIAL_APPROVAL_COUNT",
            message="partial_approvals nao pode ser maior que batches_received",
            action="Ajuste partial_approvals para <= batches_received.",
        )
    if (
        allow_partial_approval is False
        and approvals_recorded is not None
        and batches_approved is not None
        and required_approvers is not None
        and approvals_recorded < (batches_approved * required_approvers)
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_APPROVAL_RECORDS",
            message="approvals_recorded insuficiente para batches_approved",
            action="Ajuste approvals_recorded para >= batches_approved * required_approvers.",
        )
    if (
        conflicts_detected is not None
        and batches_received is not None
        and conflicts_detected > batches_received
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_CONFLICTS_DETECTED",
            message="conflicts_detected nao pode ser maior que batches_received",
            action="Ajuste conflicts_detected para refletir conflitos processados.",
        )
    if (
        auto_lock_on_conflict is True
        and auto_locked_batches is not None
        and conflicts_detected is not None
        and auto_locked_batches < conflicts_detected
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_AUTO_LOCK_COUNTS",
            message="auto_locked_batches menor que conflicts_detected com auto_lock_on_conflict=true",
            action="Ajuste auto_locked_batches para cobrir conflitos detectados.",
        )
    if (
        auto_lock_on_conflict is False
        and auto_locked_batches is not None
        and auto_locked_batches > 0
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_AUTO_LOCK_CONFIGURATION",
            message="auto_locked_batches deve ser zero quando auto_lock_on_conflict=false",
            action="Retorne auto_locked_batches=0 ou habilite auto_lock_on_conflict.",
        )
    if (
        require_justification is True
        and justifications_missing is not None
        and justifications_missing > 0
        and batches_rejected is not None
        and batches_escalated is not None
        and (batches_rejected > 0 or batches_escalated > 0)
    ):
        raise S3WorkbenchObservabilityError(
            code="INVALID_WORK_S3_OBSERVABILITY_MISSING_JUSTIFICATIONS",
            message="faltam justificativas obrigatorias para rejeicoes/escalonamentos",
            action="Garanta justificativas para todos os casos rejeitados ou escalados.",
        )
