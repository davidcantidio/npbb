"""Observability contracts for CONF Sprint 4 threshold tuning flow.

This module standardizes operational events for Sprint 4 confidence threshold
adjustment execution and provides actionable diagnostics correlated with service
telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.confidence.s4.core")

COMPONENT_NAME = "confidence_policy_s4_core"
DEFAULT_SEVERITY = "info"
ALLOWED_SEVERITIES = {"info", "warning", "error"}
ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}
ALLOWED_CRITICAL_VIOLATION_ROUTES = {"manual_review", "gap", "reject"}

MIN_CONFIDENCE_SCORE = 0.0
MAX_CONFIDENCE_SCORE = 1.0


class S4ConfidenceObservabilityError(ValueError):
    """Raised when CONF S4 observability contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4ConfidenceObservabilityInput:
    """Input contract used to create one CONF Sprint 4 observability event."""

    event_name: str
    correlation_id: str
    event_message: str
    severity: str = DEFAULT_SEVERITY
    policy_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    decision_mode: str | None = None
    confidence_score: float | None = None
    decision: str | None = None
    manual_review_queue_size: int | None = None
    max_manual_review_queue: int | None = None
    gap_escalation_triggered: bool | None = None
    critical_fields_present_count: int | None = None
    min_critical_fields_present: int | None = None
    critical_violation_triggered: bool | None = None
    critical_violation_route: str | None = None
    feedback_samples_count: int | None = None
    min_feedback_samples: int | None = None
    threshold_delta_applied: float | None = None
    tuned_thresholds: dict[str, float] | None = None
    quality_drop_value: float | None = None
    quality_drop_detected: bool | None = None
    anomaly_detected: bool | None = None
    calibration_frozen: bool | None = None
    stage: str | None = None
    context: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class S4ConfidenceObservabilityEvent:
    """Output contract for one CONF Sprint 4 observability event."""

    observability_event_id: str
    timestamp_utc: str
    component: str
    event_name: str
    correlation_id: str
    event_message: str
    severity: str
    policy_id: str | None = None
    dataset_name: str | None = None
    entity_kind: str | None = None
    schema_version: str | None = None
    decision_mode: str | None = None
    confidence_score: float | None = None
    decision: str | None = None
    manual_review_queue_size: int | None = None
    max_manual_review_queue: int | None = None
    gap_escalation_triggered: bool | None = None
    critical_fields_present_count: int | None = None
    min_critical_fields_present: int | None = None
    critical_violation_triggered: bool | None = None
    critical_violation_route: str | None = None
    feedback_samples_count: int | None = None
    min_feedback_samples: int | None = None
    threshold_delta_applied: float | None = None
    tuned_thresholds: dict[str, float] | None = None
    quality_drop_value: float | None = None
    quality_drop_detected: bool | None = None
    anomaly_detected: bool | None = None
    calibration_frozen: bool | None = None
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
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "decision_mode": self.decision_mode,
            "confidence_score": self.confidence_score,
            "decision": self.decision,
            "manual_review_queue_size": self.manual_review_queue_size,
            "max_manual_review_queue": self.max_manual_review_queue,
            "gap_escalation_triggered": self.gap_escalation_triggered,
            "critical_fields_present_count": self.critical_fields_present_count,
            "min_critical_fields_present": self.min_critical_fields_present,
            "critical_violation_triggered": self.critical_violation_triggered,
            "critical_violation_route": self.critical_violation_route,
            "feedback_samples_count": self.feedback_samples_count,
            "min_feedback_samples": self.min_feedback_samples,
            "threshold_delta_applied": self.threshold_delta_applied,
            "tuned_thresholds": self.tuned_thresholds,
            "quality_drop_value": self.quality_drop_value,
            "quality_drop_detected": self.quality_drop_detected,
            "anomaly_detected": self.anomaly_detected,
            "calibration_frozen": self.calibration_frozen,
            "stage": self.stage,
            "context": self.context or {},
        }

    def to_response_dict(self) -> dict[str, str]:
        """Return compact observability context for output contracts."""

        return {
            "observability_event_id": self.observability_event_id,
            "correlation_id": self.correlation_id,
        }


