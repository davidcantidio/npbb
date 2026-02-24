"""Validation contracts for Sprint 2 batch reception journey.

This module centralizes Sprint 2 input/output validation used by tests and
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

from .s2_core import S2CoreInput
from .s2_observability import (
    S2ObservabilityInput,
    build_s2_observability_event,
    log_s2_observability_event,
)
from .s2_scaffold import (
    ACCEPTED_CONTENT_TYPES,
    EXPECTED_CONTENT_TYPE_BY_EXTENSION,
    MAX_BATCH_BYTES,
    MAX_BATCH_FILES,
    MAX_UPLOAD_BYTES,
    S2_BATCH_ID_RE,
    S2FileMetadata,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s2")

S2_VALIDATION_VERSION = "s2.validation.v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class S2ValidationError(ValueError):
    """Raised when Sprint 2 validation contract is violated."""

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
class S2ValidationInput:
    """Input contract consumed by Sprint 2 validation checks."""

    evento_id: int
    lote_id: str
    lote_nome: str
    origem_lote: str
    total_registros_estimados: int
    arquivos: tuple[S2FileMetadata, ...]
    correlation_id: str | None = None

    def to_core_input(self) -> S2CoreInput:
        """Convert validated data to `S2CoreInput` contract."""

        return S2CoreInput(
            evento_id=self.evento_id,
            lote_id=self.lote_id,
            lote_nome=self.lote_nome,
            origem_lote=self.origem_lote,
            total_registros_estimados=self.total_registros_estimados,
            arquivos=self.arquivos,
            correlation_id=self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2ValidationResult:
    """Output contract returned by Sprint 2 input validation."""

    validation_version: str
    validation_id: str
    correlation_id: str
    status: str
    checks: tuple[str, ...]
    observabilidade: dict[str, str]
    resumo_lote: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checks": list(self.checks),
            "observabilidade": self.observabilidade,
            "resumo_lote": self.resumo_lote,
        }


@dataclass(frozen=True, slots=True)
class S2FlowOutputValidationResult:
    """Output contract returned by Sprint 2 flow-output validation."""

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


def validate_s2_input_contract(payload: S2ValidationInput) -> S2ValidationResult:
    """Validate Sprint 2 input contract before running the main flow.

    Args:
        payload: Input contract with batch metadata and file list.

    Returns:
        S2ValidationResult: Validation metadata and performed checks.

    Raises:
        S2ValidationError: If any mandatory contract rule is violated.
    """

    correlation_id = payload.correlation_id or f"s2-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="ingestao_inteligente_s2_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 2 iniciada",
        severity="info",
        evento_id=payload.evento_id if payload.evento_id > 0 else None,
        lote_id=payload.lote_id,
    )
    checks: list[str] = []

    if payload.evento_id <= 0:
        _raise_validation_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de montar o lote.",
            correlation_id=correlation_id,
            context={"evento_id": payload.evento_id},
        )
    checks.append("evento_id")

    lote_id = payload.lote_id.strip()
    if not S2_BATCH_ID_RE.match(lote_id):
        _raise_validation_error(
            code="INVALID_LOTE_ID",
            message="lote_id invalido: use 3-80 chars [a-zA-Z0-9._-]",
            action="Defina um identificador de lote estavel para rastreabilidade.",
            correlation_id=correlation_id,
            context={"lote_id": payload.lote_id},
        )
    checks.append("lote_id")

    if len(payload.lote_nome.strip()) < 3:
        _raise_validation_error(
            code="INVALID_LOTE_NOME",
            message="lote_nome deve ter ao menos 3 caracteres",
            action="Informe um nome de lote descritivo para operacao.",
            correlation_id=correlation_id,
            context={"lote_nome": payload.lote_nome},
        )
    checks.append("lote_nome")

    if len(payload.origem_lote.strip()) < 3:
        _raise_validation_error(
            code="INVALID_ORIGEM_LOTE",
            message="origem_lote deve ter ao menos 3 caracteres",
            action="Informe origem operacional do lote (ex: upload_manual).",
            correlation_id=correlation_id,
            context={"origem_lote": payload.origem_lote},
        )
    checks.append("origem_lote")

    if payload.total_registros_estimados < 0:
        _raise_validation_error(
            code="INVALID_TOTAL_REGISTROS_ESTIMADOS",
            message="total_registros_estimados nao pode ser negativo",
            action="Informe quantidade estimada maior ou igual a zero.",
            correlation_id=correlation_id,
            context={"total_registros_estimados": payload.total_registros_estimados},
        )
    checks.append("total_registros_estimados")

    total_arquivos = len(payload.arquivos)
    if total_arquivos <= 0:
        _raise_validation_error(
            code="EMPTY_BATCH_FILES",
            message="arquivos nao pode ser vazio",
            action="Adicione ao menos um arquivo no lote antes de validar.",
            correlation_id=correlation_id,
        )
    if total_arquivos > MAX_BATCH_FILES:
        _raise_validation_error(
            code="BATCH_TOO_MANY_FILES",
            message=f"Lote excede o limite de {MAX_BATCH_FILES} arquivos",
            action="Divida o lote em partes menores para respeitar o limite.",
            correlation_id=correlation_id,
            context={"total_arquivos_lote": total_arquivos},
        )
    checks.append("arquivos")

    total_bytes_calculado = 0
    for index, arquivo in enumerate(payload.arquivos):
        total_bytes_calculado += _validate_file_metadata(
            arquivo=arquivo,
            index=index,
            correlation_id=correlation_id,
        )
    if total_bytes_calculado > MAX_BATCH_BYTES:
        _raise_validation_error(
            code="BATCH_TOO_LARGE",
            message=f"Lote excede o limite de {MAX_BATCH_BYTES} bytes",
            action="Divida o lote em partes menores para operacao segura.",
            correlation_id=correlation_id,
            context={"total_bytes_lote": total_bytes_calculado},
        )
    checks.append("total_bytes_lote_calculado")

    completed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s2_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 2 concluida com sucesso",
        severity="info",
        evento_id=payload.evento_id,
        lote_id=lote_id,
        context={
            "checks": checks,
            "total_arquivos_lote": total_arquivos,
            "total_bytes_lote": total_bytes_calculado,
        },
    )

    validation_id = f"val-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s2_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "lote_id": lote_id,
            "checks": checks,
            "total_arquivos_lote": total_arquivos,
            "total_bytes_lote": total_bytes_calculado,
        },
    )
    return S2ValidationResult(
        validation_version=S2_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
        resumo_lote={
            "total_arquivos_lote": total_arquivos,
            "total_bytes_lote": total_bytes_calculado,
            "total_registros_estimados": payload.total_registros_estimados,
        },
    )


def validate_s2_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S2FlowOutputValidationResult:
    """Validate Sprint 2 main-flow output contract.

    Args:
        flow_output: Output dictionary produced by `execute_s2_main_flow`.
        correlation_id: Correlation id propagated through Sprint 2 flow.

    Returns:
        S2FlowOutputValidationResult: Summary of checked output fields.

    Raises:
        S2ValidationError: If output contract is incomplete or inconsistent.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "evento_id",
        "lote_id",
        "lote_upload_id",
        "proxima_acao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
        "lote_upload",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo principal incompleta: faltam campos {missing_fields}",
            action="Atualize o core flow para retornar o contrato completo da sprint 2.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    if str(flow_output["status"]).lower() != "accepted":
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo principal: {flow_output['status']}",
            action="Garanta status 'accepted' quando o lote for aceito.",
            correlation_id=correlation_id,
            context={"status": str(flow_output["status"])},
        )

    observabilidade = flow_output.get("observabilidade", {})
    required_obs_fields = (
        "flow_started_event_id",
        "upload_dispatch_event_id",
        "flow_completed_event_id",
    )
    for field in required_obs_fields:
        value = str(observabilidade.get(field, ""))
        if not value.startswith("s2evt-"):
            _raise_validation_error(
                code="INVALID_OBSERVABILITY_OUTPUT",
                message=f"Campo de observabilidade invalido: {field}",
                action="Propague IDs de observabilidade 's2evt-*' no output do fluxo.",
                correlation_id=correlation_id,
                context={"field": field, "value": value},
            )

    lote_upload = flow_output.get("lote_upload", {})
    lote_upload_id = str(flow_output.get("lote_upload_id", ""))
    if str(lote_upload.get("lote_upload_id", "")) != lote_upload_id:
        _raise_validation_error(
            code="LOTE_UPLOAD_ID_MISMATCH",
            message="lote_upload_id divergente entre o topo e o bloco lote_upload",
            action="Garanta consistencia de lote_upload_id na saida do fluxo.",
            correlation_id=correlation_id,
            context={
                "top_level_lote_upload_id": lote_upload_id,
                "nested_lote_upload_id": str(lote_upload.get("lote_upload_id", "")),
            },
        )

    if int(lote_upload.get("evento_id", -1)) != int(flow_output["evento_id"]):
        _raise_validation_error(
            code="EVENTO_ID_MISMATCH",
            message="evento_id divergente entre o topo e o bloco lote_upload",
            action="Garanta consistencia de evento_id na saida do fluxo.",
            correlation_id=correlation_id,
            context={
                "top_level_evento_id": int(flow_output["evento_id"]),
                "nested_evento_id": int(lote_upload.get("evento_id", -1)),
            },
        )

    if str(lote_upload.get("lote_id", "")).strip() != str(flow_output["lote_id"]).strip():
        _raise_validation_error(
            code="LOTE_ID_MISMATCH",
            message="lote_id divergente entre o topo e o bloco lote_upload",
            action="Garanta consistencia de lote_id na saida do fluxo.",
            correlation_id=correlation_id,
            context={
                "top_level_lote_id": str(flow_output["lote_id"]).strip(),
                "nested_lote_id": str(lote_upload.get("lote_id", "")).strip(),
            },
        )

    logger.info(
        "ingestao_inteligente_s2_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "checked_fields": required_fields,
            "lote_id": str(flow_output["lote_id"]),
        },
    )
    return S2FlowOutputValidationResult(
        correlation_id=correlation_id,
        status="valid",
        checked_fields=required_fields,
        observabilidade={field: str(observabilidade[field]) for field in required_obs_fields},
    )


