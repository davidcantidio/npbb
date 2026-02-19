"""Telemetry helpers for CONT Sprint 1, Sprint 2, Sprint 3, and Sprint 4 flows.

This service centralizes operational telemetry contracts used by canonical
contract validation. It keeps event payloads stable and builds actionable
error details for service layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


COMPONENT_NAME_S1 = "contrato_canonico_validacao_estrita_linhagem_obrigatoria_s1"
COMPONENT_NAME_S2 = "contrato_canonico_validacao_estrita_linhagem_obrigatoria_s2"
COMPONENT_NAME_S3 = "contrato_canonico_validacao_estrita_linhagem_obrigatoria_s3"
COMPONENT_NAME_S4 = "contrato_canonico_validacao_estrita_linhagem_obrigatoria_s4"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}


class S1ContractTelemetryContractError(ValueError):
    """Raised when CONT Sprint 1 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S2ContractTelemetryContractError(ValueError):
    """Raised when CONT Sprint 2 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S3ContractTelemetryContractError(ValueError):
    """Raised when CONT Sprint 3 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


class S4ContractTelemetryContractError(ValueError):
    """Raised when CONT Sprint 4 telemetry contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1ContractTelemetryInput:
    """Input contract for CONT Sprint 1 telemetry event creation."""

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
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S2ContractTelemetryInput:
    """Input contract for CONT Sprint 2 telemetry event creation."""

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
    schema_checks_executed: int | None = None
    domain_checks_executed: int | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S3ContractTelemetryInput:
    """Input contract for CONT Sprint 3 telemetry event creation."""

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
    field_lineage_checks_executed: int | None = None
    metric_lineage_checks_executed: int | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4ContractTelemetryInput:
    """Input contract for CONT Sprint 4 telemetry event creation."""

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
class S1ContractTelemetryEvent:
    """Output contract for one structured CONT Sprint 1 telemetry event."""

    telemetry_event_id: str
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
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
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
class S2ContractTelemetryEvent:
    """Output contract for one structured CONT Sprint 2 telemetry event."""

    telemetry_event_id: str
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
    schema_checks_executed: int | None = None
    domain_checks_executed: int | None = None
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
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
            "schema_checks_executed": self.schema_checks_executed,
            "domain_checks_executed": self.domain_checks_executed,
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
class S3ContractTelemetryEvent:
    """Output contract for one structured CONT Sprint 3 telemetry event."""

    telemetry_event_id: str
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
    field_lineage_checks_executed: int | None = None
    metric_lineage_checks_executed: int | None = None
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
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
            "field_lineage_checks_executed": self.field_lineage_checks_executed,
            "metric_lineage_checks_executed": self.metric_lineage_checks_executed,
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
class S4ContractTelemetryEvent:
    """Output contract for one structured CONT Sprint 4 telemetry event."""

    telemetry_event_id: str
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
        """Return safe dictionary for `logging.Logger.*(..., extra=...)`."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
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
        """Return compact telemetry context for service output payloads."""

        return {
            "telemetry_event_id": self.telemetry_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s1_contract_telemetry_event(
    payload: S1ContractTelemetryInput,
) -> S1ContractTelemetryEvent:
    """Build a validated CONT Sprint 1 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S1ContractTelemetryEvent: Structured event ready for logging.

    Raises:
        S1ContractTelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S1ContractTelemetryContractError(
            code="INVALID_CONT_S1_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria CONT S1 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S1ContractTelemetryContractError(
            code="INVALID_CONT_S1_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria CONT S1 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S1ContractTelemetryContractError(
            code="INVALID_CONT_S1_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria CONT S1 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S1ContractTelemetryContractError(
            code="INVALID_CONT_S1_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    return S1ContractTelemetryEvent(
        telemetry_event_id=f"conts1evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S1,
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
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def build_s2_contract_telemetry_event(
    payload: S2ContractTelemetryInput,
) -> S2ContractTelemetryEvent:
    """Build a validated CONT Sprint 2 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S2ContractTelemetryEvent: Structured event ready for logging.

    Raises:
        S2ContractTelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S2ContractTelemetryContractError(
            code="INVALID_CONT_S2_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria CONT S2 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S2ContractTelemetryContractError(
            code="INVALID_CONT_S2_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria CONT S2 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S2ContractTelemetryContractError(
            code="INVALID_CONT_S2_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria CONT S2 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S2ContractTelemetryContractError(
            code="INVALID_CONT_S2_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    if payload.schema_checks_executed is not None and payload.schema_checks_executed < 0:
        raise S2ContractTelemetryContractError(
            code="INVALID_CONT_S2_TELEMETRY_SCHEMA_CHECKS",
            message="schema_checks_executed deve ser >= 0",
            action="Propague contagem valida de verificacoes de schema no evento.",
        )
    if payload.domain_checks_executed is not None and payload.domain_checks_executed < 0:
        raise S2ContractTelemetryContractError(
            code="INVALID_CONT_S2_TELEMETRY_DOMAIN_CHECKS",
            message="domain_checks_executed deve ser >= 0",
            action="Propague contagem valida de verificacoes de dominio no evento.",
        )

    return S2ContractTelemetryEvent(
        telemetry_event_id=f"conts2evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S2,
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
        schema_checks_executed=payload.schema_checks_executed,
        domain_checks_executed=payload.domain_checks_executed,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def build_s3_contract_telemetry_event(
    payload: S3ContractTelemetryInput,
) -> S3ContractTelemetryEvent:
    """Build a validated CONT Sprint 3 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S3ContractTelemetryEvent: Structured event ready for logging.

    Raises:
        S3ContractTelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S3ContractTelemetryContractError(
            code="INVALID_CONT_S3_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria CONT S3 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S3ContractTelemetryContractError(
            code="INVALID_CONT_S3_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria CONT S3 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S3ContractTelemetryContractError(
            code="INVALID_CONT_S3_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria CONT S3 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S3ContractTelemetryContractError(
            code="INVALID_CONT_S3_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )
    if payload.field_lineage_checks_executed is not None and payload.field_lineage_checks_executed < 0:
        raise S3ContractTelemetryContractError(
            code="INVALID_CONT_S3_TELEMETRY_FIELD_LINEAGE_CHECKS",
            message="field_lineage_checks_executed deve ser >= 0",
            action="Propague contagem valida de verificacoes de linhagem por campo no evento.",
        )
    if payload.metric_lineage_checks_executed is not None and payload.metric_lineage_checks_executed < 0:
        raise S3ContractTelemetryContractError(
            code="INVALID_CONT_S3_TELEMETRY_METRIC_LINEAGE_CHECKS",
            message="metric_lineage_checks_executed deve ser >= 0",
            action="Propague contagem valida de verificacoes de linhagem por metrica no evento.",
        )

    return S3ContractTelemetryEvent(
        telemetry_event_id=f"conts3evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S3,
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
        field_lineage_checks_executed=payload.field_lineage_checks_executed,
        metric_lineage_checks_executed=payload.metric_lineage_checks_executed,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def build_s4_contract_telemetry_event(
    payload: S4ContractTelemetryInput,
) -> S4ContractTelemetryEvent:
    """Build a validated CONT Sprint 4 telemetry event.

    Args:
        payload: Input telemetry contract with operation context and severity.

    Returns:
        S4ContractTelemetryEvent: Structured event ready for logging.

    Raises:
        S4ContractTelemetryContractError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_EVENT_NAME",
            message="event_name de telemetria CONT S4 nao pode ser vazio",
            action="Defina o nome do evento operacional antes de emitir logs.",
        )
    if not correlation_id:
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_CORRELATION_ID",
            message="correlation_id de telemetria CONT S4 nao pode ser vazio",
            action="Propague correlation_id no fluxo antes de logar eventos.",
        )
    if not event_message:
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_EVENT_MESSAGE",
            message="event_message de telemetria CONT S4 nao pode ser vazio",
            action="Forneca descricao operacional para diagnostico do evento.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_SEVERITY",
            message=f"severity de telemetria invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    if payload.regression_failures is not None and payload.regression_failures < 0:
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_REGRESSION_FAILURES",
            message="regression_failures deve ser >= 0",
            action="Propague contagem valida de falhas de regressao no evento.",
        )

    if payload.max_regression_failures is not None and payload.max_regression_failures < 0:
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_MAX_REGRESSION_FAILURES",
            message="max_regression_failures deve ser >= 0",
            action="Propague limite valido de falhas de regressao no evento.",
        )

    if (
        payload.regression_failures is not None
        and payload.max_regression_failures is not None
        and payload.regression_failures > payload.max_regression_failures
        and payload.regression_gate_passed is True
    ):
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_REGRESSION_GATE_STATE",
            message=(
                "regression_gate_passed=true e inconsistente com "
                "regression_failures > max_regression_failures"
            ),
            action="Corrija status do gate ou contagens de regressao antes de emitir telemetria.",
        )

    if payload.compatibility_result is not None and not str(payload.compatibility_result).strip():
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_COMPATIBILITY_RESULT",
            message="compatibility_result nao pode ser vazio",
            action="Propague resultado de compatibilidade com valor descritivo.",
        )

    if (
        payload.breaking_change_detected is not None
        and not isinstance(payload.breaking_change_detected, bool)
    ):
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_BREAKING_CHANGE_FLAG",
            message="breaking_change_detected deve ser booleano",
            action="Use true/false para indicar deteccao de breaking change.",
        )
    if (
        payload.regression_gate_required is not None
        and not isinstance(payload.regression_gate_required, bool)
    ):
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_REGRESSION_GATE_REQUIRED",
            message="regression_gate_required deve ser booleano",
            action="Use true/false para indicar obrigatoriedade do regression gate.",
        )
    if payload.regression_gate_passed is not None and not isinstance(payload.regression_gate_passed, bool):
        raise S4ContractTelemetryContractError(
            code="INVALID_CONT_S4_TELEMETRY_REGRESSION_GATE_PASSED",
            message="regression_gate_passed deve ser booleano",
            action="Use true/false para indicar status final do regression gate.",
        )

    return S4ContractTelemetryEvent(
        telemetry_event_id=f"conts4evt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME_S4,
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


def emit_s1_contract_telemetry_event(
    logger: logging.Logger,
    event: S1ContractTelemetryEvent,
) -> None:
    """Emit one CONT Sprint 1 telemetry event to operational logger.

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


def emit_s2_contract_telemetry_event(
    logger: logging.Logger,
    event: S2ContractTelemetryEvent,
) -> None:
    """Emit one CONT Sprint 2 telemetry event to operational logger.

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


def emit_s3_contract_telemetry_event(
    logger: logging.Logger,
    event: S3ContractTelemetryEvent,
) -> None:
    """Emit one CONT Sprint 3 telemetry event to operational logger.

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


def emit_s4_contract_telemetry_event(
    logger: logging.Logger,
    event: S4ContractTelemetryEvent,
) -> None:
    """Emit one CONT Sprint 4 telemetry event to operational logger.

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


def build_s1_contract_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONT Sprint 1 error detail with telemetry references.

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


def build_s2_contract_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONT Sprint 2 error detail with telemetry references.

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


def build_s3_contract_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONT Sprint 3 error detail with telemetry references.

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


def build_s4_contract_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    telemetry_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONT Sprint 4 error detail with telemetry references.

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
