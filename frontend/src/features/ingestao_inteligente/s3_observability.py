"""Observability contracts for Sprint 3 monitoring and reprocessing flow.

This module standardizes frontend-side operational events for Sprint 3 and
provides actionable diagnostics correlated with backend telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.ingestao_inteligente.s3")

COMPONENT_NAME = "frontend_ingestao_inteligente_s3"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S3ObservabilityError(ValueError):
    """Raised when Sprint 3 observability contract is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3ObservabilityInput:
    """Input contract used to create one Sprint 3 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = "info"
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    status_processamento: str | None = None
    tentativas_reprocessamento: int | None = None
    reprocessamento_id: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3ObservabilityEvent:
    """Output contract for one Sprint 3 frontend observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    status_processamento: str | None = None
    tentativas_reprocessamento: int | None = None
    reprocessamento_id: str | None = None
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
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "status_processamento": self.status_processamento,
            "tentativas_reprocessamento": self.tentativas_reprocessamento,
            "reprocessamento_id": self.reprocessamento_id,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact event fields used in flow output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s3_observability_event(payload: S3ObservabilityInput) -> S3ObservabilityEvent:
    """Build validated observability event for Sprint 3 frontend flow.

    Args:
        payload: Input observability data from one stage of Sprint 3 flow.

    Returns:
        S3ObservabilityEvent: Structured event ready to be logged.

    Raises:
        S3ObservabilityError: If required observability fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3ObservabilityError(
            code="INVALID_S3_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S3ObservabilityError(
            code="INVALID_S3_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo da sprint.",
        )
    if not event_message:
        raise S3ObservabilityError(
            code="INVALID_S3_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3ObservabilityError(
            code="INVALID_S3_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    lote_id = (payload.lote_id or "").strip() or None
    lote_upload_id = (payload.lote_upload_id or "").strip().lower() or None
    status_processamento = (payload.status_processamento or "").strip().lower() or None
    reprocessamento_id = (payload.reprocessamento_id or "").strip() or None
    tentativas_reprocessamento = payload.tentativas_reprocessamento
    if tentativas_reprocessamento is not None and tentativas_reprocessamento < 0:
        raise S3ObservabilityError(
            code="INVALID_S3_OBSERVABILITY_REPROCESS_ATTEMPTS",
            message="tentativas_reprocessamento nao pode ser negativo",
            action="Use contador de tentativas maior ou igual a zero.",
        )

    return S3ObservabilityEvent(
        observability_event_id=f"obs-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=payload.evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        status_processamento=status_processamento,
        tentativas_reprocessamento=tentativas_reprocessamento,
        reprocessamento_id=reprocessamento_id,
        context=payload.context or {},
    )


def log_s3_observability_event(event: S3ObservabilityEvent) -> None:
    """Emit observability event to Sprint 3 frontend operational logger.

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


def build_s3_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build standardized actionable error dictionary for Sprint 3 flow.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error description.
        action: Suggested next action for operators/developers.
        correlation_id: Correlation identifier for cross-layer tracing.
        observability_event_id: Frontend observability event id for log lookup.
        context: Optional diagnostics context.

    Returns:
        dict[str, Any]: Error payload aligned with Sprint 3 diagnostics contract.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "observability_event_id": observability_event_id,
        "context": context or {},
    }
