"""Sprint 4 scaffold contracts for calibrated AI extraction consolidation.

This module defines the stable input/output contract used by XIA Sprint 4 to
calibrate quality by source format and prepare cross-format consolidation.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.extract.ai.s4")

CONTRACT_VERSION = "xia.s4.v1"
BACKEND_XIA_S4_PREPARE_ENDPOINT = "/internal/etl/extract/ai/s4/prepare"
SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")

ALLOWED_SOURCE_KINDS = ("pdf", "docx", "pptx", "xlsx", "csv", "pdf_scan", "jpg", "png")
ALLOWED_MODEL_PROVIDERS = ("openai", "azure_openai", "anthropic", "local")
ALLOWED_CHUNK_STRATEGIES = (
    "section",
    "page",
    "paragraph",
    "slide",
    "sheet",
    "row_block",
    "image",
    "region",
)
ALLOWED_QUALITY_PROFILE_HINTS = (
    "strict_textual",
    "table_sensitive",
    "ocr_resilient",
    "multimodal_document",
)
ALLOWED_CONSOLIDATION_SCOPES = ("single_source", "batch_session", "cross_format_event")
ALLOWED_OUTPUT_NORMALIZATION_PROFILES = ("canonical_fields_v1", "canonical_fields_v2")
MIN_MAX_TOKENS = 128
MAX_MAX_TOKENS = 8192

_SOURCE_KIND_CHUNK_STRATEGY = {
    "pdf": {"section", "page", "paragraph"},
    "docx": {"section", "paragraph"},
    "pptx": {"slide"},
    "xlsx": {"sheet", "row_block"},
    "csv": {"sheet", "row_block"},
    "pdf_scan": {"page", "region"},
    "jpg": {"image", "region"},
    "png": {"image", "region"},
}


class S4AIExtractScaffoldError(ValueError):
    """Raised when XIA S4 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4AIExtractScaffoldRequest:
    """Input contract for XIA Sprint 4 scaffold validation."""

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

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible XIA Sprint 4 contract."""

        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "quality_profile_hint": self.quality_profile_hint,
            "consolidation_scope": self.consolidation_scope,
            "output_normalization_profile": self.output_normalization_profile,
            "ia_model_provider": self.ia_model_provider,
            "ia_model_name": self.ia_model_name,
            "chunk_strategy": self.chunk_strategy,
            "max_tokens_output": self.max_tokens_output,
            "temperature": self.temperature,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4AIExtractScaffoldResponse:
    """Output contract returned when XIA Sprint 4 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    extraction_plan: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "extraction_plan": self.extraction_plan,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s4_ai_extract_scaffold_contract(
    request: S4AIExtractScaffoldRequest,
) -> S4AIExtractScaffoldResponse:
    """Build XIA Sprint 4 scaffold contract for calibrated extraction.

    Args:
        request: Extraction input contract with source metadata, quality
            calibration, and consolidation parameters.

    Returns:
        S4AIExtractScaffoldResponse: Stable scaffold output with calibrated
            extraction plan and integration points.

    Raises:
        S4AIExtractScaffoldError: If one or more XIA Sprint 4 input rules fail.
    """

    correlation_id = request.correlation_id or f"xia-s4-{uuid4().hex[:12]}"
    logger.info(
        "etl_extract_ai_s4_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "source_uri": request.source_uri,
            "quality_profile_hint": request.quality_profile_hint,
            "consolidation_scope": request.consolidation_scope,
            "output_normalization_profile": request.output_normalization_profile,
            "ia_model_provider": request.ia_model_provider,
            "ia_model_name": request.ia_model_name,
            "chunk_strategy": request.chunk_strategy,
            "max_tokens_output": request.max_tokens_output,
            "temperature": request.temperature,
        },
    )

    (
        source_id,
        source_kind,
        source_uri,
        quality_profile_hint,
        consolidation_scope,
        output_normalization_profile,
        provider,
        model_name,
        chunk_strategy,
        max_tokens_output,
        temperature,
    ) = _validate_s4_input(request=request)

    extraction_plan = {
        "modo_extracao": "ai_calibrada_s4",
        "source_kind": source_kind,
        "quality_profile_hint": quality_profile_hint,
        "consolidation_scope": consolidation_scope,
        "output_normalization_profile": output_normalization_profile,
        "ia_model_provider": provider,
        "ia_model_name": model_name,
        "chunk_strategy": chunk_strategy,
        "max_tokens_output": max_tokens_output,
        "temperature": temperature,
        "campos_obrigatorios": [
            "correlation_id",
            "source_id",
            "source_kind",
            "calibration_profile",
            "chunk_index",
            "consolidation_group_id",
            "model_name",
        ],
    }

    response = S4AIExtractScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        extraction_plan=extraction_plan,
        pontos_integracao={
            "xia_s4_prepare_endpoint": BACKEND_XIA_S4_PREPARE_ENDPOINT,
            "extract_ai_service_module": "app.services.etl_extract_ai_service.execute_s4_extract_ai_service",
            "orchestrator_route_module": "app.services.etl_orchestrator_service.execute_s4_orchestrator_service",
            "extract_ai_s4_core_module": "etl.extract.ai.s4_core.execute_s4_ai_extract_main_flow",
        },
    )
    logger.info(
        "etl_extract_ai_s4_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "quality_profile_hint": quality_profile_hint,
            "consolidation_scope": consolidation_scope,
            "chunk_strategy": chunk_strategy,
        },
    )
    return response


