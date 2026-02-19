"""Observability contracts for ORQ Sprint 4 telemetry-first flow.

This module standardizes operational events for Sprint 4 decision telemetry,
cost governance, and latency tracking with actionable diagnostics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s4.core")

COMPONENT_NAME = "etl_orchestrator_s4_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_CUSTO_STATUS = {"within_budget", "above_budget"}
ALLOWED_LATENCIA_STATUS = {"within_sla", "above_sla"}


class S4OrchestratorObservabilityError(ValueError):
    """Raised when ORQ Sprint 4 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4OrchestratorObservabilityInput:
    """Input contract used to create one ORQ Sprint 4 observability event."""

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
class S4OrchestratorObservabilityEvent:
    """Output contract for one ORQ Sprint 4 observability event."""

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
    decision_reason: str | None = None
    latency_ms: int | None = None
    cost_usd: float | None = None
    custo_status: str | None = None
    latencia_status: str | None = None
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
            "decision_reason": self.decision_reason,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "custo_status": self.custo_status,
            "latencia_status": self.latencia_status,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s4_orchestrator_observability_event(
    payload: S4OrchestratorObservabilityInput,
) -> S4OrchestratorObservabilityEvent:
    """Build validated ORQ Sprint 4 observability event.

    Args:
        payload: Input observability contract with event details and context.

    Returns:
        S4OrchestratorObservabilityEvent: Structured event ready for logging.

    Raises:
        S4OrchestratorObservabilityError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade do ORQ S4 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade do ORQ S4 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo do orquestrador.",
        )
    if not event_message:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade do ORQ S4 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    attempt = payload.attempt
    if attempt is not None and attempt < 1:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_ATTEMPT",
            message="attempt de observabilidade do ORQ S4 deve ser >= 1",
            action="Informe attempt valido para rastreabilidade de execucao.",
        )

    latency_ms = payload.latency_ms
    if latency_ms is not None and latency_ms < 0:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_LATENCY_MS",
            message="latency_ms de observabilidade do ORQ S4 deve ser >= 0",
            action="Informe latencia valida em milissegundos.",
        )

    cost_usd = payload.cost_usd
    if cost_usd is not None and cost_usd < 0:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_COST_USD",
            message="cost_usd de observabilidade do ORQ S4 deve ser >= 0",
            action="Informe custo valido em USD.",
        )

    custo_status = (payload.custo_status or "").strip().lower() or None
    if custo_status and custo_status not in ALLOWED_CUSTO_STATUS:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_CUSTO_STATUS",
            message=f"custo_status de observabilidade invalido: {payload.custo_status}",
            action="Use custo_status valido: within_budget ou above_budget.",
        )

    latencia_status = (payload.latencia_status or "").strip().lower() or None
    if latencia_status and latencia_status not in ALLOWED_LATENCIA_STATUS:
        raise S4OrchestratorObservabilityError(
            code="INVALID_ORQ_S4_OBSERVABILITY_LATENCIA_STATUS",
            message=f"latencia_status de observabilidade invalido: {payload.latencia_status}",
            action="Use latencia_status valido: within_sla ou above_sla.",
        )

    return S4OrchestratorObservabilityEvent(
        observability_event_id=f"orqs4coreevt-{uuid4().hex[:12]}",
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
        decision_reason=(payload.decision_reason or "").strip() or None,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        custo_status=custo_status,
        latencia_status=latencia_status,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def log_s4_orchestrator_observability_event(event: S4OrchestratorObservabilityEvent) -> None:
    """Emit one ORQ Sprint 4 observability event to the operational logger.

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


def build_s4_orchestrator_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 4 error payload for diagnostics.

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
