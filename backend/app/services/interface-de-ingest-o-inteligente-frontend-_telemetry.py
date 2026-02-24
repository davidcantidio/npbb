"""Telemetry helpers for Sprint 1, Sprint 2, Sprint 3 and Sprint 4 flows.

This service centralizes operational telemetry contracts used by interface
journeys. It keeps event payloads stable, logs structured diagnostics, and
builds actionable error details for API responses.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME = "interface_de_ingestao_inteligente_frontend"
COMPONENT_NAME_S2 = "interface_de_ingestao_inteligente_frontend_s2"
COMPONENT_NAME_S3 = "interface_de_ingestao_inteligente_frontend_s3"
COMPONENT_NAME_S4 = "interface_de_ingestao_inteligente_frontend_s4"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S1TelemetryContractError(ValueError):
    """Raised when telemetry contract input is invalid for Sprint 1."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


class S2TelemetryContractError(ValueError):
    """Raised when telemetry contract input is invalid for Sprint 2."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


class S3TelemetryContractError(ValueError):
    """Raised when telemetry contract input is invalid for Sprint 3."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


class S4TelemetryContractError(ValueError):
    """Raised when telemetry contract input is invalid for Sprint 4."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


@dataclass(frozen=True, slots=True)
class S1TelemetryInput:
    """Input contract for Sprint 1 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    evento_id: int | None = None
    upload_id: str | None = None
    severity: str = DEFAULT_SEVERITY
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S2TelemetryInput:
    """Input contract for Sprint 2 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    severity: str = DEFAULT_SEVERITY
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3TelemetryInput:
    """Input contract for Sprint 3 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    reprocessamento_id: str | None = None
    severity: str = DEFAULT_SEVERITY
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4TelemetryInput:
    """Input contract for Sprint 4 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    codigo_mensagem: str | None = None
    destino_acao_principal: str | None = None
    severity: str = DEFAULT_SEVERITY
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1TelemetryEvent:
    """Output contract for one structured Sprint 1 telemetry event."""

    telemetry_event_id: str
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
        """Return safe dictionary for `logging.Logger.*(..., extra=...)`."""
        return {
            "telemetry_event_id": self.telemetry_event_id,
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
        """Return compact telemetry context for API responses."""
        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2TelemetryEvent:
    """Output contract for one structured Sprint 2 telemetry event."""

    telemetry_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
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
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for API responses."""
        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3TelemetryEvent:
    """Output contract for one structured Sprint 3 telemetry event."""

    telemetry_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    reprocessamento_id: str | None = None
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
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "reprocessamento_id": self.reprocessamento_id,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for API responses."""
        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4TelemetryEvent:
    """Output contract for one structured Sprint 4 telemetry event."""

    telemetry_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    codigo_mensagem: str | None = None
    destino_acao_principal: str | None = None
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
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "codigo_mensagem": self.codigo_mensagem,
            "destino_acao_principal": self.destino_acao_principal,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for API responses."""
        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_telemetry_event(payload: S1TelemetryInput) -> S1TelemetryEvent:
    """Build a validated Sprint 1 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S1TelemetryEvent: Structured event ready for logging and response usage.

    Raises:
        S1TelemetryContractError: If event name, correlation id, message, or
            severity are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1TelemetryContractError(
            code="INVALID_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S1TelemetryContractError(
            code="INVALID_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria nao pode ser vazio",
            action="Propague correlation_id no fluxo da sprint antes de logar eventos.",
        )
    if not event_message:
        raise S1TelemetryContractError(
            code="INVALID_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1TelemetryContractError(
            code="INVALID_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    return S1TelemetryEvent(
        telemetry_event_id=f"tel-{uuid4().hex[:12]}",
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


def build_s2_telemetry_event(payload: S2TelemetryInput) -> S2TelemetryEvent:
    """Build a validated Sprint 2 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S2TelemetryEvent: Structured event ready for logging and response usage.

    Raises:
        S2TelemetryContractError: If event name, correlation id, message, or
            severity are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2TelemetryContractError(
            code="INVALID_S2_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S2TelemetryContractError(
            code="INVALID_S2_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria nao pode ser vazio",
            action="Propague correlation_id no fluxo da sprint antes de logar eventos.",
        )
    if not event_message:
        raise S2TelemetryContractError(
            code="INVALID_S2_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2TelemetryContractError(
            code="INVALID_S2_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    lote_id = (payload.lote_id or "").strip() or None
    lote_upload_id = (payload.lote_upload_id or "").strip() or None
    return S2TelemetryEvent(
        telemetry_event_id=f"tel-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S2,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=payload.evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        context=payload.context or {},
    )


def build_s3_telemetry_event(payload: S3TelemetryInput) -> S3TelemetryEvent:
    """Build a validated Sprint 3 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S3TelemetryEvent: Structured event ready for logging and response usage.

    Raises:
        S3TelemetryContractError: If event name, correlation id, message, or
            severity are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3TelemetryContractError(
            code="INVALID_S3_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S3TelemetryContractError(
            code="INVALID_S3_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria nao pode ser vazio",
            action="Propague correlation_id no fluxo da sprint antes de logar eventos.",
        )
    if not event_message:
        raise S3TelemetryContractError(
            code="INVALID_S3_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3TelemetryContractError(
            code="INVALID_S3_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    lote_id = (payload.lote_id or "").strip() or None
    lote_upload_id = (payload.lote_upload_id or "").strip().lower() or None
    reprocessamento_id = (payload.reprocessamento_id or "").strip() or None
    return S3TelemetryEvent(
        telemetry_event_id=f"tel-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S3,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=payload.evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        reprocessamento_id=reprocessamento_id,
        context=payload.context or {},
    )


def build_s4_telemetry_event(payload: S4TelemetryInput) -> S4TelemetryEvent:
    """Build a validated Sprint 4 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S4TelemetryEvent: Structured event ready for logging and response usage.

    Raises:
        S4TelemetryContractError: If event name, correlation id, message, or
            severity are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4TelemetryContractError(
            code="INVALID_S4_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S4TelemetryContractError(
            code="INVALID_S4_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria nao pode ser vazio",
            action="Propague correlation_id no fluxo da sprint antes de logar eventos.",
        )
    if not event_message:
        raise S4TelemetryContractError(
            code="INVALID_S4_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4TelemetryContractError(
            code="INVALID_S4_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    lote_id = (payload.lote_id or "").strip() or None
    lote_upload_id = (payload.lote_upload_id or "").strip().lower() or None
    codigo_mensagem = (payload.codigo_mensagem or "").strip() or None
    destino_acao_principal = (payload.destino_acao_principal or "").strip() or None
    return S4TelemetryEvent(
        telemetry_event_id=f"tel-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S4,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=payload.evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        codigo_mensagem=codigo_mensagem,
        destino_acao_principal=destino_acao_principal,
        context=payload.context or {},
    )


def emit_s1_telemetry_event(logger: logging.Logger, event: S1TelemetryEvent) -> None:
    """Emit one Sprint 1 telemetry event to operational logger.

    Args:
        logger: Logger instance used by API/router layer.
        event: Structured telemetry event to be logged.
    """

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def emit_s2_telemetry_event(logger: logging.Logger, event: S2TelemetryEvent) -> None:
    """Emit one Sprint 2 telemetry event to operational logger.

    Args:
        logger: Logger instance used by API/router layer.
        event: Structured telemetry event to be logged.
    """

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def emit_s3_telemetry_event(logger: logging.Logger, event: S3TelemetryEvent) -> None:
    """Emit one Sprint 3 telemetry event to operational logger.

    Args:
        logger: Logger instance used by API/router layer.
        event: Structured telemetry event to be logged.
    """

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def emit_s4_telemetry_event(logger: logging.Logger, event: S4TelemetryEvent) -> None:
    """Emit one Sprint 4 telemetry event to operational logger.

    Args:
        logger: Logger instance used by API/router layer.
        event: Structured telemetry event to be logged.
    """

    if event.severity == "error":
        logger.error(event.event_name, extra=event.to_log_extra())
        return
    if event.severity == "warning":
        logger.warning(event.event_name, extra=event.to_log_extra())
        return
    logger.info(event.event_name, extra=event.to_log_extra())


def build_s1_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable error payload enriched with telemetry references.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action to fix or diagnose the error.
        correlation_id: Correlation identifier for cross-service tracing.
        telemetry_event_id: Telemetry event identifier for log lookup.
        context: Optional contextual fields attached to error diagnostics.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "telemetry_event_id": telemetry_event_id,
        "context": context or {},
    }


def build_s2_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    lote_id: str | None = None,
    lote_upload_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable Sprint 2 error payload with telemetry references.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action to fix or diagnose the error.
        correlation_id: Correlation identifier for cross-service tracing.
        telemetry_event_id: Telemetry event identifier for log lookup.
        lote_id: Optional lot identifier associated with the failure.
        lote_upload_id: Optional lot upload id associated with the failure.
        context: Optional contextual fields attached to error diagnostics.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    diagnostics = dict(context or {})
    if lote_id:
        diagnostics["lote_id"] = lote_id
    if lote_upload_id:
        diagnostics["lote_upload_id"] = lote_upload_id
    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "telemetry_event_id": telemetry_event_id,
        "context": diagnostics,
    }


