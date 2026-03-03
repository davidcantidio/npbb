"""Operational services for ORQ Sprint 1, Sprint 2, Sprint 3, and Sprint 4.

This module executes:
- Sprint 1 main flow contracts.
- Sprint 2 deterministic-first contracts.
- Sprint 3 agent-first contracts.
- Sprint 4 telemetry/cost/latency main-flow contracts.
It emits structured operational logs with actionable errors for integration
layers.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from etl.orchestrator.s3_core import (
    S3OrchestratorCoreError,
    S3OrchestratorCoreInput,
    execute_s3_orchestrator_main_flow,
)
from etl.orchestrator.s3_scaffold import (
    S3OrchestratorScaffoldRequest,
)
from etl.orchestrator.s4_core import (
    S4OrchestratorCoreError,
    S4OrchestratorCoreInput,
    execute_s4_orchestrator_main_flow,
)
from etl.orchestrator.s4_scaffold import (
    S4OrchestratorScaffoldRequest,
)

_HAS_S1_ORQ_MODULES = True
try:  # pragma: no cover - optional while S1 ORQ modules are not restored
    from etl.orchestrator.s1_core import (
        S1OrchestratorCoreError,
        S1OrchestratorCoreInput,
        execute_s1_orchestrator_main_flow,
    )
    from etl.orchestrator.s1_scaffold import (
        S1OrchestratorRequest,
    )
except ModuleNotFoundError:  # pragma: no cover
    S1OrchestratorCoreError = RuntimeError  # type: ignore[assignment]
    S1OrchestratorCoreInput = Any  # type: ignore[assignment]
    S1OrchestratorRequest = Any  # type: ignore[assignment]
    execute_s1_orchestrator_main_flow = None  # type: ignore[assignment]
    _HAS_S1_ORQ_MODULES = False

_HAS_S2_ORQ_MODULES = True
try:  # pragma: no cover - optional while S2 ORQ modules are not restored
    from etl.orchestrator.s2_core import (
        S2OrchestratorCoreError,
        S2OrchestratorCoreInput,
        execute_s2_orchestrator_main_flow,
    )
    from etl.orchestrator.s2_scaffold import (
        S2OrchestratorScaffoldRequest,
    )
except ModuleNotFoundError:  # pragma: no cover
    S2OrchestratorCoreError = RuntimeError  # type: ignore[assignment]
    S2OrchestratorCoreInput = Any  # type: ignore[assignment]
    S2OrchestratorScaffoldRequest = Any  # type: ignore[assignment]
    execute_s2_orchestrator_main_flow = None  # type: ignore[assignment]
    _HAS_S2_ORQ_MODULES = False


logger = logging.getLogger("app.services.etl_orchestrator")
orq_telemetry = importlib.import_module(
    "app.services.orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry"
)

SERVICE_CONTRACT_VERSION = "orq.s1.service.v1"
SERVICE_CONTRACT_VERSION_S2 = "orq.s2.service.v1"
SERVICE_CONTRACT_VERSION_S3 = "orq.s3.service.v1"
SERVICE_CONTRACT_VERSION_S4 = "orq.s4.service.v1"


class S1OrchestratorServiceError(RuntimeError):
    """Raised when ORQ Sprint 1 service flow fails."""

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
        """Return serializable diagnostics payload for API integration."""

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
class S1OrchestratorServiceOutput:
    """Output contract returned by ORQ Sprint 1 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    politica_roteamento: dict[str, Any]
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for API/CLI serialization."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "politica_roteamento": self.politica_roteamento,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


class S2OrchestratorServiceError(RuntimeError):
    """Raised when ORQ Sprint 2 service flow fails."""

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
        """Return serializable diagnostics payload for API integration."""

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


class S3OrchestratorServiceError(RuntimeError):
    """Raised when ORQ Sprint 3 service flow fails."""

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
        """Return serializable diagnostics payload for API integration."""

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


