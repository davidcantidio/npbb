"""Observability contracts for CONT Sprint 4 compatibility/regression flow.

This module standardizes operational events for Sprint 4 canonical contract
validation and provides actionable diagnostics correlated with service telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.contracts.s4.core")

COMPONENT_NAME = "contract_validation_s4_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S4ContractObservabilityError(ValueError):
    """Raised when CONT S4 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4ContractObservabilityInput:
    """Input contract used to create one CONT Sprint 4 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    contract_id: str | None = None
    dataset_name: str | None = None
    source_kind: str | None = None
    schema_version: str | None = None
    strict_validation: bool | None = None
    lineage_required: bool | None = None
    compatibility_mode: str | None = None
    compatibility_result: str | None = None
    breaking_change_detected: bool | None = None
    regression_failures: int | None = None
    max_regression_failures: int | None = None
    regression_gate_required: bool | None = None
    regression_gate_passed: bool | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4ContractObservabilityEvent:
    """Output contract for one CONT Sprint 4 observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    contract_id: str | None = None
    dataset_name: str | None = None
    source_kind: str | None = None
    schema_version: str | None = None
    strict_validation: bool | None = None
    lineage_required: bool | None = None
    compatibility_mode: str | None = None
    compatibility_result: str | None = None
    breaking_change_detected: bool | None = None
    regression_failures: int | None = None
    max_regression_failures: int | None = None
    regression_gate_required: bool | None = None
    regression_gate_passed: bool | None = None
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
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
            "compatibility_mode": self.compatibility_mode,
            "compatibility_result": self.compatibility_result,
            "breaking_change_detected": self.breaking_change_detected,
            "regression_failures": self.regression_failures,
            "max_regression_failures": self.max_regression_failures,
            "regression_gate_required": self.regression_gate_required,
            "regression_gate_passed": self.regression_gate_passed,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s4_contract_observability_event(
    payload: S4ContractObservabilityInput,
) -> S4ContractObservabilityEvent:
    """Build validated CONT Sprint 4 observability event.

    Args:
        payload: Input observability contract with event details and context.

    Returns:
        S4ContractObservabilityEvent: Structured event ready for logging.

    Raises:
        S4ContractObservabilityError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade CONT S4 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade CONT S4 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo de validacao.",
        )
    if not event_message:
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade CONT S4 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    if payload.regression_failures is not None and payload.regression_failures < 0:
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_REGRESSION_FAILURES",
            message="regression_failures deve ser >= 0",
            action="Propague contagem valida de falhas de regressao.",
        )

    if payload.max_regression_failures is not None and payload.max_regression_failures < 0:
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_MAX_REGRESSION_FAILURES",
            message="max_regression_failures deve ser >= 0",
            action="Propague limite valido de falhas de regressao.",
        )

    if (
        payload.regression_failures is not None
        and payload.max_regression_failures is not None
        and payload.regression_failures > payload.max_regression_failures
        and payload.regression_gate_passed is True
    ):
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_REGRESSION_GATE_STATE",
            message=(
                "regression_gate_passed=true e inconsistente com "
                "regression_failures > max_regression_failures"
            ),
            action="Corrija flags de gate ou contagens de regressao antes de emitir o evento.",
        )

    if payload.compatibility_result is not None and not str(payload.compatibility_result).strip():
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_COMPATIBILITY_RESULT",
            message="compatibility_result nao pode ser vazio",
            action="Propague resultado de compatibilidade com valor descritivo.",
        )

    if (
        payload.breaking_change_detected is not None
        and not isinstance(payload.breaking_change_detected, bool)
    ):
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_BREAKING_CHANGE_FLAG",
            message="breaking_change_detected deve ser booleano",
            action="Use true/false para indicar deteccao de breaking change.",
        )
    if (
        payload.regression_gate_required is not None
        and not isinstance(payload.regression_gate_required, bool)
    ):
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_REGRESSION_GATE_REQUIRED",
            message="regression_gate_required deve ser booleano",
            action="Use true/false para indicar obrigatoriedade do regression gate.",
        )
    if payload.regression_gate_passed is not None and not isinstance(payload.regression_gate_passed, bool):
        raise S4ContractObservabilityError(
            code="INVALID_CONT_S4_OBSERVABILITY_REGRESSION_GATE_PASSED",
            message="regression_gate_passed deve ser booleano",
            action="Use true/false para indicar status final do regression gate.",
        )

    return S4ContractObservabilityEvent(
        observability_event_id=f"conts4coreevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        contract_id=(payload.contract_id or "").strip() or None,
        dataset_name=(payload.dataset_name or "").strip() or None,
        source_kind=(payload.source_kind or "").strip().lower() or None,
        schema_version=(payload.schema_version or "").strip().lower() or None,
        strict_validation=payload.strict_validation,
        lineage_required=payload.lineage_required,
        compatibility_mode=(payload.compatibility_mode or "").strip().lower() or None,
        compatibility_result=(payload.compatibility_result or "").strip().lower() or None,
        breaking_change_detected=payload.breaking_change_detected,
        regression_failures=payload.regression_failures,
        max_regression_failures=payload.max_regression_failures,
        regression_gate_required=payload.regression_gate_required,
        regression_gate_passed=payload.regression_gate_passed,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def log_s4_contract_observability_event(event: S4ContractObservabilityEvent) -> None:
    """Emit one CONT Sprint 4 observability event to operational logger.

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


def build_s4_contract_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONT Sprint 4 error payload for diagnostics.

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
