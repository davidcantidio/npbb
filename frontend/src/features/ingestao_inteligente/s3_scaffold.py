"""Base scaffold contract for Sprint 3 status monitoring and reprocessing.

Sprint 3 introduces monitoring and reprocessing contracts after Sprint 2 lote
reception. The goal is to keep one stable and traceable interface between
frontend and backend for status polling and reprocess decisions.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_scaffold import S2_BATCH_ID_RE


logger = logging.getLogger("npbb.ingestao_inteligente.s3")

CONTRACT_VERSION = "s3.v1"
BACKEND_S3_SCAFFOLD_ENDPOINT = "/internal/ingestao-inteligente/s3/scaffold"
MAX_REPROCESS_ATTEMPTS = 5
DEFAULT_STATUS_POLL_INTERVAL_SECONDS = 30

S3_ALLOWED_PROCESSING_STATUSES = (
    "queued",
    "processing",
    "completed",
    "failed",
    "partial_success",
    "cancelled",
)
S3_REPROCESSABLE_STATUSES = {"failed", "partial_success"}
S3_TERMINAL_STATUSES = {"completed", "failed", "partial_success", "cancelled"}
S3_LOTE_UPLOAD_ID_RE = re.compile(r"^lot-[a-z0-9]{6,64}$")


class S3ScaffoldContractError(ValueError):
    """Raised when Sprint 3 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3ScaffoldRequest:
    """Input contract for Sprint 3 scaffold validation."""

    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    tentativas_reprocessamento: int = 0
    reprocessamento_habilitado: bool = True
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible Sprint 3 contract."""

        return {
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "status_processamento": self.status_processamento,
            "tentativas_reprocessamento": self.tentativas_reprocessamento,
            "reprocessamento_habilitado": self.reprocessamento_habilitado,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3ScaffoldResponse:
    """Output contract returned when Sprint 3 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    limites_reprocessamento: dict[str, Any]
    monitoramento_status: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "status_processamento": self.status_processamento,
            "proxima_acao": self.proxima_acao,
            "limites_reprocessamento": self.limites_reprocessamento,
            "monitoramento_status": self.monitoramento_status,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s3_scaffold_contract(request: S3ScaffoldRequest) -> S3ScaffoldResponse:
    """Build Sprint 3 scaffold contract for monitoring and reprocessing flow.

    Args:
        request: Monitoring metadata payload from Sprint 3 interface.

    Returns:
        S3ScaffoldResponse: Stable scaffold output with monitoring and
            reprocessing integrations.

    Raises:
        S3ScaffoldContractError: If one or more Sprint 3 input rules fail.
    """

    correlation_id = request.correlation_id or f"s3-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s3_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "lote_id": request.lote_id,
            "lote_upload_id": request.lote_upload_id,
            "status_processamento": request.status_processamento,
            "tentativas_reprocessamento": request.tentativas_reprocessamento,
        },
    )

    normalized_status = _validate_s3_contract_input(request=request)
    proxima_acao = _resolve_next_action(
        status_processamento=normalized_status,
        tentativas_reprocessamento=request.tentativas_reprocessamento,
        reprocessamento_habilitado=request.reprocessamento_habilitado,
    )
    response = S3ScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        evento_id=request.evento_id,
        lote_id=request.lote_id.strip(),
        lote_upload_id=request.lote_upload_id.strip().lower(),
        status_processamento=normalized_status,
        proxima_acao=proxima_acao,
        limites_reprocessamento={
            "max_tentativas_reprocessamento": MAX_REPROCESS_ATTEMPTS,
            "status_reprocessaveis": sorted(S3_REPROCESSABLE_STATUSES),
        },
        monitoramento_status={
            "status_terminal": sorted(S3_TERMINAL_STATUSES),
            "polling_interval_seconds": DEFAULT_STATUS_POLL_INTERVAL_SECONDS,
            "tentativas_reprocessamento": request.tentativas_reprocessamento,
            "reprocessamento_habilitado": request.reprocessamento_habilitado,
        },
        pontos_integracao={
            "s3_scaffold_endpoint": BACKEND_S3_SCAFFOLD_ENDPOINT,
            "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
            "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
            "s2_lote_upload_endpoint": "/internal/ingestao-inteligente/s2/lote/upload",
        },
    )
    logger.info(
        "ingestao_inteligente_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "lote_id": request.lote_id.strip(),
            "lote_upload_id": request.lote_upload_id.strip().lower(),
            "status_processamento": normalized_status,
            "proxima_acao": proxima_acao,
        },
    )
    return response


def _validate_s3_contract_input(*, request: S3ScaffoldRequest) -> str:
    if request.evento_id <= 0:
        _raise_contract_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de monitorar o lote.",
        )

    lote_id = request.lote_id.strip()
    if not S2_BATCH_ID_RE.match(lote_id):
        _raise_contract_error(
            code="INVALID_LOTE_ID",
            message="lote_id invalido: use 3-80 chars [a-zA-Z0-9._-]",
            action="Defina um identificador de lote estavel para rastreabilidade.",
        )

    lote_upload_id = request.lote_upload_id.strip().lower()
    if not S3_LOTE_UPLOAD_ID_RE.match(lote_upload_id):
        _raise_contract_error(
            code="INVALID_LOTE_UPLOAD_ID",
            message="lote_upload_id invalido: use prefixo lot- com sufixo alfanumerico",
            action="Use o identificador retornado pelo endpoint /s2/lote/upload.",
        )

    status_processamento = request.status_processamento.strip().lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        _raise_contract_error(
            code="INVALID_STATUS_PROCESSAMENTO",
            message=f"status_processamento invalido: {request.status_processamento}",
            action=(
                "Use status aceitos: "
                + ", ".join(S3_ALLOWED_PROCESSING_STATUSES)
                + "."
            ),
        )

    if request.tentativas_reprocessamento < 0:
        _raise_contract_error(
            code="INVALID_REPROCESS_ATTEMPTS",
            message="tentativas_reprocessamento nao pode ser negativo",
            action="Informe quantidade de tentativas maior ou igual a zero.",
        )
    if request.tentativas_reprocessamento > MAX_REPROCESS_ATTEMPTS:
        _raise_contract_error(
            code="REPROCESS_ATTEMPTS_EXCEEDED",
            message=(
                f"tentativas_reprocessamento excede limite de {MAX_REPROCESS_ATTEMPTS}: "
                f"{request.tentativas_reprocessamento}"
            ),
            action="Encaminhe para analise manual ou ajuste limite operacional do fluxo.",
        )

    return status_processamento


def _resolve_next_action(
    *,
    status_processamento: str,
    tentativas_reprocessamento: int,
    reprocessamento_habilitado: bool,
) -> str:
    if (
        status_processamento in S3_REPROCESSABLE_STATUSES
        and reprocessamento_habilitado
        and tentativas_reprocessamento < MAX_REPROCESS_ATTEMPTS
    ):
        return "avaliar_reprocessamento_lote"
    if status_processamento in S3_TERMINAL_STATUSES:
        return "consultar_resultado_final_lote"
    return "monitorar_status_lote"


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "ingestao_inteligente_s3_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S3ScaffoldContractError(code=code, message=message, action=action)