class S4OrchestratorServiceError(RuntimeError):
    """Raised when ORQ Sprint 4 service flow fails."""

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
        """Return serializable diagnostics payload for API integration."""

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
class S2OrchestratorServiceOutput:
    """Output contract returned by ORQ Sprint 2 service scaffold flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_execucao: dict[str, Any]
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for API/CLI serialization."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "plano_execucao": self.plano_execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S3OrchestratorServiceOutput:
    """Output contract returned by ORQ Sprint 3 service main flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_execucao: dict[str, Any]
    circuit_breaker: dict[str, Any]
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for API/CLI serialization."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "plano_execucao": self.plano_execucao,
            "circuit_breaker": self.circuit_breaker,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S4OrchestratorServiceOutput:
    """Output contract returned by ORQ Sprint 4 service main flow."""

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
        """Return plain dictionary for API/CLI serialization."""

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


def execute_s1_orchestrator_service(
    request: S1OrchestratorRequest,
) -> S1OrchestratorServiceOutput:
    """Execute ORQ Sprint 1 routing service using main-flow orchestration.

    Args:
        request: Orchestrator input contract with source metadata and routing flags.

    Returns:
        S1OrchestratorServiceOutput: Stable service output with main-flow and
            service observability identifiers.

    Raises:
        S1OrchestratorServiceError: If main-flow execution fails or an
            unexpected service error happens.
    """

    if not _HAS_S1_ORQ_MODULES:
        correlation_id = f"orq-s1-{uuid4().hex[:12]}"
        raise S1OrchestratorServiceError(
            code="ORQ_S1_MODULES_NOT_AVAILABLE",
            message="Modulos ORQ S1 nao estao disponiveis neste branch (s1_core/s1_scaffold).",
            action="Restaure os arquivos etl/orchestrator/s1_* para habilitar o servico S1.",
            correlation_id=correlation_id,
            stage="bootstrap",
        )

    correlation_id = request.correlation_id or f"orq-s1-{uuid4().hex[:12]}"
    started_event = _emit_s1_telemetry_event(
        event_name="etl_orchestrator_s1_flow_started",
        correlation_id=correlation_id,
        event_message="Fluxo do servico ORQ S1 iniciado",
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        stage="service",
        severity="info",
    )

    try:
        core_output = execute_s1_orchestrator_main_flow(
            _to_core_input(request=request, correlation_id=correlation_id)
        )

        route_event = _emit_s1_telemetry_event(
            event_name="etl_orchestrator_s1_route_decision",
            correlation_id=correlation_id,
            event_message="Rota do ORQ S1 confirmada pelo servico",
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            stage="service",
            severity="info",
            context={
                "modo_roteamento": core_output.politica_roteamento.get("modo_roteamento"),
            },
        )

        completed_event = _emit_s1_telemetry_event(
            event_name="etl_orchestrator_s1_flow_completed",
            correlation_id=correlation_id,
            event_message="Fluxo do servico ORQ S1 concluido",
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            stage="service",
            severity="info",
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["orchestrator_service_module"] = (
            "app.services.etl_orchestrator_service.execute_s1_orchestrator_service"
        )
        pontos_integracao["orchestrator_service_telemetry_module"] = (
            "app.services.orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry"
        )
        observabilidade = {
            "flow_started_event_id": started_event.telemetry_event_id,
            "route_decision_event_id": route_event.telemetry_event_id,
            "flow_completed_event_id": completed_event.telemetry_event_id,
        }
        if core_output.observabilidade.get("flow_started_event_id"):
            observabilidade["main_flow_started_event_id"] = core_output.observabilidade[
                "flow_started_event_id"
            ]
        if core_output.observabilidade.get("route_resolved_event_id"):
            observabilidade["main_flow_route_event_id"] = core_output.observabilidade[
                "route_resolved_event_id"
            ]
        if core_output.observabilidade.get("flow_completed_event_id"):
            observabilidade["main_flow_completed_event_id"] = core_output.observabilidade[
                "flow_completed_event_id"
            ]

        return S1OrchestratorServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            politica_roteamento=dict(core_output.politica_roteamento),
            pontos_integracao=pontos_integracao,
            observabilidade=observabilidade,
            scaffold=dict(core_output.scaffold),
        )
    except S1OrchestratorCoreError as exc:
        failed_event = _emit_s1_telemetry_event(
            event_name="etl_orchestrator_s1_flow_main_flow_error",
            correlation_id=correlation_id,
            event_message=exc.message,
            source_id=request.source_id,
            source_kind=request.source_kind,
            source_uri=request.source_uri,
            stage=exc.stage,
            severity="warning",
            context={
                "error_code": exc.code,
                "recommended_action": exc.action,
                "core_event_id": exc.event_id,
            },
        )
        raise S1OrchestratorServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event.telemetry_event_id,
        ) from exc
    except S1OrchestratorServiceError:
        raise
    except Exception as exc:
        failed_event = _emit_s1_telemetry_event(
            event_name="etl_orchestrator_s1_flow_unexpected_error",
            correlation_id=correlation_id,
            event_message=f"Falha inesperada no servico ORQ S1: {type(exc).__name__}",
            source_id=request.source_id,
            source_kind=request.source_kind,
            source_uri=request.source_uri,
            stage="service",
            severity="error",
            context={"error_type": type(exc).__name__},
        )
        raise S1OrchestratorServiceError(
            code="ETL_ORCHESTRATOR_S1_FLOW_FAILED",
            message=f"Falha ao executar orquestrador S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do orquestrador.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event.telemetry_event_id,
        ) from exc


