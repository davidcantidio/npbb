"""Validation contracts for CONF Sprint 4 threshold tuning flow.

This module centralizes CONF Sprint 4 input/output validation used by tests
and integration checks. It provides structured actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s4_core import S4ConfidenceCoreInput
from .s4_observability import (
    S4ConfidenceObservabilityInput,
    build_s4_confidence_observability_event,
    log_s4_confidence_observability_event,
)
from .s4_scaffold import (
    S4ConfidenceScaffoldError,
    S4ConfidenceScaffoldRequest,
    build_s4_confidence_scaffold,
)


logger = logging.getLogger("npbb.core.confidence.s4.validation")

CONF_S4_VALIDATION_VERSION = "conf.s4.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}
ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}
ALLOWED_CRITICAL_VIOLATION_ROUTES = {"manual_review", "gap", "reject"}


class S4ConfidenceValidationError(ValueError):
    """Raised when CONF Sprint 4 validation contract is violated."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        stage: str,
        observability_event_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.stage = stage
        self.observability_event_id = observability_event_id

    def to_dict(self) -> dict[str, str]:
        """Return serializable actionable diagnostics payload."""

        payload = {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "stage": self.stage,
        }
        if self.observability_event_id:
            payload["observability_event_id"] = self.observability_event_id
        return payload


@dataclass(frozen=True, slots=True)
class S4ConfidenceValidationInput:
    """Input contract consumed by CONF Sprint 4 validation checks."""

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

    def to_core_input(self, *, correlation_id: str | None = None) -> S4ConfidenceCoreInput:
        """Convert validated data to `S4ConfidenceCoreInput` contract."""

        return S4ConfidenceCoreInput(
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
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S4ConfidenceScaffoldRequest:
        """Convert validated data to `S4ConfidenceScaffoldRequest` contract."""

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
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4ConfidenceValidationResult:
    """Output contract returned by CONF Sprint 4 input validation."""

    validation_version: str
    validation_id: str
    correlation_id: str
    status: str
    checks: tuple[str, ...]
    route_preview: str
    observabilidade: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checks": list(self.checks),
            "route_preview": self.route_preview,
            "observabilidade": self.observabilidade,
        }


@dataclass(frozen=True, slots=True)
class S4ConfidenceFlowOutputValidationResult:
    """Output contract returned by CONF Sprint 4 flow-output validation."""

    correlation_id: str
    status: str
    layer: str
    checked_fields: tuple[str, ...]
    observabilidade: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "correlation_id": self.correlation_id,
            "status": self.status,
            "layer": self.layer,
            "checked_fields": list(self.checked_fields),
            "observabilidade": self.observabilidade,
        }


