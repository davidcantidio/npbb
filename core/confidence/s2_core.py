"""Main flow for CONF Sprint 2 confidence decision policy triage.

This module executes the Sprint 2 core path:
1) validate input and resolve Sprint 2 scaffold policy;
2) execute one auto/review/gap decision pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s2_scaffold import (
    S2ConfidenceScaffoldError,
    S2ConfidenceScaffoldRequest,
    build_s2_confidence_scaffold,
)


logger = logging.getLogger("npbb.core.confidence.s2.core")

CONTRACT_VERSION = "conf.s2.core.v1"
CONF_S2_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONF_S2_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONF_S2_ALLOWED_EXEC_STATUSES = CONF_S2_SUCCESS_STATUSES | CONF_S2_FAILED_STATUSES
CONF_S2_ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}

MIN_SCORE = 0.0
MAX_SCORE = 1.0


class S2ConfidenceCoreError(RuntimeError):
    """Raised when CONF Sprint 2 core flow fails."""

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
class S2ConfidenceCoreInput:
    """Input contract consumed by CONF Sprint 2 core flow."""

    policy_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v2"
    owner_team: str = "etl"
    field_weights: dict[str, float] | None = None
    default_weight: float = 1.0
    auto_approve_threshold: float = 0.85
    manual_review_threshold: float = 0.60
    gap_threshold: float = 0.40
    missing_field_penalty: float = 0.10
    decision_mode: str = "auto_review_gap"
    gap_escalation_required: bool = True
    max_manual_review_queue: int = 500
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S2ConfidenceScaffoldRequest:
        """Build scaffold request using CONF Sprint 2 stable fields."""

        return S2ConfidenceScaffoldRequest(
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
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2ConfidenceCoreOutput:
    """Output contract returned by CONF Sprint 2 core flow."""

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


def execute_s2_confidence_policy_main_flow(
    flow_input: S2ConfidenceCoreInput,
    *,
    execute_decision: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S2ConfidenceCoreOutput:
    """Execute CONF Sprint 2 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with policy metadata and decision
            thresholds for Sprint 2 (`auto_approve`, `manual_review`, `gap`).
        execute_decision: Optional callback responsible for one decision
            execution. It receives an execution context and must return a
            dictionary with `status` and `confidence_score` fields.

    Returns:
        S2ConfidenceCoreOutput: Stable output with decision policy,
            execution diagnostics, and observability identifiers.

    Raises:
        S2ConfidenceCoreError: If scaffold validation fails, execution response
            is invalid, or decision execution fails.
    """

    correlation_id = flow_input.correlation_id or f"conf-s2-{uuid4().hex[:12]}"
    decision_executor = execute_decision or _default_decision_executor
    started_event_id = _new_event_id()
    logger.info(
        "confidence_policy_s2_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": flow_input.policy_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "decision_mode": flow_input.decision_mode,
            "gap_escalation_required": flow_input.gap_escalation_required,
        },
    )

    try:
        scaffold = build_s2_confidence_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        thresholds = dict(scaffold.decision_policy.get("thresholds", {}))
        auto_approve_threshold = float(thresholds.get("auto_approve", 0.85))
        manual_review_threshold = float(thresholds.get("manual_review", 0.60))
        gap_threshold = float(thresholds.get("gap", 0.40))

        operational_policy = dict(scaffold.decision_policy.get("operational_policy", {}))
        gap_escalation_required = bool(operational_policy.get("gap_escalation_required", False))
        max_manual_review_queue = int(operational_policy.get("max_manual_review_queue", 0))

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
        }

        response = decision_executor(decision_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="decision_engine",
        )
        status = normalized["status"]
        confidence_score = float(normalized["confidence_score"])
        manual_review_queue_size = int(normalized.get("manual_review_queue_size", 0))

        decision = str(normalized.get("decision") or "").strip().lower()
        if not decision:
            decision = _derive_decision(
                confidence_score=confidence_score,
                auto_approve_threshold=auto_approve_threshold,
                manual_review_threshold=manual_review_threshold,
                gap_threshold=gap_threshold,
            )
        if decision not in CONF_S2_ALLOWED_DECISIONS:
            raise S2ConfidenceCoreError(
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
            "confidence_policy_s2_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "decision": decision,
                "confidence_score": confidence_score,
                "manual_review_queue_size": manual_review_queue_size,
                "max_manual_review_queue": max_manual_review_queue,
                "gap_escalation_triggered": gap_escalation_triggered,
            },
        )

        if status not in CONF_S2_SUCCESS_STATUSES:
            raise S2ConfidenceCoreError(
                code="CONF_S2_DECISION_EXECUTION_FAILED",
                message=f"Execucao de decisao CONF S2 falhou com status '{status}'",
                action=(
                    "Revisar logs do executor de decisao e conferir limiares/politica "
                    "operacional do contrato da sprint."
                ),
                correlation_id=correlation_id,
                stage="decision_engine",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["confidence_policy_core_module"] = (
            "core.confidence.s2_core.execute_s2_confidence_policy_main_flow"
        )

        return S2ConfidenceCoreOutput(
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
                "gap_escalation_triggered": gap_escalation_triggered,
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S2ConfidenceScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "confidence_policy_s2_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S2ConfidenceCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S2ConfidenceCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "confidence_policy_s2_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S2ConfidenceCoreError(
            code="CONF_S2_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONF S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONF S2.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S2ConfidenceCoreError(
            code="INVALID_DECISION_RESPONSE",
            message="Executor de decisao retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e 'confidence_score'.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONF_S2_ALLOWED_EXEC_STATUSES:
        raise S2ConfidenceCoreError(
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
        raise S2ConfidenceCoreError(
            code="INVALID_CONFIDENCE_SCORE",
            message=f"confidence_score invalido: {score}",
            action="Retorne confidence_score numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    score_value = float(score)
    if score_value < MIN_SCORE or score_value > MAX_SCORE:
        raise S2ConfidenceCoreError(
            code="CONFIDENCE_SCORE_OUT_OF_RANGE",
            message=f"confidence_score fora do intervalo permitido: {score}",
            action="Ajuste confidence_score para intervalo entre 0.0 e 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    manual_review_queue_size_raw = response.get("manual_review_queue_size", 0)
    if isinstance(manual_review_queue_size_raw, bool):
        raise S2ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message="manual_review_queue_size invalido: valor booleano nao permitido",
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if isinstance(manual_review_queue_size_raw, float) and not manual_review_queue_size_raw.is_integer():
        raise S2ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=(
                "manual_review_queue_size invalido: "
                f"{manual_review_queue_size_raw}"
            ),
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if not isinstance(manual_review_queue_size_raw, (int, float)):
        raise S2ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=(
                "manual_review_queue_size invalido: "
                f"{manual_review_queue_size_raw}"
            ),
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    manual_review_queue_size = int(manual_review_queue_size_raw)
    if manual_review_queue_size < 0:
        raise S2ConfidenceCoreError(
            code="INVALID_MANUAL_REVIEW_QUEUE_SIZE",
            message=(
                "manual_review_queue_size invalido: "
                f"{manual_review_queue_size_raw}"
            ),
            action="Retorne manual_review_queue_size como inteiro >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    normalized["confidence_score"] = round(score_value, 6)
    normalized["manual_review_queue_size"] = manual_review_queue_size
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
    """Execute one CONF Sprint 2 decision pass in dry-run mode.

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
        "decision_reason": "dry_run_confidence_decision",
        "decision_result_id": f"confs2decision-{uuid4().hex[:12]}",
        "manual_review_queue_size": 0,
    }


def _new_event_id() -> str:
    return f"confs2coreevt-{uuid4().hex[:12]}"
