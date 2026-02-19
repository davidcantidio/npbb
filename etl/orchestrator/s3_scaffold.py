"""Sprint 3 scaffold contracts for ORQ agent-first orchestration.

This module defines the stable input/output contract used by ORQ Sprint 3 to
prepare route selection, fallback policy, and circuit breaker controls.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s3")

CONTRACT_VERSION = "orq.s3.v1"
BACKEND_ORQ_S3_PREPARE_ENDPOINT = "/internal/etl/orchestrator/s3/prepare"
SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")

ALLOWED_SOURCE_KINDS = ("pdf", "xlsx", "csv", "pptx", "docx", "other")
ALLOWED_ROUTES = (
    "agent_first_extract",
    "agent_pdf_extract",
    "agent_tabular_extract",
    "agent_document_extract",
    "manual_assistido_review",
)
DETERMINISTIC_FALLBACK_BY_KIND = {
    "pdf": "deterministic_pdf_extract",
    "xlsx": "deterministic_tabular_extract",
    "csv": "deterministic_tabular_extract",
    "pptx": "hybrid_document_extract",
    "docx": "hybrid_document_extract",
    "other": "hybrid_document_extract",
}

MIN_RETRY_ATTEMPTS = 0
MAX_RETRY_ATTEMPTS = 5
MIN_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 900
MIN_CIRCUIT_BREAKER_THRESHOLD = 1
MAX_CIRCUIT_BREAKER_THRESHOLD = 10
MIN_CIRCUIT_RESET_TIMEOUT_SECONDS = 30
MAX_CIRCUIT_RESET_TIMEOUT_SECONDS = 3600


class S3OrchestratorScaffoldError(ValueError):
    """Raised when ORQ S3 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3OrchestratorScaffoldRequest:
    """Input contract for ORQ Sprint 3 scaffold validation."""

    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    agent_habilitado: bool = True
    permitir_fallback_deterministico: bool = True
    permitir_fallback_manual: bool = True
    retry_attempts: int = 0
    timeout_seconds: int = 240
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_reset_timeout_seconds: int = 180
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible ORQ Sprint 3 contract."""

        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "agent_habilitado": self.agent_habilitado,
            "permitir_fallback_deterministico": self.permitir_fallback_deterministico,
            "permitir_fallback_manual": self.permitir_fallback_manual,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "circuit_breaker_reset_timeout_seconds": self.circuit_breaker_reset_timeout_seconds,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3OrchestratorScaffoldResponse:
    """Output contract returned when ORQ Sprint 3 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_execucao: dict[str, Any]
    circuit_breaker: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "plano_execucao": self.plano_execucao,
            "circuit_breaker": self.circuit_breaker,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s3_scaffold_contract(
    request: S3OrchestratorScaffoldRequest,
) -> S3OrchestratorScaffoldResponse:
    """Build ORQ Sprint 3 scaffold contract for agent-first orchestration."""

    correlation_id = request.correlation_id or f"orq-s3-{uuid4().hex[:12]}"
    logger.info(
        "etl_orchestrator_s3_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "source_uri": request.source_uri,
            "rota_selecionada": request.rota_selecionada,
            "agent_habilitado": request.agent_habilitado,
            "permitir_fallback_deterministico": request.permitir_fallback_deterministico,
            "permitir_fallback_manual": request.permitir_fallback_manual,
            "retry_attempts": request.retry_attempts,
            "timeout_seconds": request.timeout_seconds,
            "circuit_breaker_failure_threshold": request.circuit_breaker_failure_threshold,
            "circuit_breaker_reset_timeout_seconds": request.circuit_breaker_reset_timeout_seconds,
        },
    )

    (
        source_id,
        source_kind,
        source_uri,
        route,
        agent_habilitado,
        permitir_fallback_deterministico,
        permitir_fallback_manual,
        retry_attempts,
        timeout_seconds,
        circuit_breaker_failure_threshold,
        circuit_breaker_reset_timeout_seconds,
    ) = _validate_s3_input(request=request)

    route_chain = _build_route_chain(
        route=route,
        source_kind=source_kind,
        permitir_fallback_deterministico=permitir_fallback_deterministico,
        permitir_fallback_manual=permitir_fallback_manual,
    )

    response = S3OrchestratorScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=route,
        plano_execucao={
            "executor_strategy": "agent_first",
            "route_chain": route_chain,
            "retry_attempts": retry_attempts,
            "timeout_seconds": timeout_seconds,
            "agent_habilitado": agent_habilitado,
            "permitir_fallback_deterministico": permitir_fallback_deterministico,
            "permitir_fallback_manual": permitir_fallback_manual,
        },
        circuit_breaker={
            "state": "closed",
            "failure_threshold": circuit_breaker_failure_threshold,
            "consecutive_failures": 0,
            "reset_timeout_seconds": circuit_breaker_reset_timeout_seconds,
        },
        pontos_integracao={
            "orq_s3_prepare_endpoint": BACKEND_ORQ_S3_PREPARE_ENDPOINT,
            "orq_s3_service_module": "app.services.etl_orchestrator_service.execute_s3_orchestrator_service",
            "orq_s3_core_module": "etl.orchestrator.s3_core.execute_s3_orchestrator_main_flow",
            "orq_s3_validation_module": "etl.orchestrator.s3_validation.validate_s3_orchestrator_input_contract",
        },
    )

    logger.info(
        "etl_orchestrator_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "rota_selecionada": route,
            "route_chain_size": len(route_chain),
            "circuit_breaker_failure_threshold": circuit_breaker_failure_threshold,
        },
    )
    return response


