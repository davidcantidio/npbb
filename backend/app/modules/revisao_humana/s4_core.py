"""Main flow for WORK Sprint 4 audit, SLA, and productivity operations.

This module executes the Sprint 4 core path:
1) validate input and resolve Sprint 4 scaffold policy;
2) execute one operational-audit pass (dry-run by default);
3) return a stable output contract for API and integration layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s4_scaffold import (
    S4WorkbenchScaffoldError,
    S4WorkbenchScaffoldRequest,
    build_s4_workbench_scaffold,
)


logger = logging.getLogger("npbb.frontend.revisao_humana.s4.core")

CONTRACT_VERSION = "work.s4.core.v1"
BACKEND_WORK_S4_EXECUTE_ENDPOINT = "/internal/revisao-humana/s4/execute"

WORK_S4_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
WORK_S4_FAILED_STATUSES = {
    "failed",
    "fatal_error",
    "timeout",
    "transient_error",
    "retryable_failure",
}
WORK_S4_ALLOWED_EXEC_STATUSES = WORK_S4_SUCCESS_STATUSES | WORK_S4_FAILED_STATUSES
WORK_S4_ALLOWED_AUDIT_MODES = {"full_trace", "sampled_trace", "compliance_only"}


class S4WorkbenchCoreError(RuntimeError):
    """Raised when WORK Sprint 4 core flow fails."""

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
class S4WorkbenchCoreInput:
    """Input contract consumed by WORK Sprint 4 core flow."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v4"
    owner_team: str = "etl"
    audit_dimensions: tuple[str, ...] | None = None
    change_channels: tuple[str, ...] | None = None
    audit_mode: str = "full_trace"
    sla_target_minutes: int = 120
    sla_warning_threshold_minutes: int = 90
    sla_breach_grace_minutes: int = 15
    productivity_window_hours: int = 8
    minimum_actions_per_window: int = 10
    require_change_reason: bool = True
    capture_before_after_state: bool = True
    enable_anomaly_alerts: bool = True
    reviewer_roles: tuple[str, ...] | None = None
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S4WorkbenchScaffoldRequest:
        """Build scaffold request using WORK Sprint 4 stable fields."""

        return S4WorkbenchScaffoldRequest(
            workflow_id=self.workflow_id,
            dataset_name=self.dataset_name,
            entity_kind=self.entity_kind,
            schema_version=self.schema_version,
            owner_team=self.owner_team,
            audit_dimensions=self.audit_dimensions,
            change_channels=self.change_channels,
            audit_mode=self.audit_mode,
            sla_target_minutes=self.sla_target_minutes,
            sla_warning_threshold_minutes=self.sla_warning_threshold_minutes,
            sla_breach_grace_minutes=self.sla_breach_grace_minutes,
            productivity_window_hours=self.productivity_window_hours,
            minimum_actions_per_window=self.minimum_actions_per_window,
            require_change_reason=self.require_change_reason,
            capture_before_after_state=self.capture_before_after_state,
            enable_anomaly_alerts=self.enable_anomaly_alerts,
            reviewer_roles=self.reviewer_roles,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4WorkbenchCoreOutput:
    """Output contract returned by WORK Sprint 4 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    operational_audit_policy: dict[str, Any]
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
            "operational_audit_policy": self.operational_audit_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_workbench_revisao_s4_main_flow(
    flow_input: S4WorkbenchCoreInput,
    *,
    execute_operational_audit: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S4WorkbenchCoreOutput:
    """Execute WORK Sprint 4 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with audit, SLA, and productivity
            guardrails.
        execute_operational_audit: Optional callback responsible for one
            operational-audit execution pass. It receives an execution context
            and must return a dictionary with `status` and audit metrics.

    Returns:
        S4WorkbenchCoreOutput: Stable output with operational policy,
            execution diagnostics, and observability identifiers.

    Raises:
        S4WorkbenchCoreError: If scaffold validation fails, execution response
            is invalid, or operational-audit execution fails.
    """

    correlation_id = flow_input.correlation_id or f"work-s4-{uuid4().hex[:12]}"
    audit_executor = execute_operational_audit or _default_operational_audit_executor
    started_event_id = _new_event_id()
    logger.info(
        "workbench_revisao_s4_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "workflow_id": flow_input.workflow_id,
            "dataset_name": flow_input.dataset_name,
            "entity_kind": flow_input.entity_kind,
            "schema_version": flow_input.schema_version,
            "audit_mode": flow_input.audit_mode,
            "sla_target_minutes": flow_input.sla_target_minutes,
            "productivity_window_hours": flow_input.productivity_window_hours,
        },
    )

    try:
        scaffold = build_s4_workbench_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        operational_audit_policy = dict(scaffold.operational_audit_policy)
        audit_mode = str(operational_audit_policy.get("audit_mode", "")).strip().lower()
        audit_dimensions = tuple(operational_audit_policy.get("audit_dimensions", ()))
        change_channels = tuple(operational_audit_policy.get("change_channels", ()))
        sla_target_minutes = int(operational_audit_policy.get("sla_target_minutes", 0))
        sla_warning_threshold_minutes = int(
            operational_audit_policy.get("sla_warning_threshold_minutes", 0)
        )
        sla_breach_grace_minutes = int(operational_audit_policy.get("sla_breach_grace_minutes", 0))
        productivity_window_hours = int(
            operational_audit_policy.get("productivity_window_hours", 0)
        )
        minimum_actions_per_window = int(
            operational_audit_policy.get("minimum_actions_per_window", 0)
        )
        require_change_reason = bool(operational_audit_policy.get("require_change_reason", False))
        capture_before_after_state = bool(
            operational_audit_policy.get("capture_before_after_state", False)
        )
        enable_anomaly_alerts = bool(operational_audit_policy.get("enable_anomaly_alerts", False))
        reviewer_roles_count = int(operational_audit_policy.get("reviewer_roles_count", 0))

        audit_queue_capacity = max(minimum_actions_per_window * 10, minimum_actions_per_window + 1)
        productivity_target_rate_per_hour = round(
            minimum_actions_per_window / max(1, productivity_window_hours),
            6,
        )

        audit_context = {
            "correlation_id": correlation_id,
            "workflow_id": scaffold.workflow_id,
            "dataset_name": scaffold.dataset_name,
            "entity_kind": operational_audit_policy.get("entity_kind"),
            "audit_mode": audit_mode,
            "audit_dimensions": list(audit_dimensions),
            "change_channels": list(change_channels),
            "sla_target_minutes": sla_target_minutes,
            "sla_warning_threshold_minutes": sla_warning_threshold_minutes,
            "sla_breach_grace_minutes": sla_breach_grace_minutes,
            "productivity_window_hours": productivity_window_hours,
            "minimum_actions_per_window": minimum_actions_per_window,
            "productivity_target_rate_per_hour": productivity_target_rate_per_hour,
            "require_change_reason": require_change_reason,
            "capture_before_after_state": capture_before_after_state,
            "enable_anomaly_alerts": enable_anomaly_alerts,
            "reviewer_roles_count": reviewer_roles_count,
            "audit_queue_capacity": audit_queue_capacity,
        }

        response = audit_executor(audit_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="operational_audit",
            audit_queue_capacity=audit_queue_capacity,
        )

        status = normalized["status"]
        actions_received = int(normalized["actions_received"])
        actions_audited = int(normalized["actions_audited"])
        pending_audit_items = int(normalized["pending_audit_items"])
        sla_warning_breaches = int(normalized["sla_warning_breaches"])
        sla_violations_detected = int(normalized["sla_violations_detected"])
        productivity_alerts = int(normalized["productivity_alerts"])
        anomaly_alerts_triggered = int(normalized["anomaly_alerts_triggered"])
        change_reasons_missing = int(normalized["change_reasons_missing"])
        before_after_missing = int(normalized["before_after_missing"])
        productivity_rate_per_hour = float(normalized["productivity_rate_per_hour"])
        audit_overflow_detected = bool(normalized["audit_overflow_detected"])

        if audit_mode not in WORK_S4_ALLOWED_AUDIT_MODES:
            raise S4WorkbenchCoreError(
                code="INVALID_AUDIT_MODE",
                message=f"audit_mode invalido: {audit_mode}",
                action="Use audit_mode valido: full_trace, sampled_trace ou compliance_only.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if actions_audited > actions_received:
            raise S4WorkbenchCoreError(
                code="INVALID_ACTION_COUNTS",
                message="actions_audited nao pode ser maior que actions_received",
                action="Ajuste metrica para manter actions_audited <= actions_received.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if pending_audit_items > actions_received:
            raise S4WorkbenchCoreError(
                code="INVALID_PENDING_AUDIT_ITEMS",
                message="pending_audit_items nao pode ser maior que actions_received",
                action="Ajuste pending_audit_items para refletir volume real pendente.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if (actions_audited + pending_audit_items) > actions_received:
            raise S4WorkbenchCoreError(
                code="INCONSISTENT_AUDIT_DISTRIBUTION",
                message="actions_audited + pending_audit_items excede actions_received",
                action="Revise distribuicao entre itens auditados e pendentes.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if sla_violations_detected > actions_received:
            raise S4WorkbenchCoreError(
                code="INVALID_SLA_VIOLATION_COUNTS",
                message="sla_violations_detected nao pode ser maior que actions_received",
                action="Ajuste metrica de violacoes para refletir somente acoes recebidas.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if sla_warning_breaches < sla_violations_detected:
            raise S4WorkbenchCoreError(
                code="INCONSISTENT_SLA_COUNTS",
                message="sla_warning_breaches nao pode ser menor que sla_violations_detected",
                action="Garanta warning count >= violation count.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if "produtividade" in audit_dimensions and (
            actions_audited < minimum_actions_per_window and productivity_alerts == 0
        ):
            raise S4WorkbenchCoreError(
                code="MISSING_PRODUCTIVITY_ALERT",
                message="produtividade abaixo do minimo sem alerta operacional",
                action=(
                    "Quando actions_audited < minimum_actions_per_window, "
                    "retorne productivity_alerts > 0."
                ),
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if require_change_reason and change_reasons_missing > 0:
            raise S4WorkbenchCoreError(
                code="MISSING_CHANGE_REASONS",
                message="faltam justificativas obrigatorias de alteracao",
                action="Garanta justificativa para todas as alteracoes auditadas.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if capture_before_after_state and before_after_missing > 0:
            raise S4WorkbenchCoreError(
                code="MISSING_BEFORE_AFTER_STATE",
                message="faltam snapshots before/after obrigatorios para auditoria",
                action="Garanta captura before/after em todos os registros auditados.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if not enable_anomaly_alerts and anomaly_alerts_triggered > 0:
            raise S4WorkbenchCoreError(
                code="INVALID_ANOMALY_ALERT_CONFIGURATION",
                message="anomaly_alerts_triggered deve ser zero quando alerts estao desabilitados",
                action="Retorne anomaly_alerts_triggered=0 ou habilite enable_anomaly_alerts.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        if pending_audit_items > audit_queue_capacity and not audit_overflow_detected:
            raise S4WorkbenchCoreError(
                code="AUDIT_QUEUE_OVERFLOW_NOT_FLAGGED",
                message="pending_audit_items excede capacidade sem audit_overflow_detected=true",
                action="Sinalize overflow quando pendencia exceder audit_queue_capacity.",
                correlation_id=correlation_id,
                stage="operational_audit",
            )

        completed_event_id = _new_event_id()
        logger.info(
            "workbench_revisao_s4_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "workflow_id": scaffold.workflow_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "actions_received": actions_received,
                "actions_audited": actions_audited,
                "pending_audit_items": pending_audit_items,
                "sla_warning_breaches": sla_warning_breaches,
                "sla_violations_detected": sla_violations_detected,
                "productivity_rate_per_hour": productivity_rate_per_hour,
                "audit_overflow_detected": audit_overflow_detected,
            },
        )

        if status not in WORK_S4_SUCCESS_STATUSES:
            raise S4WorkbenchCoreError(
                code="WORK_S4_OPERATIONAL_AUDIT_FAILED",
                message=f"Execucao de auditoria operacional WORK S4 falhou com status '{status}'",
                action=(
                    "Revisar logs do executor e validar consistencia de SLA, "
                    "produtividade e rastreabilidade de alteracoes."
                ),
                correlation_id=correlation_id,
                stage="operational_audit",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["workbench_revisao_s4_core_module"] = (
            "app.modules.revisao_humana.s4_core.execute_workbench_revisao_s4_main_flow"
        )
        pontos_integracao["work_s4_execute_endpoint"] = BACKEND_WORK_S4_EXECUTE_ENDPOINT

        return S4WorkbenchCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            workflow_id=scaffold.workflow_id,
            dataset_name=scaffold.dataset_name,
            operational_audit_policy=operational_audit_policy,
            execucao={
                "status": status,
                "operational_audit_result_id": str(
                    normalized.get("operational_audit_result_id", f"works4audit-{uuid4().hex[:12]}")
                ),
                "actions_received": actions_received,
                "actions_audited": actions_audited,
                "pending_audit_items": pending_audit_items,
                "sla_warning_breaches": sla_warning_breaches,
                "sla_violations_detected": sla_violations_detected,
                "productivity_alerts": productivity_alerts,
                "anomaly_alerts_triggered": anomaly_alerts_triggered,
                "change_reasons_missing": change_reasons_missing,
                "before_after_missing": before_after_missing,
                "productivity_rate_per_hour": round(productivity_rate_per_hour, 6),
                "productivity_target_rate_per_hour": productivity_target_rate_per_hour,
                "audit_queue_capacity": audit_queue_capacity,
                "audit_overflow_detected": audit_overflow_detected,
                "audit_mode": audit_mode,
                "require_change_reason": require_change_reason,
                "capture_before_after_state": capture_before_after_state,
                "enable_anomaly_alerts": enable_anomaly_alerts,
                "decision_reason": str(
                    normalized.get("decision_reason", "dry_run_operational_audit_execution")
                ),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S4WorkbenchScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "workbench_revisao_s4_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S4WorkbenchCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4WorkbenchCoreError:
        raise
    except Exception as exc:  # noqa: BLE001
        failed_event_id = _new_event_id()
        logger.error(
            "workbench_revisao_s4_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4WorkbenchCoreError(
            code="WORK_S4_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal WORK S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor WORK S4.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
    audit_queue_capacity: int,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S4WorkbenchCoreError(
            code="INVALID_OPERATIONAL_AUDIT_RESPONSE",
            message="Executor de auditoria retornou resposta em formato invalido",
            action="Garantir retorno dict com campos 'status' e metricas operacionais.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in WORK_S4_ALLOWED_EXEC_STATUSES:
        raise S4WorkbenchCoreError(
            code="INVALID_OPERATIONAL_AUDIT_STATUS",
            message=f"Status de execucao de auditoria invalido: {response.get('status')}",
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
        "actions_received",
        "actions_audited",
        "pending_audit_items",
        "sla_warning_breaches",
        "sla_violations_detected",
        "productivity_alerts",
        "anomaly_alerts_triggered",
        "change_reasons_missing",
        "before_after_missing",
    ):
        value = normalized.get(field_name, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise S4WorkbenchCoreError(
                code=f"INVALID_{field_name.upper()}",
                message=f"{field_name} invalido: {value}",
                action=f"Retorne {field_name} como inteiro >= 0.",
                correlation_id=correlation_id,
                stage=stage,
            )
        normalized[field_name] = int(value)

    productivity_rate_per_hour = normalized.get("productivity_rate_per_hour", 0.0)
    if isinstance(productivity_rate_per_hour, bool) or not isinstance(
        productivity_rate_per_hour, (int, float)
    ):
        raise S4WorkbenchCoreError(
            code="INVALID_PRODUCTIVITY_RATE_PER_HOUR",
            message=f"productivity_rate_per_hour invalido: {productivity_rate_per_hour}",
            action="Retorne productivity_rate_per_hour como numero >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    if float(productivity_rate_per_hour) < 0:
        raise S4WorkbenchCoreError(
            code="INVALID_PRODUCTIVITY_RATE_PER_HOUR",
            message=f"productivity_rate_per_hour nao pode ser negativo: {productivity_rate_per_hour}",
            action="Retorne productivity_rate_per_hour como numero >= 0.",
            correlation_id=correlation_id,
            stage=stage,
        )
    normalized["productivity_rate_per_hour"] = round(float(productivity_rate_per_hour), 6)

    audit_overflow_detected = normalized.get("audit_overflow_detected")
    if audit_overflow_detected is None:
        audit_overflow_detected = normalized["pending_audit_items"] > audit_queue_capacity
    if not isinstance(audit_overflow_detected, bool):
        raise S4WorkbenchCoreError(
            code="INVALID_AUDIT_OVERFLOW_DETECTED",
            message=f"audit_overflow_detected invalido: {audit_overflow_detected}",
            action="Retorne audit_overflow_detected como booleano.",
            correlation_id=correlation_id,
            stage=stage,
        )
    normalized["audit_overflow_detected"] = audit_overflow_detected

    return normalized


def _default_operational_audit_executor(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one WORK Sprint 4 operational-audit pass in dry-run mode.

    Args:
        context: Structured operational-audit context with policy metadata.

    Returns:
        dict[str, Any]: Dry-run operational-audit execution result.
    """

    audit_mode = str(context.get("audit_mode", "full_trace")).strip().lower()
    minimum_actions_per_window = int(context.get("minimum_actions_per_window", 0))
    productivity_window_hours = int(context.get("productivity_window_hours", 1))
    audit_queue_capacity = int(context.get("audit_queue_capacity", 0))
    require_change_reason = bool(context.get("require_change_reason", False))
    capture_before_after_state = bool(context.get("capture_before_after_state", False))
    enable_anomaly_alerts = bool(context.get("enable_anomaly_alerts", False))

    actions_received = max(20, minimum_actions_per_window * 12)
    if audit_mode == "sampled_trace":
        audit_ratio = 0.65
    elif audit_mode == "compliance_only":
        audit_ratio = 0.55
    else:
        audit_ratio = 0.92

    actions_audited = min(actions_received, int(round(actions_received * audit_ratio)))
    pending_audit_items = max(0, actions_received - actions_audited)
    sla_warning_breaches = max(0, actions_received // 12)
    sla_violations_detected = max(0, sla_warning_breaches // 3)
    productivity_alerts = 1 if actions_audited < minimum_actions_per_window else 0
    anomaly_alerts_triggered = (
        1
        if enable_anomaly_alerts and sla_violations_detected > max(2, actions_received // 20)
        else 0
    )
    change_reasons_missing = 0 if require_change_reason else 0
    before_after_missing = 0 if capture_before_after_state else 0
    productivity_rate_per_hour = round(actions_audited / max(1, productivity_window_hours), 6)
    audit_overflow_detected = pending_audit_items > audit_queue_capacity

    return {
        "status": "succeeded",
        "operational_audit_result_id": f"works4audit-{uuid4().hex[:12]}",
        "actions_received": actions_received,
        "actions_audited": actions_audited,
        "pending_audit_items": pending_audit_items,
        "sla_warning_breaches": sla_warning_breaches,
        "sla_violations_detected": sla_violations_detected,
        "productivity_alerts": productivity_alerts,
        "anomaly_alerts_triggered": anomaly_alerts_triggered,
        "change_reasons_missing": change_reasons_missing,
        "before_after_missing": before_after_missing,
        "productivity_rate_per_hour": productivity_rate_per_hour,
        "audit_overflow_detected": audit_overflow_detected,
        "decision_reason": "dry_run_operational_audit_execution",
    }


def _new_event_id() -> str:
    return f"works4coreevt-{uuid4().hex[:12]}"