def validate_s4_confidence_input_contract(
    payload: S4ConfidenceValidationInput,
) -> S4ConfidenceValidationResult:
    """Validate CONF Sprint 4 input contract before running the main flow.

    Args:
        payload: Input contract with policy metadata, critical-field rules,
            and threshold-adjustment guardrails.

    Returns:
        S4ConfidenceValidationResult: Validation metadata and checks summary.

    Raises:
        S4ConfidenceValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"conf-s4-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="confidence_policy_s4_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do CONF S4 iniciada",
        severity="info",
        policy_id=payload.policy_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        decision_mode=payload.decision_mode,
        stage="validation_input",
    )
    checks: list[str] = []

    if not payload.policy_id.strip():
        _raise_validation_error(
            code="EMPTY_POLICY_ID",
            message="policy_id nao pode ser vazio",
            action="Informe identificador da politica de confianca antes de iniciar a validacao.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("policy_id")

    if not payload.dataset_name.strip():
        _raise_validation_error(
            code="EMPTY_DATASET_NAME",
            message="dataset_name nao pode ser vazio",
            action="Informe dataset_name para rastreabilidade da politica de confianca.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("dataset_name")

    if not payload.entity_kind.strip():
        _raise_validation_error(
            code="EMPTY_ENTITY_KIND",
            message="entity_kind nao pode ser vazio",
            action="Informe entity_kind para aplicar regras de decisao da sprint.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("entity_kind")

    if not payload.decision_mode.strip():
        _raise_validation_error(
            code="EMPTY_DECISION_MODE",
            message="decision_mode nao pode ser vazio",
            action="Informe decision_mode conforme politica de decisao da sprint.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("decision_mode")

    if payload.field_weights is not None and not isinstance(payload.field_weights, dict):
        _raise_validation_error(
            code="INVALID_FIELD_WEIGHTS_TYPE",
            message="field_weights deve ser dicionario no formato campo->peso",
            action="Informe field_weights como objeto com chaves de campo e pesos numericos.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"field_weights_type": type(payload.field_weights).__name__},
        )
    checks.append("field_weights")

    if not isinstance(payload.gap_escalation_required, bool):
        _raise_validation_error(
            code="INVALID_GAP_ESCALATION_REQUIRED_TYPE",
            message="gap_escalation_required deve ser booleano",
            action="Ajuste gap_escalation_required para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"gap_escalation_required": payload.gap_escalation_required},
        )
    checks.append("gap_escalation_required")

    if isinstance(payload.max_manual_review_queue, bool) or not isinstance(
        payload.max_manual_review_queue,
        int,
    ):
        _raise_validation_error(
            code="INVALID_MAX_MANUAL_REVIEW_QUEUE_TYPE",
            message="max_manual_review_queue deve ser inteiro",
            action="Ajuste max_manual_review_queue para inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"max_manual_review_queue": payload.max_manual_review_queue},
        )
    if payload.max_manual_review_queue < 0:
        _raise_validation_error(
            code="INVALID_MAX_MANUAL_REVIEW_QUEUE",
            message="max_manual_review_queue deve ser >= 0",
            action="Ajuste max_manual_review_queue para inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"max_manual_review_queue": payload.max_manual_review_queue},
        )
    checks.append("max_manual_review_queue")

    if payload.critical_fields is not None and not isinstance(payload.critical_fields, tuple):
        _raise_validation_error(
            code="INVALID_CRITICAL_FIELDS_TYPE",
            message="critical_fields deve ser tupla de campos",
            action="Informe critical_fields como tuple[str, ...] com nomes validos.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"critical_fields_type": type(payload.critical_fields).__name__},
        )
    checks.append("critical_fields")

    if isinstance(payload.min_critical_fields_present, bool) or not isinstance(
        payload.min_critical_fields_present,
        int,
    ):
        _raise_validation_error(
            code="INVALID_MIN_CRITICAL_FIELDS_PRESENT_TYPE",
            message="min_critical_fields_present deve ser inteiro",
            action="Ajuste min_critical_fields_present para inteiro >= 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"min_critical_fields_present": payload.min_critical_fields_present},
        )
    if payload.min_critical_fields_present < 1:
        _raise_validation_error(
            code="INVALID_MIN_CRITICAL_FIELDS_PRESENT",
            message="min_critical_fields_present deve ser >= 1",
            action="Ajuste min_critical_fields_present para inteiro >= 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"min_critical_fields_present": payload.min_critical_fields_present},
        )
    checks.append("min_critical_fields_present")

    critical_violation_route = payload.critical_violation_route.strip().lower()
    if critical_violation_route not in ALLOWED_CRITICAL_VIOLATION_ROUTES:
        _raise_validation_error(
            code="INVALID_CRITICAL_VIOLATION_ROUTE",
            message=f"critical_violation_route invalido: {payload.critical_violation_route}",
            action="Use critical_violation_route valido: manual_review, gap ou reject.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"critical_violation_route": payload.critical_violation_route},
        )
    checks.append("critical_violation_route")

    if not isinstance(payload.critical_override_required, bool):
        _raise_validation_error(
            code="INVALID_CRITICAL_OVERRIDE_REQUIRED_TYPE",
            message="critical_override_required deve ser booleano",
            action="Ajuste critical_override_required para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"critical_override_required": payload.critical_override_required},
        )
    checks.append("critical_override_required")

    if isinstance(payload.feedback_window_days, bool) or not isinstance(payload.feedback_window_days, int):
        _raise_validation_error(
            code="INVALID_FEEDBACK_WINDOW_DAYS_TYPE",
            message="feedback_window_days deve ser inteiro",
            action="Ajuste feedback_window_days para inteiro >= 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"feedback_window_days": payload.feedback_window_days},
        )
    if payload.feedback_window_days < 1:
        _raise_validation_error(
            code="INVALID_FEEDBACK_WINDOW_DAYS",
            message="feedback_window_days deve ser >= 1",
            action="Ajuste feedback_window_days para inteiro >= 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"feedback_window_days": payload.feedback_window_days},
        )
    checks.append("feedback_window_days")

    if isinstance(payload.min_feedback_samples, bool) or not isinstance(payload.min_feedback_samples, int):
        _raise_validation_error(
            code="INVALID_MIN_FEEDBACK_SAMPLES_TYPE",
            message="min_feedback_samples deve ser inteiro",
            action="Ajuste min_feedback_samples para inteiro >= 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"min_feedback_samples": payload.min_feedback_samples},
        )
    if payload.min_feedback_samples < 1:
        _raise_validation_error(
            code="INVALID_MIN_FEEDBACK_SAMPLES",
            message="min_feedback_samples deve ser >= 1",
            action="Ajuste min_feedback_samples para inteiro >= 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"min_feedback_samples": payload.min_feedback_samples},
        )
    checks.append("min_feedback_samples")

    if not isinstance(payload.auto_threshold_tuning_enabled, bool):
        _raise_validation_error(
            code="INVALID_AUTO_THRESHOLD_TUNING_ENABLED_TYPE",
            message="auto_threshold_tuning_enabled deve ser booleano",
            action="Ajuste auto_threshold_tuning_enabled para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"auto_threshold_tuning_enabled": payload.auto_threshold_tuning_enabled},
        )
    checks.append("auto_threshold_tuning_enabled")

    for field_name, value in (
        ("max_threshold_delta", payload.max_threshold_delta),
        ("quality_drop_tolerance", payload.quality_drop_tolerance),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _raise_validation_error(
                code="INVALID_NUMERIC_GUARDRAIL",
                message=f"{field_name} deve ser numerico",
                action=f"Ajuste {field_name} para valor numerico entre 0.0 e 1.0.",
                correlation_id=correlation_id,
                stage="validation_input",
                context={field_name: value},
            )
    checks.append("threshold_guardrails")

    if not isinstance(payload.calibration_freeze_on_anomaly, bool):
        _raise_validation_error(
            code="INVALID_CALIBRATION_FREEZE_ON_ANOMALY_TYPE",
            message="calibration_freeze_on_anomaly deve ser booleano",
            action="Ajuste calibration_freeze_on_anomaly para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"calibration_freeze_on_anomaly": payload.calibration_freeze_on_anomaly},
        )
    checks.append("calibration_freeze_on_anomaly")

    try:
        scaffold = build_s4_confidence_scaffold(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S4ConfidenceScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "entity_kind": payload.entity_kind,
                "schema_version": payload.schema_version,
                "decision_mode": payload.decision_mode,
                "auto_threshold_tuning_enabled": payload.auto_threshold_tuning_enabled,
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="confidence_policy_s4_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do CONF S4 concluida com sucesso",
        severity="info",
        policy_id=scaffold.policy_id,
        dataset_name=scaffold.dataset_name,
        entity_kind=scaffold.decision_policy.get("entity_kind"),
        schema_version=scaffold.decision_policy.get("schema_version"),
        decision_mode=scaffold.decision_policy.get("decision_mode"),
        max_manual_review_queue=(
            scaffold.decision_policy.get("operational_policy", {}).get("max_manual_review_queue")
        ),
        min_critical_fields_present=(
            scaffold.decision_policy.get("critical_fields_policy", {}).get(
                "min_critical_fields_present"
            )
        ),
        critical_violation_route=(
            scaffold.decision_policy.get("critical_fields_policy", {}).get(
                "critical_violation_route"
            )
        ),
        feedback_samples_count=(
            scaffold.decision_policy.get("threshold_calibration_policy", {}).get(
                "min_feedback_samples"
            )
        ),
        min_feedback_samples=(
            scaffold.decision_policy.get("threshold_calibration_policy", {}).get(
                "min_feedback_samples"
            )
        ),
        threshold_delta_applied=(
            scaffold.decision_policy.get("threshold_calibration_policy", {}).get(
                "max_threshold_delta"
            )
        ),
        quality_drop_value=(
            scaffold.decision_policy.get("threshold_calibration_policy", {}).get(
                "quality_drop_tolerance"
            )
        ),
        calibration_frozen=(
            scaffold.decision_policy.get("threshold_calibration_policy", {}).get(
                "calibration_freeze_on_anomaly"
            )
        ),
        stage="validation_input",
        context={
            "checks": checks,
            "field_weights_count": scaffold.decision_policy.get("field_weights_count"),
            "critical_fields_count": scaffold.decision_policy.get("critical_fields_policy", {}).get(
                "critical_fields_count"
            ),
        },
    )

    validation_id = f"confval-{uuid4().hex[:12]}"
    logger.info(
        "confidence_policy_s4_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "confidence_policy_s4_threshold_tuning",
        },
    )
    return S4ConfidenceValidationResult(
        validation_version=CONF_S4_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="confidence_policy_s4_threshold_tuning",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_s4_confidence_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S4ConfidenceFlowOutputValidationResult:
    """Validate CONF Sprint 4 flow output contract.

    Args:
        flow_output: Output dictionary produced by CONF S4 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S4ConfidenceFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S4ConfidenceValidationError: If output contract is incomplete or
            inconsistent with CONF Sprint 4 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "policy_id",
        "dataset_name",
        "decision_policy",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo CONF S4 incompleta: faltam campos {missing_fields}",
            action="Atualize o fluxo para retornar o contrato completo da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"missing_fields": ",".join(missing_fields)},
        )

    contract_version = str(flow_output.get("contrato_versao", "")).strip()
    layer, required_obs = _resolve_output_layer(
        contract_version=contract_version,
        correlation_id=correlation_id,
    )

    status = str(flow_output.get("status", "")).lower()
    if status not in ALLOWED_FLOW_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo CONF S4: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do CONF S4.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"status": str(flow_output.get("status", ""))},
        )

    if str(flow_output.get("correlation_id", "")).strip() != correlation_id.strip():
        _raise_validation_error(
            code="CORRELATION_ID_MISMATCH",
            message="correlation_id divergente entre chamada e payload de saida",
            action="Propague correlation_id estavel em todo o fluxo da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"output_correlation_id": str(flow_output.get("correlation_id", ""))},
        )

    execucao = flow_output.get("execucao", {})
    exec_status = str(execucao.get("status", "")).lower()
    if exec_status not in ALLOWED_EXEC_STATUSES:
        _raise_validation_error(
            code="INVALID_EXECUTION_STATUS",
            message=f"status de execucao invalido na saida: {execucao.get('status')}",
            action="Use status de execucao valido: succeeded/completed/success.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"exec_status": str(execucao.get("status", ""))},
        )

    decision_result_id = str(execucao.get("decision_result_id", "")).strip()
    if not decision_result_id:
        _raise_validation_error(
            code="MISSING_DECISION_RESULT_ID",
            message="decision_result_id ausente na saida de execucao",
            action="Propague decision_result_id para rastreabilidade da decisao de confianca.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    decision = str(execucao.get("decision", "")).strip().lower()
    if decision not in ALLOWED_DECISIONS:
        _raise_validation_error(
            code="INVALID_DECISION",
            message=f"decisao invalida na saida: {execucao.get('decision')}",
            action="Use decisao valida: auto_approve, manual_review, gap ou reject.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"decision": str(execucao.get("decision", ""))},
        )

    confidence_score = execucao.get("confidence_score")
    if isinstance(confidence_score, bool) or not isinstance(confidence_score, (int, float)):
        _raise_validation_error(
            code="INVALID_CONFIDENCE_SCORE",
            message=f"confidence_score invalido na saida: {confidence_score}",
            action="Retorne confidence_score numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"confidence_score": str(confidence_score)},
        )
    if float(confidence_score) < 0.0 or float(confidence_score) > 1.0:
        _raise_validation_error(
            code="CONFIDENCE_SCORE_OUT_OF_RANGE",
            message=f"confidence_score fora do intervalo permitido: {confidence_score}",
            action="Retorne confidence_score no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"confidence_score": str(confidence_score)},
        )

    manual_review_queue_size = execucao.get("manual_review_queue_size")
    if isinstance(manual_review_queue_size, bool) or not isinstance(manual_review_queue_size, int):
        _raise_validation_error(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=f"manual_review_queue_size invalido na saida: {manual_review_queue_size}",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"manual_review_queue_size": str(manual_review_queue_size)},
        )
    if manual_review_queue_size < 0:
        _raise_validation_error(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=f"manual_review_queue_size invalido na saida: {manual_review_queue_size}",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"manual_review_queue_size": str(manual_review_queue_size)},
        )

    critical_fields_present_count = execucao.get("critical_fields_present_count")
    if isinstance(critical_fields_present_count, bool) or not isinstance(
        critical_fields_present_count,
        int,
    ):
        _raise_validation_error(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count invalido na saida: "
                f"{critical_fields_present_count}"
            ),
            action="Retorne critical_fields_present_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"critical_fields_present_count": str(critical_fields_present_count)},
        )
    if critical_fields_present_count < 0:
        _raise_validation_error(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count invalido na saida: "
                f"{critical_fields_present_count}"
            ),
            action="Retorne critical_fields_present_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"critical_fields_present_count": str(critical_fields_present_count)},
        )

    critical_violation_triggered = execucao.get("critical_violation_triggered")
    if not isinstance(critical_violation_triggered, bool):
        _raise_validation_error(
            code="INVALID_CRITICAL_VIOLATION_TRIGGERED",
            message=(
                "critical_violation_triggered invalido na saida: "
                f"{critical_violation_triggered}"
            ),
            action="Retorne critical_violation_triggered como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"critical_violation_triggered": str(critical_violation_triggered)},
        )

    gap_escalation_triggered = execucao.get("gap_escalation_triggered")
    if not isinstance(gap_escalation_triggered, bool):
        _raise_validation_error(
            code="INVALID_GAP_ESCALATION_TRIGGERED",
            message=(
                "gap_escalation_triggered invalido na saida: "
                f"{gap_escalation_triggered}"
            ),
            action="Retorne gap_escalation_triggered como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"gap_escalation_triggered": str(gap_escalation_triggered)},
        )

    feedback_samples_count = execucao.get("feedback_samples_count")
    if isinstance(feedback_samples_count, bool) or not isinstance(feedback_samples_count, int):
        _raise_validation_error(
            code="INVALID_FEEDBACK_SAMPLES_COUNT",
            message=f"feedback_samples_count invalido na saida: {feedback_samples_count}",
            action="Retorne feedback_samples_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"feedback_samples_count": str(feedback_samples_count)},
        )
    if feedback_samples_count < 0:
        _raise_validation_error(
            code="INVALID_FEEDBACK_SAMPLES_COUNT",
            message=f"feedback_samples_count invalido na saida: {feedback_samples_count}",
            action="Retorne feedback_samples_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"feedback_samples_count": str(feedback_samples_count)},
        )

    threshold_delta_applied = execucao.get("threshold_delta_applied")
    if isinstance(threshold_delta_applied, bool) or not isinstance(
        threshold_delta_applied,
        (int, float),
    ):
        _raise_validation_error(
            code="INVALID_THRESHOLD_DELTA_APPLIED",
            message=f"threshold_delta_applied invalido na saida: {threshold_delta_applied}",
            action="Retorne threshold_delta_applied como numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"threshold_delta_applied": str(threshold_delta_applied)},
        )
    if float(threshold_delta_applied) < 0.0 or float(threshold_delta_applied) > 1.0:
        _raise_validation_error(
            code="INVALID_THRESHOLD_DELTA_APPLIED",
            message=f"threshold_delta_applied fora do intervalo permitido: {threshold_delta_applied}",
            action="Retorne threshold_delta_applied como numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"threshold_delta_applied": str(threshold_delta_applied)},
        )

    tuned_thresholds = execucao.get("tuned_thresholds")
    if not isinstance(tuned_thresholds, dict):
        _raise_validation_error(
            code="INVALID_TUNED_THRESHOLDS",
            message=f"tuned_thresholds invalido na saida: {tuned_thresholds}",
            action=(
                "Retorne tuned_thresholds como objeto com auto_approve, manual_review e gap "
                "no intervalo de 0.0 a 1.0."
            ),
            correlation_id=correlation_id,
            stage="validation_output",
            context={"tuned_thresholds": str(tuned_thresholds)},
        )
    for key in ("auto_approve", "manual_review", "gap"):
        value = tuned_thresholds.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _raise_validation_error(
                code="INVALID_TUNED_THRESHOLDS",
                message=f"tuned_thresholds.{key} invalido na saida: {value}",
                action="Retorne tuned_thresholds com valores numericos entre 0.0 e 1.0.",
                correlation_id=correlation_id,
                stage="validation_output",
                context={"threshold_key": key, "threshold_value": str(value)},
            )
        if float(value) < 0.0 or float(value) > 1.0:
            _raise_validation_error(
                code="INVALID_TUNED_THRESHOLDS",
                message=f"tuned_thresholds.{key} fora do intervalo permitido: {value}",
                action="Retorne tuned_thresholds com valores numericos entre 0.0 e 1.0.",
                correlation_id=correlation_id,
                stage="validation_output",
                context={"threshold_key": key, "threshold_value": str(value)},
            )
    if not (
        float(tuned_thresholds["gap"])
        <= float(tuned_thresholds["manual_review"])
        <= float(tuned_thresholds["auto_approve"])
    ):
        _raise_validation_error(
            code="INVALID_TUNED_THRESHOLDS",
            message="tuned_thresholds invalido: esperado gap <= manual_review <= auto_approve",
            action="Ajuste tuned_thresholds para manter ordem de decisao auto/review/gap.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"tuned_thresholds": str(tuned_thresholds)},
        )

    quality_drop_value = execucao.get("quality_drop_value")
    if isinstance(quality_drop_value, bool) or not isinstance(quality_drop_value, (int, float)):
        _raise_validation_error(
            code="INVALID_QUALITY_DROP_VALUE",
            message=f"quality_drop_value invalido na saida: {quality_drop_value}",
            action="Retorne quality_drop_value como numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"quality_drop_value": str(quality_drop_value)},
        )
    if float(quality_drop_value) < 0.0 or float(quality_drop_value) > 1.0:
        _raise_validation_error(
            code="INVALID_QUALITY_DROP_VALUE",
            message=f"quality_drop_value fora do intervalo permitido: {quality_drop_value}",
            action="Retorne quality_drop_value como numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"quality_drop_value": str(quality_drop_value)},
        )

    for field_name in (
        "quality_drop_detected",
        "anomaly_detected",
        "calibration_frozen",
    ):
        field_value = execucao.get(field_name)
        if not isinstance(field_value, bool):
            _raise_validation_error(
                code="INVALID_EXECUTION_BOOLEAN_FLAG",
                message=f"{field_name} invalido na saida: {field_value}",
                action=f"Retorne {field_name} como booleano.",
                correlation_id=correlation_id,
                stage="validation_output",
                context={field_name: str(field_value)},
            )

    if critical_violation_triggered and decision not in ALLOWED_CRITICAL_VIOLATION_ROUTES:
        _raise_validation_error(
            code="INVALID_CRITICAL_VIOLATION_DECISION",
            message=f"decisao invalida para violacao critica: {decision}",
            action="Use decisao de violacao critica valida: manual_review, gap ou reject.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"decision": decision},
        )

    observabilidade = flow_output.get("observabilidade", {})
    for field, prefix in required_obs.items():
        value = str(observabilidade.get(field, ""))
        if not value.startswith(prefix):
            _raise_validation_error(
                code="INVALID_OBSERVABILITY_OUTPUT",
                message=f"Campo de observabilidade invalido: {field}",
                action=f"Propague IDs de observabilidade com prefixo {prefix}.",
                correlation_id=correlation_id,
                stage="validation_output",
                context={"field": field, "value": value, "expected_prefix": prefix},
            )

    logger.info(
        "confidence_policy_s4_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "policy_id": str(flow_output.get("policy_id", "")),
        },
    )
    return S4ConfidenceFlowOutputValidationResult(
        correlation_id=correlation_id,
        status="valid",
        layer=layer,
        checked_fields=required_fields,
        observabilidade={field: str(observabilidade[field]) for field in required_obs},
    )


