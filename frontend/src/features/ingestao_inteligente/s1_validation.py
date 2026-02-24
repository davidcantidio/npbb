"""Validation contracts for Sprint 1 upload and event-selection journey.

This module centralizes input/output validation used by Sprint 1 tests and
integration checks. It provides structured, actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from .s1_core import S1CoreInput
from .s1_observability import (
    S1ObservabilityInput,
    build_s1_observability_event,
    log_s1_observability_event,
)
from .s1_scaffold import (
    ACCEPTED_CONTENT_TYPES,
    EXPECTED_CONTENT_TYPE_BY_EXTENSION,
    MAX_UPLOAD_BYTES,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s1")

S1_VALIDATION_VERSION = "s1.validation.v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class S1ValidationError(ValueError):
    """Raised when Sprint 1 validation contract is violated."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        observability_event_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.observability_event_id = observability_event_id

    def to_dict(self) -> dict[str, str]:
        """Return serializable actionable diagnostics payload."""
        payload = {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
        }
        if self.observability_event_id:
            payload["observability_event_id"] = self.observability_event_id
        return payload


@dataclass(frozen=True, slots=True)
class S1ValidationInput:
    """Input contract consumed by Sprint 1 validation checks."""

    evento_id: int
    nome_arquivo: str
    tamanho_arquivo_bytes: int
    content_type: str
    checksum_sha256: str | None = None
    correlation_id: str | None = None

    def to_core_input(self) -> S1CoreInput:
        """Convert validated data to `S1CoreInput` contract."""
        return S1CoreInput(
            evento_id=self.evento_id,
            nome_arquivo=self.nome_arquivo,
            tamanho_arquivo_bytes=self.tamanho_arquivo_bytes,
            content_type=self.content_type,
            checksum_sha256=self.checksum_sha256,
            correlation_id=self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1ValidationResult:
    """Output contract returned by Sprint 1 input validation."""

    validation_version: str
    validation_id: str
    correlation_id: str
    status: str
    checks: tuple[str, ...]
    observabilidade: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""
        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checks": list(self.checks),
            "observabilidade": self.observabilidade,
        }


@dataclass(frozen=True, slots=True)
class S1FlowOutputValidationResult:
    """Output contract returned by Sprint 1 flow-output validation."""

    correlation_id: str
    status: str
    checked_fields: tuple[str, ...]
    observabilidade: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""
        return {
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checked_fields": list(self.checked_fields),
            "observabilidade": self.observabilidade,
        }


