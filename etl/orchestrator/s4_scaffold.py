"""Sprint 4 scaffold contracts for telemetry, cost, and latency governance.

This module defines the stable input/output contract used by ORQ Sprint 4 to
prepare decision-telemetry fields and operational controls for cost/latency.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s4")

CONTRACT_VERSION = "orq.s4.v1"
BACKEND_ORQ_S4_PREPARE_ENDPOINT = "/internal/etl/orchestrator/s4/telemetry"
SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")

ALLOWED_SOURCE_KINDS = ("pdf", "xlsx", "csv", "pptx", "docx", "other")
ALLOWED_ROUTES = (
    "deterministic_tabular_extract",
    "deterministic_pdf_extract",
    "ia_assisted_pdf_extract",
    "hybrid_pdf_extract",
    "hybrid_document_extract",
    "agent_first_extract",
    "agent_pdf_extract",
    "agent_tabular_extract",
    "agent_document_extract",
    "manual_assistido_review",
)
MIN_LATENCY_MS = 1
MAX_LATENCY_MS = 600_000
MAX_COST_USD = 10_000.0


class S4OrchestratorScaffoldError(ValueError):
    """Raised when ORQ S4 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4OrchestratorScaffoldRequest:
    """Input contract for ORQ Sprint 4 scaffold validation."""

    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    decisao_telemetria_habilitada: bool = True
    custo_estimado_usd: float = 0.0
    custo_orcamento_usd: float = 1.0
    latencia_estimada_ms: int = 1200
    latencia_sla_ms: int = 4000
    telemetria_amostragem: float = 1.0
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible ORQ Sprint 4 contract."""

        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "rota_selecionada": self.rota_selecionada,
            "decisao_telemetria_habilitada": self.decisao_telemetria_habilitada,
            "custo_estimado_usd": self.custo_estimado_usd,
            "custo_orcamento_usd": self.custo_orcamento_usd,
            "latencia_estimada_ms": self.latencia_estimada_ms,
            "latencia_sla_ms": self.latencia_sla_ms,
            "telemetria_amostragem": self.telemetria_amostragem,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4OrchestratorScaffoldResponse:
    """Output contract returned when ORQ Sprint 4 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    plano_telemetria: dict[str, Any]
    governanca_custo_latencia: dict[str, Any]
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
            "plano_telemetria": self.plano_telemetria,
            "governanca_custo_latencia": self.governanca_custo_latencia,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s4_scaffold_contract(
    request: S4OrchestratorScaffoldRequest,
) -> S4OrchestratorScaffoldResponse:
    """Build ORQ Sprint 4 scaffold contract for telemetry/cost/latency.

    Args:
        request: Orchestrator telemetry input with route, cost, and latency
            controls for Sprint 4.

    Returns:
        S4OrchestratorScaffoldResponse: Stable scaffold output with telemetry
            planning and governance thresholds.

    Raises:
        S4OrchestratorScaffoldError: If one or more ORQ Sprint 4 input rules
            fail.
    """

    correlation_id = request.correlation_id or f"orq-s4-{uuid4().hex[:12]}"
    logger.info(
        "etl_orchestrator_s4_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "source_uri": request.source_uri,
            "rota_selecionada": request.rota_selecionada,
            "decisao_telemetria_habilitada": request.decisao_telemetria_habilitada,
            "custo_estimado_usd": request.custo_estimado_usd,
            "custo_orcamento_usd": request.custo_orcamento_usd,
            "latencia_estimada_ms": request.latencia_estimada_ms,
            "latencia_sla_ms": request.latencia_sla_ms,
            "telemetria_amostragem": request.telemetria_amostragem,
        },
    )

    (
        source_id,
        source_kind,
        source_uri,
        route,
        telemetria_habilitada,
        custo_estimado_usd,
        custo_orcamento_usd,
        latencia_estimada_ms,
        latencia_sla_ms,
        telemetria_amostragem,
    ) = _validate_s4_input(request=request)
    plano_telemetria = _resolve_telemetry_plan(
        route=route,
        telemetria_habilitada=telemetria_habilitada,
        telemetria_amostragem=telemetria_amostragem,
    )
    governanca = _resolve_governance_summary(
        custo_estimado_usd=custo_estimado_usd,
        custo_orcamento_usd=custo_orcamento_usd,
        latencia_estimada_ms=latencia_estimada_ms,
        latencia_sla_ms=latencia_sla_ms,
    )

    response = S4OrchestratorScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=route,
        plano_telemetria=plano_telemetria,
        governanca_custo_latencia=governanca,
        pontos_integracao={
            "orq_s4_prepare_endpoint": BACKEND_ORQ_S4_PREPARE_ENDPOINT,
            "orq_s3_service_module": "app.services.etl_orchestrator_service.execute_s3_orchestrator_service",
            "telemetry_service_module": "app.services.orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry",
            "cost_registry_module": "app.services.etl_registry_service",
            "latency_metrics_module": "app.services.etl_registry_service",
        },
    )
    logger.info(
        "etl_orchestrator_s4_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "rota_selecionada": route,
            "telemetry_enabled": telemetria_habilitada,
            "telemetria_amostragem": telemetria_amostragem,
            "custo_status": governanca.get("custo_status"),
            "latencia_status": governanca.get("latencia_status"),
        },
    )
    return response


