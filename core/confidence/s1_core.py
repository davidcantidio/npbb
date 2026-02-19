"""Main flow for CONF Sprint 1 field-level confidence scoring.

This module executes the Sprint 1 core path:
1) validate input and resolve Sprint 1 scaffold policy;
2) execute one confidence scoring pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s1_scaffold import (
    S1ConfidenceScaffoldError,
    S1ConfidenceScaffoldRequest,
    build_s1_confidence_scaffold,
)


logger = logging.getLogger("npbb.core.confidence.s1.core")

CONTRACT_VERSION = "conf.s1.core.v1"
CONF_S1_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONF_S1_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONF_S1_ALLOWED_EXEC_STATUSES = CONF_S1_SUCCESS_STATUSES | CONF_S1_FAILED_STATUSES
CONF_S1_ALLOWED_DECISIONS = {"auto_approve", "manual_review", "reject"}

MIN_SCORE = 0.0
MAX_SCORE = 1.0


class S1ConfidenceCoreError(RuntimeError):
    """Raised when CONF Sprint 1 core flow fails."""

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
class S1ConfidenceCoreInput:
    """Input contract consumed by CONF Sprint 1 core flow."""

    policy_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v1"
    owner_team: str = "etl"
    field_weights: dict[str, float] | None = None
    default_weight: float = 1.0
    auto_approve_threshold: float = 0.85
    manual_review_threshold: float = 0.60
    missing_field_penalty: float = 0.10
    decision_mode: str = "weighted_threshold"
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S1ConfidenceScaffoldRequest:
        """Build scaffold request using CONF Sprint 1 stable fields."""

        return S1ConfidenceScaffoldRequest(
            policy_id=self.policy_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            field_weights=self.field_weights,
            default_weight=self.default_weight,
            auto_approve_threshold=self.auto_approve_threshold,
            manual_review_threshold=self.manual_review_threshold,
            missing_field_penalty=self.missing_field_penalty,
            decision_mode=self.decision_mode,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1ConfidenceCoreOutput:
    """Output contract returned by CONF Sprint 1 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    policy_id: str
    dataset_name: str
    confidence_policy: dict[str, Any]
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
            "confidence_policy": self.confidence_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s1_confidence_policy_main_flow(
    flow_input: S1ConfidenceCoreInput,
    *,
    execute_scoring: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S1ConfidenceCoreOutput:
    """Execute CONF Sprint 1 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with policy metadata and confidence
            thresholds for Sprint 1.
        execute_scoring: Optional callback responsible for one confidence score
            execution. It receives an execution context and must return a
            dictionary with `status` and optional diagnostics fields.

    Returns:
        S1ConfidenceCoreOutput: Stable output with confidence policy,
            execution diagnostics, and observability identifiers.

    Raises:
        S1ConfidenceCoreError: If scaffold validation fails, execution response
            is invalid, or scoring execution fails.
    """

    correlation_id = flow_input.correlation_id or f"conf-s1-{uuid4().hex[:12]}"
    scorer = execute_scoring or _default_scorer
    started_event_id = _new_event_id()
    logger.info(
        "confidence_policy_s1_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": flow_input.policy_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "decision_mode": flow_input.decision_mode,
        },
    )

    try:
        scaffold = build_s1_confidence_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        thresholds = dict(scaffold.confidence_policy.get("thresholds", {}))
        auto_approve_threshold = float(thresholds.get("auto_approve", 0.85))
        manual_review_threshold = float(thresholds.get("manual_review", 0.60))
        scoring_context = {
            "correlation_id": correlation_id,
            "policy_id": scaffold.policy_id,
            "dataset_name": scaffold.dataset_name,
            "entity_kind": scaffold.confidence_policy.get("entity_kind"),
            "decision_mode": scaffold.confidence_policy.get("decision_mode"),
            "field_weights_count": scaffold.confidence_policy.get("field_weights_count", 0),
            "default_weight": scaffold.confidence_policy.get("default_weight", 1.0),
            "missing_field_penalty": scaffold.confidence_policy.get("missing_field_penalty", 0.0),
            "auto_approve_threshold": auto_approve_threshold,
            "manual_review_threshold": manual_review_threshold,
        }
        response = scorer(scoring_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="scoring",
        )
        status = normalized["status"]
        confidence_score = float(normalized["confidence_score"])

        decision = str(normalized.get("decision") or "").strip().lower()
        if not decision:
            decision = _derive_decision(
                confidence_score=confidence_score,
                auto_approve_threshold=auto_approve_threshold,
                manual_review_threshold=manual_review_threshold,
            )
        if decision not in CONF_S1_ALLOWED_DECISIONS:
            raise S1ConfidenceCoreError(
                code="INVALID_CONFIDENCE_DECISION",
                message=f"Decisao de confianca invalida: {decision}",
                action="Retorne decisao valida: auto_approve, manual_review ou reject.",
                correlation_id=correlation_id,
                stage="scoring",
            )

        completed_event_id = _new_event_id()
        logger.info(
            "confidence_policy_s1_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "decision": decision,
                "confidence_score": confidence_score,
            },
        )

        if status not in CONF_S1_SUCCESS_STATUSES:
            raise S1ConfidenceCoreError(
                code="CONF_S1_SCORING_FAILED",
                message=f"Execucao de score CONF S1 falhou com status '{status}'",
                action=(
                    "Revisar logs de scoring e conferir pesos/limiares de confianca "
                    "do contrato da politica."
                ),
                correlation_id=correlation_id,
                stage="scoring",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["confidence_policy_core_module"] = (
            "core.confidence.s1_core.execute_s1_confidence_policy_main_flow"
        )

        return S1ConfidenceCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            policy_id=scaffold.policy_id,
            dataset_name=scaffold.dataset_name,
            confidence_policy=dict(scaffold.confidence_policy),
            execucao={
                "status": status,
                "decision": decision,
                "confidence_score": round(confidence_score, 6),
                "decision_reason": str(normalized.get("decision_reason", "dry_run_main_flow")),
                "score_result_id": str(normalized.get("score_result_id", "")),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S1ConfidenceScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "confidence_policy_s1_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S1ConfidenceCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S1ConfidenceCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "confidence_policy_s1_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S1ConfidenceCoreError(
            code="CONF_S1_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONF S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONF S1.",
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
        raise S1ConfidenceCoreError(
            code="INVALID_SCORING_RESPONSE",
            message="Executor de score retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e 'confidence_score'.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONF_S1_ALLOWED_EXEC_STATUSES:
        raise S1ConfidenceCoreError(
            code="INVALID_SCORING_STATUS",
            message=f"Status de score invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    score = response.get("confidence_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise S1ConfidenceCoreError(
            code="INVALID_CONFIDENCE_SCORE",
            message=f"confidence_score invalido: {score}",
            action="Retorne confidence_score numerico no intervalo de 0.0 a 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    score_value = float(score)
    if score_value < MIN_SCORE or score_value > MAX_SCORE:
        raise S1ConfidenceCoreError(
            code="CONFIDENCE_SCORE_OUT_OF_RANGE",
            message=f"confidence_score fora do intervalo permitido: {score}",
            action="Ajuste confidence_score para intervalo entre 0.0 e 1.0.",
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    normalized["confidence_score"] = round(score_value, 6)
    return normalized


def _derive_decision(
    *,
    confidence_score: float,
    auto_approve_threshold: float,
    manual_review_threshold: float,
) -> str:
    if confidence_score >= auto_approve_threshold:
        return "auto_approve"
    if confidence_score >= manual_review_threshold:
        return "manual_review"
    return "reject"


def _default_scorer(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one confidence scoring pass in dry-run mode.

    Args:
        context: Structured scoring context with policy metadata.

    Returns:
        dict[str, Any]: Dry-run score execution result.
    """

    field_weights_count = int(context.get("field_weights_count", 0))
    missing_field_penalty = float(context.get("missing_field_penalty", 0.0))
    auto_approve_threshold = float(context.get("auto_approve_threshold", 0.85))
    manual_review_threshold = float(context.get("manual_review_threshold", 0.60))

    base_score = 0.90 if field_weights_count > 0 else 0.70
    confidence_score = max(MIN_SCORE, min(MAX_SCORE, base_score - missing_field_penalty))
    decision = _derive_decision(
        confidence_score=confidence_score,
        auto_approve_threshold=auto_approve_threshold,
        manual_review_threshold=manual_review_threshold,
    )

    return {
        "status": "succeeded",
        "confidence_score": round(confidence_score, 6),
        "decision": decision,
        "decision_reason": "dry_run_confidence_scoring",
        "score_result_id": f"confs1score-{uuid4().hex[:12]}",
    }


def _new_event_id() -> str:
    return f"confs1coreevt-{uuid4().hex[:12]}"
