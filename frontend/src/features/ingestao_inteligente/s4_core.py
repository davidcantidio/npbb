"""Main flow for Sprint 4 final UX and accessibility journey.

This module orchestrates the Sprint 4 core path:
1) validate and resolve the Sprint 4 scaffold contract;
2) call backend UX integration for actionable message rendering;
3) validate response contract for accessibility and traceability;
4) return a stable output contract with actionable diagnostics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s4_scaffold import (
    BACKEND_S4_SCAFFOLD_ENDPOINT,
    BACKEND_S4_UX_ENDPOINT,
    S3_ALLOWED_PROCESSING_STATUSES,
    S4_ALLOWED_NEXT_ACTIONS,
    S4ScaffoldContractError,
    S4ScaffoldRequest,
    build_s4_scaffold_contract,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s4")

CONTRACT_VERSION = "s4.v1"
S4_ALLOWED_UX_STATUSES = {"ready", "ok"}
S4_ALLOWED_MESSAGE_SEVERITIES = {"info", "warning", "success", "error"}
S4_ALLOWED_PRIORITY = {"high", "medium", "low"}


class S4CoreFlowError(RuntimeError):
    """Raised when Sprint 4 core flow fails at validation or integration."""

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
class S4CoreInput:
    """Input contract consumed by Sprint 4 core flow."""

    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    leitor_tela_ativo: bool = False
    alto_contraste_ativo: bool = False
    reduzir_movimento: bool = False
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S4ScaffoldRequest:
        """Build scaffold request for Sprint 4 with stable contract fields."""

        return S4ScaffoldRequest(
            evento_id=self.evento_id,
            lote_id=self.lote_id,
            lote_upload_id=self.lote_upload_id,
            status_processamento=self.status_processamento,
            proxima_acao=self.proxima_acao,
            leitor_tela_ativo=self.leitor_tela_ativo,
            alto_contraste_ativo=self.alto_contraste_ativo,
            reduzir_movimento=self.reduzir_movimento,
            correlation_id=correlation_id,
        )

    def to_ux_payload(self, *, correlation_id: str) -> dict[str, Any]:
        """Build UX payload for backend integration endpoint."""

        return self.to_scaffold_request(correlation_id=correlation_id).to_backend_payload()


@dataclass(frozen=True, slots=True)
class S4CoreOutput:
    """Output contract returned when Sprint 4 core flow succeeds."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    mensagem_acionavel: dict[str, Any]
    acessibilidade: dict[str, Any]
    experiencia_usuario: dict[str, Any]
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]
    ux: dict[str, Any]

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
            "mensagem_acionavel": self.mensagem_acionavel,
            "acessibilidade": self.acessibilidade,
            "experiencia_usuario": self.experiencia_usuario,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
            "ux": self.ux,
        }


