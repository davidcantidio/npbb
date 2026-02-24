"""Main flow for Sprint 2 batch reception of smart ingestion interface.

This module orchestrates the Sprint 2 core path:
1) validate and resolve the Sprint 2 scaffold contract;
2) prepare batch upload payload;
3) call backend batch upload intake integration;
4) return a stable output contract with actionable diagnostics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s2_scaffold import (
    BACKEND_S2_SCAFFOLD_ENDPOINT,
    S2FileMetadata,
    S2ScaffoldContractError,
    S2ScaffoldRequest,
    build_s2_scaffold_contract,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s2")

CONTRACT_VERSION = "s2.v1"
BACKEND_S2_LOTE_UPLOAD_ENDPOINT = "/internal/ingestao-inteligente/s2/lote/upload"


class S2CoreFlowError(RuntimeError):
    """Raised when Sprint 2 core flow fails at validation or integration."""

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
        """Return serializable payload for diagnostics in UI and tools."""

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
class S2CoreInput:
    """Input contract consumed by Sprint 2 core flow."""

    evento_id: int
    lote_id: str
    lote_nome: str
    origem_lote: str
    total_registros_estimados: int
    arquivos: tuple[S2FileMetadata, ...]
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S2ScaffoldRequest:
        """Build scaffold request with derived totals from file metadata."""

        return S2ScaffoldRequest(
            evento_id=self.evento_id,
            lote_id=self.lote_id,
            lote_nome=self.lote_nome,
            origem_lote=self.origem_lote,
            total_arquivos_lote=len(self.arquivos),
            total_bytes_lote=sum(item.tamanho_arquivo_bytes for item in self.arquivos),
            total_registros_estimados=self.total_registros_estimados,
            arquivos=self.arquivos,
            correlation_id=correlation_id,
        )

    def to_lote_upload_payload(self, *, correlation_id: str) -> dict[str, Any]:
        """Build backend payload for Sprint 2 batch upload intake endpoint."""

        scaffold_request = self.to_scaffold_request(correlation_id=correlation_id)
        return scaffold_request.to_backend_payload()


@dataclass(frozen=True, slots=True)
class S2CoreOutput:
    """Output contract returned when Sprint 2 core flow succeeds."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]
    lote_upload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for serialization and integration testing."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "proxima_acao": self.proxima_acao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
            "lote_upload": self.lote_upload,
        }


