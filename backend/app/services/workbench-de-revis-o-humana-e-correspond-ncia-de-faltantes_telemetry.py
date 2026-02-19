"""Telemetry helpers for WORK Sprint 1 human-review workbench flow.

This service centralizes operational telemetry contracts used by Sprint 1 of
the workbench for missing-field correspondence and review queue execution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME_S1 = "workbench_revisao_humana_correspondencia_faltantes_s1"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_ENTITY_KINDS = {"lead", "evento", "ingresso", "generic"}
ALLOWED_PRIORITIES = {"baixa", "media", "alta", "critica"}
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


class S1WorkbenchTelemetryContractError(ValueError):
    """Raised when WORK S1 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1WorkbenchTelemetryInput:
    """Input contract for WORK Sprint 1 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    workflow_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    owner_team: str | None = None
    default_priority: str | None = None
    status: str | None = None
    stage: str | None = None
    required_fields_count: int | None = None
    evidence_sources_count: int | None = None
    reviewer_roles_count: int | None = None
    max_queue_size: int | None = None
    generated_items: int | None = None
    queue_size: int | None = None
    critical_items: int | None = None
    assigned_items: int | None = None
    pending_fields_count: int | None = None
    overflow_detected: bool | None = None
    auto_assignment_enabled: bool | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1WorkbenchTelemetryEvent:
    """Output contract for one structured WORK Sprint 1 telemetry event."""

    telemetry_event_id: str
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
    default_priority: str | None = None
    status: str | None = None
    stage: str | None = None
    required_fields_count: int | None = None
    evidence_sources_count: int | None = None
    reviewer_roles_count: int | None = None
    max_queue_size: int | None = None
    generated_items: int | None = None
    queue_size: int | None = None
    critical_items: int | None = None
    assigned_items: int | None = None
    pending_fields_count: int | None = None
    overflow_detected: bool | None = None
    auto_assignment_enabled: bool | None = None
    context: dict[str, Any] | None = None

    def to_log_extra(self) -> dict[str, Any]:
        """Return safe dictionary for `logging.Logger.*(..., extra=...)`."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
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
            "default_priority": self.default_priority,
            "status": self.status,
            "stage": self.stage,
            "required_fields_count": self.required_fields_count,
            "evidence_sources_count": self.evidence_sources_count,
            "reviewer_roles_count": self.reviewer_roles_count,
            "max_queue_size": self.max_queue_size,
            "generated_items": self.generated_items,
            "queue_size": self.queue_size,
            "critical_items": self.critical_items,
            "assigned_items": self.assigned_items,
            "pending_fields_count": self.pending_fields_count,
            "overflow_detected": self.overflow_detected,
            "auto_assignment_enabled": self.auto_assignment_enabled,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry references for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_workbench_telemetry_event(
    payload: S1WorkbenchTelemetryInput,
) -> S1WorkbenchTelemetryEvent:
    """Build a validated WORK Sprint 1 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S1WorkbenchTelemetryEvent: Structured event ready for logging.

    Raises:
        S1WorkbenchTelemetryContractError: If one or more fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria WORK S1 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria WORK S1 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria WORK S1 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    entity_kind = _normalize_optional_text(
        field_name="entity_kind",
        value=payload.entity_kind,
        lower=True,
    )
    if entity_kind is not None and entity_kind not in ALLOWED_ENTITY_KINDS:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_ENTITY_KIND",
            message=f"entity_kind de telemetria invalido: {payload.entity_kind}",
            action="Use entity_kind suportado: lead, evento, ingresso ou generic.",
        )

    default_priority = _normalize_optional_text(
        field_name="default_priority",
        value=payload.default_priority,
        lower=True,
    )
    if default_priority is not None and default_priority not in ALLOWED_PRIORITIES:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_DEFAULT_PRIORITY",
            message=f"default_priority de telemetria invalido: {payload.default_priority}",
            action="Use prioridade valida: baixa, media, alta ou critica.",
        )

    status = _normalize_optional_text(field_name="status", value=payload.status, lower=True)
    if status is not None and status not in ALLOWED_STATUSES:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_STATUS",
            message=f"status de telemetria invalido: {payload.status}",
            action=(
                "Use status valido: ready, queued, succeeded, completed, success, failed, "
                "fatal_error, timeout, transient_error ou retryable_failure."
            ),
        )

    required_fields_count = _validate_non_negative_int(
        field_name="required_fields_count",
        value=payload.required_fields_count,
        error_code="INVALID_WORK_S1_TELEMETRY_REQUIRED_FIELDS_COUNT",
    )
    evidence_sources_count = _validate_non_negative_int(
        field_name="evidence_sources_count",
        value=payload.evidence_sources_count,
        error_code="INVALID_WORK_S1_TELEMETRY_EVIDENCE_SOURCES_COUNT",
    )
    reviewer_roles_count = _validate_non_negative_int(
        field_name="reviewer_roles_count",
        value=payload.reviewer_roles_count,
        error_code="INVALID_WORK_S1_TELEMETRY_REVIEWER_ROLES_COUNT",
    )
    max_queue_size = _validate_non_negative_int(
        field_name="max_queue_size",
        value=payload.max_queue_size,
        error_code="INVALID_WORK_S1_TELEMETRY_MAX_QUEUE_SIZE",
    )
    generated_items = _validate_non_negative_int(
        field_name="generated_items",
        value=payload.generated_items,
        error_code="INVALID_WORK_S1_TELEMETRY_GENERATED_ITEMS",
    )
    queue_size = _validate_non_negative_int(
        field_name="queue_size",
        value=payload.queue_size,
        error_code="INVALID_WORK_S1_TELEMETRY_QUEUE_SIZE",
    )
    critical_items = _validate_non_negative_int(
        field_name="critical_items",
        value=payload.critical_items,
        error_code="INVALID_WORK_S1_TELEMETRY_CRITICAL_ITEMS",
    )
    assigned_items = _validate_non_negative_int(
        field_name="assigned_items",
        value=payload.assigned_items,
        error_code="INVALID_WORK_S1_TELEMETRY_ASSIGNED_ITEMS",
    )
    pending_fields_count = _validate_non_negative_int(
        field_name="pending_fields_count",
        value=payload.pending_fields_count,
        error_code="INVALID_WORK_S1_TELEMETRY_PENDING_FIELDS_COUNT",
    )
    overflow_detected = _validate_optional_bool(
        field_name="overflow_detected",
        value=payload.overflow_detected,
        error_code="INVALID_WORK_S1_TELEMETRY_OVERFLOW_DETECTED",
    )
    auto_assignment_enabled = _validate_optional_bool(
        field_name="auto_assignment_enabled",
        value=payload.auto_assignment_enabled,
        error_code="INVALID_WORK_S1_TELEMETRY_AUTO_ASSIGNMENT_ENABLED",
    )

    _validate_metrics_consistency(
        generated_items=generated_items,
        queue_size=queue_size,
        max_queue_size=max_queue_size,
        critical_items=critical_items,
        assigned_items=assigned_items,
        overflow_detected=overflow_detected,
        auto_assignment_enabled=auto_assignment_enabled,
    )

    return S1WorkbenchTelemetryEvent(
        telemetry_event_id=f"works1tmlevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S1,
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
        default_priority=default_priority,
        status=status,
        stage=_normalize_optional_text(field_name="stage", value=payload.stage),
        required_fields_count=required_fields_count,
        evidence_sources_count=evidence_sources_count,
        reviewer_roles_count=reviewer_roles_count,
        max_queue_size=max_queue_size,
        generated_items=generated_items,
        queue_size=queue_size,
        critical_items=critical_items,
        assigned_items=assigned_items,
        pending_fields_count=pending_fields_count,
        overflow_detected=overflow_detected,
        auto_assignment_enabled=auto_assignment_enabled,
        context=payload.context or {},
    )


def emit_s1_workbench_telemetry_event(
    logger: logging.Logger,
    event: S1WorkbenchTelemetryEvent,
) -> None:
    """Emit one WORK Sprint 1 telemetry event to operational logger.

    Args:
        logger: Logger instance used by the backend service layer.
        event: Structured telemetry event to be logged.
    """

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def build_s1_workbench_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable WORK Sprint 1 error detail with telemetry references.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action to fix or diagnose the error.
        correlation_id: Correlation identifier for cross-service tracing.
        telemetry_event_id: Telemetry event identifier for log lookup.
        stage: Flow stage where the error happened.
        context: Optional contextual fields attached to diagnostics payload.

    Returns:
        dict[str, Any]: Stable service error detail payload.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "telemetry_event_id": telemetry_event_id,
        "stage": stage,
        "context": context or {},
    }


def _normalize_optional_text(
    *,
    field_name: str,
    value: str | None,
    lower: bool = False,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise S1WorkbenchTelemetryContractError(
            code=f"INVALID_WORK_S1_TELEMETRY_{field_name.upper()}",
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
        raise S1WorkbenchTelemetryContractError(
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
        raise S1WorkbenchTelemetryContractError(
            code=error_code,
            message=f"{field_name} deve ser booleano quando informado",
            action=f"Propague {field_name} com true/false.",
        )
    return value


def _validate_metrics_consistency(
    *,
    generated_items: int | None,
    queue_size: int | None,
    max_queue_size: int | None,
    critical_items: int | None,
    assigned_items: int | None,
    overflow_detected: bool | None,
    auto_assignment_enabled: bool | None,
) -> None:
    if generated_items is not None and critical_items is not None and critical_items > generated_items:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_CRITICAL_GT_GENERATED",
            message="critical_items nao pode ser maior que generated_items",
            action="Ajuste metricas de fila para manter consistencia operacional.",
        )
    if generated_items is not None and assigned_items is not None and assigned_items > generated_items:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_ASSIGNED_GT_GENERATED",
            message="assigned_items nao pode ser maior que generated_items",
            action="Ajuste atribuicoes para manter assigned_items <= generated_items.",
        )
    if (
        auto_assignment_enabled is True
        and generated_items is not None
        and generated_items > 0
        and assigned_items is not None
        and assigned_items <= 0
    ):
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_AUTO_ASSIGNMENT_WITHOUT_ASSIGNMENTS",
            message="auto_assignment_enabled ativo sem assigned_items positivo",
            action="Propague assigned_items > 0 ou desative auto_assignment_enabled.",
        )
    if queue_size is not None and generated_items is not None and queue_size > generated_items:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_QUEUE_GT_GENERATED",
            message="queue_size nao pode ser maior que generated_items",
            action="Ajuste metricas de fila para queue_size <= generated_items.",
        )
    if max_queue_size is not None and queue_size is not None and queue_size > max_queue_size:
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_QUEUE_GT_MAX",
            message="queue_size nao pode ser maior que max_queue_size",
            action="Ajuste metricas para queue_size <= max_queue_size.",
        )
    if (
        generated_items is not None
        and max_queue_size is not None
        and generated_items > max_queue_size
        and overflow_detected is False
    ):
        raise S1WorkbenchTelemetryContractError(
            code="INVALID_WORK_S1_TELEMETRY_OVERFLOW_FLAG",
            message="generated_items excede max_queue_size sem overflow_detected=true",
            action="Defina overflow_detected=true quando generated_items > max_queue_size.",
        )

