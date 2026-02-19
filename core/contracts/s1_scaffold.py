"""Sprint 1 scaffold contracts for canonical output validation.

This module defines the stable input/output contract for CONT Sprint 1,
establishing canonical output contract metadata, strict validation flags,
and mandatory lineage requirements.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.contracts.s1")

CONTRACT_VERSION = "cont.s1.v1"
BACKEND_CONT_S1_VALIDATE_ENDPOINT = "/internal/contracts/s1/validate"
CONTRACT_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")

ALLOWED_SOURCE_KINDS = ("pdf", "docx", "pptx", "xlsx", "csv", "api", "manual", "other")


class S1ContractScaffoldError(ValueError):
    """Raised when CONT S1 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S1CanonicalContractScaffoldRequest:
    """Input contract for CONT Sprint 1 scaffold validation."""

    contract_id: str
    dataset_name: str
    source_kind: str
    schema_version: str = "v1"
    strict_validation: bool = True
    lineage_required: bool = True
    owner_team: str = "etl"
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible CONT Sprint 1 contract."""

        return {
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "source_kind": self.source_kind,
            "schema_version": self.schema_version,
            "strict_validation": self.strict_validation,
            "lineage_required": self.lineage_required,
            "owner_team": self.owner_team,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S1CanonicalContractScaffoldResponse:
    """Output contract returned when CONT Sprint 1 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    canonical_contract: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "canonical_contract": self.canonical_contract,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s1_contract_scaffold(
    request: S1CanonicalContractScaffoldRequest,
) -> S1CanonicalContractScaffoldResponse:
    """Build CONT Sprint 1 scaffold contract for canonical output validation.

    Args:
        request: Contract metadata and strict validation policy input.

    Returns:
        S1CanonicalContractScaffoldResponse: Stable scaffold output with
            canonical contract metadata and integration points.

    Raises:
        S1ContractScaffoldError: If one or more CONT Sprint 1 input rules fail.
    """

    correlation_id = request.correlation_id or f"cont-s1-{uuid4().hex[:12]}"
    logger.info(
        "contract_validation_s1_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "contract_id": request.contract_id,
            "dataset_name": request.dataset_name,
            "source_kind": request.source_kind,
            "schema_version": request.schema_version,
            "strict_validation": request.strict_validation,
            "lineage_required": request.lineage_required,
            "owner_team": request.owner_team,
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
    ) = _validate_s1_input(request=request)

    required_fields = ["record_id", "event_ts", "source_id", "payload_checksum"]
    if lineage_required:
        required_fields.append("lineage_ref_id")

    canonical_contract = {
        "contract_id": contract_id,
        "dataset_name": dataset_name,
        "source_kind": source_kind,
        "schema_version": schema_version,
        "strict_validation": strict_validation,
        "lineage_required": lineage_required,
        "owner_team": owner_team,
        "required_fields": required_fields,
        "lineage_policy": "required" if lineage_required else "optional",
        "validation_mode": "strict" if strict_validation else "lenient",
    }

    response = S1CanonicalContractScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        contract_id=contract_id,
        dataset_name=dataset_name,
        canonical_contract=canonical_contract,
        pontos_integracao={
            "cont_s1_validate_endpoint": BACKEND_CONT_S1_VALIDATE_ENDPOINT,
            "contract_validation_service_module": (
                "app.services.contract_validation_service.execute_s1_contract_validation_service"
            ),
            "lineage_policy_module": "core.registry.lineage_policy.evaluate_lineage_policy",
            "registry_types_module": "core.registry.types",
        },
    )
    logger.info(
        "contract_validation_s1_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "contract_id": contract_id,
            "dataset_name": dataset_name,
            "source_kind": source_kind,
            "schema_version": schema_version,
            "lineage_required": lineage_required,
        },
    )
    return response


def _validate_s1_input(
    *,
    request: S1CanonicalContractScaffoldRequest,
) -> tuple[str, str, str, str, bool, bool, str]:
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

    return (
        contract_id,
        dataset_name,
        source_kind,
        schema_version,
        request.strict_validation,
        request.lineage_required,
        owner_team,
    )


def _normalize_contract_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not CONTRACT_ID_RE.match(normalized):
        _raise_contract_error(
            code="INVALID_CONTRACT_ID",
            message="contract_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action=(
                "Padronize contract_id para formato estavel de auditoria "
                "(ex: CONT_STG_OPTIN_V1)."
            ),
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "contract_validation_s1_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S1ContractScaffoldError(code=code, message=message, action=action)
