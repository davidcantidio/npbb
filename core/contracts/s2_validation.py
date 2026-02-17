"""Validation contracts for CONT Sprint 2 strict schema/domain flow.

This module centralizes CONT Sprint 2 input/output validation used by tests
and integration checks. It provides structured actionable errors with
correlation and observability identifiers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .s2_core import S2CanonicalContractCoreInput
from .s2_observability import (
    S2ContractObservabilityInput,
    build_s2_contract_observability_event,
    log_s2_contract_observability_event,
)
from .s2_scaffold import (
    S2CanonicalContractScaffoldRequest,
    S2ContractScaffoldError,
    build_s2_contract_scaffold,
)


logger = logging.getLogger("npbb.core.contracts.s2.validation")

CONT_S2_VALIDATION_VERSION = "cont.s2.validation.v1"
ALLOWED_FLOW_STATUSES = {"completed"}
ALLOWED_EXEC_STATUSES = {"succeeded", "completed", "success"}


class S2CanonicalContractValidationError(ValueError):
    """Raised when CONT Sprint 2 validation contract is violated."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        stage: str,
        observability_event_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.stage = stage
        self.observability_event_id = observability_event_id

    def to_dict(self) -> dict[str, str]:
        """Return serializable actionable diagnostics payload."""

        payload = {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "stage": self.stage,
        }
        if self.observability_event_id:
            payload["observability_event_id"] = self.observability_event_id
        return payload


@dataclass(frozen=True, slots=True)
class S2CanonicalContractValidationInput:
    """Input contract consumed by CONT Sprint 2 validation checks."""

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

    def to_core_input(self, *, correlation_id: str | None = None) -> S2CanonicalContractCoreInput:
        """Convert validated data to `S2CanonicalContractCoreInput` contract."""

        return S2CanonicalContractCoreInput(
            contract_id=self.contract_id,
            dataset_name=self.dataset_name,
            source_kind=self.source_kind,
            schema_version=self.schema_version,
            strict_validation=self.strict_validation,
            lineage_required=self.lineage_required,
            owner_team=self.owner_team,
            schema_required_fields=self.schema_required_fields,
            domain_constraints=self.domain_constraints,
            correlation_id=correlation_id or self.correlation_id,
        )

    def to_scaffold_request(
        self,
        *,
        correlation_id: str | None = None,
    ) -> S2CanonicalContractScaffoldRequest:
        """Convert validated data to `S2CanonicalContractScaffoldRequest` contract."""

        return S2CanonicalContractScaffoldRequest(
            contract_id=self.contract_id,
            dataset_name=self.dataset_name,
            source_kind=self.source_kind,
            schema_version=self.schema_version,
            strict_validation=self.strict_validation,
            lineage_required=self.lineage_required,
            owner_team=self.owner_team,
            schema_required_fields=self.schema_required_fields,
            domain_constraints=self.domain_constraints,
            correlation_id=correlation_id or self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S2CanonicalContractValidationResult:
    """Output contract returned by CONT Sprint 2 input validation."""

    validation_version: str
    validation_id: str
    correlation_id: str
    status: str
    checks: tuple[str, ...]
    route_preview: str
    observabilidade: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "checks": list(self.checks),
            "route_preview": self.route_preview,
            "observabilidade": self.observabilidade,
        }


