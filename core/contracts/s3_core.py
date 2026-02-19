"""Main flow for CONT Sprint 3 field/metric lineage enforcement validation.

This module executes the Sprint 3 core path:
1) validate input and resolve Sprint 3 scaffold profile;
2) execute one lineage enforcement pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s3_scaffold import (
    S3CanonicalContractScaffoldRequest,
    S3ContractScaffoldError,
    build_s3_contract_scaffold,
)


logger = logging.getLogger("npbb.core.contracts.s3.core")

CONTRACT_VERSION = "cont.s3.core.v1"
CONT_S3_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONT_S3_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONT_S3_ALLOWED_EXEC_STATUSES = CONT_S3_SUCCESS_STATUSES | CONT_S3_FAILED_STATUSES


class S3CanonicalContractCoreError(RuntimeError):
    """Raised when CONT Sprint 3 core flow fails."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        stage: str,
        event_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.stage = stage
        self.event_id = event_id

    def to_dict(self) -> dict[str, str]:
        """Return serializable diagnostics payload."""

        payload = {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "stage": self.stage,
        }
        if self.event_id:
            payload["event_id"] = self.event_id
        return payload


@dataclass(frozen=True, slots=True)
class S3CanonicalContractCoreInput:
    """Input contract consumed by CONT Sprint 3 core flow."""

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

    def to_scaffold_request(self, *, correlation_id: str) -> S3CanonicalContractScaffoldRequest:
        """Build scaffold request using CONT Sprint 3 stable fields."""

        return S3CanonicalContractScaffoldRequest(
            contract_id=self.contract_id,
            dataset_name=self.dataset_name,
            source_kind=self.source_kind,
            schema_version=self.schema_version,
            strict_validation=self.strict_validation,
            lineage_required=self.lineage_required,
            owner_team=self.owner_team,
            schema_required_fields=self.schema_required_fields,
            lineage_field_requirements=self.lineage_field_requirements,
            metric_lineage_requirements=self.metric_lineage_requirements,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S3CanonicalContractCoreOutput:
    """Output contract returned by CONT Sprint 3 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    lineage_profile: dict[str, Any]
    execucao: dict[str, Any]
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]
    scaffold: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return plain dictionary for API, logs, and integration tests."""

        return {
            "contrato_versao": self.contrato_versao,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "contract_id": self.contract_id,
            "dataset_name": self.dataset_name,
            "lineage_profile": self.lineage_profile,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s3_contract_validation_main_flow(
    flow_input: S3CanonicalContractCoreInput,
    *,
    execute_lineage_enforcement: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S3CanonicalContractCoreOutput:
    """Execute CONT Sprint 3 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with lineage-by-field and lineage-by-metric
            enforcement rules.
        execute_lineage_enforcement: Optional callback responsible for one
            lineage enforcement execution. It receives a context payload and
            must return a dictionary with `status` and optional diagnostics.

    Returns:
        S3CanonicalContractCoreOutput: Stable output with lineage profile,
            execution diagnostics, and observability identifiers.

    Raises:
        S3CanonicalContractCoreError: If scaffold validation fails, execution
            response is invalid, or enforcement fails.
    """

    correlation_id = flow_input.correlation_id or f"cont-s3-{uuid4().hex[:12]}"
    enforcer = execute_lineage_enforcement or _default_enforcer
    started_event_id = _new_event_id()
    logger.info(
        "contract_validation_s3_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "contract_id": flow_input.contract_id,
            "dataset_name": flow_input.dataset_name,
            "source_kind": flow_input.source_kind,
            "schema_version": flow_input.schema_version,
        },
    )

    try:
        scaffold = build_s3_contract_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        enforcement_context = {
            "correlation_id": correlation_id,
            "contract_id": scaffold.contract_id,
            "dataset_name": scaffold.dataset_name,
            "source_kind": scaffold.lineage_profile.get("source_kind"),
            "schema_version": scaffold.lineage_profile.get("schema_version"),
            "strict_validation": scaffold.lineage_profile.get("strict_validation"),
            "lineage_required": scaffold.lineage_profile.get("lineage_required"),
            "field_lineage_rules_count": scaffold.lineage_profile.get("field_lineage_rules_count", 0),
            "metric_lineage_rules_count": scaffold.lineage_profile.get("metric_lineage_rules_count", 0),
        }
        response = enforcer(enforcement_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="lineage_enforcement",
        )
        status = normalized["status"]

        completed_event_id = _new_event_id()
        logger.info(
            "contract_validation_s3_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "contract_id": scaffold.contract_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
            },
        )

        if status not in CONT_S3_SUCCESS_STATUSES:
            raise S3CanonicalContractCoreError(
                code="CONT_S3_LINEAGE_ENFORCEMENT_FAILED",
                message=f"Enforcement de linhagem CONT S3 falhou com status '{status}'",
                action=(
                    "Revisar logs de enforcement e conferir lineage_field_requirements/"
                    "metric_lineage_requirements do contrato canonico."
                ),
                correlation_id=correlation_id,
                stage="lineage_enforcement",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["contract_validation_core_module"] = (
            "core.contracts.s3_core.execute_s3_contract_validation_main_flow"
        )
        return S3CanonicalContractCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            contract_id=scaffold.contract_id,
            dataset_name=scaffold.dataset_name,
            lineage_profile=dict(scaffold.lineage_profile),
            execucao={
                "status": status,
                "decision_reason": str(normalized.get("decision_reason", "dry_run_main_flow")),
                "validation_result_id": str(normalized.get("validation_result_id", "")),
                "field_lineage_checks_executed": int(normalized.get("field_lineage_checks_executed", 1)),
                "metric_lineage_checks_executed": int(normalized.get("metric_lineage_checks_executed", 1)),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S3ContractScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "contract_validation_s3_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S3CanonicalContractCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S3CanonicalContractCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "contract_validation_s3_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3CanonicalContractCoreError(
            code="CONT_S3_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONT S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONT S3.",
            correlation_id=correlation_id,
            stage="main_flow",
            event_id=failed_event_id,
        ) from exc


def _normalize_execution_response(
    *,
    response: dict[str, Any],
    correlation_id: str,
    stage: str,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise S3CanonicalContractCoreError(
            code="INVALID_LINEAGE_ENFORCEMENT_RESPONSE",
            message="Executor de enforcement retornou resposta em formato invalido",
            action="Garantir retorno dict com campo 'status' no executor de enforcement.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONT_S3_ALLOWED_EXEC_STATUSES:
        raise S3CanonicalContractCoreError(
            code="INVALID_LINEAGE_ENFORCEMENT_STATUS",
            message=f"Status de enforcement invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status
    return normalized


def _default_enforcer(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one lineage enforcement pass in dry-run mode.

    Args:
        context: Structured enforcement context with lineage metadata.

    Returns:
        dict[str, Any]: Dry-run lineage enforcement result.
    """

    return {
        "status": "succeeded",
        "decision_reason": "dry_run_main_flow",
        "validation_result_id": f"dryrun-{context.get('correlation_id', '')}",
        "field_lineage_checks_executed": int(context.get("field_lineage_rules_count", 0)) or 1,
        "metric_lineage_checks_executed": int(context.get("metric_lineage_rules_count", 0)) or 1,
    }


def _new_event_id() -> str:
    return f"conts3coreevt-{uuid4().hex[:12]}"
