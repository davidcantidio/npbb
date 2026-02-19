"""Sprint 3 scaffold contracts for confidence policy critical field guardrails.

This module defines the stable input/output contract for CONF Sprint 3,
preparing special rules for critical report fields on top of auto/review/gap
policy routing.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.confidence.s3")

CONTRACT_VERSION = "conf.s3.v1"
BACKEND_CONF_S3_PREPARE_ENDPOINT = "/internal/confidence/s3/prepare"

POLICY_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
FIELD_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")

ALLOWED_ENTITY_KINDS = ("lead", "evento", "ingresso", "generic")
ALLOWED_DECISION_MODES = (
    "critical_fields_guardrails",
    "weighted_critical_fields_guardrails",
)
ALLOWED_CRITICAL_VIOLATION_ROUTES = ("manual_review", "gap", "reject")

MIN_PROBABILITY = 0.0
MAX_PROBABILITY = 1.0
MIN_MAX_MANUAL_REVIEW_QUEUE = 0
MAX_MAX_MANUAL_REVIEW_QUEUE = 100000
MIN_CRITICAL_FIELDS_COUNT = 1
MAX_CRITICAL_FIELDS_COUNT = 64

DEFAULT_CRITICAL_FIELDS_BY_ENTITY_KIND: dict[str, tuple[str, ...]] = {
    "lead": ("nome", "email", "telefone"),
    "evento": ("nome_evento", "data_evento", "local_evento"),
    "ingresso": ("evento_id", "numero_ingresso", "titular_documento"),
    "generic": ("record_id",),
}


class S3ConfidenceScaffoldError(ValueError):
    """Raised when CONF S3 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S3ConfidenceScaffoldRequest:
    """Input contract for CONF Sprint 3 scaffold validation."""

    policy_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v3"
    owner_team: str = "etl"
    field_weights: dict[str, float] | None = None
    default_weight: float = 1.0
    auto_approve_threshold: float = 0.85
    manual_review_threshold: float = 0.60
    gap_threshold: float = 0.40
    missing_field_penalty: float = 0.10
    decision_mode: str = "critical_fields_guardrails"
    gap_escalation_required: bool = True
    max_manual_review_queue: int = 500
    critical_fields: tuple[str, ...] | None = None
    min_critical_fields_present: int = 1
    critical_field_penalty: float = 0.20
    critical_violation_route: str = "manual_review"
    critical_override_required: bool = True
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible CONF Sprint 3 contract."""

        return {
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "entity_kind": self.entity_kind,
            "schema_version": self.schema_version,
            "owner_team": self.owner_team,
            "field_weights": dict(self.field_weights or {}),
            "default_weight": self.default_weight,
            "auto_approve_threshold": self.auto_approve_threshold,
            "manual_review_threshold": self.manual_review_threshold,
            "gap_threshold": self.gap_threshold,
            "missing_field_penalty": self.missing_field_penalty,
            "decision_mode": self.decision_mode,
            "gap_escalation_required": self.gap_escalation_required,
            "max_manual_review_queue": self.max_manual_review_queue,
            "critical_fields": list(self.critical_fields or ()),
            "min_critical_fields_present": self.min_critical_fields_present,
            "critical_field_penalty": self.critical_field_penalty,
            "critical_violation_route": self.critical_violation_route,
            "critical_override_required": self.critical_override_required,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S3ConfidenceScaffoldResponse:
    """Output contract returned when CONF Sprint 3 scaffold is valid."""

    contrato_versao: str
    correlation_id: str
    status: str
    policy_id: str
    dataset_name: str
    decision_policy: dict[str, Any]
    pontos_integracao: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for logs and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "decision_policy": self.decision_policy,
            "pontos_integracao": self.pontos_integracao,
        }


def build_s3_confidence_scaffold(
    request: S3ConfidenceScaffoldRequest,
) -> S3ConfidenceScaffoldResponse:
    """Build CONF Sprint 3 scaffold contract for critical field guardrails.

    Args:
        request: CONF Sprint 3 policy metadata, thresholds, and critical field
            special rules for report-oriented decisions.

    Returns:
        S3ConfidenceScaffoldResponse: Stable scaffold output with decision
            policy metadata and integration points.

    Raises:
        S3ConfidenceScaffoldError: If one or more CONF Sprint 3 input rules fail.
    """

    correlation_id = request.correlation_id or f"conf-s3-{uuid4().hex[:12]}"
    logger.info(
        "confidence_policy_s3_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "policy_id": request.policy_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "decision_mode": request.decision_mode,
            "critical_violation_route": request.critical_violation_route,
            "critical_override_required": request.critical_override_required,
        },
    )

    (
        policy_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        decision_mode,
        auto_approve_threshold,
        manual_review_threshold,
        gap_threshold,
        missing_field_penalty,
        default_weight,
        gap_escalation_required,
        max_manual_review_queue,
        field_weights,
        critical_fields,
        min_critical_fields_present,
        critical_field_penalty,
        critical_violation_route,
        critical_override_required,
    ) = _validate_s3_input(request=request)

    total_weight = sum(field_weights.values())
    normalized_field_weights = (
        {field: round(weight / total_weight, 6) for field, weight in field_weights.items()}
        if total_weight > 0.0
        else {}
    )

    critical_field_rules = {
        field: {
            "required_for_auto_approve": True,
            "missing_route": critical_violation_route,
            "penalty": critical_field_penalty,
        }
        for field in critical_fields
    }

    decision_policy = {
        "policy_id": policy_id,
        "dataset_name": dataset_name,
        "entity_kind": entity_kind,
        "schema_version": schema_version,
        "owner_team": owner_team,
        "decision_mode": decision_mode,
        "scoring_scope": "critical_fields_decision_policy",
        "field_weights": field_weights,
        "normalized_field_weights": normalized_field_weights,
        "field_weights_count": len(field_weights),
        "default_weight": default_weight,
        "missing_field_penalty": missing_field_penalty,
        "thresholds": {
            "auto_approve": auto_approve_threshold,
            "manual_review": manual_review_threshold,
            "gap": gap_threshold,
        },
        "decision_routes": {
            "auto_approve_range": [auto_approve_threshold, MAX_PROBABILITY],
            "manual_review_range": [manual_review_threshold, auto_approve_threshold],
            "gap_range": [gap_threshold, manual_review_threshold],
            "reject_range": [MIN_PROBABILITY, gap_threshold],
        },
        "operational_policy": {
            "gap_escalation_required": gap_escalation_required,
            "max_manual_review_queue": max_manual_review_queue,
        },
        "critical_fields_policy": {
            "critical_fields": critical_fields,
            "critical_fields_count": len(critical_fields),
            "min_critical_fields_present": min_critical_fields_present,
            "critical_field_penalty": critical_field_penalty,
            "critical_violation_route": critical_violation_route,
            "critical_override_required": critical_override_required,
            "critical_field_rules": critical_field_rules,
        },
    }

    response = S3ConfidenceScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        policy_id=policy_id,
        dataset_name=dataset_name,
        decision_policy=decision_policy,
        pontos_integracao={
            "conf_s3_prepare_endpoint": BACKEND_CONF_S3_PREPARE_ENDPOINT,
            "confidence_policy_service_module": (
                "app.services.confidence_policy_service.execute_s3_confidence_policy_service"
            ),
            "confidence_policy_s3_core_module": (
                "core.confidence.s3_core.execute_s3_confidence_policy_main_flow"
            ),
            "confidence_policy_s3_validation_module": (
                "core.confidence.s3_validation.validate_s3_confidence_output_contract"
            ),
        },
    )
    logger.info(
        "confidence_policy_s3_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "policy_id": policy_id,
            "dataset_name": dataset_name,
            "entity_kind": entity_kind,
            "decision_mode": decision_mode,
            "critical_fields_count": len(critical_fields),
            "critical_violation_route": critical_violation_route,
        },
    )
    return response


def _validate_s3_input(
    *,
    request: S3ConfidenceScaffoldRequest,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
    str,
    float,
    float,
    float,
    float,
    float,
    bool,
    int,
    dict[str, float],
    list[str],
    int,
    float,
    str,
    bool,
]:
    policy_id = _normalize_policy_id(request.policy_id)

    dataset_name = request.dataset_name.strip()
    if len(dataset_name) < 3:
        _raise_confidence_error(
            code="INVALID_DATASET_NAME",
            message="dataset_name invalido: informe nome com ao menos 3 caracteres",
            action="Defina dataset_name estavel para rastreabilidade da politica de decisao.",
        )

    entity_kind = request.entity_kind.strip().lower()
    if entity_kind not in ALLOWED_ENTITY_KINDS:
        _raise_confidence_error(
            code="INVALID_ENTITY_KIND",
            message=f"entity_kind invalido: {request.entity_kind}",
            action="Use entity_kind suportado: lead, evento, ingresso ou generic.",
        )

    schema_version = request.schema_version.strip().lower()
    if not SCHEMA_VERSION_RE.match(schema_version):
        _raise_confidence_error(
            code="INVALID_SCHEMA_VERSION",
            message=f"schema_version invalida: {request.schema_version}",
            action="Use schema_version no formato vN (ex: v3).",
        )

    owner_team = request.owner_team.strip().lower()
    if len(owner_team) < 2:
        _raise_confidence_error(
            code="INVALID_OWNER_TEAM",
            message="owner_team invalido: informe identificador com ao menos 2 caracteres",
            action="Defina owner_team para direcionar ownership operacional da politica.",
        )

    decision_mode = request.decision_mode.strip().lower()
    if decision_mode not in ALLOWED_DECISION_MODES:
        _raise_confidence_error(
            code="INVALID_DECISION_MODE",
            message=f"decision_mode invalido: {request.decision_mode}",
            action=(
                "Use decision_mode suportado: critical_fields_guardrails ou "
                "weighted_critical_fields_guardrails."
            ),
        )

    auto_approve_threshold = _validate_probability(
        field_name="auto_approve_threshold",
        value=request.auto_approve_threshold,
    )
    manual_review_threshold = _validate_probability(
        field_name="manual_review_threshold",
        value=request.manual_review_threshold,
    )
    gap_threshold = _validate_probability(
        field_name="gap_threshold",
        value=request.gap_threshold,
    )
    if not (gap_threshold <= manual_review_threshold <= auto_approve_threshold):
        _raise_confidence_error(
            code="INVALID_DECISION_THRESHOLDS",
            message=(
                "limiares invalidos: esperado gap_threshold <= manual_review_threshold <= "
                "auto_approve_threshold"
            ),
            action=(
                "Ajuste limiares para manter ordem de decisao auto/review/gap."
            ),
        )

    missing_field_penalty = _validate_probability(
        field_name="missing_field_penalty",
        value=request.missing_field_penalty,
    )
    default_weight = _validate_probability(
        field_name="default_weight",
        value=request.default_weight,
    )
    if default_weight <= 0.0:
        _raise_confidence_error(
            code="INVALID_DEFAULT_WEIGHT",
            message="default_weight deve ser maior que zero",
            action="Informe default_weight no intervalo (0.0, 1.0].",
        )

    if not isinstance(request.gap_escalation_required, bool):
        _raise_confidence_error(
            code="INVALID_GAP_ESCALATION_REQUIRED_FLAG",
            message="gap_escalation_required deve ser booleano",
            action="Ajuste gap_escalation_required para true/false.",
        )

    if not isinstance(request.max_manual_review_queue, int):
        _raise_confidence_error(
            code="INVALID_MAX_MANUAL_REVIEW_QUEUE_TYPE",
            message="max_manual_review_queue deve ser inteiro",
            action="Informe max_manual_review_queue como inteiro >= 0.",
        )
    if (
        request.max_manual_review_queue < MIN_MAX_MANUAL_REVIEW_QUEUE
        or request.max_manual_review_queue > MAX_MAX_MANUAL_REVIEW_QUEUE
    ):
        _raise_confidence_error(
            code="INVALID_MAX_MANUAL_REVIEW_QUEUE_RANGE",
            message=(
                "max_manual_review_queue fora do intervalo permitido: "
                f"{request.max_manual_review_queue}"
            ),
            action="Use max_manual_review_queue no intervalo de 0 a 100000.",
        )

    critical_fields = _normalize_critical_fields(
        critical_fields=request.critical_fields,
        entity_kind=entity_kind,
    )

    if not isinstance(request.min_critical_fields_present, int):
        _raise_confidence_error(
            code="INVALID_MIN_CRITICAL_FIELDS_PRESENT_TYPE",
            message="min_critical_fields_present deve ser inteiro",
            action="Informe min_critical_fields_present como inteiro >= 1.",
        )
    if request.min_critical_fields_present < MIN_CRITICAL_FIELDS_COUNT:
        _raise_confidence_error(
            code="INVALID_MIN_CRITICAL_FIELDS_PRESENT",
            message="min_critical_fields_present deve ser >= 1",
            action="Use min_critical_fields_present no intervalo de 1 ate o total de campos criticos.",
        )
    if request.min_critical_fields_present > len(critical_fields):
        _raise_confidence_error(
            code="INVALID_MIN_CRITICAL_FIELDS_PRESENT",
            message=(
                "min_critical_fields_present nao pode ser maior que o total de campos criticos"
            ),
            action="Ajuste min_critical_fields_present para valor <= quantidade de critical_fields.",
        )

    critical_field_penalty = _validate_probability(
        field_name="critical_field_penalty",
        value=request.critical_field_penalty,
    )

    critical_violation_route = request.critical_violation_route.strip().lower()
    if critical_violation_route not in ALLOWED_CRITICAL_VIOLATION_ROUTES:
        _raise_confidence_error(
            code="INVALID_CRITICAL_VIOLATION_ROUTE",
            message=f"critical_violation_route invalido: {request.critical_violation_route}",
            action="Use critical_violation_route suportado: manual_review, gap ou reject.",
        )

    if not isinstance(request.critical_override_required, bool):
        _raise_confidence_error(
            code="INVALID_CRITICAL_OVERRIDE_REQUIRED_FLAG",
            message="critical_override_required deve ser booleano",
            action="Ajuste critical_override_required para true/false.",
        )

    field_weights = _normalize_field_weights(request.field_weights)

    return (
        policy_id,
        dataset_name,
        entity_kind,
        schema_version,
        owner_team,
        decision_mode,
        auto_approve_threshold,
        manual_review_threshold,
        gap_threshold,
        missing_field_penalty,
        default_weight,
        request.gap_escalation_required,
        request.max_manual_review_queue,
        field_weights,
        critical_fields,
        request.min_critical_fields_present,
        critical_field_penalty,
        critical_violation_route,
        request.critical_override_required,
    )


def _normalize_policy_id(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not POLICY_ID_RE.match(normalized):
        _raise_confidence_error(
            code="INVALID_POLICY_ID",
            message="policy_id invalido: use 3-160 chars com A-Z, 0-9 e underscore",
            action=(
                "Padronize policy_id para formato estavel de auditoria "
                "(ex: CONF_REPORT_POLICY_V3)."
            ),
        )
    return normalized


def _normalize_field_weights(raw_weights: dict[str, float] | None) -> dict[str, float]:
    if raw_weights is None:
        return {}
    if not isinstance(raw_weights, dict):
        _raise_confidence_error(
            code="INVALID_FIELD_WEIGHTS_TYPE",
            message="field_weights deve ser dicionario no formato campo->peso",
            action="Informe field_weights como objeto com chaves de campo e pesos numericos.",
        )

    normalized: dict[str, float] = {}
    for raw_field, raw_weight in raw_weights.items():
        field_name = (raw_field or "").strip().replace(" ", "_").lower()
        field_name = re.sub(r"_+", "_", field_name)
        if not FIELD_NAME_RE.match(field_name):
            _raise_confidence_error(
                code="INVALID_FIELD_NAME",
                message=f"campo invalido em field_weights: {raw_field}",
                action=(
                    "Use nomes de campo com letras, numeros e underscore "
                    "(2-64 caracteres)."
                ),
            )

        weight = _validate_probability(field_name=f"field_weights.{field_name}", value=raw_weight)
        if weight <= 0.0:
            _raise_confidence_error(
                code="INVALID_FIELD_WEIGHT",
                message=f"peso invalido para campo {field_name}: {raw_weight}",
                action="Informe pesos de campo no intervalo (0.0, 1.0].",
            )
        normalized[field_name] = weight

    return dict(sorted(normalized.items()))


def _normalize_critical_fields(
    *,
    critical_fields: tuple[str, ...] | None,
    entity_kind: str,
) -> list[str]:
    source_fields = critical_fields or DEFAULT_CRITICAL_FIELDS_BY_ENTITY_KIND.get(entity_kind, ("record_id",))

    if not isinstance(source_fields, tuple):
        _raise_confidence_error(
            code="INVALID_CRITICAL_FIELDS_TYPE",
            message="critical_fields deve ser tupla de campos",
            action="Informe critical_fields como tuple[str, ...] com nomes de campo validos.",
        )

    normalized: list[str] = []
    for raw_field in source_fields:
        field_name = (raw_field or "").strip().replace(" ", "_").lower()
        field_name = re.sub(r"_+", "_", field_name)
        if not FIELD_NAME_RE.match(field_name):
            _raise_confidence_error(
                code="INVALID_CRITICAL_FIELD_NAME",
                message=f"campo critico invalido: {raw_field}",
                action="Use critical_fields com nomes validos (letras, numeros e underscore).",
            )
        if field_name not in normalized:
            normalized.append(field_name)

    if len(normalized) < MIN_CRITICAL_FIELDS_COUNT:
        _raise_confidence_error(
            code="INVALID_CRITICAL_FIELDS",
            message="critical_fields deve conter ao menos um campo",
            action="Defina ao menos um campo critico para aplicar regras especiais da sprint 3.",
        )
    if len(normalized) > MAX_CRITICAL_FIELDS_COUNT:
        _raise_confidence_error(
            code="INVALID_CRITICAL_FIELDS",
            message=f"critical_fields excede limite de {MAX_CRITICAL_FIELDS_COUNT} campos",
            action="Reduza critical_fields para no maximo 64 campos por politica.",
        )

    return normalized


def _validate_probability(*, field_name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _raise_confidence_error(
            code="INVALID_NUMERIC_VALUE",
            message=f"{field_name} deve ser numerico",
            action=f"Ajuste {field_name} para valor numerico entre 0.0 e 1.0.",
        )

    numeric_value = float(value)
    if numeric_value < MIN_PROBABILITY or numeric_value > MAX_PROBABILITY:
        _raise_confidence_error(
            code="INVALID_NUMERIC_RANGE",
            message=f"{field_name} fora do intervalo permitido: {value}",
            action=f"Use {field_name} no intervalo de 0.0 a 1.0.",
        )
    return round(numeric_value, 6)


def _raise_confidence_error(*, code: str, message: str, action: str) -> None:
    raise S3ConfidenceScaffoldError(code=code, message=message, action=action)