@dataclass(frozen=True, slots=True)
class S2CanonicalContractFlowOutputValidationResult:
    """Output contract returned by CONT Sprint 2 flow-output validation."""

    correlation_id: str
    status: str
    layer: str
    checked_fields: tuple[str, ...]
    observabilidade: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for diagnostics and assertions."""

        return {
            "correlation_id": self.correlation_id,
            "status": self.status,
            "layer": self.layer,
            "checked_fields": list(self.checked_fields),
            "observabilidade": self.observabilidade,
        }


def validate_s2_contract_input_contract(
    payload: S2CanonicalContractValidationInput,
) -> S2CanonicalContractValidationResult:
    """Validate CONT Sprint 2 input contract before running the main flow.

    Args:
        payload: Input contract with canonical metadata and schema/domain rules.

    Returns:
        S2CanonicalContractValidationResult: Validation metadata and checks summary.

    Raises:
        S2CanonicalContractValidationError: If mandatory contract rules are violated.
    """

    correlation_id = payload.correlation_id or f"cont-s2-val-{uuid4().hex[:12]}"
    started_event = _emit_observability_event(
        event_name="contract_validation_s2_validation_started",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do CONT S2 iniciada",
        severity="info",
        contract_id=payload.contract_id,
        dataset_name=payload.dataset_name,
        source_kind=payload.source_kind,
        schema_version=payload.schema_version,
        strict_validation=payload.strict_validation,
        lineage_required=payload.lineage_required,
        stage="validation_input",
    )
    checks: list[str] = []

    if not payload.contract_id.strip():
        _raise_validation_error(
            code="EMPTY_CONTRACT_ID",
            message="contract_id nao pode ser vazio",
            action="Informe identificador do contrato canonico antes de iniciar a validacao.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("contract_id")

    if not payload.dataset_name.strip():
        _raise_validation_error(
            code="EMPTY_DATASET_NAME",
            message="dataset_name nao pode ser vazio",
            action="Informe dataset_name para rastreabilidade do contrato canonico.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("dataset_name")

    if not payload.source_kind.strip():
        _raise_validation_error(
            code="EMPTY_SOURCE_KIND",
            message="source_kind nao pode ser vazio",
            action="Informe source_kind para selecionar contrato por formato de origem.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("source_kind")

    if not isinstance(payload.strict_validation, bool):
        _raise_validation_error(
            code="INVALID_STRICT_VALIDATION_FLAG_TYPE",
            message="strict_validation deve ser booleano",
            action="Ajuste strict_validation para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"strict_validation": payload.strict_validation},
        )
    checks.append("strict_validation")

    if not isinstance(payload.lineage_required, bool):
        _raise_validation_error(
            code="INVALID_LINEAGE_REQUIRED_FLAG_TYPE",
            message="lineage_required deve ser booleano",
            action="Ajuste lineage_required para true/false.",
            correlation_id=correlation_id,
            stage="validation_input",
            context={"lineage_required": payload.lineage_required},
        )
    checks.append("lineage_required")

    if not isinstance(payload.schema_required_fields, tuple) or len(payload.schema_required_fields) == 0:
        _raise_validation_error(
            code="INVALID_SCHEMA_REQUIRED_FIELDS",
            message="schema_required_fields deve conter ao menos um campo",
            action="Informe schema_required_fields como tupla com campos obrigatorios do schema.",
            correlation_id=correlation_id,
            stage="validation_input",
        )
    checks.append("schema_required_fields")

    try:
        scaffold = build_s2_contract_scaffold(
            payload.to_scaffold_request(correlation_id=correlation_id)
        )
    except S2ContractScaffoldError as exc:
        _raise_validation_error(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold_validation",
            context={
                "source_kind": payload.source_kind,
                "schema_version": payload.schema_version,
                "lineage_required": payload.lineage_required,
            },
        )
        raise AssertionError("unreachable")
    checks.append("scaffold_contract")

    completed_event = _emit_observability_event(
        event_name="contract_validation_s2_validation_completed",
        correlation_id=correlation_id,
        event_message="Validacao de entrada do CONT S2 concluida com sucesso",
        severity="info",
        contract_id=scaffold.contract_id,
        dataset_name=scaffold.dataset_name,
        source_kind=scaffold.validation_profile.get("source_kind"),
        schema_version=scaffold.validation_profile.get("schema_version"),
        strict_validation=scaffold.validation_profile.get("strict_validation"),
        lineage_required=scaffold.validation_profile.get("lineage_required"),
        stage="validation_input",
        context={
            "checks": checks,
            "required_fields_count": scaffold.validation_profile.get("required_fields_count"),
            "domain_rules_count": scaffold.validation_profile.get("domain_rules_count"),
        },
    )

    validation_id = f"contval-{uuid4().hex[:12]}"
    logger.info(
        "contract_validation_s2_validation_result",
        extra={
            "validation_id": validation_id,
            "correlation_id": correlation_id,
            "status": "valid",
            "checks": checks,
            "route_preview": "canonical_contract_s2_schema_domain",
        },
    )
    return S2CanonicalContractValidationResult(
        validation_version=CONT_S2_VALIDATION_VERSION,
        validation_id=validation_id,
        correlation_id=correlation_id,
        status="valid",
        checks=tuple(checks),
        route_preview="canonical_contract_s2_schema_domain",
        observabilidade={
            "validation_started_event_id": started_event.observability_event_id,
            "validation_completed_event_id": completed_event.observability_event_id,
        },
    )


def validate_s2_contract_flow_output_contract(
    flow_output: dict[str, Any],
    *,
    correlation_id: str,
) -> S2CanonicalContractFlowOutputValidationResult:
    """Validate CONT Sprint 2 flow output contract.

    Args:
        flow_output: Output dictionary produced by CONT S2 core or service flow.
        correlation_id: Correlation identifier propagated by caller.

    Returns:
        S2CanonicalContractFlowOutputValidationResult: Summary of checked fields.

    Raises:
        S2CanonicalContractValidationError: If output contract is incomplete or
            inconsistent with CONT Sprint 2 specifications.
    """

    required_fields = (
        "contrato_versao",
        "correlation_id",
        "status",
        "contract_id",
        "dataset_name",
        "validation_profile",
        "execucao",
        "pontos_integracao",
        "observabilidade",
        "scaffold",
    )
    missing_fields = [field for field in required_fields if field not in flow_output]
    if missing_fields:
        _raise_validation_error(
            code="INCOMPLETE_FLOW_OUTPUT",
            message=f"Saida do fluxo CONT S2 incompleta: faltam campos {missing_fields}",
            action="Atualize o fluxo para retornar o contrato completo da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"missing_fields": ",".join(missing_fields)},
        )

    contract_version = str(flow_output.get("contrato_versao", "")).strip()
    layer, required_obs = _resolve_output_layer(
        contract_version=contract_version,
        correlation_id=correlation_id,
    )

    status = str(flow_output.get("status", "")).lower()
    if status not in ALLOWED_FLOW_STATUSES:
        _raise_validation_error(
            code="INVALID_FLOW_STATUS",
            message=f"Status final inesperado no fluxo CONT S2: {flow_output.get('status')}",
            action="Garanta status 'completed' para saidas validas do CONT S2.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"status": str(flow_output.get("status", ""))},
        )

    if str(flow_output.get("correlation_id", "")).strip() != correlation_id.strip():
        _raise_validation_error(
            code="CORRELATION_ID_MISMATCH",
            message="correlation_id divergente entre chamada e payload de saida",
            action="Propague correlation_id estavel em todo o fluxo da sprint.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"output_correlation_id": str(flow_output.get("correlation_id", ""))},
        )

    execucao = flow_output.get("execucao", {})
    exec_status = str(execucao.get("status", "")).lower()
    if exec_status not in ALLOWED_EXEC_STATUSES:
        _raise_validation_error(
            code="INVALID_EXECUTION_STATUS",
            message=f"status de execucao invalido na saida: {execucao.get('status')}",
            action="Use status de execucao valido: succeeded/completed/success.",
            correlation_id=correlation_id,
            stage="validation_output",
            context={"exec_status": str(execucao.get("status", ""))},
        )

    validation_result_id = str(execucao.get("validation_result_id", "")).strip()
    if not validation_result_id:
        _raise_validation_error(
            code="MISSING_VALIDATION_RESULT_ID",
            message="validation_result_id ausente na saida de execucao",
            action="Propague validation_result_id para rastreabilidade da validacao estrita.",
            correlation_id=correlation_id,
            stage="validation_output",
        )

    observabilidade = flow_output.get("observabilidade", {})
    for field, prefix in required_obs.items():
        value = str(observabilidade.get(field, ""))
        if not value.startswith(prefix):
            _raise_validation_error(
                code="INVALID_OBSERVABILITY_OUTPUT",
                message=f"Campo de observabilidade invalido: {field}",
                action=f"Propague IDs de observabilidade com prefixo {prefix}.",
                correlation_id=correlation_id,
                stage="validation_output",
                context={"field": field, "value": value, "expected_prefix": prefix},
            )

    logger.info(
        "contract_validation_s2_flow_output_validated",
        extra={
            "correlation_id": correlation_id,
            "status": "valid",
            "layer": layer,
            "checked_fields": required_fields,
            "contract_id": str(flow_output.get("contract_id", "")),
        },
    )
    return S2CanonicalContractFlowOutputValidationResult(
        correlation_id=correlation_id,
        status="valid",
        layer=layer,
        checked_fields=required_fields,
        observabilidade={field: str(observabilidade[field]) for field in required_obs},
    )


def _resolve_output_layer(
    *,
    contract_version: str,
    correlation_id: str,
) -> tuple[str, dict[str, str]]:
    if contract_version == "cont.s2.core.v1":
        return (
            "core",
            {
                "flow_started_event_id": "conts2coreevt-",
                "flow_completed_event_id": "conts2coreevt-",
            },
        )
    if contract_version == "cont.s2.service.v1":
        return (
            "service",
            {
                "flow_started_event_id": "conts2evt-",
                "validation_profile_ready_event_id": "conts2evt-",
                "flow_completed_event_id": "conts2evt-",
                "main_flow_started_event_id": "conts2coreevt-",
                "main_flow_completed_event_id": "conts2coreevt-",
            },
        )
    raise S2CanonicalContractValidationError(
        code="UNSUPPORTED_OUTPUT_CONTRACT_VERSION",
        message=f"versao de contrato nao suportada para validacao: {contract_version}",
        action="Use contratos cont.s2.core.v1 ou cont.s2.service.v1.",
        correlation_id=correlation_id,
        stage="validation_output",
    )


def _raise_validation_error(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> None:
    failed_event = _emit_observability_event(
        event_name="contract_validation_s2_validation_failed",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        stage=stage,
        context={"error_code": code, "action": action, **(context or {})},
    )
    logger.warning(
        "contract_validation_s2_validation_error",
        extra={
            "correlation_id": correlation_id,
            "error_code": code,
            "error_message": message,
            "action": action,
            "stage": stage,
            "context": context or {},
            "observability_event_id": failed_event.observability_event_id,
        },
    )
    raise S2CanonicalContractValidationError(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        stage=stage,
        observability_event_id=failed_event.observability_event_id,
    )


def _emit_observability_event(
    *,
    event_name: str,
    correlation_id: str,
    event_message: str,
    severity: str,
    stage: str,
    contract_id: str | None = None,
    dataset_name: str | None = None,
    source_kind: str | None = None,
    schema_version: str | None = None,
    strict_validation: bool | None = None,
    lineage_required: bool | None = None,
    schema_checks_executed: int | None = None,
    domain_checks_executed: int | None = None,
    context: dict[str, Any] | None = None,
):
    payload = S2ContractObservabilityInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        severity=severity,
        contract_id=contract_id,
        dataset_name=dataset_name,
        source_kind=source_kind,
        schema_version=schema_version,
        strict_validation=strict_validation,
        lineage_required=lineage_required,
        schema_checks_executed=schema_checks_executed,
        domain_checks_executed=domain_checks_executed,
        stage=stage,
        context=context,
    )
    event = build_s2_contract_observability_event(payload)
    log_s2_contract_observability_event(event)
    return event
