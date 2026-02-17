"""Sprint 2 scaffold contracts for strict schema and domain validation.

This module defines the stable input/output contract for CONT Sprint 2,
preparing strict schema and domain validation profiles with actionable
diagnostics and operational integration points.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.contracts.s2")

CONTRACT_VERSION = "cont.s2.v1"
BACKEND_CONT_S2_PREPARE_ENDPOINT = "/internal/contracts/s2/prepare"
CONTRACT_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")

ALLOWED_SOURCE_KINDS = ("pdf", "docx", "pptx", "xlsx", "csv", "api", "manual", "other")


class S2ContractScaffoldError(ValueError):
    """Raised when CONT S2 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2CanonicalContractScaffoldRequest:
    """Input contract for CONT Sprint 2 scaffold validation."""

    contract_id: str
    dataset_name: str
    source_kind: str
    schema_version: str = "v1"
    strict_validation: bool = True
    lineage_required: bool = True
    owner_team: str = "etl"
    schema_required_fields: tuple[str, ...] = (
        "record_id",
        "event_ts",
        "source_id",
        "payload_checksum",
    )
    domain_constraints: dict[str, tuple[str, ...]] | None = None
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible CONT Sprint 2 contract."""

        return {
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
            "owner_team": self.owner_team,
            "schema_required_fields": list(self.schema_required_fields),
            "domain_constraints": {
                key: list(values)
                for key, values in (self.domain_constraints or {}).items()
            },
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2CanonicalContractScaffoldResponse:
    """Output contract returned when CONT Sprint 2 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    validation_profile: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "validation_profile": self.validation_profile,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s2_contract_scaffold(
    request: S2CanonicalContractScaffoldRequest,
) -> S2CanonicalContractScaffoldResponse:
    """Build CONT Sprint 2 scaffold contract for strict schema/domain validation.

    Args:
        request: Contract metadata and strict schema/domain validation policy
            input.

    Returns:
        S2CanonicalContractScaffoldResponse: Stable scaffold output with
            validation profile and integration points.

    Raises:
        S2ContractScaffoldError: If one or more CONT Sprint 2 input rules fail.
    """

    correlation_id = request.correlation_id or f"cont-s2-{uuid4().hex[:12]}"
    logger.info(
        "contract_validation_s2_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "contract_id": request.contract_id,
            "dataset_name": request.dataset_name,
            "source_kind": request.source_kind,
            "schema_version": request.schema_version,
            "strict_validation": request.strict_validation,
            "lineage_required": request.lineage_required,
            "owner_team": request.owner_team,
            "schema_required_fields_count": len(request.schema_required_fields),
        },
    )

    (
        contract_id,
        dataset_name,
        source_kind,
        schema_version,
        strict_validation,
        lineage_required,
        owner_team,
        schema_required_fields,
        domain_constraints,
    ) = _validate_s2_input(request=request)

    validation_profile = {
        "contract_id": contract_id,
        "dataset_name": dataset_name,
        "source_kind": source_kind,
        "schema_version": schema_version,
        "strict_validation": strict_validation,
        "lineage_required": lineage_required,
        "owner_team": owner_team,
        "validation_scope": "schema_and_domain",
        "schema_required_fields": schema_required_fields,
        "domain_constraints": domain_constraints,
        "required_fields_count": len(schema_required_fields),
        "domain_rules_count": len(domain_constraints),
    }

    response = S2CanonicalContractScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        contract_id=contract_id,
        dataset_name=dataset_name,
        validation_profile=validation_profile,
        pontos_integracao={
            "cont_s2_prepare_endpoint": BACKEND_CONT_S2_PREPARE_ENDPOINT,
            "contract_validation_service_module": (
                "app.services.contract_validation_service.execute_s2_contract_validation_service"
            ),
            "contract_validation_s2_core_module": (
                "core.contracts.s2_core.execute_s2_contract_validation_main_flow"
            ),
            "contract_validation_s2_validation_module": (
                "core.contracts.s2_validation.validate_s2_contract_input_contract"
            ),
        },
    )
    logger.info(
        "contract_validation_s2_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "contract_id": contract_id,
            "dataset_name": dataset_name,
            "source_kind": source_kind,
            "schema_version": schema_version,
            "domain_rules_count": len(domain_constraints),
        },
    )
    return response


