"""Sprint 2 scaffold contracts for hybrid ETL extraction orchestration.

This module defines the stable input/output contract used by ORQ Sprint 2 to
prepare execution parameters for the route selected in Sprint 1.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s2")

CONTRACT_VERSION = "orq.s2.v1"
BACKEND_ORQ_S2_PREPARE_ENDPOINT = "/internal/etl/orchestrator/s2/prepare"
SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")

ALLOWED_SOURCE_KINDS = ("pdf", "xlsx", "csv", "pptx", "docx", "other")
ALLOWED_ROUTES = (
    "deterministic_tabular_extract",
    "deterministic_pdf_extract",
    "ia_assisted_pdf_extract",
    "hybrid_pdf_extract",
    "hybrid_document_extract",
    "manual_assistido_review",
)
MAX_RETRY_ATTEMPTS = 3
MIN_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 900


class S2OrchestratorScaffoldError(ValueError):
    """Raised when ORQ S2 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2OrchestratorScaffoldRequest:
    """Input contract for ORQ Sprint 2 scaffold validation."""

    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    ia_habilitada: bool = True
    permitir_fallback_manual: bool = True
    retry_attempts: int = 0
    timeout_seconds: int = 180
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible ORQ Sprint 2 contract."""

        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "ia_habilitada": self.ia_habilitada,
            "permitir_fallback_manual": self.permitir_fallback_manual,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2OrchestratorScaffoldResponse:
    """Output contract returned when ORQ Sprint 2 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_execucao: dict[str, Any]
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
            "pontos_integracao": self.pontos_integracao,
        }


def build_s2_scaffold_contract(
    request: S2OrchestratorScaffoldRequest,
) -> S2OrchestratorScaffoldResponse:
    """Build ORQ Sprint 2 scaffold contract and execution preparation plan.

    Args:
        request: Orchestrator execution input with selected route and runtime
            policy flags.

    Returns:
        S2OrchestratorScaffoldResponse: Stable scaffold output with execution
            plan and integration points for ORQ Sprint 2.

    Raises:
        S2OrchestratorScaffoldError: If one or more ORQ Sprint 2 input rules
            fail.
    """

    correlation_id = request.correlation_id or f"orq-s2-{uuid4().hex[:12]}"
    logger.info(
        "etl_orchestrator_s2_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "source_uri": request.source_uri,
            "rota_selecionada": request.rota_selecionada,
            "ia_habilitada": request.ia_habilitada,
            "permitir_fallback_manual": request.permitir_fallback_manual,
            "retry_attempts": request.retry_attempts,
            "timeout_seconds": request.timeout_seconds,
        },
    )

    source_id, source_kind, source_uri, route, retry_attempts, timeout_seconds = _validate_s2_input(
        request=request
    )
    execution_plan = _resolve_execution_plan(
        source_kind=source_kind,
        route=route,
        ia_habilitada=request.ia_habilitada,
        permitir_fallback_manual=request.permitir_fallback_manual,
        retry_attempts=retry_attempts,
        timeout_seconds=timeout_seconds,
    )

    response = S2OrchestratorScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=route,
        plano_execucao=execution_plan,
        pontos_integracao={
            "orq_s2_prepare_endpoint": BACKEND_ORQ_S2_PREPARE_ENDPOINT,
            "orq_s1_route_endpoint": "/internal/etl/orchestrator/s1/route",
            "route_executor_module": "etl.orchestrator.route_executor.dispatch_route",
            "registry_module": "app.services.etl_registry_service",
        },
    )
    logger.info(
        "etl_orchestrator_s2_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "rota_selecionada": route,
            "executor_strategy": response.plano_execucao.get("executor_strategy"),
            "queue_name": response.plano_execucao.get("queue_name"),
        },
    )
    return response


