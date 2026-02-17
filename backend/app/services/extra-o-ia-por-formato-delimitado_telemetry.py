"""Telemetry helpers for XIA Sprint 1, Sprint 2, and Sprint 3 extraction flows.

This service centralizes operational telemetry contracts used by extraction AI
by delimited format. It keeps event payloads stable and builds actionable
error details for service layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME_S1 = "extracao_ia_por_formato_delimitado_s1"
COMPONENT_NAME_S2 = "extracao_ia_por_formato_delimitado_s2"
COMPONENT_NAME_S3 = "extracao_ia_por_formato_delimitado_s3"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S1ExtractAITelemetryContractError(ValueError):
    """Raised when XIA Sprint 1 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S2ExtractAITelemetryContractError(ValueError):
    """Raised when XIA Sprint 2 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S3ExtractAITelemetryContractError(ValueError):
    """Raised when XIA Sprint 3 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1ExtractAITelemetryInput:
    """Input contract for XIA Sprint 1 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    source_id: str | None = None
    source_kind: str | None = None
    source_uri: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S2ExtractAITelemetryInput:
    """Input contract for XIA Sprint 2 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    source_id: str | None = None
    source_kind: str | None = None
    source_uri: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    tabular_layout_hint: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3ExtractAITelemetryInput:
    """Input contract for XIA Sprint 3 telemetry event creation."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    source_id: str | None = None
    source_kind: str | None = None
    source_uri: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    image_preprocess_hint: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S1ExtractAITelemetryEvent:
    """Output contract for one structured XIA Sprint 1 telemetry event."""

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
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
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
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "chunk_strategy": self.chunk_strategy,
            "chunk_count": self.chunk_count,
            "decision_reason": self.decision_reason,
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
class S2ExtractAITelemetryEvent:
    """Output contract for one structured XIA Sprint 2 telemetry event."""

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
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    tabular_layout_hint: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
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
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "chunk_strategy": self.chunk_strategy,
            "tabular_layout_hint": self.tabular_layout_hint,
            "chunk_count": self.chunk_count,
            "decision_reason": self.decision_reason,
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
class S3ExtractAITelemetryEvent:
    """Output contract for one structured XIA Sprint 3 telemetry event."""

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
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    image_preprocess_hint: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
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
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "chunk_strategy": self.chunk_strategy,
            "image_preprocess_hint": self.image_preprocess_hint,
            "chunk_count": self.chunk_count,
            "decision_reason": self.decision_reason,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_extract_ai_telemetry_event(
    payload: S1ExtractAITelemetryInput,
) -> S1ExtractAITelemetryEvent:
    """Build a validated XIA Sprint 1 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S1ExtractAITelemetryEvent: Structured event ready for logging.

    Raises:
        S1ExtractAITelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1ExtractAITelemetryContractError(
            code="INVALID_XIA_S1_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria XIA S1 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S1ExtractAITelemetryContractError(
            code="INVALID_XIA_S1_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria XIA S1 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S1ExtractAITelemetryContractError(
            code="INVALID_XIA_S1_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria XIA S1 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1ExtractAITelemetryContractError(
            code="INVALID_XIA_S1_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    if payload.chunk_count is not None and payload.chunk_count < 1:
        raise S1ExtractAITelemetryContractError(
            code="INVALID_XIA_S1_TELEMETRY_CHUNK_COUNT",
            message="chunk_count de telemetria XIA S1 deve ser >= 1",
            action="Propague chunk_count valido para diagnostico operacional.",
        )

    return S1ExtractAITelemetryEvent(
        telemetry_event_id=f"xias1evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S1,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=(payload.source_id or "").strip() or None,
        source_kind=(payload.source_kind or "").strip().lower() or None,
        source_uri=(payload.source_uri or "").strip() or None,
        model_provider=(payload.model_provider or "").strip().lower() or None,
        model_name=(payload.model_name or "").strip() or None,
        chunk_strategy=(payload.chunk_strategy or "").strip().lower() or None,
        chunk_count=payload.chunk_count,
        decision_reason=(payload.decision_reason or "").strip() or None,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def build_s2_extract_ai_telemetry_event(
    payload: S2ExtractAITelemetryInput,
) -> S2ExtractAITelemetryEvent:
    """Build a validated XIA Sprint 2 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S2ExtractAITelemetryEvent: Structured event ready for logging.

    Raises:
        S2ExtractAITelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2ExtractAITelemetryContractError(
            code="INVALID_XIA_S2_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria XIA S2 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S2ExtractAITelemetryContractError(
            code="INVALID_XIA_S2_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria XIA S2 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S2ExtractAITelemetryContractError(
            code="INVALID_XIA_S2_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria XIA S2 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2ExtractAITelemetryContractError(
            code="INVALID_XIA_S2_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    if payload.chunk_count is not None and payload.chunk_count < 1:
        raise S2ExtractAITelemetryContractError(
            code="INVALID_XIA_S2_TELEMETRY_CHUNK_COUNT",
            message="chunk_count de telemetria XIA S2 deve ser >= 1",
            action="Propague chunk_count valido para diagnostico operacional.",
        )

    return S2ExtractAITelemetryEvent(
        telemetry_event_id=f"xias2evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S2,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=(payload.source_id or "").strip() or None,
        source_kind=(payload.source_kind or "").strip().lower() or None,
        source_uri=(payload.source_uri or "").strip() or None,
        model_provider=(payload.model_provider or "").strip().lower() or None,
        model_name=(payload.model_name or "").strip() or None,
        chunk_strategy=(payload.chunk_strategy or "").strip().lower() or None,
        tabular_layout_hint=(payload.tabular_layout_hint or "").strip().lower() or None,
        chunk_count=payload.chunk_count,
        decision_reason=(payload.decision_reason or "").strip() or None,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def build_s3_extract_ai_telemetry_event(
    payload: S3ExtractAITelemetryInput,
) -> S3ExtractAITelemetryEvent:
    """Build a validated XIA Sprint 3 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S3ExtractAITelemetryEvent: Structured event ready for logging.

    Raises:
        S3ExtractAITelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3ExtractAITelemetryContractError(
            code="INVALID_XIA_S3_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria XIA S3 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S3ExtractAITelemetryContractError(
            code="INVALID_XIA_S3_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria XIA S3 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S3ExtractAITelemetryContractError(
            code="INVALID_XIA_S3_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria XIA S3 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3ExtractAITelemetryContractError(
            code="INVALID_XIA_S3_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    if payload.chunk_count is not None and payload.chunk_count < 1:
        raise S3ExtractAITelemetryContractError(
            code="INVALID_XIA_S3_TELEMETRY_CHUNK_COUNT",
            message="chunk_count de telemetria XIA S3 deve ser >= 1",
            action="Propague chunk_count valido para diagnostico operacional.",
        )

    return S3ExtractAITelemetryEvent(
        telemetry_event_id=f"xias3evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S3,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=(payload.source_id or "").strip() or None,
        source_kind=(payload.source_kind or "").strip().lower() or None,
        source_uri=(payload.source_uri or "").strip() or None,
        model_provider=(payload.model_provider or "").strip().lower() or None,
        model_name=(payload.model_name or "").strip() or None,
        chunk_strategy=(payload.chunk_strategy or "").strip().lower() or None,
        image_preprocess_hint=(payload.image_preprocess_hint or "").strip().lower() or None,
        chunk_count=payload.chunk_count,
        decision_reason=(payload.decision_reason or "").strip() or None,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def emit_s1_extract_ai_telemetry_event(
    logger: logging.Logger,
    event: S1ExtractAITelemetryEvent,
) -> None:
    """Emit one XIA Sprint 1 telemetry event to operational logger.

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


def emit_s2_extract_ai_telemetry_event(
    logger: logging.Logger,
    event: S2ExtractAITelemetryEvent,
) -> None:
    """Emit one XIA Sprint 2 telemetry event to operational logger.

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


def emit_s3_extract_ai_telemetry_event(
    logger: logging.Logger,
    event: S3ExtractAITelemetryEvent,
) -> None:
    """Emit one XIA Sprint 3 telemetry event to operational logger.

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


def build_s1_extract_ai_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable XIA Sprint 1 error detail with telemetry references.

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


def build_s2_extract_ai_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable XIA Sprint 2 error detail with telemetry references.

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


def build_s3_extract_ai_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable XIA Sprint 3 error detail with telemetry references.

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
