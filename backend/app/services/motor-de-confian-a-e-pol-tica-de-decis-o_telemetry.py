"""Telemetry helpers for CONF Sprint 1 confidence policy flow.

This service centralizes operational telemetry contracts used by the confidence
policy flow. It keeps event payloads stable and builds actionable error details
for service layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME_S1 = "motor_de_confianca_e_politica_de_decisao_s1"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_DECISIONS = {"auto_approve", "manual_review", "reject"}

MIN_CONFIDENCE_SCORE = 0.0
MAX_CONFIDENCE_SCORE = 1.0


class S1ConfidenceTelemetryContractError(ValueError):
    """Raised when CONF Sprint 1 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1ConfidenceTelemetryInput:
    """Input contract for CONF Sprint 1 telemetry event creation."""

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
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1ConfidenceTelemetryEvent:
    """Output contract for one structured CONF Sprint 1 telemetry event."""

    telemetry_event_id: str
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
    stage: str | None = None
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
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "decision_mode": self.decision_mode,
            "confidence_score": self.confidence_score,
            "decision": self.decision,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_confidence_telemetry_event(
    payload: S1ConfidenceTelemetryInput,
) -> S1ConfidenceTelemetryEvent:
    """Build a validated CONF Sprint 1 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S1ConfidenceTelemetryEvent: Structured event ready for logging.

    Raises:
        S1ConfidenceTelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1ConfidenceTelemetryContractError(
            code="INVALID_CONF_S1_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria CONF S1 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S1ConfidenceTelemetryContractError(
            code="INVALID_CONF_S1_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria CONF S1 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S1ConfidenceTelemetryContractError(
            code="INVALID_CONF_S1_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria CONF S1 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1ConfidenceTelemetryContractError(
            code="INVALID_CONF_S1_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    confidence_score = payload.confidence_score
    if confidence_score is not None:
        if isinstance(confidence_score, bool) or not isinstance(confidence_score, (int, float)):
            raise S1ConfidenceTelemetryContractError(
                code="INVALID_CONF_S1_TELEMETRY_CONFIDENCE_SCORE",
                message="confidence_score deve ser numerico",
                action="Propague confidence_score numerico no intervalo de 0.0 a 1.0.",
            )
        confidence_score = float(confidence_score)
        if confidence_score < MIN_CONFIDENCE_SCORE or confidence_score > MAX_CONFIDENCE_SCORE:
            raise S1ConfidenceTelemetryContractError(
                code="INVALID_CONF_S1_TELEMETRY_CONFIDENCE_SCORE",
                message=f"confidence_score fora do intervalo permitido: {payload.confidence_score}",
                action="Use confidence_score no intervalo de 0.0 a 1.0.",
            )
        confidence_score = round(confidence_score, 6)

    decision = (payload.decision or "").strip().lower() or None
    if decision is not None and decision not in ALLOWED_DECISIONS:
        raise S1ConfidenceTelemetryContractError(
            code="INVALID_CONF_S1_TELEMETRY_DECISION",
            message=f"decision de telemetria invalida: {payload.decision}",
            action="Use decision valida: auto_approve, manual_review ou reject.",
        )

    return S1ConfidenceTelemetryEvent(
        telemetry_event_id=f"confs1evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S1,
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
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def emit_s1_confidence_telemetry_event(
    logger: logging.Logger,
    event: S1ConfidenceTelemetryEvent,
) -> None:
    """Emit one CONF Sprint 1 telemetry event to operational logger.

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


def build_s1_confidence_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONF Sprint 1 error detail with telemetry references.

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
