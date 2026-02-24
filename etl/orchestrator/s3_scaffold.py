"""Sprint 3 scaffold contracts for agent-first orchestration.

This module defines the stable input/output contract used by ORQ Sprint 3 to
prepare an agent-first execution plan with retries and circuit breaker policy.
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
MAX_RETRY_ATTEMPTS = 5
MIN_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 900
MIN_CIRCUIT_BREAKER_FAILURE_THRESHOLD = 1
MAX_CIRCUIT_BREAKER_FAILURE_THRESHOLD = 10
MIN_CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS = 30
MAX_CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS = 3600


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
    """Build ORQ Sprint 3 scaffold contract and execution preparation plan.

    Args:
        request: Orchestrator execution input with selected route, retry, and
            circuit breaker policy flags.

    Returns:
        S3OrchestratorScaffoldResponse: Stable scaffold output with execution
            plan and integration points for ORQ Sprint 3.

    Raises:
        S3OrchestratorScaffoldError: If one or more ORQ Sprint 3 input rules
            fail.
    """

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
        retry_attempts,
        timeout_seconds,
        failure_threshold,
        reset_timeout_seconds,
    ) = _validate_s3_input(request=request)
    execution_plan = _resolve_execution_plan(
        source_kind=source_kind,
        route=route,
        agent_habilitado=request.agent_habilitado,
        permitir_fallback_deterministico=request.permitir_fallback_deterministico,
        permitir_fallback_manual=request.permitir_fallback_manual,
        retry_attempts=retry_attempts,
        timeout_seconds=timeout_seconds,
        failure_threshold=failure_threshold,
        reset_timeout_seconds=reset_timeout_seconds,
    )
    circuit_breaker = dict(execution_plan["circuit_breaker"])

    response = S3OrchestratorScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=route,
        plano_execucao=execution_plan,
        circuit_breaker=circuit_breaker,
        pontos_integracao={
            "orq_s3_prepare_endpoint": BACKEND_ORQ_S3_PREPARE_ENDPOINT,
            "orq_s2_prepare_endpoint": "/internal/etl/orchestrator/s2/prepare",
            "route_executor_module": "etl.orchestrator.route_executor.dispatch_route",
            "registry_module": "app.services.etl_registry_service",
            "circuit_breaker_state_module": "app.services.etl_registry_service",
        },
    )
    logger.info(
        "etl_orchestrator_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "rota_selecionada": route,
            "executor_strategy": response.plano_execucao.get("executor_strategy"),
            "queue_name": response.plano_execucao.get("queue_name"),
            "fallback_chain_size": len(response.plano_execucao.get("fallback_chain", [])),
            "circuit_breaker_threshold": failure_threshold,
        },
    )
    return response


def _validate_s3_input(
    *,
    request: S3OrchestratorScaffoldRequest,
) -> tuple[str, str, str, str, int, int, int, int]:
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
            action=(
                "Use rota suportada: agent_first_extract, agent_pdf_extract, "
                "agent_tabular_extract, agent_document_extract ou manual_assistido_review."
            ),
        )
    _validate_route_vs_source_kind(source_kind=source_kind, route=route)

    if not isinstance(request.agent_habilitado, bool):
        _raise_contract_error(
            code="INVALID_AGENT_HABILITADO_FLAG",
            message="agent_habilitado deve ser booleano",
            action="Ajuste agent_habilitado para true/false.",
        )
    if route.startswith("agent_") and not request.agent_habilitado:
        _raise_contract_error(
            code="AGENT_ROUTE_REQUIRES_AGENT_ENABLED",
            message="rota agent-first exige agent_habilitado=true",
            action="Habilite agent_habilitado ou selecione rota manual_assistido_review.",
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

    retry_attempts = request.retry_attempts
    if not isinstance(retry_attempts, int) or retry_attempts < 0 or retry_attempts > MAX_RETRY_ATTEMPTS:
        _raise_contract_error(
            code="INVALID_RETRY_ATTEMPTS",
            message=(
                "retry_attempts invalido: use inteiro entre 0 e "
                f"{MAX_RETRY_ATTEMPTS}"
            ),
            action="Ajuste retry_attempts para a politica operacional da Sprint 3.",
        )

    timeout_seconds = request.timeout_seconds
    if (
        not isinstance(timeout_seconds, int)
        or timeout_seconds < MIN_TIMEOUT_SECONDS
        or timeout_seconds > MAX_TIMEOUT_SECONDS
    ):
        _raise_contract_error(
            code="INVALID_TIMEOUT_SECONDS",
            message=(
                "timeout_seconds invalido: use inteiro entre "
                f"{MIN_TIMEOUT_SECONDS} e {MAX_TIMEOUT_SECONDS}"
            ),
            action="Ajuste timeout_seconds para limites operacionais do ORQ S3.",
        )

    failure_threshold = request.circuit_breaker_failure_threshold
    if (
        not isinstance(failure_threshold, int)
        or failure_threshold < MIN_CIRCUIT_BREAKER_FAILURE_THRESHOLD
        or failure_threshold > MAX_CIRCUIT_BREAKER_FAILURE_THRESHOLD
    ):
        _raise_contract_error(
            code="INVALID_CIRCUIT_BREAKER_FAILURE_THRESHOLD",
            message=(
                "circuit_breaker_failure_threshold invalido: use inteiro entre "
                f"{MIN_CIRCUIT_BREAKER_FAILURE_THRESHOLD} e "
                f"{MAX_CIRCUIT_BREAKER_FAILURE_THRESHOLD}"
            ),
            action="Ajuste limiar do circuit breaker para a politica da Sprint 3.",
        )

    reset_timeout_seconds = request.circuit_breaker_reset_timeout_seconds
    if (
        not isinstance(reset_timeout_seconds, int)
        or reset_timeout_seconds < MIN_CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS
        or reset_timeout_seconds > MAX_CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS
    ):
        _raise_contract_error(
            code="INVALID_CIRCUIT_BREAKER_RESET_TIMEOUT",
            message=(
                "circuit_breaker_reset_timeout_seconds invalido: use inteiro entre "
                f"{MIN_CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS} e "
                f"{MAX_CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS}"
            ),
            action="Ajuste janela de reset do circuit breaker para operacao do ORQ S3.",
        )

    return (
        source_id,
        source_kind,
        source_uri,
        route,
        retry_attempts,
        timeout_seconds,
        failure_threshold,
        reset_timeout_seconds,
    )


def _validate_route_vs_source_kind(*, source_kind: str, route: str) -> None:
    allowed_by_kind: dict[str, set[str]] = {
        "pdf": {"agent_first_extract", "agent_pdf_extract", "manual_assistido_review"},
        "xlsx": {"agent_first_extract", "agent_tabular_extract", "manual_assistido_review"},
        "csv": {"agent_first_extract", "agent_tabular_extract", "manual_assistido_review"},
        "pptx": {"agent_first_extract", "agent_document_extract", "manual_assistido_review"},
        "docx": {"agent_first_extract", "agent_document_extract", "manual_assistido_review"},
        "other": {"agent_first_extract", "manual_assistido_review"},
    }
    if route not in allowed_by_kind[source_kind]:
        _raise_contract_error(
            code="INVALID_ROUTE_FOR_SOURCE_KIND",
            message=(
                "rota_selecionada incompativel com source_kind: "
                f"source_kind={source_kind}, rota={route}"
            ),
            action="Ajuste rota_selecionada para combinacao suportada na Sprint 3.",
        )


def _resolve_execution_plan(
    *,
    source_kind: str,
    route: str,
    agent_habilitado: bool,
    permitir_fallback_deterministico: bool,
    permitir_fallback_manual: bool,
    retry_attempts: int,
    timeout_seconds: int,
    failure_threshold: int,
    reset_timeout_seconds: int,
) -> dict[str, Any]:
    queue_by_kind = {
        "pdf": "orq_s3_agent_pdf",
        "xlsx": "orq_s3_agent_tabular",
        "csv": "orq_s3_agent_tabular",
        "pptx": "orq_s3_agent_document",
        "docx": "orq_s3_agent_document",
        "other": "orq_s3_agent_generic",
    }
    fallback_deterministic_route_by_kind = {
        "pdf": "deterministic_pdf_extract",
        "xlsx": "deterministic_tabular_extract",
        "csv": "deterministic_tabular_extract",
        "pptx": "hybrid_document_extract",
        "docx": "hybrid_document_extract",
        "other": None,
    }
    fallback_chain: list[str] = []
    deterministic_fallback_route = fallback_deterministic_route_by_kind[source_kind]
    if (
        route != "manual_assistido_review"
        and permitir_fallback_deterministico
        and deterministic_fallback_route
        and deterministic_fallback_route != route
    ):
        fallback_chain.append(deterministic_fallback_route)
    if route != "manual_assistido_review" and permitir_fallback_manual:
        fallback_chain.append("manual_assistido_review")

    return {
        "rota_selecionada": route,
        "source_kind": source_kind,
        "executor_strategy": "agent_first",
        "executor_module": "etl.orchestrator.route_executor",
        "executor_entrypoint": "dispatch_route",
        "agent_profile": _resolve_agent_profile(source_kind=source_kind, route=route),
        "queue_name": queue_by_kind[source_kind],
        "timeout_seconds": timeout_seconds,
        "retry_policy": {
            "max_attempts": retry_attempts + 1,
            "current_retry_attempts": retry_attempts,
            "max_retry_attempts": MAX_RETRY_ATTEMPTS,
            "backoff_seconds": [1, 3, 5],
        },
        "agent_habilitado": agent_habilitado,
        "permitir_fallback_deterministico": permitir_fallback_deterministico,
        "permitir_fallback_manual": permitir_fallback_manual,
        "fallback_chain": fallback_chain,
        "circuit_breaker": {
            "failure_threshold": failure_threshold,
            "reset_timeout_seconds": reset_timeout_seconds,
            "state_store_key": "orq_s3_circuit_breaker",
            "half_open_max_calls": 1,
        },
    }


def _resolve_agent_profile(*, source_kind: str, route: str) -> str:
    if route == "agent_pdf_extract":
        return "pdf_reasoning"
    if route == "agent_tabular_extract":
        return "tabular_reasoning"
    if route == "agent_document_extract":
        return "document_reasoning"
    profile_by_kind = {
        "pdf": "pdf_reasoning",
        "xlsx": "tabular_reasoning",
        "csv": "tabular_reasoning",
        "pptx": "document_reasoning",
        "docx": "document_reasoning",
        "other": "generic_reasoning",
    }
    return profile_by_kind[source_kind]


def _normalize_source_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not SOURCE_ID_RE.match(normalized):
        _raise_contract_error(
            code="INVALID_SOURCE_ID",
            message="source_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action="Padronize source_id para formato estavel de auditoria (ex: SRC_PDF_TMJ_2025).",
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
