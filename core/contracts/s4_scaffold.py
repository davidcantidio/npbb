"""Sprint 4 scaffold contracts for version compatibility and regression gates.

This module defines the stable input/output contract for CONT Sprint 4,
preparing compatibility policies across contract versions and regression gates
for rollout safety.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.contracts.s4")

CONTRACT_VERSION = "cont.s4.v1"
BACKEND_CONT_S4_PREPARE_ENDPOINT = "/internal/contracts/s4/prepare"
CONTRACT_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
LINEAGE_REF_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]{2,127}$")
REGRESSION_SUITE_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")

ALLOWED_SOURCE_KINDS = ("pdf", "docx", "pptx", "xlsx", "csv", "api", "manual", "other")
ALLOWED_COMPATIBILITY_MODES = (
    "strict_backward",
    "backward_with_deprecation",
    "forward_and_backward",
)
ALLOWED_BREAKING_CHANGE_POLICIES = ("block", "allow_with_waiver")
MIN_MAX_REGRESSION_FAILURES = 0
MAX_MAX_REGRESSION_FAILURES = 100
MIN_DEPRECATION_WINDOW_DAYS = 0
MAX_DEPRECATION_WINDOW_DAYS = 3650


class S4ContractScaffoldError(ValueError):
    """Raised when CONT S4 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S4CanonicalContractScaffoldRequest:
    """Input contract for CONT Sprint 4 scaffold validation."""

    contract_id: str
    dataset_name: str
    source_kind: str
    schema_version: str = "v4"
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
    compatibility_mode: str = "strict_backward"
    previous_contract_versions: tuple[str, ...] = ("v3",)
    regression_gate_required: bool = True
    regression_suite_version: str = "s4"
    max_regression_failures: int = 0
    breaking_change_policy: str = "block"
    deprecation_window_days: int = 0
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible CONT Sprint 4 contract."""

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
            "compatibility_mode": self.compatibility_mode,
            "previous_contract_versions": list(self.previous_contract_versions),
            "regression_gate_required": self.regression_gate_required,
            "regression_suite_version": self.regression_suite_version,
            "max_regression_failures": self.max_regression_failures,
            "breaking_change_policy": self.breaking_change_policy,
            "deprecation_window_days": self.deprecation_window_days,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S4CanonicalContractScaffoldResponse:
    """Output contract returned when CONT Sprint 4 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    versioning_profile: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "versioning_profile": self.versioning_profile,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s4_contract_scaffold(
    request: S4CanonicalContractScaffoldRequest,
) -> S4CanonicalContractScaffoldResponse:
    """Build CONT Sprint 4 scaffold contract for version compatibility gates.

    Args:
        request: Contract metadata, lineage rules, and compatibility/regression
            policy input for Sprint 4.

    Returns:
        S4CanonicalContractScaffoldResponse: Stable scaffold output with
            versioning profile and integration points.

    Raises:
        S4ContractScaffoldError: If one or more CONT Sprint 4 input rules fail.
    """

    correlation_id = request.correlation_id or f"cont-s4-{uuid4().hex[:12]}"
    logger.info(
        "contract_validation_s4_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "contract_id": request.contract_id,
            "dataset_name": request.dataset_name,
            "source_kind": request.source_kind,
            "schema_version": request.schema_version,
            "compatibility_mode": request.compatibility_mode,
            "regression_gate_required": request.regression_gate_required,
            "regression_suite_version": request.regression_suite_version,
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
        compatibility_mode,
        previous_contract_versions,
        regression_gate_required,
        regression_suite_version,
        max_regression_failures,
        breaking_change_policy,
        deprecation_window_days,
    ) = _validate_s4_input(request=request)

    versioning_profile = {
        "contract_id": contract_id,
        "dataset_name": dataset_name,
        "source_kind": source_kind,
        "schema_version": schema_version,
        "strict_validation": strict_validation,
        "lineage_required": lineage_required,
        "owner_team": owner_team,
        "schema_required_fields": schema_required_fields,
        "lineage_field_requirements": lineage_field_requirements,
        "metric_lineage_requirements": metric_lineage_requirements,
        "field_lineage_rules_count": len(lineage_field_requirements),
        "metric_lineage_rules_count": len(metric_lineage_requirements),
        "compatibility_scope": "contract_version_and_regression_gate",
        "compatibility_mode": compatibility_mode,
        "previous_contract_versions": previous_contract_versions,
        "regression_gate_required": regression_gate_required,
        "regression_suite_version": regression_suite_version,
        "max_regression_failures": max_regression_failures,
        "breaking_change_policy": breaking_change_policy,
        "deprecation_window_days": deprecation_window_days,
    }

    response = S4CanonicalContractScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        contract_id=contract_id,
        dataset_name=dataset_name,
        versioning_profile=versioning_profile,
        pontos_integracao={
            "cont_s4_prepare_endpoint": BACKEND_CONT_S4_PREPARE_ENDPOINT,
            "contract_validation_service_module": (
                "app.services.contract_validation_service.execute_s4_contract_validation_service"
            ),
            "contract_validation_s4_core_module": (
                "core.contracts.s4_core.execute_s4_contract_validation_main_flow"
            ),
            "contract_validation_s4_validation_module": (
                "core.contracts.s4_validation.validate_s4_contract_input_contract"
            ),
            "contract_registry_module": "core.registry.contract_registry",
        },
    )
    logger.info(
        "contract_validation_s4_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "contract_id": contract_id,
            "dataset_name": dataset_name,
            "schema_version": schema_version,
            "compatibility_mode": compatibility_mode,
            "regression_gate_required": regression_gate_required,
            "previous_contract_versions_count": len(previous_contract_versions),
        },
    )
    return response


