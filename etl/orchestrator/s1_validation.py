"""Validation contracts for ORQ Sprint 1 orchestration journey.

This module centralizes ORQ Sprint 1 input/output validation used by tests and
integration checks. It provides structured actionable errors with correlation
and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s1_core import S1OrchestratorCoreInput
from .s1_observability import (
    S1OrchestratorObservabilityInput,
    build_s1_orchestrator_observability_event,
    log_s1_orchestrator_observability_event,
)
from .s1_scaffold import (
    S1OrchestratorRequest,
    S1OrchestratorScaffoldError,
    build_s1_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.orchestrator.s1.validation")

S1_ORCHESTRATOR_VALIDATION_VERSION = "orq.s1.validation.v1"


class S1OrchestratorValidationError(ValueError):
    """Raised when ORQ Sprint 1 validation contract is violated."""

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
class S1OrchestratorValidationInput:
    """Input contract consumed by ORQ Sprint 1 validation checks."""

    source_id: str
    source_kind: str
    source_uri: str
    profile_strategy_hint: str | None = None
    ia_habilitada: bool = True
    permitir_fallback_manual: bool = True
    correlation_id: str | None = None

    def to_core_input(self, *, correlation_id: str | None = None) -> S1OrchestratorCoreInput:
        """Convert validated data to `S1OrchestratorCoreInput` contract."""

        return S1OrchestratorCoreInput(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            profile_strategy_hint=self.profile_strategy_hint,
            ia_habilitada=self.ia_habilitada,
            permitir_fallback_manual=self.permitir_fallback_manual,
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(self, *, correlation_id: str | None = None) -> S1OrchestratorRequest:
        """Convert validated data to `S1OrchestratorRequest` contract."""

        return S1OrchestratorRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            profile_strategy_hint=self.profile_strategy_hint,
            ia_habilitada=self.ia_habilitada,
            permitir_fallback_manual=self.permitir_fallback_manual,
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1OrchestratorValidationResult:
    """Output contract returned by ORQ Sprint 1 input validation."""

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
class S1OrchestratorFlowOutputValidationResult:
    """Output contract returned by ORQ Sprint 1 flow-output validation."""

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


def validate_s1_orchestrator_input_contract(
    payload: S1OrchestratorValidationInput,
) -> S1OrchestratorValidationResult:
    """Validate ORQ Sprint 1 input contract before running the main flow.

    Args:
        payload: Input contract with source metadata and routing flags.

    Returns:
        S1OrchestratorValidationResult: Validation metadata and checks summary.

    Raises:
        S1OrchestratorValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"orq-s1-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="etl_orchestrator_s1_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do ORQ S1 iniciada",
        severity="info",
        source_id=payload.source_id,
        source_kind=payload.source_kind,
        source_uri=payload.source_uri,
        stage="validation_input",
    )
    checks: list[str] = []

    if not payload.source_id.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_ID",
            message="source_id nao pode ser vazio",
            action="Informe identificador da fonte antes de iniciar o roteamento.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("source_id")

    if not payload.source_kind.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_KIND",
            message="source_kind nao pode ser vazio",
            action="Informe tipo da fonte para selecionar a politica de roteamento.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("source_kind")

    if len(payload.source_uri.strip()) < 3:
        _raise_validation_error(
            code="INVALID_SOURCE_URI",
            message="source_uri invalido: informe URI/caminho com ao menos 3 caracteres",
            action="Forneca o caminho/URI do artefato para rastreabilidade operacional.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"source_uri": payload.source_uri},
        )
    checks.append("source_uri")

    if not isinstance(payload.ia_habilitada, bool):
        _raise_validation_error(
            code="INVALID_IA_HABILITADA_FLAG",
            message="ia_habilitada deve ser booleano",
            action="Ajuste ia_habilitada para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"ia_habilitada": payload.ia_habilitada},
        )
    checks.append("ia_habilitada")

    if not isinstance(payload.permitir_fallback_manual, bool):
        _raise_validation_error(
            code="INVALID_FALLBACK_MANUAL_FLAG",
            message="permitir_fallback_manual deve ser booleano",
            action="Ajuste permitir_fallback_manual para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"permitir_fallback_manual": payload.permitir_fallback_manual},
        )
    checks.append("permitir_fallback_manual")

    try:
        scaffold = build_s1_scaffold_contract(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S1OrchestratorScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={"source_kind": payload.source_kind},
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="etl_orchestrator_s1_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do ORQ S1 concluida com sucesso",
        severity="info",
        source_id=scaffold.source_id,
        source_kind=scaffold.source_kind,
        source_uri=scaffold.source_uri,
        rota_selecionada=scaffold.rota_selecionada,
        stage="validation_input",
        context={"checks": checks},
    )

    validation_id = f"orqval-{uuid4().hex[:12]}"
    logger.info(
        "etl_orchestrator_s1_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": scaffold.rota_selecionada,
        },
    )
    return S1OrchestratorValidationResult(
        validation_version=S1_ORCHESTRATOR_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview=scaffold.rota_selecionada,
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_s1_orchestrator_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S1OrchestratorFlowOutputValidationResult:
    """Validate ORQ Sprint 1 flow output contract.

    Args:
        flow_output: Output dictionary produced by ORQ S1 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S1OrchestratorFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S1OrchestratorValidationError: If output contract is incomplete or
            inconsistent with ORQ Sprint 1 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "source_id",
        "source_kind",
        "source_uri",
        "rota_selecionada",
        "politica_roteamento",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo ORQ S1 incompleta: faltam campos {missing_fields}",
            action="Atualize o fluxo para retornar o contrato completo da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"missing_fields": ",".join(missing_fields)},
        )

    if str(flow_output.get("status", "")).lower() != "ready":
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo ORQ S1: {flow_output.get('status')}",
            action="Garanta status 'ready' para saidas validas do ORQ S1.",
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

    politica = flow_output.get("politica_roteamento", {})
    route = str(flow_output.get("rota_selecionada", ""))
    if str(politica.get("rota_selecionada", "")) != route:
        _raise_validation_error(
            code="ROUTE_POLICY_MISMATCH",
            message="rota_selecionada divergente entre topo e politica_roteamento",
            action="Garanta consistencia de rota no payload de saida.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={
                "top_level_route": route,
                "policy_route": str(politica.get("rota_selecionada", "")),
            },
        )

    observabilidade = flow_output.get("observabilidade", {})
    contract_version = str(flow_output.get("contrato_versao", "")).strip()
    layer, required_obs = _resolve_output_layer(
        contract_version=contract_version,
        correlation_id=correlation_id,
    )
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
        "etl_orchestrator_s1_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "rota_selecionada": route,
        },
    )
    return S1OrchestratorFlowOutputValidationResult(
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
    if contract_version == "orq.s1.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "orqs1coreevt-",
                "route_resolved_event_id": "orqs1coreevt-",
                "flow_completed_event_id": "orqs1coreevt-",
            },
        )
    if contract_version == "orq.s1.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "orqs1evt-",
                "route_decision_event_id": "orqs1evt-",
                "flow_completed_event_id": "orqs1evt-",
                "main_flow_started_event_id": "orqs1coreevt-",
                "main_flow_route_event_id": "orqs1coreevt-",
                "main_flow_completed_event_id": "orqs1coreevt-",
            },
        )
    raise S1OrchestratorValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos orq.s1.core.v1 ou orq.s1.service.v1.",
        correlation_id=correlation_id,
        stage="validation_output",
    )


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
        event_name="etl_orchestrator_s1_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "etl_orchestrator_s1_validation_error",
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
    raise S1OrchestratorValidationError(
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
    source_id: str | None = None,
    source_kind: str | None = None,
    source_uri: str | None = None,
    rota_selecionada: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S1OrchestratorObservabilityInput(
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
    event = build_s1_orchestrator_observability_event(payload)
    log_s1_orchestrator_observability_event(event)
    return event
