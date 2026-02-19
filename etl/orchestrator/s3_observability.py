"""Observability contracts for ORQ Sprint 3 agent-first flow.

This module standardizes operational events for Sprint 3 route decisions,
fallback behavior, and circuit breaker transitions with actionable diagnostics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s3.core")

COMPONENT_NAME = "etl_orchestrator_s3_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_CIRCUIT_STATES = {"closed", "open", "half_open"}


class S3OrchestratorObservabilityError(ValueError):
    """Raised when ORQ Sprint 3 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3OrchestratorObservabilityInput:
    """Input contract used to create one ORQ Sprint 3 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    source_id: str | None = None
    source_kind: str | None = None
    source_uri: str | None = None
    rota_selecionada: str | None = None
    route_name: str | None = None
    attempt: int | None = None
    route_position: int | None = None
    total_routes: int | None = None
    circuit_state: str | None = None
    consecutive_failures: int | None = None
    failure_threshold: int | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3OrchestratorObservabilityEvent:
    """Output contract for one ORQ Sprint 3 observability event."""

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
    route_name: str | None = None
    attempt: int | None = None
    route_position: int | None = None
    total_routes: int | None = None
    circuit_state: str | None = None
    consecutive_failures: int | None = None
    failure_threshold: int | None = None
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
            "route_name": self.route_name,
            "attempt": self.attempt,
            "route_position": self.route_position,
            "total_routes": self.total_routes,
            "circuit_state": self.circuit_state,
            "consecutive_failures": self.consecutive_failures,
            "failure_threshold": self.failure_threshold,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s3_orchestrator_observability_event(
    payload: S3OrchestratorObservabilityInput,
) -> S3OrchestratorObservabilityEvent:
    """Build validated ORQ Sprint 3 observability event."""

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade do ORQ S3 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade do ORQ S3 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo do orquestrador.",
        )
    if not event_message:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade do ORQ S3 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    attempt = payload.attempt
    if attempt is not None and attempt < 1:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_ATTEMPT",
            message="attempt de observabilidade do ORQ S3 deve ser >= 1",
            action="Informe attempt valido para rastreabilidade de execucao.",
        )

    route_position = payload.route_position
    if route_position is not None and route_position < 1:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_ROUTE_POSITION",
            message="route_position deve ser >= 1 quando informado",
            action="Informe route_position valido para rastreabilidade da cadeia.",
        )

    total_routes = payload.total_routes
    if total_routes is not None and total_routes < 1:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_TOTAL_ROUTES",
            message="total_routes deve ser >= 1 quando informado",
            action="Informe total_routes valido para rastreabilidade da cadeia.",
        )

    consecutive_failures = payload.consecutive_failures
    if consecutive_failures is not None and consecutive_failures < 0:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_CONSECUTIVE_FAILURES",
            message="consecutive_failures deve ser >= 0 quando informado",
            action="Informe consecutive_failures valido para circuit breaker.",
        )

    failure_threshold = payload.failure_threshold
    if failure_threshold is not None and failure_threshold < 1:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_FAILURE_THRESHOLD",
            message="failure_threshold deve ser >= 1 quando informado",
            action="Informe failure_threshold valido para circuit breaker.",
        )

    circuit_state = (payload.circuit_state or "").strip().lower() or None
    if circuit_state and circuit_state not in ALLOWED_CIRCUIT_STATES:
        raise S3OrchestratorObservabilityError(
            code="INVALID_ORQ_S3_OBSERVABILITY_CIRCUIT_STATE",
            message=f"circuit_state invalido: {payload.circuit_state}",
            action="Use circuit_state valido: closed, open ou half_open.",
        )

    return S3OrchestratorObservabilityEvent(
        observability_event_id=f"orqs3coreevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=(payload.source_id or "").strip() or None,
        source_kind=(payload.source_kind or "").strip().lower() or None,
        source_uri=(payload.source_uri or "").strip() or None,
        rota_selecionada=(payload.rota_selecionada or "").strip() or None,
        route_name=(payload.route_name or "").strip() or None,
        attempt=attempt,
        route_position=route_position,
        total_routes=total_routes,
        circuit_state=circuit_state,
        consecutive_failures=consecutive_failures,
        failure_threshold=failure_threshold,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def log_s3_orchestrator_observability_event(event: S3OrchestratorObservabilityEvent) -> None:
    """Emit one ORQ Sprint 3 observability event to operational logger."""

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def build_s3_orchestrator_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 3 error payload for diagnostics."""

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "observability_event_id": observability_event_id,
        "stage": stage,
        "context": context or {},
    }