def _validate_s2_input(
    *,
    request: S2CanonicalContractScaffoldRequest,
) -> tuple[str, str, str, str, bool, bool, str, list[str], dict[str, list[str]]]:
    contract_id = _normalize_contract_id(request.contract_id)

    dataset_name = request.dataset_name.strip()
    if len(dataset_name) < 3:
        _raise_contract_error(
            code="INVALID_DATASET_NAME",
            message="dataset_name invalido: informe nome com ao menos 3 caracteres",
            action="Defina dataset_name estavel para rastreabilidade de contrato canonico.",
        )

    source_kind = request.source_kind.strip().lower()
    if source_kind not in ALLOWED_SOURCE_KINDS:
        _raise_contract_error(
            code="INVALID_SOURCE_KIND",
            message=f"source_kind invalido: {request.source_kind}",
            action="Use source_kind suportado: pdf, docx, pptx, xlsx, csv, api, manual ou other.",
        )

    schema_version = request.schema_version.strip().lower()
    if not SCHEMA_VERSION_RE.match(schema_version):
        _raise_contract_error(
            code="INVALID_SCHEMA_VERSION",
            message=f"schema_version invalida: {request.schema_version}",
            action="Use schema_version no formato vN (ex: v1, v2).",
        )

    if not isinstance(request.strict_validation, bool):
        _raise_contract_error(
            code="INVALID_STRICT_VALIDATION_FLAG",
            message="strict_validation deve ser booleano",
            action="Ajuste strict_validation para true/false.",
        )

    if not isinstance(request.lineage_required, bool):
        _raise_contract_error(
            code="INVALID_LINEAGE_REQUIRED_FLAG",
            message="lineage_required deve ser booleano",
            action="Ajuste lineage_required para true/false.",
        )

    owner_team = request.owner_team.strip().lower()
    if len(owner_team) < 2:
        _raise_contract_error(
            code="INVALID_OWNER_TEAM",
            message="owner_team invalido: informe identificador com ao menos 2 caracteres",
            action="Defina owner_team para direcionar ownership operacional do contrato.",
        )

    schema_required_fields = _normalize_required_fields(
        fields=request.schema_required_fields,
        lineage_required=request.lineage_required,
    )
    domain_constraints = _normalize_domain_constraints(
        constraints=request.domain_constraints,
        source_kind=source_kind,
        schema_version=schema_version,
        required_fields=schema_required_fields,
        strict_validation=request.strict_validation,
    )

    return (
        contract_id,
        dataset_name,
        source_kind,
        schema_version,
        request.strict_validation,
        request.lineage_required,
        owner_team,
        schema_required_fields,
        domain_constraints,
    )


def _normalize_required_fields(
    *,
    fields: tuple[str, ...],
    lineage_required: bool,
) -> list[str]:
    if not isinstance(fields, tuple) or len(fields) == 0:
        _raise_contract_error(
            code="INVALID_REQUIRED_FIELDS",
            message="schema_required_fields deve conter ao menos um campo",
            action="Informe campos obrigatorios do schema canonico na entrada do S2.",
        )

    normalized: list[str] = []
    for field in fields:
        name = str(field).strip()
        if not name:
            _raise_contract_error(
                code="INVALID_REQUIRED_FIELDS",
                message="schema_required_fields contem nome de campo vazio",
                action="Remova campos vazios e mantenha nomes estaveis de schema.",
            )
        if name not in normalized:
            normalized.append(name)

    if lineage_required and "lineage_ref_id" not in normalized:
        normalized.append("lineage_ref_id")
    return normalized


def _normalize_domain_constraints(
    *,
    constraints: dict[str, tuple[str, ...]] | None,
    source_kind: str,
    schema_version: str,
    required_fields: list[str],
    strict_validation: bool,
) -> dict[str, list[str]]:
    base_constraints: dict[str, list[str]] = {
        "source_kind": [source_kind],
        "schema_version": [schema_version],
    }
    if constraints is None:
        return base_constraints

    if not isinstance(constraints, dict):
        _raise_contract_error(
            code="INVALID_DOMAIN_CONSTRAINTS",
            message="domain_constraints deve ser dicionario field -> valores permitidos",
            action="Ajuste domain_constraints para dict[str, tuple[str, ...]].",
        )

    normalized = dict(base_constraints)
    for field_name, allowed_values in constraints.items():
        field = str(field_name).strip()
        if not field:
            _raise_contract_error(
                code="INVALID_DOMAIN_CONSTRAINTS",
                message="domain_constraints contem chave de campo vazia",
                action="Defina campos validos para constraints de dominio.",
            )
        if field not in required_fields:
            _raise_contract_error(
                code="DOMAIN_FIELD_NOT_IN_SCHEMA",
                message=f"Campo de dominio nao faz parte do schema_required_fields: {field}",
                action="Inclua o campo no schema ou remova a regra de dominio inconsistente.",
            )
        if not isinstance(allowed_values, tuple) or len(allowed_values) == 0:
            _raise_contract_error(
                code="INVALID_DOMAIN_VALUES",
                message=f"domain_constraints[{field}] deve conter ao menos um valor permitido",
                action="Informe valores validos para constraints de dominio.",
            )

        options: list[str] = []
        for raw_value in allowed_values:
            value = str(raw_value).strip()
            if not value:
                _raise_contract_error(
                    code="INVALID_DOMAIN_VALUES",
                    message=f"domain_constraints[{field}] contem valor vazio",
                    action="Remova valores vazios dos dominios permitidos.",
                )
            if value not in options:
                options.append(value)
        normalized[field] = options

    if strict_validation and len(normalized) < 2:
        _raise_contract_error(
            code="INSUFFICIENT_DOMAIN_CONSTRAINTS",
            message="strict_validation requer ao menos uma regra de dominio adicional",
            action="Adicione constraints de dominio alem de source_kind/schema_version.",
        )
    return normalized


def _normalize_contract_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not CONTRACT_ID_RE.match(normalized):
        _raise_contract_error(
            code="INVALID_CONTRACT_ID",
            message="contract_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action=(
                "Padronize contract_id para formato estavel de auditoria "
                "(ex: CONT_STG_OPTIN_V2)."
            ),
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "contract_validation_s2_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S2ContractScaffoldError(code=code, message=message, action=action)
