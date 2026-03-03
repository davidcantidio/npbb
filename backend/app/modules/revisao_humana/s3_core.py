"""Main flow for WORK Sprint 3 batch operations and approval flow.

This module executes the Sprint 3 core path:
1) validate input and resolve Sprint 3 scaffold policy;
2) execute one batch-approval pass (dry-run by default);
3) return a stable output contract for API and integration layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s3_scaffold import (
    S3WorkbenchScaffoldError,
    S3WorkbenchScaffoldRequest,
    build_s3_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s3.core")

CONTRACT_VERSION = "work.s3.core.v1"
BACKEND_WORK_S3_EXECUTE_ENDPOINT = "/internal/revisao-humana/s3/execute"

WORK_S3_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
WORK_S3_FAILED_STATUSES = {
    "failed",
    "fatal_error",
    "timeout",
    "transient_error",
    "retryable_failure",
}
WORK_S3_ALLOWED_EXEC_STATUSES = WORK_S3_SUCCESS_STATUSES | WORK_S3_FAILED_STATUSES
WORK_S3_ALLOWED_APPROVAL_MODES = {"single_reviewer", "dual_control", "committee"}


class S3WorkbenchCoreError(RuntimeError):
    """Raised when WORK Sprint 3 core flow fails."""

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
class S3WorkbenchCoreInput:
    """Input contract consumed by WORK Sprint 3 core flow."""

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

    def to_scaffold_request(self, *, correlation_id: str) -> S3WorkbenchScaffoldRequest:
        """Build scaffold request using WORK Sprint 3 stable fields."""

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
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3WorkbenchCoreOutput:
    """Output contract returned by WORK Sprint 3 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    batch_approval_policy: dict[str, Any]
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
            "batch_approval_policy": self.batch_approval_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_workbench_revisao_s3_main_flow(
    flow_input: S3WorkbenchCoreInput,
    *,
    execute_batch_approval: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S3WorkbenchCoreOutput:
    """Execute WORK Sprint 3 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with batch approval policy metadata and
            operational guardrails.
        execute_batch_approval: Optional callback responsible for one
            batch-approval execution pass. It receives an execution context and
            must return a dictionary with `status` and batch metrics.

    Returns:
        S3WorkbenchCoreOutput: Stable output with batch policy, execution
            diagnostics, and observability identifiers.

    Raises:
        S3WorkbenchCoreError: If scaffold validation fails, execution response
            is invalid, or batch approval execution fails.
    """

    correlation_id = flow_input.correlation_id or f"work-s3-{uuid4().hex[:12]}"
    approval_executor = execute_batch_approval or _default_batch_approval_executor
    started_event_id = _new_event_id()
    logger.info(
        "workbench_revisao_s3_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "workflow_id": flow_input.workflow_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "approval_mode": flow_input.approval_mode,
            "required_approvers": flow_input.required_approvers,
            "batch_size": flow_input.batch_size,
        },
    )

    try:
        scaffold = build_s3_workbench_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        batch_approval_policy = dict(scaffold.batch_approval_policy)
        batch_size = int(batch_approval_policy.get("batch_size", 0))
        max_pending_batches = int(batch_approval_policy.get("max_pending_batches", 0))
        approval_mode = str(batch_approval_policy.get("approval_mode", "")).strip().lower()
        required_approvers = int(batch_approval_policy.get("required_approvers", 0))
        approver_roles_count = int(batch_approval_policy.get("approver_roles_count", 0))
        approval_sla_hours = int(batch_approval_policy.get("approval_sla_hours", 0))
        require_justification = bool(batch_approval_policy.get("require_justification", False))
        allow_partial_approval = bool(batch_approval_policy.get("allow_partial_approval", False))
        auto_lock_on_conflict = bool(batch_approval_policy.get("auto_lock_on_conflict", False))
        approval_queue_capacity = max_pending_batches

        batch_context = {
            "correlation_id": correlation_id,
            "workflow_id": scaffold.workflow_id,
            "dataset_name": scaffold.dataset_name,
            "entity_kind": batch_approval_policy.get("entity_kind"),
            "approval_mode": approval_mode,
            "required_approvers": required_approvers,
            "approver_roles_count": approver_roles_count,
            "approval_sla_hours": approval_sla_hours,
            "batch_size": batch_size,
            "max_pending_batches": max_pending_batches,
            "approval_queue_capacity": approval_queue_capacity,
            "require_justification": require_justification,
            "allow_partial_approval": allow_partial_approval,
            "auto_lock_on_conflict": auto_lock_on_conflict,
        }

        response = approval_executor(batch_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="approval",
            approval_queue_capacity=approval_queue_capacity,
        )

        status = normalized["status"]
        batches_received = int(normalized["batches_received"])
        batches_approved = int(normalized["batches_approved"])
        batches_rejected = int(normalized["batches_rejected"])
        batches_escalated = int(normalized["batches_escalated"])
        pending_batches = int(normalized["pending_batches"])
        approvals_recorded = int(normalized["approvals_recorded"])
        conflicts_detected = int(normalized["conflicts_detected"])
        auto_locked_batches = int(normalized["auto_locked_batches"])
        partial_approvals = int(normalized["partial_approvals"])
        justifications_missing = int(normalized["justifications_missing"])
        approval_overflow_detected = bool(normalized["approval_overflow_detected"])

        if approval_mode not in WORK_S3_ALLOWED_APPROVAL_MODES:
            raise S3WorkbenchCoreError(
                code="INVALID_APPROVAL_MODE",
                message=f"approval_mode invalido: {approval_mode}",
                action="Use approval_mode valido: single_reviewer, dual_control ou committee.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if required_approvers <= 0:
            raise S3WorkbenchCoreError(
                code="INVALID_REQUIRED_APPROVERS",
                message="required_approvers deve ser maior que zero",
                action="Ajuste required_approvers para inteiro >= 1.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if approver_roles_count < required_approvers:
            raise S3WorkbenchCoreError(
                code="INSUFFICIENT_APPROVER_ROLES",
                message="approver_roles_count menor que required_approvers",
                action="Ajuste approver_roles ou required_approvers para manter consistencia.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if (batches_approved + batches_rejected + batches_escalated) > batches_received:
            raise S3WorkbenchCoreError(
                code="INVALID_BATCH_OUTCOME_COUNTS",
                message="soma de outcomes excede batches_received",
                action="Ajuste metricas para approved+rejected+escalated <= batches_received.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if pending_batches > batches_received:
            raise S3WorkbenchCoreError(
                code="INVALID_PENDING_BATCHES",
                message="pending_batches nao pode ser maior que batches_received",
                action="Ajuste pending_batches para refletir batches pendentes reais.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if pending_batches > approval_queue_capacity:
            raise S3WorkbenchCoreError(
                code="PENDING_BATCHES_EXCEED_CAPACITY",
                message="pending_batches excede approval_queue_capacity",
                action="Ajuste pending_batches ou aumente max_pending_batches no contrato.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if (not allow_partial_approval) and partial_approvals > 0:
            raise S3WorkbenchCoreError(
                code="INVALID_PARTIAL_APPROVALS",
                message="partial_approvals deve ser zero quando allow_partial_approval=false",
                action="Retorne partial_approvals=0 ou habilite allow_partial_approval.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if allow_partial_approval and partial_approvals > batches_received:
            raise S3WorkbenchCoreError(
                code="INVALID_PARTIAL_APPROVAL_COUNT",
                message="partial_approvals nao pode ser maior que batches_received",
                action="Ajuste partial_approvals para <= batches_received.",
                correlation_id=correlation_id,
                stage="approval",
            )

        min_approvals_required = batches_approved * required_approvers
        if (not allow_partial_approval) and approvals_recorded < min_approvals_required:
            raise S3WorkbenchCoreError(
                code="INSUFFICIENT_APPROVAL_RECORDS",
                message="approvals_recorded insuficiente para batches_approved",
                action="Ajuste approvals_recorded para >= batches_approved * required_approvers.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if conflicts_detected > batches_received:
            raise S3WorkbenchCoreError(
                code="INVALID_CONFLICTS_DETECTED",
                message="conflicts_detected nao pode ser maior que batches_received",
                action="Ajuste conflicts_detected para refletir conflitos processados.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if auto_lock_on_conflict and auto_locked_batches < conflicts_detected:
            raise S3WorkbenchCoreError(
                code="INVALID_AUTO_LOCK_COUNTS",
                message="auto_locked_batches menor que conflicts_detected com auto_lock_on_conflict=true",
                action="Ajuste auto_locked_batches para cobrir conflitos detectados.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if (not auto_lock_on_conflict) and auto_locked_batches > 0:
            raise S3WorkbenchCoreError(
                code="INVALID_AUTO_LOCK_CONFIGURATION",
                message="auto_locked_batches deve ser zero quando auto_lock_on_conflict=false",
                action="Retorne auto_locked_batches=0 ou habilite auto_lock_on_conflict.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if (
            (batches_rejected > 0 or batches_escalated > 0)
            and require_justification
            and justifications_missing > 0
        ):
            raise S3WorkbenchCoreError(
                code="MISSING_APPROVAL_JUSTIFICATIONS",
                message="faltam justificativas obrigatorias para rejeicoes/escalonamentos",
                action="Garanta justificativas para todos os casos rejeitados ou escalados.",
                correlation_id=correlation_id,
                stage="approval",
            )

        if pending_batches > approval_queue_capacity and not approval_overflow_detected:
            raise S3WorkbenchCoreError(
                code="APPROVAL_QUEUE_OVERFLOW_NOT_FLAGGED",
                message="pending_batches excede capacidade sem approval_overflow_detected=true",
                action="Sinalize overflow quando pending_batches > approval_queue_capacity.",
                correlation_id=correlation_id,
                stage="approval",
            )

        completed_event_id = _new_event_id()
        logger.info(
            "workbench_revisao_s3_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "workflow_id": scaffold.workflow_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "batches_received": batches_received,
                "batches_approved": batches_approved,
                "batches_rejected": batches_rejected,
                "batches_escalated": batches_escalated,
                "pending_batches": pending_batches,
                "approval_overflow_detected": approval_overflow_detected,
            },
        )

        if status not in WORK_S3_SUCCESS_STATUSES:
            raise S3WorkbenchCoreError(
                code="WORK_S3_BATCH_APPROVAL_FAILED",
                message=f"Execucao de aprovacao em lote WORK S3 falhou com status '{status}'",
                action=(
                    "Revisar logs do executor de lote e validar regras de aprovacao, "
                    "justificativa, conflitos e capacidade."
                ),
                correlation_id=correlation_id,
                stage="approval",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["workbench_revisao_s3_core_module"] = (
            "app.modules.revisao_humana.s3_core.execute_workbench_revisao_s3_main_flow"
        )
        pontos_integracao["work_s3_execute_endpoint"] = BACKEND_WORK_S3_EXECUTE_ENDPOINT

        return S3WorkbenchCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            workflow_id=scaffold.workflow_id,
            dataset_name=scaffold.dataset_name,
            batch_approval_policy=batch_approval_policy,
            execucao={
                "status": status,
                "batch_approval_result_id": str(
                    normalized.get("batch_approval_result_id", f"works3batch-{uuid4().hex[:12]}")
                ),
                "batches_received": batches_received,
                "batches_approved": batches_approved,
                "batches_rejected": batches_rejected,
                "batches_escalated": batches_escalated,
                "pending_batches": pending_batches,
                "approvals_recorded": approvals_recorded,
                "conflicts_detected": conflicts_detected,
                "auto_locked_batches": auto_locked_batches,
                "partial_approvals": partial_approvals,
                "justifications_missing": justifications_missing,
                "approval_queue_capacity": approval_queue_capacity,
                "approval_overflow_detected": approval_overflow_detected,
                "approval_mode": approval_mode,
                "required_approvers": required_approvers,
                "require_justification": require_justification,
                "allow_partial_approval": allow_partial_approval,
                "auto_lock_on_conflict": auto_lock_on_conflict,
                "decision_reason": str(
                    normalized.get("decision_reason", "dry_run_batch_approval_execution")
                ),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S3WorkbenchScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "workbench_revisao_s3_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S3WorkbenchCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S3WorkbenchCoreError:
        raise
    except Exception as exc:  # noqa: BLE001
        failed_event_id = _new_event_id()
        logger.error(
            "workbench_revisao_s3_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3WorkbenchCoreError(
            code="WORK_S3_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal WORK S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor WORK S3.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
    approval_queue_capacity: int,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S3WorkbenchCoreError(
            code="INVALID_BATCH_APPROVAL_RESPONSE",
            message="Executor de lote retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e metricas de aprovacao em lote.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in WORK_S3_ALLOWED_EXEC_STATUSES:
        raise S3WorkbenchCoreError(
            code="INVALID_BATCH_APPROVAL_STATUS",
            message=f"Status de execucao em lote invalido: {response.get('status')}",
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
        "batches_received",
        "batches_approved",
        "batches_rejected",
        "batches_escalated",
        "pending_batches",
        "approvals_recorded",
        "conflicts_detected",
        "auto_locked_batches",
        "partial_approvals",
        "justifications_missing",
    ):
        value = normalized.get(field_name, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise S3WorkbenchCoreError(
                code=f"INVALID_{field_name.upper()}",
                message=f"{field_name} invalido: {value}",
                action=f"Retorne {field_name} como inteiro >= 0.",
                correlation_id=correlation_id,
                stage=stage,
            )
        normalized[field_name] = int(value)

    approval_overflow_detected = normalized.get("approval_overflow_detected")
    if approval_overflow_detected is None:
        approval_overflow_detected = normalized["pending_batches"] > approval_queue_capacity
    if not isinstance(approval_overflow_detected, bool):
        raise S3WorkbenchCoreError(
            code="INVALID_APPROVAL_OVERFLOW_DETECTED",
            message=f"approval_overflow_detected invalido: {approval_overflow_detected}",
            action="Retorne approval_overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage=stage,
        )
    normalized["approval_overflow_detected"] = approval_overflow_detected

    return normalized


def _default_batch_approval_executor(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one WORK Sprint 3 batch-approval pass in dry-run mode.

    Args:
        context: Structured batch-approval context with policy metadata.

    Returns:
        dict[str, Any]: Dry-run batch-approval execution result.
    """

    batch_size = int(context.get("batch_size", 0))
    max_pending_batches = int(context.get("max_pending_batches", 0))
    required_approvers = int(context.get("required_approvers", 1))
    approval_mode = str(context.get("approval_mode", "dual_control")).strip().lower()
    allow_partial_approval = bool(context.get("allow_partial_approval", False))
    auto_lock_on_conflict = bool(context.get("auto_lock_on_conflict", False))
    require_justification = bool(context.get("require_justification", False))

    batches_received = max(0, min(batch_size, max_pending_batches))

    if approval_mode == "single_reviewer":
        approval_ratio = 0.70
    elif approval_mode == "committee":
        approval_ratio = 0.45
    else:
        approval_ratio = 0.55

    batches_approved = min(batches_received, int(round(batches_received * approval_ratio)))
    remaining = max(0, batches_received - batches_approved)
    batches_rejected = remaining // 3
    batches_escalated = max(0, remaining - batches_rejected)

    if allow_partial_approval and batches_escalated > 0:
        partial_approvals = min(batches_escalated, max(1, batches_escalated // 2))
    else:
        partial_approvals = 0

    pending_batches = max(0, batches_received - batches_approved - batches_rejected - batches_escalated)
    conflicts_detected = min(batches_escalated, max(0, batches_received // 10))
    auto_locked_batches = conflicts_detected if auto_lock_on_conflict else 0
    approvals_recorded = (batches_approved * max(1, required_approvers)) + partial_approvals
    justifications_missing = 0 if require_justification else 0
    approval_overflow_detected = pending_batches > max_pending_batches

    return {
        "status": "succeeded",
        "batch_approval_result_id": f"works3batch-{uuid4().hex[:12]}",
        "batches_received": batches_received,
        "batches_approved": batches_approved,
        "batches_rejected": batches_rejected,
        "batches_escalated": batches_escalated,
        "pending_batches": pending_batches,
        "approvals_recorded": approvals_recorded,
        "conflicts_detected": conflicts_detected,
        "auto_locked_batches": auto_locked_batches,
        "partial_approvals": partial_approvals,
        "justifications_missing": justifications_missing,
        "approval_overflow_detected": approval_overflow_detected,
        "decision_reason": "dry_run_batch_approval_execution",
    }


def _new_event_id() -> str:
    return f"works3coreevt-{uuid4().hex[:12]}"