def execute_s2_orchestrator_service(
    request: S2OrchestratorScaffoldRequest,
) -> S2OrchestratorServiceOutput:
    """Execute ORQ Sprint 2 main-flow service with actionable diagnostics.

    Args:
        request: ORQ Sprint 2 input contract with selected route and runtime
            parameters.

    Returns:
        S2OrchestratorServiceOutput: Stable Sprint 2 service output with
            execution diagnostics and observability identifiers.

    Raises:
        S2OrchestratorServiceError: If main-flow execution fails or an
            unexpected service error happens.
    """

    if not _HAS_S2_ORQ_MODULES:
        correlation_id = f"orq-s2-{uuid4().hex[:12]}"
        raise S2OrchestratorServiceError(
            code="ORQ_S2_MODULES_NOT_AVAILABLE",
            message="Modulos ORQ S2 nao estao disponiveis neste branch (s2_core/s2_scaffold).",
            action="Restaure os arquivos etl/orchestrator/s2_* para habilitar o servico S2.",
            correlation_id=correlation_id,
            stage="bootstrap",
        )

    correlation_id = request.correlation_id or f"orq-s2-{uuid4().hex[:12]}"
    started_event = _emit_s2_telemetry_event(
        event_name="etl_orchestrator_s2_scaffold_started",
        correlation_id=correlation_id,
        event_message="Fluxo do servico ORQ S2 iniciado",
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        rota_selecionada=request.rota_selecionada,
        stage="service",
        severity="info",
    )

    try:
        core_output = execute_s2_orchestrator_main_flow(
            _to_s2_core_input(request=request, correlation_id=correlation_id)
        )
        route_event = _emit_s2_telemetry_event(
            event_name="etl_orchestrator_s2_route_decision",
            correlation_id=correlation_id,
            event_message="Rota do ORQ S2 confirmada pelo servico",
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            route_name=core_output.rota_selecionada,
            stage="service",
            severity="info",
            context={
                "executor_strategy": core_output.plano_execucao.get("executor_strategy"),
                "fallback_activated": core_output.execucao.get("fallback_activated"),
            },
        )

        completed_event = _emit_s2_telemetry_event(
            event_name="etl_orchestrator_s2_main_flow_completed",
            correlation_id=correlation_id,
            event_message="Fluxo do servico ORQ S2 concluido",
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            route_name=core_output.rota_selecionada,
            stage="service",
            severity="info",
            context={
                "executor_strategy": core_output.plano_execucao.get("executor_strategy"),
                "final_status": core_output.execucao.get("final_status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["orchestrator_service_module"] = (
            "app.services.etl_orchestrator_service.execute_s2_orchestrator_service"
        )
        pontos_integracao["orchestrator_service_telemetry_module"] = (
            "app.services.orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry"
        )
        observabilidade = {
            "scaffold_started_event_id": started_event.telemetry_event_id,
            "route_decision_event_id": route_event.telemetry_event_id,
            "scaffold_completed_event_id": completed_event.telemetry_event_id,
        }
        if core_output.observabilidade.get("flow_started_event_id"):
            observabilidade["main_flow_started_event_id"] = core_output.observabilidade[
                "flow_started_event_id"
            ]
        if core_output.observabilidade.get("flow_completed_event_id"):
            observabilidade["main_flow_completed_event_id"] = core_output.observabilidade[
                "flow_completed_event_id"
            ]

        return S2OrchestratorServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S2,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            plano_execucao=dict(core_output.plano_execucao),
            pontos_integracao=pontos_integracao,
            observabilidade=observabilidade,
            scaffold=dict(core_output.scaffold),
        )
    except S2OrchestratorCoreError as exc:
        failed_event = _emit_s2_telemetry_event(
            event_name="etl_orchestrator_s2_main_flow_error",
            correlation_id=correlation_id,
            event_message=exc.message,
            source_id=request.source_id,
            source_kind=request.source_kind,
            source_uri=request.source_uri,
            rota_selecionada=request.rota_selecionada,
            stage=exc.stage,
            severity="warning",
            context={
                "error_code": exc.code,
                "recommended_action": exc.action,
                "core_event_id": exc.event_id,
            },
        )
        raise S2OrchestratorServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event.telemetry_event_id,
        ) from exc
    except S2OrchestratorServiceError:
        raise
    except Exception as exc:
        failed_event = _emit_s2_telemetry_event(
            event_name="etl_orchestrator_s2_scaffold_unexpected_error",
            correlation_id=correlation_id,
            event_message=f"Falha inesperada no servico ORQ S2: {type(exc).__name__}",
            source_id=request.source_id,
            source_kind=request.source_kind,
            source_uri=request.source_uri,
            rota_selecionada=request.rota_selecionada,
            stage="service",
            severity="error",
            context={"error_type": type(exc).__name__},
        )
        raise S2OrchestratorServiceError(
            code="ETL_ORCHESTRATOR_S2_SCAFFOLD_FAILED",
            message=f"Falha ao executar scaffold do orquestrador S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do ORQ S2.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event.telemetry_event_id,
        ) from exc


