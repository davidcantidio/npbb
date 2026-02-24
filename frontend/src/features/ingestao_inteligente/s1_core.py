"""Main flow for Sprint 1 (upload + event selection) of smart ingestion.

This module orchestrates the core path:
1) validate input and resolve scaffold contract;
2) prepare upload payload;
3) call backend upload integration;
4) return a stable, diagnosable output contract.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s1_observability import (
    S1ObservabilityInput,
    build_s1_actionable_error,
    build_s1_observability_event,
    log_s1_observability_event,
)
from .s1_scaffold import (
    BACKEND_SCAFFOLD_ENDPOINT,
    S1ScaffoldContractError,
    S1ScaffoldRequest,
    build_s1_scaffold_contract,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s1")

CONTRACT_VERSION = "s1.v1"
BACKEND_UPLOAD_ENDPOINT = "/internal/ingestao-inteligente/s1/upload"


class S1CoreFlowError(RuntimeError):
    """Raised when Sprint 1 core flow fails at validation or integration."""

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
        """Return serializable payload for diagnostics in UI."""
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
class S1CoreInput:
    """Input contract consumed by Sprint 1 core flow."""

    evento_id: int
    nome_arquivo: str
    tamanho_arquivo_bytes: int
    content_type: str
    checksum_sha256: str | None = None
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S1ScaffoldRequest:
        """Build scaffold input payload using stable contract fields."""
        return S1ScaffoldRequest(
            evento_id=self.evento_id,
            nome_arquivo=self.nome_arquivo,
            tamanho_arquivo_bytes=self.tamanho_arquivo_bytes,
            content_type=self.content_type,
            correlation_id=correlation_id,
        )

    def to_upload_payload(self, *, correlation_id: str) -> dict[str, Any]:
        """Build upload payload for backend integration endpoint."""
        payload: dict[str, Any] = {
            "evento_id": self.evento_id,
            "nome_arquivo": self.nome_arquivo,
            "tamanho_arquivo_bytes": self.tamanho_arquivo_bytes,
            "content_type": self.content_type,
            "correlation_id": correlation_id,
        }
        if self.checksum_sha256:
            payload["checksum_sha256"] = self.checksum_sha256.strip().lower()
        return payload


@dataclass(frozen=True, slots=True)
class S1CoreOutput:
    """Output contract returned when Sprint 1 core flow succeeds."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    upload_id: str
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]
    upload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for serialization and integration testing."""
        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "evento_id": self.evento_id,
            "upload_id": self.upload_id,
            "proxima_acao": self.proxima_acao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
            "upload": self.upload,
        }


def execute_s1_main_flow(
    flow_input: S1CoreInput,
    *,
    send_backend: Callable[[str, dict[str, Any]], dict[str, Any]],
) -> S1CoreOutput:
    """Execute Sprint 1 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with selected event and upload metadata.
        send_backend: Callback used to call backend endpoints. It receives
            `(endpoint, payload)` and returns parsed JSON dictionary.

    Returns:
        S1CoreOutput: Flow contract containing scaffold and upload responses.

    Raises:
        S1CoreFlowError: When validation fails or backend integration returns
            an invalid/unexpected payload.
    """

    correlation_id = flow_input.correlation_id or f"s1-{uuid4().hex[:12]}"
    start_event = build_s1_observability_event(
        S1ObservabilityInput(
            event_name="ingestao_inteligente_s1_main_flow_started",
            correlation_id=correlation_id,
            event_message="Fluxo principal da Sprint 1 iniciado",
            severity="info",
            evento_id=flow_input.evento_id,
            context={
                "nome_arquivo": flow_input.nome_arquivo,
                "tamanho_arquivo_bytes": flow_input.tamanho_arquivo_bytes,
                "content_type": flow_input.content_type,
            },
        )
    )
    log_s1_observability_event(start_event)

    try:
        scaffold = build_s1_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        upload_payload = flow_input.to_upload_payload(correlation_id=correlation_id)
        dispatch_event = build_s1_observability_event(
            S1ObservabilityInput(
                event_name="ingestao_inteligente_s1_main_flow_upload_dispatch",
                correlation_id=correlation_id,
                event_message="Payload de upload enviado para o backend",
                severity="info",
                evento_id=flow_input.evento_id,
                context={"upload_endpoint": BACKEND_UPLOAD_ENDPOINT},
            )
        )
        log_s1_observability_event(dispatch_event)
        upload_response = send_backend(BACKEND_UPLOAD_ENDPOINT, upload_payload)
        _validate_upload_response(upload_response, correlation_id=correlation_id)
        upload_id = str(upload_response["upload_id"])
        completed_event = build_s1_observability_event(
            S1ObservabilityInput(
                event_name="ingestao_inteligente_s1_main_flow_completed",
                correlation_id=correlation_id,
                event_message="Fluxo principal da Sprint 1 concluido",
                severity="info",
                evento_id=flow_input.evento_id,
                upload_id=upload_id,
                context={"status": str(upload_response.get("status", ""))},
            )
        )
        log_s1_observability_event(completed_event)

        result = S1CoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="accepted",
            evento_id=flow_input.evento_id,
            upload_id=upload_id,
            proxima_acao=str(upload_response["proxima_acao"]),
            pontos_integracao={
                "scaffold_endpoint": BACKEND_SCAFFOLD_ENDPOINT,
                "upload_endpoint": BACKEND_UPLOAD_ENDPOINT,
            },
            observabilidade={
                "flow_start_event_id": start_event.observability_event_id,
                "upload_dispatch_event_id": dispatch_event.observability_event_id,
                "flow_completed_event_id": completed_event.observability_event_id,
            },
            scaffold=scaffold.to_dict(),
            upload=upload_response,
        )
        return result
    except S1ScaffoldContractError as exc:
        failed_event = build_s1_observability_event(
            S1ObservabilityInput(
                event_name="ingestao_inteligente_s1_main_flow_scaffold_error",
                correlation_id=correlation_id,
                event_message=exc.message,
                severity="warning",
                evento_id=flow_input.evento_id,
                context={"error_code": exc.code},
            )
        )
        log_s1_observability_event(failed_event)
        error_detail = build_s1_actionable_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
        )
        raise S1CoreFlowError(
            code=error_detail["code"],
            message=error_detail["message"],
            action=error_detail["action"],
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
        ) from exc
    except S1CoreFlowError:
        raise
    except Exception as exc:
        failed_event = build_s1_observability_event(
            S1ObservabilityInput(
                event_name="ingestao_inteligente_s1_main_flow_unexpected_error",
                correlation_id=correlation_id,
                event_message=f"Erro inesperado no fluxo principal: {type(exc).__name__}",
                severity="error",
                evento_id=flow_input.evento_id,
            )
        )
        log_s1_observability_event(failed_event)
        raise S1CoreFlowError(
            code="S1_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal da sprint: {type(exc).__name__}",
            action="Validar disponibilidade do endpoint de upload e revisar logs operacionais.",
            correlation_id=correlation_id,
            observability_event_id=failed_event.observability_event_id,
        ) from exc


def _validate_upload_response(response: dict[str, Any], *, correlation_id: str) -> None:
    if not isinstance(response, dict):
        raise S1CoreFlowError(
            code="INVALID_UPLOAD_RESPONSE",
            message="Resposta de upload invalida: formato nao suportado",
            action="Garantir retorno JSON com os campos obrigatorios do contrato s1.v1.",
            correlation_id=correlation_id,
        )

    required_fields = ("status", "upload_id", "evento_id", "proxima_acao")
    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise S1CoreFlowError(
            code="INCOMPLETE_UPLOAD_RESPONSE",
            message=f"Resposta de upload incompleta: faltam campos {missing_fields}",
            action="Atualizar endpoint de upload para respeitar o contrato s1.v1.",
            correlation_id=correlation_id,
        )

    if str(response["status"]).lower() not in {"accepted", "processing", "queued"}:
        raise S1CoreFlowError(
            code="INVALID_UPLOAD_STATUS",
            message=f"Status de upload inesperado: {response['status']}",
            action="Usar status aceitos pelo contrato: accepted, processing ou queued.",
            correlation_id=correlation_id,
        )