def build_s3_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    lote_id: str | None = None,
    lote_upload_id: str | None = None,
    reprocessamento_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable Sprint 3 error payload with telemetry references.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action to fix or diagnose the error.
        correlation_id: Correlation identifier for cross-service tracing.
        telemetry_event_id: Telemetry event identifier for log lookup.
        lote_id: Optional lot identifier associated with the failure.
        lote_upload_id: Optional lot upload id associated with the failure.
        reprocessamento_id: Optional reprocessing id associated with the failure.
        context: Optional contextual fields attached to error diagnostics.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    diagnostics = dict(context or {})
    if lote_id:
        diagnostics["lote_id"] = lote_id
    if lote_upload_id:
        diagnostics["lote_upload_id"] = lote_upload_id
    if reprocessamento_id:
        diagnostics["reprocessamento_id"] = reprocessamento_id
    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "telemetry_event_id": telemetry_event_id,
        "context": diagnostics,
    }


def build_s4_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    lote_id: str | None = None,
    lote_upload_id: str | None = None,
    codigo_mensagem: str | None = None,
    destino_acao_principal: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable Sprint 4 error payload with telemetry references.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action to fix or diagnose the error.
        correlation_id: Correlation identifier for cross-service tracing.
        telemetry_event_id: Telemetry event identifier for log lookup.
        lote_id: Optional lot identifier associated with the failure.
        lote_upload_id: Optional lot upload id associated with the failure.
        codigo_mensagem: Optional UX message code associated with the failure.
        destino_acao_principal: Optional UX destination associated with the failure.
        context: Optional contextual fields attached to error diagnostics.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    diagnostics = dict(context or {})
    if lote_id:
        diagnostics["lote_id"] = lote_id
    if lote_upload_id:
        diagnostics["lote_upload_id"] = lote_upload_id
    if codigo_mensagem:
        diagnostics["codigo_mensagem"] = codigo_mensagem
    if destino_acao_principal:
        diagnostics["destino_acao_principal"] = destino_acao_principal
    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "telemetry_event_id": telemetry_event_id,
        "context": diagnostics,
    }