def execute_s4_main_flow(
    flow_input: S4CoreInput,
    *,
    send_backend: Callable[[str, dict[str, Any]], dict[str, Any]],
) -> S4CoreOutput:
    """Execute Sprint 4 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with final UX and accessibility metadata.
        send_backend: Callback used to call backend endpoints. It receives
            `(endpoint, payload)` and returns parsed JSON dictionary.

    Returns:
        S4CoreOutput: Flow contract containing scaffold and final UX payload.

    Raises:
        S4CoreFlowError: When scaffold validation fails or backend integration
            returns an invalid/unexpected payload.
    """

    correlation_id = flow_input.correlation_id or f"s4-{uuid4().hex[:12]}"
    flow_started_event_id = _new_event_id()
    logger.info(
        "ingestao_inteligente_s4_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": flow_started_event_id,
            "evento_id": flow_input.evento_id,
            "lote_id": flow_input.lote_id,
            "lote_upload_id": flow_input.lote_upload_id,
            "status_processamento": flow_input.status_processamento,
            "proxima_acao": flow_input.proxima_acao,
        },
    )

    try:
        scaffold = build_s4_scaffold_contract(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )
        ux_dispatch_event_id = _new_event_id()
        ux_payload = flow_input.to_ux_payload(correlation_id=correlation_id)
        logger.info(
            "ingestao_inteligente_s4_main_flow_ux_dispatch",
            extra={
                "correlation_id": correlation_id,
                "event_id": ux_dispatch_event_id,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
                "lote_upload_id": flow_input.lote_upload_id,
                "ux_endpoint": BACKEND_S4_UX_ENDPOINT,
            },
        )
        ux_response = send_backend(BACKEND_S4_UX_ENDPOINT, ux_payload)
        _validate_s4_ux_response(
            ux_response,
            correlation_id=correlation_id,
            expected_evento_id=flow_input.evento_id,
            expected_lote_id=flow_input.lote_id.strip(),
            expected_lote_upload_id=flow_input.lote_upload_id.strip().lower(),
        )

        completed_event_id = _new_event_id()
        logger.info(
            "ingestao_inteligente_s4_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id.strip(),
                "lote_upload_id": flow_input.lote_upload_id.strip().lower(),
                "status_processamento": str(ux_response["status_processamento"]).lower(),
                "proxima_acao": str(ux_response["proxima_acao"]),
                "codigo_mensagem": str(ux_response["mensagem_acionavel"]["codigo_mensagem"]),
            },
        )

        pontos_integracao = ux_response.get("pontos_integracao", {})
        return S4CoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status=str(ux_response["status"]).lower(),
            evento_id=flow_input.evento_id,
            lote_id=flow_input.lote_id.strip(),
            lote_upload_id=flow_input.lote_upload_id.strip().lower(),
            status_processamento=str(ux_response["status_processamento"]).lower(),
            proxima_acao=str(ux_response["proxima_acao"]),
            mensagem_acionavel=dict(ux_response["mensagem_acionavel"]),
            acessibilidade=dict(ux_response["acessibilidade"]),
            experiencia_usuario=dict(ux_response["experiencia_usuario"]),
            pontos_integracao={
                "s4_scaffold_endpoint": str(
                    pontos_integracao.get("s4_scaffold_endpoint", BACKEND_S4_SCAFFOLD_ENDPOINT)
                ),
                "s4_ux_endpoint": str(
                    pontos_integracao.get("s4_ux_endpoint", BACKEND_S4_UX_ENDPOINT)
                ),
                "s3_status_endpoint": str(
                    pontos_integracao.get(
                        "s3_status_endpoint", "/internal/ingestao-inteligente/s3/status"
                    )
                ),
                "s3_reprocess_endpoint": str(
                    pontos_integracao.get(
                        "s3_reprocess_endpoint", "/internal/ingestao-inteligente/s3/reprocessar"
                    )
                ),
            },
            observabilidade={
                "flow_started_event_id": flow_started_event_id,
                "ux_dispatch_event_id": ux_dispatch_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
            ux=ux_response,
        )
    except S4ScaffoldContractError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "ingestao_inteligente_s4_main_flow_scaffold_error",
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
        raise S4CoreFlowError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4CoreFlowError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "ingestao_inteligente_s4_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
                "evento_id": flow_input.evento_id,
                "lote_id": flow_input.lote_id,
                "lote_upload_id": flow_input.lote_upload_id,
            },
        )
        raise S4CoreFlowError(
            code="S4_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal da sprint 4: {type(exc).__name__}",
            action="Validar disponibilidade do endpoint /s4/ux e revisar logs operacionais.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _validate_s4_ux_response(
    response: dict[str, Any],
    *,
    correlation_id: str,
    expected_evento_id: int,
    expected_lote_id: str,
    expected_lote_upload_id: str,
) -> None:
    if not isinstance(response, dict):
        raise S4CoreFlowError(
            code="INVALID_S4_UX_RESPONSE",
            message="Resposta de UX final invalida: formato nao suportado",
            action="Garantir retorno JSON com campos obrigatorios do contrato s4.v1.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    required_fields = (
        "status",
        "evento_id",
        "lote_id",
        "lote_upload_id",
        "status_processamento",
        "proxima_acao",
        "mensagem_acionavel",
        "acessibilidade",
        "experiencia_usuario",
    )
    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise S4CoreFlowError(
            code="INCOMPLETE_S4_UX_RESPONSE",
            message=f"Resposta de UX final incompleta: faltam campos {missing_fields}",
            action="Atualizar endpoint /s4/ux para respeitar o contrato s4.v1.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    status = str(response["status"]).lower()
    if status not in S4_ALLOWED_UX_STATUSES:
        raise S4CoreFlowError(
            code="INVALID_S4_UX_STATUS",
            message=f"status de UX final inesperado: {response['status']}",
            action="Use status aceitos: ready ou ok.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    status_processamento = str(response["status_processamento"]).lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        raise S4CoreFlowError(
            code="INVALID_S4_STATUS_PROCESSAMENTO_RESPONSE",
            message=f"status_processamento inesperado na resposta: {response['status_processamento']}",
            action="Retornar status_processamento compativel com contrato s4.v1.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    proxima_acao = str(response["proxima_acao"])
    if proxima_acao not in S4_ALLOWED_NEXT_ACTIONS:
        raise S4CoreFlowError(
            code="INVALID_S4_NEXT_ACTION_RESPONSE",
            message=f"proxima_acao inesperada na resposta: {response['proxima_acao']}",
            action="Retornar proxima_acao valida para o fluxo final da Sprint 4.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    if int(response["evento_id"]) != expected_evento_id:
        raise S4CoreFlowError(
            code="S4_EVENTO_ID_MISMATCH",
            message=(
                f"evento_id divergente na resposta de UX: esperado {expected_evento_id}, "
                f"recebido {response['evento_id']}"
            ),
            action="Alinhar payload de resposta com o evento selecionado no fluxo.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    if str(response["lote_id"]).strip() != expected_lote_id:
        raise S4CoreFlowError(
            code="S4_LOTE_ID_MISMATCH",
            message=(
                f"lote_id divergente na resposta de UX: esperado {expected_lote_id}, "
                f"recebido {response['lote_id']}"
            ),
            action="Alinhar lote_id de resposta com o lote exibido na UX final.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    if str(response["lote_upload_id"]).strip().lower() != expected_lote_upload_id:
        raise S4CoreFlowError(
            code="S4_LOTE_UPLOAD_ID_MISMATCH",
            message=(
                "lote_upload_id divergente na resposta de UX: "
                f"esperado {expected_lote_upload_id}, recebido {response['lote_upload_id']}"
            ),
            action="Alinhar lote_upload_id de resposta com o lote exibido na UX final.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    _validate_actionable_message(
        response["mensagem_acionavel"],
        correlation_id=correlation_id,
    )
    _validate_accessibility_hints(
        response["acessibilidade"],
        correlation_id=correlation_id,
    )
    _validate_ux_experience(
        response["experiencia_usuario"],
        correlation_id=correlation_id,
    )


def _validate_actionable_message(
    payload: dict[str, Any],
    *,
    correlation_id: str,
) -> None:
    if not isinstance(payload, dict):
        raise S4CoreFlowError(
            code="INVALID_S4_ACTIONABLE_MESSAGE",
            message="mensagem_acionavel invalida: formato nao suportado",
            action="Retornar mensagem_acionavel como objeto JSON com campos obrigatorios.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    required_fields = (
        "codigo_mensagem",
        "titulo",
        "mensagem",
        "acao_recomendada",
        "severidade",
    )
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        raise S4CoreFlowError(
            code="INCOMPLETE_S4_ACTIONABLE_MESSAGE",
            message=f"mensagem_acionavel incompleta: faltam campos {missing_fields}",
            action="Atualizar contrato de mensagem para incluir campos obrigatorios da Sprint 4.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    severidade = str(payload["severidade"]).lower()
    if severidade not in S4_ALLOWED_MESSAGE_SEVERITIES:
        raise S4CoreFlowError(
            code="INVALID_S4_MESSAGE_SEVERITY",
            message=f"severidade de mensagem invalida: {payload['severidade']}",
            action="Use severidades aceitas: info, warning, success ou error.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )


def _validate_accessibility_hints(
    payload: dict[str, Any],
    *,
    correlation_id: str,
) -> None:
    if not isinstance(payload, dict):
        raise S4CoreFlowError(
            code="INVALID_S4_ACCESSIBILITY_HINTS",
            message="acessibilidade invalida: formato nao suportado",
            action="Retornar bloco de acessibilidade como objeto JSON valido.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    required_fields = (
        "leitor_tela_ativo",
        "alto_contraste_ativo",
        "reduzir_movimento",
        "aria_live",
        "foco_inicial",
    )
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        raise S4CoreFlowError(
            code="INCOMPLETE_S4_ACCESSIBILITY_HINTS",
            message=f"acessibilidade incompleta: faltam campos {missing_fields}",
            action="Atualizar bloco de acessibilidade com todos os campos obrigatorios.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    aria_live = str(payload["aria_live"]).lower()
    if aria_live not in {"polite", "assertive"}:
        raise S4CoreFlowError(
            code="INVALID_S4_ARIA_LIVE",
            message=f"aria_live invalido na resposta de UX: {payload['aria_live']}",
            action="Use aria_live com valores polite ou assertive.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    foco_inicial = str(payload["foco_inicial"])
    if foco_inicial not in {"banner_mensagem_acionavel", "acao_recomendada"}:
        raise S4CoreFlowError(
            code="INVALID_S4_FOCUS_TARGET",
            message=f"foco_inicial invalido na resposta de UX: {payload['foco_inicial']}",
            action="Use foco_inicial em banner_mensagem_acionavel ou acao_recomendada.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )


def _validate_ux_experience(
    payload: dict[str, Any],
    *,
    correlation_id: str,
) -> None:
    if not isinstance(payload, dict):
        raise S4CoreFlowError(
            code="INVALID_S4_UX_EXPERIENCE",
            message="experiencia_usuario invalida: formato nao suportado",
            action="Retornar experiencia_usuario como objeto JSON com campos obrigatorios.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    required_fields = (
        "exibir_banner_acao",
        "destino_acao_principal",
        "prioridade_exibicao",
    )
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        raise S4CoreFlowError(
            code="INCOMPLETE_S4_UX_EXPERIENCE",
            message=f"experiencia_usuario incompleta: faltam campos {missing_fields}",
            action="Atualizar resposta de UX com campos obrigatorios da Sprint 4.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )

    prioridade = str(payload["prioridade_exibicao"]).lower()
    if prioridade not in S4_ALLOWED_PRIORITY:
        raise S4CoreFlowError(
            code="INVALID_S4_UX_PRIORITY",
            message=f"prioridade_exibicao invalida: {payload['prioridade_exibicao']}",
            action="Use prioridades aceitas: high, medium ou low.",
            correlation_id=correlation_id,
            stage="ux_response_validation",
        )


def _new_event_id() -> str:
    return f"s4evt-{uuid4().hex[:12]}"
