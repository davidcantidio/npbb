"""Observability contracts for Sprint 1 upload and event-selection flow.

This module standardizes frontend-side operational events and provides
actionable diagnostics that can be correlated with backend telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.ingestao_inteligente.s1")

COMPONENT_NAME = "frontend_ingestao_inteligente_s1"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S1ObservabilityError(ValueError):
    """Raised when Sprint 1 observability contract is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""
        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1ObservabilityInput:
    """Input contract used to create one Sprint 1 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = "info"
    evento_id: int | None = None
    upload_id: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1ObservabilityEvent:
    """Output contract for one Sprint 1 frontend observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    evento_id: int | None = None
    upload_id: str | None = None
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
            "evento_id": self.evento_id,
            "upload_id": self.upload_id,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact event fields used in flow output contracts."""
        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_observability_event(payload: S1ObservabilityInput) -> S1ObservabilityEvent:
    """Build validated observability event for Sprint 1 frontend flow.

    Args:
        payload: Input telemetry data from one stage of the Sprint 1 flow.

    Returns:
        S1ObservabilityEvent: Structured event ready to be logged.

    Raises:
        S1ObservabilityError: If required telemetry fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1ObservabilityError(
            code="INVALID_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S1ObservabilityError(
            code="INVALID_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo da sprint.",
        )
    if not event_message:
        raise S1ObservabilityError(
            code="INVALID_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1ObservabilityError(
            code="INVALID_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    return S1ObservabilityEvent(
        observability_event_id=f"obs-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=payload.evento_id,
        upload_id=payload.upload_id,
        context=payload.context or {},
    )


def log_s1_observability_event(event: S1ObservabilityEvent) -> None:
    """Emit observability event to Sprint 1 frontend operational logger.

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


def build_s1_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
) -> dict[str, str]:
    """Build standardized actionable error dictionary for Sprint 1 flow.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error description.
        action: Suggested next action for operators/developers.
        correlation_id: Correlation identifier for cross-layer tracing.
        observability_event_id: Frontend observability event id for log lookup.

    Returns:
        dict[str, str]: Error payload aligned with Sprint 1 diagnostics contract.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "observability_event_id": observability_event_id,
    }
