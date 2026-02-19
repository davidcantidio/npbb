"""Validation contracts for WORK Sprint 2 correspondence workbench flow.

This module centralizes WORK Sprint 2 input/output validation used by tests
and integration checks. It provides structured actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_core import S2WorkbenchCoreInput
from .s2_observability import (
    S2WorkbenchObservabilityInput,
    build_s2_workbench_observability_event,
    get_s2_workbench_observability_integration_points,
    log_s2_workbench_observability_event,
)
from .s2_scaffold import (
    S2WorkbenchScaffoldError,
    S2WorkbenchScaffoldRequest,
    build_s2_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s2.validation")

WORK_S2_VALIDATION_VERSION = "work.s2.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}
ALLOWED_CORRESPONDENCE_MODES = {"manual_confirm", "suggest_only", "semi_auto"}
ALLOWED_MATCH_STRATEGIES = {"exact", "normalized", "fuzzy", "semantic"}

EXPECTED_PREPARE_ENDPOINT = "/internal/revisao-humana/s2/prepare"
EXPECTED_EXECUTE_ENDPOINT = "/internal/revisao-humana/s2/execute"
EXPECTED_ROUTER_MODULE = "app.routers.revisao_humana.prepare_workbench_revisao_s2"
EXPECTED_VALIDATION_MODULE = (
    "frontend.src.features.revisao_humana.s2_validation."
    "validate_workbench_revisao_s2_output_contract"
)


class S2WorkbenchValidationError(ValueError):
    """Raised when WORK Sprint 2 validation contract is violated."""

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
class S2WorkbenchValidationInput:
    """Input contract consumed by WORK Sprint 2 validation checks."""

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

    def to_core_input(self, *, correlation_id: str | None = None) -> S2WorkbenchCoreInput:
        """Convert validated data to `S2WorkbenchCoreInput` contract."""

        return S2WorkbenchCoreInput(
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
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S2WorkbenchScaffoldRequest:
        """Convert validated data to `S2WorkbenchScaffoldRequest` contract."""

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
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2WorkbenchValidationResult:
    """Output contract returned by WORK Sprint 2 input validation."""

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
class S2WorkbenchFlowOutputValidationResult:
    """Output contract returned by WORK Sprint 2 flow-output validation."""

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


def validate_workbench_revisao_s2_input_contract(
    payload: S2WorkbenchValidationInput,
) -> S2WorkbenchValidationResult:
    """Validate WORK Sprint 2 input contract before running the main flow.

    Args:
        payload: Input contract with correspondence policy metadata and
            guardrails.

    Returns:
        S2WorkbenchValidationResult: Validation metadata and checks summary.

    Raises:
        S2WorkbenchValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"work-s2-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="workbench_revisao_s2_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do WORK S2 iniciada",
        severity="info",
        workflow_id=payload.workflow_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        owner_team=payload.owner_team,
        correspondence_mode=payload.correspondence_mode,
        match_strategy=payload.match_strategy,
        max_suggestions_per_field=payload.max_suggestions_per_field,
        stage="validation_input",
    )
    checks: list[str] = []

    if not payload.workflow_id.strip():
        _raise_validation_error(
            code="EMPTY_WORKFLOW_ID",
            message="workflow_id nao pode ser vazio",
            action="Informe workflow_id estavel antes de iniciar a validacao.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("workflow_id")

    if not payload.dataset_name.strip():
        _raise_validation_error(
            code="EMPTY_DATASET_NAME",
            message="dataset_name nao pode ser vazio",
            action="Informe dataset_name para rastreabilidade da correspondencia.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("dataset_name")

    if not payload.entity_kind.strip():
        _raise_validation_error(
            code="EMPTY_ENTITY_KIND",
            message="entity_kind nao pode ser vazio",
            action="Informe entity_kind para aplicar regras da sprint.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("entity_kind")

    if payload.missing_fields is not None and not isinstance(payload.missing_fields, tuple):
        _raise_validation_error(
            code="INVALID_MISSING_FIELDS_TYPE",
            message="missing_fields deve ser tupla de nomes de campos",
            action="Informe missing_fields como tuple[str, ...].",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"missing_fields_type": type(payload.missing_fields).__name__},
        )
    checks.append("missing_fields")

    if payload.candidate_sources is not None and not isinstance(payload.candidate_sources, tuple):
        _raise_validation_error(
            code="INVALID_CANDIDATE_SOURCES_TYPE",
            message="candidate_sources deve ser tupla de fontes",
            action="Informe candidate_sources como tuple[str, ...].",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"candidate_sources_type": type(payload.candidate_sources).__name__},
        )
    checks.append("candidate_sources")

    if payload.reviewer_roles is not None and not isinstance(payload.reviewer_roles, tuple):
        _raise_validation_error(
            code="INVALID_REVIEWER_ROLES_TYPE",
            message="reviewer_roles deve ser tupla de papeis",
            action="Informe reviewer_roles como tuple[str, ...].",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"reviewer_roles_type": type(payload.reviewer_roles).__name__},
        )
    checks.append("reviewer_roles")

    if isinstance(payload.max_suggestions_per_field, bool) or not isinstance(
        payload.max_suggestions_per_field,
        int,
    ):
        _raise_validation_error(
            code="INVALID_MAX_SUGGESTIONS_PER_FIELD_TYPE",
            message="max_suggestions_per_field deve ser inteiro",
            action="Ajuste max_suggestions_per_field para um valor inteiro valido.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"max_suggestions_per_field": str(payload.max_suggestions_per_field)},
        )
    checks.append("max_suggestions_per_field")

    if not isinstance(payload.require_evidence_for_suggestion, bool):
        _raise_validation_error(
            code="INVALID_REQUIRE_EVIDENCE_FOR_SUGGESTION_FLAG",
            message="require_evidence_for_suggestion deve ser booleano",
            action="Ajuste require_evidence_for_suggestion para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={
                "require_evidence_for_suggestion": str(payload.require_evidence_for_suggestion)
            },
        )
    checks.append("require_evidence_for_suggestion")

    try:
        scaffold = build_s2_workbench_scaffold(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S2WorkbenchScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "entity_kind": payload.entity_kind,
                "schema_version": payload.schema_version,
                "correspondence_mode": payload.correspondence_mode,
                "match_strategy": payload.match_strategy,
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="workbench_revisao_s2_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do WORK S2 concluida com sucesso",
        severity="info",
        workflow_id=scaffold.workflow_id,
        dataset_name=scaffold.dataset_name,
        entity_kind=scaffold.correspondence_policy.get("entity_kind"),
        schema_version=scaffold.correspondence_policy.get("schema_version"),
        owner_team=scaffold.correspondence_policy.get("owner_team"),
        status=scaffold.status,
        correspondence_mode=scaffold.correspondence_policy.get("correspondence_mode"),
        match_strategy=scaffold.correspondence_policy.get("match_strategy"),
        missing_fields_count=scaffold.correspondence_policy.get("missing_fields_count"),
        candidate_sources_count=scaffold.correspondence_policy.get("candidate_sources_count"),
        reviewer_roles_count=scaffold.correspondence_policy.get("reviewer_roles_count"),
        max_suggestions_per_field=scaffold.correspondence_policy.get("max_suggestions_per_field"),
        require_evidence_for_suggestion=scaffold.correspondence_policy.get(
            "require_evidence_for_suggestion"
        ),
        stage="validation_input",
        context={"checks": checks},
    )

    validation_id = f"workval-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s2_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "workbench_revisao_s2",
        },
    )
    return S2WorkbenchValidationResult(
        validation_version=WORK_S2_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="workbench_revisao_s2",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_workbench_revisao_s2_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S2WorkbenchFlowOutputValidationResult:
    """Validate WORK Sprint 2 flow output contract.

    Args:
        flow_output: Output dictionary produced by WORK S2 core flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S2WorkbenchFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S2WorkbenchValidationError: If output contract is incomplete or
            inconsistent with WORK Sprint 2 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "workflow_id",
        "dataset_name",
        "correspondence_policy",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo WORK S2 incompleta: faltam campos {missing_fields}",
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
            message=f"Status final inesperado no fluxo WORK S2: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do WORK S2.",
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

    execucao = flow_output.get("execucao")
    if not isinstance(execucao, dict):
        _raise_validation_error(
            code="INVALID_EXECUCAO_PAYLOAD",
            message=f"execucao invalido na saida: {type(execucao).__name__}",
            action="Retorne execucao como objeto com metricas da correspondencia.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

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

    correspondence_result_id = str(execucao.get("correspondence_result_id", "")).strip()
    if not correspondence_result_id:
        _raise_validation_error(
            code="MISSING_CORRESPONDENCE_RESULT_ID",
            message="correspondence_result_id ausente na saida de execucao",
            action="Propague correspondence_result_id para rastreabilidade da correspondencia.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    suggested_matches = _read_non_negative_int_field(
        container=execucao,
        field_name="suggested_matches",
        correlation_id=correlation_id,
    )
    reviewed_matches = _read_non_negative_int_field(
        container=execucao,
        field_name="reviewed_matches",
        correlation_id=correlation_id,
    )
    auto_applied_matches = _read_non_negative_int_field(
        container=execucao,
        field_name="auto_applied_matches",
        correlation_id=correlation_id,
    )
    unresolved_fields_count = _read_non_negative_int_field(
        container=execucao,
        field_name="unresolved_fields_count",
        correlation_id=correlation_id,
    )
    candidate_pairs_evaluated = _read_non_negative_int_field(
        container=execucao,
        field_name="candidate_pairs_evaluated",
        correlation_id=correlation_id,
    )
    suggestion_capacity = _read_non_negative_int_field(
        container=execucao,
        field_name="suggestion_capacity",
        correlation_id=correlation_id,
    )
    evidence_links_count = _read_non_negative_int_field(
        container=execucao,
        field_name="evidence_links_count",
        correlation_id=correlation_id,
    )

    suggestion_overflow_detected = execucao.get("suggestion_overflow_detected")
    if not isinstance(suggestion_overflow_detected, bool):
        _raise_validation_error(
            code="INVALID_SUGGESTION_OVERFLOW_DETECTED",
            message=(
                "suggestion_overflow_detected invalido na saida: "
                f"{suggestion_overflow_detected}"
            ),
            action="Retorne suggestion_overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"suggestion_overflow_detected": str(suggestion_overflow_detected)},
        )

    require_evidence_for_suggestion = execucao.get("require_evidence_for_suggestion")
    if not isinstance(require_evidence_for_suggestion, bool):
        _raise_validation_error(
            code="INVALID_REQUIRE_EVIDENCE_FOR_SUGGESTION_FLAG",
            message=(
                "require_evidence_for_suggestion invalido na saida: "
                f"{require_evidence_for_suggestion}"
            ),
            action="Retorne require_evidence_for_suggestion como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "require_evidence_for_suggestion": str(require_evidence_for_suggestion)
            },
        )

    correspondence_mode = str(execucao.get("correspondence_mode", "")).strip().lower()
    if correspondence_mode not in ALLOWED_CORRESPONDENCE_MODES:
        _raise_validation_error(
            code="INVALID_CORRESPONDENCE_MODE",
            message=f"correspondence_mode invalido na saida: {execucao.get('correspondence_mode')}",
            action="Use correspondence_mode valido: manual_confirm, suggest_only ou semi_auto.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    match_strategy = str(execucao.get("match_strategy", "")).strip().lower()
    if match_strategy not in ALLOWED_MATCH_STRATEGIES:
        _raise_validation_error(
            code="INVALID_MATCH_STRATEGY",
            message=f"match_strategy invalido na saida: {execucao.get('match_strategy')}",
            action="Use match_strategy valido: exact, normalized, fuzzy ou semantic.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    decision_reason = str(execucao.get("decision_reason", "")).strip()
    if not decision_reason:
        _raise_validation_error(
            code="MISSING_DECISION_REASON",
            message="decision_reason ausente na saida de execucao",
            action="Propague decision_reason para diagnostico operacional da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    correspondence_policy = flow_output.get("correspondence_policy")
    if not isinstance(correspondence_policy, dict):
        _raise_validation_error(
            code="INVALID_CORRESPONDENCE_POLICY_PAYLOAD",
            message=(
                "correspondence_policy invalido na saida: "
                f"{type(correspondence_policy).__name__}"
            ),
            action="Retorne correspondence_policy como objeto do contrato da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    missing_fields_count = _read_non_negative_int_field(
        container=correspondence_policy,
        field_name="missing_fields_count",
        correlation_id=correlation_id,
    )
    reviewer_roles_count = _read_non_negative_int_field(
        container=correspondence_policy,
        field_name="reviewer_roles_count",
        correlation_id=correlation_id,
    )
    max_suggestions_per_field = _read_non_negative_int_field(
        container=correspondence_policy,
        field_name="max_suggestions_per_field",
        correlation_id=correlation_id,
    )

    policy_correspondence_mode = str(
        correspondence_policy.get("correspondence_mode", "")
    ).strip().lower()
    if policy_correspondence_mode and policy_correspondence_mode != correspondence_mode:
        _raise_validation_error(
            code="CORRESPONDENCE_MODE_MISMATCH",
            message="correspondence_mode divergente entre correspondence_policy e execucao",
            action="Propague correspondence_mode consistente entre politica e execucao.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "policy_correspondence_mode": policy_correspondence_mode,
                "execucao_correspondence_mode": correspondence_mode,
            },
        )

    policy_match_strategy = str(correspondence_policy.get("match_strategy", "")).strip().lower()
    if policy_match_strategy and policy_match_strategy != match_strategy:
        _raise_validation_error(
            code="MATCH_STRATEGY_MISMATCH",
            message="match_strategy divergente entre correspondence_policy e execucao",
            action="Propague match_strategy consistente entre politica e execucao.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "policy_match_strategy": policy_match_strategy,
                "execucao_match_strategy": match_strategy,
            },
        )

    expected_capacity = missing_fields_count * max_suggestions_per_field
    if suggestion_capacity != expected_capacity:
        _raise_validation_error(
            code="INVALID_SUGGESTION_CAPACITY",
            message="suggestion_capacity inconsistente com missing_fields_count e max_suggestions_per_field",
            action=(
                "Ajuste suggestion_capacity para "
                "missing_fields_count * max_suggestions_per_field."
            ),
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "suggestion_capacity": str(suggestion_capacity),
                "missing_fields_count": str(missing_fields_count),
                "max_suggestions_per_field": str(max_suggestions_per_field),
            },
        )

    if reviewed_matches > suggested_matches:
        _raise_validation_error(
            code="INVALID_REVIEWED_MATCHES_COUNT",
            message="reviewed_matches nao pode ser maior que suggested_matches",
            action="Ajuste reviewed_matches para <= suggested_matches.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if auto_applied_matches > suggested_matches:
        _raise_validation_error(
            code="INVALID_AUTO_APPLIED_MATCHES_COUNT",
            message="auto_applied_matches nao pode ser maior que suggested_matches",
            action="Ajuste auto_applied_matches para <= suggested_matches.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if unresolved_fields_count > missing_fields_count:
        _raise_validation_error(
            code="INVALID_UNRESOLVED_FIELDS_COUNT",
            message="unresolved_fields_count nao pode ser maior que missing_fields_count",
            action="Ajuste unresolved_fields_count para <= missing_fields_count.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if candidate_pairs_evaluated < suggested_matches:
        _raise_validation_error(
            code="INVALID_CANDIDATE_PAIRS_EVALUATED",
            message="candidate_pairs_evaluated nao pode ser menor que suggested_matches",
            action="Ajuste candidate_pairs_evaluated para refletir avaliacoes realizadas.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if suggested_matches > suggestion_capacity:
        _raise_validation_error(
            code="SUGGESTIONS_EXCEED_CAPACITY",
            message="suggested_matches excede suggestion_capacity",
            action="Ajuste suggested_matches para <= suggestion_capacity.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if candidate_pairs_evaluated > suggestion_capacity and suggestion_overflow_detected is False:
        _raise_validation_error(
            code="SUGGESTION_CAPACITY_OVERFLOW_NOT_FLAGGED",
            message=(
                "candidate_pairs_evaluated excede suggestion_capacity sem "
                "suggestion_overflow_detected=true"
            ),
            action=(
                "Sinalize suggestion_overflow_detected=true quando "
                "candidate_pairs_evaluated > suggestion_capacity."
            ),
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if correspondence_mode in {"manual_confirm", "suggest_only"} and auto_applied_matches > 0:
        _raise_validation_error(
            code="INVALID_AUTO_APPLY_FOR_MODE",
            message=(
                "auto_applied_matches deve ser zero para correspondence_mode "
                f"{correspondence_mode}"
            ),
            action="Retorne auto_applied_matches=0 ou use correspondence_mode=semi_auto.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if require_evidence_for_suggestion and suggested_matches > 0 and evidence_links_count <= 0:
        _raise_validation_error(
            code="MISSING_EVIDENCE_LINKS",
            message="require_evidence_for_suggestion ativo sem evidence_links_count positivo",
            action="Propague evidence_links_count > 0 ou desative require_evidence_for_suggestion.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if reviewer_roles_count <= 0 and reviewed_matches > 0:
        _raise_validation_error(
            code="INVALID_REVIEW_WITHOUT_REVIEWER",
            message="reviewed_matches positivo sem reviewer_roles_count valido",
            action="Propague reviewer_roles_count >= 1 quando reviewed_matches > 0.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    pontos_integracao = flow_output.get("pontos_integracao")
    if not isinstance(pontos_integracao, dict):
        _raise_validation_error(
            code="INVALID_PONTOS_INTEGRACAO",
            message=(
                "pontos_integracao invalido na saida: "
                f"{type(pontos_integracao).__name__}"
            ),
            action="Retorne pontos_integracao como objeto de modulos/endpoints da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    observability_points = get_s2_workbench_observability_integration_points()
    expected_core_module = observability_points["workbench_revisao_s2_core_module"]

    expected_points = {
        "work_s2_prepare_endpoint": EXPECTED_PREPARE_ENDPOINT,
        "work_s2_execute_endpoint": EXPECTED_EXECUTE_ENDPOINT,
        "workbench_revisao_router_module": EXPECTED_ROUTER_MODULE,
        "workbench_revisao_s2_core_module": expected_core_module,
        "workbench_revisao_s2_validation_module": EXPECTED_VALIDATION_MODULE,
    }
    for key, expected_value in expected_points.items():
        value = str(pontos_integracao.get(key, "")).strip()
        if value != expected_value:
            _raise_validation_error(
                code="INVALID_INTEGRATION_POINT",
                message=f"Ponto de integracao invalido para {key}: {value}",
                action=(
                    "Atualize pontos_integracao para refletir endpoints e modulos "
                    "tecnicos esperados da Sprint 2."
                ),
                correlation_id=correlation_id,
                stage="validation_output",
                context={"key": key, "value": value, "expected": expected_value},
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
        "workbench_revisao_s2_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "workflow_id": str(flow_output.get("workflow_id", "")),
            "dataset_name": str(flow_output.get("dataset_name", "")),
        },
    )
    return S2WorkbenchFlowOutputValidationResult(
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
    if contract_version == "work.s2.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "works2coreevt-",
                "flow_completed_event_id": "works2coreevt-",
            },
        )

    raise S2WorkbenchValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contrato work.s2.core.v1.",
        correlation_id=correlation_id,
        stage="validation_output",
    )


def _read_non_negative_int_field(
    *,
    container: dict[str, Any],
    field_name: str,
    correlation_id: str,
) -> int:
    value = container.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _raise_validation_error(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} invalido na saida: {value}",
            action=f"Retorne {field_name} como inteiro >= 0.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={field_name: str(value)},
        )
    return int(value)


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
        event_name="workbench_revisao_s2_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "workbench_revisao_s2_validation_error",
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
    raise S2WorkbenchValidationError(
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
    workflow_id: str | None = None,
    dataset_name: str | None = None,
    entity_kind: str | None = None,
    schema_version: str | None = None,
    owner_team: str | None = None,
    status: str | None = None,
    correspondence_mode: str | None = None,
    match_strategy: str | None = None,
    missing_fields_count: int | None = None,
    candidate_sources_count: int | None = None,
    reviewer_roles_count: int | None = None,
    max_suggestions_per_field: int | None = None,
    suggestion_capacity: int | None = None,
    candidate_pairs_evaluated: int | None = None,
    suggested_matches: int | None = None,
    reviewed_matches: int | None = None,
    auto_applied_matches: int | None = None,
    unresolved_fields_count: int | None = None,
    evidence_links_count: int | None = None,
    suggestion_overflow_detected: bool | None = None,
    require_evidence_for_suggestion: bool | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S2WorkbenchObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        workflow_id=workflow_id,
        dataset_name=dataset_name,
        entity_kind=entity_kind,
        schema_version=schema_version,
        owner_team=owner_team,
        status=status,
        stage=stage,
        correspondence_mode=correspondence_mode,
        match_strategy=match_strategy,
        missing_fields_count=missing_fields_count,
        candidate_sources_count=candidate_sources_count,
        reviewer_roles_count=reviewer_roles_count,
        max_suggestions_per_field=max_suggestions_per_field,
        suggestion_capacity=suggestion_capacity,
        candidate_pairs_evaluated=candidate_pairs_evaluated,
        suggested_matches=suggested_matches,
        reviewed_matches=reviewed_matches,
        auto_applied_matches=auto_applied_matches,
        unresolved_fields_count=unresolved_fields_count,
        evidence_links_count=evidence_links_count,
        suggestion_overflow_detected=suggestion_overflow_detected,
        require_evidence_for_suggestion=require_evidence_for_suggestion,
        context=context,
    )
    event = build_s2_workbench_observability_event(payload)
    log_s2_workbench_observability_event(event)
    return event
