"""Observability contracts for WORK Sprint 2 correspondence flow.

This module standardizes operational observability events for Sprint 2 of the
human-review workbench. It validates payload contracts, emits structured logs,
and builds actionable diagnostics for incident triage.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.frontend.revisao_humana.s2.observability")

COMPONENT_NAME = "workbench_revisao_humana_s2_core"
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
ALLOWED_CORRESPONDENCE_MODES = {"manual_confirm", "suggest_only", "semi_auto"}
ALLOWED_MATCH_STRATEGIES = {"exact", "normalized", "fuzzy", "semantic"}

S2_OBSERVABILITY_INTEGRATION_POINTS = {
    "workbench_revisao_s2_core_module": (
        "frontend.src.features.revisao_humana.s2_core.execute_workbench_revisao_s2_main_flow"
    ),
    "workbench_revisao_s2_observability_module": (
        "frontend.src.features.revisao_humana.s2_observability.build_s2_workbench_observability_event"
    ),
    "workbench_revisao_s2_backend_telemetry_module": (
        "backend.app.services.workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry"
    ),
}


class S2WorkbenchObservabilityError(ValueError):
    """Raised when WORK S2 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2WorkbenchObservabilityInput:
    """Input contract used to create one WORK Sprint 2 observability event."""

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
class S2WorkbenchObservabilityEvent:
    """Output contract for one WORK Sprint 2 observability event."""

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
        """Return compact observability references for contract outputs."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s2_workbench_observability_event(
    payload: S2WorkbenchObservabilityInput,
) -> S2WorkbenchObservabilityEvent:
    """Build one validated WORK Sprint 2 observability event.

    Args:
        payload: Input contract with operational metadata, status, and
            correspondence metrics for Sprint 2.

    Returns:
        S2WorkbenchObservabilityEvent: Structured event ready for logging.

    Raises:
        S2WorkbenchObservabilityError: If one or more contract fields are
            invalid or inconsistent.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade WORK S2 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade WORK S2 nao pode ser vazio",
            action="Propague correlation_id no fluxo de correspondencia da sprint.",
        )
    if not event_message:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade WORK S2 nao pode ser vazio",
            action="Forneca descricao diagnostica para o evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    entity_kind = _normalize_optional_text(
        field_name="entity_kind",
        value=payload.entity_kind,
        lower=True,
    )
    if entity_kind is not None and entity_kind not in ALLOWED_ENTITY_KINDS:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_ENTITY_KIND",
            message=f"entity_kind de observabilidade invalido: {payload.entity_kind}",
            action="Use entity_kind suportado: lead, evento, ingresso ou generic.",
        )

    status = _normalize_optional_text(field_name="status", value=payload.status, lower=True)
    if status is not None and status not in ALLOWED_STATUSES:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_STATUS",
            message=f"status de observabilidade invalido: {payload.status}",
            action=(
                "Use status valido: ready, queued, succeeded, completed, success, failed, "
                "fatal_error, timeout, transient_error ou retryable_failure."
            ),
        )

    correspondence_mode = _normalize_optional_text(
        field_name="correspondence_mode",
        value=payload.correspondence_mode,
        lower=True,
    )
    if correspondence_mode is not None and correspondence_mode not in ALLOWED_CORRESPONDENCE_MODES:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_CORRESPONDENCE_MODE",
            message=f"correspondence_mode de observabilidade invalido: {payload.correspondence_mode}",
            action="Use correspondence_mode valido: manual_confirm, suggest_only ou semi_auto.",
        )

    match_strategy = _normalize_optional_text(
        field_name="match_strategy",
        value=payload.match_strategy,
        lower=True,
    )
    if match_strategy is not None and match_strategy not in ALLOWED_MATCH_STRATEGIES:
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_MATCH_STRATEGY",
            message=f"match_strategy de observabilidade invalido: {payload.match_strategy}",
            action="Use match_strategy valido: exact, normalized, fuzzy ou semantic.",
        )

    missing_fields_count = _validate_non_negative_int(
        field_name="missing_fields_count",
        value=payload.missing_fields_count,
        error_code="INVALID_WORK_S2_OBSERVABILITY_MISSING_FIELDS_COUNT",
    )
    candidate_sources_count = _validate_non_negative_int(
        field_name="candidate_sources_count",
        value=payload.candidate_sources_count,
        error_code="INVALID_WORK_S2_OBSERVABILITY_CANDIDATE_SOURCES_COUNT",
    )
    reviewer_roles_count = _validate_non_negative_int(
        field_name="reviewer_roles_count",
        value=payload.reviewer_roles_count,
        error_code="INVALID_WORK_S2_OBSERVABILITY_REVIEWER_ROLES_COUNT",
    )
    max_suggestions_per_field = _validate_non_negative_int(
        field_name="max_suggestions_per_field",
        value=payload.max_suggestions_per_field,
        error_code="INVALID_WORK_S2_OBSERVABILITY_MAX_SUGGESTIONS_PER_FIELD",
    )
    suggestion_capacity = _validate_non_negative_int(
        field_name="suggestion_capacity",
        value=payload.suggestion_capacity,
        error_code="INVALID_WORK_S2_OBSERVABILITY_SUGGESTION_CAPACITY",
    )
    candidate_pairs_evaluated = _validate_non_negative_int(
        field_name="candidate_pairs_evaluated",
        value=payload.candidate_pairs_evaluated,
        error_code="INVALID_WORK_S2_OBSERVABILITY_CANDIDATE_PAIRS_EVALUATED",
    )
    suggested_matches = _validate_non_negative_int(
        field_name="suggested_matches",
        value=payload.suggested_matches,
        error_code="INVALID_WORK_S2_OBSERVABILITY_SUGGESTED_MATCHES",
    )
    reviewed_matches = _validate_non_negative_int(
        field_name="reviewed_matches",
        value=payload.reviewed_matches,
        error_code="INVALID_WORK_S2_OBSERVABILITY_REVIEWED_MATCHES",
    )
    auto_applied_matches = _validate_non_negative_int(
        field_name="auto_applied_matches",
        value=payload.auto_applied_matches,
        error_code="INVALID_WORK_S2_OBSERVABILITY_AUTO_APPLIED_MATCHES",
    )
    unresolved_fields_count = _validate_non_negative_int(
        field_name="unresolved_fields_count",
        value=payload.unresolved_fields_count,
        error_code="INVALID_WORK_S2_OBSERVABILITY_UNRESOLVED_FIELDS_COUNT",
    )
    evidence_links_count = _validate_non_negative_int(
        field_name="evidence_links_count",
        value=payload.evidence_links_count,
        error_code="INVALID_WORK_S2_OBSERVABILITY_EVIDENCE_LINKS_COUNT",
    )
    suggestion_overflow_detected = _validate_optional_bool(
        field_name="suggestion_overflow_detected",
        value=payload.suggestion_overflow_detected,
        error_code="INVALID_WORK_S2_OBSERVABILITY_SUGGESTION_OVERFLOW_DETECTED",
    )
    require_evidence_for_suggestion = _validate_optional_bool(
        field_name="require_evidence_for_suggestion",
        value=payload.require_evidence_for_suggestion,
        error_code="INVALID_WORK_S2_OBSERVABILITY_REQUIRE_EVIDENCE_FOR_SUGGESTION",
    )

    context: dict[str, Any] = payload.context or {}
    if not isinstance(context, dict):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_CONTEXT",
            message="context deve ser objeto/dicionario quando informado",
            action="Propague context como dict serializavel.",
        )

    _validate_metrics_consistency(
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

    return S2WorkbenchObservabilityEvent(
        observability_event_id=f"works2obsevt-{uuid4().hex[:12]}",
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


def log_s2_workbench_observability_event(event: S2WorkbenchObservabilityEvent) -> None:
    """Emit one WORK Sprint 2 observability event to operational logger.

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


def build_s2_workbench_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable WORK Sprint 2 diagnostics with observability references.

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


def get_s2_workbench_observability_integration_points() -> dict[str, str]:
    """Return stable WORK Sprint 2 observability integration points.

    Returns:
        dict[str, str]: Module paths that compose the Sprint 2 observability
            and telemetry pipeline.
    """

    return dict(S2_OBSERVABILITY_INTEGRATION_POINTS)


def _normalize_optional_text(
    *,
    field_name: str,
    value: str | None,
    lower: bool = False,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise S2WorkbenchObservabilityError(
            code=f"INVALID_WORK_S2_OBSERVABILITY_{field_name.upper()}",
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
        raise S2WorkbenchObservabilityError(
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
        raise S2WorkbenchObservabilityError(
            code=error_code,
            message=f"{field_name} deve ser booleano quando informado",
            action=f"Propague {field_name} com true/false.",
        )
    return value


def _validate_metrics_consistency(
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
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_SUGGESTION_CAPACITY",
            message="suggestion_capacity inconsistente com missing_fields_count e max_suggestions_per_field",
            action="Ajuste suggestion_capacity para missing_fields_count * max_suggestions_per_field.",
        )
    if (
        reviewed_matches is not None
        and suggested_matches is not None
        and reviewed_matches > suggested_matches
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_REVIEWED_GT_SUGGESTED",
            message="reviewed_matches nao pode ser maior que suggested_matches",
            action="Ajuste reviewed_matches para <= suggested_matches.",
        )
    if (
        auto_applied_matches is not None
        and suggested_matches is not None
        and auto_applied_matches > suggested_matches
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_AUTO_APPLIED_GT_SUGGESTED",
            message="auto_applied_matches nao pode ser maior que suggested_matches",
            action="Ajuste auto_applied_matches para <= suggested_matches.",
        )
    if (
        unresolved_fields_count is not None
        and missing_fields_count is not None
        and unresolved_fields_count > missing_fields_count
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_UNRESOLVED_GT_MISSING",
            message="unresolved_fields_count nao pode ser maior que missing_fields_count",
            action="Ajuste unresolved_fields_count para <= missing_fields_count.",
        )
    if (
        candidate_pairs_evaluated is not None
        and suggested_matches is not None
        and candidate_pairs_evaluated < suggested_matches
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_CANDIDATES_LT_SUGGESTED",
            message="candidate_pairs_evaluated nao pode ser menor que suggested_matches",
            action="Ajuste candidate_pairs_evaluated para refletir pares avaliados.",
        )
    if (
        suggestion_capacity is not None
        and suggested_matches is not None
        and suggested_matches > suggestion_capacity
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_SUGGESTED_GT_CAPACITY",
            message="suggested_matches nao pode ser maior que suggestion_capacity",
            action="Ajuste suggested_matches para <= suggestion_capacity.",
        )
    if (
        suggestion_capacity is not None
        and candidate_pairs_evaluated is not None
        and candidate_pairs_evaluated > suggestion_capacity
        and suggestion_overflow_detected is False
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_OVERFLOW_FLAG",
            message="candidate_pairs_evaluated excede suggestion_capacity sem suggestion_overflow_detected=true",
            action="Defina suggestion_overflow_detected=true quando candidate_pairs_evaluated > suggestion_capacity.",
        )
    if (
        correspondence_mode in {"manual_confirm", "suggest_only"}
        and auto_applied_matches is not None
        and auto_applied_matches > 0
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_AUTO_APPLY_FOR_MODE",
            message=f"auto_applied_matches deve ser zero para correspondence_mode {correspondence_mode}",
            action="Retorne auto_applied_matches=0 ou use correspondence_mode=semi_auto.",
        )
    if (
        require_evidence_for_suggestion is True
        and suggested_matches is not None
        and suggested_matches > 0
        and (evidence_links_count is None or evidence_links_count <= 0)
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_MISSING_EVIDENCE_LINKS",
            message="require_evidence_for_suggestion ativo sem evidence_links_count positivo",
            action="Propague evidence_links_count > 0 ou desative require_evidence_for_suggestion.",
        )
    if (
        reviewer_roles_count is not None
        and reviewer_roles_count <= 0
        and reviewed_matches is not None
        and reviewed_matches > 0
    ):
        raise S2WorkbenchObservabilityError(
            code="INVALID_WORK_S2_OBSERVABILITY_REVIEW_WITHOUT_REVIEWER",
            message="reviewed_matches positivo sem reviewer_roles_count valido",
            action="Propague reviewer_roles_count >= 1 quando reviewed_matches > 0.",
        )
