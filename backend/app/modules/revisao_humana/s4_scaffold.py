"""Sprint 4 scaffold contracts for edit-audit, SLA, and productivity policy.

This module defines the stable input/output contract for WORK Sprint 4,
preparing operational guardrails for edit traceability, SLA monitoring, and
team productivity diagnostics.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.frontend.revisao_humana.s4")

CONTRACT_VERSION = "work.s4.v1"
BACKEND_WORK_S4_PREPARE_ENDPOINT = "/internal/revisao-humana/s4/prepare"

WORKFLOW_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
ROLE_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")

ALLOWED_ENTITY_KINDS = ("lead", "evento", "ingresso", "generic")
ALLOWED_AUDIT_DIMENSIONS = ("edicao", "sla", "produtividade")
ALLOWED_CHANGE_CHANNELS = ("ui", "api", "batch", "automacao", "manual")
ALLOWED_AUDIT_MODES = ("full_trace", "sampled_trace", "compliance_only")

MIN_SLA_TARGET_MINUTES = 5
MAX_SLA_TARGET_MINUTES = 4320
MIN_SLA_WARNING_THRESHOLD_MINUTES = 1
MAX_SLA_WARNING_THRESHOLD_MINUTES = 4319
MIN_SLA_BREACH_GRACE_MINUTES = 0
MAX_SLA_BREACH_GRACE_MINUTES = 720
MIN_PRODUCTIVITY_WINDOW_HOURS = 1
MAX_PRODUCTIVITY_WINDOW_HOURS = 168
MIN_ACTIONS_PER_WINDOW = 0
MAX_ACTIONS_PER_WINDOW = 100000

DEFAULT_AUDIT_DIMENSIONS = ("edicao", "sla", "produtividade")
DEFAULT_CHANGE_CHANNELS = ("ui", "api", "batch")
DEFAULT_REVIEWER_ROLES = ("operador", "supervisor", "auditoria")


class S4WorkbenchScaffoldError(ValueError):
    """Raised when WORK S4 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4WorkbenchScaffoldRequest:
    """Input contract for WORK Sprint 4 scaffold validation."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v4"
    owner_team: str = "etl"
    audit_dimensions: tuple[str, ...] | None = None
    change_channels: tuple[str, ...] | None = None
    audit_mode: str = "full_trace"
    sla_target_minutes: int = 120
    sla_warning_threshold_minutes: int = 90
    sla_breach_grace_minutes: int = 15
    productivity_window_hours: int = 8
    minimum_actions_per_window: int = 10
    require_change_reason: bool = True
    capture_before_after_state: bool = True
    enable_anomaly_alerts: bool = True
    reviewer_roles: tuple[str, ...] | None = None
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible WORK Sprint 4 contract."""

        return {
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "owner_team": self.owner_team,
            "audit_dimensions": list(self.audit_dimensions or ()),
            "change_channels": list(self.change_channels or ()),
            "audit_mode": self.audit_mode,
            "sla_target_minutes": self.sla_target_minutes,
            "sla_warning_threshold_minutes": self.sla_warning_threshold_minutes,
            "sla_breach_grace_minutes": self.sla_breach_grace_minutes,
            "productivity_window_hours": self.productivity_window_hours,
            "minimum_actions_per_window": self.minimum_actions_per_window,
            "require_change_reason": self.require_change_reason,
            "capture_before_after_state": self.capture_before_after_state,
            "enable_anomaly_alerts": self.enable_anomaly_alerts,
            "reviewer_roles": list(self.reviewer_roles or ()),
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4WorkbenchScaffoldResponse:
    """Output contract returned when WORK Sprint 4 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    operational_audit_policy: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "operational_audit_policy": self.operational_audit_policy,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s4_workbench_scaffold(
    request: S4WorkbenchScaffoldRequest,
) -> S4WorkbenchScaffoldResponse:
    """Build WORK Sprint 4 scaffold contract for audit, SLA, and productivity.

    Args:
        request: Workbench metadata and operational guardrails used by Sprint 4.

    Returns:
        S4WorkbenchScaffoldResponse: Stable scaffold output with operational
            audit policy and integration points.

    Raises:
        S4WorkbenchScaffoldError: If one or more WORK Sprint 4 input rules fail.
    """

    correlation_id = request.correlation_id or f"work-s4-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s4_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": request.workflow_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "audit_mode": request.audit_mode,
            "sla_target_minutes": request.sla_target_minutes,
            "productivity_window_hours": request.productivity_window_hours,
        },
    )

    (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        audit_dimensions,
        change_channels,
        audit_mode,
        sla_target_minutes,
        sla_warning_threshold_minutes,
        sla_breach_grace_minutes,
        productivity_window_hours,
        minimum_actions_per_window,
        require_change_reason,
        capture_before_after_state,
        enable_anomaly_alerts,
        reviewer_roles,
    ) = _validate_s4_input(request=request)

    operational_audit_policy = {
        "workflow_id": workflow_id,
        "dataset_name": dataset_name,
        "entity_kind": entity_kind,
        "schema_version": schema_version,
        "owner_team": owner_team,
        "page_scope": "auditoria_edicao_sla_produtividade_operacional",
        "policy_key": f"{workflow_id}:{dataset_name}:{entity_kind}:s4",
        "audit_dimensions": audit_dimensions,
        "audit_dimensions_count": len(audit_dimensions),
        "change_channels": change_channels,
        "change_channels_count": len(change_channels),
        "audit_mode": audit_mode,
        "sla_target_minutes": sla_target_minutes,
        "sla_warning_threshold_minutes": sla_warning_threshold_minutes,
        "sla_breach_grace_minutes": sla_breach_grace_minutes,
        "productivity_window_hours": productivity_window_hours,
        "minimum_actions_per_window": minimum_actions_per_window,
        "require_change_reason": require_change_reason,
        "capture_before_after_state": capture_before_after_state,
        "enable_anomaly_alerts": enable_anomaly_alerts,
        "reviewer_roles": reviewer_roles,
        "reviewer_roles_count": len(reviewer_roles),
    }

    response = S4WorkbenchScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        workflow_id=workflow_id,
        dataset_name=dataset_name,
        operational_audit_policy=operational_audit_policy,
        pontos_integracao={
            "work_s4_prepare_endpoint": BACKEND_WORK_S4_PREPARE_ENDPOINT,
            "workbench_revisao_router_module": "app.routers.revisao_humana.prepare_workbench_revisao_s4",
            "workbench_revisao_s4_core_module": (
                "app.modules.revisao_humana.s4_core.execute_workbench_revisao_s4_main_flow"
            ),
            "workbench_revisao_s4_validation_module": (
                "app.modules.revisao_humana.s4_validation.validate_workbench_revisao_s4_output_contract"
            ),
        },
    )
    logger.info(
        "workbench_revisao_s4_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "dataset_name": dataset_name,
            "entity_kind": entity_kind,
            "audit_mode": audit_mode,
            "audit_dimensions_count": len(audit_dimensions),
            "change_channels_count": len(change_channels),
            "reviewer_roles_count": len(reviewer_roles),
        },
    )
    return response


def _validate_s4_input(
    *,
    request: S4WorkbenchScaffoldRequest,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
    tuple[str, ...],
    tuple[str, ...],
    str,
    int,
    int,
    int,
    int,
    int,
    bool,
    bool,
    bool,
    tuple[str, ...],
]:
    workflow_id = _normalize_workflow_id(request.workflow_id)

    dataset_name = request.dataset_name.strip()
    if len(dataset_name) < 3:
        _raise_workbench_error(
            code="INVALID_DATASET_NAME",
            message="dataset_name invalido: informe nome com ao menos 3 caracteres",
            action="Defina dataset_name estavel para rastreabilidade operacional da sprint.",
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
            action="Use schema_version no formato vN (ex: v4).",
        )

    owner_team = request.owner_team.strip().lower()
    if len(owner_team) < 2:
        _raise_workbench_error(
            code="INVALID_OWNER_TEAM",
            message="owner_team invalido: informe identificador com ao menos 2 caracteres",
            action="Defina owner_team para ownership operacional da auditoria.",
        )

    audit_dimensions = _normalize_audit_dimensions(request.audit_dimensions)
    change_channels = _normalize_change_channels(request.change_channels)
    reviewer_roles = _normalize_reviewer_roles(request.reviewer_roles)

    audit_mode = request.audit_mode.strip().lower()
    if audit_mode not in ALLOWED_AUDIT_MODES:
        _raise_workbench_error(
            code="INVALID_AUDIT_MODE",
            message=f"audit_mode invalido: {request.audit_mode}",
            action="Use audit_mode suportado: full_trace, sampled_trace ou compliance_only.",
        )

    sla_target_minutes = _validate_bounded_int(
        field_name="sla_target_minutes",
        value=request.sla_target_minutes,
        min_value=MIN_SLA_TARGET_MINUTES,
        max_value=MAX_SLA_TARGET_MINUTES,
    )
    sla_warning_threshold_minutes = _validate_bounded_int(
        field_name="sla_warning_threshold_minutes",
        value=request.sla_warning_threshold_minutes,
        min_value=MIN_SLA_WARNING_THRESHOLD_MINUTES,
        max_value=MAX_SLA_WARNING_THRESHOLD_MINUTES,
    )
    sla_breach_grace_minutes = _validate_bounded_int(
        field_name="sla_breach_grace_minutes",
        value=request.sla_breach_grace_minutes,
        min_value=MIN_SLA_BREACH_GRACE_MINUTES,
        max_value=MAX_SLA_BREACH_GRACE_MINUTES,
    )
    productivity_window_hours = _validate_bounded_int(
        field_name="productivity_window_hours",
        value=request.productivity_window_hours,
        min_value=MIN_PRODUCTIVITY_WINDOW_HOURS,
        max_value=MAX_PRODUCTIVITY_WINDOW_HOURS,
    )
    minimum_actions_per_window = _validate_bounded_int(
        field_name="minimum_actions_per_window",
        value=request.minimum_actions_per_window,
        min_value=MIN_ACTIONS_PER_WINDOW,
        max_value=MAX_ACTIONS_PER_WINDOW,
    )

    if "sla" in audit_dimensions and sla_warning_threshold_minutes >= sla_target_minutes:
        _raise_workbench_error(
            code="INVALID_SLA_THRESHOLDS",
            message="sla_warning_threshold_minutes deve ser menor que sla_target_minutes",
            action="Ajuste os limiares para manter warning estritamente abaixo do target.",
        )

    if sla_breach_grace_minutes > sla_target_minutes:
        _raise_workbench_error(
            code="INVALID_SLA_BREACH_GRACE_MINUTES",
            message="sla_breach_grace_minutes nao pode ser maior que sla_target_minutes",
            action="Use janela de tolerancia menor ou igual ao SLA target.",
        )

    if not isinstance(request.require_change_reason, bool):
        _raise_workbench_error(
            code="INVALID_REQUIRE_CHANGE_REASON_FLAG",
            message="require_change_reason deve ser booleano",
            action="Ajuste require_change_reason para true/false.",
        )
    if not isinstance(request.capture_before_after_state, bool):
        _raise_workbench_error(
            code="INVALID_CAPTURE_BEFORE_AFTER_STATE_FLAG",
            message="capture_before_after_state deve ser booleano",
            action="Ajuste capture_before_after_state para true/false.",
        )
    if not isinstance(request.enable_anomaly_alerts, bool):
        _raise_workbench_error(
            code="INVALID_ENABLE_ANOMALY_ALERTS_FLAG",
            message="enable_anomaly_alerts deve ser booleano",
            action="Ajuste enable_anomaly_alerts para true/false.",
        )

    if audit_mode == "full_trace" and not request.capture_before_after_state:
        _raise_workbench_error(
            code="INVALID_AUDIT_MODE_CONFIGURATION",
            message="audit_mode full_trace exige capture_before_after_state=true",
            action="Ative capture_before_after_state ou use sampled_trace/compliance_only.",
        )

    if (
        "edicao" in audit_dimensions
        and audit_mode != "compliance_only"
        and not request.require_change_reason
    ):
        _raise_workbench_error(
            code="INVALID_CHANGE_REASON_CONFIGURATION",
            message="auditoria de edicao requer require_change_reason=true",
            action="Ative require_change_reason para rastreabilidade de alteracoes.",
        )

    return (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        audit_dimensions,
        change_channels,
        audit_mode,
        sla_target_minutes,
        sla_warning_threshold_minutes,
        sla_breach_grace_minutes,
        productivity_window_hours,
        minimum_actions_per_window,
        request.require_change_reason,
        request.capture_before_after_state,
        request.enable_anomaly_alerts,
        reviewer_roles,
    )


def _normalize_workflow_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not WORKFLOW_ID_RE.match(normalized):
        _raise_workbench_error(
            code="INVALID_WORKFLOW_ID",
            message="workflow_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action="Padronize workflow_id para formato estavel (ex: WORK_AUDITORIA_OPERACIONAL_V4).",
        )
    return normalized


def _normalize_audit_dimensions(raw_dimensions: tuple[str, ...] | None) -> tuple[str, ...]:
    dimensions = raw_dimensions or DEFAULT_AUDIT_DIMENSIONS
    if not isinstance(dimensions, tuple):
        _raise_workbench_error(
            code="INVALID_AUDIT_DIMENSIONS_TYPE",
            message="audit_dimensions deve ser tupla de dimensoes",
            action="Informe audit_dimensions como tuple[str, ...].",
        )

    normalized: list[str] = []
    for dimension in dimensions:
        name = (dimension or "").strip().lower()
        if name not in ALLOWED_AUDIT_DIMENSIONS:
            _raise_workbench_error(
                code="INVALID_AUDIT_DIMENSION",
                message=f"audit_dimension invalida: {dimension}",
                action="Use dimensoes suportadas: edicao, sla e produtividade.",
            )
        if name not in normalized:
            normalized.append(name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_AUDIT_DIMENSIONS",
            message="audit_dimensions nao pode ser vazio",
            action="Informe ao menos uma dimensao para auditoria operacional.",
        )
    return tuple(normalized)


def _normalize_change_channels(raw_channels: tuple[str, ...] | None) -> tuple[str, ...]:
    channels = raw_channels or DEFAULT_CHANGE_CHANNELS
    if not isinstance(channels, tuple):
        _raise_workbench_error(
            code="INVALID_CHANGE_CHANNELS_TYPE",
            message="change_channels deve ser tupla de canais",
            action="Informe change_channels como tuple[str, ...].",
        )

    normalized: list[str] = []
    for channel in channels:
        name = (channel or "").strip().lower()
        if name not in ALLOWED_CHANGE_CHANNELS:
            _raise_workbench_error(
                code="INVALID_CHANGE_CHANNEL",
                message=f"change_channel invalido: {channel}",
                action="Use canais suportados: ui, api, batch, automacao ou manual.",
            )
        if name not in normalized:
            normalized.append(name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_CHANGE_CHANNELS",
            message="change_channels nao pode ser vazio",
            action="Informe ao menos um canal de alteracao auditavel.",
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
            action="Informe ao menos um papel para acompanhar auditoria e SLA.",
        )
    return tuple(normalized)


def _validate_bounded_int(
    *,
    field_name: str,
    value: int,
    min_value: int,
    max_value: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _raise_workbench_error(
            code=f"INVALID_{field_name.upper()}_TYPE",
            message=f"{field_name} deve ser inteiro",
            action=f"Ajuste {field_name} para inteiro no intervalo {min_value}..{max_value}.",
        )
    if value < min_value or value > max_value:
        _raise_workbench_error(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} fora do intervalo suportado: {value}",
            action=f"Use {field_name} entre {min_value} e {max_value}.",
        )
    return int(value)


def _raise_workbench_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "workbench_revisao_s4_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S4WorkbenchScaffoldError(code=code, message=message, action=action)
