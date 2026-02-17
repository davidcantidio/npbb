"""Sprint 3 scaffold contracts for field/metric lineage enforcement.

This module defines the stable input/output contract for CONT Sprint 3,
preparing mandatory lineage enforcement rules per field and per metric with
actionable diagnostics and operational integration points.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.contracts.s3")

CONTRACT_VERSION = "cont.s3.v1"
BACKEND_CONT_S3_PREPARE_ENDPOINT = "/internal/contracts/s3/prepare"
CONTRACT_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
LINEAGE_REF_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]{2,127}$")

ALLOWED_SOURCE_KINDS = ("pdf", "docx", "pptx", "xlsx", "csv", "api", "manual", "other")


class S3ContractScaffoldError(ValueError):
    """Raised when CONT S3 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3CanonicalContractScaffoldRequest:
    """Input contract for CONT Sprint 3 scaffold validation."""

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
    lineage_field_requirements: dict[str, tuple[str, ...]] | None = None
    metric_lineage_requirements: dict[str, tuple[str, ...]] | None = None
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible CONT Sprint 3 contract."""

        return {
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
            "owner_team": self.owner_team,
            "schema_required_fields": list(self.schema_required_fields),
            "lineage_field_requirements": {
                key: list(values)
                for key, values in (self.lineage_field_requirements or {}).items()
            },
            "metric_lineage_requirements": {
                key: list(values)
                for key, values in (self.metric_lineage_requirements or {}).items()
            },
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3CanonicalContractScaffoldResponse:
    """Output contract returned when CONT Sprint 3 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    lineage_profile: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "lineage_profile": self.lineage_profile,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s3_contract_scaffold(
    request: S3CanonicalContractScaffoldRequest,
) -> S3CanonicalContractScaffoldResponse:
    """Build CONT Sprint 3 scaffold contract for lineage-by-field/metric rules.

    Args:
        request: Contract metadata and lineage enforcement policy input.

    Returns:
        S3CanonicalContractScaffoldResponse: Stable scaffold output with
            lineage profile and integration points.

    Raises:
        S3ContractScaffoldError: If one or more CONT Sprint 3 input rules fail.
    """

    correlation_id = request.correlation_id or f"cont-s3-{uuid4().hex[:12]}"
    logger.info(
        "contract_validation_s3_scaffold_input_received",
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
        lineage_field_requirements,
        metric_lineage_requirements,
    ) = _validate_s3_input(request=request)

    lineage_profile = {
        "contract_id": contract_id,
        "dataset_name": dataset_name,
        "source_kind": source_kind,
        "schema_version": schema_version,
        "strict_validation": strict_validation,
        "lineage_required": lineage_required,
        "owner_team": owner_team,
        "enforcement_scope": "field_and_metric_lineage",
        "schema_required_fields": schema_required_fields,
        "lineage_field_requirements": lineage_field_requirements,
        "metric_lineage_requirements": metric_lineage_requirements,
        "field_lineage_rules_count": len(lineage_field_requirements),
        "metric_lineage_rules_count": len(metric_lineage_requirements),
    }

    response = S3CanonicalContractScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        contract_id=contract_id,
        dataset_name=dataset_name,
        lineage_profile=lineage_profile,
        pontos_integracao={
            "cont_s3_prepare_endpoint": BACKEND_CONT_S3_PREPARE_ENDPOINT,
            "contract_validation_service_module": (
                "app.services.contract_validation_service.execute_s3_contract_validation_service"
            ),
            "contract_validation_s3_core_module": (
                "core.contracts.s3_core.execute_s3_contract_validation_main_flow"
            ),
            "lineage_registry_module": "core.registry.lineage_policy.evaluate_lineage_policy",
        },
    )
    logger.info(
        "contract_validation_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "contract_id": contract_id,
            "dataset_name": dataset_name,
            "source_kind": source_kind,
            "schema_version": schema_version,
            "field_lineage_rules_count": len(lineage_field_requirements),
            "metric_lineage_rules_count": len(metric_lineage_requirements),
        },
    )
    return response


