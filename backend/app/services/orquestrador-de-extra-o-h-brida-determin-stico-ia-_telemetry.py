"""Telemetry helpers for ORQ Sprint 1, Sprint 2, Sprint 3, and Sprint 4 flows.

This service centralizes operational telemetry contracts used by the hybrid
extraction orchestrator. It keeps event payloads stable, emits structured
diagnostics, and builds actionable error details for service layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME = "orquestrador_extracao_hibrida_deterministico_ia_s1"
COMPONENT_NAME_S2 = "orquestrador_extracao_hibrida_deterministico_ia_s2"
COMPONENT_NAME_S3 = "orquestrador_extracao_hibrida_deterministico_ia_s3"
COMPONENT_NAME_S4 = "orquestrador_extracao_hibrida_deterministico_ia_s4"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_CIRCUIT_STATES = {"closed", "open", "half_open"}
ALLOWED_CUSTO_STATUS = {"within_budget", "above_budget"}
ALLOWED_LATENCIA_STATUS = {"within_sla", "above_sla"}


class S1OrchestratorTelemetryContractError(ValueError):
    """Raised when ORQ Sprint 1 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S2OrchestratorTelemetryContractError(ValueError):
    """Raised when ORQ Sprint 2 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S3OrchestratorTelemetryContractError(ValueError):
    """Raised when ORQ Sprint 3 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S4OrchestratorTelemetryContractError(ValueError):
    """Raised when ORQ Sprint 4 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1OrchestratorTelemetryInput:
    """Input contract for ORQ Sprint 1 telemetry event creation."""

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
class S2OrchestratorTelemetryInput:
    """Input contract for ORQ Sprint 2 telemetry event creation."""

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
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3OrchestratorTelemetryInput:
    """Input contract for ORQ Sprint 3 telemetry event creation."""

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
    circuit_state: str | None = None
    failure_threshold: int | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4OrchestratorTelemetryInput:
    """Input contract for ORQ Sprint 4 telemetry event creation."""

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
    decision_reason: str | None = None
    latency_ms: int | None = None
    cost_usd: float | None = None
    custo_status: str | None = None
    latencia_status: str | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1OrchestratorTelemetryEvent:
    """Output contract for one structured ORQ Sprint 1 telemetry event."""

    telemetry_event_id: str
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
        """Return safe dictionary for `logging.Logger.*(..., extra=...)`."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
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
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2OrchestratorTelemetryEvent:
    """Output contract for one structured ORQ Sprint 2 telemetry event."""

    telemetry_event_id: str
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "route_name": self.route_name,
            "attempt": self.attempt,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3OrchestratorTelemetryEvent:
    """Output contract for one structured ORQ Sprint 3 telemetry event."""

    telemetry_event_id: str
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
    circuit_state: str | None = None
    failure_threshold: int | None = None
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "route_name": self.route_name,
            "attempt": self.attempt,
            "circuit_state": self.circuit_state,
            "failure_threshold": self.failure_threshold,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4OrchestratorTelemetryEvent:
    """Output contract for one structured ORQ Sprint 4 telemetry event."""

    telemetry_event_id: str
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
    decision_reason: str | None = None
    latency_ms: int | None = None
    cost_usd: float | None = None
    custo_status: str | None = None
    latencia_status: str | None = None
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "route_name": self.route_name,
            "attempt": self.attempt,
            "decision_reason": self.decision_reason,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "custo_status": self.custo_status,
            "latencia_status": self.latencia_status,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_orchestrator_telemetry_event(
    payload: S1OrchestratorTelemetryInput,
) -> S1OrchestratorTelemetryEvent:
    """Build a validated ORQ Sprint 1 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S1OrchestratorTelemetryEvent: Structured event ready for logging.

    Raises:
        S1OrchestratorTelemetryContractError: If event name, correlation id,
            event message, or severity are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S1_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria do ORQ S1 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S1OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S1_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria do ORQ S1 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S1OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S1_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria do ORQ S1 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S1_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    source_id = (payload.source_id or "").strip() or None
    source_kind = (payload.source_kind or "").strip().lower() or None
    source_uri = (payload.source_uri or "").strip() or None
    rota_selecionada = (payload.rota_selecionada or "").strip() or None
    stage = (payload.stage or "").strip() or None
    return S1OrchestratorTelemetryEvent(
        telemetry_event_id=f"orqs1evt-{uuid4().hex[:12]}",
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


def emit_s1_orchestrator_telemetry_event(
    logger: logging.Logger,
    event: S1OrchestratorTelemetryEvent,
) -> None:
    """Emit one ORQ Sprint 1 telemetry event to operational logger.

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


def build_s1_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 1 error detail with telemetry references.

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


def build_s2_orchestrator_telemetry_event(
    payload: S2OrchestratorTelemetryInput,
) -> S2OrchestratorTelemetryEvent:
    """Build a validated ORQ Sprint 2 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S2OrchestratorTelemetryEvent: Structured event ready for logging.

    Raises:
        S2OrchestratorTelemetryContractError: If event name, correlation id,
            event message, severity, or attempt are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S2_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria do ORQ S2 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S2OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S2_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria do ORQ S2 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S2OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S2_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria do ORQ S2 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S2_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    attempt = payload.attempt
    if attempt is not None and attempt < 1:
        raise S2OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S2_TELEMETRY_ATTEMPT",
            message="attempt de telemetria do ORQ S2 deve ser >= 1",
            action="Propague contador de tentativa valido para retries do ORQ S2.",
        )

    source_id = (payload.source_id or "").strip() or None
    source_kind = (payload.source_kind or "").strip().lower() or None
    source_uri = (payload.source_uri or "").strip() or None
    rota_selecionada = (payload.rota_selecionada or "").strip() or None
    route_name = (payload.route_name or "").strip() or None
    stage = (payload.stage or "").strip() or None
    return S2OrchestratorTelemetryEvent(
        telemetry_event_id=f"orqs2evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S2,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=rota_selecionada,
        route_name=route_name,
        attempt=attempt,
        stage=stage,
        context=payload.context or {},
    )


def emit_s2_orchestrator_telemetry_event(
    logger: logging.Logger,
    event: S2OrchestratorTelemetryEvent,
) -> None:
    """Emit one ORQ Sprint 2 telemetry event to operational logger.

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


