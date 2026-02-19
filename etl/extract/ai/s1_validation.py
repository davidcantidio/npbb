"""Validation contracts for XIA Sprint 1 bounded AI extraction.

This module centralizes XIA Sprint 1 input/output validation used by tests and
integration checks. It provides structured actionable errors with correlation
and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s1_core import S1AIExtractCoreInput
from .s1_observability import (
    S1ExtractAIObservabilityInput,
    build_s1_extract_ai_observability_event,
    log_s1_extract_ai_observability_event,
)
from .s1_scaffold import (
    S1AIExtractScaffoldError,
    S1AIExtractScaffoldRequest,
    build_s1_ai_extract_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.extract.ai.s1.validation")

XIA_S1_VALIDATION_VERSION = "xia.s1.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}


class S1AIExtractValidationError(ValueError):
    """Raised when XIA Sprint 1 validation contract is violated."""

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
class S1AIExtractValidationInput:
    """Input contract consumed by XIA Sprint 1 validation checks."""

    source_id: str
    source_kind: str
    source_uri: str
    document_profile_hint: str | None = None
    ia_model_provider: str = "openai"
    ia_model_name: str = "gpt-4.1-mini"
    chunk_strategy: str = "section"
    max_tokens_output: int = 2048
    temperature: float = 0.0
    correlation_id: str | None = None

    def to_core_input(self, *, correlation_id: str | None = None) -> S1AIExtractCoreInput:
        """Convert validated data to `S1AIExtractCoreInput` contract."""

        return S1AIExtractCoreInput(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            document_profile_hint=self.document_profile_hint,
            ia_model_provider=self.ia_model_provider,
            ia_model_name=self.ia_model_name,
            chunk_strategy=self.chunk_strategy,
            max_tokens_output=self.max_tokens_output,
            temperature=self.temperature,
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S1AIExtractScaffoldRequest:
        """Convert validated data to `S1AIExtractScaffoldRequest` contract."""

        return S1AIExtractScaffoldRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            document_profile_hint=self.document_profile_hint,
            ia_model_provider=self.ia_model_provider,
            ia_model_name=self.ia_model_name,
            chunk_strategy=self.chunk_strategy,
            max_tokens_output=self.max_tokens_output,
            temperature=self.temperature,
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1AIExtractValidationResult:
    """Output contract returned by XIA Sprint 1 input validation."""

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
class S1AIExtractFlowOutputValidationResult:
    """Output contract returned by XIA Sprint 1 flow-output validation."""

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


def validate_s1_extract_ai_input_contract(
    payload: S1AIExtractValidationInput,
) -> S1AIExtractValidationResult:
    """Validate XIA Sprint 1 input contract before running the main flow.

    Args:
        payload: Input contract with source metadata and AI extraction params.

    Returns:
        S1AIExtractValidationResult: Validation metadata and checks summary.

    Raises:
        S1AIExtractValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"xia-s1-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="etl_extract_ai_s1_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do XIA S1 iniciada",
        severity="info",
        source_id=payload.source_id,
        source_kind=payload.source_kind,
        source_uri=payload.source_uri,
        model_provider=payload.ia_model_provider,
        model_name=payload.ia_model_name,
        chunk_strategy=payload.chunk_strategy,
        stage="validation_input",
    )
    checks: list[str] = []

    if not payload.source_id.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_ID",
            message="source_id nao pode ser vazio",
            action="Informe identificador da fonte antes de iniciar a extracao IA.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("source_id")

    if not payload.source_kind.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_KIND",
            message="source_kind nao pode ser vazio",
            action="Informe tipo da fonte para selecionar extracao delimitada.",
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

    if not isinstance(payload.max_tokens_output, int):
        _raise_validation_error(
            code="INVALID_MAX_TOKENS_OUTPUT_TYPE",
            message="max_tokens_output deve ser inteiro",
            action="Ajuste max_tokens_output para valor inteiro dentro da politica da sprint.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"max_tokens_output": payload.max_tokens_output},
        )
    checks.append("max_tokens_output")

    if not isinstance(payload.temperature, (int, float)):
        _raise_validation_error(
            code="INVALID_TEMPERATURE_TYPE",
            message="temperature deve ser numerico",
            action="Ajuste temperature para valor numerico entre 0 e 1.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"temperature": payload.temperature},
        )
    checks.append("temperature")

    try:
        scaffold = build_s1_ai_extract_scaffold_contract(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S1AIExtractScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "source_kind": payload.source_kind,
                "model_provider": payload.ia_model_provider,
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="etl_extract_ai_s1_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do XIA S1 concluida com sucesso",
        severity="info",
        source_id=scaffold.source_id,
        source_kind=scaffold.source_kind,
        source_uri=scaffold.source_uri,
        model_provider=scaffold.extraction_plan.get("ia_model_provider"),
        model_name=scaffold.extraction_plan.get("ia_model_name"),
        chunk_strategy=scaffold.extraction_plan.get("chunk_strategy"),
        stage="validation_input",
        context={"checks": checks},
    )

    validation_id = f"xiaval-{uuid4().hex[:12]}"
    logger.info(
        "etl_extract_ai_s1_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "ai_delimitada",
        },
    )
    return S1AIExtractValidationResult(
        validation_version=XIA_S1_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="ai_delimitada",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_s1_extract_ai_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S1AIExtractFlowOutputValidationResult:
    """Validate XIA Sprint 1 flow output contract.

    Args:
        flow_output: Output dictionary produced by XIA S1 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S1AIExtractFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S1AIExtractValidationError: If output contract is incomplete or
            inconsistent with XIA Sprint 1 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "source_id",
        "source_kind",
        "source_uri",
        "extraction_plan",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo XIA S1 incompleta: faltam campos {missing_fields}",
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

    status = str(flow_output.get("status", "")).lower()
    if status not in ALLOWED_FLOW_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo XIA S1: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do XIA S1.",
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

    execucao = flow_output.get("execucao", {})
    exec_status = str(execucao.get("status", "")).lower()
    if exec_status not in ALLOWED_EXEC_STATUSES:
        _raise_validation_error(
            code="INVALID_EXECUTION_STATUS",
            message=f"status de execucao invalido na saida: {execucao.get('status')}",
            action="Use status de execucao valido: succeeded/completed/success.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"exec_status": str(execucao.get("status", ""))},
        )
    chunk_count = execucao.get("chunk_count")
    if not isinstance(chunk_count, int) or chunk_count < 1:
        _raise_validation_error(
            code="INVALID_EXECUTION_CHUNK_COUNT",
            message=f"chunk_count invalido na saida: {chunk_count}",
            action="Propague chunk_count inteiro >= 1 na saida de execucao.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"chunk_count": chunk_count},
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
        "etl_extract_ai_s1_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "source_kind": str(flow_output.get("source_kind", "")),
        },
    )
    return S1AIExtractFlowOutputValidationResult(
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
    if contract_version == "xia.s1.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "xias1coreevt-",
                "flow_completed_event_id": "xias1coreevt-",
            },
        )
    if contract_version == "xia.s1.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "xias1evt-",
                "plan_ready_event_id": "xias1evt-",
                "flow_completed_event_id": "xias1evt-",
                "main_flow_started_event_id": "xias1coreevt-",
                "main_flow_completed_event_id": "xias1coreevt-",
            },
        )
    raise S1AIExtractValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos xia.s1.core.v1 ou xia.s1.service.v1.",
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
        event_name="etl_extract_ai_s1_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "etl_extract_ai_s1_validation_error",
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
    raise S1AIExtractValidationError(
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
    model_provider: str | None = None,
    model_name: str | None = None,
    chunk_strategy: str | None = None,
    chunk_count: int | None = None,
    decision_reason: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S1ExtractAIObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        model_provider=model_provider,
        model_name=model_name,
        chunk_strategy=chunk_strategy,
        chunk_count=chunk_count,
        decision_reason=decision_reason,
        stage=stage,
        context=context,
    )
    event = build_s1_extract_ai_observability_event(payload)
    log_s1_extract_ai_observability_event(event)
    return event
