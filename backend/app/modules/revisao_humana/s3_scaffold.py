"""Sprint 3 scaffold contracts for batch operations and approval flow.

This module defines the stable input/output contract for WORK Sprint 3,
preparing batch operation policies and approval-flow guardrails with
actionable diagnostics and integration points.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.frontend.revisao_humana.s3")

CONTRACT_VERSION = "work.s3.v1"
BACKEND_WORK_S3_PREPARE_ENDPOINT = "/internal/revisao-humana/s3/prepare"

WORKFLOW_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
ROLE_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")

ALLOWED_ENTITY_KINDS = ("lead", "evento", "ingresso", "generic")
ALLOWED_APPROVAL_MODES = ("single_reviewer", "dual_control", "committee")

MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 10000
MIN_PENDING_BATCHES = 1
MAX_PENDING_BATCHES = 10000
MIN_REQUIRED_APPROVERS = 1
MAX_REQUIRED_APPROVERS = 5
MIN_APPROVAL_SLA_HOURS = 1
MAX_APPROVAL_SLA_HOURS = 720

DEFAULT_APPROVER_ROLES = ("supervisor", "coordenador")


class S3WorkbenchScaffoldError(ValueError):
    """Raised when WORK S3 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3WorkbenchScaffoldRequest:
    """Input contract for WORK Sprint 3 scaffold validation."""

    workflow_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v3"
    owner_team: str = "etl"
    batch_size: int = 200
    max_pending_batches: int = 2000
    approval_mode: str = "dual_control"
    required_approvers: int = 2
    approver_roles: tuple[str, ...] | None = None
    approval_sla_hours: int = 24
    require_justification: bool = True
    allow_partial_approval: bool = False
    auto_lock_on_conflict: bool = True
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible WORK Sprint 3 contract."""

        return {
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "owner_team": self.owner_team,
            "batch_size": self.batch_size,
            "max_pending_batches": self.max_pending_batches,
            "approval_mode": self.approval_mode,
            "required_approvers": self.required_approvers,
            "approver_roles": list(self.approver_roles or ()),
            "approval_sla_hours": self.approval_sla_hours,
            "require_justification": self.require_justification,
            "allow_partial_approval": self.allow_partial_approval,
            "auto_lock_on_conflict": self.auto_lock_on_conflict,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3WorkbenchScaffoldResponse:
    """Output contract returned when WORK Sprint 3 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    workflow_id: str
    dataset_name: str
    batch_approval_policy: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "workflow_id": self.workflow_id,
            "dataset_name": self.dataset_name,
            "batch_approval_policy": self.batch_approval_policy,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s3_workbench_scaffold(
    request: S3WorkbenchScaffoldRequest,
) -> S3WorkbenchScaffoldResponse:
    """Build WORK Sprint 3 scaffold contract for batch approval operations.

    Args:
        request: Workbench metadata and batch approval guardrails used by
            Sprint 3.

    Returns:
        S3WorkbenchScaffoldResponse: Stable scaffold output with batch approval
            policy and integration points.

    Raises:
        S3WorkbenchScaffoldError: If one or more WORK Sprint 3 input rules fail.
    """

    correlation_id = request.correlation_id or f"work-s3-{uuid4().hex[:12]}"
    logger.info(
        "workbench_revisao_s3_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": request.workflow_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "approval_mode": request.approval_mode,
            "required_approvers": request.required_approvers,
            "batch_size": request.batch_size,
            "max_pending_batches": request.max_pending_batches,
        },
    )

    (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        batch_size,
        max_pending_batches,
        approval_mode,
        required_approvers,
        approver_roles,
        approval_sla_hours,
        require_justification,
        allow_partial_approval,
        auto_lock_on_conflict,
    ) = _validate_s3_input(request=request)

    batch_approval_policy = {
        "workflow_id": workflow_id,
        "dataset_name": dataset_name,
        "entity_kind": entity_kind,
        "schema_version": schema_version,
        "owner_team": owner_team,
        "page_scope": "operacoes_em_lote_fluxo_aprovacao",
        "batch_key": f"{workflow_id}:{dataset_name}:{entity_kind}:s3",
        "batch_size": batch_size,
        "max_pending_batches": max_pending_batches,
        "approval_mode": approval_mode,
        "required_approvers": required_approvers,
        "approver_roles": approver_roles,
        "approver_roles_count": len(approver_roles),
        "approval_sla_hours": approval_sla_hours,
        "require_justification": require_justification,
        "allow_partial_approval": allow_partial_approval,
        "auto_lock_on_conflict": auto_lock_on_conflict,
    }

    response = S3WorkbenchScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        workflow_id=workflow_id,
        dataset_name=dataset_name,
        batch_approval_policy=batch_approval_policy,
        pontos_integracao={
            "work_s3_prepare_endpoint": BACKEND_WORK_S3_PREPARE_ENDPOINT,
            "workbench_revisao_router_module": "app.routers.revisao_humana.prepare_workbench_revisao_s3",
            "workbench_revisao_s3_core_module": (
                "app.modules.revisao_humana.s3_core.execute_workbench_revisao_s3_main_flow"
            ),
            "workbench_revisao_s3_validation_module": (
                "app.modules.revisao_humana.s3_validation.validate_workbench_revisao_s3_output_contract"
            ),
        },
    )
    logger.info(
        "workbench_revisao_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "dataset_name": dataset_name,
            "entity_kind": entity_kind,
            "approval_mode": approval_mode,
            "required_approvers": required_approvers,
            "approver_roles_count": len(approver_roles),
            "batch_size": batch_size,
            "max_pending_batches": max_pending_batches,
        },
    )
    return response