def execute_s3_orchestrator_service(
    request: S3OrchestratorScaffoldRequest,
) -> S3OrchestratorServiceOutput:
    """Execute ORQ Sprint 3 main-flow service with actionable diagnostics.

    Args:
        request: ORQ Sprint 3 input contract with agent-first route,
            retry policy, and circuit breaker parameters.

    Returns:
        S3OrchestratorServiceOutput: Stable Sprint 3 service output with
            execution diagnostics and observability identifiers.

    Raises:
        S3OrchestratorServiceError: If main-flow execution fails or an
            unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"orq-s3-{uuid4().hex[:12]}"
    started_event_id = _new_s3_event_id()
    logger.info(
        "etl_orchestrator_s3_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "rota_selecionada": request.rota_selecionada,
            "agent_habilitado": request.agent_habilitado,
        },
    )

    try:
        core_output = execute_s3_orchestrator_main_flow(
            _to_s3_core_input(request=request, correlation_id=correlation_id)
        )
        route_event_id = _new_s3_event_id()
        logger.info(
            "etl_orchestrator_s3_route_decision",
            extra={
                "correlation_id": correlation_id,
                "event_id": route_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "rota_selecionada": core_output.rota_selecionada,
                "executor_strategy": core_output.plano_execucao.get("executor_strategy"),
                "fallback_activated": core_output.execucao.get("fallback_activated"),
                "circuit_state": core_output.circuit_breaker.get("state"),
                "circuit_breaker_threshold": core_output.circuit_breaker.get(
                    "failure_threshold"
                ),
            },
        )

        completed_event_id = _new_s3_event_id()
        logger.info(
            "etl_orchestrator_s3_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "rota_selecionada": core_output.rota_selecionada,
                "status": core_output.status,
                "final_status": core_output.execucao.get("final_status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["orchestrator_service_module"] = (
            "app.services.etl_orchestrator_service.execute_s3_orchestrator_service"
        )
        pontos_integracao["orchestrator_service_telemetry_module"] = (
            "app.services.etl_orchestrator_service"
        )

        observabilidade = {
            "flow_started_event_id": started_event_id,
            "route_decision_event_id": route_event_id,
            "flow_completed_event_id": completed_event_id,
        }
        if core_output.observabilidade.get("flow_started_event_id"):
            observabilidade["main_flow_started_event_id"] = core_output.observabilidade[
                "flow_started_event_id"
            ]
        if core_output.observabilidade.get("route_resolved_event_id"):
            observabilidade["main_flow_route_event_id"] = core_output.observabilidade[
                "route_resolved_event_id"
            ]
        if core_output.observabilidade.get("flow_completed_event_id"):
            observabilidade["main_flow_completed_event_id"] = core_output.observabilidade[
                "flow_completed_event_id"
            ]

        return S3OrchestratorServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S3,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            plano_execucao=dict(core_output.plano_execucao),
            circuit_breaker=dict(core_output.circuit_breaker),
            pontos_integracao=pontos_integracao,
            observabilidade=observabilidade,
            scaffold=dict(core_output.scaffold),
        )
    except S3OrchestratorCoreError as exc:
        failed_event_id = _new_s3_event_id()
        logger.warning(
            "etl_orchestrator_s3_main_flow_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "failed_stage": exc.stage,
                "core_event_id": exc.event_id,
            },
        )
        raise S3OrchestratorServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event_id,
        ) from exc
    except S3OrchestratorServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s3_event_id()
        logger.error(
            "etl_orchestrator_s3_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3OrchestratorServiceError(
            code="ETL_ORCHESTRATOR_S3_FLOW_FAILED",
            message=f"Falha ao executar fluxo do orquestrador S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do ORQ S3.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def execute_s4_orchestrator_service(
    request: S4OrchestratorScaffoldRequest,
) -> S4OrchestratorServiceOutput:
    """Execute ORQ Sprint 4 main-flow service with actionable diagnostics.

    Args:
        request: ORQ Sprint 4 input contract with telemetry, cost, and latency
            governance fields.

    Returns:
        S4OrchestratorServiceOutput: Stable Sprint 4 service output with
            telemetry plan, governance controls, execution diagnostics, and
            observability identifiers.

    Raises:
        S4OrchestratorServiceError: If main-flow execution fails or an
            unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"orq-s4-{uuid4().hex[:12]}"
    started_event_id = _new_s4_event_id()
    logger.info(
        "etl_orchestrator_s4_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "rota_selecionada": request.rota_selecionada,
            "decisao_telemetria_habilitada": request.decisao_telemetria_habilitada,
        },
    )

    try:
        core_output = execute_s4_orchestrator_main_flow(
            _to_s4_core_input(request=request, correlation_id=correlation_id)
        )

        telemetry_plan_event_id = _new_s4_event_id()
        logger.info(
            "etl_orchestrator_s4_telemetry_plan_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": telemetry_plan_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "rota_selecionada": core_output.rota_selecionada,
                "decision_reason": core_output.execucao.get("decision_reason"),
                "custo_status": core_output.governanca_custo_latencia.get("custo_status"),
                "latencia_status": core_output.governanca_custo_latencia.get("latencia_status"),
            },
        )

        completed_event_id = _new_s4_event_id()
        logger.info(
            "etl_orchestrator_s4_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "rota_selecionada": core_output.rota_selecionada,
                "status": core_output.status,
                "route_status": core_output.execucao.get("status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["orchestrator_service_module"] = (
            "app.services.etl_orchestrator_service.execute_s4_orchestrator_service"
        )
        pontos_integracao["orchestrator_service_telemetry_module"] = (
            "app.services.orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry"
        )

        return S4OrchestratorServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S4,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            rota_selecionada=core_output.rota_selecionada,
            plano_telemetria=dict(core_output.plano_telemetria),
            governanca_custo_latencia=dict(core_output.governanca_custo_latencia),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "telemetry_plan_event_id": telemetry_plan_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_decision_event_id": core_output.observabilidade[
                    "decision_recorded_event_id"
                ],
                "main_flow_completed_event_id": core_output.observabilidade[
                    "flow_completed_event_id"
                ],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S4OrchestratorCoreError as exc:
        failed_event_id = _new_s4_event_id()
        logger.warning(
            "etl_orchestrator_s4_main_flow_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "failed_stage": exc.stage,
                "core_event_id": exc.event_id,
            },
        )
        raise S4OrchestratorServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4OrchestratorServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s4_event_id()
        logger.error(
            "etl_orchestrator_s4_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4OrchestratorServiceError(
            code="ETL_ORCHESTRATOR_S4_FLOW_FAILED",
            message=f"Falha ao executar fluxo do orquestrador S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do ORQ S4.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def build_s1_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    event_id: str,
    stage: str = "service",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 1 error detail for API responses.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        event_id: Service event identifier for log lookup.
        stage: Flow stage where the error happened.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    detail = orq_telemetry.build_s1_orchestrator_error_detail(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        telemetry_event_id=event_id,
        stage=stage,
        context=context,
    )
    detail["event_id"] = event_id
    return detail


def build_s2_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    event_id: str,
    stage: str = "service",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 2 error detail for API responses.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        event_id: Service event identifier for log lookup.
        stage: Flow stage where the error happened.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    detail = orq_telemetry.build_s2_orchestrator_error_detail(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        telemetry_event_id=event_id,
        stage=stage,
        context=context,
    )
    detail["event_id"] = event_id
    return detail


def build_s3_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    event_id: str,
    stage: str = "service",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 3 error detail for API responses.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        event_id: Service event identifier for log lookup.
        stage: Flow stage where the error happened.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "event_id": event_id,
        "stage": stage,
        "context": context or {},
    }


