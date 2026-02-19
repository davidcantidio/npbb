"""Main flow for CONT Sprint 1 canonical contract validation.

This module executes the Sprint 1 core path:
1) validate input and resolve scaffold contract;
2) execute one strict validation pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s1_scaffold import (
    S1CanonicalContractScaffoldRequest,
    S1ContractScaffoldError,
    build_s1_contract_scaffold,
)


logger = logging.getLogger("npbb.core.contracts.s1.core")

CONTRACT_VERSION = "cont.s1.core.v1"
CONT_S1_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONT_S1_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONT_S1_ALLOWED_EXEC_STATUSES = CONT_S1_SUCCESS_STATUSES | CONT_S1_FAILED_STATUSES


class S1CanonicalContractCoreError(RuntimeError):
    """Raised when CONT Sprint 1 core flow fails."""

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
class S1CanonicalContractCoreInput:
    """Input contract consumed by CONT Sprint 1 core flow."""

    contract_id: str
    dataset_name: str
    source_kind: str
    schema_version: str = "v1"
    strict_validation: bool = True
    lineage_required: bool = True
    owner_team: str = "etl"
    correlation_id: str | None = None

    def to_scaffold_request(self, *, correlation_id: str) -> S1CanonicalContractScaffoldRequest:
        """Build scaffold request using CONT Sprint 1 stable fields."""

        return S1CanonicalContractScaffoldRequest(
            contract_id=self.contract_id,
            dataset_name=self.dataset_name,
            source_kind=self.source_kind,
            schema_version=self.schema_version,
            strict_validation=self.strict_validation,
            lineage_required=self.lineage_required,
            owner_team=self.owner_team,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S1CanonicalContractCoreOutput:
    """Output contract returned by CONT Sprint 1 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    canonical_contract: dict[str, Any]
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
            "canonical_contract": self.canonical_contract,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s1_contract_validation_main_flow(
    flow_input: S1CanonicalContractCoreInput,
    *,
    execute_validation: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S1CanonicalContractCoreOutput:
    """Execute CONT Sprint 1 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with canonical metadata and strict
            validation flags.
        execute_validation: Optional callback responsible for one validation
            execution. It receives a validation context and must return a
            dictionary with `status` and optional diagnostics fields.

    Returns:
        S1CanonicalContractCoreOutput: Stable output with canonical contract,
            execution diagnostics, and observability identifiers.

    Raises:
        S1CanonicalContractCoreError: If scaffold validation fails, validation
            response is invalid, or validation execution fails.
    """

    correlation_id = flow_input.correlation_id or f"cont-s1-{uuid4().hex[:12]}"
    validator = execute_validation or _default_validator
    started_event_id = _new_event_id()
    logger.info(
        "contract_validation_s1_main_flow_started",
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
        scaffold = build_s1_contract_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        validation_context = {
            "correlation_id": correlation_id,
            "contract_id": scaffold.contract_id,
            "dataset_name": scaffold.dataset_name,
            "source_kind": scaffold.canonical_contract.get("source_kind"),
            "schema_version": scaffold.canonical_contract.get("schema_version"),
            "strict_validation": scaffold.canonical_contract.get("strict_validation"),
            "lineage_required": scaffold.canonical_contract.get("lineage_required"),
            "required_fields_count": len(scaffold.canonical_contract.get("required_fields", [])),
        }
        response = validator(validation_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="validation",
        )
        status = normalized["status"]

        completed_event_id = _new_event_id()
        logger.info(
            "contract_validation_s1_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "contract_id": scaffold.contract_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
            },
        )

        if status not in CONT_S1_SUCCESS_STATUSES:
            raise S1CanonicalContractCoreError(
                code="CONT_S1_VALIDATION_FAILED",
                message=f"Validacao de contrato CONT S1 falhou com status '{status}'",
                action=(
                    "Revisar logs de validacao estrita e conferir schema/required_fields/"
                    "lineage_policy do contrato canonico."
                ),
                correlation_id=correlation_id,
                stage="validation",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["contract_validation_core_module"] = (
            "core.contracts.s1_core.execute_s1_contract_validation_main_flow"
        )
        return S1CanonicalContractCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            contract_id=scaffold.contract_id,
            dataset_name=scaffold.dataset_name,
            canonical_contract=dict(scaffold.canonical_contract),
            execucao={
                "status": status,
                "decision_reason": str(normalized.get("decision_reason", "dry_run_main_flow")),
                "validation_result_id": str(normalized.get("validation_result_id", "")),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S1ContractScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "contract_validation_s1_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S1CanonicalContractCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S1CanonicalContractCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "contract_validation_s1_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S1CanonicalContractCoreError(
            code="CONT_S1_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONT S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONT S1.",
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
        raise S1CanonicalContractCoreError(
            code="INVALID_VALIDATION_RESPONSE",
            message="Executor de validacao retornou resposta em formato invalido",
            action="Garantir retorno dict com campo 'status' no executor de validacao.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONT_S1_ALLOWED_EXEC_STATUSES:
        raise S1CanonicalContractCoreError(
            code="INVALID_VALIDATION_STATUS",
            message=f"Status de validacao invalido: {response.get('status')}",
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


def _default_validator(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one strict contract validation pass in dry-run mode.

    Args:
        context: Structured validation context with canonical metadata.

    Returns:
        dict[str, Any]: Dry-run validation execution result.
    """

    return {
        "status": "succeeded",
        "decision_reason": "dry_run_main_flow",
        "validation_result_id": f"dryrun-{context.get('correlation_id', '')}",
    }


def _new_event_id() -> str:
    return f"conts1coreevt-{uuid4().hex[:12]}"
