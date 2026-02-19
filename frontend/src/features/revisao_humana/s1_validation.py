"""Validation contracts for WORK Sprint 1 human-review workbench flow.

This module centralizes WORK Sprint 1 input/output validation used by tests
and integration checks. It provides structured actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s1_core import S1WorkbenchCoreInput
from .s1_observability import (
    S1WorkbenchObservabilityInput,
    build_s1_workbench_observability_event,
    log_s1_workbench_observability_event,
)
from .s1_scaffold import (
    S1WorkbenchScaffoldError,
    S1WorkbenchScaffoldRequest,
    build_s1_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s1.validation")

WORK_S1_VALIDATION_VERSION = "work.s1.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}


class S1WorkbenchValidationError(ValueError):
    """Raised when WORK Sprint 1 validation contract is violated."""

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
class S1WorkbenchValidationInput:
    """Input contract consumed by WORK Sprint 1 validation checks."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v1"
    owner_team: str = "etl"
    required_fields: tuple[str, ...] | None = None
    evidence_sources: tuple[str, ...] | None = None
    default_priority: str = "media"
    sla_hours: int = 24
    max_queue_size: int = 1000
    auto_assignment_enabled: bool = True
    reviewer_roles: tuple[str, ...] | None = None
    correlation_id: str | None = None

    def to_core_input(self, *, correlation_id: str | None = None) -> S1WorkbenchCoreInput:
        """Convert validated data to `S1WorkbenchCoreInput` contract."""

        return S1WorkbenchCoreInput(
            workflow_id=self.workflow_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            required_fields=self.required_fields,
            evidence_sources=self.evidence_sources,
            default_priority=self.default_priority,
            sla_hours=self.sla_hours,
            max_queue_size=self.max_queue_size,
            auto_assignment_enabled=self.auto_assignment_enabled,
            reviewer_roles=self.reviewer_roles,
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S1WorkbenchScaffoldRequest:
        """Convert validated data to `S1WorkbenchScaffoldRequest` contract."""

        return S1WorkbenchScaffoldRequest(
            workflow_id=self.workflow_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            required_fields=self.required_fields,
            evidence_sources=self.evidence_sources,
            default_priority=self.default_priority,
            sla_hours=self.sla_hours,
            max_queue_size=self.max_queue_size,
            auto_assignment_enabled=self.auto_assignment_enabled,
            reviewer_roles=self.reviewer_roles,
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1WorkbenchValidationResult:
    """Output contract returned by WORK Sprint 1 input validation."""

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
class S1WorkbenchFlowOutputValidationResult:
    """Output contract returned by WORK Sprint 1 flow-output validation."""

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


def validate_workbench_revisao_s1_input_contract(
    payload: S1WorkbenchValidationInput,
) -> S1WorkbenchValidationResult:
    """Validate WORK Sprint 1 input contract before running the main flow.

    Args:
        payload: Input contract with queue policy metadata and guardrails.

    Returns:
        S1WorkbenchValidationResult: Validation metadata and checks summary.

    Raises:
        S1WorkbenchValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"work-s1-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="workbench_revisao_s1_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do WORK S1 iniciada",
        severity="info",
        workflow_id=payload.workflow_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        owner_team=payload.owner_team,
        default_priority=payload.default_priority,
        max_queue_size=payload.max_queue_size,
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
            action="Informe dataset_name para rastreabilidade da fila de revisao.",
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

    if payload.required_fields is not None and not isinstance(payload.required_fields, tuple):
        _raise_validation_error(
            code="INVALID_REQUIRED_FIELDS_TYPE",
            message="required_fields deve ser tupla de nomes de campos",
            action="Informe required_fields como tuple[str, ...].",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"required_fields_type": type(payload.required_fields).__name__},
        )
    checks.append("required_fields")

    if payload.evidence_sources is not None and not isinstance(payload.evidence_sources, tuple):
        _raise_validation_error(
            code="INVALID_EVIDENCE_SOURCES_TYPE",
            message="evidence_sources deve ser tupla de fontes",
            action="Informe evidence_sources como tuple[str, ...].",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"evidence_sources_type": type(payload.evidence_sources).__name__},
        )
    checks.append("evidence_sources")

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

    if not isinstance(payload.auto_assignment_enabled, bool):
        _raise_validation_error(
            code="INVALID_AUTO_ASSIGNMENT_ENABLED_FLAG",
            message="auto_assignment_enabled deve ser booleano",
            action="Ajuste auto_assignment_enabled para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"auto_assignment_enabled": payload.auto_assignment_enabled},
        )
    checks.append("auto_assignment_enabled")

    try:
        scaffold = build_s1_workbench_scaffold(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S1WorkbenchScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "entity_kind": payload.entity_kind,
                "schema_version": payload.schema_version,
                "default_priority": payload.default_priority,
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="workbench_revisao_s1_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do WORK S1 concluida com sucesso",
        severity="info",
        workflow_id=scaffold.workflow_id,
        dataset_name=scaffold.dataset_name,
        entity_kind=scaffold.review_queue_policy.get("entity_kind"),
        schema_version=scaffold.review_queue_policy.get("schema_version"),
        owner_team=scaffold.review_queue_policy.get("owner_team"),
        default_priority=scaffold.review_queue_policy.get("default_priority"),
        required_fields_count=scaffold.review_queue_policy.get("required_fields_count"),
        evidence_sources_count=scaffold.review_queue_policy.get("evidence_sources_count"),
        reviewer_roles_count=scaffold.review_queue_policy.get("reviewer_roles_count"),
        max_queue_size=scaffold.review_queue_policy.get("max_queue_size"),
        auto_assignment_enabled=scaffold.review_queue_policy.get("auto_assignment_enabled"),
        stage="validation_input",
        context={"checks": checks},
    )

    validation_id = f"workval-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s1_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "workbench_revisao_s1",
        },
    )
    return S1WorkbenchValidationResult(
        validation_version=WORK_S1_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="workbench_revisao_s1",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_workbench_revisao_s1_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S1WorkbenchFlowOutputValidationResult:
    """Validate WORK Sprint 1 flow output contract.

    Args:
        flow_output: Output dictionary produced by WORK S1 core flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S1WorkbenchFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S1WorkbenchValidationError: If output contract is incomplete or
            inconsistent with WORK Sprint 1 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "workflow_id",
        "dataset_name",
        "review_queue_policy",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo WORK S1 incompleta: faltam campos {missing_fields}",
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
            message=f"Status final inesperado no fluxo WORK S1: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do WORK S1.",
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

    queue_build_result_id = str(execucao.get("queue_build_result_id", "")).strip()
    if not queue_build_result_id:
        _raise_validation_error(
            code="MISSING_QUEUE_BUILD_RESULT_ID",
            message="queue_build_result_id ausente na saida de execucao",
            action="Propague queue_build_result_id para rastreabilidade da fila.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    generated_items = _read_non_negative_int_field(
        container=execucao,
        field_name="generated_items",
        correlation_id=correlation_id,
    )
    queue_size = _read_non_negative_int_field(
        container=execucao,
        field_name="queue_size",
        correlation_id=correlation_id,
    )
    queue_capacity = _read_non_negative_int_field(
        container=execucao,
        field_name="queue_capacity",
        correlation_id=correlation_id,
    )
    critical_items = _read_non_negative_int_field(
        container=execucao,
        field_name="critical_items",
        correlation_id=correlation_id,
    )
    assigned_items = _read_non_negative_int_field(
        container=execucao,
        field_name="assigned_items",
        correlation_id=correlation_id,
    )
    pending_fields_count = _read_non_negative_int_field(
        container=execucao,
        field_name="pending_fields_count",
        correlation_id=correlation_id,
    )
    evidence_sources_count = _read_non_negative_int_field(
        container=execucao,
        field_name="evidence_sources_count",
        correlation_id=correlation_id,
    )

    overflow_detected = execucao.get("overflow_detected")
    if not isinstance(overflow_detected, bool):
        _raise_validation_error(
            code="INVALID_OVERFLOW_DETECTED",
            message=f"overflow_detected invalido na saida: {overflow_detected}",
            action="Retorne overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"overflow_detected": str(overflow_detected)},
        )

    auto_assignment_enabled = execucao.get("auto_assignment_enabled")
    if not isinstance(auto_assignment_enabled, bool):
        _raise_validation_error(
            code="INVALID_AUTO_ASSIGNMENT_ENABLED_FLAG",
            message=f"auto_assignment_enabled invalido na saida: {auto_assignment_enabled}",
            action="Retorne auto_assignment_enabled como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"auto_assignment_enabled": str(auto_assignment_enabled)},
        )

    decision_reason = str(execucao.get("decision_reason", "")).strip()
    if not decision_reason:
        _raise_validation_error(
            code="MISSING_DECISION_REASON",
            message="decision_reason ausente na saida de execucao",
            action="Propague decision_reason para diagnostico operacional da fila.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    review_queue_policy = flow_output.get("review_queue_policy", {})
    max_queue_size = _read_non_negative_int_field(
        container=review_queue_policy,
        field_name="max_queue_size",
        correlation_id=correlation_id,
    )

    if queue_size > generated_items:
        _raise_validation_error(
            code="INVALID_QUEUE_SIZE",
            message="queue_size nao pode ser maior que generated_items",
            action="Ajuste metricas para queue_size <= generated_items.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if max_queue_size > 0 and queue_size > max_queue_size:
        _raise_validation_error(
            code="INVALID_QUEUE_SIZE",
            message="queue_size nao pode ser maior que max_queue_size",
            action="Ajuste metricas para queue_size <= max_queue_size.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if critical_items > generated_items:
        _raise_validation_error(
            code="INVALID_CRITICAL_ITEMS_COUNT",
            message="critical_items nao pode ser maior que generated_items",
            action="Ajuste metricas para critical_items <= generated_items.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if assigned_items > generated_items:
        _raise_validation_error(
            code="INVALID_ASSIGNED_ITEMS_COUNT",
            message="assigned_items nao pode ser maior que generated_items",
            action="Ajuste metricas para assigned_items <= generated_items.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if generated_items > max_queue_size and overflow_detected is False:
        _raise_validation_error(
            code="INVALID_OVERFLOW_FLAG",
            message="generated_items excede max_queue_size sem overflow_detected=true",
            action="Defina overflow_detected=true quando generated_items > max_queue_size.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if auto_assignment_enabled and generated_items > 0 and assigned_items <= 0:
        _raise_validation_error(
            code="INVALID_AUTO_ASSIGNMENT_RESULT",
            message="auto_assignment_enabled ativo sem atribuicoes na saida",
            action="Retorne assigned_items > 0 ou desative auto_assignment_enabled.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if queue_capacity + queue_size < generated_items and max_queue_size >= generated_items:
        _raise_validation_error(
            code="INVALID_QUEUE_CAPACITY",
            message="queue_capacity inconsistente com queue_size e generated_items",
            action="Ajuste queue_capacity para refletir capacidade real da fila.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "generated_items": str(generated_items),
                "queue_size": str(queue_size),
                "queue_capacity": str(queue_capacity),
            },
        )
    if pending_fields_count > generated_items:
        _raise_validation_error(
            code="INVALID_PENDING_FIELDS_COUNT",
            message="pending_fields_count nao pode ser maior que generated_items",
            action="Ajuste pending_fields_count para refletir itens gerados.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if evidence_sources_count <= 0:
        _raise_validation_error(
            code="INVALID_EVIDENCE_SOURCES_COUNT",
            message="evidence_sources_count deve ser maior que zero",
            action="Propague evidence_sources_count valido na saida de execucao.",
            correlation_id=correlation_id,
            stage="validation_output",
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
        "workbench_revisao_s1_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "workflow_id": str(flow_output.get("workflow_id", "")),
            "dataset_name": str(flow_output.get("dataset_name", "")),
        },
    )
    return S1WorkbenchFlowOutputValidationResult(
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
    if contract_version == "work.s1.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "works1coreevt-",
                "flow_completed_event_id": "works1coreevt-",
            },
        )

    raise S1WorkbenchValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contrato work.s1.core.v1.",
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
        event_name="workbench_revisao_s1_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "workbench_revisao_s1_validation_error",
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
    raise S1WorkbenchValidationError(
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
    default_priority: str | None = None,
    status: str | None = None,
    required_fields_count: int | None = None,
    evidence_sources_count: int | None = None,
    reviewer_roles_count: int | None = None,
    max_queue_size: int | None = None,
    generated_items: int | None = None,
    queue_size: int | None = None,
    critical_items: int | None = None,
    assigned_items: int | None = None,
    pending_fields_count: int | None = None,
    overflow_detected: bool | None = None,
    auto_assignment_enabled: bool | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S1WorkbenchObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        workflow_id=workflow_id,
        dataset_name=dataset_name,
        entity_kind=entity_kind,
        schema_version=schema_version,
        owner_team=owner_team,
        default_priority=default_priority,
        status=status,
        stage=stage,
        required_fields_count=required_fields_count,
        evidence_sources_count=evidence_sources_count,
        reviewer_roles_count=reviewer_roles_count,
        max_queue_size=max_queue_size,
        generated_items=generated_items,
        queue_size=queue_size,
        critical_items=critical_items,
        assigned_items=assigned_items,
        pending_fields_count=pending_fields_count,
        overflow_detected=overflow_detected,
        auto_assignment_enabled=auto_assignment_enabled,
        context=context,
    )
    event = build_s1_workbench_observability_event(payload)
    log_s1_workbench_observability_event(event)
    return event

