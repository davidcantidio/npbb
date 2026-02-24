"""Validation contracts for Sprint 4 final UX and accessibility journey.

This module centralizes Sprint 4 input/output validation used by tests and
integration checks. It provides structured, actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_scaffold import S2_BATCH_ID_RE
from .s3_scaffold import (
    S3_LOTE_UPLOAD_ID_RE,
    S3_REPROCESSABLE_STATUSES,
    S3_TERMINAL_STATUSES,
)
from .s4_core import (
    S4_ALLOWED_MESSAGE_SEVERITIES,
    S4_ALLOWED_PRIORITY,
    S4_ALLOWED_UX_STATUSES,
    S4CoreInput,
)
from .s4_observability import (
    S4ObservabilityInput,
    build_s4_observability_event,
    log_s4_observability_event,
)
from .s4_scaffold import S3_ALLOWED_PROCESSING_STATUSES, S4_ALLOWED_NEXT_ACTIONS


logger = logging.getLogger("npbb.ingestao_inteligente.s4")

S4_VALIDATION_VERSION = "s4.validation.v1"
S4_ALLOWED_FLOW_STATUSES = set(S4_ALLOWED_UX_STATUSES)


class S4ValidationError(ValueError):
    """Raised when Sprint 4 validation contract is violated."""

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
class S4ValidationInput:
    """Input contract consumed by Sprint 4 validation checks."""

    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    leitor_tela_ativo: bool = False
    alto_contraste_ativo: bool = False
    reduzir_movimento: bool = False
    correlation_id: str | None = None

    def to_core_input(self) -> S4CoreInput:
        """Convert validated data to `S4CoreInput` contract."""

        return S4CoreInput(
            evento_id=self.evento_id,
            lote_id=self.lote_id,
            lote_upload_id=self.lote_upload_id,
            status_processamento=self.status_processamento,
            proxima_acao=self.proxima_acao,
            leitor_tela_ativo=self.leitor_tela_ativo,
            alto_contraste_ativo=self.alto_contraste_ativo,
            reduzir_movimento=self.reduzir_movimento,
            correlation_id=self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4ValidationResult:
    """Output contract returned by Sprint 4 input validation."""

    validation_version: str
    validation_id: str
    correlation_id: str
    status: str
    checks: tuple[str, ...]
    observabilidade: dict[str, str]
    resumo_ux: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checks": list(self.checks),
            "observabilidade": self.observabilidade,
            "resumo_ux": self.resumo_ux,
        }


@dataclass(frozen=True, slots=True)
class S4FlowOutputValidationResult:
    """Output contract returned by Sprint 4 flow-output validation."""

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


def validate_s4_input_contract(payload: S4ValidationInput) -> S4ValidationResult:
    """Validate Sprint 4 input contract before running the main flow.

    Args:
        payload: Input contract with UX and accessibility metadata.

    Returns:
        S4ValidationResult: Validation metadata and performed checks.

    Raises:
        S4ValidationError: If any mandatory contract rule is violated.
    """

    correlation_id = payload.correlation_id or f"s4-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="ingestao_inteligente_s4_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 4 iniciada",
        severity="info",
        evento_id=payload.evento_id if payload.evento_id > 0 else None,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        proxima_acao=payload.proxima_acao,
    )
    checks: list[str] = []

    if payload.evento_id <= 0:
        _raise_validation_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de montar a UX final.",
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

    lote_upload_id = payload.lote_upload_id.strip().lower()
    if not S3_LOTE_UPLOAD_ID_RE.match(lote_upload_id):
        _raise_validation_error(
            code="INVALID_LOTE_UPLOAD_ID",
            message="lote_upload_id invalido: use prefixo lot- com sufixo alfanumerico",
            action="Use o identificador retornado pelo endpoint /s2/lote/upload.",
            correlation_id=correlation_id,
            context={"lote_upload_id": payload.lote_upload_id},
        )
    checks.append("lote_upload_id")

    status_processamento = payload.status_processamento.strip().lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        _raise_validation_error(
            code="INVALID_STATUS_PROCESSAMENTO",
            message=f"status_processamento invalido: {payload.status_processamento}",
            action="Use status aceitos pelo contrato da sprint 3 e 4.",
            correlation_id=correlation_id,
            context={"status_processamento": payload.status_processamento},
        )
    checks.append("status_processamento")

    proxima_acao = payload.proxima_acao.strip()
    if proxima_acao not in S4_ALLOWED_NEXT_ACTIONS:
        _raise_validation_error(
            code="INVALID_PROXIMA_ACAO",
            message=f"proxima_acao invalida para UX final: {payload.proxima_acao}",
            action="Use proxima_acao valida para monitoramento, reprocessamento ou resultado.",
            correlation_id=correlation_id,
            context={"proxima_acao": payload.proxima_acao},
        )
    checks.append("proxima_acao")

    if (
        proxima_acao == "avaliar_reprocessamento_lote"
        and status_processamento not in S3_REPROCESSABLE_STATUSES
    ):
        _raise_validation_error(
            code="INVALID_STATUS_FOR_REPROCESS_ACTION",
            message="proxima_acao de reprocessamento exige status failed ou partial_success",
            action="Ajuste proxima_acao para refletir o status real retornado pela Sprint 3.",
            correlation_id=correlation_id,
            context={
                "proxima_acao": proxima_acao,
                "status_processamento": status_processamento,
            },
        )
    if (
        proxima_acao == "consultar_resultado_final_lote"
        and status_processamento not in S3_TERMINAL_STATUSES
    ):
        _raise_validation_error(
            code="INVALID_STATUS_FOR_FINAL_RESULT_ACTION",
            message="proxima_acao de resultado final exige status terminal do lote",
            action="Use consultar_resultado_final_lote apenas com status terminal.",
            correlation_id=correlation_id,
            context={
                "proxima_acao": proxima_acao,
                "status_processamento": status_processamento,
            },
        )
    checks.append("status_vs_next_action")

    _validate_bool_flag(
        value=payload.leitor_tela_ativo,
        field_name="leitor_tela_ativo",
        correlation_id=correlation_id,
    )
    _validate_bool_flag(
        value=payload.alto_contraste_ativo,
        field_name="alto_contraste_ativo",
        correlation_id=correlation_id,
    )
    _validate_bool_flag(
        value=payload.reduzir_movimento,
        field_name="reduzir_movimento",
        correlation_id=correlation_id,
    )
    checks.extend(("leitor_tela_ativo", "alto_contraste_ativo", "reduzir_movimento"))

    codigo_mensagem, severidade_mensagem = _resolve_expected_message(
        status_processamento=status_processamento,
        proxima_acao=proxima_acao,
    )
    completed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s4_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 4 concluida com sucesso",
        severity="info",
        evento_id=payload.evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        status_processamento=status_processamento,
        proxima_acao=proxima_acao,
        codigo_mensagem=codigo_mensagem,
        severidade_mensagem=severidade_mensagem,
        context={"checks": checks},
    )

    validation_id = f"val-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s4_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "lote_id": lote_id,
            "lote_upload_id": lote_upload_id,
            "status_processamento": status_processamento,
            "proxima_acao": proxima_acao,
            "checks": checks,
        },
    )
    return S4ValidationResult(
        validation_version=S4_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
        resumo_ux={
            "status_processamento": status_processamento,
            "proxima_acao": proxima_acao,
            "codigo_mensagem_esperado": codigo_mensagem,
            "severidade_mensagem_esperada": severidade_mensagem,
            "acessibilidade": {
                "leitor_tela_ativo": payload.leitor_tela_ativo,
                "alto_contraste_ativo": payload.alto_contraste_ativo,
                "reduzir_movimento": payload.reduzir_movimento,
            },
        },
    )


def validate_s4_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S4FlowOutputValidationResult:
    """Validate Sprint 4 main-flow output contract.

    Args:
        flow_output: Output dictionary produced by `execute_s4_main_flow`.
        correlation_id: Correlation id propagated through Sprint 4 flow.

    Returns:
        S4FlowOutputValidationResult: Summary of checked output fields.

    Raises:
        S4ValidationError: If output contract is incomplete or inconsistent.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "evento_id",
        "lote_id",
        "lote_upload_id",
        "status_processamento",
        "proxima_acao",
        "mensagem_acionavel",
        "acessibilidade",
        "experiencia_usuario",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
        "ux",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo principal incompleta: faltam campos {missing_fields}",
            action="Atualize o core flow para retornar o contrato completo da sprint 4.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    status = str(flow_output["status"]).lower()
    if status not in S4_ALLOWED_FLOW_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo principal: {flow_output['status']}",
            action="Use status aceitos: ready ou ok.",
            correlation_id=correlation_id,
            context={"status": str(flow_output["status"])},
        )

    status_processamento = str(flow_output["status_processamento"]).lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS_PROCESSAMENTO",
            message=f"status_processamento final inesperado: {flow_output['status_processamento']}",
            action="Retorne status_processamento compativel com contrato s4.v1.",
            correlation_id=correlation_id,
            context={"status_processamento": str(flow_output["status_processamento"])},
        )

    proxima_acao = str(flow_output["proxima_acao"]).strip()
    if proxima_acao not in S4_ALLOWED_NEXT_ACTIONS:
        _raise_validation_error(
            code="INVALID_FLOW_NEXT_ACTION",
            message=f"proxima_acao final inesperada: {flow_output['proxima_acao']}",
            action="Retorne proxima_acao valida para UX final da Sprint 4.",
            correlation_id=correlation_id,
            context={"proxima_acao": str(flow_output["proxima_acao"])},
        )

    observabilidade = flow_output.get("observabilidade", {})
    required_obs_fields = (
        "flow_started_event_id",
        "ux_dispatch_event_id",
        "flow_completed_event_id",
    )
    for field in required_obs_fields:
        value = str(observabilidade.get(field, ""))
        if not value.startswith("s4evt-"):
            _raise_validation_error(
                code="INVALID_OBSERVABILITY_OUTPUT",
                message=f"Campo de observabilidade invalido: {field}",
                action="Propague IDs de observabilidade 's4evt-*' no output do fluxo.",
                correlation_id=correlation_id,
                context={"field": field, "value": value},
            )

    ux = flow_output.get("ux", {})
    required_ux_fields = (
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
    missing_ux_fields = [field for field in required_ux_fields if field not in ux]
    if missing_ux_fields:
        _raise_validation_error(
            code="INCOMPLETE_UX_OUTPUT",
            message=f"Bloco ux incompleto: faltam campos {missing_ux_fields}",
            action="Atualize o fluxo para propagar resposta completa de /s4/ux.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_ux_fields)},
        )

    if int(ux["evento_id"]) != int(flow_output["evento_id"]):
        _raise_validation_error(
            code="EVENTO_ID_MISMATCH",
            message="evento_id divergente entre o topo e o bloco ux",
            action="Garanta consistencia de evento_id na saida do fluxo.",
            correlation_id=correlation_id,
        )
    if str(ux["lote_id"]).strip() != str(flow_output["lote_id"]).strip():
        _raise_validation_error(
            code="LOTE_ID_MISMATCH",
            message="lote_id divergente entre o topo e o bloco ux",
            action="Garanta consistencia de lote_id na saida do fluxo.",
            correlation_id=correlation_id,
        )
    if str(ux["lote_upload_id"]).strip().lower() != str(flow_output["lote_upload_id"]).strip().lower():
        _raise_validation_error(
            code="LOTE_UPLOAD_ID_MISMATCH",
            message="lote_upload_id divergente entre o topo e o bloco ux",
            action="Garanta consistencia de lote_upload_id na saida do fluxo.",
            correlation_id=correlation_id,
        )

    if str(ux["status"]).lower() != status:
        _raise_validation_error(
            code="FLOW_STATUS_MISMATCH",
            message="status divergente entre o topo e o bloco ux",
            action="Garanta consistencia de status entre saida principal e bloco ux.",
            correlation_id=correlation_id,
        )
    if str(ux["status_processamento"]).lower() != status_processamento:
        _raise_validation_error(
            code="FLOW_STATUS_PROCESSAMENTO_MISMATCH",
            message="status_processamento divergente entre o topo e o bloco ux",
            action="Garanta consistencia de status_processamento no output do fluxo.",
            correlation_id=correlation_id,
        )
    if str(ux["proxima_acao"]).strip() != proxima_acao:
        _raise_validation_error(
            code="FLOW_NEXT_ACTION_MISMATCH",
            message="proxima_acao divergente entre o topo e o bloco ux",
            action="Garanta consistencia de proxima_acao no output do fluxo.",
            correlation_id=correlation_id,
        )

    _validate_actionable_message(flow_output["mensagem_acionavel"], correlation_id=correlation_id)
    _validate_actionable_message(ux["mensagem_acionavel"], correlation_id=correlation_id)
    _validate_accessibility(flow_output["acessibilidade"], correlation_id=correlation_id)
    _validate_accessibility(ux["acessibilidade"], correlation_id=correlation_id)
    _validate_ux_experience(flow_output["experiencia_usuario"], correlation_id=correlation_id)
    _validate_ux_experience(ux["experiencia_usuario"], correlation_id=correlation_id)

    if flow_output["mensagem_acionavel"] != ux["mensagem_acionavel"]:
        _raise_validation_error(
            code="ACTIONABLE_MESSAGE_MISMATCH",
            message="mensagem_acionavel divergente entre o topo e o bloco ux",
            action="Propague o mesmo payload de mensagem_acionavel no output final.",
            correlation_id=correlation_id,
        )
    if flow_output["acessibilidade"] != ux["acessibilidade"]:
        _raise_validation_error(
            code="ACCESSIBILITY_BLOCK_MISMATCH",
            message="acessibilidade divergente entre o topo e o bloco ux",
            action="Propague o mesmo payload de acessibilidade no output final.",
            correlation_id=correlation_id,
        )
    if flow_output["experiencia_usuario"] != ux["experiencia_usuario"]:
        _raise_validation_error(
            code="UX_EXPERIENCE_BLOCK_MISMATCH",
            message="experiencia_usuario divergente entre o topo e o bloco ux",
            action="Propague o mesmo payload de experiencia_usuario no output final.",
            correlation_id=correlation_id,
        )

    logger.info(
        "ingestao_inteligente_s4_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "checked_fields": required_fields,
            "lote_id": str(flow_output["lote_id"]).strip(),
            "lote_upload_id": str(flow_output["lote_upload_id"]).strip().lower(),
        },
    )
    return S4FlowOutputValidationResult(
        correlation_id=correlation_id,
        status="valid",
        checked_fields=required_fields,
        observabilidade={field: str(observabilidade[field]) for field in required_obs_fields},
    )