def _validate_s3_input(
    *,
    request: S3OrchestratorScaffoldRequest,
) -> tuple[str, str, str, str, bool, bool, bool, int, int, int, int]:
    source_id = _normalize_source_id(request.source_id)

    source_kind = request.source_kind.strip().lower()
    if source_kind not in ALLOWED_SOURCE_KINDS:
        _raise_contract_error(
            code="INVALID_SOURCE_KIND",
            message=f"source_kind invalido: {request.source_kind}",
            action="Use source_kind suportado: pdf, xlsx, csv, pptx, docx ou other.",
        )

    source_uri = request.source_uri.strip()
    if len(source_uri) < 3:
        _raise_contract_error(
            code="INVALID_SOURCE_URI",
            message="source_uri invalido: informe URI/caminho com ao menos 3 caracteres",
            action="Forneca o caminho/URI do artefato para rastreabilidade operacional.",
        )

    route = request.rota_selecionada.strip().lower()
    if route not in ALLOWED_ROUTES:
        _raise_contract_error(
            code="INVALID_ROUTE_SELECTION",
            message=f"rota_selecionada invalida: {request.rota_selecionada}",
            action="Use rota suportada para Sprint 3 (agent-first, agent-* ou manual_assistido_review).",
        )
    _validate_route_vs_source_kind(source_kind=source_kind, route=route)

    if not isinstance(request.agent_habilitado, bool):
        _raise_contract_error(
            code="INVALID_AGENT_HABILITADO_FLAG",
            message="agent_habilitado deve ser booleano",
            action="Ajuste agent_habilitado para true/false.",
        )
    if not request.agent_habilitado and route != "manual_assistido_review":
        _raise_contract_error(
            code="AGENT_DISABLED_REQUIRES_MANUAL_ROUTE",
            message="agent_habilitado=false exige rota manual_assistido_review",
            action="Habilite agent_habilitado ou use rota manual_assistido_review.",
        )

    if not isinstance(request.permitir_fallback_deterministico, bool):
        _raise_contract_error(
            code="INVALID_FALLBACK_DETERMINISTICO_FLAG",
            message="permitir_fallback_deterministico deve ser booleano",
            action="Ajuste permitir_fallback_deterministico para true/false.",
        )

    if not isinstance(request.permitir_fallback_manual, bool):
        _raise_contract_error(
            code="INVALID_FALLBACK_MANUAL_FLAG",
            message="permitir_fallback_manual deve ser booleano",
            action="Ajuste permitir_fallback_manual para true/false.",
        )
    if route == "manual_assistido_review" and not request.permitir_fallback_manual:
        _raise_contract_error(
            code="MANUAL_ROUTE_DISABLED",
            message="manual_assistido_review requer permitir_fallback_manual=true",
            action="Habilite fallback manual para usar a rota manual_assistido_review.",
        )

    if not isinstance(request.retry_attempts, int):
        _raise_contract_error(
            code="INVALID_RETRY_ATTEMPTS_TYPE",
            message="retry_attempts deve ser inteiro",
            action="Ajuste retry_attempts para inteiro entre 0 e 5.",
        )
    retry_attempts = request.retry_attempts
    if retry_attempts < MIN_RETRY_ATTEMPTS or retry_attempts > MAX_RETRY_ATTEMPTS:
        _raise_contract_error(
            code="INVALID_RETRY_ATTEMPTS",
            message=f"retry_attempts fora do intervalo suportado: {retry_attempts}",
            action=f"Use retry_attempts entre {MIN_RETRY_ATTEMPTS} e {MAX_RETRY_ATTEMPTS}.",
        )

    if not isinstance(request.timeout_seconds, int):
        _raise_contract_error(
            code="INVALID_TIMEOUT_SECONDS_TYPE",
            message="timeout_seconds deve ser inteiro",
            action="Ajuste timeout_seconds para inteiro entre 30 e 900.",
        )
    timeout_seconds = request.timeout_seconds
    if timeout_seconds < MIN_TIMEOUT_SECONDS or timeout_seconds > MAX_TIMEOUT_SECONDS:
        _raise_contract_error(
            code="INVALID_TIMEOUT_SECONDS",
            message=f"timeout_seconds fora do intervalo suportado: {timeout_seconds}",
            action=f"Use timeout_seconds entre {MIN_TIMEOUT_SECONDS} e {MAX_TIMEOUT_SECONDS}.",
        )

    if not isinstance(request.circuit_breaker_failure_threshold, int):
        _raise_contract_error(
            code="INVALID_CIRCUIT_BREAKER_FAILURE_THRESHOLD_TYPE",
            message="circuit_breaker_failure_threshold deve ser inteiro",
            action="Ajuste limiar do circuit breaker para inteiro entre 1 e 10.",
        )
    circuit_breaker_failure_threshold = request.circuit_breaker_failure_threshold
    if (
        circuit_breaker_failure_threshold < MIN_CIRCUIT_BREAKER_THRESHOLD
        or circuit_breaker_failure_threshold > MAX_CIRCUIT_BREAKER_THRESHOLD
    ):
        _raise_contract_error(
            code="INVALID_CIRCUIT_BREAKER_FAILURE_THRESHOLD",
            message=(
                "circuit_breaker_failure_threshold fora do intervalo suportado: "
                f"{circuit_breaker_failure_threshold}"
            ),
            action=(
                "Use circuit_breaker_failure_threshold entre "
                f"{MIN_CIRCUIT_BREAKER_THRESHOLD} e {MAX_CIRCUIT_BREAKER_THRESHOLD}."
            ),
        )

    if not isinstance(request.circuit_breaker_reset_timeout_seconds, int):
        _raise_contract_error(
            code="INVALID_CIRCUIT_BREAKER_RESET_TIMEOUT_TYPE",
            message="circuit_breaker_reset_timeout_seconds deve ser inteiro",
            action="Ajuste timeout de reset para inteiro entre 30 e 3600.",
        )
    circuit_breaker_reset_timeout_seconds = request.circuit_breaker_reset_timeout_seconds
    if (
        circuit_breaker_reset_timeout_seconds < MIN_CIRCUIT_RESET_TIMEOUT_SECONDS
        or circuit_breaker_reset_timeout_seconds > MAX_CIRCUIT_RESET_TIMEOUT_SECONDS
    ):
        _raise_contract_error(
            code="INVALID_CIRCUIT_BREAKER_RESET_TIMEOUT",
            message=(
                "circuit_breaker_reset_timeout_seconds fora do intervalo suportado: "
                f"{circuit_breaker_reset_timeout_seconds}"
            ),
            action=(
                "Use circuit_breaker_reset_timeout_seconds entre "
                f"{MIN_CIRCUIT_RESET_TIMEOUT_SECONDS} e {MAX_CIRCUIT_RESET_TIMEOUT_SECONDS}."
            ),
        )

    return (
        source_id,
        source_kind,
        source_uri,
        route,
        request.agent_habilitado,
        request.permitir_fallback_deterministico,
        request.permitir_fallback_manual,
        retry_attempts,
        timeout_seconds,
        circuit_breaker_failure_threshold,
        circuit_breaker_reset_timeout_seconds,
    )