def _validate_s4_input(
    *,
    request: S4OrchestratorScaffoldRequest,
) -> tuple[str, str, str, str, bool, float, float, int, int, float]:
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
            action="Use rota suportada para Sprint 4 (deterministica, hibrida, agent-first ou manual).",
        )
    _validate_route_vs_source_kind(source_kind=source_kind, route=route)

    telemetria_habilitada = request.decisao_telemetria_habilitada
    if not isinstance(telemetria_habilitada, bool):
        _raise_contract_error(
            code="INVALID_DECISAO_TELEMETRIA_FLAG",
            message="decisao_telemetria_habilitada deve ser booleano",
            action="Ajuste decisao_telemetria_habilitada para true/false.",
        )

    if not isinstance(request.custo_estimado_usd, (int, float)):
        _raise_contract_error(
            code="INVALID_CUSTO_ESTIMADO_USD_TYPE",
            message="custo_estimado_usd deve ser numerico",
            action="Informe custo_estimado_usd como numero (float).",
        )
    custo_estimado_usd = float(request.custo_estimado_usd)
    if custo_estimado_usd < 0 or custo_estimado_usd > MAX_COST_USD:
        _raise_contract_error(
            code="INVALID_CUSTO_ESTIMADO_USD",
            message=f"custo_estimado_usd fora do intervalo suportado: {custo_estimado_usd}",
            action=f"Use custo_estimado_usd entre 0 e {MAX_COST_USD}.",
        )

    if not isinstance(request.custo_orcamento_usd, (int, float)):
        _raise_contract_error(
            code="INVALID_CUSTO_ORCAMENTO_USD_TYPE",
            message="custo_orcamento_usd deve ser numerico",
            action="Informe custo_orcamento_usd como numero (float).",
        )
    custo_orcamento_usd = float(request.custo_orcamento_usd)
    if custo_orcamento_usd <= 0 or custo_orcamento_usd > MAX_COST_USD:
        _raise_contract_error(
            code="INVALID_CUSTO_ORCAMENTO_USD",
            message=f"custo_orcamento_usd fora do intervalo suportado: {custo_orcamento_usd}",
            action=f"Use custo_orcamento_usd entre 0.01 e {MAX_COST_USD}.",
        )

    if custo_estimado_usd > custo_orcamento_usd:
        _raise_contract_error(
            code="COST_ESTIMATE_EXCEEDS_BUDGET",
            message=(
                "custo_estimado_usd excede custo_orcamento_usd: "
                f"estimado={custo_estimado_usd}, orcamento={custo_orcamento_usd}"
            ),
            action="Ajuste rota/estrategia para reduzir custo ou aumente o orcamento permitido.",
        )

    latencia_estimada_ms = request.latencia_estimada_ms
    if (
        not isinstance(latencia_estimada_ms, int)
        or latencia_estimada_ms < MIN_LATENCY_MS
        or latencia_estimada_ms > MAX_LATENCY_MS
    ):
        _raise_contract_error(
            code="INVALID_LATENCIA_ESTIMADA_MS",
            message=(
                "latencia_estimada_ms invalida: use inteiro entre "
                f"{MIN_LATENCY_MS} e {MAX_LATENCY_MS}"
            ),
            action="Ajuste latencia_estimada_ms para parametro operacional valido.",
        )

    latencia_sla_ms = request.latencia_sla_ms
    if (
        not isinstance(latencia_sla_ms, int)
        or latencia_sla_ms < MIN_LATENCY_MS
        or latencia_sla_ms > MAX_LATENCY_MS
    ):
        _raise_contract_error(
            code="INVALID_LATENCIA_SLA_MS",
            message=(
                "latencia_sla_ms invalida: use inteiro entre "
                f"{MIN_LATENCY_MS} e {MAX_LATENCY_MS}"
            ),
            action="Ajuste latencia_sla_ms para SLA valido da sprint.",
        )

    if not isinstance(request.telemetria_amostragem, (int, float)):
        _raise_contract_error(
            code="INVALID_TELEMETRIA_AMOSTRAGEM_TYPE",
            message="telemetria_amostragem deve ser numerico",
            action="Informe telemetria_amostragem como numero entre 0 e 1.",
        )
    telemetria_amostragem = float(request.telemetria_amostragem)
    if telemetria_amostragem < 0 or telemetria_amostragem > 1:
        _raise_contract_error(
            code="INVALID_TELEMETRIA_AMOSTRAGEM",
            message=f"telemetria_amostragem invalida: {request.telemetria_amostragem}",
            action="Use telemetria_amostragem entre 0 e 1.",
        )
    if telemetria_habilitada and telemetria_amostragem == 0:
        _raise_contract_error(
            code="TELEMETRY_ENABLED_REQUIRES_SAMPLING",
            message="telemetria_amostragem deve ser > 0 quando telemetria esta habilitada",
            action="Defina telemetria_amostragem > 0 ou desabilite telemetria.",
        )
    if not telemetria_habilitada and telemetria_amostragem != 0:
        _raise_contract_error(
            code="TELEMETRY_DISABLED_REQUIRES_ZERO_SAMPLING",
            message="telemetria_amostragem deve ser 0 quando telemetria esta desabilitada",
            action="Defina telemetria_amostragem=0 ou habilite telemetria.",
        )

    return (
        source_id,
        source_kind,
        source_uri,
        route,
        telemetria_habilitada,
        round(custo_estimado_usd, 4),
        round(custo_orcamento_usd, 4),
        latencia_estimada_ms,
        latencia_sla_ms,
        round(telemetria_amostragem, 4),
    )