def _validate_actionable_message(payload: Any, *, correlation_id: str) -> None:
    if not isinstance(payload, dict):
        _raise_validation_error(
            code="INVALID_ACTIONABLE_MESSAGE_OUTPUT",
            message="mensagem_acionavel invalida: formato nao suportado",
            action="Retorne mensagem_acionavel como objeto JSON com campos obrigatorios.",
            correlation_id=correlation_id,
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
        _raise_validation_error(
            code="INCOMPLETE_ACTIONABLE_MESSAGE_OUTPUT",
            message=f"mensagem_acionavel incompleta: faltam campos {missing_fields}",
            action="Inclua os campos obrigatorios de mensagem_acionavel no output da Sprint 4.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    severidade = str(payload["severidade"]).lower()
    if severidade not in S4_ALLOWED_MESSAGE_SEVERITIES:
        _raise_validation_error(
            code="INVALID_MESSAGE_SEVERITY_OUTPUT",
            message=f"severidade invalida em mensagem_acionavel: {payload['severidade']}",
            action="Use severidades aceitas: info, warning, success ou error.",
            correlation_id=correlation_id,
            context={"severidade": str(payload["severidade"])},
        )


def _validate_accessibility(payload: Any, *, correlation_id: str) -> None:
    if not isinstance(payload, dict):
        _raise_validation_error(
            code="INVALID_ACCESSIBILITY_OUTPUT",
            message="acessibilidade invalida: formato nao suportado",
            action="Retorne acessibilidade como objeto JSON com campos obrigatorios.",
            correlation_id=correlation_id,
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
        _raise_validation_error(
            code="INCOMPLETE_ACCESSIBILITY_OUTPUT",
            message=f"acessibilidade incompleta: faltam campos {missing_fields}",
            action="Inclua os campos obrigatorios de acessibilidade no output da Sprint 4.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    for field in ("leitor_tela_ativo", "alto_contraste_ativo", "reduzir_movimento"):
        if not isinstance(payload[field], bool):
            _raise_validation_error(
                code="INVALID_ACCESSIBILITY_FLAG_OUTPUT",
                message=f"{field} invalido em acessibilidade: deve ser booleano",
                action="Retorne flags de acessibilidade com valores true/false.",
                correlation_id=correlation_id,
                context={"field": field},
            )

    aria_live = str(payload["aria_live"]).lower()
    if aria_live not in {"polite", "assertive"}:
        _raise_validation_error(
            code="INVALID_ARIA_LIVE_OUTPUT",
            message=f"aria_live invalido em acessibilidade: {payload['aria_live']}",
            action="Use aria_live com valores polite ou assertive.",
            correlation_id=correlation_id,
            context={"aria_live": str(payload["aria_live"])},
        )

    foco_inicial = str(payload["foco_inicial"]).strip()
    if foco_inicial not in {"banner_mensagem_acionavel", "acao_recomendada"}:
        _raise_validation_error(
            code="INVALID_FOCUS_TARGET_OUTPUT",
            message=f"foco_inicial invalido em acessibilidade: {payload['foco_inicial']}",
            action="Use foco_inicial em banner_mensagem_acionavel ou acao_recomendada.",
            correlation_id=correlation_id,
            context={"foco_inicial": foco_inicial},
        )


def _validate_ux_experience(payload: Any, *, correlation_id: str) -> None:
    if not isinstance(payload, dict):
        _raise_validation_error(
            code="INVALID_UX_EXPERIENCE_OUTPUT",
            message="experiencia_usuario invalida: formato nao suportado",
            action="Retorne experiencia_usuario como objeto JSON com campos obrigatorios.",
            correlation_id=correlation_id,
        )

    required_fields = (
        "exibir_banner_acao",
        "destino_acao_principal",
        "prioridade_exibicao",
    )
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_UX_EXPERIENCE_OUTPUT",
            message=f"experiencia_usuario incompleta: faltam campos {missing_fields}",
            action="Inclua os campos obrigatorios de experiencia_usuario no output da Sprint 4.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    if not isinstance(payload["exibir_banner_acao"], bool):
        _raise_validation_error(
            code="INVALID_UX_BANNER_FLAG_OUTPUT",
            message="exibir_banner_acao invalido em experiencia_usuario",
            action="Retorne exibir_banner_acao com valor true/false.",
            correlation_id=correlation_id,
        )

    if len(str(payload["destino_acao_principal"]).strip()) < 3:
        _raise_validation_error(
            code="INVALID_UX_PRIMARY_ACTION_TARGET_OUTPUT",
            message="destino_acao_principal invalido em experiencia_usuario",
            action="Informe destino_acao_principal descritivo com ao menos 3 caracteres.",
            correlation_id=correlation_id,
        )

    prioridade_exibicao = str(payload["prioridade_exibicao"]).lower()
    if prioridade_exibicao not in S4_ALLOWED_PRIORITY:
        _raise_validation_error(
            code="INVALID_UX_PRIORITY_OUTPUT",
            message="prioridade_exibicao invalida em experiencia_usuario",
            action="Use prioridade_exibicao com valores high, medium ou low.",
            correlation_id=correlation_id,
            context={"prioridade_exibicao": str(payload["prioridade_exibicao"])},
        )


def _validate_bool_flag(*, value: Any, field_name: str, correlation_id: str) -> None:
    if isinstance(value, bool):
        return

    _raise_validation_error(
        code="INVALID_ACCESSIBILITY_FLAG",
        message=f"{field_name} deve ser booleano",
        action="Corrija as flags de acessibilidade para true/false.",
        correlation_id=correlation_id,
        context={"field_name": field_name, "received_type": type(value).__name__},
    )


def _resolve_expected_message(
    *,
    status_processamento: str,
    proxima_acao: str,
) -> tuple[str, str]:
    if proxima_acao == "avaliar_reprocessamento_lote":
        return "S4_REPROCESS_RECOMMENDED", "warning"
    if proxima_acao == "consultar_resultado_final_lote":
        if status_processamento == "completed":
            return "S4_FINAL_RESULT_COMPLETED", "success"
        if status_processamento == "cancelled":
            return "S4_FINAL_RESULT_CANCELLED", "warning"
        return "S4_FINAL_RESULT_WITH_ISSUES", "warning"
    return "S4_MONITORING_IN_PROGRESS", "info"


def _raise_validation_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    failed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s4_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "ingestao_inteligente_s4_validation_error",
        extra={
            "correlation_id": correlation_id,
            "error_code": code,
            "error_message": message,
            "action": action,
            "context": context or {},
            "observability_event_id": failed_event.observability_event_id,
        },
    )
    raise S4ValidationError(
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
    status_processamento: str | None = None,
    proxima_acao: str | None = None,
    codigo_mensagem: str | None = None,
    severidade_mensagem: str | None = None,
    destino_acao_principal: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S4ObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        status_processamento=status_processamento,
        proxima_acao=proxima_acao,
        codigo_mensagem=codigo_mensagem,
        severidade_mensagem=severidade_mensagem,
        destino_acao_principal=destino_acao_principal,
        context=context,
    )
    event = build_s4_observability_event(payload)
    log_s4_observability_event(event)
    return event