def _resolve_output_layer(
    *,
    contract_version: str,
    correlation_id: str,
) -> tuple[str, dict[str, str]]:
    if contract_version == "conf.s4.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "confs4coreevt-",
                "flow_completed_event_id": "confs4coreevt-",
            },
        )
    if contract_version == "conf.s4.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "confs4evt-",
                "policy_profile_ready_event_id": "confs4evt-",
                "flow_completed_event_id": "confs4evt-",
                "main_flow_started_event_id": "confs4coreevt-",
                "main_flow_completed_event_id": "confs4coreevt-",
            },
        )
    raise S4ConfidenceValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos conf.s4.core.v1 ou conf.s4.service.v1.",
        correlation_id=correlation_id,
        stage="validation_output",
    )


def _raise_validation_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> None:
    failed_event = _emit_observability_event(
        event_name="confidence_policy_s4_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "confidence_policy_s4_validation_error",
        extra={
            "correlation_id": correlation_id,
            "error_code": code,
            "error_message": message,
            "action": action,
            "stage": stage,
            "context": context or {},
            "observability_event_id": failed_event.observability_event_id,
        },
    )
    raise S4ConfidenceValidationError(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        stage=stage,
        observability_event_id=failed_event.observability_event_id,
    )


def _emit_observability_event(
    *,
    event_name: str,
    correlation_id: str,
    event_message: str,
    severity: str,
    stage: str,
    policy_id: str | None = None,
    dataset_name: str | None = None,
    entity_kind: str | None = None,
    schema_version: str | None = None,
    decision_mode: str | None = None,
    confidence_score: float | None = None,
    decision: str | None = None,
    manual_review_queue_size: int | None = None,
    max_manual_review_queue: int | None = None,
    gap_escalation_triggered: bool | None = None,
    critical_fields_present_count: int | None = None,
    min_critical_fields_present: int | None = None,
    critical_violation_triggered: bool | None = None,
    critical_violation_route: str | None = None,
    feedback_samples_count: int | None = None,
    min_feedback_samples: int | None = None,
    threshold_delta_applied: float | None = None,
    tuned_thresholds: dict[str, float] | None = None,
    quality_drop_value: float | None = None,
    quality_drop_detected: bool | None = None,
    anomaly_detected: bool | None = None,
    calibration_frozen: bool | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S4ConfidenceObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        policy_id=policy_id,
        dataset_name=dataset_name,
        entity_kind=entity_kind,
        schema_version=schema_version,
        decision_mode=decision_mode,
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
        stage=stage,
        context=context,
    )
    event = build_s4_confidence_observability_event(payload)
    log_s4_confidence_observability_event(event)
    return event