def _validate_s3_input(
    *,
    request: S3WorkbenchScaffoldRequest,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
    int,
    int,
    str,
    int,
    tuple[str, ...],
    int,
    bool,
    bool,
    bool,
]:
    workflow_id = _normalize_workflow_id(request.workflow_id)

    dataset_name = request.dataset_name.strip()
    if len(dataset_name) < 3:
        _raise_workbench_error(
            code="INVALID_DATASET_NAME",
            message="dataset_name invalido: informe nome com ao menos 3 caracteres",
            action="Defina dataset_name estavel para rastreabilidade das operacoes em lote.",
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
            action="Use schema_version no formato vN (ex: v3).",
        )

    owner_team = request.owner_team.strip().lower()
    if len(owner_team) < 2:
        _raise_workbench_error(
            code="INVALID_OWNER_TEAM",
            message="owner_team invalido: informe identificador com ao menos 2 caracteres",
            action="Defina owner_team para ownership operacional da aprovacao em lote.",
        )

    batch_size = _validate_bounded_int(
        field_name="batch_size",
        value=request.batch_size,
        min_value=MIN_BATCH_SIZE,
        max_value=MAX_BATCH_SIZE,
    )
    max_pending_batches = _validate_bounded_int(
        field_name="max_pending_batches",
        value=request.max_pending_batches,
        min_value=MIN_PENDING_BATCHES,
        max_value=MAX_PENDING_BATCHES,
    )

    if max_pending_batches < batch_size:
        _raise_workbench_error(
            code="INVALID_PENDING_BATCH_CAPACITY",
            message="max_pending_batches nao pode ser menor que batch_size",
            action="Ajuste max_pending_batches para valor maior ou igual ao batch_size.",
        )

    approval_mode = request.approval_mode.strip().lower()
    if approval_mode not in ALLOWED_APPROVAL_MODES:
        _raise_workbench_error(
            code="INVALID_APPROVAL_MODE",
            message=f"approval_mode invalido: {request.approval_mode}",
            action="Use approval_mode suportado: single_reviewer, dual_control ou committee.",
        )

    required_approvers = _validate_bounded_int(
        field_name="required_approvers",
        value=request.required_approvers,
        min_value=MIN_REQUIRED_APPROVERS,
        max_value=MAX_REQUIRED_APPROVERS,
    )

    approver_roles = _normalize_approver_roles(request.approver_roles)
    if required_approvers > len(approver_roles):
        _raise_workbench_error(
            code="INVALID_REQUIRED_APPROVERS",
            message="required_approvers nao pode ser maior que approver_roles_count",
            action="Ajuste required_approvers ou informe mais approver_roles.",
        )

    if approval_mode == "single_reviewer" and required_approvers != 1:
        _raise_workbench_error(
            code="INVALID_APPROVAL_MODE_CONFIGURATION",
            message="approval_mode single_reviewer exige required_approvers=1",
            action="Ajuste required_approvers para 1 ou use outro approval_mode.",
        )
    if approval_mode in {"dual_control", "committee"} and required_approvers < 2:
        _raise_workbench_error(
            code="INVALID_APPROVAL_MODE_CONFIGURATION",
            message=f"approval_mode {approval_mode} exige ao menos 2 aprovadores",
            action="Ajuste required_approvers para valor >= 2.",
        )

    approval_sla_hours = _validate_bounded_int(
        field_name="approval_sla_hours",
        value=request.approval_sla_hours,
        min_value=MIN_APPROVAL_SLA_HOURS,
        max_value=MAX_APPROVAL_SLA_HOURS,
    )

    if not isinstance(request.require_justification, bool):
        _raise_workbench_error(
            code="INVALID_REQUIRE_JUSTIFICATION_FLAG",
            message="require_justification deve ser booleano",
            action="Ajuste require_justification para true/false.",
        )
    if not isinstance(request.allow_partial_approval, bool):
        _raise_workbench_error(
            code="INVALID_ALLOW_PARTIAL_APPROVAL_FLAG",
            message="allow_partial_approval deve ser booleano",
            action="Ajuste allow_partial_approval para true/false.",
        )
    if not isinstance(request.auto_lock_on_conflict, bool):
        _raise_workbench_error(
            code="INVALID_AUTO_LOCK_ON_CONFLICT_FLAG",
            message="auto_lock_on_conflict deve ser booleano",
            action="Ajuste auto_lock_on_conflict para true/false.",
        )

    if request.allow_partial_approval and required_approvers <= 1:
        _raise_workbench_error(
            code="INVALID_PARTIAL_APPROVAL_CONFIGURATION",
            message="allow_partial_approval requer required_approvers maior que 1",
            action="Defina required_approvers >= 2 ou desative allow_partial_approval.",
        )

    return (
        workflow_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        batch_size,
        max_pending_batches,
        approval_mode,
        required_approvers,
        approver_roles,
        approval_sla_hours,
        request.require_justification,
        request.allow_partial_approval,
        request.auto_lock_on_conflict,
    )