def _validate_s3_input(
    *,
    request: S3CanonicalContractScaffoldRequest,
) -> tuple[
    str,
    str,
    str,
    str,
    bool,
    bool,
    str,
    list[str],
    dict[str, list[str]],
    dict[str, list[str]],
]:
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
    lineage_field_requirements = _normalize_lineage_map(
        requirements=request.lineage_field_requirements,
        requirement_name="lineage_field_requirements",
        require_schema_membership=True,
        schema_required_fields=schema_required_fields,
    )
    metric_lineage_requirements = _normalize_lineage_map(
        requirements=request.metric_lineage_requirements,
        requirement_name="metric_lineage_requirements",
        require_schema_membership=False,
        schema_required_fields=schema_required_fields,
    )

    if request.lineage_required and (
        len(lineage_field_requirements) == 0 or len(metric_lineage_requirements) == 0
    ):
        _raise_contract_error(
            code="INSUFFICIENT_LINEAGE_REQUIREMENTS",
            message="lineage_required=true exige regras por campo e por metrica",
            action="Defina lineage_field_requirements e metric_lineage_requirements com referencias validas.",
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
        lineage_field_requirements,
        metric_lineage_requirements,
    )


def _normalize_required_fields(*, fields: tuple[str, ...], lineage_required: bool) -> list[str]:
    if not isinstance(fields, tuple) or len(fields) == 0:
        _raise_contract_error(
            code="INVALID_REQUIRED_FIELDS",
            message="schema_required_fields deve conter ao menos um campo",
            action="Informe campos obrigatorios do schema canonico na entrada do S3.",
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


def _normalize_lineage_map(
    *,
    requirements: dict[str, tuple[str, ...]] | None,
    requirement_name: str,
    require_schema_membership: bool,
    schema_required_fields: list[str],
) -> dict[str, list[str]]:
    if requirements is None:
        return {}
    if not isinstance(requirements, dict):
        _raise_contract_error(
            code="INVALID_LINEAGE_REQUIREMENTS",
            message=f"{requirement_name} deve ser dicionario chave -> refs",
            action=f"Ajuste {requirement_name} para dict[str, tuple[str, ...]].",
        )

    normalized: dict[str, list[str]] = {}
    for raw_name, refs in requirements.items():
        name = str(raw_name).strip()
        if not name:
            _raise_contract_error(
                code="INVALID_LINEAGE_REQUIREMENTS",
                message=f"{requirement_name} contem chave vazia",
                action="Defina campos/metricas validos para regras de linhagem.",
            )
        if require_schema_membership and name not in schema_required_fields:
            _raise_contract_error(
                code="LINEAGE_FIELD_NOT_IN_SCHEMA",
                message=f"Campo de linhagem nao pertence ao schema: {name}",
                action="Inclua o campo no schema ou remova regra de linhagem inconsistente.",
            )
        if not isinstance(refs, tuple) or len(refs) == 0:
            _raise_contract_error(
                code="INVALID_LINEAGE_REFERENCES",
                message=f"{requirement_name}[{name}] deve conter ao menos uma referencia",
                action="Informe refs de linhagem no formato sistema.tabela.campo.",
            )

        refs_normalized: list[str] = []
        for raw_ref in refs:
            ref = str(raw_ref).strip().lower()
            if not LINEAGE_REF_RE.match(ref):
                _raise_contract_error(
                    code="INVALID_LINEAGE_REFERENCE_FORMAT",
                    message=f"Referencia de linhagem invalida: {raw_ref}",
                    action="Use referencias com padrao estavel (ex: crm.orders.total_amount).",
                )
            if ref not in refs_normalized:
                refs_normalized.append(ref)
        normalized[name] = refs_normalized
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
                "(ex: CONT_STG_OPTIN_V3)."
            ),
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "contract_validation_s3_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S3ContractScaffoldError(code=code, message=message, action=action)
