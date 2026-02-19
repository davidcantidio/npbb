"""Main flow for ORQ Sprint 3 hybrid agent-first orchestration.

This module executes the Sprint 3 core path:
1) validate input and resolve scaffold contract;
2) execute the route chain with retries/fallback and circuit breaker checks;
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s3_observability import (
    S3OrchestratorObservabilityInput,
    build_s3_orchestrator_observability_event,
    log_s3_orchestrator_observability_event,
)
from .s3_scaffold import (
    S3OrchestratorScaffoldError,
    S3OrchestratorScaffoldRequest,
    build_s3_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.orchestrator.s3.core")

CONTRACT_VERSION = "orq.s3.core.v1"
ORQ_S3_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
ORQ_S3_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
ORQ_S3_ALLOWED_EXEC_STATUSES = ORQ_S3_SUCCESS_STATUSES | ORQ_S3_FAILED_STATUSES


class S3OrchestratorCoreError(RuntimeError):
    """Raised when ORQ Sprint 3 core flow fails."""

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
class S3OrchestratorCoreInput:
    """Input contract consumed by ORQ Sprint 3 core flow."""

    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    agent_habilitado: bool = True
    permitir_fallback_deterministico: bool = True
    permitir_fallback_manual: bool = True
    retry_attempts: int = 0
    timeout_seconds: int = 240
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_reset_timeout_seconds: int = 180
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S3OrchestratorScaffoldRequest:
        """Build scaffold request using ORQ Sprint 3 stable fields."""

        return S3OrchestratorScaffoldRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            rota_selecionada=self.rota_selecionada,
            agent_habilitado=self.agent_habilitado,
            permitir_fallback_deterministico=self.permitir_fallback_deterministico,
            permitir_fallback_manual=self.permitir_fallback_manual,
            retry_attempts=self.retry_attempts,
            timeout_seconds=self.timeout_seconds,
            circuit_breaker_failure_threshold=self.circuit_breaker_failure_threshold,
            circuit_breaker_reset_timeout_seconds=self.circuit_breaker_reset_timeout_seconds,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3OrchestratorCoreOutput:
    """Output contract returned by ORQ Sprint 3 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_execucao: dict[str, Any]
    execucao: dict[str, Any]
    circuit_breaker: dict[str, Any]
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
            "plano_execucao": self.plano_execucao,
            "execucao": self.execucao,
            "circuit_breaker": self.circuit_breaker,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s3_orchestrator_main_flow(
    flow_input: S3OrchestratorCoreInput,
    *,
    execute_route: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
) -> S3OrchestratorCoreOutput:
    """Execute ORQ Sprint 3 main flow with route chain and circuit breaker."""

    correlation_id = flow_input.correlation_id or f"orq-s3-{uuid4().hex[:12]}"
    route_executor = execute_route or _default_route_executor
    started_event = _emit_observability_event(
        event_name="etl_orchestrator_s3_main_flow_started",
        correlation_id=correlation_id,
        event_message="Fluxo principal ORQ S3 iniciado",
        severity="info",
        source_id=flow_input.source_id,
        source_kind=flow_input.source_kind,
        source_uri=flow_input.source_uri,
        rota_selecionada=flow_input.rota_selecionada,
        stage="main_flow",
    )

    try:
        scaffold = build_s3_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        route_chain = list(scaffold.plano_execucao.get("route_chain", []))
        if not route_chain:
            route_chain = [scaffold.rota_selecionada]

        attempts_trace: list[dict[str, Any]] = []
        consecutive_failures = 0
        failure_threshold = int(scaffold.circuit_breaker.get("failure_threshold", 3))
        reset_timeout_seconds = int(scaffold.circuit_breaker.get("reset_timeout_seconds", 180))
        route_event_id = _new_event_id()
        final_route = scaffold.rota_selecionada
        final_status = "succeeded"
        fallback_activated = False
        circuit_state = "closed"

        for route_position, route_name in enumerate(route_chain, start=1):
            route_context = {
                "correlation_id": correlation_id,
                "source_id": scaffold.source_id,
                "source_kind": scaffold.source_kind,
                "source_uri": scaffold.source_uri,
                "route_name": route_name,
                "route_position": route_position,
                "total_routes": len(route_chain),
                "retry_attempts": scaffold.plano_execucao.get("retry_attempts", 0),
                "timeout_seconds": scaffold.plano_execucao.get("timeout_seconds", 240),
            }

            response = route_executor(route_name, route_context)
            normalized = _normalize_route_response(
                response=response,
                correlation_id=correlation_id,
                stage="route_execution",
            )
            status = normalized["status"]
            decision_reason = str(normalized.get("decision_reason", "route_executed")).strip()
            if not decision_reason:
                decision_reason = "route_executed"

            attempts_trace.append(
                {
                    "route_name": route_name,
                    "route_position": route_position,
                    "status": status,
                    "decision_reason": decision_reason,
                }
            )

            route_event = _emit_observability_event(
                event_name="etl_orchestrator_s3_route_decision_recorded",
                correlation_id=correlation_id,
                event_message=f"Execucao da rota '{route_name}' registrada",
                severity="info" if status in ORQ_S3_SUCCESS_STATUSES else "warning",
                source_id=scaffold.source_id,
                source_kind=scaffold.source_kind,
                source_uri=scaffold.source_uri,
                rota_selecionada=route_name,
                route_name=route_name,
                attempt=1,
                route_position=route_position,
                total_routes=len(route_chain),
                circuit_state=circuit_state,
                consecutive_failures=consecutive_failures,
                failure_threshold=failure_threshold,
                stage="route_execution",
                context={"status": status, "decision_reason": decision_reason},
            )
            route_event_id = route_event.observability_event_id

            if status in ORQ_S3_SUCCESS_STATUSES:
                final_route = route_name
                final_status = status
                fallback_activated = route_position > 1
                break

            consecutive_failures += 1
            if consecutive_failures >= failure_threshold:
                circuit_state = "open"
                breaker_event = _emit_observability_event(
                    event_name="etl_orchestrator_s3_circuit_breaker_opened",
                    correlation_id=correlation_id,
                    event_message="Circuit breaker ORQ S3 aberto por falhas consecutivas",
                    severity="warning",
                    source_id=scaffold.source_id,
                    source_kind=scaffold.source_kind,
                    source_uri=scaffold.source_uri,
                    rota_selecionada=route_name,
                    route_name=route_name,
                    attempt=1,
                    route_position=route_position,
                    total_routes=len(route_chain),
                    circuit_state=circuit_state,
                    consecutive_failures=consecutive_failures,
                    failure_threshold=failure_threshold,
                    stage="route_execution",
                )
                raise S3OrchestratorCoreError(
                    code="ORQ_S3_CIRCUIT_BREAKER_OPEN",
                    message="Circuit breaker ORQ S3 abriu por falhas consecutivas de rota",
                    action="Aguarde a janela de reset e revise falhas por rota no historico de observabilidade.",
                    correlation_id=correlation_id,
                    stage="route_execution",
                    event_id=breaker_event.observability_event_id,
                )

        if final_status not in ORQ_S3_SUCCESS_STATUSES:
            exhausted_event = _emit_observability_event(
                event_name="etl_orchestrator_s3_route_chain_exhausted",
                correlation_id=correlation_id,
                event_message="Todas as rotas do ORQ S3 foram tentadas sem sucesso",
                severity="warning",
                source_id=scaffold.source_id,
                source_kind=scaffold.source_kind,
                source_uri=scaffold.source_uri,
                rota_selecionada=scaffold.rota_selecionada,
                circuit_state=circuit_state,
                consecutive_failures=consecutive_failures,
                failure_threshold=failure_threshold,
                stage="route_execution",
            )
            raise S3OrchestratorCoreError(
                code="ORQ_S3_ROUTE_CHAIN_EXHAUSTED",
                message="Nao foi possivel concluir a cadeia de rotas do ORQ S3",
                action="Revise as respostas de rota e ajuste fallback/retries da estrategia agent-first.",
                correlation_id=correlation_id,
                stage="route_execution",
                event_id=exhausted_event.observability_event_id,
            )

        completed_event = _emit_observability_event(
            event_name="etl_orchestrator_s3_main_flow_completed",
            correlation_id=correlation_id,
            event_message="Fluxo principal ORQ S3 concluido",
            severity="info",
            source_id=scaffold.source_id,
            source_kind=scaffold.source_kind,
            source_uri=scaffold.source_uri,
            rota_selecionada=final_route,
            route_name=final_route,
            attempt=1,
            stage="main_flow",
            context={"final_status": final_status, "fallback_activated": fallback_activated},
        )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["orchestrator_core_module"] = (
            "etl.orchestrator.s3_core.execute_s3_orchestrator_main_flow"
        )

        circuit_breaker = {
            "state": circuit_state,
            "failure_threshold": failure_threshold,
            "consecutive_failures": consecutive_failures,
            "reset_timeout_seconds": reset_timeout_seconds,
        }
        plano_execucao = dict(scaffold.plano_execucao)
        plano_execucao["route_chain"] = route_chain

        return S3OrchestratorCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            source_id=scaffold.source_id,
            source_kind=scaffold.source_kind,
            source_uri=scaffold.source_uri,
            rota_selecionada=final_route,
            plano_execucao=plano_execucao,
            execucao={
                "status": final_status,
                "route_chain": route_chain,
                "attempts_trace": attempts_trace,
                "fallback_activated": fallback_activated,
                "final_route": final_route,
                "final_status": final_status,
            },
            circuit_breaker=circuit_breaker,
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event.observability_event_id,
                "route_resolved_event_id": route_event_id,
                "flow_completed_event_id": completed_event.observability_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S3OrchestratorScaffoldError as exc:
        failed_event = _emit_observability_event(
            event_name="etl_orchestrator_s3_main_flow_scaffold_error",
            correlation_id=correlation_id,
            event_message=exc.message,
            severity="warning",
            source_id=flow_input.source_id,
            source_kind=flow_input.source_kind,
            source_uri=flow_input.source_uri,
            rota_selecionada=flow_input.rota_selecionada,
            stage="scaffold",
            context={"error_code": exc.code, "recommended_action": exc.action},
        )
        raise S3OrchestratorCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event.observability_event_id,
        ) from exc
    except S3OrchestratorCoreError:
        raise
    except Exception as exc:
        failed_event = _emit_observability_event(
            event_name="etl_orchestrator_s3_main_flow_unexpected_error",
            correlation_id=correlation_id,
            event_message=f"Falha inesperada no ORQ S3: {type(exc).__name__}",
            severity="error",
            source_id=flow_input.source_id,
            source_kind=flow_input.source_kind,
            source_uri=flow_input.source_uri,
            rota_selecionada=flow_input.rota_selecionada,
            stage="main_flow",
            context={"error_type": type(exc).__name__},
        )
        raise S3OrchestratorCoreError(
            code="ORQ_S3_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal do ORQ S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor do ORQ S3.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event.observability_event_id,
        ) from exc


