"""Main flow for ORQ Sprint 2 deterministic-first orchestration.

This module executes the Sprint 2 core path:
1) validate input and resolve scaffold contract;
2) run deterministic-first route execution with controlled fallback;
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s2_observability import (
    S2OrchestratorObservabilityEvent,
    S2OrchestratorObservabilityInput,
    build_s2_orchestrator_actionable_error,
    build_s2_orchestrator_observability_event,
    log_s2_orchestrator_observability_event,
)
from .s2_scaffold import (
    S2OrchestratorScaffoldError,
    S2OrchestratorScaffoldRequest,
    build_s2_scaffold_contract,
)

CONTRACT_VERSION = "orq.s2.core.v1"
S2_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
S2_FAILED_STATUSES = {"failed", "fatal_error"}
S2_RETRYABLE_STATUSES = {"retryable_failure", "timeout", "transient_error"}
S2_ALLOWED_EXEC_STATUSES = S2_SUCCESS_STATUSES | S2_FAILED_STATUSES | S2_RETRYABLE_STATUSES


class S2OrchestratorCoreError(RuntimeError):
    """Raised when ORQ Sprint 2 core flow fails."""

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
class S2OrchestratorCoreInput:
    """Input contract consumed by ORQ Sprint 2 core flow."""

    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    ia_habilitada: bool = True
    permitir_fallback_manual: bool = True
    retry_attempts: int = 0
    timeout_seconds: int = 180
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S2OrchestratorScaffoldRequest:
        """Build scaffold request using ORQ Sprint 2 stable fields."""

        return S2OrchestratorScaffoldRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            rota_selecionada=self.rota_selecionada,
            ia_habilitada=self.ia_habilitada,
            permitir_fallback_manual=self.permitir_fallback_manual,
            retry_attempts=self.retry_attempts,
            timeout_seconds=self.timeout_seconds,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2OrchestratorCoreOutput:
    """Output contract returned by ORQ Sprint 2 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_execucao: dict[str, Any]
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
            "plano_execucao": self.plano_execucao,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s2_orchestrator_main_flow(
    flow_input: S2OrchestratorCoreInput,
    *,
    execute_route: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
) -> S2OrchestratorCoreOutput:
    """Execute ORQ Sprint 2 main flow with deterministic-first fallback logic.

    Args:
        flow_input: Input contract with source metadata, selected route, and
            runtime policy flags.
        execute_route: Optional callback responsible for executing one route.
            It receives `(route_name, route_context)` and must return a
            dictionary with `status` and optional diagnostic fields.

    Returns:
        S2OrchestratorCoreOutput: Stable output contract containing resolved
            execution plan and route-attempt diagnostics.

    Raises:
        S2OrchestratorCoreError: If scaffold validation fails, route execution
            responses are invalid, or all fallback routes fail.
    """

    correlation_id = flow_input.correlation_id or f"orq-s2-{uuid4().hex[:12]}"
    route_executor = execute_route or _default_route_executor
    started_event = _emit_s2_observability_event(
        event_name="etl_orchestrator_s2_main_flow_started",
        correlation_id=correlation_id,
        event_message="Fluxo principal do ORQ S2 iniciado",
        source_id=flow_input.source_id,
        source_kind=flow_input.source_kind,
        source_uri=flow_input.source_uri,
        rota_selecionada=flow_input.rota_selecionada,
        stage="main_flow",
    )

    try:
        scaffold = build_s2_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        plano_execucao = dict(scaffold.plano_execucao)
        fallback_chain = [str(item) for item in plano_execucao.get("fallback_chain", [])]
        route_chain = _build_route_chain(
            source_kind=scaffold.source_kind,
            selected_route=scaffold.rota_selecionada,
            fallback_chain=fallback_chain,
        )
        max_attempts_per_route = int(plano_execucao.get("retry_policy", {}).get("max_attempts", 1))
        if max_attempts_per_route < 1:
            max_attempts_per_route = 1

        attempts_trace: list[dict[str, Any]] = []
        final_route = ""
        final_status = "failed"
        fallback_activated = False

        for route_index, route_name in enumerate(route_chain):
            if route_index > 0:
                fallback_activated = True

            for attempt in range(1, max_attempts_per_route + 1):
                route_attempt_event = _emit_s2_observability_event(
                    event_name="etl_orchestrator_s2_route_attempt_started",
                    correlation_id=correlation_id,
                    event_message="Tentativa de execucao de rota iniciada",
                    source_id=scaffold.source_id,
                    source_kind=scaffold.source_kind,
                    source_uri=scaffold.source_uri,
                    rota_selecionada=scaffold.rota_selecionada,
                    route_name=route_name,
                    attempt=attempt,
                    route_position=route_index + 1,
                    total_routes=len(route_chain),
                    stage="route_execution",
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
                }
                response = route_executor(route_name, execution_context)
                normalized = _normalize_route_response(
                    response=response,
                    correlation_id=correlation_id,
                    stage="route_execution",
                )
                status = normalized["status"]
                attempts_trace.append(
                    {
                        "route_name": route_name,
                        "attempt": attempt,
                        "status": status,
                        "message": normalized.get("message"),
                        "route_event_id": route_attempt_event.observability_event_id,
                    }
                )
                _emit_s2_observability_event(
                    event_name="etl_orchestrator_s2_route_attempt_result",
                    correlation_id=correlation_id,
                    event_message="Tentativa de execucao de rota concluida",
                    source_id=scaffold.source_id,
                    source_kind=scaffold.source_kind,
                    source_uri=scaffold.source_uri,
                    rota_selecionada=scaffold.rota_selecionada,
                    route_name=route_name,
                    attempt=attempt,
                    route_position=route_index + 1,
                    total_routes=len(route_chain),
                    stage="route_execution",
                    context={"status": status},
                )

                if status in S2_SUCCESS_STATUSES:
                    final_route = route_name
                    final_status = "completed"
                    route_resolved_event = _emit_s2_observability_event(
                        event_name="etl_orchestrator_s2_route_resolved",
                        correlation_id=correlation_id,
                        event_message="Rota final do ORQ S2 resolvida com sucesso",
                        source_id=scaffold.source_id,
                        source_kind=scaffold.source_kind,
                        source_uri=scaffold.source_uri,
                        rota_selecionada=final_route,
                        route_name=final_route,
                        attempt=attempt,
                        route_position=route_index + 1,
                        total_routes=len(route_chain),
                        stage="route_execution",
                        context={
                            "fallback_activated": fallback_activated,
                            "attempts_count": len(attempts_trace),
                        },
                    )
                    completed_event = _emit_s2_observability_event(
                        event_name="etl_orchestrator_s2_main_flow_completed",
                        correlation_id=correlation_id,
                        event_message="Fluxo principal do ORQ S2 concluido",
                        source_id=scaffold.source_id,
                        source_kind=scaffold.source_kind,
                        source_uri=scaffold.source_uri,
                        rota_selecionada=final_route,
                        route_name=final_route,
                        stage="main_flow",
                        context={
                            "fallback_activated": fallback_activated,
                            "attempts_count": len(attempts_trace),
                        },
                    )
                    pontos_integracao = dict(scaffold.pontos_integracao)
                    pontos_integracao["orchestrator_core_module"] = (
                        "etl.orchestrator.s2_core.execute_s2_orchestrator_main_flow"
                    )
                    pontos_integracao["orchestrator_observability_module"] = (
                        "etl.orchestrator.s2_observability"
                    )
                    return S2OrchestratorCoreOutput(
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
                        pontos_integracao=pontos_integracao,
                        observabilidade={
                            "flow_started_event_id": started_event.observability_event_id,
                            "route_resolved_event_id": route_resolved_event.observability_event_id,
                            "flow_completed_event_id": completed_event.observability_event_id,
                        },
                        scaffold=scaffold.to_dict(),
                    )

                if status in S2_FAILED_STATUSES:
                    break
                if status in S2_RETRYABLE_STATUSES and attempt < max_attempts_per_route:
                    continue
                if status in S2_RETRYABLE_STATUSES:
                    break

        failed_event = _emit_s2_observability_event(
            event_name="etl_orchestrator_s2_main_flow_route_exhausted",
            correlation_id=correlation_id,
            event_message="Todas as rotas do ORQ S2 foram esgotadas",
            severity="warning",
            source_id=scaffold.source_id,
            source_kind=scaffold.source_kind,
            source_uri=scaffold.source_uri,
            rota_selecionada=scaffold.rota_selecionada,
            stage="route_execution",
            context={
                "route_chain": route_chain,
                "attempts_count": len(attempts_trace),
                "fallback_activated": fallback_activated,
            },
        )
        error_detail = build_s2_orchestrator_actionable_error(
            code="ORQ_S2_ROUTE_CHAIN_EXHAUSTED",
            message="Todas as rotas do fluxo S2 falharam apos tentativas controladas",
            action="Revisar falhas por rota nos logs e ajustar politica de fallback/retry.",
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
            stage="route_execution",
            context={
                "route_chain": route_chain,
                "attempts_count": len(attempts_trace),
                "fallback_activated": fallback_activated,
            },
        )
        raise S2OrchestratorCoreError(
            code=str(error_detail["code"]),
            message=str(error_detail["message"]),
            action=str(error_detail["action"]),
            correlation_id=correlation_id,
            stage="route_execution",
            event_id=failed_event.observability_event_id,
        )
    except S2OrchestratorScaffoldError as exc:
        failed_event = _emit_s2_observability_event(
            event_name="etl_orchestrator_s2_main_flow_scaffold_error",
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
        error_detail = build_s2_orchestrator_actionable_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
            stage="scaffold",
            context={"source_kind": flow_input.source_kind},
        )
        raise S2OrchestratorCoreError(
            code=str(error_detail["code"]),
            message=str(error_detail["message"]),
            action=str(error_detail["action"]),
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event.observability_event_id,
        ) from exc
    except S2OrchestratorCoreError as exc:
        if exc.event_id:
            raise
        failed_event = _emit_s2_observability_event(
            event_name="etl_orchestrator_s2_main_flow_error",
            correlation_id=correlation_id,
            event_message=exc.message,
            severity="warning",
            source_id=flow_input.source_id,
            source_kind=flow_input.source_kind,
            source_uri=flow_input.source_uri,
            rota_selecionada=flow_input.rota_selecionada,
            stage=exc.stage,
            context={"error_code": exc.code, "recommended_action": exc.action},
        )
        error_detail = build_s2_orchestrator_actionable_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
            stage=exc.stage,
        )
        raise S2OrchestratorCoreError(
            code=str(error_detail["code"]),
            message=str(error_detail["message"]),
            action=str(error_detail["action"]),
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event.observability_event_id,
        ) from exc
    except Exception as exc:
        failed_event = _emit_s2_observability_event(
            event_name="etl_orchestrator_s2_main_flow_unexpected_error",
            correlation_id=correlation_id,
            event_message=f"Falha inesperada no ORQ S2: {type(exc).__name__}",
            severity="error",
            source_id=flow_input.source_id,
            source_kind=flow_input.source_kind,
            source_uri=flow_input.source_uri,
            rota_selecionada=flow_input.rota_selecionada,
            stage="main_flow",
            context={"error_type": type(exc).__name__},
        )
        raise S2OrchestratorCoreError(
            code="ORQ_S2_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal do ORQ S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor do ORQ S2.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event.observability_event_id,
        ) from exc


