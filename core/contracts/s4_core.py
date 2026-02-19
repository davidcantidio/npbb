"""Main flow for CONT Sprint 4 version compatibility and regression gates.

This module executes the Sprint 4 core path:
1) validate input and resolve Sprint 4 scaffold profile;
2) execute one compatibility/regression validation pass (dry-run by default);
3) return a stable output contract for service/API layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .s4_scaffold import (
    S4CanonicalContractScaffoldRequest,
    S4ContractScaffoldError,
    build_s4_contract_scaffold,
)


logger = logging.getLogger("npbb.core.contracts.s4.core")

CONTRACT_VERSION = "cont.s4.core.v1"
CONT_S4_SUCCESS_STATUSES = {"succeeded", "completed", "success"}
CONT_S4_FAILED_STATUSES = {"failed", "fatal_error", "timeout", "transient_error", "retryable_failure"}
CONT_S4_ALLOWED_EXEC_STATUSES = CONT_S4_SUCCESS_STATUSES | CONT_S4_FAILED_STATUSES


class S4CanonicalContractCoreError(RuntimeError):
    """Raised when CONT Sprint 4 core flow fails."""

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
class S4CanonicalContractCoreInput:
    """Input contract consumed by CONT Sprint 4 core flow."""

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

    def to_scaffold_request(self, *, correlation_id: str) -> S4CanonicalContractScaffoldRequest:
        """Build scaffold request using CONT Sprint 4 stable fields."""

        return S4CanonicalContractScaffoldRequest(
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
            compatibility_mode=self.compatibility_mode,
            previous_contract_versions=self.previous_contract_versions,
            regression_gate_required=self.regression_gate_required,
            regression_suite_version=self.regression_suite_version,
            max_regression_failures=self.max_regression_failures,
            breaking_change_policy=self.breaking_change_policy,
            deprecation_window_days=self.deprecation_window_days,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class S4CanonicalContractCoreOutput:
    """Output contract returned by CONT Sprint 4 core flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    versioning_profile: dict[str, Any]
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
            "versioning_profile": self.versioning_profile,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s4_contract_validation_main_flow(
    flow_input: S4CanonicalContractCoreInput,
    *,
    execute_compatibility_validation: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> S4CanonicalContractCoreOutput:
    """Execute CONT Sprint 4 main flow with stable contracts and diagnostics.

    Args:
        flow_input: Input contract with version compatibility and regression
            gate requirements for Sprint 4.
        execute_compatibility_validation: Optional callback responsible for one
            compatibility/regression validation execution. It receives an
            execution context and must return a dictionary with `status` and
            optional diagnostics fields.

    Returns:
        S4CanonicalContractCoreOutput: Stable output with versioning profile,
            execution diagnostics, and observability identifiers.

    Raises:
        S4CanonicalContractCoreError: If scaffold validation fails, execution
            response is invalid, or compatibility/regression gate fails.
    """

    correlation_id = flow_input.correlation_id or f"cont-s4-{uuid4().hex[:12]}"
    validator = execute_compatibility_validation or _default_validator
    started_event_id = _new_event_id()
    logger.info(
        "contract_validation_s4_main_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "contract_id": flow_input.contract_id,
            "dataset_name": flow_input.dataset_name,
            "source_kind": flow_input.source_kind,
            "schema_version": flow_input.schema_version,
            "compatibility_mode": flow_input.compatibility_mode,
        },
    )

    try:
        scaffold = build_s4_contract_scaffold(
            flow_input.to_scaffold_request(correlation_id=correlation_id)
        )

        validation_context = {
            "correlation_id": correlation_id,
            "contract_id": scaffold.contract_id,
            "dataset_name": scaffold.dataset_name,
            "source_kind": scaffold.versioning_profile.get("source_kind"),
            "schema_version": scaffold.versioning_profile.get("schema_version"),
            "strict_validation": scaffold.versioning_profile.get("strict_validation"),
            "lineage_required": scaffold.versioning_profile.get("lineage_required"),
            "compatibility_mode": scaffold.versioning_profile.get("compatibility_mode"),
            "previous_contract_versions_count": len(
                scaffold.versioning_profile.get("previous_contract_versions", [])
            ),
            "regression_gate_required": scaffold.versioning_profile.get(
                "regression_gate_required", False
            ),
            "regression_suite_version": scaffold.versioning_profile.get("regression_suite_version"),
            "max_regression_failures": scaffold.versioning_profile.get("max_regression_failures", 0),
            "breaking_change_policy": scaffold.versioning_profile.get("breaking_change_policy"),
            "deprecation_window_days": scaffold.versioning_profile.get("deprecation_window_days", 0),
        }
        response = validator(validation_context)
        normalized = _normalize_execution_response(
            response=response,
            correlation_id=correlation_id,
            stage="compatibility_validation",
        )
        status = normalized["status"]

        regression_gate_required = bool(
            scaffold.versioning_profile.get("regression_gate_required", False)
        )
        max_regression_failures = int(
            scaffold.versioning_profile.get("max_regression_failures", 0)
        )
        regression_failures = int(normalized.get("regression_failures", 0))
        breaking_change_policy = str(
            scaffold.versioning_profile.get("breaking_change_policy", "block")
        ).strip().lower()
        breaking_change_detected = bool(normalized.get("breaking_change_detected", False))
        regression_gate_passed = bool(
            normalized.get(
                "regression_gate_passed",
                (not regression_gate_required) or regression_failures <= max_regression_failures,
            )
        )
        compatibility_result = str(
            normalized.get("compatibility_result", "backward_compatible")
        ).strip().lower() or "backward_compatible"

        completed_event_id = _new_event_id()
        logger.info(
            "contract_validation_s4_main_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "contract_id": scaffold.contract_id,
                "dataset_name": scaffold.dataset_name,
                "status": status,
                "compatibility_result": compatibility_result,
                "breaking_change_detected": breaking_change_detected,
                "regression_failures": regression_failures,
                "regression_gate_passed": regression_gate_passed,
            },
        )

        if status not in CONT_S4_SUCCESS_STATUSES:
            raise S4CanonicalContractCoreError(
                code="CONT_S4_COMPATIBILITY_VALIDATION_FAILED",
                message=(
                    "Validacao de compatibilidade/regressao CONT S4 falhou "
                    f"com status '{status}'"
                ),
                action=(
                    "Revisar logs de compatibilidade e regressao, incluindo "
                    "compatibility_mode, previous_contract_versions e regras de gate."
                ),
                correlation_id=correlation_id,
                stage="compatibility_validation",
                event_id=completed_event_id,
            )

        if breaking_change_detected and breaking_change_policy == "block":
            raise S4CanonicalContractCoreError(
                code="CONT_S4_BREAKING_CHANGE_BLOCKED",
                message="Mudanca breaking detectada com politica de bloqueio no CONT S4",
                action=(
                    "Ajustar contrato para manter compatibilidade backward ou registrar waiver "
                    "com politica allow_with_waiver."
                ),
                correlation_id=correlation_id,
                stage="compatibility_validation",
                event_id=completed_event_id,
            )

        if regression_gate_required and (
            not regression_gate_passed or regression_failures > max_regression_failures
        ):
            raise S4CanonicalContractCoreError(
                code="CONT_S4_REGRESSION_GATE_FAILED",
                message=(
                    "Regression gate CONT S4 bloqueou a liberacao: "
                    f"{regression_failures} falhas para limite {max_regression_failures}"
                ),
                action=(
                    "Corrigir regressao, reduzir falhas abaixo do limite configurado ou revisar "
                    "max_regression_failures conforme politica de rollout."
                ),
                correlation_id=correlation_id,
                stage="compatibility_validation",
                event_id=completed_event_id,
            )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["contract_validation_core_module"] = (
            "core.contracts.s4_core.execute_s4_contract_validation_main_flow"
        )

        return S4CanonicalContractCoreOutput(
            contrato_versao=CONTRACT_VERSION,
            correlation_id=correlation_id,
            status="completed",
            contract_id=scaffold.contract_id,
            dataset_name=scaffold.dataset_name,
            versioning_profile=dict(scaffold.versioning_profile),
            execucao={
                "status": status,
                "decision_reason": str(normalized.get("decision_reason", "dry_run_main_flow")),
                "validation_result_id": str(normalized.get("validation_result_id", "")),
                "compatibility_result": compatibility_result,
                "breaking_change_detected": breaking_change_detected,
                "regression_failures": regression_failures,
                "max_regression_failures": max_regression_failures,
                "regression_gate_required": regression_gate_required,
                "regression_gate_passed": regression_gate_passed,
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S4ContractScaffoldError as exc:
        failed_event_id = _new_event_id()
        logger.warning(
            "contract_validation_s4_main_flow_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S4CanonicalContractCoreError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4CanonicalContractCoreError:
        raise
    except Exception as exc:
        failed_event_id = _new_event_id()
        logger.error(
            "contract_validation_s4_main_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4CanonicalContractCoreError(
            code="CONT_S4_MAIN_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal CONT S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/executor CONT S4.",
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
        raise S4CanonicalContractCoreError(
            code="INVALID_COMPATIBILITY_VALIDATION_RESPONSE",
            message="Executor de compatibilidade retornou resposta em formato invalido",
            action="Garantir retorno dict com campo 'status' no executor de compatibilidade.",
            correlation_id=correlation_id,
            stage=stage,
        )

    status = str(response.get("status", "")).strip().lower()
    if status not in CONT_S4_ALLOWED_EXEC_STATUSES:
        raise S4CanonicalContractCoreError(
            code="INVALID_COMPATIBILITY_VALIDATION_STATUS",
            message=f"Status de execucao invalido: {response.get('status')}",
            action=(
                "Retorne status valido no executor: "
                "succeeded/completed/success/failed/fatal_error/timeout/transient_error/retryable_failure."
            ),
            correlation_id=correlation_id,
            stage=stage,
        )

    normalized = dict(response)
    normalized["status"] = status

    if "regression_failures" in normalized:
        regression_failures = normalized["regression_failures"]
        if not isinstance(regression_failures, int) or regression_failures < 0:
            raise S4CanonicalContractCoreError(
                code="INVALID_REGRESSION_FAILURES_COUNT",
                message=f"regression_failures invalido na resposta de execucao: {regression_failures}",
                action="Retorne regression_failures como inteiro >= 0.",
                correlation_id=correlation_id,
                stage=stage,
            )

    if "breaking_change_detected" in normalized and not isinstance(
        normalized["breaking_change_detected"], bool
    ):
        raise S4CanonicalContractCoreError(
            code="INVALID_BREAKING_CHANGE_FLAG",
            message="breaking_change_detected deve ser booleano na resposta de execucao",
            action="Retorne breaking_change_detected como true/false.",
            correlation_id=correlation_id,
            stage=stage,
        )

    if "regression_gate_passed" in normalized and not isinstance(
        normalized["regression_gate_passed"], bool
    ):
        raise S4CanonicalContractCoreError(
            code="INVALID_REGRESSION_GATE_FLAG",
            message="regression_gate_passed deve ser booleano na resposta de execucao",
            action="Retorne regression_gate_passed como true/false.",
            correlation_id=correlation_id,
            stage=stage,
        )

    if "compatibility_result" in normalized:
        compatibility_result = str(normalized["compatibility_result"]).strip().lower()
        if not compatibility_result:
            raise S4CanonicalContractCoreError(
                code="INVALID_COMPATIBILITY_RESULT",
                message="compatibility_result vazio na resposta de execucao",
                action="Retorne compatibility_result com valor descritivo (ex: backward_compatible).",
                correlation_id=correlation_id,
                stage=stage,
            )
        normalized["compatibility_result"] = compatibility_result

    return normalized


def _default_validator(context: dict[str, Any]) -> dict[str, Any]:
    """Execute one compatibility/regression validation pass in dry-run mode.

    Args:
        context: Structured validation context with Sprint 4 compatibility
            and regression gate metadata.

    Returns:
        dict[str, Any]: Dry-run execution result for Sprint 4 main flow.
    """

    regression_gate_required = bool(context.get("regression_gate_required", False))
    max_regression_failures = int(context.get("max_regression_failures", 0))
    regression_failures = 0

    return {
        "status": "succeeded",
        "decision_reason": "dry_run_main_flow",
        "validation_result_id": f"dryrun-{context.get('correlation_id', '')}",
        "compatibility_result": "backward_compatible",
        "breaking_change_detected": False,
        "regression_failures": regression_failures,
        "regression_gate_passed": (
            (not regression_gate_required) or regression_failures <= max_regression_failures
        ),
    }


def _new_event_id() -> str:
    return f"conts4coreevt-{uuid4().hex[:12]}"