def build_s2_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 2 error detail with telemetry references.

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


def build_s3_orchestrator_telemetry_event(
    payload: S3OrchestratorTelemetryInput,
) -> S3OrchestratorTelemetryEvent:
    """Build a validated ORQ Sprint 3 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S3OrchestratorTelemetryEvent: Structured event ready for logging.

    Raises:
        S3OrchestratorTelemetryContractError: If event name, correlation id,
            event message, severity, attempt, failure threshold, or
            circuit state are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria do ORQ S3 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria do ORQ S3 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria do ORQ S3 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    attempt = payload.attempt
    if attempt is not None and attempt < 1:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_ATTEMPT",
            message="attempt de telemetria do ORQ S3 deve ser >= 1",
            action="Propague contador de tentativa valido para retries do ORQ S3.",
        )

    failure_threshold = payload.failure_threshold
    if failure_threshold is not None and failure_threshold < 1:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_FAILURE_THRESHOLD",
            message="failure_threshold de telemetria do ORQ S3 deve ser >= 1",
            action="Propague threshold valido para diagnostico do circuit breaker.",
        )

    circuit_state = (payload.circuit_state or "").strip().lower() or None
    if circuit_state and circuit_state not in ALLOWED_CIRCUIT_STATES:
        raise S3OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S3_TELEMETRY_CIRCUIT_STATE",
            message=f"circuit_state de telemetria invalido: {payload.circuit_state}",
            action="Use circuit_state valido: closed, open ou half_open.",
        )

    source_id = (payload.source_id or "").strip() or None
    source_kind = (payload.source_kind or "").strip().lower() or None
    source_uri = (payload.source_uri or "").strip() or None
    rota_selecionada = (payload.rota_selecionada or "").strip() or None
    route_name = (payload.route_name or "").strip() or None
    stage = (payload.stage or "").strip() or None

    return S3OrchestratorTelemetryEvent(
        telemetry_event_id=f"orqs3evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S3,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=rota_selecionada,
        route_name=route_name,
        attempt=attempt,
        circuit_state=circuit_state,
        failure_threshold=failure_threshold,
        stage=stage,
        context=payload.context or {},
    )


def emit_s3_orchestrator_telemetry_event(
    logger: logging.Logger,
    event: S3OrchestratorTelemetryEvent,
) -> None:
    """Emit one ORQ Sprint 3 telemetry event to operational logger.

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


def build_s3_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 3 error detail with telemetry references.

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


def build_s4_orchestrator_telemetry_event(
    payload: S4OrchestratorTelemetryInput,
) -> S4OrchestratorTelemetryEvent:
    """Build a validated ORQ Sprint 4 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S4OrchestratorTelemetryEvent: Structured event ready for logging.

    Raises:
        S4OrchestratorTelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria do ORQ S4 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria do ORQ S4 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria do ORQ S4 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    attempt = payload.attempt
    if attempt is not None and attempt < 1:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_ATTEMPT",
            message="attempt de telemetria do ORQ S4 deve ser >= 1",
            action="Propague contador de tentativa valido para execucao do ORQ S4.",
        )

    latency_ms = payload.latency_ms
    if latency_ms is not None and latency_ms < 0:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_LATENCY_MS",
            message="latency_ms de telemetria do ORQ S4 deve ser >= 0",
            action="Propague latencia valida em milissegundos.",
        )

    cost_usd = payload.cost_usd
    if cost_usd is not None and cost_usd < 0:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_COST_USD",
            message="cost_usd de telemetria do ORQ S4 deve ser >= 0",
            action="Propague custo valido em USD.",
        )

    custo_status = (payload.custo_status or "").strip().lower() or None
    if custo_status and custo_status not in ALLOWED_CUSTO_STATUS:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_CUSTO_STATUS",
            message=f"custo_status de telemetria invalido: {payload.custo_status}",
            action="Use custo_status valido: within_budget ou above_budget.",
        )

    latencia_status = (payload.latencia_status or "").strip().lower() or None
    if latencia_status and latencia_status not in ALLOWED_LATENCIA_STATUS:
        raise S4OrchestratorTelemetryContractError(
            code="INVALID_ORQ_S4_TELEMETRY_LATENCIA_STATUS",
            message=f"latencia_status de telemetria invalido: {payload.latencia_status}",
            action="Use latencia_status valido: within_sla ou above_sla.",
        )

    return S4OrchestratorTelemetryEvent(
        telemetry_event_id=f"orqs4evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S4,
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
        decision_reason=(payload.decision_reason or "").strip() or None,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        custo_status=custo_status,
        latencia_status=latencia_status,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def emit_s4_orchestrator_telemetry_event(
    logger: logging.Logger,
    event: S4OrchestratorTelemetryEvent,
) -> None:
    """Emit one ORQ Sprint 4 telemetry event to operational logger.

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


def build_s4_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 4 error detail with telemetry references.

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
