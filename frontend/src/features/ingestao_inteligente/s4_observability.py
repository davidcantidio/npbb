"""Observability contracts for Sprint 4 final UX and accessibility flow.

This module standardizes frontend-side operational events for Sprint 4 and
provides actionable diagnostics correlated with backend telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.ingestao_inteligente.s4")

COMPONENT_NAME = "frontend_ingestao_inteligente_s4"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_MESSAGE_SEVERITIES = {"info", "warning", "success", "error"}


class S4ObservabilityError(ValueError):
    """Raised when Sprint 4 observability contract is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4ObservabilityInput:
    """Input contract used to create one Sprint 4 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = "info"
    evento_id: int | None = None
    lote_id: str | None = None
    lote_upload_id: str | None = None
    status_processamento: str | None = None
    proxima_acao: str | None = None
    codigo_mensagem: str | None = None
    severidade_mensagem: str | None = None
    destino_acao_principal: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4ObservabilityEvent:
    """Output contract for one Sprint 4 frontend observability event."""

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
    proxima_acao: str | None = None
    codigo_mensagem: str | None = None
    severidade_mensagem: str | None = None
    destino_acao_principal: str | None = None
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
            "proxima_acao": self.proxima_acao,
            "codigo_mensagem": self.codigo_mensagem,
            "severidade_mensagem": self.severidade_mensagem,
            "destino_acao_principal": self.destino_acao_principal,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact event fields used in flow output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s4_observability_event(payload: S4ObservabilityInput) -> S4ObservabilityEvent:
    """Build validated observability event for Sprint 4 frontend flow.

    Args:
        payload: Input observability data from one stage of Sprint 4 flow.

    Returns:
        S4ObservabilityEvent: Structured event ready to be logged.

    Raises:
        S4ObservabilityError: If required observability fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4ObservabilityError(
            code="INVALID_S4_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S4ObservabilityError(
            code="INVALID_S4_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo da sprint.",
        )
    if not event_message:
        raise S4ObservabilityError(
            code="INVALID_S4_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4ObservabilityError(
            code="INVALID_S4_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    lote_id = (payload.lote_id or "").strip() or None
    lote_upload_id = (payload.lote_upload_id or "").strip().lower() or None
    status_processamento = (payload.status_processamento or "").strip().lower() or None
    proxima_acao = (payload.proxima_acao or "").strip() or None
    codigo_mensagem = (payload.codigo_mensagem or "").strip() or None
    severidade_mensagem = (payload.severidade_mensagem or "").strip().lower() or None
    destino_acao_principal = (payload.destino_acao_principal or "").strip() or None

    if severidade_mensagem and severidade_mensagem not in ALLOWED_MESSAGE_SEVERITIES:
        raise S4ObservabilityError(
            code="INVALID_S4_MESSAGE_SEVERITY",
            message=f"severidade_mensagem invalida: {payload.severidade_mensagem}",
            action="Use severidades de mensagem aceitas: info, warning, success ou error.",
        )

    return S4ObservabilityEvent(
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
        proxima_acao=proxima_acao,
        codigo_mensagem=codigo_mensagem,
        severidade_mensagem=severidade_mensagem,
        destino_acao_principal=destino_acao_principal,
        context=payload.context or {},
    )


def log_s4_observability_event(event: S4ObservabilityEvent) -> None:
    """Emit observability event to Sprint 4 frontend operational logger.

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


def build_s4_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build standardized actionable error dictionary for Sprint 4 flow.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error description.
        action: Suggested next action for operators/developers.
        correlation_id: Correlation identifier for cross-layer tracing.
        observability_event_id: Frontend observability event id for log lookup.
        context: Optional diagnostics context.

    Returns:
        dict[str, Any]: Error payload aligned with Sprint 4 diagnostics contract.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "observability_event_id": observability_event_id,
        "context": context or {},
    }