def _build_route_chain(
    *,
    source_kind: str,
    selected_route: str,
    fallback_chain: list[str],
) -> list[str]:
    chain: list[str] = []
    deterministic_route_by_kind = {
        "pdf": "deterministic_pdf_extract",
        "xlsx": "deterministic_tabular_extract",
        "csv": "deterministic_tabular_extract",
    }
    deterministic_route = deterministic_route_by_kind.get(source_kind)
    if deterministic_route and selected_route != "manual_assistido_review":
        chain.append(deterministic_route)
    chain.append(selected_route)
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
        raise S2OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_RESPONSE",
            message="Executor de rota retornou resposta em formato invalido",
            action="Garantir retorno dict com campo 'status' no executor de rota.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in S2_ALLOWED_EXEC_STATUSES:
        raise S2OrchestratorCoreError(
            code="INVALID_ROUTE_EXECUTION_STATUS",
            message=f"Status de execucao de rota invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor de rota: "
                "succeeded/completed/success/failed/fatal_error/retryable_failure/timeout/transient_error."
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


def _emit_s2_observability_event(
    *,
    event_name: str,
    correlation_id: str,
    event_message: str,
    stage: str,
    severity: str = "info",
    source_id: str | None = None,
    source_kind: str | None = None,
    source_uri: str | None = None,
    rota_selecionada: str | None = None,
    route_name: str | None = None,
    attempt: int | None = None,
    route_position: int | None = None,
    total_routes: int | None = None,
    context: dict[str, Any] | None = None,
) -> S2OrchestratorObservabilityEvent:
    """Build and emit one ORQ Sprint 2 observability event.

    Args:
        event_name: Stable operational event name.
        correlation_id: Correlation identifier propagated in the flow.
        event_message: Human-readable operational description.
        stage: Flow stage where event is being emitted.
        severity: Event severity (`info`, `warning`, or `error`).
        source_id: Optional source identifier.
        source_kind: Optional source kind.
        source_uri: Optional source URI/path.
        rota_selecionada: Optional selected route name.
        route_name: Optional route currently being attempted.
        attempt: Optional attempt number for retry diagnostics.
        route_position: Optional position in route chain.
        total_routes: Optional total routes in route chain.
        context: Optional additional diagnostics context.

    Returns:
        S2OrchestratorObservabilityEvent: Structured emitted event.
    """

    payload = S2OrchestratorObservabilityInput(
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
        stage=stage,
        context=context,
    )
    event = build_s2_orchestrator_observability_event(payload)
    log_s2_orchestrator_observability_event(event)
    return event
