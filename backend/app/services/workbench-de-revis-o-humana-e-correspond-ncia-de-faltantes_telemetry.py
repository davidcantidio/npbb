"""Telemetry helpers for WORK Sprint 1 and Sprint 2 workbench flows.

This service centralizes operational telemetry contracts used by the human
review workbench. It keeps event payloads stable, logs operational signals,
and builds actionable error details for service layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME_S1 = "workbench_revisao_humana_correspondencia_faltantes_s1"
COMPONENT_NAME_S2 = "workbench_revisao_humana_correspondencia_faltantes_s2"
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
ALLOWED_CORRESPONDENCE_MODES = {"manual_confirm", "suggest_only", "semi_auto"}
ALLOWED_MATCH_STRATEGIES = {"exact", "normalized", "fuzzy", "semantic"}

WORKBENCH_S2_TELEMETRY_INTEGRATION_POINTS = {
    "workbench_revisao_s2_observability_module": (
        "frontend.src.features.revisao_humana.s2_observability.build_s2_workbench_observability_event"
    ),
    "workbench_revisao_s2_core_module": (
        "frontend.src.features.revisao_humana.s2_core.execute_workbench_revisao_s2_main_flow"
    ),
    "workbench_revisao_s2_backend_telemetry_module": (
        "backend.app.services.workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry"
    ),
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


class S2WorkbenchTelemetryContractError(ValueError):
    """Raised when WORK S2 telemetry contract input is invalid."""

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


@dataclass(frozen=True, slots=True)
class S2WorkbenchTelemetryInput:
    """Input contract for WORK Sprint 2 telemetry event creation."""

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
    correspondence_mode: str | None = None
    match_strategy: str | None = None
    missing_fields_count: int | None = None
    candidate_sources_count: int | None = None
    reviewer_roles_count: int | None = None
    max_suggestions_per_field: int | None = None
    suggestion_capacity: int | None = None
    candidate_pairs_evaluated: int | None = None
    suggested_matches: int | None = None
    reviewed_matches: int | None = None
    auto_applied_matches: int | None = None
    unresolved_fields_count: int | None = None
    evidence_links_count: int | None = None
    suggestion_overflow_detected: bool | None = None
    require_evidence_for_suggestion: bool | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S2WorkbenchTelemetryEvent:
    """Output contract for one structured WORK Sprint 2 telemetry event."""

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
    status: str | None = None
    stage: str | None = None
    correspondence_mode: str | None = None
    match_strategy: str | None = None
    missing_fields_count: int | None = None
    candidate_sources_count: int | None = None
    reviewer_roles_count: int | None = None
    max_suggestions_per_field: int | None = None
    suggestion_capacity: int | None = None
    candidate_pairs_evaluated: int | None = None
    suggested_matches: int | None = None
    reviewed_matches: int | None = None
    auto_applied_matches: int | None = None
    unresolved_fields_count: int | None = None
    evidence_links_count: int | None = None
    suggestion_overflow_detected: bool | None = None
    require_evidence_for_suggestion: bool | None = None
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
            "status": self.status,
            "stage": self.stage,
            "correspondence_mode": self.correspondence_mode,
            "match_strategy": self.match_strategy,
            "missing_fields_count": self.missing_fields_count,
            "candidate_sources_count": self.candidate_sources_count,
            "reviewer_roles_count": self.reviewer_roles_count,
            "max_suggestions_per_field": self.max_suggestions_per_field,
            "suggestion_capacity": self.suggestion_capacity,
            "candidate_pairs_evaluated": self.candidate_pairs_evaluated,
            "suggested_matches": self.suggested_matches,
            "reviewed_matches": self.reviewed_matches,
            "auto_applied_matches": self.auto_applied_matches,
            "unresolved_fields_count": self.unresolved_fields_count,
            "evidence_links_count": self.evidence_links_count,
            "suggestion_overflow_detected": self.suggestion_overflow_detected,
            "require_evidence_for_suggestion": self.require_evidence_for_suggestion,
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


def build_s2_workbench_telemetry_event(
    payload: S2WorkbenchTelemetryInput,
) -> S2WorkbenchTelemetryEvent:
    """Build a validated WORK Sprint 2 telemetry event.

    Args:
        payload: Input telemetry contract with Sprint 2 correspondence metadata,
            execution metrics, and severity.

    Returns:
        S2WorkbenchTelemetryEvent: Structured event ready for logging.

    Raises:
        S2WorkbenchTelemetryContractError: If one or more fields are invalid or
            inconsistent.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria WORK S2 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria WORK S2 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria WORK S2 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    entity_kind = _normalize_optional_text_s2(
        field_name="entity_kind",
        value=payload.entity_kind,
        lower=True,
    )
    if entity_kind is not None and entity_kind not in ALLOWED_ENTITY_KINDS:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_ENTITY_KIND",
            message=f"entity_kind de telemetria invalido: {payload.entity_kind}",
            action="Use entity_kind suportado: lead, evento, ingresso ou generic.",
        )

    status = _normalize_optional_text_s2(field_name="status", value=payload.status, lower=True)
    if status is not None and status not in ALLOWED_STATUSES:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_STATUS",
            message=f"status de telemetria invalido: {payload.status}",
            action=(
                "Use status valido: ready, queued, succeeded, completed, success, failed, "
                "fatal_error, timeout, transient_error ou retryable_failure."
            ),
        )

    correspondence_mode = _normalize_optional_text_s2(
        field_name="correspondence_mode",
        value=payload.correspondence_mode,
        lower=True,
    )
    if correspondence_mode is not None and correspondence_mode not in ALLOWED_CORRESPONDENCE_MODES:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_CORRESPONDENCE_MODE",
            message=f"correspondence_mode de telemetria invalido: {payload.correspondence_mode}",
            action="Use correspondence_mode valido: manual_confirm, suggest_only ou semi_auto.",
        )

    match_strategy = _normalize_optional_text_s2(
        field_name="match_strategy",
        value=payload.match_strategy,
        lower=True,
    )
    if match_strategy is not None and match_strategy not in ALLOWED_MATCH_STRATEGIES:
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_MATCH_STRATEGY",
            message=f"match_strategy de telemetria invalido: {payload.match_strategy}",
            action="Use match_strategy valido: exact, normalized, fuzzy ou semantic.",
        )

    missing_fields_count = _validate_non_negative_int_s2(
        field_name="missing_fields_count",
        value=payload.missing_fields_count,
        error_code="INVALID_WORK_S2_TELEMETRY_MISSING_FIELDS_COUNT",
    )
    candidate_sources_count = _validate_non_negative_int_s2(
        field_name="candidate_sources_count",
        value=payload.candidate_sources_count,
        error_code="INVALID_WORK_S2_TELEMETRY_CANDIDATE_SOURCES_COUNT",
    )
    reviewer_roles_count = _validate_non_negative_int_s2(
        field_name="reviewer_roles_count",
        value=payload.reviewer_roles_count,
        error_code="INVALID_WORK_S2_TELEMETRY_REVIEWER_ROLES_COUNT",
    )
    max_suggestions_per_field = _validate_non_negative_int_s2(
        field_name="max_suggestions_per_field",
        value=payload.max_suggestions_per_field,
        error_code="INVALID_WORK_S2_TELEMETRY_MAX_SUGGESTIONS_PER_FIELD",
    )
    suggestion_capacity = _validate_non_negative_int_s2(
        field_name="suggestion_capacity",
        value=payload.suggestion_capacity,
        error_code="INVALID_WORK_S2_TELEMETRY_SUGGESTION_CAPACITY",
    )
    candidate_pairs_evaluated = _validate_non_negative_int_s2(
        field_name="candidate_pairs_evaluated",
        value=payload.candidate_pairs_evaluated,
        error_code="INVALID_WORK_S2_TELEMETRY_CANDIDATE_PAIRS_EVALUATED",
    )
    suggested_matches = _validate_non_negative_int_s2(
        field_name="suggested_matches",
        value=payload.suggested_matches,
        error_code="INVALID_WORK_S2_TELEMETRY_SUGGESTED_MATCHES",
    )
    reviewed_matches = _validate_non_negative_int_s2(
        field_name="reviewed_matches",
        value=payload.reviewed_matches,
        error_code="INVALID_WORK_S2_TELEMETRY_REVIEWED_MATCHES",
    )
    auto_applied_matches = _validate_non_negative_int_s2(
        field_name="auto_applied_matches",
        value=payload.auto_applied_matches,
        error_code="INVALID_WORK_S2_TELEMETRY_AUTO_APPLIED_MATCHES",
    )
    unresolved_fields_count = _validate_non_negative_int_s2(
        field_name="unresolved_fields_count",
        value=payload.unresolved_fields_count,
        error_code="INVALID_WORK_S2_TELEMETRY_UNRESOLVED_FIELDS_COUNT",
    )
    evidence_links_count = _validate_non_negative_int_s2(
        field_name="evidence_links_count",
        value=payload.evidence_links_count,
        error_code="INVALID_WORK_S2_TELEMETRY_EVIDENCE_LINKS_COUNT",
    )
    suggestion_overflow_detected = _validate_optional_bool_s2(
        field_name="suggestion_overflow_detected",
        value=payload.suggestion_overflow_detected,
        error_code="INVALID_WORK_S2_TELEMETRY_SUGGESTION_OVERFLOW_DETECTED",
    )
    require_evidence_for_suggestion = _validate_optional_bool_s2(
        field_name="require_evidence_for_suggestion",
        value=payload.require_evidence_for_suggestion,
        error_code="INVALID_WORK_S2_TELEMETRY_REQUIRE_EVIDENCE_FOR_SUGGESTION",
    )

    context = payload.context or {}
    if not isinstance(context, dict):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_CONTEXT",
            message="context deve ser objeto/dicionario quando informado",
            action="Propague context como dict serializavel.",
        )

    _validate_s2_metrics_consistency(
        correspondence_mode=correspondence_mode,
        missing_fields_count=missing_fields_count,
        reviewer_roles_count=reviewer_roles_count,
        max_suggestions_per_field=max_suggestions_per_field,
        suggestion_capacity=suggestion_capacity,
        candidate_pairs_evaluated=candidate_pairs_evaluated,
        suggested_matches=suggested_matches,
        reviewed_matches=reviewed_matches,
        auto_applied_matches=auto_applied_matches,
        unresolved_fields_count=unresolved_fields_count,
        evidence_links_count=evidence_links_count,
        suggestion_overflow_detected=suggestion_overflow_detected,
        require_evidence_for_suggestion=require_evidence_for_suggestion,
    )

    return S2WorkbenchTelemetryEvent(
        telemetry_event_id=f"works2tmlevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S2,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        workflow_id=_normalize_optional_text_s2(field_name="workflow_id", value=payload.workflow_id),
        dataset_name=_normalize_optional_text_s2(field_name="dataset_name", value=payload.dataset_name),
        entity_kind=entity_kind,
        schema_version=_normalize_optional_text_s2(
            field_name="schema_version",
            value=payload.schema_version,
            lower=True,
        ),
        owner_team=_normalize_optional_text_s2(
            field_name="owner_team",
            value=payload.owner_team,
            lower=True,
        ),
        status=status,
        stage=_normalize_optional_text_s2(field_name="stage", value=payload.stage),
        correspondence_mode=correspondence_mode,
        match_strategy=match_strategy,
        missing_fields_count=missing_fields_count,
        candidate_sources_count=candidate_sources_count,
        reviewer_roles_count=reviewer_roles_count,
        max_suggestions_per_field=max_suggestions_per_field,
        suggestion_capacity=suggestion_capacity,
        candidate_pairs_evaluated=candidate_pairs_evaluated,
        suggested_matches=suggested_matches,
        reviewed_matches=reviewed_matches,
        auto_applied_matches=auto_applied_matches,
        unresolved_fields_count=unresolved_fields_count,
        evidence_links_count=evidence_links_count,
        suggestion_overflow_detected=suggestion_overflow_detected,
        require_evidence_for_suggestion=require_evidence_for_suggestion,
        context=context,
    )