def _validate_s2_input(
    *,
    request: S2OrchestratorScaffoldRequest,
) -> tuple[str, str, str, str, int, int]:
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

    route = request.rota_selecionada.strip()
    if route not in ALLOWED_ROUTES:
        _raise_contract_error(
            code="INVALID_ROUTE_SELECTION",
            message=f"rota_selecionada invalida: {request.rota_selecionada}",
            action=(
                "Use rota suportada: deterministic_tabular_extract, deterministic_pdf_extract, "
                "ia_assisted_pdf_extract, hybrid_pdf_extract, hybrid_document_extract "
                "ou manual_assistido_review."
            ),
        )
    _validate_route_vs_source_kind(source_kind=source_kind, route=route)

    if not isinstance(request.ia_habilitada, bool):
        _raise_contract_error(
            code="INVALID_IA_HABILITADA_FLAG",
            message="ia_habilitada deve ser booleano",
            action="Ajuste ia_habilitada para true/false.",
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
            action="Ajuste retry_attempts para a politica operacional da Sprint 2.",
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
            action="Ajuste timeout_seconds para limites operacionais do ORQ S2.",
        )

    return source_id, source_kind, source_uri, route, retry_attempts, timeout_seconds


def _validate_route_vs_source_kind(*, source_kind: str, route: str) -> None:
    allowed_by_kind: dict[str, set[str]] = {
        "pdf": {
            "deterministic_pdf_extract",
            "ia_assisted_pdf_extract",
            "hybrid_pdf_extract",
            "manual_assistido_review",
        },
        "xlsx": {"deterministic_tabular_extract", "manual_assistido_review"},
        "csv": {"deterministic_tabular_extract", "manual_assistido_review"},
        "pptx": {"hybrid_document_extract", "manual_assistido_review"},
        "docx": {"hybrid_document_extract", "manual_assistido_review"},
        "other": {"manual_assistido_review"},
    }
    if route not in allowed_by_kind[source_kind]:
        _raise_contract_error(
            code="INVALID_ROUTE_FOR_SOURCE_KIND",
            message=(
                "rota_selecionada incompativel com source_kind: "
                f"source_kind={source_kind}, rota={route}"
            ),
            action="Ajuste rota_selecionada para combinacao suportada na Sprint 2.",
        )


def _resolve_execution_plan(
    *,
    source_kind: str,
    route: str,
    ia_habilitada: bool,
    permitir_fallback_manual: bool,
    retry_attempts: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    executor_map = {
        "deterministic_tabular_extract": (
            "deterministico",
            "etl.extract.extract_xlsx_optin_aceitos",
            "extract_optin_xlsx",
            "orq_s2_deterministic",
        ),
        "deterministic_pdf_extract": (
            "deterministico",
            "etl.extract.extract_pdf_assisted",
            "extract_pdf_assisted",
            "orq_s2_deterministic_pdf",
        ),
        "ia_assisted_pdf_extract": (
            "ia_assistida",
            "etl.extract.extract_pdf_assisted",
            "extract_pdf_assisted",
            "orq_s2_ai_assisted",
        ),
        "hybrid_pdf_extract": (
            "hibrido",
            "etl.orchestrator.route_executor",
            "dispatch_route",
            "orq_s2_hybrid_pdf",
        ),
        "hybrid_document_extract": (
            "hibrido",
            "etl.orchestrator.route_executor",
            "dispatch_route",
            "orq_s2_hybrid_document",
        ),
        "manual_assistido_review": (
            "manual_assistido",
            "etl.orchestrator.route_executor",
            "dispatch_route",
            "orq_s2_manual",
        ),
    }
    executor_strategy, executor_module, executor_entrypoint, queue_name = executor_map[route]
    fallback_chain: list[str] = []
    if route != "manual_assistido_review":
        if ia_habilitada and route != "ia_assisted_pdf_extract":
            fallback_chain.append("ia_assisted_pdf_extract")
        if permitir_fallback_manual:
            fallback_chain.append("manual_assistido_review")

    return {
        "rota_selecionada": route,
        "source_kind": source_kind,
        "executor_strategy": executor_strategy,
        "executor_module": executor_module,
        "executor_entrypoint": executor_entrypoint,
        "queue_name": queue_name,
        "timeout_seconds": timeout_seconds,
        "retry_policy": {
            "max_attempts": retry_attempts + 1,
            "current_retry_attempts": retry_attempts,
            "max_retry_attempts": MAX_RETRY_ATTEMPTS,
        },
        "ia_habilitada": ia_habilitada,
        "permitir_fallback_manual": permitir_fallback_manual,
        "fallback_chain": fallback_chain,
    }


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
        "etl_orchestrator_s2_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S2OrchestratorScaffoldError(code=code, message=message, action=action)
