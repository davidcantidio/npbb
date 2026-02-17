"""Sprint 3 scaffold contracts for AI extraction on scanned document formats.

This module defines the stable input/output contract used by XIA Sprint 3 to
prepare AI extraction for PDF scan and JPG/PNG document images.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.extract.ai.s3")

CONTRACT_VERSION = "xia.s3.v1"
BACKEND_XIA_S3_PREPARE_ENDPOINT = "/internal/etl/extract/ai/s3/prepare"
SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")

ALLOWED_SOURCE_KINDS = ("pdf_scan", "jpg", "png")
ALLOWED_MODEL_PROVIDERS = ("openai", "azure_openai", "anthropic", "local")
ALLOWED_CHUNK_STRATEGIES = ("page", "image", "region")
ALLOWED_DOCUMENT_PROFILE_HINTS = (
    "pdf_scan_document",
    "image_document",
    "image_id_document",
)
ALLOWED_IMAGE_PREPROCESS_HINTS = ("none", "deskew", "denoise", "ocr_enhanced")
MIN_MAX_TOKENS = 128
MAX_MAX_TOKENS = 8192


class S3AIExtractScaffoldError(ValueError):
    """Raised when XIA S3 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3AIExtractScaffoldRequest:
    """Input contract for XIA Sprint 3 scaffold validation."""

    source_id: str
    source_kind: str
    source_uri: str
    document_profile_hint: str | None = None
    image_preprocess_hint: str | None = None
    ia_model_provider: str = "openai"
    ia_model_name: str = "gpt-4.1-mini"
    chunk_strategy: str = "page"
    max_tokens_output: int = 4096
    temperature: float = 0.0
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible XIA Sprint 3 contract."""

        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "document_profile_hint": self.document_profile_hint,
            "image_preprocess_hint": self.image_preprocess_hint,
            "ia_model_provider": self.ia_model_provider,
            "ia_model_name": self.ia_model_name,
            "chunk_strategy": self.chunk_strategy,
            "max_tokens_output": self.max_tokens_output,
            "temperature": self.temperature,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3AIExtractScaffoldResponse:
    """Output contract returned when XIA Sprint 3 scaffold is valid."""

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


def build_s3_ai_extract_scaffold_contract(
    request: S3AIExtractScaffoldRequest,
) -> S3AIExtractScaffoldResponse:
    """Build XIA Sprint 3 scaffold contract for AI extraction preparation.

    Args:
        request: Extraction input contract with source metadata and model
            execution parameters.

    Returns:
        S3AIExtractScaffoldResponse: Stable scaffold output with extraction
            plan and integration points.

    Raises:
        S3AIExtractScaffoldError: If one or more XIA Sprint 3 input rules fail.
    """

    correlation_id = request.correlation_id or f"xia-s3-{uuid4().hex[:12]}"
    logger.info(
        "etl_extract_ai_s3_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "source_uri": request.source_uri,
            "document_profile_hint": request.document_profile_hint,
            "image_preprocess_hint": request.image_preprocess_hint,
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
        profile_hint,
        image_preprocess_hint,
        provider,
        model_name,
        chunk_strategy,
        max_tokens_output,
        temperature,
    ) = _validate_s3_input(request=request)

    extraction_plan = {
        "modo_extracao": "ai_documento_scan_s3",
        "source_kind": source_kind,
        "document_profile_hint": profile_hint,
        "image_preprocess_hint": image_preprocess_hint,
        "ia_model_provider": provider,
        "ia_model_name": model_name,
        "chunk_strategy": chunk_strategy,
        "max_tokens_output": max_tokens_output,
        "temperature": temperature,
        "campos_obrigatorios": [
            "correlation_id",
            "source_id",
            "source_kind",
            "chunk_index",
            "ocr_confidence",
            "model_name",
        ],
    }

    response = S3AIExtractScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        extraction_plan=extraction_plan,
        pontos_integracao={
            "xia_s3_prepare_endpoint": BACKEND_XIA_S3_PREPARE_ENDPOINT,
            "extract_ai_service_module": "app.services.etl_extract_ai_service.execute_s3_extract_ai_service",
            "pdf_profile_module": "etl.extract.pdf_profile",
            "image_extraction_module": "etl.extract.extract_pdf_assisted",
        },
    )
    logger.info(
        "etl_extract_ai_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "ia_model_provider": provider,
            "chunk_strategy": chunk_strategy,
        },
    )
    return response


def _validate_s3_input(
    *,
    request: S3AIExtractScaffoldRequest,
) -> tuple[str, str, str, str | None, str | None, str, str, str, int, float]:
    source_id = _normalize_source_id(request.source_id)

    source_kind = request.source_kind.strip().lower()
    if source_kind not in ALLOWED_SOURCE_KINDS:
        _raise_contract_error(
            code="INVALID_SOURCE_KIND",
            message=f"source_kind invalido: {request.source_kind}",
            action="Use source_kind suportado para sprint 3: pdf_scan, jpg ou png.",
        )

    source_uri = request.source_uri.strip()
    if len(source_uri) < 3:
        _raise_contract_error(
            code="INVALID_SOURCE_URI",
            message="source_uri invalido: informe URI/caminho com ao menos 3 caracteres",
            action="Forneca o caminho/URI do artefato para rastreabilidade operacional.",
        )

    profile_hint = (request.document_profile_hint or "").strip().lower() or None
    if profile_hint and profile_hint not in ALLOWED_DOCUMENT_PROFILE_HINTS:
        _raise_contract_error(
            code="INVALID_DOCUMENT_PROFILE_HINT",
            message=f"document_profile_hint invalido: {request.document_profile_hint}",
            action="Use profile hint suportado para sprint 3 (pdf_scan/jpg/png).",
        )

    image_preprocess_hint = (request.image_preprocess_hint or "").strip().lower() or None
    if image_preprocess_hint and image_preprocess_hint not in ALLOWED_IMAGE_PREPROCESS_HINTS:
        _raise_contract_error(
            code="INVALID_IMAGE_PREPROCESS_HINT",
            message=f"image_preprocess_hint invalido: {request.image_preprocess_hint}",
            action="Use image_preprocess_hint valido: none, deskew, denoise ou ocr_enhanced.",
        )
    if source_kind == "pdf_scan" and image_preprocess_hint == "none":
        _raise_contract_error(
            code="INVALID_IMAGE_PREPROCESS_HINT_FOR_PDF_SCAN",
            message="image_preprocess_hint=none nao e recomendado para source_kind=pdf_scan",
            action="Para PDF scan use deskew, denoise ou ocr_enhanced.",
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
            action="Defina modelo IA valido para executar extracao delimitada.",
        )

    chunk_strategy = request.chunk_strategy.strip().lower()
    if chunk_strategy not in ALLOWED_CHUNK_STRATEGIES:
        _raise_contract_error(
            code="INVALID_CHUNK_STRATEGY",
            message=f"chunk_strategy invalida: {request.chunk_strategy}",
            action="Use chunk_strategy suportada: page, image ou region.",
        )

    if source_kind == "pdf_scan" and chunk_strategy != "page":
        _raise_contract_error(
            code="INVALID_CHUNK_STRATEGY_FOR_PDF_SCAN",
            message=f"chunk_strategy invalida para pdf_scan: {request.chunk_strategy}",
            action="Para PDF scan use chunk_strategy=page.",
        )
    if source_kind in {"jpg", "png"} and chunk_strategy == "page":
        _raise_contract_error(
            code="INVALID_CHUNK_STRATEGY_FOR_IMAGE",
            message=f"chunk_strategy invalida para imagem: {request.chunk_strategy}",
            action="Para JPG/PNG use chunk_strategy=image ou region.",
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
        profile_hint,
        image_preprocess_hint,
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
            action="Padronize source_id para formato estavel de auditoria (ex: SRC_PDFSCAN_TMJ_2025).",
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "etl_extract_ai_s3_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S3AIExtractScaffoldError(code=code, message=message, action=action)
