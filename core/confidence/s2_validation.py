"""Validation contracts for CONF Sprint 2 confidence decision policy flow.

This module centralizes CONF Sprint 2 input/output validation used by tests
and integration checks. It provides structured actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_core import S2ConfidenceCoreInput
from .s2_observability import (
    S2ConfidenceObservabilityInput,
    build_s2_confidence_observability_event,
    log_s2_confidence_observability_event,
)
from .s2_scaffold import (
    S2ConfidenceScaffoldError,
    S2ConfidenceScaffoldRequest,
    build_s2_confidence_scaffold,
)


logger = logging.getLogger("npbb.core.confidence.s2.validation")

CONF_S2_VALIDATION_VERSION = "conf.s2.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}
ALLOWED_DECISIONS = {"auto_approve", "manual_review", "gap", "reject"}


class S2ConfidenceValidationError(ValueError):
    """Raised when CONF Sprint 2 validation contract is violated."""

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
class S2ConfidenceValidationInput:
    """Input contract consumed by CONF Sprint 2 validation checks."""

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

    def to_core_input(self, *, correlation_id: str | None = None) -> S2ConfidenceCoreInput:
        """Convert validated data to `S2ConfidenceCoreInput` contract."""

        return S2ConfidenceCoreInput(
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
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S2ConfidenceScaffoldRequest:
        """Convert validated data to `S2ConfidenceScaffoldRequest` contract."""

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
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2ConfidenceValidationResult:
    """Output contract returned by CONF Sprint 2 input validation."""

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
class S2ConfidenceFlowOutputValidationResult:
    """Output contract returned by CONF Sprint 2 flow-output validation."""

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


def validate_s2_confidence_input_contract(
    payload: S2ConfidenceValidationInput,
) -> S2ConfidenceValidationResult:
    """Validate CONF Sprint 2 input contract before running the main flow.

    Args:
        payload: Input contract with policy metadata and decision thresholds.

    Returns:
        S2ConfidenceValidationResult: Validation metadata and checks summary.

    Raises:
        S2ConfidenceValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"conf-s2-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="confidence_policy_s2_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do CONF S2 iniciada",
        severity="info",
        policy_id=payload.policy_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        decision_mode=payload.decision_mode,
        max_manual_review_queue=payload.max_manual_review_queue,
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

    try:
        scaffold = build_s2_confidence_scaffold(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S2ConfidenceScaffoldError as exc:
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
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="confidence_policy_s2_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do CONF S2 concluida com sucesso",
        severity="info",
        policy_id=scaffold.policy_id,
        dataset_name=scaffold.dataset_name,
        entity_kind=scaffold.decision_policy.get("entity_kind"),
        schema_version=scaffold.decision_policy.get("schema_version"),
        decision_mode=scaffold.decision_policy.get("decision_mode"),
        max_manual_review_queue=(
            scaffold.decision_policy.get("operational_policy", {}).get("max_manual_review_queue")
        ),
        stage="validation_input",
        context={
            "checks": checks,
            "field_weights_count": scaffold.decision_policy.get("field_weights_count"),
            "gap_threshold": scaffold.decision_policy.get("thresholds", {}).get("gap"),
        },
    )

    validation_id = f"confval-{uuid4().hex[:12]}"
    logger.info(
        "confidence_policy_s2_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "confidence_policy_s2",
        },
    )
    return S2ConfidenceValidationResult(
        validation_version=CONF_S2_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="confidence_policy_s2",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_s2_confidence_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S2ConfidenceFlowOutputValidationResult:
    """Validate CONF Sprint 2 flow output contract.

    Args:
        flow_output: Output dictionary produced by CONF S2 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S2ConfidenceFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S2ConfidenceValidationError: If output contract is incomplete or
            inconsistent with CONF Sprint 2 specifications.
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
            message=f"Saida do fluxo CONF S2 incompleta: faltam campos {missing_fields}",
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
            message=f"Status final inesperado no fluxo CONF S2: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do CONF S2.",
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
        "confidence_policy_s2_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "policy_id": str(flow_output.get("policy_id", "")),
        },
    )
    return S2ConfidenceFlowOutputValidationResult(
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
    if contract_version == "conf.s2.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "confs2coreevt-",
                "flow_completed_event_id": "confs2coreevt-",
            },
        )
    if contract_version == "conf.s2.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "confs2evt-",
                "policy_profile_ready_event_id": "confs2evt-",
                "flow_completed_event_id": "confs2evt-",
                "main_flow_started_event_id": "confs2coreevt-",
                "main_flow_completed_event_id": "confs2coreevt-",
            },
        )
    raise S2ConfidenceValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos conf.s2.core.v1 ou conf.s2.service.v1.",
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
        event_name="confidence_policy_s2_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "confidence_policy_s2_validation_error",
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
    raise S2ConfidenceValidationError(
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
    context: dict[str, Any] | None = None,
):
    payload = S2ConfidenceObservabilityInput(
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
        stage=stage,
        context=context,
    )
    event = build_s2_confidence_observability_event(payload)
    log_s2_confidence_observability_event(event)
    return event
