"""Sprint 1 scaffold contracts for hybrid ETL extraction orchestration.

This module defines the stable input/output contract used by the orchestrator
to decide the initial routing policy between deterministic, AI-assisted,
hybrid, and manual fallback extraction paths.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.etl.orchestrator.s1")

CONTRACT_VERSION = "orq.s1.v1"
BACKEND_ORQ_S1_ROUTE_ENDPOINT = "/internal/etl/orchestrator/s1/route"
SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")

ALLOWED_SOURCE_KINDS = ("pdf", "xlsx", "csv", "pptx", "docx", "other")
ALLOWED_PDF_PROFILE_HINTS = (
    "text_table",
    "ocr_or_assisted",
    "hybrid",
    "manual_assisted",
    "empty_document",
)


class S1OrchestratorScaffoldError(ValueError):
    """Raised when ORQ S1 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1OrchestratorRequest:
    """Input contract for ORQ Sprint 1 scaffold validation."""

    source_id: str
    source_kind: str
    source_uri: str
    profile_strategy_hint: str | None = None
    ia_habilitada: bool = True
    permitir_fallback_manual: bool = True
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible ORQ Sprint 1 contract."""

        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "profile_strategy_hint": self.profile_strategy_hint,
            "ia_habilitada": self.ia_habilitada,
            "permitir_fallback_manual": self.permitir_fallback_manual,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S1OrchestratorResponse:
    """Output contract returned when ORQ Sprint 1 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    rota_selecionada: str
    politica_roteamento: dict[str, Any]
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
            "politica_roteamento": self.politica_roteamento,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s1_scaffold_contract(request: S1OrchestratorRequest) -> S1OrchestratorResponse:
    """Build ORQ Sprint 1 scaffold contract and routing policy decision.

    Args:
        request: Orchestrator routing input with source metadata and policy flags.

    Returns:
        S1OrchestratorResponse: Stable scaffold output with selected route and
            integration points.

    Raises:
        S1OrchestratorScaffoldError: If one or more ORQ Sprint 1 input rules fail.
    """

    correlation_id = request.correlation_id or f"orq-s1-{uuid4().hex[:12]}"
    logger.info(
        "etl_orchestrator_s1_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "source_uri": request.source_uri,
            "profile_strategy_hint": request.profile_strategy_hint,
            "ia_habilitada": request.ia_habilitada,
            "permitir_fallback_manual": request.permitir_fallback_manual,
        },
    )

    source_id, source_kind, source_uri, profile_strategy_hint = _validate_s1_input(request=request)
    policy = _resolve_routing_policy(
        source_kind=source_kind,
        profile_strategy_hint=profile_strategy_hint,
        ia_habilitada=request.ia_habilitada,
        permitir_fallback_manual=request.permitir_fallback_manual,
    )

    response = S1OrchestratorResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        source_id=source_id,
        source_kind=source_kind,
        source_uri=source_uri,
        rota_selecionada=policy["rota_selecionada"],
        politica_roteamento=policy,
        pontos_integracao={
            "orq_s1_route_endpoint": BACKEND_ORQ_S1_ROUTE_ENDPOINT,
            "extract_all_cli": "etl.cli_extract.run_extract_all",
            "pdf_classifier_module": "etl.extract.pdf_classify.classify_pdf",
            "pdf_assisted_extractor_module": "etl.extract.extract_pdf_assisted.extract_pdf_assisted",
            "xlsx_optin_extractor_module": "etl.extract.extract_xlsx_optin_aceitos.extract_optin_xlsx",
        },
    )
    logger.info(
        "etl_orchestrator_s1_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "rota_selecionada": response.rota_selecionada,
            "modo_roteamento": response.politica_roteamento.get("modo_roteamento"),
        },
    )
    return response


def _validate_s1_input(*, request: S1OrchestratorRequest) -> tuple[str, str, str, str | None]:
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

    profile_strategy_hint = None
    raw_hint = (request.profile_strategy_hint or "").strip().lower()
    if raw_hint:
        if raw_hint not in ALLOWED_PDF_PROFILE_HINTS:
            _raise_contract_error(
                code="INVALID_PROFILE_STRATEGY_HINT",
                message=f"profile_strategy_hint invalido: {request.profile_strategy_hint}",
                action=(
                    "Use hints aceitos para PDF: text_table, ocr_or_assisted, hybrid, "
                    "manual_assisted ou empty_document."
                ),
            )
        profile_strategy_hint = raw_hint
        if source_kind != "pdf":
            _raise_contract_error(
                code="PROFILE_HINT_NOT_APPLICABLE",
                message=(
                    "profile_strategy_hint so pode ser usado com source_kind=pdf na "
                    "Sprint 1"
                ),
                action="Remova profile_strategy_hint para fontes nao PDF.",
            )

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

    return source_id, source_kind, source_uri, profile_strategy_hint


