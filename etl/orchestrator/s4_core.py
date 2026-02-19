"""Main flow for ORQ Sprint 4 telemetry, cost, and latency orchestration.

This module executes the Sprint 4 core path:
1) validate input and resolve scaffold contract;
2) execute route decision telemetry flow (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s4_scaffold import (
    MAX_COST_USD,
    MAX_LATENCY_MS,
    S4OrchestratorScaffoldError,
    S4OrchestratorScaffoldRequest,
    build_s4_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.orchestrator.s4.core")

CONTRACT_VERSION = "orq.s4.core.v1"
S4_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
S4_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
S4_ALLOWED_EXEC_STATUSES = S4_SUCCESS_STATUSES | S4_FAILED_STATUSES


class S4OrchestratorCoreError(RuntimeError):
    """Raised when ORQ Sprint 4 core flow fails."""

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
class S4OrchestratorCoreInput:
    """Input contract consumed by ORQ Sprint 4 core flow."""

    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    decisao_telemetria_habilitada: bool = True
    custo_estimado_usd: float = 0.0
    custo_orcamento_usd: float = 1.0
    latencia_estimada_ms: int = 1200
    latencia_sla_ms: int = 4000
    telemetria_amostragem: float = 1.0
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S4OrchestratorScaffoldRequest:
        """Build scaffold request using ORQ Sprint 4 stable fields."""

        return S4OrchestratorScaffoldRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            rota_selecionada=self.rota_selecionada,
            decisao_telemetria_habilitada=self.decisao_telemetria_habilitada,
            custo_estimado_usd=self.custo_estimado_usd,
            custo_orcamento_usd=self.custo_orcamento_usd,
            latencia_estimada_ms=self.latencia_estimada_ms,
            latencia_sla_ms=self.latencia_sla_ms,
            telemetria_amostragem=self.telemetria_amostragem,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4OrchestratorCoreOutput:
    """Output contract returned by ORQ Sprint 4 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_telemetria: dict[str, Any]
    governanca_custo_latencia: dict[str, Any]
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "plano_telemetria": self.plano_telemetria,
            "governanca_custo_latencia": self.governanca_custo_latencia,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s4_orchestrator_main_flow(
    flow_input: S4OrchestratorCoreInput,
    *,
    execute_route: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
) -> S4OrchestratorCoreOutput:
    """Execute ORQ Sprint 4 main flow with decision telemetry governance.

    Args:
        flow_input: Input contract with source metadata, route, telemetry, cost,
            and latency controls.
        execute_route: Optional callback responsible for route execution.
            It receives `(route_name, route_context)` and must return a
            dictionary containing `status` and optional metrics fields.

    Returns:
        S4OrchestratorCoreOutput: Stable output contract containing telemetry
            plan, governance summary, and execution diagnostics.

    Raises:
        S4OrchestratorCoreError: If scaffold validation fails, route execution
            response is invalid, or the route execution fails.
    """

    correlation_id = flow_input.correlation_id or f"orq-s4-{uuid4().hex[:12]}"
    route_executor = execute_route or _default_route_executor
    started_event_id = _new_event_id()
    logger.info(
        "etl_orchestrator_s4_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": flow_input.source_id,
            "source_kind": flow_input.source_kind,
            "rota_selecionada": flow_input.rota_selecionada,
            "decisao_telemetria_habilitada": flow_input.decisao_telemetria_habilitada,
        },
    )

    try:
        scaffold = build_s4_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        decision_event_id = _new_event_id()
        route_context = {
            "correlation_id": correlation_id,
            "source_id": scaffold.source_id,
            "source_kind": scaffold.source_kind,
            "source_uri": scaffold.source_uri,
            "route_name": scaffold.rota_selecionada,
            "attempt": 1,
            "telemetria_amostragem": scaffold.plano_telemetria.get("telemetria_amostragem"),
            "latencia_sla_ms": scaffold.governanca_custo_latencia.get("latencia_sla_ms"),
            "custo_orcamento_usd": scaffold.governanca_custo_latencia.get("custo_orcamento_usd"),
        }
        execution_response = route_executor(scaffold.rota_selecionada, route_context)
        normalized = _normalize_route_response(
            response=execution_response,
            correlation_id=correlation_id,
            stage="route_execution",
        )

        decision_reason = str(normalized.get("decision_reason", "route_executed")).strip()
        if not decision_reason:
            decision_reason = "route_executed"
        latency_ms = _normalize_latency_ms(
            value=normalized.get(
                "latency_ms", scaffold.governanca_custo_latencia.get("latencia_estimada_ms")
            ),
            correlation_id=correlation_id,
            stage="route_execution",
        )
        cost_usd = _normalize_cost_usd(
            value=normalized.get(
                "cost_usd", scaffold.governanca_custo_latencia.get("custo_estimado_usd")
            ),
            correlation_id=correlation_id,
            stage="route_execution",
        )

        governance = dict(scaffold.governanca_custo_latencia)
        budget_usd = float(governance.get("custo_orcamento_usd", 0.0))
        sla_ms = int(governance.get("latencia_sla_ms", 0))
        governance["custo_estimado_usd"] = cost_usd
        governance["latencia_estimada_ms"] = latency_ms
        governance["custo_status"] = "within_budget" if cost_usd <= budget_usd else "above_budget"
        governance["latencia_status"] = "within_sla" if latency_ms <= sla_ms else "above_sla"

        status = normalized["status"]
        logger.info(
            "etl_orchestrator_s4_route_decision_recorded",
            extra={
                "correlation_id": correlation_id,
                "event_id": decision_event_id,
                "source_id": scaffold.source_id,
                "source_kind": scaffold.source_kind,
                "route_name": scaffold.rota_selecionada,
                "decision_reason": decision_reason,
                "status": status,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
                "custo_status": governance["custo_status"],
                "latencia_status": governance["latencia_status"],
            },
        )

        if status not in S4_SUCCESS_STATUSES:
            failed_event_id = _new_event_id()
            logger.warning(
                "etl_orchestrator_s4_main_flow_route_failed",
                extra={
                    "correlation_id": correlation_id,
                    "event_id": failed_event_id,
                    "source_id": scaffold.source_id,
                    "source_kind": scaffold.source_kind,
                    "route_name": scaffold.rota_selecionada,
                    "decision_reason": decision_reason,
                    "status": status,
                    "latency_ms": latency_ms,
                    "cost_usd": cost_usd,
                },
            )
            raise S4OrchestratorCoreError(
                code="ORQ_S4_ROUTE_EXECUTION_FAILED",
                message=f"Execucao da rota S4 falhou com status '{status}'",
                action="Revisar telemetry decision logs e ajustar a rota/parametros operacionais.",
                correlation_id=correlation_id,
                stage="route_execution",
                event_id=failed_event_id,
            )

        completed_event_id = _new_event_id()
        logger.info(
            "etl_orchestrator_s4_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": scaffold.source_id,
                "source_kind": scaffold.source_kind,
                "route_name": scaffold.rota_selecionada,
                "status": "completed",
                "decision_reason": decision_reason,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
            },
        )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["orchestrator_core_module"] = (
            "etl.orchestrator.s4_core.execute_s4_orchestrator_main_flow"
        )

        return S4OrchestratorCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            source_id=scaffold.source_id,
            source_kind=scaffold.source_kind,
            source_uri=scaffold.source_uri,
            rota_selecionada=scaffold.rota_selecionada,
            plano_telemetria=dict(scaffold.plano_telemetria),
            governanca_custo_latencia=governance,
            execucao={
                "decision_reason": decision_reason,
                "attempt": 1,
                "status": status,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "decision_recorded_event_id": decision_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S4OrchestratorScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "etl_orchestrator_s4_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S4OrchestratorCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4OrchestratorCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "etl_orchestrator_s4_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4OrchestratorCoreError(
            code="ORQ_S4_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal do ORQ S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor do ORQ S4.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_route_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S4OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_RESPONSE",
            message="Executor de rota retornou resposta em formato invalido",
            action="Garantir retorno dict com campo 'status' no executor de rota.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in S4_ALLOWED_EXEC_STATUSES:
        raise S4OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_STATUS",
            message=f"Status de execucao de rota invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor de rota: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    return normalized


def _normalize_latency_ms(*, value: Any, correlation_id: str, stage: str) -> int:
    if not isinstance(value, int) or value < 0 or value > MAX_LATENCY_MS:
        raise S4OrchestratorCoreError(
            code="INVALID_ROUTE_LATENCY_MS",
            message=f"latency_ms invalido no retorno de execucao: {value}",
            action=f"Retorne latency_ms inteiro entre 0 e {MAX_LATENCY_MS}.",
            correlation_id=correlation_id,
            stage=stage,
        )
    return value


def _normalize_cost_usd(*, value: Any, correlation_id: str, stage: str) -> float:
    if not isinstance(value, (int, float)):
        raise S4OrchestratorCoreError(
            code="INVALID_ROUTE_COST_USD_TYPE",
            message=f"cost_usd invalido no retorno de execucao: {value}",
            action="Retorne cost_usd como numero (int/float).",
            correlation_id=correlation_id,
            stage=stage,
        )
    normalized = float(value)
    if normalized < 0 or normalized > MAX_COST_USD:
        raise S4OrchestratorCoreError(
            code="INVALID_ROUTE_COST_USD",
            message=f"cost_usd fora do intervalo suportado: {normalized}",
            action=f"Retorne cost_usd entre 0 e {MAX_COST_USD}.",
            correlation_id=correlation_id,
            stage=stage,
        )
    return round(normalized, 4)


def _default_route_executor(route_name: str, route_context: dict[str, Any]) -> dict[str, Any]:
    """Execute one route in dry-run mode when no external executor is provided.

    Args:
        route_name: Route identifier selected for this attempt.
        route_context: Structured context with source metadata and SLA/budget.

    Returns:
        dict[str, Any]: Dry-run response with status and decision telemetry
            fields used by Sprint 4 contracts.
    """

    return {
        "status": "succeeded",
        "decision_reason": "dry_run_main_flow",
        "latency_ms": int(route_context.get("latencia_sla_ms", 1000)),
        "cost_usd": float(route_context.get("custo_orcamento_usd", 1.0)),
        "message": f"Route '{route_name}' executada em modo dry-run",
    }


def _new_event_id() -> str:
    return f"orqs4coreevt-{uuid4().hex[:12]}"
