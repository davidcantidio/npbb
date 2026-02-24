"""Main flow for ORQ Sprint 3 agent-first orchestration.

This module executes the Sprint 3 core path:
1) validate input and resolve scaffold contract;
2) run agent-first route execution with retries and circuit breaker policy;
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s3_scaffold import (
    S3OrchestratorScaffoldError,
    S3OrchestratorScaffoldRequest,
    build_s3_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.orchestrator.s3.core")

CONTRACT_VERSION = "orq.s3.core.v1"
S3_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
S3_FAILED_STATUSES = {"failed", "fatal_error"}
S3_RETRYABLE_STATUSES = {"retryable_failure", "timeout", "transient_error"}
S3_CIRCUIT_STATUSES = {"circuit_open"}
S3_ALLOWED_EXEC_STATUSES = (
    S3_SUCCESS_STATUSES | S3_FAILED_STATUSES | S3_RETRYABLE_STATUSES | S3_CIRCUIT_STATUSES
)


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
    """Execute ORQ Sprint 3 main flow with retries and circuit breaker.

    Args:
        flow_input: Input contract with source metadata, selected route,
            fallback flags, retry policy, and circuit breaker parameters.
        execute_route: Optional callback responsible for executing one route.
            It receives `(route_name, route_context)` and must return a
            dictionary with `status` and optional diagnostic fields.

    Returns:
        S3OrchestratorCoreOutput: Stable output contract containing execution
            diagnostics and circuit breaker state.

    Raises:
        S3OrchestratorCoreError: If scaffold validation fails, route execution
            responses are invalid, circuit breaker opens, or all routes fail.
    """

    correlation_id = flow_input.correlation_id or f"orq-s3-{uuid4().hex[:12]}"
    route_executor = execute_route or _default_route_executor
    started_event_id = _new_event_id()
    logger.info(
        "etl_orchestrator_s3_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": flow_input.source_id,
            "source_kind": flow_input.source_kind,
            "rota_selecionada": flow_input.rota_selecionada,
            "agent_habilitado": flow_input.agent_habilitado,
        },
    )

    try:
        scaffold = build_s3_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        plano_execucao = dict(scaffold.plano_execucao)
        circuit_breaker_plan = dict(scaffold.circuit_breaker)
        fallback_chain = [str(item) for item in plano_execucao.get("fallback_chain", [])]
        route_chain = _build_route_chain(
            selected_route=scaffold.rota_selecionada,
            fallback_chain=fallback_chain,
        )
        max_attempts_per_route = int(plano_execucao.get("retry_policy", {}).get("max_attempts", 1))
        if max_attempts_per_route < 1:
            max_attempts_per_route = 1

        failure_threshold = int(circuit_breaker_plan.get("failure_threshold", 1))
        if failure_threshold < 1:
            failure_threshold = 1
        reset_timeout_seconds = int(circuit_breaker_plan.get("reset_timeout_seconds", 0))

        attempts_trace: list[dict[str, Any]] = []
        final_route = ""
        final_status = "failed"
        fallback_activated = False
        circuit_state = "closed"
        consecutive_failures = 0
        circuit_opened_event_id: str | None = None

        for route_index, route_name in enumerate(route_chain):
            if route_index > 0:
                fallback_activated = True
            if circuit_state == "open":
                break

            for attempt in range(1, max_attempts_per_route + 1):
                route_event_id = _new_event_id()
                logger.info(
                    "etl_orchestrator_s3_route_attempt_started",
                    extra={
                        "correlation_id": correlation_id,
                        "event_id": route_event_id,
                        "source_id": scaffold.source_id,
                        "source_kind": scaffold.source_kind,
                        "route_name": route_name,
                        "route_position": route_index + 1,
                        "total_routes": len(route_chain),
                        "attempt": attempt,
                        "circuit_state": circuit_state,
                        "consecutive_failures": consecutive_failures,
                    },
                )

                execution_context = {
                    "correlation_id": correlation_id,
                    "source_id": scaffold.source_id,
                    "source_kind": scaffold.source_kind,
                    "source_uri": scaffold.source_uri,
                    "route_name": route_name,
                    "route_position": route_index + 1,
                    "attempt": attempt,
                    "max_attempts_per_route": max_attempts_per_route,
                    "timeout_seconds": int(plano_execucao.get("timeout_seconds", 0)),
                    "queue_name": plano_execucao.get("queue_name"),
                    "agent_profile": plano_execucao.get("agent_profile"),
                    "circuit_breaker": {
                        "state": circuit_state,
                        "consecutive_failures": consecutive_failures,
                        "failure_threshold": failure_threshold,
                        "reset_timeout_seconds": reset_timeout_seconds,
                    },
                }
                response = route_executor(route_name, execution_context)
                normalized = _normalize_route_response(
                    response=response,
                    correlation_id=correlation_id,
                    stage="route_execution",
                )
                status = normalized["status"]

                if status in S3_SUCCESS_STATUSES:
                    consecutive_failures = 0
                elif status in S3_CIRCUIT_STATUSES:
                    consecutive_failures = failure_threshold
                elif status in S3_FAILED_STATUSES:
                    consecutive_failures += 1
                elif status in S3_RETRYABLE_STATUSES and attempt >= max_attempts_per_route:
                    consecutive_failures += 1

                attempts_trace.append(
                    {
                        "route_name": route_name,
                        "attempt": attempt,
                        "status": status,
                        "message": normalized.get("message"),
                        "route_event_id": route_event_id,
                        "consecutive_failures": consecutive_failures,
                    }
                )
                logger.info(
                    "etl_orchestrator_s3_route_attempt_result",
                    extra={
                        "correlation_id": correlation_id,
                        "event_id": route_event_id,
                        "route_name": route_name,
                        "attempt": attempt,
                        "status": status,
                        "consecutive_failures": consecutive_failures,
                    },
                )

                if status in S3_SUCCESS_STATUSES:
                    final_route = route_name
                    final_status = "completed"
                    route_resolved_event_id = _new_event_id()
                    logger.info(
                        "etl_orchestrator_s3_route_resolved",
                        extra={
                            "correlation_id": correlation_id,
                            "event_id": route_resolved_event_id,
                            "source_id": scaffold.source_id,
                            "source_kind": scaffold.source_kind,
                            "final_route": final_route,
                            "fallback_activated": fallback_activated,
                            "attempts_count": len(attempts_trace),
                            "circuit_state": circuit_state,
                        },
                    )
                    completed_event_id = _new_event_id()
                    logger.info(
                        "etl_orchestrator_s3_main_flow_completed",
                        extra={
                            "correlation_id": correlation_id,
                            "event_id": completed_event_id,
                            "source_id": scaffold.source_id,
                            "source_kind": scaffold.source_kind,
                            "final_route": final_route,
                            "final_status": final_status,
                            "fallback_activated": fallback_activated,
                            "attempts_count": len(attempts_trace),
                            "circuit_state": circuit_state,
                        },
                    )
                    pontos_integracao = dict(scaffold.pontos_integracao)
                    pontos_integracao["orchestrator_core_module"] = (
                        "etl.orchestrator.s3_core.execute_s3_orchestrator_main_flow"
                    )
                    return S3OrchestratorCoreOutput(
                        contrato_versao=CONTRACT_VERSION,
                        correlation_id=correlation_id,
                        status=final_status,
                        source_id=scaffold.source_id,
                        source_kind=scaffold.source_kind,
                        source_uri=scaffold.source_uri,
                        rota_selecionada=final_route,
                        plano_execucao=plano_execucao,
                        execucao={
                            "route_chain": route_chain,
                            "fallback_activated": fallback_activated,
                            "attempts_trace": attempts_trace,
                            "final_route": final_route,
                            "final_status": final_status,
                        },
                        circuit_breaker={
                            "state": circuit_state,
                            "failure_threshold": failure_threshold,
                            "consecutive_failures": consecutive_failures,
                            "reset_timeout_seconds": reset_timeout_seconds,
                            "opened_event_id": circuit_opened_event_id,
                        },
                        pontos_integracao=pontos_integracao,
                        observabilidade={
                            "flow_started_event_id": started_event_id,
                            "route_resolved_event_id": route_resolved_event_id,
                            "flow_completed_event_id": completed_event_id,
                        },
                        scaffold=scaffold.to_dict(),
                    )

                if consecutive_failures >= failure_threshold:
                    circuit_state = "open"
                    circuit_opened_event_id = _new_event_id()
                    logger.warning(
                        "etl_orchestrator_s3_circuit_breaker_opened",
                        extra={
                            "correlation_id": correlation_id,
                            "event_id": circuit_opened_event_id,
                            "source_id": scaffold.source_id,
                            "source_kind": scaffold.source_kind,
                            "route_name": route_name,
                            "attempt": attempt,
                            "failure_threshold": failure_threshold,
                            "consecutive_failures": consecutive_failures,
                        },
                    )
                    break

                if status in S3_FAILED_STATUSES | S3_CIRCUIT_STATUSES:
                    break
                if status in S3_RETRYABLE_STATUSES and attempt < max_attempts_per_route:
                    continue
                if status in S3_RETRYABLE_STATUSES:
                    break

            if circuit_state == "open":
                break

        if circuit_state == "open":
            raise S3OrchestratorCoreError(
                code="ORQ_S3_CIRCUIT_BREAKER_OPEN",
                message="Circuit breaker do ORQ S3 foi aberto por excesso de falhas consecutivas",
                action=(
                    "Aguarde janela de reset do circuit breaker e investigue falhas "
                    "de rota antes de reexecutar."
                ),
                correlation_id=correlation_id,
                stage="circuit_breaker",
                event_id=circuit_opened_event_id,
            )

        failed_event_id = _new_event_id()
        logger.warning(
            "etl_orchestrator_s3_main_flow_route_exhausted",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "source_id": scaffold.source_id,
                "source_kind": scaffold.source_kind,
                "route_chain": route_chain,
                "attempts_count": len(attempts_trace),
            },
        )
        raise S3OrchestratorCoreError(
            code="ORQ_S3_ROUTE_CHAIN_EXHAUSTED",
            message="Todas as rotas do fluxo S3 falharam apos tentativas controladas",
            action="Revisar falhas por rota nos logs e ajustar politica agent-first/fallback.",
            correlation_id=correlation_id,
            stage="route_execution",
            event_id=failed_event_id,
        )
    except S3OrchestratorScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "etl_orchestrator_s3_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S3OrchestratorCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S3OrchestratorCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "etl_orchestrator_s3_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3OrchestratorCoreError(
            code="ORQ_S3_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal do ORQ S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor do ORQ S3.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _build_route_chain(*, selected_route: str, fallback_chain: list[str]) -> list[str]:
    chain: list[str] = [selected_route]
    chain.extend(fallback_chain)

    deduped: list[str] = []
    for route_name in chain:
        if route_name and route_name not in deduped:
            deduped.append(route_name)
    return deduped


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
            action="Garantir retorno dict com campo 'status' no executor de rota.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in S3_ALLOWED_EXEC_STATUSES:
        raise S3OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_STATUS",
            message=f"Status de execucao de rota invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor de rota: "
                "succeeded/completed/success/failed/fatal_error/retryable_failure/timeout/"
                "transient_error/circuit_open."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    return normalized


def _default_route_executor(route_name: str, route_context: dict[str, Any]) -> dict[str, Any]:
    """Execute one route in dry-run mode when no external executor is provided.

    Args:
        route_name: Route identifier selected for this attempt.
        route_context: Structured context with source metadata and retry info.

    Returns:
        dict[str, Any]: Dry-run response with `status` and actionable message.
    """

    return {
        "status": "succeeded",
        "message": f"Route '{route_name}' executada em modo dry-run",
        "route_context": route_context,
    }


def _new_event_id() -> str:
    return f"orqs3coreevt-{uuid4().hex[:12]}"