def _resolve_routing_policy(
    *,
    source_kind: str,
    profile_strategy_hint: str | None,
    ia_habilitada: bool,
    permitir_fallback_manual: bool,
) -> dict[str, Any]:
    if source_kind in {"xlsx", "csv"}:
        return _policy(
            rota_selecionada="deterministic_tabular_extract",
            modo_roteamento="deterministico",
            motivo="Fontes tabulares seguem pipeline deterministico na Sprint 1.",
            profile_strategy_hint=profile_strategy_hint,
            ia_habilitada=ia_habilitada,
            permitir_fallback_manual=permitir_fallback_manual,
            fallback_chain=("manual_assistido_review",) if permitir_fallback_manual else (),
        )

    if source_kind == "pdf":
        hint = profile_strategy_hint or "hybrid"
        if hint == "text_table":
            return _policy(
                rota_selecionada="deterministic_pdf_extract",
                modo_roteamento="deterministico",
                motivo="PDF com predomino textual pode iniciar em extracao deterministica.",
                profile_strategy_hint=hint,
                ia_habilitada=ia_habilitada,
                permitir_fallback_manual=permitir_fallback_manual,
                fallback_chain=("ia_assisted_pdf_extract", "manual_assistido_review")
                if ia_habilitada and permitir_fallback_manual
                else ("ia_assisted_pdf_extract",)
                if ia_habilitada
                else ("manual_assistido_review",)
                if permitir_fallback_manual
                else (),
            )
        if hint in {"ocr_or_assisted", "hybrid"} and ia_habilitada:
            return _policy(
                rota_selecionada="hybrid_pdf_extract" if hint == "hybrid" else "ia_assisted_pdf_extract",
                modo_roteamento="hibrido" if hint == "hybrid" else "ia_assistida",
                motivo="Perfil de PDF requer suporte de IA para reduzir perda de extracao.",
                profile_strategy_hint=hint,
                ia_habilitada=ia_habilitada,
                permitir_fallback_manual=permitir_fallback_manual,
                fallback_chain=("manual_assistido_review",) if permitir_fallback_manual else (),
            )
        if hint in {"manual_assisted", "empty_document"} and permitir_fallback_manual:
            return _policy(
                rota_selecionada="manual_assistido_review",
                modo_roteamento="manual_assistido",
                motivo="PDF sem sinal robusto de extracao automatica exige trilha assistida.",
                profile_strategy_hint=hint,
                ia_habilitada=ia_habilitada,
                permitir_fallback_manual=permitir_fallback_manual,
                fallback_chain=(),
            )

    if source_kind in {"pptx", "docx"} and ia_habilitada:
        return _policy(
            rota_selecionada="hybrid_document_extract",
            modo_roteamento="hibrido",
            motivo="Documento semiestruturado segue rota hibrida por padrao.",
            profile_strategy_hint=profile_strategy_hint,
            ia_habilitada=ia_habilitada,
            permitir_fallback_manual=permitir_fallback_manual,
            fallback_chain=("manual_assistido_review",) if permitir_fallback_manual else (),
        )
    if source_kind in {"pptx", "docx", "other"} and permitir_fallback_manual:
        return _policy(
            rota_selecionada="manual_assistido_review",
            modo_roteamento="manual_assistido",
            motivo="Fonte nao suportada por rota automatica requer fallback manual.",
            profile_strategy_hint=profile_strategy_hint,
            ia_habilitada=ia_habilitada,
            permitir_fallback_manual=permitir_fallback_manual,
            fallback_chain=(),
        )

    _raise_contract_error(
        code="ROUTE_UNAVAILABLE",
        message="Nao existe rota disponivel com a combinacao de flags informada",
        action="Habilite IA ou fallback manual para permitir roteamento seguro da fonte.",
    )
    raise AssertionError("unreachable")


def _policy(
    *,
    rota_selecionada: str,
    modo_roteamento: str,
    motivo: str,
    profile_strategy_hint: str | None,
    ia_habilitada: bool,
    permitir_fallback_manual: bool,
    fallback_chain: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "rota_selecionada": rota_selecionada,
        "modo_roteamento": modo_roteamento,
        "motivo_roteamento": motivo,
        "profile_strategy_hint": profile_strategy_hint,
        "ia_habilitada": ia_habilitada,
        "permitir_fallback_manual": permitir_fallback_manual,
        "fallback_chain": list(fallback_chain),
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
        "etl_orchestrator_s1_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S1OrchestratorScaffoldError(code=code, message=message, action=action)
