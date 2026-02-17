"""Main flow for XIA Sprint 4 calibrated AI extraction and consolidation.

This module executes the Sprint 4 core path:
1) validate input and resolve scaffold contract;
2) execute one calibrated extraction pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s4_scaffold import (
    S4AIExtractScaffoldError,
    S4AIExtractScaffoldRequest,
    build_s4_ai_extract_scaffold_contract,
)


logger = logging.getLogger("npbb.etl.extract.ai.s4.core")

CONTRACT_VERSION = "xia.s4.core.v1"
XIA_S4_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
XIA_S4_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
XIA_S4_ALLOWED_EXEC_STATUSES = XIA_S4_SUCCESS_STATUSES | XIA_S4_FAILED_STATUSES


class S4AIExtractCoreError(RuntimeError):
    """Raised when XIA Sprint 4 core flow fails."""

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
class S4AIExtractCoreInput:
    """Input contract consumed by XIA Sprint 4 core flow."""

    source_id: str
    source_kind: str
    source_uri: str
    quality_profile_hint: str = "strict_textual"
    consolidation_scope: str = "single_source"
    output_normalization_profile: str = "canonical_fields_v1"
    ia_model_provider: str = "openai"
    ia_model_name: str = "gpt-4.1-mini"
    chunk_strategy: str = "section"
    max_tokens_output: int = 4096
    temperature: float = 0.0
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S4AIExtractScaffoldRequest:
        """Build scaffold request using XIA Sprint 4 stable fields."""

        return S4AIExtractScaffoldRequest(
            source_id=self.source_id,
            source_kind=self.source_kind,
            source_uri=self.source_uri,
            quality_profile_hint=self.quality_profile_hint,
            consolidation_scope=self.consolidation_scope,
            output_normalization_profile=self.output_normalization_profile,
            ia_model_provider=self.ia_model_provider,
            ia_model_name=self.ia_model_name,
            chunk_strategy=self.chunk_strategy,
            max_tokens_output=self.max_tokens_output,
            temperature=self.temperature,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4AIExtractCoreOutput:
    """Output contract returned by XIA Sprint 4 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    extraction_plan: dict[str, Any]
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
            "extraction_plan": self.extraction_plan,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s4_ai_extract_main_flow(
    flow_input: S4AIExtractCoreInput,
    *,
    execute_extraction: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S4AIExtractCoreOutput:
    """Execute XIA Sprint 4 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with source metadata, quality calibration,
            and consolidation parameters.
        execute_extraction: Optional callback responsible for one extraction
            execution. It receives an execution context and must return a
            dictionary with `status` and optional diagnostics fields.

    Returns:
        S4AIExtractCoreOutput: Stable output with extraction plan,
            execution diagnostics, and observability identifiers.

    Raises:
        S4AIExtractCoreError: If scaffold validation fails, extraction response
            is invalid, or extraction execution fails.
    """

    correlation_id = flow_input.correlation_id or f"xia-s4-{uuid4().hex[:12]}"
    extractor = execute_extraction or _default_extractor
    started_event_id = _new_event_id()
    logger.info(
        "etl_extract_ai_s4_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": flow_input.source_id,
            "source_kind": flow_input.source_kind,
            "quality_profile_hint": flow_input.quality_profile_hint,
            "consolidation_scope": flow_input.consolidation_scope,
            "ia_model_provider": flow_input.ia_model_provider,
        },
    )

    try:
        scaffold = build_s4_ai_extract_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        exec_context = {
            "correlation_id": correlation_id,
            "source_id": scaffold.source_id,
            "source_kind": scaffold.source_kind,
            "source_uri": scaffold.source_uri,
            "quality_profile_hint": scaffold.extraction_plan.get("quality_profile_hint"),
            "consolidation_scope": scaffold.extraction_plan.get("consolidation_scope"),
            "output_normalization_profile": scaffold.extraction_plan.get(
                "output_normalization_profile"
            ),
            "model_provider": scaffold.extraction_plan.get("ia_model_provider"),
            "model_name": scaffold.extraction_plan.get("ia_model_name"),
            "chunk_strategy": scaffold.extraction_plan.get("chunk_strategy"),
            "max_tokens_output": scaffold.extraction_plan.get("max_tokens_output"),
            "temperature": scaffold.extraction_plan.get("temperature"),
        }
        response = extractor(exec_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="extraction",
        )
        status = normalized["status"]

        completed_event_id = _new_event_id()
        logger.info(
            "etl_extract_ai_s4_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": scaffold.source_id,
                "source_kind": scaffold.source_kind,
                "status": status,
                "chunk_count": normalized.get("chunk_count"),
                "consolidation_group_id": normalized.get("consolidation_group_id"),
            },
        )

        if status not in XIA_S4_SUCCESS_STATUSES:
            raise S4AIExtractCoreError(
                code="XIA_S4_EXTRACTION_FAILED",
                message=f"Execucao de extracao XIA S4 falhou com status '{status}'",
                action=(
                    "Revisar logs de execucao da extracao calibrada e validar "
                    "quality_profile_hint/chunk_strategy/consolidation_scope."
                ),
                correlation_id=correlation_id,
                stage="extraction",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["extract_ai_core_module"] = (
            "etl.extract.ai.s4_core.execute_s4_ai_extract_main_flow"
        )
        return S4AIExtractCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            source_id=scaffold.source_id,
            source_kind=scaffold.source_kind,
            source_uri=scaffold.source_uri,
            extraction_plan=dict(scaffold.extraction_plan),
            execucao={
                "status": status,
                "chunk_count": int(normalized.get("chunk_count", 1)),
                "decision_reason": str(normalized.get("decision_reason", "dry_run_main_flow")),
                "provider_response_id": str(normalized.get("provider_response_id", "")),
                "consolidation_group_id": str(
                    normalized.get("consolidation_group_id", f"grp-{correlation_id}")
                ),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S4AIExtractScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "etl_extract_ai_s4_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S4AIExtractCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4AIExtractCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "etl_extract_ai_s4_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4AIExtractCoreError(
            code="XIA_S4_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal XIA S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor XIA S4.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S4AIExtractCoreError(
            code="INVALID_EXTRACTION_RESPONSE",
            message="Executor de extracao retornou resposta em formato invalido",
            action="Garantir retorno dict com campo 'status' no executor de extracao.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in XIA_S4_ALLOWED_EXEC_STATUSES:
        raise S4AIExtractCoreError(
            code="INVALID_EXTRACTION_STATUS",
            message=f"Status de execucao invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    if "chunk_count" in normalized:
        chunk_count = normalized["chunk_count"]
        if not isinstance(chunk_count, int) or chunk_count < 1:
            raise S4AIExtractCoreError(
                code="INVALID_EXTRACTION_CHUNK_COUNT",
                message=f"chunk_count invalido na resposta de execucao: {chunk_count}",
                action="Retorne chunk_count inteiro >= 1.",
                correlation_id=correlation_id,
                stage=stage,
            )
    return normalized


def _default_extractor(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one calibrated extraction pass in dry-run mode.

    Args:
        context: Structured execution context with source, quality, and model
            parameters.

    Returns:
        dict[str, Any]: Dry-run extraction execution result.
    """

    return {
        "status": "succeeded",
        "chunk_count": 1,
        "decision_reason": "dry_run_main_flow",
        "provider_response_id": f"dryrun-{context.get('correlation_id', '')}",
        "consolidation_group_id": f"grp-{context.get('correlation_id', '')}",
    }


def _new_event_id() -> str:
    return f"xias4coreevt-{uuid4().hex[:12]}"
