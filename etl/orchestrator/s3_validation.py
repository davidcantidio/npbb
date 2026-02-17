"""Validation contracts for ORQ Sprint 3 agent-first orchestration.

This module centralizes ORQ Sprint 3 input/output validation used by tests and
integration checks. It provides structured actionable errors with correlation
and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s3_core import S3OrchestratorCoreInput
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


logger = logging.getLogger("npbb.etl.orchestrator.s3.validation")

S3_ORCHESTRATOR_VALIDATION_VERSION = "orq.s3.validation.v1"
ALLOWED_CIRCUIT_STATES = {"closed", "open", "half_open"}


class S3OrchestratorValidationError(ValueError):
    """Raised when ORQ Sprint 3 validation contract is violated."""

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
class S3OrchestratorValidationInput:
    """Input contract consumed by ORQ Sprint 3 validation checks."""

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

    def to_core_input(self, *, correlation_id: str | None = None) -> S3OrchestratorCoreInput:
        """Convert validated data to `S3OrchestratorCoreInput` contract."""

        return S3OrchestratorCoreInput(
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
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S3OrchestratorScaffoldRequest:
        """Convert validated data to `S3OrchestratorScaffoldRequest` contract."""

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
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3OrchestratorValidationResult:
    """Output contract returned by ORQ Sprint 3 input validation."""

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
class S3OrchestratorFlowOutputValidationResult:
    """Output contract returned by ORQ Sprint 3 flow-output validation."""

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


def validate_s3_orchestrator_input_contract(
    payload: S3OrchestratorValidationInput,
) -> S3OrchestratorValidationResult:
    """Validate ORQ Sprint 3 input contract before running the main flow.

    Args:
        payload: Input contract with source metadata, selected route, retry,
            and circuit breaker policy.

    Returns:
        S3OrchestratorValidationResult: Validation metadata and checks summary.

    Raises:
        S3OrchestratorValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"orq-s3-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="etl_orchestrator_s3_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do ORQ S3 iniciada",
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
            action="Informe tipo da fonte para selecionar rotas agent-first.",
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
            action="Informe rota inicial para o fluxo agent-first do ORQ S3.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("rota_selecionada")

    if not isinstance(payload.agent_habilitado, bool):
        _raise_validation_error(
            code="INVALID_AGENT_HABILITADO_FLAG",
            message="agent_habilitado deve ser booleano",
            action="Ajuste agent_habilitado para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"agent_habilitado": payload.agent_habilitado},
        )
    checks.append("agent_habilitado")

    if not isinstance(payload.permitir_fallback_deterministico, bool):
        _raise_validation_error(
            code="INVALID_FALLBACK_DETERMINISTICO_FLAG",
            message="permitir_fallback_deterministico deve ser booleano",
            action="Ajuste permitir_fallback_deterministico para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"permitir_fallback_deterministico": payload.permitir_fallback_deterministico},
        )
    checks.append("permitir_fallback_deterministico")

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

    if not isinstance(payload.retry_attempts, int):
        _raise_validation_error(
            code="INVALID_RETRY_ATTEMPTS_TYPE",
            message="retry_attempts deve ser inteiro",
            action="Ajuste retry_attempts para valor inteiro nao negativo.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"retry_attempts": payload.retry_attempts},
        )
    checks.append("retry_attempts")

    if not isinstance(payload.timeout_seconds, int):
        _raise_validation_error(
            code="INVALID_TIMEOUT_SECONDS_TYPE",
            message="timeout_seconds deve ser inteiro",
            action="Ajuste timeout_seconds para valor inteiro dentro da politica da sprint.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"timeout_seconds": payload.timeout_seconds},
        )
    checks.append("timeout_seconds")

    if not isinstance(payload.circuit_breaker_failure_threshold, int):
        _raise_validation_error(
            code="INVALID_CIRCUIT_BREAKER_THRESHOLD_TYPE",
            message="circuit_breaker_failure_threshold deve ser inteiro",
            action="Ajuste limiar do circuit breaker para valor inteiro valido.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={
                "circuit_breaker_failure_threshold": payload.circuit_breaker_failure_threshold
            },
        )
    checks.append("circuit_breaker_failure_threshold")

    if not isinstance(payload.circuit_breaker_reset_timeout_seconds, int):
        _raise_validation_error(
            code="INVALID_CIRCUIT_BREAKER_RESET_TIMEOUT_TYPE",
            message="circuit_breaker_reset_timeout_seconds deve ser inteiro",
            action="Ajuste janela de reset do circuit breaker para valor inteiro valido.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={
                "circuit_breaker_reset_timeout_seconds": payload.circuit_breaker_reset_timeout_seconds
            },
        )
    checks.append("circuit_breaker_reset_timeout_seconds")

    try:
        scaffold = build_s3_scaffold_contract(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S3OrchestratorScaffoldError as exc:
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
        event_name="etl_orchestrator_s3_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do ORQ S3 concluida com sucesso",
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
        "etl_orchestrator_s3_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": scaffold.rota_selecionada,
        },
    )
    return S3OrchestratorValidationResult(
        validation_version=S3_ORCHESTRATOR_VALIDATION_VERSION,
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


def validate_s3_orchestrator_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S3OrchestratorFlowOutputValidationResult:
    """Validate ORQ Sprint 3 flow output contract.

    Args:
        flow_output: Output dictionary produced by ORQ S3 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S3OrchestratorFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S3OrchestratorValidationError: If output contract is incomplete or
            inconsistent with ORQ Sprint 3 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "source_id",
        "source_kind",
        "source_uri",
        "rota_selecionada",
        "plano_execucao",
        "circuit_breaker",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo ORQ S3 incompleta: faltam campos {missing_fields}",
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

    if layer == "core" and "execucao" not in flow_output:
        _raise_validation_error(
            code="INCOMPLETE_CORE_FLOW_OUTPUT",
            message="Saida core do ORQ S3 deve incluir campo execucao",
            action="Propague bloco execucao com route_chain, fallback e attempts_trace.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    if str(flow_output.get("status", "")).lower() != "completed":
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo ORQ S3: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do ORQ S3.",
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

    if layer == "core":
        execucao = flow_output.get("execucao", {})
        final_route = str(execucao.get("final_route", ""))
        top_route = str(flow_output.get("rota_selecionada", ""))
        if final_route and final_route != top_route:
            _raise_validation_error(
                code="FINAL_ROUTE_MISMATCH",
                message="rota_selecionada divergente entre topo e execucao.final_route",
                action="Garanta consistencia da rota final no contrato core do ORQ S3.",
                correlation_id=correlation_id,
                stage="validation_output",
                context={"top_level_route": top_route, "final_route": final_route},
            )

    circuit_breaker = flow_output.get("circuit_breaker", {})
    circuit_state = str(circuit_breaker.get("state", "")).strip().lower()
    if circuit_state not in ALLOWED_CIRCUIT_STATES:
        _raise_validation_error(
            code="INVALID_CIRCUIT_BREAKER_STATE",
            message=f"Estado de circuit breaker invalido na saida: {circuit_breaker.get('state')}",
            action="Propague estado valido de circuit breaker: closed, open ou half_open.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"circuit_state": str(circuit_breaker.get("state", ""))},
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
        "etl_orchestrator_s3_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "rota_selecionada": str(flow_output.get("rota_selecionada", "")),
        },
    )
    return S3OrchestratorFlowOutputValidationResult(
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
    if contract_version == "orq.s3.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "orqs3coreevt-",
                "route_resolved_event_id": "orqs3coreevt-",
                "flow_completed_event_id": "orqs3coreevt-",
            },
        )
    if contract_version == "orq.s3.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "orqs3evt-",
                "route_decision_event_id": "orqs3evt-",
                "flow_completed_event_id": "orqs3evt-",
                "main_flow_started_event_id": "orqs3coreevt-",
                "main_flow_route_event_id": "orqs3coreevt-",
                "main_flow_completed_event_id": "orqs3coreevt-",
            },
        )
    raise S3OrchestratorValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos orq.s3.core.v1 ou orq.s3.service.v1.",
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
        event_name="etl_orchestrator_s3_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "etl_orchestrator_s3_validation_error",
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
    raise S3OrchestratorValidationError(
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
    route_position: int | None = None,
    total_routes: int | None = None,
    circuit_state: str | None = None,
    consecutive_failures: int | None = None,
    failure_threshold: int | None = None,
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
