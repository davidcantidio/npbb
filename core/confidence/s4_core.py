"""Main flow for CONF Sprint 4 threshold tuning from real outcomes.

This module executes the Sprint 4 core path:
1) validate input and resolve Sprint 4 scaffold policy;
2) execute one threshold-adjustment pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s4_scaffold import (
    S4ConfidenceScaffoldError,
    S4ConfidenceScaffoldRequest,
    build_s4_confidence_scaffold,
)


logger = logging.getLogger("npbb.core.confidence.s4.core")

CONTRACT_VERSION = "conf.s4.core.v1"
CONF_S4_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONF_S4_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONF_S4_ALLOWED_EXEC_STATUSES = CONF_S4_SUCCESS_STATUSES | CONF_S4_FAILED_STATUSES
CONF_S4_ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}

MIN_SCORE = 0.0
MAX_SCORE = 1.0


class S4ConfidenceCoreError(RuntimeError):
    """Raised when CONF Sprint 4 core flow fails."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        stage: str,
        event_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.stage = stage
        self.event_id = event_id

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        payload = {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "stage": self.stage,
        }
        if self.event_id:
            payload["event_id"] = self.event_id
        return payload


@dataclass(frozen=True, slots=True)
class S4ConfidenceCoreInput:
    """Input contract consumed by CONF Sprint 4 core flow."""

    policy_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v4"
    owner_team: str = "etl"
    field_weights: dict[str, float] | None = None
    default_weight: float = 1.0
    auto_approve_threshold: float = 0.85
    manual_review_threshold: float = 0.60
    gap_threshold: float = 0.40
    missing_field_penalty: float = 0.10
    decision_mode: str = "feedback_adjusted_thresholds"
    gap_escalation_required: bool = True
    max_manual_review_queue: int = 500
    critical_fields: tuple[str, ...] | None = None
    min_critical_fields_present: int = 1
    critical_field_penalty: float = 0.20
    critical_violation_route: str = "manual_review"
    critical_override_required: bool = True
    feedback_window_days: int = 30
    min_feedback_samples: int = 200
    auto_threshold_tuning_enabled: bool = True
    max_threshold_delta: float = 0.10
    quality_drop_tolerance: float = 0.05
    calibration_freeze_on_anomaly: bool = True
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S4ConfidenceScaffoldRequest:
        """Build scaffold request using CONF Sprint 4 stable fields."""

        return S4ConfidenceScaffoldRequest(
            policy_id=self.policy_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            field_weights=self.field_weights,
            default_weight=self.default_weight,
            auto_approve_threshold=self.auto_approve_threshold,
            manual_review_threshold=self.manual_review_threshold,
            gap_threshold=self.gap_threshold,
            missing_field_penalty=self.missing_field_penalty,
            decision_mode=self.decision_mode,
            gap_escalation_required=self.gap_escalation_required,
            max_manual_review_queue=self.max_manual_review_queue,
            critical_fields=self.critical_fields,
            min_critical_fields_present=self.min_critical_fields_present,
            critical_field_penalty=self.critical_field_penalty,
            critical_violation_route=self.critical_violation_route,
            critical_override_required=self.critical_override_required,
            feedback_window_days=self.feedback_window_days,
            min_feedback_samples=self.min_feedback_samples,
            auto_threshold_tuning_enabled=self.auto_threshold_tuning_enabled,
            max_threshold_delta=self.max_threshold_delta,
            quality_drop_tolerance=self.quality_drop_tolerance,
            calibration_freeze_on_anomaly=self.calibration_freeze_on_anomaly,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4ConfidenceCoreOutput:
    """Output contract returned by CONF Sprint 4 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    policy_id: str
    dataset_name: str
    decision_policy: dict[str, Any]
    execucao: dict[str, Any]
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for API, logs, and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "decision_policy": self.decision_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s4_confidence_policy_main_flow(
    flow_input: S4ConfidenceCoreInput,
    *,
    execute_threshold_adjustment: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S4ConfidenceCoreOutput:
    """Execute CONF Sprint 4 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with critical-field rules, feedback window,
            and threshold-adjustment guardrails for Sprint 4 confidence policy.
        execute_threshold_adjustment: Optional callback responsible for one
            threshold-adjustment execution. It receives an execution context and
            must return a dictionary with `status` and `confidence_score`.

    Returns:
        S4ConfidenceCoreOutput: Stable output with decision policy,
            execution diagnostics, and observability identifiers.

    Raises:
        S4ConfidenceCoreError: If scaffold validation fails, execution response
            is invalid, or threshold-adjustment execution fails.
    """

    correlation_id = flow_input.correlation_id or f"conf-s4-{uuid4().hex[:12]}"
    adjuster = execute_threshold_adjustment or _default_threshold_adjuster
    started_event_id = _new_event_id()
    logger.info(
        "confidence_policy_s4_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": flow_input.policy_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "decision_mode": flow_input.decision_mode,
            "auto_threshold_tuning_enabled": flow_input.auto_threshold_tuning_enabled,
        },
    )

    try:
        scaffold = build_s4_confidence_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        thresholds = dict(scaffold.decision_policy.get("thresholds", {}))
        auto_approve_threshold = float(thresholds.get("auto_approve", 0.85))
        manual_review_threshold = float(thresholds.get("manual_review", 0.60))
        gap_threshold = float(thresholds.get("gap", 0.40))

        operational_policy = dict(scaffold.decision_policy.get("operational_policy", {}))
        gap_escalation_required = bool(operational_policy.get("gap_escalation_required", False))
        max_manual_review_queue = int(operational_policy.get("max_manual_review_queue", 0))

        critical_fields_policy = dict(scaffold.decision_policy.get("critical_fields_policy", {}))
        critical_fields = list(critical_fields_policy.get("critical_fields", []))
        critical_fields_count = len(critical_fields)
        min_critical_fields_present = int(
            critical_fields_policy.get("min_critical_fields_present", critical_fields_count or 1)
        )
        critical_field_penalty = float(critical_fields_policy.get("critical_field_penalty", 0.0))
        critical_violation_route = str(
            critical_fields_policy.get("critical_violation_route", "manual_review")
        ).strip().lower()
        critical_override_required = bool(
            critical_fields_policy.get("critical_override_required", False)
        )

        threshold_calibration_policy = dict(
            scaffold.decision_policy.get("threshold_calibration_policy", {})
        )
        feedback_window_days = int(threshold_calibration_policy.get("feedback_window_days", 30))
        min_feedback_samples = int(threshold_calibration_policy.get("min_feedback_samples", 200))
        auto_threshold_tuning_enabled = bool(
            threshold_calibration_policy.get("auto_threshold_tuning_enabled", False)
        )
        max_threshold_delta = float(threshold_calibration_policy.get("max_threshold_delta", 0.0))
        quality_drop_tolerance = float(
            threshold_calibration_policy.get("quality_drop_tolerance", 0.0)
        )
        calibration_freeze_on_anomaly = bool(
            threshold_calibration_policy.get("calibration_freeze_on_anomaly", False)
        )

        adjustment_context = {
            "correlation_id": correlation_id,
            "policy_id": scaffold.policy_id,
            "dataset_name": scaffold.dataset_name,
            "entity_kind": scaffold.decision_policy.get("entity_kind"),
            "decision_mode": scaffold.decision_policy.get("decision_mode"),
            "field_weights_count": scaffold.decision_policy.get("field_weights_count", 0),
            "default_weight": scaffold.decision_policy.get("default_weight", 1.0),
            "missing_field_penalty": scaffold.decision_policy.get("missing_field_penalty", 0.0),
            "auto_approve_threshold": auto_approve_threshold,
            "manual_review_threshold": manual_review_threshold,
            "gap_threshold": gap_threshold,
            "gap_escalation_required": gap_escalation_required,
            "max_manual_review_queue": max_manual_review_queue,
            "critical_fields": critical_fields,
            "critical_fields_count": critical_fields_count,
            "min_critical_fields_present": min_critical_fields_present,
            "critical_field_penalty": critical_field_penalty,
            "critical_violation_route": critical_violation_route,
            "critical_override_required": critical_override_required,
            "feedback_window_days": feedback_window_days,
            "min_feedback_samples": min_feedback_samples,
            "auto_threshold_tuning_enabled": auto_threshold_tuning_enabled,
            "max_threshold_delta": max_threshold_delta,
            "quality_drop_tolerance": quality_drop_tolerance,
            "calibration_freeze_on_anomaly": calibration_freeze_on_anomaly,
        }

        response = adjuster(adjustment_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="threshold_adjustment_engine",
            thresholds={
                "auto_approve": auto_approve_threshold,
                "manual_review": manual_review_threshold,
                "gap": gap_threshold,
            },
            max_threshold_delta=max_threshold_delta,
            max_critical_fields_count=critical_fields_count,
        )
        status = normalized["status"]
        confidence_score = float(normalized["confidence_score"])
        manual_review_queue_size = int(normalized.get("manual_review_queue_size", 0))
        critical_fields_present_count = int(
            normalized.get("critical_fields_present_count", critical_fields_count)
        )
        feedback_samples_count = int(normalized.get("feedback_samples_count", 0))
        threshold_delta_applied = float(normalized.get("threshold_delta_applied", 0.0))
        quality_drop_value = float(normalized.get("quality_drop_value", 0.0))
        quality_drop_detected = bool(
            normalized.get("quality_drop_detected", quality_drop_value > quality_drop_tolerance)
        )
        anomaly_detected = bool(normalized.get("anomaly_detected", False))
        calibration_frozen = bool(normalized.get("calibration_frozen", False))

        tuned_thresholds = _resolve_tuned_thresholds(
            base_thresholds={
                "auto_approve": auto_approve_threshold,
                "manual_review": manual_review_threshold,
                "gap": gap_threshold,
            },
            response_tuned_thresholds=normalized.get("tuned_thresholds"),
            max_threshold_delta=max_threshold_delta,
            correlation_id=correlation_id,
            stage="threshold_adjustment_engine",
        )

        decision = str(normalized.get("decision") or "").strip().lower()
        if not decision:
            decision = _derive_decision(
                confidence_score=confidence_score,
                auto_approve_threshold=tuned_thresholds["auto_approve"],
                manual_review_threshold=tuned_thresholds["manual_review"],
                gap_threshold=tuned_thresholds["gap"],
            )

        if decision not in CONF_S4_ALLOWED_DECISIONS:
            raise S4ConfidenceCoreError(
                code="INVALID_CONFIDENCE_DECISION",
                message=f"Decisao de confianca invalida: {decision}",
                action="Retorne decisao valida: auto_approve, manual_review, gap ou reject.",
                correlation_id=correlation_id,
                stage="threshold_adjustment_engine",
            )

        if not auto_threshold_tuning_enabled and threshold_delta_applied > 0.0:
            raise S4ConfidenceCoreError(
                code="MANUAL_TUNING_REQUIRES_ZERO_MAX_THRESHOLD_DELTA",
                message="auto_threshold_tuning_enabled=false exige threshold_delta_applied=0.0",
                action=(
                    "Retorne threshold_delta_applied=0.0 quando auto_threshold_tuning_enabled=false."
                ),
                correlation_id=correlation_id,
                stage="threshold_adjustment_engine",
            )

        if (
            auto_threshold_tuning_enabled
            and feedback_samples_count < min_feedback_samples
            and threshold_delta_applied > 0.0
        ):
            raise S4ConfidenceCoreError(
                code="INSUFFICIENT_FEEDBACK_FOR_THRESHOLD_TUNING",
                message=(
                    "feedback_samples_count insuficiente para ajuste de threshold: "
                    f"{feedback_samples_count} < {min_feedback_samples}"
                ),
                action=(
                    "Aguarde mais feedback real ou force threshold_delta_applied=0.0 "
                    "ate atingir min_feedback_samples."
                ),
                correlation_id=correlation_id,
                stage="threshold_adjustment_engine",
            )

        critical_violation_triggered = (
            critical_override_required
            and critical_fields_present_count < min_critical_fields_present
        )
        if critical_violation_triggered:
            decision = critical_violation_route
            confidence_score = max(MIN_SCORE, confidence_score - critical_field_penalty)
            if not str(normalized.get("decision_reason") or "").strip():
                normalized["decision_reason"] = "critical_fields_violation"

        gap_escalation_triggered = False
        if (
            decision == "manual_review"
            and gap_escalation_required
            and manual_review_queue_size > max_manual_review_queue
        ):
            decision = "gap"
            gap_escalation_triggered = True
            if not str(normalized.get("decision_reason") or "").strip():
                normalized["decision_reason"] = "manual_review_queue_overflow"

        if calibration_freeze_on_anomaly and anomaly_detected:
            calibration_frozen = True

        completed_event_id = _new_event_id()
        logger.info(
            "confidence_policy_s4_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "decision": decision,
                "confidence_score": confidence_score,
                "manual_review_queue_size": manual_review_queue_size,
                "critical_fields_present_count": critical_fields_present_count,
                "feedback_samples_count": feedback_samples_count,
                "threshold_delta_applied": threshold_delta_applied,
                "quality_drop_value": quality_drop_value,
                "quality_drop_detected": quality_drop_detected,
                "anomaly_detected": anomaly_detected,
                "calibration_frozen": calibration_frozen,
            },
        )

        if status not in CONF_S4_SUCCESS_STATUSES:
            raise S4ConfidenceCoreError(
                code="CONF_S4_THRESHOLD_ADJUSTMENT_FAILED",
                message=(
                    "Execucao de ajuste de threshold CONF S4 falhou com status "
                    f"'{status}'"
                ),
                action=(
                    "Revisar logs do executor de ajuste e validar guardrails de "
                    "feedback_window_days/min_feedback_samples/max_threshold_delta."
                ),
                correlation_id=correlation_id,
                stage="threshold_adjustment_engine",
                event_id=completed_event_id,
            )

        if quality_drop_value > quality_drop_tolerance:
            raise S4ConfidenceCoreError(
                code="CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED",
                message=(
                    "quality_drop_value excedeu quality_drop_tolerance: "
                    f"{quality_drop_value} > {quality_drop_tolerance}"
                ),
                action=(
                    "Congele calibracao, revise qualidade real por janela de feedback "
                    "e reduza threshold_delta_applied antes de reprocessar."
                ),
                correlation_id=correlation_id,
                stage="threshold_adjustment_engine",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["confidence_policy_core_module"] = (
            "core.confidence.s4_core.execute_s4_confidence_policy_main_flow"
        )

        return S4ConfidenceCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            policy_id=scaffold.policy_id,
            dataset_name=scaffold.dataset_name,
            decision_policy=dict(scaffold.decision_policy),
            execucao={
                "status": status,
                "decision": decision,
                "confidence_score": round(confidence_score, 6),
                "decision_reason": str(
                    normalized.get("decision_reason", "dry_run_threshold_adjustment")
                ),
                "decision_result_id": str(normalized.get("decision_result_id", "")),
                "manual_review_queue_size": manual_review_queue_size,
                "critical_fields_present_count": critical_fields_present_count,
                "critical_violation_triggered": critical_violation_triggered,
                "gap_escalation_triggered": gap_escalation_triggered,
                "feedback_samples_count": feedback_samples_count,
                "threshold_delta_applied": round(threshold_delta_applied, 6),
                "tuned_thresholds": tuned_thresholds,
                "quality_drop_value": round(quality_drop_value, 6),
                "quality_drop_detected": quality_drop_detected,
                "anomaly_detected": anomaly_detected,
                "calibration_frozen": calibration_frozen,
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S4ConfidenceScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "confidence_policy_s4_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S4ConfidenceCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4ConfidenceCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "confidence_policy_s4_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4ConfidenceCoreError(
            code="CONF_S4_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONF S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONF S4.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
    thresholds: dict[str, float],
    max_threshold_delta: float,
    max_critical_fields_count: int,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S4ConfidenceCoreError(
            code="INVALID_THRESHOLD_ADJUSTMENT_RESPONSE",
            message="Executor de ajuste retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e 'confidence_score'.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONF_S4_ALLOWED_EXEC_STATUSES:
        raise S4ConfidenceCoreError(
            code="INVALID_THRESHOLD_ADJUSTMENT_STATUS",
            message=f"Status de ajuste invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    score = response.get("confidence_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise S4ConfidenceCoreError(
            code="INVALID_CONFIDENCE_SCORE",
            message=f"confidence_score invalido: {score}",
            action="Retorne confidence_score numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    score_value = float(score)
    if score_value < MIN_SCORE or score_value > MAX_SCORE:
        raise S4ConfidenceCoreError(
            code="CONFIDENCE_SCORE_OUT_OF_RANGE",
            message=f"confidence_score fora do intervalo permitido: {score}",
            action="Ajuste confidence_score para intervalo entre 0.0 e 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    manual_review_queue_size = _normalize_non_negative_int(
        field_name="manual_review_queue_size",
        value=response.get("manual_review_queue_size", 0),
        correlation_id=correlation_id,
        stage=stage,
    )
    critical_fields_present_count = _normalize_non_negative_int(
        field_name="critical_fields_present_count",
        value=response.get("critical_fields_present_count", max_critical_fields_count),
        correlation_id=correlation_id,
        stage=stage,
    )
    if critical_fields_present_count > max_critical_fields_count:
        raise S4ConfidenceCoreError(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count nao pode ser maior que o total "
                f"de campos criticos: {critical_fields_present_count}"
            ),
            action="Ajuste critical_fields_present_count para valor <= total de campos criticos.",
            correlation_id=correlation_id,
            stage=stage,
        )

    feedback_samples_count = _normalize_non_negative_int(
        field_name="feedback_samples_count",
        value=response.get("feedback_samples_count", 0),
        correlation_id=correlation_id,
        stage=stage,
    )

    threshold_delta_applied = _normalize_probability(
        field_name="threshold_delta_applied",
        value=response.get("threshold_delta_applied", 0.0),
        correlation_id=correlation_id,
        stage=stage,
    )
    if threshold_delta_applied > max_threshold_delta:
        raise S4ConfidenceCoreError(
            code="THRESHOLD_DELTA_EXCEEDS_LIMIT",
            message=(
                "threshold_delta_applied excede max_threshold_delta: "
                f"{threshold_delta_applied} > {max_threshold_delta}"
            ),
            action="Ajuste threshold_delta_applied para valor <= max_threshold_delta.",
            correlation_id=correlation_id,
            stage=stage,
        )

    quality_drop_value = _normalize_probability(
        field_name="quality_drop_value",
        value=response.get("quality_drop_value", 0.0),
        correlation_id=correlation_id,
        stage=stage,
    )

    normalized = dict(response)
    normalized["status"] = status
    normalized["confidence_score"] = round(score_value, 6)
    normalized["manual_review_queue_size"] = manual_review_queue_size
    normalized["critical_fields_present_count"] = critical_fields_present_count
    normalized["feedback_samples_count"] = feedback_samples_count
    normalized["threshold_delta_applied"] = round(threshold_delta_applied, 6)
    normalized["quality_drop_value"] = round(quality_drop_value, 6)

    if "decision" in normalized:
        decision = str(normalized.get("decision", "")).strip().lower()
        if decision and decision not in CONF_S4_ALLOWED_DECISIONS:
            raise S4ConfidenceCoreError(
                code="INVALID_CONFIDENCE_DECISION",
                message=f"Decisao de confianca invalida: {normalized.get('decision')}",
                action="Retorne decisao valida: auto_approve, manual_review, gap ou reject.",
                correlation_id=correlation_id,
                stage=stage,
            )
        normalized["decision"] = decision

    for field_name in ("quality_drop_detected", "anomaly_detected", "calibration_frozen"):
        if field_name in normalized and not isinstance(normalized[field_name], bool):
            raise S4ConfidenceCoreError(
                code="INVALID_BOOLEAN_FLAG",
                message=f"{field_name} deve ser booleano na resposta de execucao",
                action=f"Retorne {field_name} como true/false.",
                correlation_id=correlation_id,
                stage=stage,
            )

    if "tuned_thresholds" in normalized and normalized["tuned_thresholds"] is not None:
        if not isinstance(normalized["tuned_thresholds"], dict):
            raise S4ConfidenceCoreError(
                code="INVALID_TUNED_THRESHOLDS",
                message="tuned_thresholds deve ser objeto com auto_approve/manual_review/gap",
                action=(
                    "Retorne tuned_thresholds como dict com chaves auto_approve, "
                    "manual_review e gap."
                ),
                correlation_id=correlation_id,
                stage=stage,
            )
        _resolve_tuned_thresholds(
            base_thresholds=thresholds,
            response_tuned_thresholds=normalized["tuned_thresholds"],
            max_threshold_delta=max_threshold_delta,
            correlation_id=correlation_id,
            stage=stage,
        )

    return normalized


def _resolve_tuned_thresholds(
    *,
    base_thresholds: dict[str, float],
    response_tuned_thresholds: dict[str, Any] | None,
    max_threshold_delta: float,
    correlation_id: str,
    stage: str,
) -> dict[str, float]:
    source = response_tuned_thresholds if response_tuned_thresholds is not None else base_thresholds
    if not isinstance(source, dict):
        raise S4ConfidenceCoreError(
            code="INVALID_TUNED_THRESHOLDS",
            message="tuned_thresholds deve ser objeto com auto_approve/manual_review/gap",
            action=(
                "Retorne tuned_thresholds como dict com chaves auto_approve, "
                "manual_review e gap."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    tuned_thresholds: dict[str, float] = {}
    for key in ("auto_approve", "manual_review", "gap"):
        raw_value = source.get(key, base_thresholds.get(key))
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
            raise S4ConfidenceCoreError(
                code="INVALID_TUNED_THRESHOLD_VALUE",
                message=f"Valor invalido para tuned_thresholds.{key}: {raw_value}",
                action=(
                    "Retorne tuned_thresholds com valores numericos entre 0.0 e 1.0 "
                    "para auto_approve/manual_review/gap."
                ),
                correlation_id=correlation_id,
                stage=stage,
            )

        tuned_value = float(raw_value)
        if tuned_value < MIN_SCORE or tuned_value > MAX_SCORE:
            raise S4ConfidenceCoreError(
                code="INVALID_TUNED_THRESHOLD_RANGE",
                message=f"tuned_thresholds.{key} fora do intervalo permitido: {raw_value}",
                action=f"Ajuste tuned_thresholds.{key} para valor entre 0.0 e 1.0.",
                correlation_id=correlation_id,
                stage=stage,
            )

        base_value = float(base_thresholds.get(key, tuned_value))
        if abs(tuned_value - base_value) > max_threshold_delta:
            raise S4ConfidenceCoreError(
                code="THRESHOLD_DELTA_EXCEEDS_LIMIT",
                message=(
                    f"Ajuste de tuned_thresholds.{key} excede max_threshold_delta: "
                    f"|{tuned_value} - {base_value}| > {max_threshold_delta}"
                ),
                action=(
                    "Reduza diferenca entre tuned_thresholds e thresholds originais "
                    "para ficar dentro de max_threshold_delta."
                ),
                correlation_id=correlation_id,
                stage=stage,
            )

        tuned_thresholds[key] = round(tuned_value, 6)

    if not (
        tuned_thresholds["gap"] <= tuned_thresholds["manual_review"] <= tuned_thresholds["auto_approve"]
    ):
        raise S4ConfidenceCoreError(
            code="INVALID_TUNED_THRESHOLDS",
            message=(
                "limiares ajustados invalidos: esperado gap <= manual_review <= auto_approve"
            ),
            action="Ajuste tuned_thresholds para manter ordem de decisao auto/review/gap.",
            correlation_id=correlation_id,
            stage=stage,
        )

    return tuned_thresholds


def _normalize_non_negative_int(
    *,
    field_name: str,
    value: Any,
    correlation_id: str,
    stage: str,
) -> int:
    if isinstance(value, bool):
        raise S4ConfidenceCoreError(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} invalido: valor booleano nao permitido",
            action=f"Retorne {field_name} como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if isinstance(value, float) and not value.is_integer():
        raise S4ConfidenceCoreError(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} invalido: {value}",
            action=f"Retorne {field_name} como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if not isinstance(value, (int, float)):
        raise S4ConfidenceCoreError(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} invalido: {value}",
            action=f"Retorne {field_name} como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = int(value)
    if normalized < 0:
        raise S4ConfidenceCoreError(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} invalido: {value}",
            action=f"Retorne {field_name} como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    return normalized


def _normalize_probability(
    *,
    field_name: str,
    value: Any,
    correlation_id: str,
    stage: str,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise S4ConfidenceCoreError(
            code="INVALID_NUMERIC_VALUE",
            message=f"{field_name} invalido: {value}",
            action=f"Retorne {field_name} como valor numerico entre 0.0 e 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = float(value)
    if normalized < MIN_SCORE or normalized > MAX_SCORE:
        raise S4ConfidenceCoreError(
            code="INVALID_NUMERIC_RANGE",
            message=f"{field_name} fora do intervalo permitido: {value}",
            action=f"Ajuste {field_name} para valor entre 0.0 e 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    return round(normalized, 6)


def _derive_decision(
    *,
    confidence_score: float,
    auto_approve_threshold: float,
    manual_review_threshold: float,
    gap_threshold: float,
) -> str:
    if confidence_score >= auto_approve_threshold:
        return "auto_approve"
    if confidence_score >= manual_review_threshold:
        return "manual_review"
    if confidence_score >= gap_threshold:
        return "gap"
    return "reject"


def _default_threshold_adjuster(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one CONF Sprint 4 threshold-adjustment pass in dry-run mode.

    Args:
        context: Structured adjustment context with policy metadata and
            threshold-calibration guardrails.

    Returns:
        dict[str, Any]: Dry-run threshold-adjustment result.
    """

    field_weights_count = int(context.get("field_weights_count", 0))
    missing_field_penalty = float(context.get("missing_field_penalty", 0.0))
    auto_approve_threshold = float(context.get("auto_approve_threshold", 0.85))
    manual_review_threshold = float(context.get("manual_review_threshold", 0.60))
    gap_threshold = float(context.get("gap_threshold", 0.40))

    critical_fields_count = int(context.get("critical_fields_count", 0))
    min_feedback_samples = int(context.get("min_feedback_samples", 0))

    base_score = 0.90 if field_weights_count > 0 else 0.70
    confidence_score = max(MIN_SCORE, min(MAX_SCORE, base_score - missing_field_penalty))
    decision = _derive_decision(
        confidence_score=confidence_score,
        auto_approve_threshold=auto_approve_threshold,
        manual_review_threshold=manual_review_threshold,
        gap_threshold=gap_threshold,
    )

    return {
        "status": "succeeded",
        "confidence_score": round(confidence_score, 6),
        "decision": decision,
        "decision_reason": "dry_run_confidence_threshold_adjustment",
        "decision_result_id": f"confs4decision-{uuid4().hex[:12]}",
        "manual_review_queue_size": 0,
        "critical_fields_present_count": critical_fields_count,
        "feedback_samples_count": max(0, min_feedback_samples),
        "threshold_delta_applied": 0.0,
        "tuned_thresholds": {
            "auto_approve": round(auto_approve_threshold, 6),
            "manual_review": round(manual_review_threshold, 6),
            "gap": round(gap_threshold, 6),
        },
        "quality_drop_value": 0.0,
        "quality_drop_detected": False,
        "anomaly_detected": False,
        "calibration_frozen": False,
    }


def _new_event_id() -> str:
    return f"confs4coreevt-{uuid4().hex[:12]}"
