"""Main flow for Sprint 3 status monitoring and reprocessing journey.

This module orchestrates the Sprint 3 core path:
1) validate and resolve the Sprint 3 scaffold contract;
2) call backend status monitoring integration;
3) optionally trigger reprocessing when eligible;
4) return a stable output contract with actionable diagnostics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s3_scaffold import (
    BACKEND_S3_SCAFFOLD_ENDPOINT,
    S3_ALLOWED_PROCESSING_STATUSES,
    S3ScaffoldContractError,
    S3ScaffoldRequest,
    build_s3_scaffold_contract,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s3")

CONTRACT_VERSION = "s3.v1"
BACKEND_S3_STATUS_ENDPOINT = "/internal/ingestao-inteligente/s3/status"
BACKEND_S3_REPROCESS_ENDPOINT = "/internal/ingestao-inteligente/s3/reprocessar"
S3_ALLOWED_NEXT_ACTIONS = {
    "monitorar_status_lote",
    "avaliar_reprocessamento_lote",
    "consultar_resultado_final_lote",
}


class S3CoreFlowError(RuntimeError):
    """Raised when Sprint 3 core flow fails at validation or integration."""

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
class S3CoreInput:
    """Input contract consumed by Sprint 3 core flow."""

    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    tentativas_reprocessamento: int = 0
    reprocessamento_habilitado: bool = True
    motivo_reprocessamento: str | None = None
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S3ScaffoldRequest:
        """Build scaffold request for Sprint 3 with stable contract fields."""

        return S3ScaffoldRequest(
            evento_id=self.evento_id,
            lote_id=self.lote_id,
            lote_upload_id=self.lote_upload_id,
            status_processamento=self.status_processamento,
            tentativas_reprocessamento=self.tentativas_reprocessamento,
            reprocessamento_habilitado=self.reprocessamento_habilitado,
            correlation_id=correlation_id,
        )

    def to_status_payload(self, *, correlation_id: str) -> dict[str, Any]:
        """Build status monitoring payload for backend integration endpoint."""

        return self.to_scaffold_request(correlation_id=correlation_id).to_backend_payload()

    def to_reprocess_payload(self, *, correlation_id: str) -> dict[str, Any]:
        """Build reprocessing payload for backend integration endpoint."""

        payload = self.to_scaffold_request(correlation_id=correlation_id).to_backend_payload()
        payload["motivo_reprocessamento"] = (
            self.motivo_reprocessamento or "reprocessamento_manual_sprint3"
        )
        return payload


@dataclass(frozen=True, slots=True)
class S3CoreOutput:
    """Output contract returned when Sprint 3 core flow succeeds."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]
    status_monitoramento: dict[str, Any]
    reprocessamento: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for serialization and integration testing."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "status_processamento": self.status_processamento,
            "proxima_acao": self.proxima_acao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
            "status_monitoramento": self.status_monitoramento,
            "reprocessamento": self.reprocessamento,
        }


