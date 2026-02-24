"""Base scaffold contract for Sprint 4 final UX and accessibility journey.

Sprint 4 consolidates user-facing feedback from Sprint 3 status monitoring and
reprocessing. The goal is to keep one stable contract for actionable messages
and accessibility hints before full UI integration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_scaffold import S2_BATCH_ID_RE
from .s3_scaffold import (
    S3_ALLOWED_PROCESSING_STATUSES,
    S3_LOTE_UPLOAD_ID_RE,
    S3_REPROCESSABLE_STATUSES,
    S3_TERMINAL_STATUSES,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s4")

CONTRACT_VERSION = "s4.v1"
BACKEND_S4_SCAFFOLD_ENDPOINT = "/internal/ingestao-inteligente/s4/scaffold"
BACKEND_S4_UX_ENDPOINT = "/internal/ingestao-inteligente/s4/ux"
S4_ALLOWED_NEXT_ACTIONS = (
    "monitorar_status_lote",
    "avaliar_reprocessamento_lote",
    "consultar_resultado_final_lote",
)


class S4ScaffoldContractError(ValueError):
    """Raised when Sprint 4 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4ScaffoldRequest:
    """Input contract for Sprint 4 scaffold validation."""

    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    leitor_tela_ativo: bool = False
    alto_contraste_ativo: bool = False
    reduzir_movimento: bool = False
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible Sprint 4 contract."""

        return {
            "evento_id": self.evento_id,
            "lote_id": self.lote_id,
            "lote_upload_id": self.lote_upload_id,
            "status_processamento": self.status_processamento,
            "proxima_acao": self.proxima_acao,
            "leitor_tela_ativo": self.leitor_tela_ativo,
            "alto_contraste_ativo": self.alto_contraste_ativo,
            "reduzir_movimento": self.reduzir_movimento,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4ScaffoldResponse:
    """Output contract returned when Sprint 4 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    mensagem_acionavel: dict[str, str]
    acessibilidade: dict[str, Any]
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
            "mensagem_acionavel": self.mensagem_acionavel,
            "acessibilidade": self.acessibilidade,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s4_scaffold_contract(request: S4ScaffoldRequest) -> S4ScaffoldResponse:
    """Build Sprint 4 scaffold contract for final UX and accessibility hints.

    Args:
        request: UX input payload with monitoring state and accessibility flags.

    Returns:
        S4ScaffoldResponse: Stable scaffold output with actionable UX content.

    Raises:
        S4ScaffoldContractError: If one or more Sprint 4 input rules fail.
    """

    correlation_id = request.correlation_id or f"s4-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s4_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "lote_id": request.lote_id,
            "lote_upload_id": request.lote_upload_id,
            "status_processamento": request.status_processamento,
            "proxima_acao": request.proxima_acao,
            "leitor_tela_ativo": request.leitor_tela_ativo,
            "alto_contraste_ativo": request.alto_contraste_ativo,
            "reduzir_movimento": request.reduzir_movimento,
        },
    )

    status_processamento, proxima_acao = _validate_s4_contract_input(request=request)
    mensagem_acionavel = _build_s4_actionable_message(
        status_processamento=status_processamento,
        proxima_acao=proxima_acao,
    )
    acessibilidade = _build_s4_accessibility_hints(
        leitor_tela_ativo=request.leitor_tela_ativo,
        alto_contraste_ativo=request.alto_contraste_ativo,
        reduzir_movimento=request.reduzir_movimento,
        severidade_mensagem=mensagem_acionavel["severidade"],
    )
    response = S4ScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        evento_id=request.evento_id,
        lote_id=request.lote_id.strip(),
        lote_upload_id=request.lote_upload_id.strip().lower(),
        status_processamento=status_processamento,
        proxima_acao=proxima_acao,
        mensagem_acionavel=mensagem_acionavel,
        acessibilidade=acessibilidade,
        pontos_integracao={
            "s4_scaffold_endpoint": BACKEND_S4_SCAFFOLD_ENDPOINT,
            "s4_ux_endpoint": BACKEND_S4_UX_ENDPOINT,
            "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
            "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
            "s3_scaffold_endpoint": "/internal/ingestao-inteligente/s3/scaffold",
        },
    )
    logger.info(
        "ingestao_inteligente_s4_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "evento_id": request.evento_id,
            "lote_id": request.lote_id.strip(),
            "lote_upload_id": request.lote_upload_id.strip().lower(),
            "status_processamento": status_processamento,
            "proxima_acao": proxima_acao,
            "codigo_mensagem": mensagem_acionavel["codigo_mensagem"],
        },
    )
    return response


