"""Main flow for CONF Sprint 3 critical-field confidence decision policy.

This module executes the Sprint 3 core path:
1) validate input and resolve Sprint 3 scaffold policy;
2) execute one confidence decision pass with critical-field rules;
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s3_scaffold import (
    S3ConfidenceScaffoldError,
    S3ConfidenceScaffoldRequest,
    build_s3_confidence_scaffold,
)


logger = logging.getLogger("npbb.core.confidence.s3.core")

CONTRACT_VERSION = "conf.s3.core.v1"
CONF_S3_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONF_S3_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONF_S3_ALLOWED_EXEC_STATUSES = CONF_S3_SUCCESS_STATUSES | CONF_S3_FAILED_STATUSES
CONF_S3_ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}

MIN_SCORE = 0.0
MAX_SCORE = 1.0


class S3ConfidenceCoreError(RuntimeError):
    """Raised when CONF Sprint 3 core flow fails."""

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
class S3ConfidenceCoreInput:
    """Input contract consumed by CONF Sprint 3 core flow."""

    policy_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v3"
    owner_team: str = "etl"
    field_weights: dict[str, float] | None = None
    default_weight: float = 1.0
    auto_approve_threshold: float = 0.85
    manual_review_threshold: float = 0.60
    gap_threshold: float = 0.40
    missing_field_penalty: float = 0.10
    decision_mode: str = "critical_fields_guardrails"
    gap_escalation_required: bool = True
    max_manual_review_queue: int = 500
    critical_fields: tuple[str, ...] | None = None
    min_critical_fields_present: int = 1
    critical_field_penalty: float = 0.20
    critical_violation_route: str = "manual_review"
    critical_override_required: bool = True
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S3ConfidenceScaffoldRequest:
        """Build scaffold request using CONF Sprint 3 stable fields."""

        return S3ConfidenceScaffoldRequest(
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
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3ConfidenceCoreOutput:
    """Output contract returned by CONF Sprint 3 core flow."""

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


def execute_s3_confidence_policy_main_flow(
    flow_input: S3ConfidenceCoreInput,
    *,
    execute_decision: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S3ConfidenceCoreOutput:
    """Execute CONF Sprint 3 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with critical-field rules and decision
            thresholds for Sprint 3 confidence policy.
        execute_decision: Optional callback responsible for one decision
            execution. It receives an execution context and must return a
            dictionary with `status` and `confidence_score` fields.

    Returns:
        S3ConfidenceCoreOutput: Stable output with decision policy,
            execution diagnostics, and observability identifiers.

    Raises:
        S3ConfidenceCoreError: If scaffold validation fails, execution response
            is invalid, or decision execution fails.
    """

    correlation_id = flow_input.correlation_id or f"conf-s3-{uuid4().hex[:12]}"
    decision_executor = execute_decision or _default_decision_executor
    started_event_id = _new_event_id()
    logger.info(
        "confidence_policy_s3_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": flow_input.policy_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "decision_mode": flow_input.decision_mode,
            "critical_violation_route": flow_input.critical_violation_route,
        },
    )

    try:
        scaffold = build_s3_confidence_scaffold(
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

        decision_context = {
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
        }

        response = decision_executor(decision_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="decision_engine",
            max_critical_fields_count=critical_fields_count,
        )
        status = normalized["status"]
        confidence_score = float(normalized["confidence_score"])
        manual_review_queue_size = int(normalized.get("manual_review_queue_size", 0))
        critical_fields_present_count = int(
            normalized.get("critical_fields_present_count", critical_fields_count)
        )

        decision = str(normalized.get("decision") or "").strip().lower()
        if not decision:
            decision = _derive_decision(
                confidence_score=confidence_score,
                auto_approve_threshold=auto_approve_threshold,
                manual_review_threshold=manual_review_threshold,
                gap_threshold=gap_threshold,
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

        if decision not in CONF_S3_ALLOWED_DECISIONS:
            raise S3ConfidenceCoreError(
                code="INVALID_CONFIDENCE_DECISION",
                message=f"Decisao de confianca invalida: {decision}",
                action="Retorne decisao valida: auto_approve, manual_review, gap ou reject.",
                correlation_id=correlation_id,
                stage="decision_engine",
            )

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

        completed_event_id = _new_event_id()
        logger.info(
            "confidence_policy_s3_main_flow_completed",
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
                "min_critical_fields_present": min_critical_fields_present,
                "critical_violation_triggered": critical_violation_triggered,
                "gap_escalation_triggered": gap_escalation_triggered,
            },
        )

        if status not in CONF_S3_SUCCESS_STATUSES:
            raise S3ConfidenceCoreError(
                code="CONF_S3_DECISION_EXECUTION_FAILED",
                message=f"Execucao de decisao CONF S3 falhou com status '{status}'",
                action=(
                    "Revisar logs do executor de decisao e conferir regras de campos criticos/"
                    "limiares da politica da sprint."
                ),
                correlation_id=correlation_id,
                stage="decision_engine",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["confidence_policy_core_module"] = (
            "core.confidence.s3_core.execute_s3_confidence_policy_main_flow"
        )

        return S3ConfidenceCoreOutput(
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
                "decision_reason": str(normalized.get("decision_reason", "dry_run_main_flow")),
                "decision_result_id": str(normalized.get("decision_result_id", "")),
                "manual_review_queue_size": manual_review_queue_size,
                "critical_fields_present_count": critical_fields_present_count,
                "critical_violation_triggered": critical_violation_triggered,
                "gap_escalation_triggered": gap_escalation_triggered,
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S3ConfidenceScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "confidence_policy_s3_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S3ConfidenceCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S3ConfidenceCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "confidence_policy_s3_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3ConfidenceCoreError(
            code="CONF_S3_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONF S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONF S3.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
    max_critical_fields_count: int,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S3ConfidenceCoreError(
            code="INVALID_DECISION_RESPONSE",
            message="Executor de decisao retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e 'confidence_score'.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONF_S3_ALLOWED_EXEC_STATUSES:
        raise S3ConfidenceCoreError(
            code="INVALID_DECISION_EXECUTION_STATUS",
            message=f"Status de decisao invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    score = response.get("confidence_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise S3ConfidenceCoreError(
            code="INVALID_CONFIDENCE_SCORE",
            message=f"confidence_score invalido: {score}",
            action="Retorne confidence_score numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    score_value = float(score)
    if score_value < MIN_SCORE or score_value > MAX_SCORE:
        raise S3ConfidenceCoreError(
            code="CONFIDENCE_SCORE_OUT_OF_RANGE",
            message=f"confidence_score fora do intervalo permitido: {score}",
            action="Ajuste confidence_score para intervalo entre 0.0 e 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    manual_review_queue_size_raw = response.get("manual_review_queue_size", 0)
    if isinstance(manual_review_queue_size_raw, bool):
        raise S3ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message="manual_review_queue_size invalido: valor booleano nao permitido",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if isinstance(manual_review_queue_size_raw, float) and not manual_review_queue_size_raw.is_integer():
        raise S3ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=f"manual_review_queue_size invalido: {manual_review_queue_size_raw}",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if not isinstance(manual_review_queue_size_raw, (int, float)):
        raise S3ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=f"manual_review_queue_size invalido: {manual_review_queue_size_raw}",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    manual_review_queue_size = int(manual_review_queue_size_raw)
    if manual_review_queue_size < 0:
        raise S3ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=f"manual_review_queue_size invalido: {manual_review_queue_size_raw}",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    critical_fields_present_count_raw = response.get(
        "critical_fields_present_count",
        max_critical_fields_count,
    )
    if isinstance(critical_fields_present_count_raw, bool):
        raise S3ConfidenceCoreError(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message="critical_fields_present_count invalido: valor booleano nao permitido",
            action="Retorne critical_fields_present_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if (
        isinstance(critical_fields_present_count_raw, float)
        and not critical_fields_present_count_raw.is_integer()
    ):
        raise S3ConfidenceCoreError(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count invalido: "
                f"{critical_fields_present_count_raw}"
            ),
            action="Retorne critical_fields_present_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if not isinstance(critical_fields_present_count_raw, (int, float)):
        raise S3ConfidenceCoreError(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count invalido: "
                f"{critical_fields_present_count_raw}"
            ),
            action="Retorne critical_fields_present_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    critical_fields_present_count = int(critical_fields_present_count_raw)
    if critical_fields_present_count < 0:
        raise S3ConfidenceCoreError(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count invalido: "
                f"{critical_fields_present_count_raw}"
            ),
            action="Retorne critical_fields_present_count como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if critical_fields_present_count > max_critical_fields_count:
        raise S3ConfidenceCoreError(
            code="INVALID_CRITICAL_FIELDS_PRESENT_COUNT",
            message=(
                "critical_fields_present_count nao pode ser maior que o total "
                f"de campos criticos: {critical_fields_present_count}"
            ),
            action="Ajuste critical_fields_present_count para valor <= total de campos criticos.",
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    normalized["confidence_score"] = round(score_value, 6)
    normalized["manual_review_queue_size"] = manual_review_queue_size
    normalized["critical_fields_present_count"] = critical_fields_present_count
    return normalized


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


def _default_decision_executor(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one CONF Sprint 3 decision pass in dry-run mode.

    Args:
        context: Structured decision context with policy metadata.

    Returns:
        dict[str, Any]: Dry-run decision execution result.
    """

    field_weights_count = int(context.get("field_weights_count", 0))
    missing_field_penalty = float(context.get("missing_field_penalty", 0.0))
    auto_approve_threshold = float(context.get("auto_approve_threshold", 0.85))
    manual_review_threshold = float(context.get("manual_review_threshold", 0.60))
    gap_threshold = float(context.get("gap_threshold", 0.40))

    critical_fields_count = int(context.get("critical_fields_count", 0))
    min_critical_fields_present = int(
        context.get("min_critical_fields_present", critical_fields_count or 1)
    )
    critical_field_penalty = float(context.get("critical_field_penalty", 0.0))
    critical_violation_route = str(context.get("critical_violation_route", "manual_review")).strip().lower()

    critical_fields_present_count = critical_fields_count

    base_score = 0.90 if field_weights_count > 0 else 0.70
    confidence_score = max(MIN_SCORE, min(MAX_SCORE, base_score - missing_field_penalty))

    critical_violation = critical_fields_present_count < min_critical_fields_present
    if critical_violation:
        confidence_score = max(MIN_SCORE, confidence_score - critical_field_penalty)

    decision = _derive_decision(
        confidence_score=confidence_score,
        auto_approve_threshold=auto_approve_threshold,
        manual_review_threshold=manual_review_threshold,
        gap_threshold=gap_threshold,
    )
    if critical_violation and critical_violation_route in CONF_S3_ALLOWED_DECISIONS:
        decision = critical_violation_route

    return {
        "status": "succeeded",
        "confidence_score": round(confidence_score, 6),
        "decision": decision,
        "decision_reason": "dry_run_confidence_decision",
        "decision_result_id": f"confs3decision-{uuid4().hex[:12]}",
        "manual_review_queue_size": 0,
        "critical_fields_present_count": critical_fields_present_count,
    }


def _new_event_id() -> str:
    return f"confs3coreevt-{uuid4().hex[:12]}"