def emit_s2_workbench_telemetry_event(
    logger: logging.Logger,
    event: S2WorkbenchTelemetryEvent,
) -> None:
    """Emit one WORK Sprint 2 telemetry event to operational logger.

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


def build_s2_workbench_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable WORK Sprint 2 error detail with telemetry references.

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


def get_workbench_s2_telemetry_integration_points() -> dict[str, str]:
    """Return stable WORK Sprint 2 telemetry integration-point mapping.

    Returns:
        dict[str, str]: Module paths used by Sprint 2 observability/telemetry.
    """

    return dict(WORKBENCH_S2_TELEMETRY_INTEGRATION_POINTS)


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


def _normalize_optional_text_s2(
    *,
    field_name: str,
    value: str | None,
    lower: bool = False,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise S2WorkbenchTelemetryContractError(
            code=f"INVALID_WORK_S2_TELEMETRY_{field_name.upper()}",
            message=f"{field_name} deve ser texto quando informado",
            action=f"Propague {field_name} como string valida.",
        )
    normalized = value.strip()
    if not normalized:
        return None
    return normalized.lower() if lower else normalized


def _validate_non_negative_int_s2(
    *,
    field_name: str,
    value: int | None,
    error_code: str,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise S2WorkbenchTelemetryContractError(
            code=error_code,
            message=f"{field_name} deve ser inteiro >= 0 quando informado",
            action=f"Propague {field_name} com valor inteiro nao negativo.",
        )
    return int(value)


def _validate_optional_bool_s2(
    *,
    field_name: str,
    value: bool | None,
    error_code: str,
) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise S2WorkbenchTelemetryContractError(
            code=error_code,
            message=f"{field_name} deve ser booleano quando informado",
            action=f"Propague {field_name} com true/false.",
        )
    return value


def _validate_s2_metrics_consistency(
    *,
    correspondence_mode: str | None,
    missing_fields_count: int | None,
    reviewer_roles_count: int | None,
    max_suggestions_per_field: int | None,
    suggestion_capacity: int | None,
    candidate_pairs_evaluated: int | None,
    suggested_matches: int | None,
    reviewed_matches: int | None,
    auto_applied_matches: int | None,
    unresolved_fields_count: int | None,
    evidence_links_count: int | None,
    suggestion_overflow_detected: bool | None,
    require_evidence_for_suggestion: bool | None,
) -> None:
    if (
        suggestion_capacity is not None
        and missing_fields_count is not None
        and max_suggestions_per_field is not None
        and suggestion_capacity != (missing_fields_count * max_suggestions_per_field)
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_SUGGESTION_CAPACITY",
            message="suggestion_capacity inconsistente com missing_fields_count e max_suggestions_per_field",
            action="Ajuste suggestion_capacity para missing_fields_count * max_suggestions_per_field.",
        )
    if (
        reviewed_matches is not None
        and suggested_matches is not None
        and reviewed_matches > suggested_matches
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_REVIEWED_GT_SUGGESTED",
            message="reviewed_matches nao pode ser maior que suggested_matches",
            action="Ajuste reviewed_matches para <= suggested_matches.",
        )
    if (
        auto_applied_matches is not None
        and suggested_matches is not None
        and auto_applied_matches > suggested_matches
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_AUTO_APPLIED_GT_SUGGESTED",
            message="auto_applied_matches nao pode ser maior que suggested_matches",
            action="Ajuste auto_applied_matches para <= suggested_matches.",
        )
    if (
        unresolved_fields_count is not None
        and missing_fields_count is not None
        and unresolved_fields_count > missing_fields_count
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_UNRESOLVED_GT_MISSING",
            message="unresolved_fields_count nao pode ser maior que missing_fields_count",
            action="Ajuste unresolved_fields_count para <= missing_fields_count.",
        )
    if (
        candidate_pairs_evaluated is not None
        and suggested_matches is not None
        and candidate_pairs_evaluated < suggested_matches
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_CANDIDATES_LT_SUGGESTED",
            message="candidate_pairs_evaluated nao pode ser menor que suggested_matches",
            action="Ajuste candidate_pairs_evaluated para refletir pares avaliados.",
        )
    if (
        suggestion_capacity is not None
        and suggested_matches is not None
        and suggested_matches > suggestion_capacity
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_SUGGESTED_GT_CAPACITY",
            message="suggested_matches nao pode ser maior que suggestion_capacity",
            action="Ajuste suggested_matches para <= suggestion_capacity.",
        )
    if (
        suggestion_capacity is not None
        and candidate_pairs_evaluated is not None
        and candidate_pairs_evaluated > suggestion_capacity
        and suggestion_overflow_detected is False
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_OVERFLOW_FLAG",
            message="candidate_pairs_evaluated excede suggestion_capacity sem suggestion_overflow_detected=true",
            action="Defina suggestion_overflow_detected=true quando candidate_pairs_evaluated > suggestion_capacity.",
        )
    if (
        correspondence_mode in {"manual_confirm", "suggest_only"}
        and auto_applied_matches is not None
        and auto_applied_matches > 0
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_AUTO_APPLY_FOR_MODE",
            message=f"auto_applied_matches deve ser zero para correspondence_mode {correspondence_mode}",
            action="Retorne auto_applied_matches=0 ou use correspondence_mode=semi_auto.",
        )
    if (
        require_evidence_for_suggestion is True
        and suggested_matches is not None
        and suggested_matches > 0
        and (evidence_links_count is None or evidence_links_count <= 0)
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_MISSING_EVIDENCE_LINKS",
            message="require_evidence_for_suggestion ativo sem evidence_links_count positivo",
            action="Propague evidence_links_count > 0 ou desative require_evidence_for_suggestion.",
        )
    if (
        reviewer_roles_count is not None
        and reviewer_roles_count <= 0
        and reviewed_matches is not None
        and reviewed_matches > 0
    ):
        raise S2WorkbenchTelemetryContractError(
            code="INVALID_WORK_S2_TELEMETRY_REVIEW_WITHOUT_REVIEWER",
            message="reviewed_matches positivo sem reviewer_roles_count valido",
            action="Propague reviewer_roles_count >= 1 quando reviewed_matches > 0.",
        )