def _normalize_workflow_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not WORKFLOW_ID_RE.match(normalized):
        _raise_workbench_error(
            code="INVALID_WORKFLOW_ID",
            message="workflow_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action="Padronize workflow_id para formato estavel (ex: WORK_BATCH_APPROVAL_V3).",
        )
    return normalized


def _normalize_approver_roles(raw_roles: tuple[str, ...] | None) -> tuple[str, ...]:
    roles = raw_roles or DEFAULT_APPROVER_ROLES
    if not isinstance(roles, tuple):
        _raise_workbench_error(
            code="INVALID_APPROVER_ROLES_TYPE",
            message="approver_roles deve ser tupla de papeis",
            action="Informe approver_roles como tuple[str, ...].",
        )

    normalized: list[str] = []
    for role in roles:
        role_name = (role or "").strip().lower()
        if not ROLE_NAME_RE.match(role_name):
            _raise_workbench_error(
                code="INVALID_APPROVER_ROLE",
                message=f"approver_role invalido: {role}",
                action="Use papeis com letras, numeros e underscore.",
            )
        if role_name not in normalized:
            normalized.append(role_name)

    if not normalized:
        _raise_workbench_error(
            code="INVALID_APPROVER_ROLES",
            message="approver_roles nao pode ser vazio",
            action="Informe ao menos um papel para aprovacao operacional.",
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
        "workbench_revisao_s3_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S3WorkbenchScaffoldError(code=code, message=message, action=action)