def _validate_s4_contract_input(*, request: S4ScaffoldRequest) -> tuple[str, str]:
    if request.evento_id <= 0:
        _raise_contract_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de montar a UX final.",
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
            action="Use status aceitos pelo contrato da sprint 3 e 4.",
        )

    proxima_acao = request.proxima_acao.strip()
    if proxima_acao not in S4_ALLOWED_NEXT_ACTIONS:
        _raise_contract_error(
            code="INVALID_PROXIMA_ACAO",
            message=f"proxima_acao invalida para UX final: {request.proxima_acao}",
            action=(
                "Use proxima_acao valida: "
                + ", ".join(S4_ALLOWED_NEXT_ACTIONS)
                + "."
            ),
        )

    if (
        proxima_acao == "avaliar_reprocessamento_lote"
        and status_processamento not in S3_REPROCESSABLE_STATUSES
    ):
        _raise_contract_error(
            code="INVALID_STATUS_FOR_REPROCESS_ACTION",
            message="proxima_acao de reprocessamento exige status failed ou partial_success",
            action="Ajuste proxima_acao para refletir o status real retornado pela Sprint 3.",
        )

    if (
        proxima_acao == "consultar_resultado_final_lote"
        and status_processamento not in S3_TERMINAL_STATUSES
    ):
        _raise_contract_error(
            code="INVALID_STATUS_FOR_FINAL_RESULT_ACTION",
            message="proxima_acao de resultado final exige status terminal do lote",
            action="Use consultar_resultado_final_lote apenas com status terminal.",
        )

    return status_processamento, proxima_acao


def _build_s4_actionable_message(*, status_processamento: str, proxima_acao: str) -> dict[str, str]:
    if proxima_acao == "avaliar_reprocessamento_lote":
        return {
            "codigo_mensagem": "S4_REPROCESS_RECOMMENDED",
            "titulo": "Reprocessamento recomendado",
            "mensagem": (
                "O lote apresentou falha parcial ou total. Revise o contexto e confirme "
                "um novo reprocessamento."
            ),
            "acao_recomendada": "Abrir painel de reprocessamento e confirmar tentativa.",
            "severidade": "warning",
        }

    if proxima_acao == "consultar_resultado_final_lote":
        if status_processamento == "completed":
            return {
                "codigo_mensagem": "S4_FINAL_RESULT_COMPLETED",
                "titulo": "Processamento concluido",
                "mensagem": "O lote foi processado com sucesso e esta pronto para consulta final.",
                "acao_recomendada": "Abrir resumo final e validar indicadores de conclusao.",
                "severidade": "success",
            }
        if status_processamento == "cancelled":
            return {
                "codigo_mensagem": "S4_FINAL_RESULT_CANCELLED",
                "titulo": "Processamento cancelado",
                "mensagem": "O lote foi encerrado como cancelado e requer avaliacao operacional.",
                "acao_recomendada": "Registrar justificativa e decidir novo envio do lote.",
                "severidade": "warning",
            }
        return {
            "codigo_mensagem": "S4_FINAL_RESULT_WITH_ISSUES",
            "titulo": "Processamento finalizado com alertas",
            "mensagem": "O lote finalizou com inconsistencias e precisa de tratamento.",
            "acao_recomendada": "Consultar detalhes de erro e planejar reprocessamento manual.",
            "severidade": "warning",
        }

    return {
        "codigo_mensagem": "S4_MONITORING_IN_PROGRESS",
        "titulo": "Monitoramento em andamento",
        "mensagem": "O lote segue em processamento. Continue acompanhando atualizacoes de status.",
        "acao_recomendada": "Manter polling de status ate o lote atingir estado terminal.",
        "severidade": "info",
    }


def _build_s4_accessibility_hints(
    *,
    leitor_tela_ativo: bool,
    alto_contraste_ativo: bool,
    reduzir_movimento: bool,
    severidade_mensagem: str,
) -> dict[str, Any]:
    aria_live = "assertive" if severidade_mensagem in {"warning", "error"} else "polite"
    foco_inicial = "banner_mensagem_acionavel" if leitor_tela_ativo else "acao_recomendada"
    return {
        "leitor_tela_ativo": leitor_tela_ativo,
        "alto_contraste_ativo": alto_contraste_ativo,
        "reduzir_movimento": reduzir_movimento,
        "aria_live": aria_live,
        "foco_inicial": foco_inicial,
    }


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "ingestao_inteligente_s4_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S4ScaffoldContractError(code=code, message=message, action=action)