def build_s4_orchestrator_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    event_id: str,
    stage: str = "service",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable ORQ Sprint 4 error detail for API responses.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        event_id: Service event identifier for log lookup.
        stage: Flow stage where the error happened.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "event_id": event_id,
        "stage": stage,
        "context": context or {},
    }


def _to_core_input(
    *,
    request: S1OrchestratorRequest,
    correlation_id: str,
) -> S1OrchestratorCoreInput:
    return S1OrchestratorCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        profile_strategy_hint=request.profile_strategy_hint,
        ia_habilitada=request.ia_habilitada,
        permitir_fallback_manual=request.permitir_fallback_manual,
        correlation_id=correlation_id,
    )


def _to_s2_core_input(
    *,
    request: S2OrchestratorScaffoldRequest,
    correlation_id: str,
) -> S2OrchestratorCoreInput:
    return S2OrchestratorCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        rota_selecionada=request.rota_selecionada,
        ia_habilitada=request.ia_habilitada,
        permitir_fallback_manual=request.permitir_fallback_manual,
        retry_attempts=request.retry_attempts,
        timeout_seconds=request.timeout_seconds,
        correlation_id=correlation_id,
    )


def _to_s3_core_input(
    *,
    request: S3OrchestratorScaffoldRequest,
    correlation_id: str,
) -> S3OrchestratorCoreInput:
    return S3OrchestratorCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        rota_selecionada=request.rota_selecionada,
        agent_habilitado=request.agent_habilitado,
        permitir_fallback_deterministico=request.permitir_fallback_deterministico,
        permitir_fallback_manual=request.permitir_fallback_manual,
        retry_attempts=request.retry_attempts,
        timeout_seconds=request.timeout_seconds,
        circuit_breaker_failure_threshold=request.circuit_breaker_failure_threshold,
        circuit_breaker_reset_timeout_seconds=request.circuit_breaker_reset_timeout_seconds,
        correlation_id=correlation_id,
    )


