"""Sprint 1 scaffold contracts for human-review workbench queue policy.

This module defines the stable input/output contract for WORK Sprint 1,
preparing a field-level review queue with evidence sources and operational
guardrails.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.frontend.revisao_humana.s1")

CONTRACT_VERSION = "work.s1.v1"
BACKEND_WORK_S1_PREPARE_ENDPOINT = "/internal/revisao-humana/s1/prepare"

WORKFLOW_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
FIELD_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")
ROLE_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")

ALLOWED_ENTITY_KINDS = ("lead", "evento", "ingresso", "generic")
ALLOWED_PRIORITIES = ("baixa", "media", "alta", "critica")
ALLOWED_EVIDENCE_SOURCES = ("crm", "formulario", "ocr", "evento", "api", "manual", "enriquecimento")

MIN_SLA_HOURS = 1
MAX_SLA_HOURS = 720
MIN_QUEUE_SIZE = 1
MAX_QUEUE_SIZE = 100000

DEFAULT_REQUIRED_FIELDS_BY_ENTITY_KIND: dict[str, tuple[str, ...]] = {
    "lead": ("nome", "email", "telefone"),
    "evento": ("nome_evento", "data_evento", "local_evento"),
    "ingresso": ("evento_id", "numero_ingresso", "titular_documento"),
    "generic": ("record_id",),
}
DEFAULT_EVIDENCE_SOURCES = ("crm", "formulario")
DEFAULT_REVIEWER_ROLES = ("operador", "supervisor")


class S1WorkbenchScaffoldError(ValueError):
    """Raised when WORK S1 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1WorkbenchScaffoldRequest:
    """Input contract for WORK Sprint 1 scaffold validation."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v1"
    owner_team: str = "etl"
    required_fields: tuple[str, ...] | None = None
    evidence_sources: tuple[str, ...] | None = None
    default_priority: str = "media"
    sla_hours: int = 24
    max_queue_size: int = 1000
    auto_assignment_enabled: bool = True
    reviewer_roles: tuple[str, ...] | None = None
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible WORK Sprint 1 contract."""

        return {
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "owner_team": self.owner_team,
            "required_fields": list(self.required_fields or ()),
            "evidence_sources": list(self.evidence_sources or ()),
            "default_priority": self.default_priority,
            "sla_hours": self.sla_hours,
            "max_queue_size": self.max_queue_size,
            "auto_assignment_enabled": self.auto_assignment_enabled,
            "reviewer_roles": list(self.reviewer_roles or ()),
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S1WorkbenchScaffoldResponse:
    """Output contract returned when WORK Sprint 1 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    review_queue_policy: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "review_queue_policy": self.review_queue_policy,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s1_workbench_scaffold(
    request: S1WorkbenchScaffoldRequest,
) -> S1WorkbenchScaffoldResponse:
    """Build WORK Sprint 1 scaffold contract for field-review queue policy.

    Args:
        request: Workbench metadata and queue policy guardrails used by Sprint 1.

    Returns:
        S1WorkbenchScaffoldResponse: Stable scaffold output with review queue
            policy and integration points.

    Raises:
        S1WorkbenchScaffoldError: If one or more WORK Sprint 1 input rules fail.
    """

    correlation_id = request.correlation_id or f"work-s1-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s1_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": request.workflow_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "default_priority": request.default_priority,
            "sla_hours": request.sla_hours,
            "max_queue_size": request.max_queue_size,
        },
    )

    (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        required_fields,
        evidence_sources,
        default_priority,
        sla_hours,
        max_queue_size,
        auto_assignment_enabled,
        reviewer_roles,
    ) = _validate_s1_input(request=request)

    review_queue_policy = {
        "workflow_id": workflow_id,
        "dataset_name": dataset_name,
        "entity_kind": entity_kind,
        "schema_version": schema_version,
        "owner_team": owner_team,
        "queue_scope": "campo_faltante_com_evidencia",
        "queue_key": f"{workflow_id}:{dataset_name}:{entity_kind}",
        "required_fields": required_fields,
        "required_fields_count": len(required_fields),
        "evidence_sources": evidence_sources,
        "evidence_sources_count": len(evidence_sources),
        "default_priority": default_priority,
        "sla_hours": sla_hours,
        "max_queue_size": max_queue_size,
        "auto_assignment_enabled": auto_assignment_enabled,
        "reviewer_roles": reviewer_roles,
        "reviewer_roles_count": len(reviewer_roles),
    }

    response = S1WorkbenchScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        workflow_id=workflow_id,
        dataset_name=dataset_name,
        review_queue_policy=review_queue_policy,
        pontos_integracao={
            "work_s1_prepare_endpoint": BACKEND_WORK_S1_PREPARE_ENDPOINT,
            "workbench_revisao_router_module": "app.routers.revisao_humana.prepare_workbench_revisao_s1",
            "workbench_revisao_s1_core_module": (
                "app.modules.revisao_humana.s1_core.execute_workbench_revisao_s1_main_flow"
            ),
            "workbench_revisao_s1_validation_module": (
                "app.modules.revisao_humana.s1_validation.validate_workbench_revisao_s1_output_contract"
            ),
        },
    )
    logger.info(
        "workbench_revisao_s1_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "dataset_name": dataset_name,
            "entity_kind": entity_kind,
            "required_fields_count": len(required_fields),
            "evidence_sources_count": len(evidence_sources),
            "reviewer_roles_count": len(reviewer_roles),
        },
    )
    return response


def _validate_s1_input(
    *,
    request: S1WorkbenchScaffoldRequest,
) -> tuple[str, str, str, str, str, tuple[str, ...], tuple[str, ...], str, int, int, bool, tuple[str, ...]]:
    workflow_id = _normalize_workflow_id(request.workflow_id)

    dataset_name = request.dataset_name.strip()
    if len(dataset_name) < 3:
        _raise_workbench_error(
            code="INVALID_DATASET_NAME",
            message="dataset_name invalido: informe nome com ao menos 3 caracteres",
            action="Defina dataset_name estavel para rastreabilidade da fila de revisao.",
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
            action="Use schema_version no formato vN (ex: v1, v2).",
        )

    owner_team = request.owner_team.strip().lower()
    if len(owner_team) < 2:
        _raise_workbench_error(
            code="INVALID_OWNER_TEAM",
            message="owner_team invalido: informe identificador com ao menos 2 caracteres",
            action="Defina owner_team para ownership operacional da fila de revisao.",
        )

    required_fields = _normalize_required_fields(
        raw_required_fields=request.required_fields,
        entity_kind=entity_kind,
    )
    evidence_sources = _normalize_evidence_sources(request.evidence_sources)
    reviewer_roles = _normalize_reviewer_roles(request.reviewer_roles)

    default_priority = request.default_priority.strip().lower()
    if default_priority not in ALLOWED_PRIORITIES:
        _raise_workbench_error(
            code="INVALID_DEFAULT_PRIORITY",
            message=f"default_priority invalida: {request.default_priority}",
            action="Use prioridade suportada: baixa, media, alta ou critica.",
        )

    if isinstance(request.sla_hours, bool) or not isinstance(request.sla_hours, int):
        _raise_workbench_error(
            code="INVALID_SLA_HOURS_TYPE",
            message="sla_hours deve ser inteiro",
            action="Ajuste sla_hours para inteiro no intervalo 1..720.",
        )
    sla_hours = request.sla_hours
    if sla_hours < MIN_SLA_HOURS or sla_hours > MAX_SLA_HOURS:
        _raise_workbench_error(
            code="INVALID_SLA_HOURS",
            message=f"sla_hours fora do intervalo suportado: {request.sla_hours}",
            action=f"Use sla_hours entre {MIN_SLA_HOURS} e {MAX_SLA_HOURS}.",
        )

    if isinstance(request.max_queue_size, bool) or not isinstance(request.max_queue_size, int):
        _raise_workbench_error(
            code="INVALID_MAX_QUEUE_SIZE_TYPE",
            message="max_queue_size deve ser inteiro",
            action="Ajuste max_queue_size para inteiro no intervalo 1..100000.",
        )
    max_queue_size = request.max_queue_size
    if max_queue_size < MIN_QUEUE_SIZE or max_queue_size > MAX_QUEUE_SIZE:
        _raise_workbench_error(
            code="INVALID_MAX_QUEUE_SIZE",
            message=f"max_queue_size fora do intervalo suportado: {request.max_queue_size}",
            action=f"Use max_queue_size entre {MIN_QUEUE_SIZE} e {MAX_QUEUE_SIZE}.",
        )

    if not isinstance(request.auto_assignment_enabled, bool):
        _raise_workbench_error(
            code="INVALID_AUTO_ASSIGNMENT_ENABLED_FLAG",
            message="auto_assignment_enabled deve ser booleano",
            action="Ajuste auto_assignment_enabled para true/false.",
        )

    return (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        required_fields,
        evidence_sources,
        default_priority,
        sla_hours,
        max_queue_size,
        request.auto_assignment_enabled,
        reviewer_roles,
    )


def _normalize_workflow_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not WORKFLOW_ID_RE.match(normalized):
        _raise_workbench_error(
            code="INVALID_WORKFLOW_ID",
            message="workflow_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action="Padronize workflow_id para formato estavel (ex: WORK_REVIEW_LEAD_V1).",
        )
    return normalized


def _normalize_required_fields(
    *,
    raw_required_fields: tuple[str, ...] | None,
    entity_kind: str,
) -> tuple[str, ...]:
    raw_fields = raw_required_fields or DEFAULT_REQUIRED_FIELDS_BY_ENTITY_KIND[entity_kind]
    if not isinstance(raw_fields, tuple):
        _raise_workbench_error(
            code="INVALID_REQUIRED_FIELDS_TYPE",
            message="required_fields deve ser tupla de nomes de campos",
            action="Informe required_fields como tuple[str, ...] contendo campos da revisao.",
        )

    normalized: list[str] = []
    for field in raw_fields:
        name = (field or "").strip().lower()
        if not FIELD_NAME_RE.match(name):
            _raise_workbench_error(
                code="INVALID_REQUIRED_FIELD_NAME",
                message=f"required_field invalido: {field}",
                action="Use nomes de campos com letras, numeros e underscore.",
            )
        if name not in normalized:
            normalized.append(name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_REQUIRED_FIELDS",
            message="required_fields nao pode ser vazio",
            action="Informe ao menos um campo para fila de revisao por evidencia.",
        )
    return tuple(normalized)


def _normalize_evidence_sources(raw_sources: tuple[str, ...] | None) -> tuple[str, ...]:
    sources = raw_sources or DEFAULT_EVIDENCE_SOURCES
    if not isinstance(sources, tuple):
        _raise_workbench_error(
            code="INVALID_EVIDENCE_SOURCES_TYPE",
            message="evidence_sources deve ser tupla de fontes",
            action="Informe evidence_sources como tuple[str, ...].",
        )

    normalized: list[str] = []
    for source in sources:
        source_name = (source or "").strip().lower()
        if source_name not in ALLOWED_EVIDENCE_SOURCES:
            _raise_workbench_error(
                code="INVALID_EVIDENCE_SOURCE",
                message=f"evidence_source invalida: {source}",
                action="Use fonte suportada: crm, formulario, ocr, evento, api, manual ou enriquecimento.",
            )
        if source_name not in normalized:
            normalized.append(source_name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_EVIDENCE_SOURCES",
            message="evidence_sources nao pode ser vazio",
            action="Informe ao menos uma fonte de evidencia para a fila.",
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
            action="Informe ao menos um papel de revisor para roteamento operacional.",
        )
    return tuple(normalized)


def _raise_workbench_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "workbench_revisao_s1_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S1WorkbenchScaffoldError(code=code, message=message, action=action)
