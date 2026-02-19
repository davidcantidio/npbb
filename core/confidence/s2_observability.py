"""Observability contracts for CONF Sprint 2 confidence decision policy flow.

This module standardizes operational events for Sprint 2 confidence decision
policy execution and provides actionable diagnostics correlated with service
telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.confidence.s2.core")

COMPONENT_NAME = "confidence_policy_s2_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}

MIN_CONFIDENCE_SCORE = 0.0
MAX_CONFIDENCE_SCORE = 1.0


class S2ConfidenceObservabilityError(ValueError):
    """Raised when CONF S2 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2ConfidenceObservabilityInput:
    """Input contract used to create one CONF Sprint 2 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    policy_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    decision_mode: str | None = None
    confidence_score: float | None = None
    decision: str | None = None
    manual_review_queue_size: int | None = None
    max_manual_review_queue: int | None = None
    gap_escalation_triggered: bool | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S2ConfidenceObservabilityEvent:
    """Output contract for one CONF Sprint 2 observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    policy_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    decision_mode: str | None = None
    confidence_score: float | None = None
    decision: str | None = None
    manual_review_queue_size: int | None = None
    max_manual_review_queue: int | None = None
    gap_escalation_triggered: bool | None = None
    stage: str | None = None
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
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "decision_mode": self.decision_mode,
            "confidence_score": self.confidence_score,
            "decision": self.decision,
            "manual_review_queue_size": self.manual_review_queue_size,
            "max_manual_review_queue": self.max_manual_review_queue,
            "gap_escalation_triggered": self.gap_escalation_triggered,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s2_confidence_observability_event(
    payload: S2ConfidenceObservabilityInput,
) -> S2ConfidenceObservabilityEvent:
    """Build validated CONF Sprint 2 observability event.

    Args:
        payload: Input observability contract with event details and context.

    Returns:
        S2ConfidenceObservabilityEvent: Structured event ready for logging.

    Raises:
        S2ConfidenceObservabilityError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade CONF S2 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade CONF S2 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo de confianca.",
        )
    if not event_message:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade CONF S2 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    confidence_score = payload.confidence_score
    if confidence_score is not None:
        if isinstance(confidence_score, bool) or not isinstance(confidence_score, (int, float)):
            raise S2ConfidenceObservabilityError(
                code="INVALID_CONF_S2_OBSERVABILITY_CONFIDENCE_SCORE",
                message="confidence_score deve ser numerico",
                action="Propague confidence_score numerico no intervalo de 0.0 a 1.0.",
            )
        confidence_score = float(confidence_score)
        if confidence_score < MIN_CONFIDENCE_SCORE or confidence_score > MAX_CONFIDENCE_SCORE:
            raise S2ConfidenceObservabilityError(
                code="INVALID_CONF_S2_OBSERVABILITY_CONFIDENCE_SCORE",
                message=f"confidence_score fora do intervalo permitido: {payload.confidence_score}",
                action="Use confidence_score no intervalo de 0.0 a 1.0.",
            )
        confidence_score = round(confidence_score, 6)

    decision = (payload.decision or "").strip().lower() or None
    if decision is not None and decision not in ALLOWED_DECISIONS:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_DECISION",
            message=f"decision de observabilidade invalida: {payload.decision}",
            action="Use decision valida: auto_approve, manual_review, gap ou reject.",
        )

    manual_review_queue_size = payload.manual_review_queue_size
    if manual_review_queue_size is not None and manual_review_queue_size < 0:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_MANUAL_REVIEW_QUEUE_SIZE",
            message="manual_review_queue_size de observabilidade CONF S2 deve ser >= 0",
            action="Propague manual_review_queue_size valido para rastreabilidade operacional.",
        )

    max_manual_review_queue = payload.max_manual_review_queue
    if max_manual_review_queue is not None and max_manual_review_queue < 0:
        raise S2ConfidenceObservabilityError(
            code="INVALID_CONF_S2_OBSERVABILITY_MAX_MANUAL_REVIEW_QUEUE",
            message="max_manual_review_queue de observabilidade CONF S2 deve ser >= 0",
            action="Propague max_manual_review_queue valido para rastreabilidade operacional.",
        )

    return S2ConfidenceObservabilityEvent(
        observability_event_id=f"confs2coreevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        policy_id=(payload.policy_id or "").strip() or None,
        dataset_name=(payload.dataset_name or "").strip() or None,
        entity_kind=(payload.entity_kind or "").strip().lower() or None,
        schema_version=(payload.schema_version or "").strip().lower() or None,
        decision_mode=(payload.decision_mode or "").strip().lower() or None,
        confidence_score=confidence_score,
        decision=decision,
        manual_review_queue_size=manual_review_queue_size,
        max_manual_review_queue=max_manual_review_queue,
        gap_escalation_triggered=payload.gap_escalation_triggered,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def log_s2_confidence_observability_event(event: S2ConfidenceObservabilityEvent) -> None:
    """Emit one CONF Sprint 2 observability event to operational logger.

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


def build_s2_confidence_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONF Sprint 2 error payload for diagnostics.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error description.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        observability_event_id: Observability event identifier for log lookup.
        stage: Flow stage where the failure was detected.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable error payload enriched with observability refs.
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