def _validate_file_metadata(
    *,
    arquivo: S2FileMetadata,
    index: int,
    correlation_id: str,
) -> int:
    nome_arquivo = arquivo.nome_arquivo.strip()
    if not nome_arquivo:
        _raise_validation_error(
            code="EMPTY_FILE_NAME",
            message=f"nome_arquivo vazio no item {index}",
            action="Preencha nome_arquivo para todos os itens do lote.",
            correlation_id=correlation_id,
            context={"item_index": index},
        )

    file_extension = Path(nome_arquivo).suffix.lower()
    if file_extension not in EXPECTED_CONTENT_TYPE_BY_EXTENSION:
        _raise_validation_error(
            code="UNSUPPORTED_FILE_EXTENSION",
            message=f"Extensao nao suportada no item {index}: {file_extension or '<sem_extensao>'}",
            action="Use arquivos .pdf, .xlsx ou .csv no lote.",
            correlation_id=correlation_id,
            context={
                "item_index": index,
                "nome_arquivo": nome_arquivo,
                "file_extension": file_extension or "<sem_extensao>",
            },
        )

    if arquivo.tamanho_arquivo_bytes <= 0:
        _raise_validation_error(
            code="INVALID_FILE_SIZE",
            message=f"tamanho_arquivo_bytes invalido no item {index}",
            action="Garanta tamanho maior que zero para cada arquivo.",
            correlation_id=correlation_id,
            context={
                "item_index": index,
                "tamanho_arquivo_bytes": arquivo.tamanho_arquivo_bytes,
            },
        )
    if arquivo.tamanho_arquivo_bytes > MAX_UPLOAD_BYTES:
        _raise_validation_error(
            code="FILE_TOO_LARGE",
            message=(
                f"Arquivo no item {index} excede limite de {MAX_UPLOAD_BYTES} bytes "
                f"({arquivo.tamanho_arquivo_bytes})"
            ),
            action="Divida ou compacte o arquivo para respeitar limite por item.",
            correlation_id=correlation_id,
            context={
                "item_index": index,
                "tamanho_arquivo_bytes": arquivo.tamanho_arquivo_bytes,
            },
        )

    content_type = arquivo.content_type.strip().lower()
    if content_type not in ACCEPTED_CONTENT_TYPES:
        _raise_validation_error(
            code="UNSUPPORTED_CONTENT_TYPE",
            message=f"content_type nao suportado no item {index}: {arquivo.content_type}",
            action="Ajuste content_type para .pdf, .xlsx ou .csv.",
            correlation_id=correlation_id,
            context={"item_index": index, "content_type": arquivo.content_type},
        )

    expected_content_type = EXPECTED_CONTENT_TYPE_BY_EXTENSION[file_extension]
    if content_type != expected_content_type:
        _raise_validation_error(
            code="FILE_EXTENSION_CONTENT_TYPE_MISMATCH",
            message=(
                f"Item {index}: arquivo {file_extension} deve usar content_type "
                f"{expected_content_type}, recebido {arquivo.content_type}"
            ),
            action="Corrija metadados para manter consistencia extensao/content_type.",
            correlation_id=correlation_id,
            context={
                "item_index": index,
                "file_extension": file_extension,
                "expected_content_type": expected_content_type,
                "received_content_type": arquivo.content_type,
            },
        )

    checksum = (arquivo.checksum_sha256 or "").strip().lower()
    if checksum and not SHA256_RE.match(checksum):
        _raise_validation_error(
            code="INVALID_CHECKSUM_SHA256",
            message=(
                f"checksum_sha256 invalido no item {index}: "
                "esperado hash hexadecimal com 64 caracteres"
            ),
            action="Recalcule o checksum SHA-256 antes de validar o lote.",
            correlation_id=correlation_id,
            context={"item_index": index, "checksum_sha256": arquivo.checksum_sha256 or ""},
        )

    return arquivo.tamanho_arquivo_bytes


def _raise_validation_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    failed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s2_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "ingestao_inteligente_s2_validation_error",
        extra={
            "correlation_id": correlation_id,
            "error_code": code,
            "error_message": message,
            "action": action,
            "context": context or {},
            "observability_event_id": failed_event.observability_event_id,
        },
    )
    raise S2ValidationError(
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
    lote_id: str | None = None,
    lote_upload_id: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S2ObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        context=context,
    )
    event = build_s2_observability_event(payload)
    log_s2_observability_event(event)
    return event
