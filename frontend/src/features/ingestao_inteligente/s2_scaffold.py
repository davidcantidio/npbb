"""Base scaffold contract for Sprint 2 batch file reception journey.

Sprint 2 expands Sprint 1 from single-file upload metadata to batch-level
metadata reception with one stable contract shared by frontend and backend.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from .s1_scaffold import (
    ACCEPTED_CONTENT_TYPES,
    EXPECTED_CONTENT_TYPE_BY_EXTENSION,
    MAX_UPLOAD_BYTES,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s2")

CONTRACT_VERSION = "s2.v1"
BACKEND_S2_SCAFFOLD_ENDPOINT = "/internal/ingestao-inteligente/s2/scaffold"
MAX_BATCH_FILES = 100
MAX_BATCH_BYTES = 300 * 1024 * 1024

S2_BATCH_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,79}$")


class S2ScaffoldContractError(ValueError):
    """Raised when Sprint 2 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""
        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2FileMetadata:
    """One file metadata entry in Sprint 2 batch contract."""

    nome_arquivo: str
    tamanho_arquivo_bytes: int
    content_type: str
    checksum_sha256: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize one file metadata entry."""
        payload = {
            "nome_arquivo": self.nome_arquivo,
            "tamanho_arquivo_bytes": self.tamanho_arquivo_bytes,
            "content_type": self.content_type,
        }
        if self.checksum_sha256:
            payload["checksum_sha256"] = self.checksum_sha256
        return payload


@dataclass(frozen=True, slots=True)
class S2ScaffoldRequest:
    """Input contract for Sprint 2 scaffold validation."""

    evento_id: int
    lote_id: str
    lote_nome: str
    origem_lote: str
    total_arquivos_lote: int
    total_bytes_lote: int
    total_registros_estimados: int
    arquivos: tuple[S2FileMetadata, ...]
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible Sprint 2 contract."""
        return {
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_nome": self.lote_nome,
            "origem_lote": self.origem_lote,
            "total_arquivos_lote": self.total_arquivos_lote,
            "total_bytes_lote": self.total_bytes_lote,
            "total_registros_estimados": self.total_registros_estimados,
            "arquivos": [item.to_dict() for item in self.arquivos],
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2ScaffoldResponse:
    """Output contract returned when Sprint 2 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    proxima_acao: str
    limites_lote: dict[str, Any]
    pontos_integracao: dict[str, str]
    recepcao_lote: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""
        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "proxima_acao": self.proxima_acao,
            "limites_lote": self.limites_lote,
            "pontos_integracao": self.pontos_integracao,
            "recepcao_lote": self.recepcao_lote,
        }


def build_s2_scaffold_contract(request: S2ScaffoldRequest) -> S2ScaffoldResponse:
    """Build Sprint 2 scaffold contract for batch metadata reception.

    Args:
        request: Batch metadata input payload from Sprint 2 interface.

    Returns:
        S2ScaffoldResponse: Stable scaffold output with limits and integrations.

    Raises:
        S2ScaffoldContractError: If one or more batch metadata rules fail.
    """

    correlation_id = request.correlation_id or f"s2-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s2_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "lote_id": request.lote_id,
            "total_arquivos_lote": request.total_arquivos_lote,
            "total_bytes_lote": request.total_bytes_lote,
        },
    )

    _validate_s2_contract_input(request=request)
    response = S2ScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        evento_id=request.evento_id,
        lote_id=request.lote_id.strip(),
        proxima_acao="receber_arquivos_lote",
        limites_lote={
            "max_arquivos_lote": MAX_BATCH_FILES,
            "max_bytes_lote": MAX_BATCH_BYTES,
            "max_upload_bytes_por_arquivo": MAX_UPLOAD_BYTES,
            "content_types_aceitos": list(ACCEPTED_CONTENT_TYPES),
        },
        pontos_integracao={
            "s2_scaffold_endpoint": BACKEND_S2_SCAFFOLD_ENDPOINT,
            "s2_lote_upload_endpoint": "/internal/ingestao-inteligente/s2/lote/upload",
            "s1_upload_endpoint": "/internal/ingestao-inteligente/s1/upload",
        },
        recepcao_lote={
            "total_arquivos_lote": request.total_arquivos_lote,
            "total_bytes_lote": request.total_bytes_lote,
            "total_registros_estimados": request.total_registros_estimados,
        },
    )
    logger.info(
        "ingestao_inteligente_s2_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "lote_id": request.lote_id.strip(),
            "status": response.status,
        },
    )
    return response


def _validate_s2_contract_input(*, request: S2ScaffoldRequest) -> None:
    if request.evento_id <= 0:
        _raise_contract_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de montar o lote.",
        )

    lote_id = request.lote_id.strip()
    if not S2_BATCH_ID_RE.match(lote_id):
        _raise_contract_error(
            code="INVALID_LOTE_ID",
            message="lote_id invalido: use 3-80 chars [a-zA-Z0-9._-]",
            action="Defina um identificador de lote estavel para rastreabilidade.",
        )

    if len(request.lote_nome.strip()) < 3:
        _raise_contract_error(
            code="INVALID_LOTE_NOME",
            message="lote_nome deve ter ao menos 3 caracteres",
            action="Informe um nome de lote descritivo para operacao.",
        )
    if len(request.origem_lote.strip()) < 3:
        _raise_contract_error(
            code="INVALID_ORIGEM_LOTE",
            message="origem_lote deve ter ao menos 3 caracteres",
            action="Informe origem operacional do lote (ex: upload_manual).",
        )

    if request.total_arquivos_lote <= 0 or request.total_arquivos_lote > MAX_BATCH_FILES:
        _raise_contract_error(
            code="INVALID_TOTAL_ARQUIVOS_LOTE",
            message=f"total_arquivos_lote deve estar entre 1 e {MAX_BATCH_FILES}",
            action="Ajuste quantidade de arquivos ou divida em mais lotes.",
        )

    if request.total_registros_estimados < 0:
        _raise_contract_error(
            code="INVALID_TOTAL_REGISTROS_ESTIMADOS",
            message="total_registros_estimados nao pode ser negativo",
            action="Informe quantidade estimada maior ou igual a zero.",
        )

    if not request.arquivos:
        _raise_contract_error(
            code="EMPTY_BATCH_FILES",
            message="arquivos nao pode ser vazio",
            action="Adicione ao menos um arquivo no lote antes de enviar.",
        )

    if len(request.arquivos) != request.total_arquivos_lote:
        _raise_contract_error(
            code="BATCH_FILE_COUNT_MISMATCH",
            message=(
                "total_arquivos_lote diverge da lista de arquivos: "
                f"esperado {request.total_arquivos_lote}, recebido {len(request.arquivos)}"
            ),
            action="Sincronize contagem de arquivos e metadados do lote.",
        )

    total_bytes_calculado = 0
    for index, arquivo in enumerate(request.arquivos):
        _validate_file_metadata(index=index, arquivo=arquivo)
        total_bytes_calculado += arquivo.tamanho_arquivo_bytes

    if request.total_bytes_lote <= 0:
        _raise_contract_error(
            code="INVALID_TOTAL_BYTES_LOTE",
            message="total_bytes_lote deve ser maior que zero",
            action="Informe tamanho total do lote em bytes.",
        )
    if request.total_bytes_lote > MAX_BATCH_BYTES:
        _raise_contract_error(
            code="BATCH_TOO_LARGE",
            message=f"Lote excede o limite de {MAX_BATCH_BYTES} bytes",
            action="Divida o lote em partes menores.",
        )
    if request.total_bytes_lote != total_bytes_calculado:
        _raise_contract_error(
            code="BATCH_TOTAL_BYTES_MISMATCH",
            message=(
                "total_bytes_lote diverge da soma dos arquivos: "
                f"esperado {total_bytes_calculado}, recebido {request.total_bytes_lote}"
            ),
            action="Recalcule total_bytes_lote para refletir os arquivos enviados.",
        )


def _validate_file_metadata(*, index: int, arquivo: S2FileMetadata) -> None:
    nome_arquivo = arquivo.nome_arquivo.strip()
    if not nome_arquivo:
        _raise_contract_error(
            code="EMPTY_FILE_NAME",
            message=f"nome_arquivo vazio no item {index}",
            action="Preencha nome_arquivo para todos os itens do lote.",
        )

    file_extension = Path(nome_arquivo).suffix.lower()
    if file_extension not in EXPECTED_CONTENT_TYPE_BY_EXTENSION:
        _raise_contract_error(
            code="UNSUPPORTED_FILE_EXTENSION",
            message=f"Extensao nao suportada no item {index}: {file_extension or '<sem_extensao>'}",
            action="Use arquivos .pdf, .xlsx ou .csv no lote.",
        )

    if arquivo.tamanho_arquivo_bytes <= 0:
        _raise_contract_error(
            code="INVALID_FILE_SIZE",
            message=f"tamanho_arquivo_bytes invalido no item {index}",
            action="Garanta tamanho maior que zero para cada arquivo.",
        )
    if arquivo.tamanho_arquivo_bytes > MAX_UPLOAD_BYTES:
        _raise_contract_error(
            code="FILE_TOO_LARGE",
            message=(
                f"Arquivo no item {index} excede limite de {MAX_UPLOAD_BYTES} bytes "
                f"({arquivo.tamanho_arquivo_bytes})"
            ),
            action="Divida ou compacte o arquivo para respeitar limite por item.",
        )

    content_type = arquivo.content_type.strip().lower()
    if content_type not in ACCEPTED_CONTENT_TYPES:
        _raise_contract_error(
            code="UNSUPPORTED_CONTENT_TYPE",
            message=f"content_type nao suportado no item {index}: {arquivo.content_type}",
            action="Ajuste content_type para .pdf, .xlsx ou .csv.",
        )

    expected_content_type = EXPECTED_CONTENT_TYPE_BY_EXTENSION[file_extension]
    if content_type != expected_content_type:
        _raise_contract_error(
            code="FILE_EXTENSION_CONTENT_TYPE_MISMATCH",
            message=(
                f"Item {index}: arquivo {file_extension} deve usar content_type "
                f"{expected_content_type}, recebido {arquivo.content_type}"
            ),
            action="Corrija metadados para manter consistencia extensao/content_type.",
        )


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "ingestao_inteligente_s2_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S2ScaffoldContractError(code=code, message=message, action=action)
