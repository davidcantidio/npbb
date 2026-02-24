"""Validation contracts for Sprint 3 monitoring and reprocessing journey.

This module centralizes Sprint 3 input/output validation used by tests and
integration checks. It provides structured, actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_scaffold import S2_BATCH_ID_RE
from .s3_core import S3CoreInput
from .s3_observability import (
    S3ObservabilityInput,
    build_s3_observability_event,
    log_s3_observability_event,
)
from .s3_scaffold import (
    MAX_REPROCESS_ATTEMPTS,
    S3_ALLOWED_PROCESSING_STATUSES,
    S3_LOTE_UPLOAD_ID_RE,
    S3_REPROCESSABLE_STATUSES,
)


logger = logging.getLogger("npbb.ingestao_inteligente.s3")

S3_VALIDATION_VERSION = "s3.validation.v1"
S3_ALLOWED_NEXT_ACTIONS = {
    "monitorar_status_lote",
    "avaliar_reprocessamento_lote",
    "consultar_resultado_final_lote",
}
S3_ALLOWED_FLOW_STATUSES = {"ready", "accepted", "queued", "processing"}


class S3ValidationError(ValueError):
    """Raised when Sprint 3 validation contract is violated."""

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
class S3ValidationInput:
    """Input contract consumed by Sprint 3 validation checks."""

    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    tentativas_reprocessamento: int = 0
    reprocessamento_habilitado: bool = True
    motivo_reprocessamento: str | None = None
    correlation_id: str | None = None

    def to_core_input(self) -> S3CoreInput:
        """Convert validated data to `S3CoreInput` contract."""

        return S3CoreInput(
            evento_id=self.evento_id,
            lote_id=self.lote_id,
            lote_upload_id=self.lote_upload_id,
            status_processamento=self.status_processamento,
            tentativas_reprocessamento=self.tentativas_reprocessamento,
            reprocessamento_habilitado=self.reprocessamento_habilitado,
            motivo_reprocessamento=self.motivo_reprocessamento,
            correlation_id=self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3ValidationResult:
    """Output contract returned by Sprint 3 input validation."""

    validation_version: str
    validation_id: str
    correlation_id: str
    status: str
    checks: tuple[str, ...]
    observabilidade: dict[str, str]
    resumo_monitoramento: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checks": list(self.checks),
            "observabilidade": self.observabilidade,
            "resumo_monitoramento": self.resumo_monitoramento,
        }


@dataclass(frozen=True, slots=True)
class S3FlowOutputValidationResult:
    """Output contract returned by Sprint 3 flow-output validation."""

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


def validate_s3_input_contract(payload: S3ValidationInput) -> S3ValidationResult:
    """Validate Sprint 3 input contract before running the main flow.

    Args:
        payload: Input contract with monitoring and reprocessing metadata.

    Returns:
        S3ValidationResult: Validation metadata and performed checks.

    Raises:
        S3ValidationError: If any mandatory contract rule is violated.
    """

    correlation_id = payload.correlation_id or f"s3-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="ingestao_inteligente_s3_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 3 iniciada",
        severity="info",
        evento_id=payload.evento_id if payload.evento_id > 0 else None,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        tentativas_reprocessamento=payload.tentativas_reprocessamento,
    )
    checks: list[str] = []

    if payload.evento_id <= 0:
        _raise_validation_error(
            code="INVALID_EVENTO_ID",
            message="evento_id deve ser maior que zero",
            action="Selecione um evento valido antes de monitorar o lote.",
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
            action=(
                "Use status aceitos: " + ", ".join(S3_ALLOWED_PROCESSING_STATUSES) + "."
            ),
            correlation_id=correlation_id,
            context={"status_processamento": payload.status_processamento},
        )
    checks.append("status_processamento")

    if payload.tentativas_reprocessamento < 0:
        _raise_validation_error(
            code="INVALID_REPROCESS_ATTEMPTS",
            message="tentativas_reprocessamento nao pode ser negativo",
            action="Informe quantidade de tentativas maior ou igual a zero.",
            correlation_id=correlation_id,
            context={"tentativas_reprocessamento": payload.tentativas_reprocessamento},
        )
    if payload.tentativas_reprocessamento > MAX_REPROCESS_ATTEMPTS:
        _raise_validation_error(
            code="REPROCESS_ATTEMPTS_EXCEEDED",
            message=(
                f"tentativas_reprocessamento excede limite de {MAX_REPROCESS_ATTEMPTS}: "
                f"{payload.tentativas_reprocessamento}"
            ),
            action="Encaminhe para analise manual ou ajuste limite operacional do fluxo.",
            correlation_id=correlation_id,
            context={"tentativas_reprocessamento": payload.tentativas_reprocessamento},
        )
    checks.append("tentativas_reprocessamento")

    motivo_reprocessamento = (payload.motivo_reprocessamento or "").strip()
    if motivo_reprocessamento and len(motivo_reprocessamento) < 3:
        _raise_validation_error(
            code="INVALID_MOTIVO_REPROCESSAMENTO",
            message="motivo_reprocessamento deve ter ao menos 3 caracteres",
            action="Forneca motivo minimo para auditoria do reprocessamento.",
            correlation_id=correlation_id,
            context={"motivo_reprocessamento": motivo_reprocessamento},
        )
    checks.append("motivo_reprocessamento")

    completed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s3_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada da Sprint 3 concluida com sucesso",
        severity="info",
        evento_id=payload.evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        status_processamento=status_processamento,
        tentativas_reprocessamento=payload.tentativas_reprocessamento,
        context={"checks": checks},
    )

    validation_id = f"val-{uuid4().hex[:12]}"
    logger.info(
        "ingestao_inteligente_s3_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "lote_id": lote_id,
            "lote_upload_id": lote_upload_id,
            "status_processamento": status_processamento,
            "checks": checks,
        },
    )
    return S3ValidationResult(
        validation_version=S3_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
        resumo_monitoramento={
            "status_processamento": status_processamento,
            "tentativas_reprocessamento": payload.tentativas_reprocessamento,
            "reprocessamento_habilitado": payload.reprocessamento_habilitado,
            "elegivel_reprocessamento": status_processamento in S3_REPROCESSABLE_STATUSES,
        },
    )


def validate_s3_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S3FlowOutputValidationResult:
    """Validate Sprint 3 main-flow output contract.

    Args:
        flow_output: Output dictionary produced by `execute_s3_main_flow`.
        correlation_id: Correlation id propagated through Sprint 3 flow.

    Returns:
        S3FlowOutputValidationResult: Summary of checked output fields.

    Raises:
        S3ValidationError: If output contract is incomplete or inconsistent.
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
        "pontos_integracao",
        "observabilidade",
        "scaffold",
        "status_monitoramento",
        "reprocessamento",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo principal incompleta: faltam campos {missing_fields}",
            action="Atualize o core flow para retornar o contrato completo da sprint 3.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_fields)},
        )

    status = str(flow_output["status"]).lower()
    if status not in S3_ALLOWED_FLOW_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo principal: {flow_output['status']}",
            action="Use status aceitos: ready, accepted, queued ou processing.",
            correlation_id=correlation_id,
            context={"status": str(flow_output["status"])},
        )

    status_processamento = str(flow_output["status_processamento"]).lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS_PROCESSAMENTO",
            message=f"status_processamento final inesperado: {flow_output['status_processamento']}",
            action="Retorne status_processamento compativel com contrato s3.v1.",
            correlation_id=correlation_id,
            context={"status_processamento": str(flow_output["status_processamento"])},
        )

    proxima_acao = str(flow_output["proxima_acao"])
    if proxima_acao not in S3_ALLOWED_NEXT_ACTIONS:
        _raise_validation_error(
            code="INVALID_FLOW_NEXT_ACTION",
            message=f"proxima_acao final inesperada: {flow_output['proxima_acao']}",
            action="Retorne proxima_acao valida para monitoramento/reprocessamento.",
            correlation_id=correlation_id,
            context={"proxima_acao": str(flow_output["proxima_acao"])},
        )

    observabilidade = flow_output.get("observabilidade", {})
    required_obs_fields = (
        "flow_started_event_id",
        "status_dispatch_event_id",
        "flow_completed_event_id",
    )
    for field in required_obs_fields:
        value = str(observabilidade.get(field, ""))
        if not value.startswith("s3evt-"):
            _raise_validation_error(
                code="INVALID_OBSERVABILITY_OUTPUT",
                message=f"Campo de observabilidade invalido: {field}",
                action="Propague IDs de observabilidade 's3evt-*' no output do fluxo.",
                correlation_id=correlation_id,
                context={"field": field, "value": value},
            )

    status_monitoramento = flow_output.get("status_monitoramento", {})
    required_status_fields = (
        "status",
        "evento_id",
        "lote_id",
        "lote_upload_id",
        "status_processamento",
        "proxima_acao",
    )
    missing_status_fields = [
        field for field in required_status_fields if field not in status_monitoramento
    ]
    if missing_status_fields:
        _raise_validation_error(
            code="INCOMPLETE_STATUS_MONITORING_OUTPUT",
            message=(
                "Bloco status_monitoramento incompleto: "
                f"faltam campos {missing_status_fields}"
            ),
            action="Atualize o fluxo para propagar resposta completa de /s3/status.",
            correlation_id=correlation_id,
            context={"missing_fields": ",".join(missing_status_fields)},
        )

    top_evento_id = int(flow_output["evento_id"])
    if int(status_monitoramento["evento_id"]) != top_evento_id:
        _raise_validation_error(
            code="EVENTO_ID_MISMATCH",
            message="evento_id divergente entre o topo e o bloco status_monitoramento",
            action="Garanta consistencia de evento_id na saida do fluxo.",
            correlation_id=correlation_id,
            context={
                "top_level_evento_id": top_evento_id,
                "nested_evento_id": int(status_monitoramento["evento_id"]),
            },
        )

    top_lote_id = str(flow_output["lote_id"]).strip()
    if str(status_monitoramento["lote_id"]).strip() != top_lote_id:
        _raise_validation_error(
            code="LOTE_ID_MISMATCH",
            message="lote_id divergente entre o topo e o bloco status_monitoramento",
            action="Garanta consistencia de lote_id na saida do fluxo.",
            correlation_id=correlation_id,
            context={
                "top_level_lote_id": top_lote_id,
                "nested_lote_id": str(status_monitoramento["lote_id"]).strip(),
            },
        )

    top_lote_upload_id = str(flow_output["lote_upload_id"]).strip().lower()
    if str(status_monitoramento["lote_upload_id"]).strip().lower() != top_lote_upload_id:
        _raise_validation_error(
            code="LOTE_UPLOAD_ID_MISMATCH",
            message=(
                "lote_upload_id divergente entre o topo e o bloco "
                "status_monitoramento"
            ),
            action="Garanta consistencia de lote_upload_id na saida do fluxo.",
            correlation_id=correlation_id,
            context={
                "top_level_lote_upload_id": top_lote_upload_id,
                "nested_lote_upload_id": str(status_monitoramento["lote_upload_id"])
                .strip()
                .lower(),
            },
        )

    reprocessamento = flow_output.get("reprocessamento")
    if reprocessamento is None:
        if "reprocess_dispatch_event_id" in observabilidade:
            _raise_validation_error(
                code="UNEXPECTED_REPROCESS_OBSERVABILITY_EVENT",
                message="reprocess_dispatch_event_id presente sem bloco reprocessamento",
                action="Inclua bloco reprocessamento ou remova evento de dispatch.",
                correlation_id=correlation_id,
                context={"reprocess_dispatch_event_id": observabilidade.get("reprocess_dispatch_event_id")},
            )
    else:
        reprocess_event_id = str(observabilidade.get("reprocess_dispatch_event_id", ""))
        if not reprocess_event_id.startswith("s3evt-"):
            _raise_validation_error(
                code="MISSING_REPROCESS_OBSERVABILITY_EVENT",
                message="reprocess_dispatch_event_id ausente ou invalido no output",
                action="Propague ID de dispatch do reprocessamento no output.",
                correlation_id=correlation_id,
                context={"reprocess_dispatch_event_id": reprocess_event_id},
            )

        required_reprocess_fields = (
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
        missing_reprocess_fields = [
            field for field in required_reprocess_fields if field not in reprocessamento
        ]
        if missing_reprocess_fields:
            _raise_validation_error(
                code="INCOMPLETE_REPROCESS_OUTPUT",
                message=f"Bloco reprocessamento incompleto: faltam campos {missing_reprocess_fields}",
                action="Atualize o fluxo para propagar resposta completa de /s3/reprocessar.",
                correlation_id=correlation_id,
                context={"missing_fields": ",".join(missing_reprocess_fields)},
            )

        if int(reprocessamento["evento_id"]) != top_evento_id:
            _raise_validation_error(
                code="REPROCESS_EVENTO_ID_MISMATCH",
                message="evento_id divergente entre o topo e o bloco reprocessamento",
                action="Garanta consistencia de evento_id na saida do fluxo.",
                correlation_id=correlation_id,
                context={
                    "top_level_evento_id": top_evento_id,
                    "nested_evento_id": int(reprocessamento["evento_id"]),
                },
            )

        if str(reprocessamento["lote_id"]).strip() != top_lote_id:
            _raise_validation_error(
                code="REPROCESS_LOTE_ID_MISMATCH",
                message="lote_id divergente entre o topo e o bloco reprocessamento",
                action="Garanta consistencia de lote_id na saida do fluxo.",
                correlation_id=correlation_id,
                context={
                    "top_level_lote_id": top_lote_id,
                    "nested_lote_id": str(reprocessamento["lote_id"]).strip(),
                },
            )

        if str(reprocessamento["lote_upload_id"]).strip().lower() != top_lote_upload_id:
            _raise_validation_error(
                code="REPROCESS_LOTE_UPLOAD_ID_MISMATCH",
                message=(
                    "lote_upload_id divergente entre o topo e o bloco reprocessamento"
                ),
                action="Garanta consistencia de lote_upload_id na saida do fluxo.",
                correlation_id=correlation_id,
                context={
                    "top_level_lote_upload_id": top_lote_upload_id,
                    "nested_lote_upload_id": str(reprocessamento["lote_upload_id"])
                    .strip()
                    .lower(),
                },
            )

        if str(reprocessamento["status_reprocessamento"]).lower() not in {"queued", "processing"}:
            _raise_validation_error(
                code="INVALID_REPROCESS_STATUS",
                message=(
                    "status_reprocessamento invalido no bloco reprocessamento: "
                    f"{reprocessamento['status_reprocessamento']}"
                ),
                action="Use status_reprocessamento queued ou processing.",
                correlation_id=correlation_id,
                context={"status_reprocessamento": str(reprocessamento["status_reprocessamento"])},
            )

        if int(reprocessamento["tentativas_reprocessamento"]) <= 0:
            _raise_validation_error(
                code="INVALID_REPROCESS_ATTEMPTS_OUTPUT",
                message="tentativas_reprocessamento invalido no bloco reprocessamento",
                action="Retorne contador de tentativas maior que zero apos reprocessar.",
                correlation_id=correlation_id,
                context={"tentativas_reprocessamento": int(reprocessamento["tentativas_reprocessamento"])},
            )

    logger.info(
        "ingestao_inteligente_s3_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "checked_fields": required_fields,
            "lote_id": top_lote_id,
            "lote_upload_id": top_lote_upload_id,
            "reprocess_triggered": reprocessamento is not None,
        },
    )
    return S3FlowOutputValidationResult(
        correlation_id=correlation_id,
        status="valid",
        checked_fields=required_fields,
        observabilidade={field: str(observabilidade[field]) for field in required_obs_fields},
    )


def _raise_validation_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    failed_event = _emit_observability_event(
        event_name="ingestao_inteligente_s3_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "ingestao_inteligente_s3_validation_error",
        extra={
            "correlation_id": correlation_id,
            "error_code": code,
            "error_message": message,
            "action": action,
            "context": context or {},
            "observability_event_id": failed_event.observability_event_id,
        },
    )
    raise S3ValidationError(
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
    tentativas_reprocessamento: int | None = None,
    reprocessamento_id: str | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S3ObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        evento_id=evento_id,
        lote_id=lote_id,
        lote_upload_id=lote_upload_id,
        status_processamento=status_processamento,
        tentativas_reprocessamento=tentativas_reprocessamento,
        reprocessamento_id=reprocessamento_id,
        context=context,
    )
    event = build_s3_observability_event(payload)
    log_s3_observability_event(event)
    return event
