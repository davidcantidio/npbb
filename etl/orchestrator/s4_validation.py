"""Validation contracts for ORQ Sprint 4 telemetry-first orchestration.

This module centralizes ORQ Sprint 4 input/output validation used by tests and
integration checks. It provides structured actionable errors with correlation
and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s4_core import S4OrchestratorCoreInput
from .s4_observability import (
    S4OrchestratorObservabilityInput,
    build_s4_orchestrator_observability_event,
    log_s4_orchestrator_observability_event,
)
from .s4_scaffold import (
    S4OrchestratorScaffoldError,
    S4OrchestratorScaffoldRequest,
    build_s4_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.orchestrator.s4.validation")

S4_ORCHESTRATOR_VALIDATION_VERSION = "orq.s4.validation.v1"
ALLOWED_CUSTO_STATUS = {"within_budget", "above_budget"}
ALLOWED_LATENCIA_STATUS = {"within_sla", "above_sla"}


class S4OrchestratorValidationError(ValueError):
    """Raised when ORQ Sprint 4 validation contract is violated."""

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
class S4OrchestratorValidationInput:
    """Input contract consumed by ORQ Sprint 4 validation checks."""

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

    def to_core_input(self, *, correlation_id: str | None = None) -> S4OrchestratorCoreInput:
        """Convert validated data to `S4OrchestratorCoreInput` contract."""

        return S4OrchestratorCoreInput(
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
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S4OrchestratorScaffoldRequest:
        """Convert validated data to `S4OrchestratorScaffoldRequest` contract."""

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
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4OrchestratorValidationResult:
    """Output contract returned by ORQ Sprint 4 input validation."""

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
class S4OrchestratorFlowOutputValidationResult:
    """Output contract returned by ORQ Sprint 4 flow-output validation."""

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


def validate_s4_orchestrator_input_contract(
    payload: S4OrchestratorValidationInput,
) -> S4OrchestratorValidationResult:
    """Validate ORQ Sprint 4 input contract before running the main flow.

    Args:
        payload: Input contract with source metadata, selected route, telemetry,
            cost, and latency governance controls.

    Returns:
        S4OrchestratorValidationResult: Validation metadata and checks summary.

    Raises:
        S4OrchestratorValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"orq-s4-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="etl_orchestrator_s4_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do ORQ S4 iniciada",
        severity="info",
        source_id=payload.source_id,
        source_kind=payload.source_kind,
        source_uri=payload.source_uri,
        rota_selecionada=payload.rota_selecionada,
        stage="validation_input",
    )
    checks: list[str] = []

    if not payload.source_id.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_ID",
            message="source_id nao pode ser vazio",
            action="Informe identificador da fonte antes de iniciar a orquestracao.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("source_id")

    if not payload.source_kind.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_KIND",
            message="source_kind nao pode ser vazio",
            action="Informe tipo da fonte para selecionar rota da sprint 4.",
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

    if not payload.rota_selecionada.strip():
        _raise_validation_error(
            code="EMPTY_ROUTE_SELECTION",
            message="rota_selecionada nao pode ser vazia",
            action="Informe rota inicial para o fluxo ORQ S4.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("rota_selecionada")

    if not isinstance(payload.decisao_telemetria_habilitada, bool):
        _raise_validation_error(
            code="INVALID_TELEMETRIA_FLAG",
            message="decisao_telemetria_habilitada deve ser booleano",
            action="Ajuste decisao_telemetria_habilitada para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"decisao_telemetria_habilitada": payload.decisao_telemetria_habilitada},
        )
    checks.append("decisao_telemetria_habilitada")

    if not isinstance(payload.custo_estimado_usd, (int, float)):
        _raise_validation_error(
            code="INVALID_CUSTO_ESTIMADO_USD_TYPE",
            message="custo_estimado_usd deve ser numerico",
            action="Ajuste custo_estimado_usd para valor numerico.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"custo_estimado_usd": payload.custo_estimado_usd},
        )
    checks.append("custo_estimado_usd")

    if not isinstance(payload.custo_orcamento_usd, (int, float)):
        _raise_validation_error(
            code="INVALID_CUSTO_ORCAMENTO_USD_TYPE",
            message="custo_orcamento_usd deve ser numerico",
            action="Ajuste custo_orcamento_usd para valor numerico.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"custo_orcamento_usd": payload.custo_orcamento_usd},
        )
    checks.append("custo_orcamento_usd")

    if not isinstance(payload.latencia_estimada_ms, int):
        _raise_validation_error(
            code="INVALID_LATENCIA_ESTIMADA_MS_TYPE",
            message="latencia_estimada_ms deve ser inteiro",
            action="Ajuste latencia_estimada_ms para inteiro nao negativo.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"latencia_estimada_ms": payload.latencia_estimada_ms},
        )
    checks.append("latencia_estimada_ms")

    if not isinstance(payload.latencia_sla_ms, int):
        _raise_validation_error(
            code="INVALID_LATENCIA_SLA_MS_TYPE",
            message="latencia_sla_ms deve ser inteiro",
            action="Ajuste latencia_sla_ms para inteiro nao negativo.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"latencia_sla_ms": payload.latencia_sla_ms},
        )
    checks.append("latencia_sla_ms")

    if not isinstance(payload.telemetria_amostragem, (int, float)):
        _raise_validation_error(
            code="INVALID_TELEMETRIA_AMOSTRAGEM_TYPE",
            message="telemetria_amostragem deve ser numerico",
            action="Ajuste telemetria_amostragem para valor entre 0 e 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"telemetria_amostragem": payload.telemetria_amostragem},
        )
    checks.append("telemetria_amostragem")

    try:
        scaffold = build_s4_scaffold_contract(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S4OrchestratorScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "source_kind": payload.source_kind,
                "rota_selecionada": payload.rota_selecionada,
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="etl_orchestrator_s4_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do ORQ S4 concluida com sucesso",
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
        "etl_orchestrator_s4_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": scaffold.rota_selecionada,
        },
    )
    return S4OrchestratorValidationResult(
        validation_version=S4_ORCHESTRATOR_VALIDATION_VERSION,
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


def validate_s4_orchestrator_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S4OrchestratorFlowOutputValidationResult:
    """Validate ORQ Sprint 4 flow output contract.

    Args:
        flow_output: Output dictionary produced by ORQ S4 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S4OrchestratorFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S4OrchestratorValidationError: If output contract is incomplete or
            inconsistent with ORQ Sprint 4 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "source_id",
        "source_kind",
        "source_uri",
        "rota_selecionada",
        "plano_telemetria",
        "governanca_custo_latencia",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo ORQ S4 incompleta: faltam campos {missing_fields}",
            action="Atualize o fluxo para retornar o contrato completo da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"missing_fields": ",".join(missing_fields)},
        )

    contract_version = str(flow_output.get("contrato_versao", "")).strip()
    layer, required_obs = _resolve_output_layer(
        contract_version=contract_version,
        correlation_id=correlation_id,
    )

    if str(flow_output.get("status", "")).lower() != "completed":
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo ORQ S4: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do ORQ S4.",
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

    governanca = flow_output.get("governanca_custo_latencia", {})
    custo_status = str(governanca.get("custo_status", "")).strip().lower()
    latencia_status = str(governanca.get("latencia_status", "")).strip().lower()
    if custo_status not in ALLOWED_CUSTO_STATUS:
        _raise_validation_error(
            code="INVALID_CUSTO_STATUS",
            message=f"custo_status invalido na saida: {governanca.get('custo_status')}",
            action="Use custo_status valido: within_budget ou above_budget.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"custo_status": str(governanca.get("custo_status", ""))},
        )
    if latencia_status not in ALLOWED_LATENCIA_STATUS:
        _raise_validation_error(
            code="INVALID_LATENCIA_STATUS",
            message=f"latencia_status invalido na saida: {governanca.get('latencia_status')}",
            action="Use latencia_status valido: within_sla ou above_sla.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"latencia_status": str(governanca.get("latencia_status", ""))},
        )

    observabilidade = flow_output.get("observabilidade", {})
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
        "etl_orchestrator_s4_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "rota_selecionada": str(flow_output.get("rota_selecionada", "")),
        },
    )
    return S4OrchestratorFlowOutputValidationResult(
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
    if contract_version == "orq.s4.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "orqs4coreevt-",
                "decision_recorded_event_id": "orqs4coreevt-",
                "flow_completed_event_id": "orqs4coreevt-",
            },
        )
    if contract_version == "orq.s4.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "orqs4evt-",
                "telemetry_plan_event_id": "orqs4evt-",
                "flow_completed_event_id": "orqs4evt-",
                "main_flow_started_event_id": "orqs4coreevt-",
                "main_flow_decision_event_id": "orqs4coreevt-",
                "main_flow_completed_event_id": "orqs4coreevt-",
            },
        )
    raise S4OrchestratorValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos orq.s4.core.v1 ou orq.s4.service.v1.",
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
        event_name="etl_orchestrator_s4_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "etl_orchestrator_s4_validation_error",
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
    raise S4OrchestratorValidationError(
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
    route_name: str | None = None,
    attempt: int | None = None,
    decision_reason: str | None = None,
    latency_ms: int | None = None,
    cost_usd: float | None = None,
    custo_status: str | None = None,
    latencia_status: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S4OrchestratorObservabilityInput(
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
        decision_reason=decision_reason,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        custo_status=custo_status,
        latencia_status=latencia_status,
        stage=stage,
        context=context,
    )
    event = build_s4_orchestrator_observability_event(payload)
    log_s4_orchestrator_observability_event(event)
    return event
