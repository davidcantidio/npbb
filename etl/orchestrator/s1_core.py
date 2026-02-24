"""Main flow for ORQ Sprint 1 routing policy execution.

This module executes the Sprint 1 core path:
1) validate input and resolve scaffold contract;
2) emit route decision logs for operational tracing;
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s1_observability import (
    S1OrchestratorObservabilityInput,
    build_s1_orchestrator_actionable_error,
    build_s1_orchestrator_observability_event,
    log_s1_orchestrator_observability_event,
)
from .s1_scaffold import (
    S1OrchestratorRequest,
    S1OrchestratorScaffoldError,
    build_s1_scaffold_contract,
)

CONTRACT_VERSION = "orq.s1.core.v1"


class S1OrchestratorCoreError(RuntimeError):
    """Raised when ORQ Sprint 1 core flow fails."""

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
class S1OrchestratorCoreInput:
    """Input contract consumed by ORQ Sprint 1 core flow."""

    source_id: str
    source_kind: str
    source_uri: str
    profile_strategy_hint: str | None = None
    ia_habilitada: bool = True
    permitir_fallback_manual: bool = True
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S1OrchestratorRequest:
        """Build scaffold request using ORQ Sprint 1 stable fields."""

        return S1OrchestratorRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            profile_strategy_hint=self.profile_strategy_hint,
            ia_habilitada=self.ia_habilitada,
            permitir_fallback_manual=self.permitir_fallback_manual,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1OrchestratorCoreOutput:
    """Output contract returned by ORQ Sprint 1 core flow."""

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
        """Return plain dictionary for API, logs, and integration tests."""

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


def execute_s1_orchestrator_main_flow(
    flow_input: S1OrchestratorCoreInput,
) -> S1OrchestratorCoreOutput:
    """Execute ORQ Sprint 1 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with source metadata and routing flags.

    Returns:
        S1OrchestratorCoreOutput: Stable output contract with route decision,
            integration points, observability identifiers, and scaffold payload.

    Raises:
        S1OrchestratorCoreError: If scaffold validation fails or an unexpected
            runtime error happens in the main flow.
    """

    correlation_id = flow_input.correlation_id or f"orq-s1-{uuid4().hex[:12]}"
    started_event = build_s1_orchestrator_observability_event(
        S1OrchestratorObservabilityInput(
            event_name="etl_orchestrator_s1_main_flow_started",
            correlation_id=correlation_id,
            event_message="Fluxo principal do ORQ S1 iniciado",
            severity="info",
            source_id=flow_input.source_id,
            source_kind=flow_input.source_kind,
            source_uri=flow_input.source_uri,
            stage="main_flow",
        )
    )
    log_s1_orchestrator_observability_event(started_event)

    try:
        scaffold = build_s1_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        route_event = build_s1_orchestrator_observability_event(
            S1OrchestratorObservabilityInput(
                event_name="etl_orchestrator_s1_main_flow_route_resolved",
                correlation_id=correlation_id,
                event_message="Rota do ORQ S1 resolvida com sucesso",
                severity="info",
                source_id=scaffold.source_id,
                source_kind=scaffold.source_kind,
                source_uri=scaffold.source_uri,
                rota_selecionada=scaffold.rota_selecionada,
                stage="routing",
                context={"modo_roteamento": scaffold.politica_roteamento.get("modo_roteamento")},
            )
        )
        log_s1_orchestrator_observability_event(route_event)

        completed_event = build_s1_orchestrator_observability_event(
            S1OrchestratorObservabilityInput(
                event_name="etl_orchestrator_s1_main_flow_completed",
                correlation_id=correlation_id,
                event_message="Fluxo principal do ORQ S1 concluido",
                severity="info",
                source_id=scaffold.source_id,
                source_kind=scaffold.source_kind,
                source_uri=scaffold.source_uri,
                rota_selecionada=scaffold.rota_selecionada,
                stage="main_flow",
            )
        )
        log_s1_orchestrator_observability_event(completed_event)

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["orchestrator_core_module"] = (
            "etl.orchestrator.s1_core.execute_s1_orchestrator_main_flow"
        )
        pontos_integracao["orchestrator_observability_module"] = (
            "etl.orchestrator.s1_observability"
        )
        return S1OrchestratorCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status=scaffold.status,
            source_id=scaffold.source_id,
            source_kind=scaffold.source_kind,
            source_uri=scaffold.source_uri,
            rota_selecionada=scaffold.rota_selecionada,
            politica_roteamento=dict(scaffold.politica_roteamento),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event.observability_event_id,
                "route_resolved_event_id": route_event.observability_event_id,
                "flow_completed_event_id": completed_event.observability_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S1OrchestratorScaffoldError as exc:
        failed_event = build_s1_orchestrator_observability_event(
            S1OrchestratorObservabilityInput(
                event_name="etl_orchestrator_s1_main_flow_scaffold_error",
                correlation_id=correlation_id,
                event_message=exc.message,
                severity="warning",
                source_id=flow_input.source_id,
                source_kind=flow_input.source_kind,
                source_uri=flow_input.source_uri,
                stage="scaffold",
                context={"error_code": exc.code, "recommended_action": exc.action},
            )
        )
        log_s1_orchestrator_observability_event(failed_event)
        error_detail = build_s1_orchestrator_actionable_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
            stage="scaffold",
            context={"source_kind": flow_input.source_kind},
        )
        raise S1OrchestratorCoreError(
            code=str(error_detail["code"]),
            message=str(error_detail["message"]),
            action=str(error_detail["action"]),
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event.observability_event_id,
        ) from exc
    except S1OrchestratorCoreError:
        raise
    except Exception as exc:
        failed_event = build_s1_orchestrator_observability_event(
            S1OrchestratorObservabilityInput(
                event_name="etl_orchestrator_s1_main_flow_unexpected_error",
                correlation_id=correlation_id,
                event_message=(
                    "Falha inesperada no fluxo principal do ORQ S1: "
                    f"{type(exc).__name__}"
                ),
                severity="error",
                source_id=flow_input.source_id,
                source_kind=flow_input.source_kind,
                source_uri=flow_input.source_uri,
                stage="main_flow",
                context={"error_type": type(exc).__name__},
            )
        )
        log_s1_orchestrator_observability_event(failed_event)
        raise S1OrchestratorCoreError(
            code="ORQ_S1_MAIN_FLOW_FAILED",
            message=(
                "Falha ao executar fluxo principal do orquestrador S1: "
                f"{type(exc).__name__}"
            ),
            action="Revisar logs operacionais e validar o contrato de entrada do ORQ S1.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event.observability_event_id,
        ) from exc