def _build_route_chain(
    *,
    route: str,
    source_kind: str,
    permitir_fallback_deterministico: bool,
    permitir_fallback_manual: bool,
) -> list[str]:
    route_chain: list[str] = []

    if route == "agent_first_extract":
        if source_kind in {"xlsx", "csv"}:
            route_chain.append("agent_tabular_extract")
        elif source_kind == "pdf":
            route_chain.append("agent_pdf_extract")
        else:
            route_chain.append("agent_document_extract")
    else:
        route_chain.append(route)

    if permitir_fallback_deterministico:
        fallback_route = DETERMINISTIC_FALLBACK_BY_KIND[source_kind]
        if fallback_route not in route_chain:
            route_chain.append(fallback_route)

    if permitir_fallback_manual and "manual_assistido_review" not in route_chain:
        route_chain.append("manual_assistido_review")

    return route_chain


def _validate_route_vs_source_kind(*, source_kind: str, route: str) -> None:
    if source_kind in {"xlsx", "csv"} and route == "agent_pdf_extract":
        _raise_contract_error(
            code="INVALID_ROUTE_FOR_SOURCE_KIND",
            message=f"rota '{route}' nao compativel com source_kind '{source_kind}'",
            action="Para fontes tabulares use agent_tabular_extract ou agent_first_extract.",
        )
    if source_kind in {"pdf", "pptx", "docx", "other"} and route == "agent_tabular_extract":
        _raise_contract_error(
            code="INVALID_ROUTE_FOR_SOURCE_KIND",
            message=f"rota '{route}' nao compativel com source_kind '{source_kind}'",
            action="Para documentos use agent_pdf_extract, agent_document_extract ou agent_first_extract.",
        )


def _normalize_source_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not SOURCE_ID_RE.match(normalized):
        _raise_contract_error(
            code="INVALID_SOURCE_ID",
            message="source_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action="Padronize source_id para formato estavel de auditoria (ex: SRC_TMJ_PDF_2025).",
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "etl_orchestrator_s3_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S3OrchestratorScaffoldError(code=code, message=message, action=action)
