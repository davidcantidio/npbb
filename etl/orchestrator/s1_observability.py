"""Observability contracts for ORQ Sprint 1 routing flow.

This module standardizes operational events for the orchestrator core flow and
provides actionable diagnostics that can be correlated with backend telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s1.core")

COMPONENT_NAME = "etl_orchestrator_s1_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S1OrchestratorObservabilityError(ValueError):
    """Raised when ORQ Sprint 1 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1OrchestratorObservabilityInput:
    """Input contract used to create one ORQ Sprint 1 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    source_id: str | None = None
    source_kind: str | None = None
    source_uri: str | None = None
    rota_selecionada: str | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1OrchestratorObservabilityEvent:
    """Output contract for one ORQ Sprint 1 observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    source_id: str | None = None
    source_kind: str | None = None
    source_uri: str | None = None
    rota_selecionada: str | None = None
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_orchestrator_observability_event(
    payload: S1OrchestratorObservabilityInput,
) -> S1OrchestratorObservabilityEvent:
    """Build validated ORQ Sprint 1 observability event.

    Args:
        payload: Input observability contract with event details and context.

    Returns:
        S1OrchestratorObservabilityEvent: Structured event ready for logging.

    Raises:
        S1OrchestratorObservabilityError: If event name, correlation id,
            event message, or severity are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1OrchestratorObservabilityError(
            code="INVALID_ORQ_S1_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade do ORQ S1 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S1OrchestratorObservabilityError(
            code="INVALID_ORQ_S1_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade do ORQ S1 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo do orquestrador.",
        )
    if not event_message:
        raise S1OrchestratorObservabilityError(
            code="INVALID_ORQ_S1_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade do ORQ S1 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1OrchestratorObservabilityError(
            code="INVALID_ORQ_S1_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    source_id = (payload.source_id or "").strip() or None
    source_kind = (payload.source_kind or "").strip().lower() or None
    source_uri = (payload.source_uri or "").strip() or None
    rota_selecionada = (payload.rota_selecionada or "").strip() or None
    stage = (payload.stage or "").strip() or None
    return S1OrchestratorObservabilityEvent(
        observability_event_id=f"orqs1coreevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=rota_selecionada,
        stage=stage,
        context=payload.context or {},
    )


def log_s1_orchestrator_observability_event(event: S1OrchestratorObservabilityEvent) -> None:
    """Emit one ORQ Sprint 1 observability event to the operational logger.

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


def build_s1_orchestrator_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 1 error payload for diagnostics.

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