def validate_s1_input_contract(payload: S1ValidationInput) -> S1ValidationResult:
    """Validate Sprint 1 input contract before running the main flow.

    Args:
        payload: Input contract with event selection and upload metadata.

    Returns:
        S1ValidationResult: Validation metadata and performed checks.

    Raises:
        S1ValidationError: If any mandatory contract rule is violated.
    """

    correlation_id = payload.correlation_id or f"s1-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="ingestao_inteligente_s1_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 1 iniciada",
        severity="info",
        evento_id=payload.evento_id if payload.evento_id > 0 else None,
    )
    checks: list[str] = []

    if payload.evento_id <= 0:
        _raise_validation_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de iniciar o upload.",
            correlation_id=correlation_id,
            context={"evento_id": payload.evento_id},
        )
    checks.append("evento_id")

    nome_arquivo = payload.nome_arquivo.strip()
    if not nome_arquivo:
        _raise_validation_error(
            code="EMPTY_FILE_NAME",
            message="nome_arquivo nao pode ser vazio",
            action="Informe o nome do arquivo antes de iniciar o fluxo.",
            correlation_id=correlation_id,
        )
    checks.append("nome_arquivo")

    file_extension = Path(nome_arquivo).suffix.lower()
    if file_extension not in EXPECTED_CONTENT_TYPE_BY_EXTENSION:
        _raise_validation_error(
            code="UNSUPPORTED_FILE_EXTENSION",
            message=f"Extensao de arquivo nao suportada: {file_extension or '<sem_extensao>'}",
            action="Use arquivos .pdf, .xlsx ou .csv.",
            correlation_id=correlation_id,
            context={"nome_arquivo": nome_arquivo},
        )
    checks.append("file_extension")

    if payload.tamanho_arquivo_bytes <= 0:
        _raise_validation_error(
            code="INVALID_FILE_SIZE",
            message="tamanho_arquivo_bytes deve ser maior que zero",
            action="Selecione um arquivo com conteudo valido.",
            correlation_id=correlation_id,
            context={"tamanho_arquivo_bytes": payload.tamanho_arquivo_bytes},
        )
    if payload.tamanho_arquivo_bytes > MAX_UPLOAD_BYTES:
        _raise_validation_error(
            code="FILE_TOO_LARGE",
            message=f"Arquivo excede o limite de {MAX_UPLOAD_BYTES} bytes",
            action="Reduza o tamanho do arquivo ou divida o lote.",
            correlation_id=correlation_id,
            context={"tamanho_arquivo_bytes": payload.tamanho_arquivo_bytes},
        )
    checks.append("tamanho_arquivo_bytes")

    content_type = payload.content_type.strip().lower()
    if content_type not in ACCEPTED_CONTENT_TYPES:
        _raise_validation_error(
            code="UNSUPPORTED_CONTENT_TYPE",
            message=f"content_type nao suportado: {payload.content_type}",
            action="Use content_type valido para .pdf, .xlsx ou .csv.",
            correlation_id=correlation_id,
            context={"content_type": payload.content_type},
        )

    expected_content_type = EXPECTED_CONTENT_TYPE_BY_EXTENSION[file_extension]
    if content_type != expected_content_type:
        _raise_validation_error(
            code="FILE_EXTENSION_CONTENT_TYPE_MISMATCH",
            message=(
                f"Arquivo {file_extension} deve usar content_type "
                f"{expected_content_type}, recebido {payload.content_type}"
            ),
            action="Ajuste o content_type enviado para combinar com a extensao.",
            correlation_id=correlation_id,
            context={
                "file_extension": file_extension,
                "expected_content_type": expected_content_type,
                "received_content_type": payload.content_type,
            },
        )
    checks.append("content_type")

    checksum = (payload.checksum_sha256 or "").strip().lower()
    if checksum and not SHA256_RE.match(checksum):
        _raise_validation_error(
            code="INVALID_CHECKSUM_SHA256",
            message="checksum_sha256 invalido: esperado hash hexadecimal com 64 caracteres",
            action="Recalcule o checksum SHA-256 antes de continuar.",
            correlation_id=correlation_id,
            context={"checksum_sha256": payload.checksum_sha256 or ""},
        )
    checks.append("checksum_sha256")

    completed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s1_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 1 concluida com sucesso",
        severity="info",
        evento_id=payload.evento_id,
        context={"checks": checks},
    )

    validation_id = f"val-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s1_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
        },
    )
    return S1ValidationResult(
        validation_version=S1_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_s1_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S1FlowOutputValidationResult:
    """Validate Sprint 1 main-flow output contract.

    Args:
        flow_output: Output dictionary produced by `execute_s1_main_flow`.
        correlation_id: Correlation id propagated through the Sprint 1 flow.

    Returns:
        S1FlowOutputValidationResult: Summary of checked output fields.

    Raises:
        S1ValidationError: If output contract is incomplete or inconsistent.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "evento_id",
        "upload_id",
        "proxima_acao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
        "upload",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo principal incompleta: faltam campos {missing_fields}",
            action="Atualize o core flow para retornar o contrato completo da sprint.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    if str(flow_output["status"]).lower() != "accepted":
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo principal: {flow_output['status']}",
            action="Garanta status 'accepted' quando upload for aceito.",
            correlation_id=correlation_id,
            context={"status": str(flow_output["status"])},
        )

    observabilidade = flow_output.get("observabilidade", {})
    required_obs_fields = ("flow_start_event_id", "upload_dispatch_event_id", "flow_completed_event_id")
    for field in required_obs_fields:
        value = str(observabilidade.get(field, ""))
        if not value.startswith("obs-"):
            _raise_validation_error(
                code="INVALID_OBSERVABILITY_OUTPUT",
                message=f"Campo de observabilidade invalido: {field}",
                action="Propague IDs de observabilidade 'obs-*' no output do fluxo.",
                correlation_id=correlation_id,
                context={"field": field, "value": value},
            )

    logger.info(
        "ingestao_inteligente_s1_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "checked_fields": required_fields,
        },
    )
    return S1FlowOutputValidationResult(
        correlation_id=correlation_id,
        status="valid",
        checked_fields=required_fields,
        observabilidade={field: str(observabilidade[field]) for field in required_obs_fields},
    )


def _raise_validation_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    failed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s1_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "ingestao_inteligente_s1_validation_error",
        extra={
            "correlation_id": correlation_id,
            "error_code": code,
            "error_message": message,
            "action": action,
            "context": context or {},
            "observability_event_id": failed_event.observability_event_id,
        },
    )
    raise S1ValidationError(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        observability_event_id=failed_event.observability_event_id,
    )


def _emit_observability_event(
    *,
    event_name: str,
    correlation_id: str,
    event_message: str,
    severity: str,
    evento_id: int | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S1ObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=evento_id,
        context=context,
    )
    event = build_s1_observability_event(payload)
    log_s1_observability_event(event)
    return event