def execute_s2_main_flow(
    flow_input: S2CoreInput,
    *,
    send_backend: Callable[[str, dict[str, Any]], dict[str, Any]],
) -> S2CoreOutput:
    """Execute Sprint 2 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with batch metadata and file list.
        send_backend: Callback used to call backend endpoints. It receives
            `(endpoint, payload)` and returns parsed JSON dictionary.

    Returns:
        S2CoreOutput: Flow contract containing scaffold and batch upload responses.

    Raises:
        S2CoreFlowError: When scaffold validation fails or backend integration
            returns an invalid/unexpected payload.
    """

    correlation_id = flow_input.correlation_id or f"s2-{uuid4().hex[:12]}"
    flow_started_event_id = _new_event_id()
    logger.info(
        "ingestao_inteligente_s2_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": flow_started_event_id,
            "evento_id": flow_input.evento_id,
            "lote_id": flow_input.lote_id,
            "total_arquivos_lote": len(flow_input.arquivos),
        },
    )

    try:
        scaffold = build_s2_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        lote_upload_payload = flow_input.to_lote_upload_payload(correlation_id=correlation_id)

        dispatch_event_id = _new_event_id()
        logger.info(
            "ingestao_inteligente_s2_main_flow_upload_dispatch",
            extra={
                "correlation_id": correlation_id,
                "event_id": dispatch_event_id,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
                "upload_endpoint": BACKEND_S2_LOTE_UPLOAD_ENDPOINT,
            },
        )

        lote_upload_response = send_backend(BACKEND_S2_LOTE_UPLOAD_ENDPOINT, lote_upload_payload)
        _validate_lote_upload_response(
            lote_upload_response,
            correlation_id=correlation_id,
            expected_evento_id=flow_input.evento_id,
            expected_lote_id=flow_input.lote_id.strip(),
        )
        lote_upload_id = str(lote_upload_response["lote_upload_id"])

        completed_event_id = _new_event_id()
        logger.info(
            "ingestao_inteligente_s2_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id.strip(),
                "lote_upload_id": lote_upload_id,
                "status": str(lote_upload_response.get("status", "")),
            },
        )

        return S2CoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="accepted",
            evento_id=flow_input.evento_id,
            lote_id=flow_input.lote_id.strip(),
            lote_upload_id=lote_upload_id,
            proxima_acao=str(lote_upload_response["proxima_acao"]),
            pontos_integracao={
                "s2_scaffold_endpoint": BACKEND_S2_SCAFFOLD_ENDPOINT,
                "s2_lote_upload_endpoint": BACKEND_S2_LOTE_UPLOAD_ENDPOINT,
            },
            observabilidade={
                "flow_started_event_id": flow_started_event_id,
                "upload_dispatch_event_id": dispatch_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
            lote_upload=lote_upload_response,
        )
    except S2ScaffoldContractError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "ingestao_inteligente_s2_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
            },
        )
        raise S2CoreFlowError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S2CoreFlowError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "ingestao_inteligente_s2_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
            },
        )
        raise S2CoreFlowError(
            code="S2_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal da sprint 2: {type(exc).__name__}",
            action="Validar disponibilidade do endpoint de recepcao de lote e revisar logs operacionais.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _validate_lote_upload_response(
    response: dict[str, Any],
    *,
    correlation_id: str,
    expected_evento_id: int,
    expected_lote_id: str,
) -> None:
    if not isinstance(response, dict):
        raise S2CoreFlowError(
            code="INVALID_S2_LOTE_UPLOAD_RESPONSE",
            message="Resposta de recepcao de lote invalida: formato nao suportado",
            action="Garantir retorno JSON com os campos obrigatorios do contrato s2.v1.",
            correlation_id=correlation_id,
            stage="response_validation",
        )

    required_fields = ("status", "lote_upload_id", "evento_id", "lote_id", "proxima_acao")
    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise S2CoreFlowError(
            code="INCOMPLETE_S2_LOTE_UPLOAD_RESPONSE",
            message=f"Resposta de lote incompleta: faltam campos {missing_fields}",
            action="Atualizar endpoint de lote para respeitar o contrato s2.v1.",
            correlation_id=correlation_id,
            stage="response_validation",
        )

    if str(response["status"]).lower() not in {"accepted", "processing", "queued"}:
        raise S2CoreFlowError(
            code="INVALID_S2_LOTE_UPLOAD_STATUS",
            message=f"Status de lote inesperado: {response['status']}",
            action="Usar status aceitos pelo contrato: accepted, processing ou queued.",
            correlation_id=correlation_id,
            stage="response_validation",
        )

    if int(response["evento_id"]) != expected_evento_id:
        raise S2CoreFlowError(
            code="S2_EVENTO_ID_MISMATCH",
            message=(
                f"evento_id divergente na resposta de lote: esperado {expected_evento_id}, "
                f"recebido {response['evento_id']}"
            ),
            action="Alinhar payload de resposta com o evento selecionado no fluxo.",
            correlation_id=correlation_id,
            stage="response_validation",
        )

    if str(response["lote_id"]).strip() != expected_lote_id:
        raise S2CoreFlowError(
            code="S2_LOTE_ID_MISMATCH",
            message=(
                f"lote_id divergente na resposta de lote: esperado {expected_lote_id}, "
                f"recebido {response['lote_id']}"
            ),
            action="Alinhar lote_id de resposta com o lote processado pelo backend.",
            correlation_id=correlation_id,
            stage="response_validation",
        )


def _new_event_id() -> str:
    return f"s2evt-{uuid4().hex[:12]}"