def _validate_s4_input(
    *,
    request: S4CanonicalContractScaffoldRequest,
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
    str,
    list[str],
    bool,
    str,
    int,
    str,
    int,
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
            action="Use schema_version no formato vN (ex: v3, v4).",
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

    compatibility_mode = request.compatibility_mode.strip().lower()
    if compatibility_mode not in ALLOWED_COMPATIBILITY_MODES:
        _raise_contract_error(
            code="INVALID_COMPATIBILITY_MODE",
            message=f"compatibility_mode invalido: {request.compatibility_mode}",
            action=(
                "Use compatibility_mode suportado: strict_backward, "
                "backward_with_deprecation ou forward_and_backward."
            ),
        )

    previous_contract_versions = _normalize_previous_contract_versions(
        versions=request.previous_contract_versions,
        schema_version=schema_version,
    )
    if compatibility_mode == "strict_backward" and len(previous_contract_versions) == 0:
        _raise_contract_error(
            code="MISSING_PREVIOUS_CONTRACT_VERSION",
            message="strict_backward exige ao menos uma versao anterior para checagem",
            action="Informe previous_contract_versions com versoes anteriores suportadas (ex: v3).",
        )

    if not isinstance(request.regression_gate_required, bool):
        _raise_contract_error(
            code="INVALID_REGRESSION_GATE_FLAG",
            message="regression_gate_required deve ser booleano",
            action="Ajuste regression_gate_required para true/false.",
        )

    regression_suite_version = request.regression_suite_version.strip().lower()
    if not REGRESSION_SUITE_RE.match(regression_suite_version):
        _raise_contract_error(
            code="INVALID_REGRESSION_SUITE_VERSION",
            message=f"regression_suite_version invalida: {request.regression_suite_version}",
            action="Use regression_suite_version no formato estavel (ex: s4, suite_2026_02).",
        )

    if not isinstance(request.max_regression_failures, int):
        _raise_contract_error(
            code="INVALID_MAX_REGRESSION_FAILURES_TYPE",
            message="max_regression_failures deve ser inteiro",
            action="Ajuste max_regression_failures para inteiro entre 0 e 100.",
        )
    max_regression_failures = request.max_regression_failures
    if (
        max_regression_failures < MIN_MAX_REGRESSION_FAILURES
        or max_regression_failures > MAX_MAX_REGRESSION_FAILURES
    ):
        _raise_contract_error(
            code="INVALID_MAX_REGRESSION_FAILURES",
            message=f"max_regression_failures fora do intervalo suportado: {max_regression_failures}",
            action=(
                "Use max_regression_failures entre "
                f"{MIN_MAX_REGRESSION_FAILURES} e {MAX_MAX_REGRESSION_FAILURES}."
            ),
        )
    if not request.regression_gate_required and max_regression_failures != 0:
        _raise_contract_error(
            code="REGRESSION_GATE_DISABLED_REQUIRES_ZERO_MAX_FAILURES",
            message="regression_gate_required=false exige max_regression_failures=0",
            action="Defina max_regression_failures=0 ou habilite regression_gate_required.",
        )

    breaking_change_policy = request.breaking_change_policy.strip().lower()
    if breaking_change_policy not in ALLOWED_BREAKING_CHANGE_POLICIES:
        _raise_contract_error(
            code="INVALID_BREAKING_CHANGE_POLICY",
            message=f"breaking_change_policy invalida: {request.breaking_change_policy}",
            action="Use breaking_change_policy suportada: block ou allow_with_waiver.",
        )
    if request.strict_validation and breaking_change_policy == "allow_with_waiver":
        _raise_contract_error(
            code="STRICT_VALIDATION_CONFLICTING_BREAKING_CHANGE_POLICY",
            message="strict_validation=true nao permite breaking_change_policy=allow_with_waiver",
            action="Use breaking_change_policy=block ou desative strict_validation para modo de waiver.",
        )

    if not isinstance(request.deprecation_window_days, int):
        _raise_contract_error(
            code="INVALID_DEPRECATION_WINDOW_DAYS_TYPE",
            message="deprecation_window_days deve ser inteiro",
            action="Ajuste deprecation_window_days para inteiro entre 0 e 3650.",
        )
    deprecation_window_days = request.deprecation_window_days
    if (
        deprecation_window_days < MIN_DEPRECATION_WINDOW_DAYS
        or deprecation_window_days > MAX_DEPRECATION_WINDOW_DAYS
    ):
        _raise_contract_error(
            code="INVALID_DEPRECATION_WINDOW_DAYS",
            message=f"deprecation_window_days fora do intervalo suportado: {deprecation_window_days}",
            action=(
                "Use deprecation_window_days entre "
                f"{MIN_DEPRECATION_WINDOW_DAYS} e {MAX_DEPRECATION_WINDOW_DAYS}."
            ),
        )
    if compatibility_mode == "backward_with_deprecation" and deprecation_window_days <= 0:
        _raise_contract_error(
            code="DEPRECATION_MODE_REQUIRES_WINDOW",
            message="backward_with_deprecation exige deprecation_window_days > 0",
            action="Defina deprecation_window_days com janela de deprecacao valida.",
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
        compatibility_mode,
        previous_contract_versions,
        request.regression_gate_required,
        regression_suite_version,
        max_regression_failures,
        breaking_change_policy,
        deprecation_window_days,
    )


def _normalize_required_fields(*, fields: tuple[str, ...], lineage_required: bool) -> list[str]:
    if not isinstance(fields, tuple) or len(fields) == 0:
        _raise_contract_error(
            code="INVALID_REQUIRED_FIELDS",
            message="schema_required_fields deve conter ao menos um campo",
            action="Informe campos obrigatorios do schema canonico na entrada do S4.",
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


def _normalize_previous_contract_versions(
    *,
    versions: tuple[str, ...],
    schema_version: str,
) -> list[str]:
    if not isinstance(versions, tuple):
        _raise_contract_error(
            code="INVALID_PREVIOUS_CONTRACT_VERSIONS",
            message="previous_contract_versions deve ser tupla de versoes",
            action="Use previous_contract_versions no formato tuple[str, ...] (ex: ('v3',)).",
        )

    normalized: list[str] = []
    for raw_version in versions:
        version = str(raw_version).strip().lower()
        if not version:
            continue
        if not SCHEMA_VERSION_RE.match(version):
            _raise_contract_error(
                code="INVALID_PREVIOUS_CONTRACT_VERSION_FORMAT",
                message=f"Versao anterior invalida: {raw_version}",
                action="Use versoes no formato vN em previous_contract_versions (ex: v2, v3).",
            )
        if version == schema_version:
            _raise_contract_error(
                code="PREVIOUS_VERSION_EQUALS_CURRENT_VERSION",
                message=f"Versao anterior nao pode ser igual a schema_version atual: {version}",
                action="Informe somente versoes anteriores diferentes da versao atual.",
            )
        if version not in normalized:
            normalized.append(version)

    if len(normalized) == 0:
        _raise_contract_error(
            code="MISSING_PREVIOUS_CONTRACT_VERSION",
            message="previous_contract_versions deve conter ao menos uma versao anterior",
            action="Informe previous_contract_versions com versoes anteriores suportadas (ex: v3).",
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
                "(ex: CONT_STG_OPTIN_V4)."
            ),
        )
    return normalized


def _raise_contract_error(*, code: str, message: str, action: str) -> None:
    logger.warning(
        "contract_validation_s4_scaffold_contract_error",
        extra={
            "error_code": code,
            "error_message": message,
            "recommended_action": action,
        },
    )
    raise S4ContractScaffoldError(code=code, message=message, action=action)
