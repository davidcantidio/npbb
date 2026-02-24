"""Base contract scaffold for Sprint 1 upload and event-selection flow.

The goal is to keep a stable and testable contract for the first integration
between UI and API, before the full upload pipeline is delivered.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.ingestao_inteligente.s1")

CONTRACT_VERSION = "s1.v1"
BACKEND_SCAFFOLD_ENDPOINT = "/internal/ingestao-inteligente/s1/scaffold"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

EXPECTED_CONTENT_TYPE_BY_EXTENSION: dict[str, str] = {
    ".csv": "text/csv",
    ".pdf": "application/pdf",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
ACCEPTED_CONTENT_TYPES = tuple(sorted(EXPECTED_CONTENT_TYPE_BY_EXTENSION.values()))


class S1ScaffoldContractError(ValueError):
    """Raised when the Sprint 1 scaffold contract is violated."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return a serializable error payload used by UI diagnostics."""
        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1ScaffoldRequest:
    """Input contract for Sprint 1 scaffold validation."""

    evento_id: int
    nome_arquivo: str
    tamanho_arquivo_bytes: int
    content_type: str
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request data in the exact API contract expected by backend."""
        return {
            "evento_id": self.evento_id,
            "nome_arquivo": self.nome_arquivo,
            "tamanho_arquivo_bytes": self.tamanho_arquivo_bytes,
            "content_type": self.content_type,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S1ScaffoldResponse:
    """Output contract returned when scaffold validation succeeds."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    tamanho_maximo_bytes: int
    content_types_aceitos: tuple[str, ...]
    proxima_acao: str
    endpoint_backend: str

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for integration tests and logging."""
        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "evento_id": self.evento_id,
            "tamanho_maximo_bytes": self.tamanho_maximo_bytes,
            "content_types_aceitos": list(self.content_types_aceitos),
            "proxima_acao": self.proxima_acao,
            "endpoint_backend": self.endpoint_backend,
        }


def build_s1_scaffold_contract(request: S1ScaffoldRequest) -> S1ScaffoldResponse:
    """Build the Sprint 1 scaffold contract for upload + event selection.

    Args:
        request: Component input with selected event id and upload metadata.

    Returns:
        Stable output contract with limits and the backend integration endpoint.

    Raises:
        S1ScaffoldContractError: When request input is invalid or unsupported.
    """

    correlation_id = request.correlation_id or f"s1-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s1_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "nome_arquivo": request.nome_arquivo,
            "tamanho_arquivo_bytes": request.tamanho_arquivo_bytes,
            "content_type": request.content_type,
        },
    )

    _validate_contract_input(request)
    response = S1ScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        evento_id=request.evento_id,
        tamanho_maximo_bytes=MAX_UPLOAD_BYTES,
        content_types_aceitos=ACCEPTED_CONTENT_TYPES,
        proxima_acao="upload_arquivo",
        endpoint_backend=BACKEND_SCAFFOLD_ENDPOINT,
    )
    logger.info(
        "ingestao_inteligente_s1_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "status": response.status,
        },
    )
    return response


def _validate_contract_input(request: S1ScaffoldRequest) -> None:
    if request.evento_id <= 0:
        _raise_contract_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de iniciar o upload.",
        )

    nome_arquivo = request.nome_arquivo.strip()
    if not nome_arquivo:
        _raise_contract_error(
            code="EMPTY_FILE_NAME",
            message="nome_arquivo nao pode ser vazio",
            action="Informe o nome do arquivo antes de enviar para o backend.",
        )

    file_extension = Path(nome_arquivo).suffix.lower()
    if file_extension not in EXPECTED_CONTENT_TYPE_BY_EXTENSION:
        _raise_contract_error(
            code="UNSUPPORTED_FILE_EXTENSION",
            message=f"Extensao de arquivo nao suportada: {file_extension or '<sem_extensao>'}",
            action="Use arquivos .pdf, .xlsx ou .csv.",
        )

    if request.tamanho_arquivo_bytes <= 0:
        _raise_contract_error(
            code="INVALID_FILE_SIZE",
            message="tamanho_arquivo_bytes deve ser maior que zero",
            action="Selecione um arquivo com conteudo valido.",
        )
    if request.tamanho_arquivo_bytes > MAX_UPLOAD_BYTES:
        _raise_contract_error(
            code="FILE_TOO_LARGE",
            message=f"Arquivo excede o limite de {MAX_UPLOAD_BYTES} bytes",
            action="Reduza o tamanho do arquivo ou divida o lote.",
        )

    content_type = request.content_type.strip().lower()
    if content_type not in ACCEPTED_CONTENT_TYPES:
        _raise_contract_error(
            code="UNSUPPORTED_CONTENT_TYPE",
            message=f"content_type nao suportado: {request.content_type}",
            action="Use um content_type valido para arquivos .pdf, .xlsx ou .csv.",
        )

    expected_content_type = EXPECTED_CONTENT_TYPE_BY_EXTENSION[file_extension]
    if content_type != expected_content_type:
        _raise_contract_error(
            code="FILE_EXTENSION_CONTENT_TYPE_MISMATCH",
            message=(
                f"Arquivo {file_extension} deve usar content_type "
                f"{expected_content_type}, recebido {request.content_type}"
            ),
            action="Ajuste o content_type enviado pelo frontend para combinar com a extensao.",
        )


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "ingestao_inteligente_s1_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S1ScaffoldContractError(code=code, message=message, action=action)
