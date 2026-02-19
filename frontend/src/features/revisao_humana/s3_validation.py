"""Validation contracts for WORK Sprint 3 batch-approval workbench flow.

This module centralizes WORK Sprint 3 input/output validation used by tests
and integration checks. It provides structured actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s3_core import S3WorkbenchCoreInput
from .s3_observability import (
    S3WorkbenchObservabilityInput,
    build_s3_workbench_observability_event,
    get_s3_workbench_observability_integration_points,
    log_s3_workbench_observability_event,
)
from .s3_scaffold import (
    S3WorkbenchScaffoldError,
    S3WorkbenchScaffoldRequest,
    build_s3_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s3.validation")

WORK_S3_VALIDATION_VERSION = "work.s3.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}
ALLOWED_APPROVAL_MODES = {"single_reviewer", "dual_control", "committee"}

EXPECTED_PREPARE_ENDPOINT = "/internal/revisao-humana/s3/prepare"
EXPECTED_EXECUTE_ENDPOINT = "/internal/revisao-humana/s3/execute"
EXPECTED_ROUTER_MODULE = "app.routers.revisao_humana.prepare_workbench_revisao_s3"
EXPECTED_VALIDATION_MODULE = (
    "frontend.src.features.revisao_humana.s3_validation."
    "validate_workbench_revisao_s3_output_contract"
)


class S3WorkbenchValidationError(ValueError):
    """Raised when WORK Sprint 3 validation contract is violated."""

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
class S3WorkbenchValidationInput:
    """Input contract consumed by WORK Sprint 3 validation checks."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v3"
    owner_team: str = "etl"
    batch_size: int = 200
    max_pending_batches: int = 2000
    approval_mode: str = "dual_control"
    required_approvers: int = 2
    approver_roles: tuple[str, ...] | None = None
    approval_sla_hours: int = 24
    require_justification: bool = True
    allow_partial_approval: bool = False
    auto_lock_on_conflict: bool = True
    correlation_id: str | None = None

    def to_core_input(self, *, correlation_id: str | None = None) -> S3WorkbenchCoreInput:
        """Convert validated data to `S3WorkbenchCoreInput` contract."""

        return S3WorkbenchCoreInput(
            workflow_id=self.workflow_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            batch_size=self.batch_size,
            max_pending_batches=self.max_pending_batches,
            approval_mode=self.approval_mode,
            required_approvers=self.required_approvers,
            approver_roles=self.approver_roles,
            approval_sla_hours=self.approval_sla_hours,
            require_justification=self.require_justification,
            allow_partial_approval=self.allow_partial_approval,
            auto_lock_on_conflict=self.auto_lock_on_conflict,
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S3WorkbenchScaffoldRequest:
        """Convert validated data to `S3WorkbenchScaffoldRequest` contract."""

        return S3WorkbenchScaffoldRequest(
            workflow_id=self.workflow_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            batch_size=self.batch_size,
            max_pending_batches=self.max_pending_batches,
            approval_mode=self.approval_mode,
            required_approvers=self.required_approvers,
            approver_roles=self.approver_roles,
            approval_sla_hours=self.approval_sla_hours,
            require_justification=self.require_justification,
            allow_partial_approval=self.allow_partial_approval,
            auto_lock_on_conflict=self.auto_lock_on_conflict,
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3WorkbenchValidationResult:
    """Output contract returned by WORK Sprint 3 input validation."""

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
class S3WorkbenchFlowOutputValidationResult:
    """Output contract returned by WORK Sprint 3 flow-output validation."""

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


def validate_workbench_revisao_s3_input_contract(
    payload: S3WorkbenchValidationInput,
) -> S3WorkbenchValidationResult:
    """Validate WORK Sprint 3 input contract before running the main flow.

    Args:
        payload: Input contract with batch-approval policy metadata and
            guardrails.

    Returns:
        S3WorkbenchValidationResult: Validation metadata and checks summary.

    Raises:
        S3WorkbenchValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"work-s3-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="workbench_revisao_s3_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do WORK S3 iniciada",
        severity="info",
        workflow_id=payload.workflow_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        owner_team=payload.owner_team,
        approval_mode=payload.approval_mode,
        required_approvers=payload.required_approvers,
        batch_size=payload.batch_size,
        max_pending_batches=payload.max_pending_batches,
        approval_sla_hours=payload.approval_sla_hours,
        require_justification=payload.require_justification,
        allow_partial_approval=payload.allow_partial_approval,
        auto_lock_on_conflict=payload.auto_lock_on_conflict,
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
            action="Informe dataset_name para rastreabilidade da aprovacao em lote.",
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

    if payload.approver_roles is not None and not isinstance(payload.approver_roles, tuple):
        _raise_validation_error(
            code="INVALID_APPROVER_ROLES_TYPE",
            message="approver_roles deve ser tupla de papeis",
            action="Informe approver_roles como tuple[str, ...].",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"approver_roles_type": type(payload.approver_roles).__name__},
        )
    checks.append("approver_roles")

    for field_name in (
        "batch_size",
        "max_pending_batches",
        "required_approvers",
        "approval_sla_hours",
    ):
        value = getattr(payload, field_name)
        if isinstance(value, bool) or not isinstance(value, int):
            _raise_validation_error(
                code=f"INVALID_{field_name.upper()}_TYPE",
                message=f"{field_name} deve ser inteiro",
                action=f"Ajuste {field_name} para um valor inteiro valido.",
                correlation_id=correlation_id,
                stage="validation_input",
                context={field_name: str(value)},
            )
        checks.append(field_name)

    for field_name in (
        "require_justification",
        "allow_partial_approval",
        "auto_lock_on_conflict",
    ):
        value = getattr(payload, field_name)
        if not isinstance(value, bool):
            _raise_validation_error(
                code=f"INVALID_{field_name.upper()}_FLAG",
                message=f"{field_name} deve ser booleano",
                action=f"Ajuste {field_name} para true/false.",
                correlation_id=correlation_id,
                stage="validation_input",
                context={field_name: str(value)},
            )
        checks.append(field_name)

    try:
        scaffold = build_s3_workbench_scaffold(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S3WorkbenchScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "entity_kind": payload.entity_kind,
                "schema_version": payload.schema_version,
                "approval_mode": payload.approval_mode,
                "required_approvers": str(payload.required_approvers),
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="workbench_revisao_s3_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do WORK S3 concluida com sucesso",
        severity="info",
        workflow_id=scaffold.workflow_id,
        dataset_name=scaffold.dataset_name,
        entity_kind=scaffold.batch_approval_policy.get("entity_kind"),
        schema_version=scaffold.batch_approval_policy.get("schema_version"),
        owner_team=scaffold.batch_approval_policy.get("owner_team"),
        status=scaffold.status,
        approval_mode=scaffold.batch_approval_policy.get("approval_mode"),
        required_approvers=scaffold.batch_approval_policy.get("required_approvers"),
        approver_roles_count=scaffold.batch_approval_policy.get("approver_roles_count"),
        batch_size=scaffold.batch_approval_policy.get("batch_size"),
        max_pending_batches=scaffold.batch_approval_policy.get("max_pending_batches"),
        approval_sla_hours=scaffold.batch_approval_policy.get("approval_sla_hours"),
        require_justification=scaffold.batch_approval_policy.get("require_justification"),
        allow_partial_approval=scaffold.batch_approval_policy.get("allow_partial_approval"),
        auto_lock_on_conflict=scaffold.batch_approval_policy.get("auto_lock_on_conflict"),
        stage="validation_input",
        context={"checks": checks},
    )

    validation_id = f"workval-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s3_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "workbench_revisao_s3",
        },
    )
    return S3WorkbenchValidationResult(
        validation_version=WORK_S3_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="workbench_revisao_s3",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_workbench_revisao_s3_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S3WorkbenchFlowOutputValidationResult:
    """Validate WORK Sprint 3 flow output contract.

    Args:
        flow_output: Output dictionary produced by WORK S3 core flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S3WorkbenchFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S3WorkbenchValidationError: If output contract is incomplete or
            inconsistent with WORK Sprint 3 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "workflow_id",
        "dataset_name",
        "batch_approval_policy",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo WORK S3 incompleta: faltam campos {missing_fields}",
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
            message=f"Status final inesperado no fluxo WORK S3: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do WORK S3.",
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
            action="Retorne execucao como objeto com metricas da aprovacao em lote.",
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

    batch_approval_result_id = str(execucao.get("batch_approval_result_id", "")).strip()
    if not batch_approval_result_id:
        _raise_validation_error(
            code="MISSING_BATCH_APPROVAL_RESULT_ID",
            message="batch_approval_result_id ausente na saida de execucao",
            action="Propague batch_approval_result_id para rastreabilidade da aprovacao em lote.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    batches_received = _read_non_negative_int_field(
        container=execucao,
        field_name="batches_received",
        correlation_id=correlation_id,
    )
    batches_approved = _read_non_negative_int_field(
        container=execucao,
        field_name="batches_approved",
        correlation_id=correlation_id,
    )
    batches_rejected = _read_non_negative_int_field(
        container=execucao,
        field_name="batches_rejected",
        correlation_id=correlation_id,
    )
    batches_escalated = _read_non_negative_int_field(
        container=execucao,
        field_name="batches_escalated",
        correlation_id=correlation_id,
    )
    pending_batches = _read_non_negative_int_field(
        container=execucao,
        field_name="pending_batches",
        correlation_id=correlation_id,
    )
    approvals_recorded = _read_non_negative_int_field(
        container=execucao,
        field_name="approvals_recorded",
        correlation_id=correlation_id,
    )
    conflicts_detected = _read_non_negative_int_field(
        container=execucao,
        field_name="conflicts_detected",
        correlation_id=correlation_id,
    )
    auto_locked_batches = _read_non_negative_int_field(
        container=execucao,
        field_name="auto_locked_batches",
        correlation_id=correlation_id,
    )
    partial_approvals = _read_non_negative_int_field(
        container=execucao,
        field_name="partial_approvals",
        correlation_id=correlation_id,
    )
    justifications_missing = _read_non_negative_int_field(
        container=execucao,
        field_name="justifications_missing",
        correlation_id=correlation_id,
    )
    approval_queue_capacity = _read_non_negative_int_field(
        container=execucao,
        field_name="approval_queue_capacity",
        correlation_id=correlation_id,
    )
    required_approvers = _read_non_negative_int_field(
        container=execucao,
        field_name="required_approvers",
        correlation_id=correlation_id,
    )

    approval_overflow_detected = execucao.get("approval_overflow_detected")
    if not isinstance(approval_overflow_detected, bool):
        _raise_validation_error(
            code="INVALID_APPROVAL_OVERFLOW_DETECTED",
            message=(
                "approval_overflow_detected invalido na saida: "
                f"{approval_overflow_detected}"
            ),
            action="Retorne approval_overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"approval_overflow_detected": str(approval_overflow_detected)},
        )

    require_justification = execucao.get("require_justification")
    if not isinstance(require_justification, bool):
        _raise_validation_error(
            code="INVALID_REQUIRE_JUSTIFICATION_FLAG",
            message=f"require_justification invalido na saida: {require_justification}",
            action="Retorne require_justification como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"require_justification": str(require_justification)},
        )

    allow_partial_approval = execucao.get("allow_partial_approval")
    if not isinstance(allow_partial_approval, bool):
        _raise_validation_error(
            code="INVALID_ALLOW_PARTIAL_APPROVAL_FLAG",
            message=f"allow_partial_approval invalido na saida: {allow_partial_approval}",
            action="Retorne allow_partial_approval como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"allow_partial_approval": str(allow_partial_approval)},
        )

    auto_lock_on_conflict = execucao.get("auto_lock_on_conflict")
    if not isinstance(auto_lock_on_conflict, bool):
        _raise_validation_error(
            code="INVALID_AUTO_LOCK_ON_CONFLICT_FLAG",
            message=f"auto_lock_on_conflict invalido na saida: {auto_lock_on_conflict}",
            action="Retorne auto_lock_on_conflict como booleano.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"auto_lock_on_conflict": str(auto_lock_on_conflict)},
        )

    approval_mode = str(execucao.get("approval_mode", "")).strip().lower()
    if approval_mode not in ALLOWED_APPROVAL_MODES:
        _raise_validation_error(
            code="INVALID_APPROVAL_MODE",
            message=f"approval_mode invalido na saida: {execucao.get('approval_mode')}",
            action="Use approval_mode valido: single_reviewer, dual_control ou committee.",
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

    batch_approval_policy = flow_output.get("batch_approval_policy")
    if not isinstance(batch_approval_policy, dict):
        _raise_validation_error(
            code="INVALID_BATCH_APPROVAL_POLICY_PAYLOAD",
            message=(
                "batch_approval_policy invalido na saida: "
                f"{type(batch_approval_policy).__name__}"
            ),
            action="Retorne batch_approval_policy como objeto do contrato da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    policy_required_approvers = _read_non_negative_int_field(
        container=batch_approval_policy,
        field_name="required_approvers",
        correlation_id=correlation_id,
    )
    approver_roles_count = _read_non_negative_int_field(
        container=batch_approval_policy,
        field_name="approver_roles_count",
        correlation_id=correlation_id,
    )
    batch_size = _read_non_negative_int_field(
        container=batch_approval_policy,
        field_name="batch_size",
        correlation_id=correlation_id,
    )
    max_pending_batches = _read_non_negative_int_field(
        container=batch_approval_policy,
        field_name="max_pending_batches",
        correlation_id=correlation_id,
    )
    _read_non_negative_int_field(
        container=batch_approval_policy,
        field_name="approval_sla_hours",
        correlation_id=correlation_id,
    )

    policy_approval_mode = str(batch_approval_policy.get("approval_mode", "")).strip().lower()
    if policy_approval_mode and policy_approval_mode != approval_mode:
        _raise_validation_error(
            code="APPROVAL_MODE_MISMATCH",
            message="approval_mode divergente entre batch_approval_policy e execucao",
            action="Propague approval_mode consistente entre politica e execucao.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "policy_approval_mode": policy_approval_mode,
                "execucao_approval_mode": approval_mode,
            },
        )

    if policy_required_approvers != required_approvers:
        _raise_validation_error(
            code="REQUIRED_APPROVERS_MISMATCH",
            message="required_approvers divergente entre batch_approval_policy e execucao",
            action="Propague required_approvers consistente entre politica e execucao.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "policy_required_approvers": str(policy_required_approvers),
                "execucao_required_approvers": str(required_approvers),
            },
        )

    if approver_roles_count < required_approvers:
        _raise_validation_error(
            code="INVALID_APPROVER_ROLES_COUNT",
            message="approver_roles_count menor que required_approvers",
            action="Ajuste approver_roles_count para ser >= required_approvers.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if approval_mode == "single_reviewer" and required_approvers != 1:
        _raise_validation_error(
            code="INVALID_APPROVAL_MODE_CONFIGURATION",
            message="approval_mode single_reviewer exige required_approvers=1",
            action="Ajuste required_approvers para 1 ou use outro approval_mode.",
            correlation_id=correlation_id,
            stage="validation_output",
        )
    if approval_mode in {"dual_control", "committee"} and required_approvers < 2:
        _raise_validation_error(
            code="INVALID_APPROVAL_MODE_CONFIGURATION",
            message=f"approval_mode {approval_mode} exige ao menos 2 aprovadores",
            action="Ajuste required_approvers para valor >= 2.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if max_pending_batches < batch_size:
        _raise_validation_error(
            code="INVALID_PENDING_BATCH_CAPACITY",
            message="max_pending_batches nao pode ser menor que batch_size",
            action="Ajuste max_pending_batches para valor maior ou igual ao batch_size.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if approval_queue_capacity != max_pending_batches:
        _raise_validation_error(
            code="INVALID_APPROVAL_QUEUE_CAPACITY",
            message="approval_queue_capacity divergente de max_pending_batches",
            action="Sincronize approval_queue_capacity com max_pending_batches.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "approval_queue_capacity": str(approval_queue_capacity),
                "max_pending_batches": str(max_pending_batches),
            },
        )

    if (batches_approved + batches_rejected + batches_escalated) > batches_received:
        _raise_validation_error(
            code="INVALID_BATCH_OUTCOME_COUNTS",
            message="soma de approved/rejected/escalated excede batches_received",
            action="Ajuste metricas para approved+rejected+escalated <= batches_received.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if pending_batches > batches_received:
        _raise_validation_error(
            code="INVALID_PENDING_BATCHES",
            message="pending_batches nao pode ser maior que batches_received",
            action="Ajuste pending_batches para refletir batches pendentes reais.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if pending_batches > approval_queue_capacity and not approval_overflow_detected:
        _raise_validation_error(
            code="APPROVAL_QUEUE_OVERFLOW_NOT_FLAGGED",
            message=(
                "pending_batches excede approval_queue_capacity sem "
                "approval_overflow_detected=true"
            ),
            action="Sinalize approval_overflow_detected=true quando pending_batches exceder capacidade.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if not allow_partial_approval and partial_approvals > 0:
        _raise_validation_error(
            code="INVALID_PARTIAL_APPROVALS",
            message="partial_approvals deve ser zero quando allow_partial_approval=false",
            action="Retorne partial_approvals=0 ou habilite allow_partial_approval.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if allow_partial_approval and partial_approvals > batches_received:
        _raise_validation_error(
            code="INVALID_PARTIAL_APPROVAL_COUNT",
            message="partial_approvals nao pode ser maior que batches_received",
            action="Ajuste partial_approvals para <= batches_received.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if not allow_partial_approval and approvals_recorded < (batches_approved * required_approvers):
        _raise_validation_error(
            code="INSUFFICIENT_APPROVAL_RECORDS",
            message="approvals_recorded insuficiente para batches_approved",
            action="Ajuste approvals_recorded para >= batches_approved * required_approvers.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if conflicts_detected > batches_received:
        _raise_validation_error(
            code="INVALID_CONFLICTS_DETECTED",
            message="conflicts_detected nao pode ser maior que batches_received",
            action="Ajuste conflicts_detected para refletir conflitos processados.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if auto_lock_on_conflict and auto_locked_batches < conflicts_detected:
        _raise_validation_error(
            code="INVALID_AUTO_LOCK_COUNTS",
            message="auto_locked_batches menor que conflicts_detected com auto_lock_on_conflict=true",
            action="Ajuste auto_locked_batches para cobrir conflitos detectados.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if (not auto_lock_on_conflict) and auto_locked_batches > 0:
        _raise_validation_error(
            code="INVALID_AUTO_LOCK_CONFIGURATION",
            message="auto_locked_batches deve ser zero quando auto_lock_on_conflict=false",
            action="Retorne auto_locked_batches=0 ou habilite auto_lock_on_conflict.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if (batches_rejected > 0 or batches_escalated > 0) and require_justification and justifications_missing > 0:
        _raise_validation_error(
            code="MISSING_APPROVAL_JUSTIFICATIONS",
            message="faltam justificativas obrigatorias para rejeicoes/escalonamentos",
            action="Garanta justificativas para todos os casos rejeitados ou escalados.",
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

    observability_points = get_s3_workbench_observability_integration_points()
    expected_core_module = observability_points["workbench_revisao_s3_core_module"]

    expected_points = {
        "work_s3_prepare_endpoint": EXPECTED_PREPARE_ENDPOINT,
        "work_s3_execute_endpoint": EXPECTED_EXECUTE_ENDPOINT,
        "workbench_revisao_router_module": EXPECTED_ROUTER_MODULE,
        "workbench_revisao_s3_core_module": expected_core_module,
        "workbench_revisao_s3_validation_module": EXPECTED_VALIDATION_MODULE,
    }
    for key, expected_value in expected_points.items():
        value = str(pontos_integracao.get(key, "")).strip()
        if value != expected_value:
            _raise_validation_error(
                code="INVALID_INTEGRATION_POINT",
                message=f"Ponto de integracao invalido para {key}: {value}",
                action=(
                    "Atualize pontos_integracao para refletir endpoints e modulos "
                    "tecnicos esperados da Sprint 3."
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
        "workbench_revisao_s3_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "workflow_id": str(flow_output.get("workflow_id", "")),
            "dataset_name": str(flow_output.get("dataset_name", "")),
        },
    )
    return S3WorkbenchFlowOutputValidationResult(
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
    if contract_version == "work.s3.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "works3coreevt-",
                "flow_completed_event_id": "works3coreevt-",
            },
        )

    raise S3WorkbenchValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contrato work.s3.core.v1.",
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
        event_name="workbench_revisao_s3_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "workbench_revisao_s3_validation_error",
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
    raise S3WorkbenchValidationError(
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
    approval_mode: str | None = None,
    required_approvers: int | None = None,
    approver_roles_count: int | None = None,
    batch_size: int | None = None,
    max_pending_batches: int | None = None,
    approval_sla_hours: int | None = None,
    batches_received: int | None = None,
    batches_approved: int | None = None,
    batches_rejected: int | None = None,
    batches_escalated: int | None = None,
    pending_batches: int | None = None,
    approvals_recorded: int | None = None,
    conflicts_detected: int | None = None,
    auto_locked_batches: int | None = None,
    partial_approvals: int | None = None,
    justifications_missing: int | None = None,
    approval_queue_capacity: int | None = None,
    approval_overflow_detected: bool | None = None,
    require_justification: bool | None = None,
    allow_partial_approval: bool | None = None,
    auto_lock_on_conflict: bool | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S3WorkbenchObservabilityInput(
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
        approval_mode=approval_mode,
        required_approvers=required_approvers,
        approver_roles_count=approver_roles_count,
        batch_size=batch_size,
        max_pending_batches=max_pending_batches,
        approval_sla_hours=approval_sla_hours,
        batches_received=batches_received,
        batches_approved=batches_approved,
        batches_rejected=batches_rejected,
        batches_escalated=batches_escalated,
        pending_batches=pending_batches,
        approvals_recorded=approvals_recorded,
        conflicts_detected=conflicts_detected,
        auto_locked_batches=auto_locked_batches,
        partial_approvals=partial_approvals,
        justifications_missing=justifications_missing,
        approval_queue_capacity=approval_queue_capacity,
        approval_overflow_detected=approval_overflow_detected,
        require_justification=require_justification,
        allow_partial_approval=allow_partial_approval,
        auto_lock_on_conflict=auto_lock_on_conflict,
        context=context,
    )
    event = build_s3_workbench_observability_event(payload)
    log_s3_workbench_observability_event(event)
    return event