def _to_s4_core_input(
    *,
    request: S4OrchestratorScaffoldRequest,
    correlation_id: str,
) -> S4OrchestratorCoreInput:
    return S4OrchestratorCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        rota_selecionada=request.rota_selecionada,
        decisao_telemetria_habilitada=request.decisao_telemetria_habilitada,
        custo_estimado_usd=request.custo_estimado_usd,
        custo_orcamento_usd=request.custo_orcamento_usd,
        latencia_estimada_ms=request.latencia_estimada_ms,
        latencia_sla_ms=request.latencia_sla_ms,
        telemetria_amostragem=request.telemetria_amostragem,
        correlation_id=correlation_id,
    )


def _emit_s1_telemetry_event(
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
    context: dict[str, Any] | None = None,
):
    payload = orq_telemetry.S1OrchestratorTelemetryInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=rota_selecionada,
        stage=stage,
        context=context,
    )
    event = orq_telemetry.build_s1_orchestrator_telemetry_event(payload)
    orq_telemetry.emit_s1_orchestrator_telemetry_event(logger, event)
    return event


def _emit_s2_telemetry_event(
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
    context: dict[str, Any] | None = None,
):
    payload = orq_telemetry.S2OrchestratorTelemetryInput(
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
        stage=stage,
        context=context,
    )
    event = orq_telemetry.build_s2_orchestrator_telemetry_event(payload)
    orq_telemetry.emit_s2_orchestrator_telemetry_event(logger, event)
    return event


def _new_s3_event_id() -> str:
    return f"orqs3evt-{uuid4().hex[:12]}"


def _new_s4_event_id() -> str:
    return f"orqs4evt-{uuid4().hex[:12]}"
