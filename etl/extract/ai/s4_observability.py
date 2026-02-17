"""Observability contracts for XIA Sprint 4 AI extraction flow.

This module standardizes operational events for Sprint 4 calibrated
extraction and cross-format consolidation and provides actionable diagnostics
correlated with service telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.extract.ai.s4.core")

COMPONENT_NAME = "etl_extract_ai_s4_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S4ExtractAIObservabilityError(ValueError):
    """Raised when XIA S4 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4ExtractAIObservabilityInput:
    """Input contract used to create one XIA Sprint 4 observability event."""

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
    quality_profile_hint: str | None = None
    consolidation_scope: str | None = None
    output_normalization_profile: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4ExtractAIObservabilityEvent:
    """Output contract for one XIA Sprint 4 observability event."""

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
    model_provider: str | None = None
    model_name: str | None = None
    chunk_strategy: str | None = None
    quality_profile_hint: str | None = None
    consolidation_scope: str | None = None
    output_normalization_profile: str | None = None
    chunk_count: int | None = None
    decision_reason: str | None = None
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
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "chunk_strategy": self.chunk_strategy,
            "quality_profile_hint": self.quality_profile_hint,
            "consolidation_scope": self.consolidation_scope,
            "output_normalization_profile": self.output_normalization_profile,
            "chunk_count": self.chunk_count,
            "decision_reason": self.decision_reason,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s4_extract_ai_observability_event(
    payload: S4ExtractAIObservabilityInput,
) -> S4ExtractAIObservabilityEvent:
    """Build validated XIA Sprint 4 observability event.

    Args:
        payload: Input observability contract with event details and context.

    Returns:
        S4ExtractAIObservabilityEvent: Structured event ready for logging.

    Raises:
        S4ExtractAIObservabilityError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4ExtractAIObservabilityError(
            code="INVALID_XIA_S4_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade XIA S4 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S4ExtractAIObservabilityError(
            code="INVALID_XIA_S4_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade XIA S4 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo de extracao IA.",
        )
    if not event_message:
        raise S4ExtractAIObservabilityError(
            code="INVALID_XIA_S4_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade XIA S4 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4ExtractAIObservabilityError(
            code="INVALID_XIA_S4_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    if payload.chunk_count is not None and payload.chunk_count < 1:
        raise S4ExtractAIObservabilityError(
            code="INVALID_XIA_S4_OBSERVABILITY_CHUNK_COUNT",
            message="chunk_count de observabilidade XIA S4 deve ser >= 1",
            action="Informe chunk_count valido para rastreabilidade operacional.",
        )

    return S4ExtractAIObservabilityEvent(
        observability_event_id=f"xias4coreevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
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
        quality_profile_hint=(payload.quality_profile_hint or "").strip().lower() or None,
        consolidation_scope=(payload.consolidation_scope or "").strip().lower() or None,
        output_normalization_profile=(payload.output_normalization_profile or "").strip().lower() or None,
        chunk_count=payload.chunk_count,
        decision_reason=(payload.decision_reason or "").strip() or None,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def log_s4_extract_ai_observability_event(event: S4ExtractAIObservabilityEvent) -> None:
    """Emit one XIA Sprint 4 observability event to operational logger.

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


def build_s4_extract_ai_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable XIA Sprint 4 error payload for diagnostics.

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
