"""Main flow for WORK Sprint 2 missing-field correspondence.

This module executes the Sprint 2 core path:
1) validate input and resolve Sprint 2 scaffold policy;
2) execute one correspondence pass (dry-run by default);
3) return a stable output contract for API and integration layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s2_scaffold import (
    S2WorkbenchScaffoldError,
    S2WorkbenchScaffoldRequest,
    build_s2_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s2.core")

CONTRACT_VERSION = "work.s2.core.v1"
BACKEND_WORK_S2_EXECUTE_ENDPOINT = "/internal/revisao-humana/s2/execute"

WORK_S2_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
WORK_S2_FAILED_STATUSES = {
    "failed",
    "fatal_error",
    "timeout",
    "transient_error",
    "retryable_failure",
}
WORK_S2_ALLOWED_EXEC_STATUSES = WORK_S2_SUCCESS_STATUSES | WORK_S2_FAILED_STATUSES
WORK_S2_ALLOWED_CORRESPONDENCE_MODES = {"manual_confirm", "suggest_only", "semi_auto"}


class S2WorkbenchCoreError(RuntimeError):
    """Raised when WORK Sprint 2 core flow fails."""

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
class S2WorkbenchCoreInput:
    """Input contract consumed by WORK Sprint 2 core flow."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v2"
    owner_team: str = "etl"
    missing_fields: tuple[str, ...] | None = None
    candidate_sources: tuple[str, ...] | None = None
    correspondence_mode: str = "manual_confirm"
    match_strategy: str = "fuzzy"
    min_similarity_score: float = 0.70
    auto_apply_threshold: float = 0.95
    max_suggestions_per_field: int = 5
    require_evidence_for_suggestion: bool = True
    reviewer_roles: tuple[str, ...] | None = None
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S2WorkbenchScaffoldRequest:
        """Build scaffold request using WORK Sprint 2 stable fields."""

        return S2WorkbenchScaffoldRequest(
            workflow_id=self.workflow_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            missing_fields=self.missing_fields,
            candidate_sources=self.candidate_sources,
            correspondence_mode=self.correspondence_mode,
            match_strategy=self.match_strategy,
            min_similarity_score=self.min_similarity_score,
            auto_apply_threshold=self.auto_apply_threshold,
            max_suggestions_per_field=self.max_suggestions_per_field,
            require_evidence_for_suggestion=self.require_evidence_for_suggestion,
            reviewer_roles=self.reviewer_roles,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2WorkbenchCoreOutput:
    """Output contract returned by WORK Sprint 2 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    correspondence_policy: dict[str, Any]
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
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "correspondence_policy": self.correspondence_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_workbench_revisao_s2_main_flow(
    flow_input: S2WorkbenchCoreInput,
    *,
    execute_correspondence: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S2WorkbenchCoreOutput:
    """Execute WORK Sprint 2 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with correspondence policy metadata and
            operational guardrails.
        execute_correspondence: Optional callback responsible for one
            correspondence execution pass. It receives an execution context and
            must return a dictionary with `status` and correspondence metrics.

    Returns:
        S2WorkbenchCoreOutput: Stable output with correspondence policy,
            execution diagnostics, and observability identifiers.

    Raises:
        S2WorkbenchCoreError: If scaffold validation fails, execution response
            is invalid, or correspondence execution fails.
    """

    correlation_id = flow_input.correlation_id or f"work-s2-{uuid4().hex[:12]}"
    correspondence_executor = execute_correspondence or _default_correspondence_executor
    started_event_id = _new_event_id()
    logger.info(
        "workbench_revisao_s2_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "workflow_id": flow_input.workflow_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "correspondence_mode": flow_input.correspondence_mode,
            "match_strategy": flow_input.match_strategy,
        },
    )

    try:
        scaffold = build_s2_workbench_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        correspondence_policy = dict(scaffold.correspondence_policy)
        missing_fields_count = int(correspondence_policy.get("missing_fields_count", 0))
        candidate_sources_count = int(correspondence_policy.get("candidate_sources_count", 0))
        reviewer_roles_count = int(correspondence_policy.get("reviewer_roles_count", 0))
        correspondence_mode = str(correspondence_policy.get("correspondence_mode", "")).strip().lower()
        max_suggestions_per_field = int(correspondence_policy.get("max_suggestions_per_field", 0))
        require_evidence_for_suggestion = bool(
            correspondence_policy.get("require_evidence_for_suggestion", False)
        )
        min_similarity_score = float(correspondence_policy.get("min_similarity_score", 0.0))
        auto_apply_threshold = float(correspondence_policy.get("auto_apply_threshold", 0.0))
        suggestion_capacity = max(0, missing_fields_count * max_suggestions_per_field)

        correspondence_context = {
            "correlation_id": correlation_id,
            "workflow_id": scaffold.workflow_id,
            "dataset_name": scaffold.dataset_name,
            "entity_kind": correspondence_policy.get("entity_kind"),
            "match_strategy": correspondence_policy.get("match_strategy"),
            "correspondence_mode": correspondence_mode,
            "missing_fields_count": missing_fields_count,
            "candidate_sources_count": candidate_sources_count,
            "reviewer_roles_count": reviewer_roles_count,
            "min_similarity_score": min_similarity_score,
            "auto_apply_threshold": auto_apply_threshold,
            "max_suggestions_per_field": max_suggestions_per_field,
            "suggestion_capacity": suggestion_capacity,
            "require_evidence_for_suggestion": require_evidence_for_suggestion,
        }

        response = correspondence_executor(correspondence_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="correspondence",
            suggestion_capacity=suggestion_capacity,
        )

        status = normalized["status"]
        suggested_matches = int(normalized["suggested_matches"])
        reviewed_matches = int(normalized["reviewed_matches"])
        auto_applied_matches = int(normalized["auto_applied_matches"])
        unresolved_fields_count = int(normalized["unresolved_fields_count"])
        candidate_pairs_evaluated = int(normalized["candidate_pairs_evaluated"])
        evidence_links_count = int(normalized["evidence_links_count"])
        suggestion_overflow_detected = bool(normalized["suggestion_overflow_detected"])

        if correspondence_mode not in WORK_S2_ALLOWED_CORRESPONDENCE_MODES:
            raise S2WorkbenchCoreError(
                code="INVALID_CORRESPONDENCE_MODE",
                message=f"correspondence_mode invalido: {correspondence_mode}",
                action="Use modo valido: manual_confirm, suggest_only ou semi_auto.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if suggested_matches > suggestion_capacity:
            raise S2WorkbenchCoreError(
                code="SUGGESTIONS_EXCEED_CAPACITY",
                message="suggested_matches excede suggestion_capacity",
                action="Ajuste executor para suggested_matches <= suggestion_capacity.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if reviewed_matches > suggested_matches:
            raise S2WorkbenchCoreError(
                code="INVALID_REVIEWED_MATCHES_COUNT",
                message="reviewed_matches nao pode ser maior que suggested_matches",
                action="Ajuste reviewed_matches para reviewed_matches <= suggested_matches.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if auto_applied_matches > suggested_matches:
            raise S2WorkbenchCoreError(
                code="INVALID_AUTO_APPLIED_MATCHES_COUNT",
                message="auto_applied_matches nao pode ser maior que suggested_matches",
                action="Ajuste auto_applied_matches para <= suggested_matches.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if unresolved_fields_count > missing_fields_count:
            raise S2WorkbenchCoreError(
                code="INVALID_UNRESOLVED_FIELDS_COUNT",
                message="unresolved_fields_count nao pode ser maior que missing_fields_count",
                action="Ajuste unresolved_fields_count para <= missing_fields_count.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if candidate_pairs_evaluated < suggested_matches:
            raise S2WorkbenchCoreError(
                code="INVALID_CANDIDATE_PAIRS_EVALUATED",
                message="candidate_pairs_evaluated nao pode ser menor que suggested_matches",
                action="Ajuste candidate_pairs_evaluated para refletir avaliacoes realizadas.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if correspondence_mode in {"manual_confirm", "suggest_only"} and auto_applied_matches > 0:
            raise S2WorkbenchCoreError(
                code="INVALID_AUTO_APPLY_FOR_MODE",
                message=(
                    "auto_applied_matches deve ser zero para correspondence_mode "
                    f"{correspondence_mode}"
                ),
                action="Retorne auto_applied_matches=0 ou use correspondence_mode=semi_auto.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if require_evidence_for_suggestion and suggested_matches > 0 and evidence_links_count <= 0:
            raise S2WorkbenchCoreError(
                code="MISSING_EVIDENCE_LINKS",
                message="require_evidence_for_suggestion ativo sem evidence_links_count positivo",
                action="Propague evidence_links_count > 0 ou desative require_evidence_for_suggestion.",
                correlation_id=correlation_id,
                stage="correspondence",
            )

        if candidate_pairs_evaluated > suggestion_capacity and not suggestion_overflow_detected:
            raise S2WorkbenchCoreError(
                code="SUGGESTION_CAPACITY_OVERFLOW_NOT_FLAGGED",
                message=(
                    "candidate_pairs_evaluated excede suggestion_capacity sem "
                    "suggestion_overflow_detected=true"
                ),
                action=(
                    "Sinalize suggestion_overflow_detected=true quando candidate_pairs_evaluated "
                    "> suggestion_capacity."
                ),
                correlation_id=correlation_id,
                stage="correspondence",
            )

        completed_event_id = _new_event_id()
        logger.info(
            "workbench_revisao_s2_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "workflow_id": scaffold.workflow_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "suggested_matches": suggested_matches,
                "reviewed_matches": reviewed_matches,
                "auto_applied_matches": auto_applied_matches,
                "unresolved_fields_count": unresolved_fields_count,
                "candidate_pairs_evaluated": candidate_pairs_evaluated,
                "suggestion_overflow_detected": suggestion_overflow_detected,
            },
        )

        if status not in WORK_S2_SUCCESS_STATUSES:
            raise S2WorkbenchCoreError(
                code="WORK_S2_CORRESPONDENCE_FAILED",
                message=f"Execucao de correspondencia WORK S2 falhou com status '{status}'",
                action=(
                    "Revisar logs do executor de correspondencia e validar regras de "
                    "similaridade, evidencia e capacidade."
                ),
                correlation_id=correlation_id,
                stage="correspondence",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["workbench_revisao_s2_core_module"] = (
            "app.modules.revisao_humana.s2_core.execute_workbench_revisao_s2_main_flow"
        )
        pontos_integracao["work_s2_execute_endpoint"] = BACKEND_WORK_S2_EXECUTE_ENDPOINT

        return S2WorkbenchCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            workflow_id=scaffold.workflow_id,
            dataset_name=scaffold.dataset_name,
            correspondence_policy=correspondence_policy,
            execucao={
                "status": status,
                "correspondence_result_id": str(
                    normalized.get("correspondence_result_id", f"works2corr-{uuid4().hex[:12]}")
                ),
                "suggested_matches": suggested_matches,
                "reviewed_matches": reviewed_matches,
                "auto_applied_matches": auto_applied_matches,
                "unresolved_fields_count": unresolved_fields_count,
                "candidate_pairs_evaluated": candidate_pairs_evaluated,
                "suggestion_capacity": suggestion_capacity,
                "suggestion_overflow_detected": suggestion_overflow_detected,
                "evidence_links_count": evidence_links_count,
                "require_evidence_for_suggestion": require_evidence_for_suggestion,
                "correspondence_mode": correspondence_mode,
                "match_strategy": str(correspondence_policy.get("match_strategy")),
                "decision_reason": str(
                    normalized.get("decision_reason", "dry_run_missing_field_correspondence")
                ),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S2WorkbenchScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "workbench_revisao_s2_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S2WorkbenchCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S2WorkbenchCoreError:
        raise
    except Exception as exc:  # noqa: BLE001
        failed_event_id = _new_event_id()
        logger.error(
            "workbench_revisao_s2_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S2WorkbenchCoreError(
            code="WORK_S2_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal WORK S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor WORK S2.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
    suggestion_capacity: int,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S2WorkbenchCoreError(
            code="INVALID_CORRESPONDENCE_RESPONSE",
            message="Executor de correspondencia retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e metricas de correspondencia.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in WORK_S2_ALLOWED_EXEC_STATUSES:
        raise S2WorkbenchCoreError(
            code="INVALID_CORRESPONDENCE_STATUS",
            message=f"Status de execucao da correspondencia invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status

    for field_name in (
        "suggested_matches",
        "reviewed_matches",
        "auto_applied_matches",
        "unresolved_fields_count",
        "candidate_pairs_evaluated",
        "evidence_links_count",
    ):
        value = normalized.get(field_name, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise S2WorkbenchCoreError(
                code=f"INVALID_{field_name.upper()}",
                message=f"{field_name} invalido: {value}",
                action=f"Retorne {field_name} como inteiro >= 0.",
                correlation_id=correlation_id,
                stage=stage,
            )
        normalized[field_name] = int(value)

    suggestion_overflow_detected = normalized.get("suggestion_overflow_detected")
    if suggestion_overflow_detected is None:
        suggestion_overflow_detected = normalized["candidate_pairs_evaluated"] > suggestion_capacity
    if not isinstance(suggestion_overflow_detected, bool):
        raise S2WorkbenchCoreError(
            code="INVALID_SUGGESTION_OVERFLOW_DETECTED",
            message=f"suggestion_overflow_detected invalido: {suggestion_overflow_detected}",
            action="Retorne suggestion_overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage=stage,
        )
    normalized["suggestion_overflow_detected"] = suggestion_overflow_detected
    return normalized


def _default_correspondence_executor(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one WORK Sprint 2 correspondence pass in dry-run mode.

    Args:
        context: Structured correspondence context with policy metadata.

    Returns:
        dict[str, Any]: Dry-run correspondence execution result.
    """

    missing_fields_count = int(context.get("missing_fields_count", 0))
    candidate_sources_count = int(context.get("candidate_sources_count", 0))
    reviewer_roles_count = int(context.get("reviewer_roles_count", 0))
    max_suggestions_per_field = int(context.get("max_suggestions_per_field", 0))
    correspondence_mode = str(context.get("correspondence_mode", "manual_confirm")).strip().lower()
    match_strategy = str(context.get("match_strategy", "fuzzy")).strip().lower()
    require_evidence_for_suggestion = bool(context.get("require_evidence_for_suggestion", False))

    strategy_multiplier = 2 if match_strategy in {"fuzzy", "semantic"} else 1
    candidate_pairs_evaluated = (
        missing_fields_count * max(1, candidate_sources_count) * strategy_multiplier
    )
    suggestion_capacity = max(0, missing_fields_count * max(0, max_suggestions_per_field))
    suggested_matches = min(candidate_pairs_evaluated, suggestion_capacity)
    suggestion_overflow_detected = candidate_pairs_evaluated > suggestion_capacity

    if correspondence_mode == "suggest_only":
        reviewed_matches = 0
        auto_applied_matches = 0
    elif correspondence_mode == "semi_auto":
        reviewed_matches = min(suggested_matches, max(1, reviewer_roles_count))
        auto_applied_matches = min(suggested_matches, max(1, reviewer_roles_count // 2))
    else:
        reviewed_matches = min(suggested_matches, max(1, reviewer_roles_count))
        auto_applied_matches = 0

    resolved_fields = min(missing_fields_count, max(auto_applied_matches, reviewed_matches))
    unresolved_fields_count = max(0, missing_fields_count - resolved_fields)
    evidence_links_count = (
        suggested_matches
        if require_evidence_for_suggestion
        else max(0, suggested_matches // 2)
    )

    return {
        "status": "succeeded",
        "correspondence_result_id": f"works2corr-{uuid4().hex[:12]}",
        "suggested_matches": suggested_matches,
        "reviewed_matches": reviewed_matches,
        "auto_applied_matches": auto_applied_matches,
        "unresolved_fields_count": unresolved_fields_count,
        "candidate_pairs_evaluated": candidate_pairs_evaluated,
        "suggestion_overflow_detected": suggestion_overflow_detected,
        "evidence_links_count": evidence_links_count,
        "decision_reason": "dry_run_missing_field_correspondence",
    }


def _new_event_id() -> str:
    return f"works2coreevt-{uuid4().hex[:12]}"