def execute_s3_main_flow(
    flow_input: S3CoreInput,
    *,
    send_backend: Callable[[str, dict[str, Any]], dict[str, Any]],
) -> S3CoreOutput:
    """Execute Sprint 3 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with monitoring and reprocessing metadata.
        send_backend: Callback used to call backend endpoints. It receives
            `(endpoint, payload)` and returns parsed JSON dictionary.

    Returns:
        S3CoreOutput: Flow contract with scaffold, status, and reprocessing data.

    Raises:
        S3CoreFlowError: When scaffold validation fails or backend integration
            returns an invalid/unexpected payload.
    """

    correlation_id = flow_input.correlation_id or f"s3-{uuid4().hex[:12]}"
    flow_started_event_id = _new_event_id()
    logger.info(
        "ingestao_inteligente_s3_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": flow_started_event_id,
            "evento_id": flow_input.evento_id,
            "lote_id": flow_input.lote_id,
            "lote_upload_id": flow_input.lote_upload_id,
        },
    )

    try:
        scaffold = build_s3_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        status_dispatch_event_id = _new_event_id()
        status_payload = flow_input.to_status_payload(correlation_id=correlation_id)
        logger.info(
            "ingestao_inteligente_s3_main_flow_status_dispatch",
            extra={
                "correlation_id": correlation_id,
                "event_id": status_dispatch_event_id,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
                "lote_upload_id": flow_input.lote_upload_id,
                "status_endpoint": BACKEND_S3_STATUS_ENDPOINT,
            },
        )
        status_response = send_backend(BACKEND_S3_STATUS_ENDPOINT, status_payload)
        _validate_status_response(
            status_response,
            correlation_id=correlation_id,
            expected_evento_id=flow_input.evento_id,
            expected_lote_id=flow_input.lote_id.strip(),
            expected_lote_upload_id=flow_input.lote_upload_id.strip().lower(),
        )

        reprocess_response: dict[str, Any] | None = None
        observabilidade: dict[str, str] = {
            "flow_started_event_id": flow_started_event_id,
            "status_dispatch_event_id": status_dispatch_event_id,
        }
        proxima_acao = str(status_response["proxima_acao"])
        status_fluxo = str(status_response["status"]).lower()
        status_processamento_saida = str(status_response["status_processamento"]).lower()

        if proxima_acao == "avaliar_reprocessamento_lote":
            reprocess_dispatch_event_id = _new_event_id()
            logger.info(
                "ingestao_inteligente_s3_main_flow_reprocess_dispatch",
                extra={
                    "correlation_id": correlation_id,
                    "event_id": reprocess_dispatch_event_id,
                    "evento_id": flow_input.evento_id,
                    "lote_id": flow_input.lote_id,
                    "lote_upload_id": flow_input.lote_upload_id,
                    "reprocess_endpoint": BACKEND_S3_REPROCESS_ENDPOINT,
                },
            )
            reprocess_response = send_backend(
                BACKEND_S3_REPROCESS_ENDPOINT,
                flow_input.to_reprocess_payload(correlation_id=correlation_id),
            )
            _validate_reprocess_response(
                reprocess_response,
                correlation_id=correlation_id,
                expected_evento_id=flow_input.evento_id,
                expected_lote_id=flow_input.lote_id.strip(),
                expected_lote_upload_id=flow_input.lote_upload_id.strip().lower(),
            )
            observabilidade["reprocess_dispatch_event_id"] = reprocess_dispatch_event_id
            proxima_acao = str(reprocess_response["proxima_acao"])
            status_fluxo = str(reprocess_response["status"]).lower()
            status_processamento_saida = str(reprocess_response["status_reprocessamento"]).lower()

        completed_event_id = _new_event_id()
        logger.info(
            "ingestao_inteligente_s3_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id.strip(),
                "lote_upload_id": flow_input.lote_upload_id.strip().lower(),
                "status_processamento": status_processamento_saida,
                "proxima_acao": proxima_acao,
                "reprocess_triggered": reprocess_response is not None,
            },
        )
        observabilidade["flow_completed_event_id"] = completed_event_id

        return S3CoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status=status_fluxo,
            evento_id=flow_input.evento_id,
            lote_id=flow_input.lote_id.strip(),
            lote_upload_id=flow_input.lote_upload_id.strip().lower(),
            status_processamento=status_processamento_saida,
            proxima_acao=proxima_acao,
            pontos_integracao={
                "s3_scaffold_endpoint": BACKEND_S3_SCAFFOLD_ENDPOINT,
                "s3_status_endpoint": BACKEND_S3_STATUS_ENDPOINT,
                "s3_reprocess_endpoint": BACKEND_S3_REPROCESS_ENDPOINT,
            },
            observabilidade=observabilidade,
            scaffold=scaffold.to_dict(),
            status_monitoramento=status_response,
            reprocessamento=reprocess_response,
        )
    except S3ScaffoldContractError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "ingestao_inteligente_s3_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
                "lote_upload_id": flow_input.lote_upload_id,
            },
        )
        raise S3CoreFlowError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S3CoreFlowError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "ingestao_inteligente_s3_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
                "lote_upload_id": flow_input.lote_upload_id,
            },
        )
        raise S3CoreFlowError(
            code="S3_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal da sprint 3: {type(exc).__name__}",
            action=(
                "Validar disponibilidade dos endpoints de status/reprocessamento "
                "e revisar logs operacionais."
            ),
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _validate_status_response(
    response: dict[str, Any],
    *,
    correlation_id: str,
    expected_evento_id: int,
    expected_lote_id: str,
    expected_lote_upload_id: str,
) -> None:
    if not isinstance(response, dict):
        raise S3CoreFlowError(
            code="INVALID_S3_STATUS_RESPONSE",
            message="Resposta de monitoramento invalida: formato nao suportado",
            action="Garantir retorno JSON com campos obrigatorios do contrato s3.v1.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )

    required_fields = (
        "status",
        "evento_id",
        "lote_id",
        "lote_upload_id",
        "status_processamento",
        "proxima_acao",
    )
    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise S3CoreFlowError(
            code="INCOMPLETE_S3_STATUS_RESPONSE",
            message=f"Resposta de status incompleta: faltam campos {missing_fields}",
            action="Atualizar endpoint /s3/status para respeitar o contrato s3.v1.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )

    status_processamento = str(response["status_processamento"]).lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        raise S3CoreFlowError(
            code="INVALID_S3_STATUS_PROCESSAMENTO_RESPONSE",
            message=f"status_processamento inesperado na resposta: {response['status_processamento']}",
            action="Retornar status_processamento compativel com contrato da sprint 3.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )

    proxima_acao = str(response["proxima_acao"])
    if proxima_acao not in S3_ALLOWED_NEXT_ACTIONS:
        raise S3CoreFlowError(
            code="INVALID_S3_NEXT_ACTION_RESPONSE",
            message=f"proxima_acao inesperada na resposta: {response['proxima_acao']}",
            action="Retornar proxima_acao valida para monitoramento/reprocessamento.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )

    if int(response["evento_id"]) != expected_evento_id:
        raise S3CoreFlowError(
            code="S3_EVENTO_ID_MISMATCH",
            message=(
                f"evento_id divergente na resposta de status: esperado {expected_evento_id}, "
                f"recebido {response['evento_id']}"
            ),
            action="Alinhar payload de resposta com o evento selecionado no fluxo.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )

    if str(response["lote_id"]).strip() != expected_lote_id:
        raise S3CoreFlowError(
            code="S3_LOTE_ID_MISMATCH",
            message=(
                f"lote_id divergente na resposta de status: esperado {expected_lote_id}, "
                f"recebido {response['lote_id']}"
            ),
            action="Alinhar lote_id de resposta com o lote monitorado.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )

    if str(response["lote_upload_id"]).strip().lower() != expected_lote_upload_id:
        raise S3CoreFlowError(
            code="S3_LOTE_UPLOAD_ID_MISMATCH",
            message=(
                "lote_upload_id divergente na resposta de status: "
                f"esperado {expected_lote_upload_id}, recebido {response['lote_upload_id']}"
            ),
            action="Alinhar lote_upload_id de resposta com o lote monitorado.",
            correlation_id=correlation_id,
            stage="status_response_validation",
        )


def _validate_reprocess_response(
    response: dict[str, Any],
    *,
    correlation_id: str,
    expected_evento_id: int,
    expected_lote_id: str,
    expected_lote_upload_id: str,
) -> None:
    if not isinstance(response, dict):
        raise S3CoreFlowError(
            code="INVALID_S3_REPROCESS_RESPONSE",
            message="Resposta de reprocessamento invalida: formato nao suportado",
            action="Garantir retorno JSON com campos obrigatorios do contrato s3.v1.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    required_fields = (
        "status",
        "reprocessamento_id",
        "evento_id",
        "lote_id",
        "lote_upload_id",
        "status_anterior",
        "status_reprocessamento",
        "tentativas_reprocessamento",
        "proxima_acao",
    )
    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise S3CoreFlowError(
            code="INCOMPLETE_S3_REPROCESS_RESPONSE",
            message=f"Resposta de reprocessamento incompleta: faltam campos {missing_fields}",
            action="Atualizar endpoint /s3/reprocessar para respeitar o contrato s3.v1.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    if str(response["status"]).lower() not in {"accepted", "queued", "processing"}:
        raise S3CoreFlowError(
            code="INVALID_S3_REPROCESS_STATUS",
            message=f"status de reprocessamento inesperado: {response['status']}",
            action="Usar status aceitos: accepted, queued ou processing.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    status_anterior = str(response["status_anterior"]).lower()
    if status_anterior not in S3_ALLOWED_PROCESSING_STATUSES:
        raise S3CoreFlowError(
            code="INVALID_S3_REPROCESS_STATUS_ANTERIOR",
            message=f"status_anterior inesperado: {response['status_anterior']}",
            action="Retornar status_anterior compativel com contrato da sprint 3.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    status_reprocessamento = str(response["status_reprocessamento"]).lower()
    if status_reprocessamento not in {"queued", "processing"}:
        raise S3CoreFlowError(
            code="INVALID_S3_STATUS_REPROCESSAMENTO",
            message=f"status_reprocessamento inesperado: {response['status_reprocessamento']}",
            action="Retornar status_reprocessamento como queued ou processing.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    if int(response["evento_id"]) != expected_evento_id:
        raise S3CoreFlowError(
            code="S3_EVENTO_ID_MISMATCH",
            message=(
                f"evento_id divergente na resposta de reprocessamento: "
                f"esperado {expected_evento_id}, recebido {response['evento_id']}"
            ),
            action="Alinhar payload de resposta com o evento selecionado no fluxo.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    if str(response["lote_id"]).strip() != expected_lote_id:
        raise S3CoreFlowError(
            code="S3_LOTE_ID_MISMATCH",
            message=(
                f"lote_id divergente na resposta de reprocessamento: esperado {expected_lote_id}, "
                f"recebido {response['lote_id']}"
            ),
            action="Alinhar lote_id de resposta com o lote processado.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    if str(response["lote_upload_id"]).strip().lower() != expected_lote_upload_id:
        raise S3CoreFlowError(
            code="S3_LOTE_UPLOAD_ID_MISMATCH",
            message=(
                "lote_upload_id divergente na resposta de reprocessamento: "
                f"esperado {expected_lote_upload_id}, recebido {response['lote_upload_id']}"
            ),
            action="Alinhar lote_upload_id de resposta com o lote processado.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    if int(response["tentativas_reprocessamento"]) <= 0:
        raise S3CoreFlowError(
            code="INVALID_S3_REPROCESS_ATTEMPTS_RESPONSE",
            message="tentativas_reprocessamento invalido na resposta de reprocessamento",
            action="Retornar contador de tentativas maior que zero apos reprocessar.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )

    if str(response["proxima_acao"]) != "monitorar_status_lote":
        raise S3CoreFlowError(
            code="INVALID_S3_REPROCESS_NEXT_ACTION",
            message=f"proxima_acao inesperada apos reprocessamento: {response['proxima_acao']}",
            action="Retornar proxima_acao como monitorar_status_lote apos reprocessar.",
            correlation_id=correlation_id,
            stage="reprocess_response_validation",
        )


def _new_event_id() -> str:
    return f"s3evt-{uuid4().hex[:12]}"