def build_s4_confidence_observability_event(
    payload: S4ConfidenceObservabilityInput,
) -> S4ConfidenceObservabilityEvent:
    """Build validated CONF Sprint 4 observability event.

    Args:
        payload: Input observability contract with event details and context.

    Returns:
        S4ConfidenceObservabilityEvent: Structured event ready for logging.

    Raises:
        S4ConfidenceObservabilityError: If event fields are invalid.
    """

    event_name = payload.event_name.strip()
    correlation_id = payload.correlation_id.strip()
    event_message = payload.event_message.strip()
    severity = payload.severity.strip().lower()

    if not event_name:
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_EVENT_NAME",
            message="event_name de observabilidade CONF S4 nao pode ser vazio",
            action="Defina um nome de evento operacional antes de registrar logs.",
        )
    if not correlation_id:
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_CORRELATION_ID",
            message="correlation_id de observabilidade CONF S4 nao pode ser vazio",
            action="Propague correlation_id em todo o fluxo de confianca.",
        )
    if not event_message:
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_EVENT_MESSAGE",
            message="event_message de observabilidade CONF S4 nao pode ser vazio",
            action="Forneca descricao diagnostica do evento operacional.",
        )
    if severity not in ALLOWED_SEVERITIES:
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_SEVERITY",
            message=f"severity de observabilidade invalida: {payload.severity}",
            action="Use severidades aceitas: info, warning ou error.",
        )

    confidence_score = _validate_probability(
        field_name="confidence_score",
        value=payload.confidence_score,
        error_code="INVALID_CONF_S4_OBSERVABILITY_CONFIDENCE_SCORE",
        error_action="Use confidence_score no intervalo de 0.0 a 1.0.",
    )

    decision = (payload.decision or "").strip().lower() or None
    if decision is not None and decision not in ALLOWED_DECISIONS:
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_DECISION",
            message=f"decision de observabilidade invalida: {payload.decision}",
            action="Use decision valida: auto_approve, manual_review, gap ou reject.",
        )

    manual_review_queue_size = _validate_non_negative_int(
        field_name="manual_review_queue_size",
        value=payload.manual_review_queue_size,
        error_code="INVALID_CONF_S4_OBSERVABILITY_MANUAL_REVIEW_QUEUE_SIZE",
    )
    max_manual_review_queue = _validate_non_negative_int(
        field_name="max_manual_review_queue",
        value=payload.max_manual_review_queue,
        error_code="INVALID_CONF_S4_OBSERVABILITY_MAX_MANUAL_REVIEW_QUEUE",
    )
    critical_fields_present_count = _validate_non_negative_int(
        field_name="critical_fields_present_count",
        value=payload.critical_fields_present_count,
        error_code="INVALID_CONF_S4_OBSERVABILITY_CRITICAL_FIELDS_PRESENT_COUNT",
    )
    min_critical_fields_present = _validate_non_negative_int(
        field_name="min_critical_fields_present",
        value=payload.min_critical_fields_present,
        error_code="INVALID_CONF_S4_OBSERVABILITY_MIN_CRITICAL_FIELDS_PRESENT",
    )
    feedback_samples_count = _validate_non_negative_int(
        field_name="feedback_samples_count",
        value=payload.feedback_samples_count,
        error_code="INVALID_CONF_S4_OBSERVABILITY_FEEDBACK_SAMPLES_COUNT",
    )
    min_feedback_samples = _validate_non_negative_int(
        field_name="min_feedback_samples",
        value=payload.min_feedback_samples,
        error_code="INVALID_CONF_S4_OBSERVABILITY_MIN_FEEDBACK_SAMPLES",
    )

    threshold_delta_applied = _validate_probability(
        field_name="threshold_delta_applied",
        value=payload.threshold_delta_applied,
        error_code="INVALID_CONF_S4_OBSERVABILITY_THRESHOLD_DELTA_APPLIED",
        error_action="Use threshold_delta_applied no intervalo de 0.0 a 1.0.",
    )
    quality_drop_value = _validate_probability(
        field_name="quality_drop_value",
        value=payload.quality_drop_value,
        error_code="INVALID_CONF_S4_OBSERVABILITY_QUALITY_DROP_VALUE",
        error_action="Use quality_drop_value no intervalo de 0.0 a 1.0.",
    )

    critical_violation_route = (payload.critical_violation_route or "").strip().lower() or None
    if (
        critical_violation_route is not None
        and critical_violation_route not in ALLOWED_CRITICAL_VIOLATION_ROUTES
    ):
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_CRITICAL_VIOLATION_ROUTE",
            message=(
                "critical_violation_route de observabilidade invalido: "
                f"{payload.critical_violation_route}"
            ),
            action="Use critical_violation_route valido: manual_review, gap ou reject.",
        )

    gap_escalation_triggered = _validate_optional_bool(
        field_name="gap_escalation_triggered",
        value=payload.gap_escalation_triggered,
        error_code="INVALID_CONF_S4_OBSERVABILITY_GAP_ESCALATION_TRIGGERED",
    )
    critical_violation_triggered = _validate_optional_bool(
        field_name="critical_violation_triggered",
        value=payload.critical_violation_triggered,
        error_code="INVALID_CONF_S4_OBSERVABILITY_CRITICAL_VIOLATION_TRIGGERED",
    )
    quality_drop_detected = _validate_optional_bool(
        field_name="quality_drop_detected",
        value=payload.quality_drop_detected,
        error_code="INVALID_CONF_S4_OBSERVABILITY_QUALITY_DROP_DETECTED",
    )
    anomaly_detected = _validate_optional_bool(
        field_name="anomaly_detected",
        value=payload.anomaly_detected,
        error_code="INVALID_CONF_S4_OBSERVABILITY_ANOMALY_DETECTED",
    )
    calibration_frozen = _validate_optional_bool(
        field_name="calibration_frozen",
        value=payload.calibration_frozen,
        error_code="INVALID_CONF_S4_OBSERVABILITY_CALIBRATION_FROZEN",
    )

    tuned_thresholds = _normalize_tuned_thresholds(payload.tuned_thresholds)

    return S4ConfidenceObservabilityEvent(
        observability_event_id=f"confs4coreevt-{uuid4().hex[:12]}",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        component=COMPONENT_NAME,
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        policy_id=(payload.policy_id or "").strip() or None,
        dataset_name=(payload.dataset_name or "").strip() or None,
        entity_kind=(payload.entity_kind or "").strip().lower() or None,
        schema_version=(payload.schema_version or "").strip().lower() or None,
        decision_mode=(payload.decision_mode or "").strip().lower() or None,
        confidence_score=confidence_score,
        decision=decision,
        manual_review_queue_size=manual_review_queue_size,
        max_manual_review_queue=max_manual_review_queue,
        gap_escalation_triggered=gap_escalation_triggered,
        critical_fields_present_count=critical_fields_present_count,
        min_critical_fields_present=min_critical_fields_present,
        critical_violation_triggered=critical_violation_triggered,
        critical_violation_route=critical_violation_route,
        feedback_samples_count=feedback_samples_count,
        min_feedback_samples=min_feedback_samples,
        threshold_delta_applied=threshold_delta_applied,
        tuned_thresholds=tuned_thresholds,
        quality_drop_value=quality_drop_value,
        quality_drop_detected=quality_drop_detected,
        anomaly_detected=anomaly_detected,
        calibration_frozen=calibration_frozen,
        stage=(payload.stage or "").strip() or None,
        context=payload.context or {},
    )


