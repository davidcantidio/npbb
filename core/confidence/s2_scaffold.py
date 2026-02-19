"""Sprint 2 scaffold contracts for confidence decision policy triage.

This module defines the stable input/output contract for CONF Sprint 2,
establishing decision routes for `auto_approve`, `manual_review`, and `gap`
with operational policies required by the next sprint tasks.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


logger = logging.getLogger("npbb.core.confidence.s2")

CONTRACT_VERSION = "conf.s2.v1"
BACKEND_CONF_S2_PREPARE_ENDPOINT = "/internal/confidence/s2/prepare"

POLICY_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
SCHEMA_VERSION_RE = re.compile(r"^v[0-9]+$")
FIELD_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")

ALLOWED_ENTITY_KINDS = ("lead", "evento", "ingresso", "generic")
ALLOWED_DECISION_MODES = ("auto_review_gap", "weighted_auto_review_gap")

MIN_PROBABILITY = 0.0
MAX_PROBABILITY = 1.0
MIN_MAX_MANUAL_REVIEW_QUEUE = 0
MAX_MAX_MANUAL_REVIEW_QUEUE = 100000


class S2ConfidenceScaffoldError(ValueError):
    """Raised when CONF S2 scaffold contract input is invalid."""

    def __init__(self, *, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        return {"code": self.code, "message": self.message, "action": self.action}


@dataclass(frozen=True, slots=True)
class S2ConfidenceScaffoldRequest:
    """Input contract for CONF Sprint 2 scaffold validation."""

    policy_id: str
    dataset_name: str
    entity_kind: str = "lead"
    schema_version: str = "v2"
    owner_team: str = "etl"
    field_weights: dict[str, float] | None = None
    default_weight: float = 1.0
    auto_approve_threshold: float = 0.85
    manual_review_threshold: float = 0.60
    gap_threshold: float = 0.40
    missing_field_penalty: float = 0.10
    decision_mode: str = "auto_review_gap"
    gap_escalation_required: bool = True
    max_manual_review_queue: int = 500
    correlation_id: str | None = None

    def to_backend_payload(self) -> dict[str, Any]:
        """Serialize request in backend-compatible CONF Sprint 2 contract."""

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
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class S2ConfidenceScaffoldResponse:
    """Output contract returned when CONF Sprint 2 scaffold is valid."""

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


def build_s2_confidence_scaffold(
    request: S2ConfidenceScaffoldRequest,
) -> S2ConfidenceScaffoldResponse:
    """Build CONF Sprint 2 scaffold contract for decision policy triage.

    Args:
        request: CONF Sprint 2 policy metadata and thresholds used by
            auto/review/gap decision policy.

    Returns:
        S2ConfidenceScaffoldResponse: Stable scaffold output with decision
            policy metadata and integration points.

    Raises:
        S2ConfidenceScaffoldError: If one or more CONF Sprint 2 input rules fail.
    """

    correlation_id = request.correlation_id or f"conf-s2-{uuid4().hex[:12]}"
    logger.info(
        "confidence_policy_s2_scaffold_input_received",
        extra={
            "correlation_id": correlation_id,
            "policy_id": request.policy_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "decision_mode": request.decision_mode,
            "gap_escalation_required": request.gap_escalation_required,
            "max_manual_review_queue": request.max_manual_review_queue,
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
    ) = _validate_s2_input(request=request)

    total_weight = sum(field_weights.values())
    normalized_field_weights = (
        {field: round(weight / total_weight, 6) for field, weight in field_weights.items()}
        if total_weight > 0.0
        else {}
    )

    decision_policy = {
        "policy_id": policy_id,
        "dataset_name": dataset_name,
        "entity_kind": entity_kind,
        "schema_version": schema_version,
        "owner_team": owner_team,
        "decision_mode": decision_mode,
        "scoring_scope": "field_level_decision_policy",
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
    }

    response = S2ConfidenceScaffoldResponse(
        contrato_versao=CONTRACT_VERSION,
        correlation_id=correlation_id,
        status="ready",
        policy_id=policy_id,
        dataset_name=dataset_name,
        decision_policy=decision_policy,
        pontos_integracao={
            "conf_s2_prepare_endpoint": BACKEND_CONF_S2_PREPARE_ENDPOINT,
            "confidence_policy_service_module": (
                "app.services.confidence_policy_service.execute_s2_confidence_policy_service"
            ),
            "confidence_policy_s2_core_module": (
                "core.confidence.s2_core.execute_s2_confidence_policy_main_flow"
            ),
            "confidence_policy_s2_validation_module": (
                "core.confidence.s2_validation.validate_s2_confidence_output_contract"
            ),
        },
    )
    logger.info(
        "confidence_policy_s2_scaffold_ready",
        extra={
            "correlation_id": correlation_id,
            "policy_id": policy_id,
            "dataset_name": dataset_name,
            "entity_kind": entity_kind,
            "decision_mode": decision_mode,
            "field_weights_count": len(field_weights),
            "gap_escalation_required": gap_escalation_required,
        },
    )
    return response


def _validate_s2_input(
    *,
    request: S2ConfidenceScaffoldRequest,
) -> tuple[str, str, str, str, str, str, float, float, float, float, float, bool, int, dict[str, float]]:
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
            action="Use schema_version no formato vN (ex: v2).",
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
                "Use decision_mode suportado: auto_review_gap ou "
                "weighted_auto_review_gap."
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
                "(ex: CONF_LEAD_POLICY_V2)."
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
    raise S2ConfidenceScaffoldError(code=code, message=message, action=action)