def _normalize_route_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S3OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_RESPONSE",
            message="Executor de rota retornou resposta em formato invalido",
            action="Garanta retorno dict com campo 'status' no executor de rota.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in ORQ_S3_ALLOWED_EXEC_STATUSES:
        raise S3OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_STATUS",
            message=f"Status de execucao de rota invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    return normalized


def _default_route_executor(route_name: str, route_context: dict[str, Any]) -> dict[str, Any]:
    """Execute one ORQ Sprint 3 route in dry-run mode."""

    return {
        "status": "succeeded",
        "decision_reason": "dry_run_main_flow",
        "route_name": route_name,
        "route_context": route_context,
    }


def _emit_observability_event(
    *,
    event_name: str,
    correlation_id: str,
    event_message: str,
    severity: str,
    source_id: str | None = None,
    source_kind: str | None = None,
    source_uri: str | None = None,
    rota_selecionada: str | None = None,
    route_name: str | None = None,
    attempt: int | None = None,
    route_position: int | None = None,
    total_routes: int | None = None,
    circuit_state: str | None = None,
    consecutive_failures: int | None = None,
    failure_threshold: int | None = None,
    stage: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S3OrchestratorObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=rota_selecionada,
        route_name=route_name,
        attempt=attempt,
        route_position=route_position,
        total_routes=total_routes,
        circuit_state=circuit_state,
        consecutive_failures=consecutive_failures,
        failure_threshold=failure_threshold,
        stage=stage,
        context=context,
    )
    event = build_s3_orchestrator_observability_event(payload)
    log_s3_orchestrator_observability_event(event)
    return event


def _new_event_id() -> str:
    return f"orqs3coreevt-{uuid4().hex[:12]}"