def _validate_s4_input(
    *,
    request: S4AIExtractScaffoldRequest,
) -> tuple[str, str, str, str, str, str, str, str, str, int, float]:
    source_id = _normalize_source_id(request.source_id)

    source_kind = request.source_kind.strip().lower()
    if source_kind not in ALLOWED_SOURCE_KINDS:
        _raise_contract_error(
            code="INVALID_SOURCE_KIND",
            message=f"source_kind invalido: {request.source_kind}",
            action="Use source_kind suportado para sprint 4: pdf, docx, pptx, xlsx, csv, pdf_scan, jpg ou png.",
        )

    source_uri = request.source_uri.strip()
    if len(source_uri) < 3:
        _raise_contract_error(
            code="INVALID_SOURCE_URI",
            message="source_uri invalido: informe URI/caminho com ao menos 3 caracteres",
            action="Forneca o caminho/URI do artefato para rastreabilidade operacional.",
        )

    quality_profile_hint = request.quality_profile_hint.strip().lower()
    if quality_profile_hint not in ALLOWED_QUALITY_PROFILE_HINTS:
        _raise_contract_error(
            code="INVALID_QUALITY_PROFILE_HINT",
            message=f"quality_profile_hint invalido: {request.quality_profile_hint}",
            action="Use quality_profile_hint valido: strict_textual, table_sensitive, ocr_resilient ou multimodal_document.",
        )

    consolidation_scope = request.consolidation_scope.strip().lower()
    if consolidation_scope not in ALLOWED_CONSOLIDATION_SCOPES:
        _raise_contract_error(
            code="INVALID_CONSOLIDATION_SCOPE",
            message=f"consolidation_scope invalido: {request.consolidation_scope}",
            action="Use consolidation_scope valido: single_source, batch_session ou cross_format_event.",
        )

    output_normalization_profile = request.output_normalization_profile.strip().lower()
    if output_normalization_profile not in ALLOWED_OUTPUT_NORMALIZATION_PROFILES:
        _raise_contract_error(
            code="INVALID_OUTPUT_NORMALIZATION_PROFILE",
            message=(
                "output_normalization_profile invalido: "
                f"{request.output_normalization_profile}"
            ),
            action="Use output_normalization_profile valido: canonical_fields_v1 ou canonical_fields_v2.",
        )

    provider = request.ia_model_provider.strip().lower()
    if provider not in ALLOWED_MODEL_PROVIDERS:
        _raise_contract_error(
            code="INVALID_IA_MODEL_PROVIDER",
            message=f"ia_model_provider invalido: {request.ia_model_provider}",
            action="Use provider suportado: openai, azure_openai, anthropic ou local.",
        )

    model_name = request.ia_model_name.strip()
    if len(model_name) < 2:
        _raise_contract_error(
            code="INVALID_IA_MODEL_NAME",
            message="ia_model_name invalido: informe nome do modelo com ao menos 2 caracteres",
            action="Defina modelo IA valido para executar extracao calibrada.",
        )

    chunk_strategy = request.chunk_strategy.strip().lower()
    if chunk_strategy not in ALLOWED_CHUNK_STRATEGIES:
        _raise_contract_error(
            code="INVALID_CHUNK_STRATEGY",
            message=f"chunk_strategy invalida: {request.chunk_strategy}",
            action=(
                "Use chunk_strategy suportada: section, page, paragraph, slide, "
                "sheet, row_block, image ou region."
            ),
        )

    allowed_chunk_strategies = _SOURCE_KIND_CHUNK_STRATEGY[source_kind]
    if chunk_strategy not in allowed_chunk_strategies:
        _raise_contract_error(
            code="INVALID_CHUNK_STRATEGY_FOR_SOURCE_KIND",
            message=(
                f"chunk_strategy invalida para source_kind={source_kind}: "
                f"{request.chunk_strategy}"
            ),
            action=(
                f"Para source_kind={source_kind} use chunk_strategy entre: "
                f"{', '.join(sorted(allowed_chunk_strategies))}."
            ),
        )

    max_tokens_output = request.max_tokens_output
    if (
        not isinstance(max_tokens_output, int)
        or max_tokens_output < MIN_MAX_TOKENS
        or max_tokens_output > MAX_MAX_TOKENS
    ):
        _raise_contract_error(
            code="INVALID_MAX_TOKENS_OUTPUT",
            message=f"max_tokens_output fora do intervalo suportado: {request.max_tokens_output}",
            action=f"Use max_tokens_output entre {MIN_MAX_TOKENS} e {MAX_MAX_TOKENS}.",
        )

    if not isinstance(request.temperature, (int, float)):
        _raise_contract_error(
            code="INVALID_TEMPERATURE_TYPE",
            message="temperature deve ser numerico",
            action="Informe temperature como numero entre 0 e 1.",
        )
    temperature = float(request.temperature)
    if temperature < 0 or temperature > 1:
        _raise_contract_error(
            code="INVALID_TEMPERATURE",
            message=f"temperature invalida: {request.temperature}",
            action="Use temperature entre 0 e 1.",
        )

    return (
        source_id,
        source_kind,
        source_uri,
        quality_profile_hint,
        consolidation_scope,
        output_normalization_profile,
        provider,
        model_name,
        chunk_strategy,
        max_tokens_output,
        round(temperature, 4),
    )


def _normalize_source_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not SOURCE_ID_RE.match(normalized):
        _raise_contract_error(
            code="INVALID_SOURCE_ID",
            message="source_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action=(
                "Padronize source_id para formato estavel de auditoria "
                "(ex: SRC_S4_TMJ_2025_001)."
            ),
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "etl_extract_ai_s4_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S4AIExtractScaffoldError(code=code, message=message, action=action)
