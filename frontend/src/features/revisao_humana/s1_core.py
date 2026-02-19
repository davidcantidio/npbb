"""Main flow for WORK Sprint 1 field-review queue with evidence.

This module executes the Sprint 1 core path:
1) validate input and resolve Sprint 1 scaffold policy;
2) execute one review-queue build pass (dry-run by default);
3) return a stable output contract for API and integration layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s1_scaffold import (
    S1WorkbenchScaffoldError,
    S1WorkbenchScaffoldRequest,
    build_s1_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s1.core")

CONTRACT_VERSION = "work.s1.core.v1"
BACKEND_WORK_S1_EXECUTE_ENDPOINT = "/internal/revisao-humana/s1/execute"

WORK_S1_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
WORK_S1_FAILED_STATUSES = {
    "failed",
    "fatal_error",
    "timeout",
    "transient_error",
    "retryable_failure",
}
WORK_S1_ALLOWED_EXEC_STATUSES = WORK_S1_SUCCESS_STATUSES | WORK_S1_FAILED_STATUSES


class S1WorkbenchCoreError(RuntimeError):
    """Raised when WORK Sprint 1 core flow fails."""

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
class S1WorkbenchCoreInput:
    """Input contract consumed by WORK Sprint 1 core flow."""

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

    def to_scaffold_request(self, *, correlation_id: str) -> S1WorkbenchScaffoldRequest:
        """Build scaffold request using WORK Sprint 1 stable fields."""

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
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1WorkbenchCoreOutput:
    """Output contract returned by WORK Sprint 1 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    review_queue_policy: dict[str, Any]
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
            "review_queue_policy": self.review_queue_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_workbench_revisao_s1_main_flow(
    flow_input: S1WorkbenchCoreInput,
    *,
    execute_queue_builder: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S1WorkbenchCoreOutput:
    """Execute WORK Sprint 1 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with queue policy metadata and guardrails.
        execute_queue_builder: Optional callback responsible for one queue
            build execution. It receives an execution context and must return a
            dictionary with `status` and queue diagnostics fields.

    Returns:
        S1WorkbenchCoreOutput: Stable output with queue policy, execution
            diagnostics, and observability identifiers.

    Raises:
        S1WorkbenchCoreError: If scaffold validation fails, execution response
            is invalid, or queue build execution fails.
    """

    correlation_id = flow_input.correlation_id or f"work-s1-{uuid4().hex[:12]}"
    queue_builder = execute_queue_builder or _default_queue_builder
    started_event_id = _new_event_id()
    logger.info(
        "workbench_revisao_s1_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "workflow_id": flow_input.workflow_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "default_priority": flow_input.default_priority,
            "max_queue_size": flow_input.max_queue_size,
        },
    )

    try:
        scaffold = build_s1_workbench_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        queue_policy = dict(scaffold.review_queue_policy)
        max_queue_size = int(queue_policy.get("max_queue_size", 0))
        required_fields_count = int(queue_policy.get("required_fields_count", 0))
        evidence_sources_count = int(queue_policy.get("evidence_sources_count", 0))
        reviewer_roles_count = int(queue_policy.get("reviewer_roles_count", 0))
        auto_assignment_enabled = bool(queue_policy.get("auto_assignment_enabled", False))

        queue_context = {
            "correlation_id": correlation_id,
            "workflow_id": scaffold.workflow_id,
            "dataset_name": scaffold.dataset_name,
            "entity_kind": queue_policy.get("entity_kind"),
            "default_priority": queue_policy.get("default_priority"),
            "required_fields_count": required_fields_count,
            "evidence_sources_count": evidence_sources_count,
            "reviewer_roles_count": reviewer_roles_count,
            "max_queue_size": max_queue_size,
            "sla_hours": int(queue_policy.get("sla_hours", 0)),
            "auto_assignment_enabled": auto_assignment_enabled,
        }

        response = queue_builder(queue_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="queue_build",
            max_queue_size=max_queue_size,
        )

        status = normalized["status"]
        generated_items = int(normalized["generated_items"])
        critical_items = int(normalized["critical_items"])
        assigned_items = int(normalized["assigned_items"])
        overflow_detected = bool(normalized["overflow_detected"])
        queue_size = int(normalized["queue_size"])

        if critical_items > generated_items:
            raise S1WorkbenchCoreError(
                code="INVALID_CRITICAL_ITEMS_COUNT",
                message="critical_items nao pode ser maior que generated_items",
                action="Ajuste retorno do executor para critical_items <= generated_items.",
                correlation_id=correlation_id,
                stage="queue_build",
            )

        if assigned_items > generated_items:
            raise S1WorkbenchCoreError(
                code="INVALID_ASSIGNED_ITEMS_COUNT",
                message="assigned_items nao pode ser maior que generated_items",
                action="Ajuste retorno do executor para assigned_items <= generated_items.",
                correlation_id=correlation_id,
                stage="queue_build",
            )

        if auto_assignment_enabled and generated_items > 0 and assigned_items <= 0:
            raise S1WorkbenchCoreError(
                code="AUTO_ASSIGNMENT_WITHOUT_ASSIGNMENTS",
                message="auto_assignment_enabled ativo sem atribuicoes na fila de revisao",
                action="Retorne assigned_items > 0 ou desative auto_assignment_enabled.",
                correlation_id=correlation_id,
                stage="queue_build",
            )

        completed_event_id = _new_event_id()
        logger.info(
            "workbench_revisao_s1_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "workflow_id": scaffold.workflow_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "generated_items": generated_items,
                "critical_items": critical_items,
                "assigned_items": assigned_items,
                "overflow_detected": overflow_detected,
            },
        )

        if status not in WORK_S1_SUCCESS_STATUSES:
            raise S1WorkbenchCoreError(
                code="WORK_S1_QUEUE_BUILD_FAILED",
                message=f"Execucao da fila WORK S1 falhou com status '{status}'",
                action=(
                    "Revisar logs do executor de fila e validar regras de campos obrigatorios, "
                    "evidencias e capacidade da fila."
                ),
                correlation_id=correlation_id,
                stage="queue_build",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["workbench_revisao_s1_core_module"] = (
            "frontend.src.features.revisao_humana.s1_core.execute_workbench_revisao_s1_main_flow"
        )
        pontos_integracao["work_s1_execute_endpoint"] = BACKEND_WORK_S1_EXECUTE_ENDPOINT

        return S1WorkbenchCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            workflow_id=scaffold.workflow_id,
            dataset_name=scaffold.dataset_name,
            review_queue_policy=queue_policy,
            execucao={
                "status": status,
                "queue_build_result_id": str(
                    normalized.get("queue_build_result_id", f"works1queue-{uuid4().hex[:12]}")
                ),
                "generated_items": generated_items,
                "queue_size": queue_size,
                "queue_capacity": max(0, max_queue_size - queue_size),
                "critical_items": critical_items,
                "assigned_items": assigned_items,
                "pending_fields_count": int(normalized["pending_fields_count"]),
                "overflow_detected": overflow_detected,
                "auto_assignment_enabled": auto_assignment_enabled,
                "evidence_sources_count": evidence_sources_count,
                "decision_reason": str(
                    normalized.get("decision_reason", "dry_run_workbench_review_queue_build")
                ),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S1WorkbenchScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "workbench_revisao_s1_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S1WorkbenchCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S1WorkbenchCoreError:
        raise
    except Exception as exc:  # noqa: BLE001
        failed_event_id = _new_event_id()
        logger.error(
            "workbench_revisao_s1_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S1WorkbenchCoreError(
            code="WORK_S1_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal WORK S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor WORK S1.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
    max_queue_size: int,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S1WorkbenchCoreError(
            code="INVALID_QUEUE_BUILDER_RESPONSE",
            message="Executor de fila retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e metricas da fila.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in WORK_S1_ALLOWED_EXEC_STATUSES:
        raise S1WorkbenchCoreError(
            code="INVALID_QUEUE_BUILD_STATUS",
            message=f"Status de execucao da fila invalido: {response.get('status')}",
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
        "generated_items",
        "critical_items",
        "assigned_items",
        "pending_fields_count",
    ):
        value = normalized.get(field_name, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise S1WorkbenchCoreError(
                code=f"INVALID_{field_name.upper()}",
                message=f"{field_name} invalido: {value}",
                action=f"Retorne {field_name} como inteiro >= 0.",
                correlation_id=correlation_id,
                stage=stage,
            )
        normalized[field_name] = int(value)

    overflow_detected = normalized.get("overflow_detected")
    if overflow_detected is None:
        overflow_detected = normalized["generated_items"] > max_queue_size
    if not isinstance(overflow_detected, bool):
        raise S1WorkbenchCoreError(
            code="INVALID_OVERFLOW_DETECTED",
            message=f"overflow_detected invalido: {overflow_detected}",
            action="Retorne overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage=stage,
        )
    normalized["overflow_detected"] = overflow_detected

    if normalized["generated_items"] > max_queue_size and not overflow_detected:
        raise S1WorkbenchCoreError(
            code="QUEUE_SIZE_EXCEEDS_LIMIT",
            message=(
                "generated_items excede max_queue_size sem sinalizar overflow_detected"
            ),
            action="Sinalize overflow_detected=true quando generated_items > max_queue_size.",
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized["queue_size"] = min(normalized["generated_items"], max_queue_size)
    return normalized


def _default_queue_builder(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one WORK Sprint 1 queue-build pass in dry-run mode.

    Args:
        context: Structured queue-building context with policy metadata.

    Returns:
        dict[str, Any]: Dry-run queue-build execution result.
    """

    required_fields_count = int(context.get("required_fields_count", 0))
    evidence_sources_count = int(context.get("evidence_sources_count", 0))
    reviewer_roles_count = int(context.get("reviewer_roles_count", 0))
    max_queue_size = int(context.get("max_queue_size", 0))
    default_priority = str(context.get("default_priority", "media")).strip().lower()
    auto_assignment_enabled = bool(context.get("auto_assignment_enabled", False))

    base_generated_items = max(
        required_fields_count,
        required_fields_count * max(1, evidence_sources_count),
    )
    generated_items = min(base_generated_items, max_queue_size)
    overflow_detected = base_generated_items > max_queue_size
    critical_items = (
        min(generated_items, 1) if default_priority in {"alta", "critica"} else 0
    )
    assigned_items = (
        min(generated_items, max(1, reviewer_roles_count))
        if auto_assignment_enabled and generated_items > 0
        else 0
    )

    return {
        "status": "succeeded",
        "queue_build_result_id": f"works1queue-{uuid4().hex[:12]}",
        "generated_items": generated_items,
        "critical_items": critical_items,
        "assigned_items": assigned_items,
        "pending_fields_count": required_fields_count,
        "overflow_detected": overflow_detected,
        "decision_reason": "dry_run_field_review_queue_build",
    }


def _new_event_id() -> str:
    return f"works1coreevt-{uuid4().hex[:12]}"
