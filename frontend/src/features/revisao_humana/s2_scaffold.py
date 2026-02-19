"""Sprint 2 scaffold contracts for missing-field correspondence workbench.

This module defines the stable input/output contract for WORK Sprint 2,
preparing correspondence policies for non-found fields with actionable
diagnostics and operational integration points.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.frontend.revisao_humana.s2")

CONTRACT_VERSION = "work.s2.v1"
BACKEND_WORK_S2_PREPARE_ENDPOINT = "/internal/revisao-humana/s2/prepare"

WORKFLOW_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
FIELD_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")
ROLE_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")

ALLOWED_ENTITY_KINDS = ("lead", "evento", "ingresso", "generic")
ALLOWED_CANDIDATE_SOURCES = ("crm", "formulario", "ocr", "evento", "api", "manual", "enriquecimento")
ALLOWED_CORRESPONDENCE_MODES = ("manual_confirm", "suggest_only", "semi_auto")
ALLOWED_MATCH_STRATEGIES = ("exact", "normalized", "fuzzy", "semantic")

MIN_MAX_SUGGESTIONS_PER_FIELD = 1
MAX_MAX_SUGGESTIONS_PER_FIELD = 50
MIN_PROBABILITY = 0.0
MAX_PROBABILITY = 1.0

DEFAULT_MISSING_FIELDS_BY_ENTITY_KIND: dict[str, tuple[str, ...]] = {
    "lead": ("nome", "email", "telefone"),
    "evento": ("nome_evento", "data_evento", "local_evento"),
    "ingresso": ("evento_id", "numero_ingresso", "titular_documento"),
    "generic": ("record_id",),
}
DEFAULT_CANDIDATE_SOURCES = ("crm", "formulario", "ocr")
DEFAULT_REVIEWER_ROLES = ("operador", "supervisor")


class S2WorkbenchScaffoldError(ValueError):
    """Raised when WORK S2 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2WorkbenchScaffoldRequest:
    """Input contract for WORK Sprint 2 scaffold validation."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v2"
    owner_team: str = "etl"
    missing_fields: tuple[str, ...] | None = None
    candidate_sources: tuple[str, ...] | None = None
    correspondence_mode: str = "manual_confirm"
    match_strategy: str = "fuzzy"
    min_similarity_score: float = 0.70
    auto_apply_threshold: float = 0.95
    max_suggestions_per_field: int = 5
    require_evidence_for_suggestion: bool = True
    reviewer_roles: tuple[str, ...] | None = None
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible WORK Sprint 2 contract."""

        return {
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "owner_team": self.owner_team,
            "missing_fields": list(self.missing_fields or ()),
            "candidate_sources": list(self.candidate_sources or ()),
            "correspondence_mode": self.correspondence_mode,
            "match_strategy": self.match_strategy,
            "min_similarity_score": self.min_similarity_score,
            "auto_apply_threshold": self.auto_apply_threshold,
            "max_suggestions_per_field": self.max_suggestions_per_field,
            "require_evidence_for_suggestion": self.require_evidence_for_suggestion,
            "reviewer_roles": list(self.reviewer_roles or ()),
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2WorkbenchScaffoldResponse:
    """Output contract returned when WORK Sprint 2 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    correspondence_policy: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "correspondence_policy": self.correspondence_policy,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s2_workbench_scaffold(
    request: S2WorkbenchScaffoldRequest,
) -> S2WorkbenchScaffoldResponse:
    """Build WORK Sprint 2 scaffold contract for missing-field correspondence.

    Args:
        request: Workbench metadata and correspondence policy guardrails used
            by Sprint 2.

    Returns:
        S2WorkbenchScaffoldResponse: Stable scaffold output with correspondence
            policy and integration points.

    Raises:
        S2WorkbenchScaffoldError: If one or more WORK Sprint 2 input rules fail.
    """

    correlation_id = request.correlation_id or f"work-s2-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s2_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": request.workflow_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "correspondence_mode": request.correspondence_mode,
            "match_strategy": request.match_strategy,
            "max_suggestions_per_field": request.max_suggestions_per_field,
        },
    )

    (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        missing_fields,
        candidate_sources,
        correspondence_mode,
        match_strategy,
        min_similarity_score,
        auto_apply_threshold,
        max_suggestions_per_field,
        require_evidence_for_suggestion,
        reviewer_roles,
    ) = _validate_s2_input(request=request)

    correspondence_policy = {
        "workflow_id": workflow_id,
        "dataset_name": dataset_name,
        "entity_kind": entity_kind,
        "schema_version": schema_version,
        "owner_team": owner_team,
        "page_scope": "correspondencia_campos_nao_encontrados",
        "queue_key": f"{workflow_id}:{dataset_name}:{entity_kind}:s2",
        "missing_fields": missing_fields,
        "missing_fields_count": len(missing_fields),
        "candidate_sources": candidate_sources,
        "candidate_sources_count": len(candidate_sources),
        "correspondence_mode": correspondence_mode,
        "match_strategy": match_strategy,
        "min_similarity_score": min_similarity_score,
        "auto_apply_threshold": auto_apply_threshold,
        "max_suggestions_per_field": max_suggestions_per_field,
        "require_evidence_for_suggestion": require_evidence_for_suggestion,
        "reviewer_roles": reviewer_roles,
        "reviewer_roles_count": len(reviewer_roles),
    }

    response = S2WorkbenchScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        workflow_id=workflow_id,
        dataset_name=dataset_name,
        correspondence_policy=correspondence_policy,
        pontos_integracao={
            "work_s2_prepare_endpoint": BACKEND_WORK_S2_PREPARE_ENDPOINT,
            "workbench_revisao_router_module": "app.routers.revisao_humana.prepare_workbench_revisao_s2",
            "workbench_revisao_s2_core_module": (
                "frontend.src.features.revisao_humana.s2_core.execute_workbench_revisao_s2_main_flow"
            ),
            "workbench_revisao_s2_validation_module": (
                "frontend.src.features.revisao_humana.s2_validation.validate_workbench_revisao_s2_output_contract"
            ),
        },
    )
    logger.info(
        "workbench_revisao_s2_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "dataset_name": dataset_name,
            "entity_kind": entity_kind,
            "missing_fields_count": len(missing_fields),
            "candidate_sources_count": len(candidate_sources),
            "match_strategy": match_strategy,
        },
    )
    return response


def _validate_s2_input(
    *,
    request: S2WorkbenchScaffoldRequest,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
    tuple[str, ...],
    tuple[str, ...],
    str,
    str,
    float,
    float,
    int,
    bool,
    tuple[str, ...],
]:
    workflow_id = _normalize_workflow_id(request.workflow_id)

    dataset_name = request.dataset_name.strip()
    if len(dataset_name) < 3:
        _raise_workbench_error(
            code="INVALID_DATASET_NAME",
            message="dataset_name invalido: informe nome com ao menos 3 caracteres",
            action="Defina dataset_name estavel para rastreabilidade da correspondencia de campos.",
        )

    entity_kind = request.entity_kind.strip().lower()
    if entity_kind not in ALLOWED_ENTITY_KINDS:
        _raise_workbench_error(
            code="INVALID_ENTITY_KIND",
            message=f"entity_kind invalido: {request.entity_kind}",
            action="Use entity_kind suportado: lead, evento, ingresso ou generic.",
        )

    schema_version = request.schema_version.strip().lower()
    if not SCHEMA_VERSION_RE.match(schema_version):
        _raise_workbench_error(
            code="INVALID_SCHEMA_VERSION",
            message=f"schema_version invalida: {request.schema_version}",
            action="Use schema_version no formato vN (ex: v2).",
        )

    owner_team = request.owner_team.strip().lower()
    if len(owner_team) < 2:
        _raise_workbench_error(
            code="INVALID_OWNER_TEAM",
            message="owner_team invalido: informe identificador com ao menos 2 caracteres",
            action="Defina owner_team para ownership operacional da sprint.",
        )

    missing_fields = _normalize_missing_fields(
        raw_missing_fields=request.missing_fields,
        entity_kind=entity_kind,
    )
    candidate_sources = _normalize_candidate_sources(request.candidate_sources)
    reviewer_roles = _normalize_reviewer_roles(request.reviewer_roles)

    correspondence_mode = request.correspondence_mode.strip().lower()
    if correspondence_mode not in ALLOWED_CORRESPONDENCE_MODES:
        _raise_workbench_error(
            code="INVALID_CORRESPONDENCE_MODE",
            message=f"correspondence_mode invalido: {request.correspondence_mode}",
            action="Use modo suportado: manual_confirm, suggest_only ou semi_auto.",
        )

    match_strategy = request.match_strategy.strip().lower()
    if match_strategy not in ALLOWED_MATCH_STRATEGIES:
        _raise_workbench_error(
            code="INVALID_MATCH_STRATEGY",
            message=f"match_strategy invalida: {request.match_strategy}",
            action="Use estrategia suportada: exact, normalized, fuzzy ou semantic.",
        )

    min_similarity_score = _validate_probability(
        field_name="min_similarity_score",
        value=request.min_similarity_score,
    )
    auto_apply_threshold = _validate_probability(
        field_name="auto_apply_threshold",
        value=request.auto_apply_threshold,
    )
    if auto_apply_threshold < min_similarity_score:
        _raise_workbench_error(
            code="INVALID_CORRESPONDENCE_THRESHOLDS",
            message=(
                "limiares invalidos: auto_apply_threshold deve ser maior ou igual "
                "a min_similarity_score"
            ),
            action="Ajuste limiares para manter min_similarity_score <= auto_apply_threshold.",
        )

    if (
        isinstance(request.max_suggestions_per_field, bool)
        or not isinstance(request.max_suggestions_per_field, int)
    ):
        _raise_workbench_error(
            code="INVALID_MAX_SUGGESTIONS_PER_FIELD_TYPE",
            message="max_suggestions_per_field deve ser inteiro",
            action=(
                "Ajuste max_suggestions_per_field para inteiro no intervalo "
                f"{MIN_MAX_SUGGESTIONS_PER_FIELD}..{MAX_MAX_SUGGESTIONS_PER_FIELD}."
            ),
        )
    max_suggestions_per_field = request.max_suggestions_per_field
    if (
        max_suggestions_per_field < MIN_MAX_SUGGESTIONS_PER_FIELD
        or max_suggestions_per_field > MAX_MAX_SUGGESTIONS_PER_FIELD
    ):
        _raise_workbench_error(
            code="INVALID_MAX_SUGGESTIONS_PER_FIELD",
            message=(
                "max_suggestions_per_field fora do intervalo suportado: "
                f"{request.max_suggestions_per_field}"
            ),
            action=(
                "Use max_suggestions_per_field entre "
                f"{MIN_MAX_SUGGESTIONS_PER_FIELD} e {MAX_MAX_SUGGESTIONS_PER_FIELD}."
            ),
        )

    if not isinstance(request.require_evidence_for_suggestion, bool):
        _raise_workbench_error(
            code="INVALID_REQUIRE_EVIDENCE_FOR_SUGGESTION_FLAG",
            message="require_evidence_for_suggestion deve ser booleano",
            action="Ajuste require_evidence_for_suggestion para true/false.",
        )

    return (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        missing_fields,
        candidate_sources,
        correspondence_mode,
        match_strategy,
        min_similarity_score,
        auto_apply_threshold,
        max_suggestions_per_field,
        request.require_evidence_for_suggestion,
        reviewer_roles,
    )


def _normalize_workflow_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not WORKFLOW_ID_RE.match(normalized):
        _raise_workbench_error(
            code="INVALID_WORKFLOW_ID",
            message="workflow_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action="Padronize workflow_id para formato estavel (ex: WORK_CORRESPONDENCIA_V2).",
        )
    return normalized


def _normalize_missing_fields(
    *,
    raw_missing_fields: tuple[str, ...] | None,
    entity_kind: str,
) -> tuple[str, ...]:
    raw_fields = raw_missing_fields or DEFAULT_MISSING_FIELDS_BY_ENTITY_KIND[entity_kind]
    if not isinstance(raw_fields, tuple):
        _raise_workbench_error(
            code="INVALID_MISSING_FIELDS_TYPE",
            message="missing_fields deve ser tupla de nomes de campos",
            action="Informe missing_fields como tuple[str, ...] contendo campos nao encontrados.",
        )

    normalized: list[str] = []
    for field in raw_fields:
        name = (field or "").strip().lower()
        if not FIELD_NAME_RE.match(name):
            _raise_workbench_error(
                code="INVALID_MISSING_FIELD_NAME",
                message=f"missing_field invalido: {field}",
                action="Use nomes de campos com letras, numeros e underscore.",
            )
        if name not in normalized:
            normalized.append(name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_MISSING_FIELDS",
            message="missing_fields nao pode ser vazio",
            action="Informe ao menos um campo para correspondencia da sprint.",
        )
    return tuple(normalized)


def _normalize_candidate_sources(raw_sources: tuple[str, ...] | None) -> tuple[str, ...]:
    sources = raw_sources or DEFAULT_CANDIDATE_SOURCES
    if not isinstance(sources, tuple):
        _raise_workbench_error(
            code="INVALID_CANDIDATE_SOURCES_TYPE",
            message="candidate_sources deve ser tupla de fontes",
            action="Informe candidate_sources como tuple[str, ...].",
        )

    normalized: list[str] = []
    for source in sources:
        source_name = (source or "").strip().lower()
        if source_name not in ALLOWED_CANDIDATE_SOURCES:
            _raise_workbench_error(
                code="INVALID_CANDIDATE_SOURCE",
                message=f"candidate_source invalida: {source}",
                action=(
                    "Use fonte suportada: crm, formulario, ocr, evento, api, manual "
                    "ou enriquecimento."
                ),
            )
        if source_name not in normalized:
            normalized.append(source_name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_CANDIDATE_SOURCES",
            message="candidate_sources nao pode ser vazio",
            action="Informe ao menos uma fonte candidata para correspondencia.",
        )
    return tuple(normalized)


def _normalize_reviewer_roles(raw_roles: tuple[str, ...] | None) -> tuple[str, ...]:
    roles = raw_roles or DEFAULT_REVIEWER_ROLES
    if not isinstance(roles, tuple):
        _raise_workbench_error(
            code="INVALID_REVIEWER_ROLES_TYPE",
            message="reviewer_roles deve ser tupla de papeis",
            action="Informe reviewer_roles como tuple[str, ...].",
        )

    normalized: list[str] = []
    for role in roles:
        role_name = (role or "").strip().lower()
        if not ROLE_NAME_RE.match(role_name):
            _raise_workbench_error(
                code="INVALID_REVIEWER_ROLE",
                message=f"reviewer_role invalido: {role}",
                action="Use papeis com letras, numeros e underscore.",
            )
        if role_name not in normalized:
            normalized.append(role_name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_REVIEWER_ROLES",
            message="reviewer_roles nao pode ser vazio",
            action="Informe ao menos um papel de revisor para aprovacao da correspondencia.",
        )
    return tuple(normalized)


def _validate_probability(*, field_name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _raise_workbench_error(
            code=f"INVALID_{field_name.upper()}_TYPE",
            message=f"{field_name} deve ser numerico",
            action=f"Informe {field_name} como numero entre 0.0 e 1.0.",
        )
    probability = float(value)
    if probability < MIN_PROBABILITY or probability > MAX_PROBABILITY:
        _raise_workbench_error(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} fora do intervalo suportado: {value}",
            action=f"Use {field_name} no intervalo de 0.0 a 1.0.",
        )
    return round(probability, 6)


def _raise_workbench_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "workbench_revisao_s2_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S2WorkbenchScaffoldError(code=code, message=message, action=action)