def log_s4_confidence_observability_event(event: S4ConfidenceObservabilityEvent) -> None:
    """Emit one CONF Sprint 4 observability event to operational logger.

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


def build_s4_confidence_actionable_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    observability_event_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONF Sprint 4 error payload for diagnostics.

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


def _validate_non_negative_int(
    *,
    field_name: str,
    value: int | None,
    error_code: str,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise S4ConfidenceObservabilityError(
            code=error_code,
            message=f"{field_name} de observabilidade CONF S4 deve ser inteiro >= 0",
            action=f"Propague {field_name} valido para rastreabilidade operacional.",
        )
    return value


def _validate_optional_bool(
    *,
    field_name: str,
    value: bool | None,
    error_code: str,
) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise S4ConfidenceObservabilityError(
            code=error_code,
            message=f"{field_name} de observabilidade CONF S4 deve ser booleano",
            action=f"Propague {field_name} como true/false para rastreabilidade operacional.",
        )
    return value


def _validate_probability(
    *,
    field_name: str,
    value: float | None,
    error_code: str,
    error_action: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise S4ConfidenceObservabilityError(
            code=error_code,
            message=f"{field_name} deve ser numerico",
            action=error_action,
        )
    numeric = float(value)
    if numeric < MIN_CONFIDENCE_SCORE or numeric > MAX_CONFIDENCE_SCORE:
        raise S4ConfidenceObservabilityError(
            code=error_code,
            message=f"{field_name} fora do intervalo permitido: {value}",
            action=error_action,
        )
    return round(numeric, 6)


def _normalize_tuned_thresholds(raw: dict[str, float] | None) -> dict[str, float] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_TUNED_THRESHOLDS",
            message="tuned_thresholds deve ser objeto com auto_approve/manual_review/gap",
            action=(
                "Propague tuned_thresholds como dict com chaves auto_approve, "
                "manual_review e gap."
            ),
        )

    normalized: dict[str, float] = {}
    for key in ("auto_approve", "manual_review", "gap"):
        if key not in raw:
            raise S4ConfidenceObservabilityError(
                code="INVALID_CONF_S4_OBSERVABILITY_TUNED_THRESHOLDS",
                message=f"tuned_thresholds sem chave obrigatoria: {key}",
                action="Inclua auto_approve, manual_review e gap em tuned_thresholds.",
            )
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise S4ConfidenceObservabilityError(
                code="INVALID_CONF_S4_OBSERVABILITY_TUNED_THRESHOLDS",
                message=f"tuned_thresholds.{key} deve ser numerico",
                action="Use valores numericos entre 0.0 e 1.0 em tuned_thresholds.",
            )
        numeric = float(value)
        if numeric < MIN_CONFIDENCE_SCORE or numeric > MAX_CONFIDENCE_SCORE:
            raise S4ConfidenceObservabilityError(
                code="INVALID_CONF_S4_OBSERVABILITY_TUNED_THRESHOLDS",
                message=f"tuned_thresholds.{key} fora do intervalo permitido: {value}",
                action="Use valores entre 0.0 e 1.0 em tuned_thresholds.",
            )
        normalized[key] = round(numeric, 6)

    if not (
        normalized["gap"] <= normalized["manual_review"] <= normalized["auto_approve"]
    ):
        raise S4ConfidenceObservabilityError(
            code="INVALID_CONF_S4_OBSERVABILITY_TUNED_THRESHOLDS",
            message="tuned_thresholds invalido: esperado gap <= manual_review <= auto_approve",
            action="Ajuste tuned_thresholds para manter ordem de decisao auto/review/gap.",
        )

    return normalized