def _validate_route_vs_source_kind(*, source_kind: str, route: str) -> None:
    allowed_by_kind: dict[str, set[str]] = {
        "pdf": {
            "deterministic_pdf_extract",
            "ia_assisted_pdf_extract",
            "hybrid_pdf_extract",
            "agent_first_extract",
            "agent_pdf_extract",
            "manual_assistido_review",
        },
        "xlsx": {
            "deterministic_tabular_extract",
            "agent_first_extract",
            "agent_tabular_extract",
            "manual_assistido_review",
        },
        "csv": {
            "deterministic_tabular_extract",
            "agent_first_extract",
            "agent_tabular_extract",
            "manual_assistido_review",
        },
        "pptx": {
            "hybrid_document_extract",
            "agent_first_extract",
            "agent_document_extract",
            "manual_assistido_review",
        },
        "docx": {
            "hybrid_document_extract",
            "agent_first_extract",
            "agent_document_extract",
            "manual_assistido_review",
        },
        "other": {"agent_first_extract", "manual_assistido_review"},
    }
    if route not in allowed_by_kind[source_kind]:
        _raise_contract_error(
            code="INVALID_ROUTE_FOR_SOURCE_KIND",
            message=(
                "rota_selecionada incompativel com source_kind: "
                f"source_kind={source_kind}, rota={route}"
            ),
            action="Ajuste rota_selecionada para combinacao suportada na Sprint 4.",
        )


def _resolve_telemetry_plan(
    *,
    route: str,
    telemetria_habilitada: bool,
    telemetria_amostragem: float,
) -> dict[str, Any]:
    return {
        "rota_selecionada": route,
        "decisao_telemetria_habilitada": telemetria_habilitada,
        "telemetria_amostragem": telemetria_amostragem,
        "eventos": {
            "decision_event": "etl_orchestrator_s4_route_decision",
            "cost_event": "etl_orchestrator_s4_cost_tracking",
            "latency_event": "etl_orchestrator_s4_latency_tracking",
        },
        "campos_obrigatorios": [
            "correlation_id",
            "source_id",
            "source_kind",
            "rota_selecionada",
            "route_name",
            "attempt",
            "decision_reason",
            "latencia_ms",
            "custo_usd",
        ],
        "retencao_dias": 30,
    }


def _resolve_governance_summary(
    *,
    custo_estimado_usd: float,
    custo_orcamento_usd: float,
    latencia_estimada_ms: int,
    latencia_sla_ms: int,
) -> dict[str, Any]:
    return {
        "custo_estimado_usd": custo_estimado_usd,
        "custo_orcamento_usd": custo_orcamento_usd,
        "custo_status": "within_budget",
        "latencia_estimada_ms": latencia_estimada_ms,
        "latencia_sla_ms": latencia_sla_ms,
        "latencia_status": "within_sla" if latencia_estimada_ms <= latencia_sla_ms else "above_sla",
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
        "etl_orchestrator_s4_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S4OrchestratorScaffoldError(code=code, message=message, action=action)
