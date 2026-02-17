"""Operational service for CONT Sprint 1 canonical contract scaffolding.

This module executes Sprint 1 scaffold contracts for canonical output
validation and emits structured operational logs with actionable errors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

try:  # pragma: no cover - import style depends on execution cwd
    from core.contracts.s1_scaffold import (
        S1CanonicalContractScaffoldRequest,
        S1ContractScaffoldError,
        build_s1_contract_scaffold,
    )
except ModuleNotFoundError:  # pragma: no cover
    npbb_root = Path(__file__).resolve().parents[3]
    if str(npbb_root) not in sys.path:
        sys.path.insert(0, str(npbb_root))
    from core.contracts.s1_scaffold import (
        S1CanonicalContractScaffoldRequest,
        S1ContractScaffoldError,
        build_s1_contract_scaffold,
    )


logger = logging.getLogger("app.services.contract_validation")

SERVICE_CONTRACT_VERSION_S1 = "cont.s1.service.v1"


class S1ContractValidationServiceError(RuntimeError):
    """Raised when CONT Sprint 1 service flow fails."""

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
        """Return serializable diagnostics payload for API integration."""

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
class S1ContractValidationServiceOutput:
    """Output contract returned by CONT Sprint 1 service flow."""

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
        """Return plain dictionary for API/CLI serialization."""

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


def execute_s1_contract_validation_service(
    request: S1CanonicalContractScaffoldRequest,
) -> S1ContractValidationServiceOutput:
    """Execute CONT Sprint 1 scaffold service with actionable diagnostics.

    Args:
        request: CONT Sprint 1 input contract with canonical metadata and
            strict validation flags.

    Returns:
        S1ContractValidationServiceOutput: Stable Sprint 1 service output with
            canonical scaffold and observability identifiers.

    Raises:
        S1ContractValidationServiceError: If scaffold validation fails or an
            unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"cont-s1-{uuid4().hex[:12]}"
    started_event_id = _new_s1_event_id()
    logger.info(
        "contract_validation_s1_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "contract_id": request.contract_id,
            "dataset_name": request.dataset_name,
            "source_kind": request.source_kind,
            "schema_version": request.schema_version,
        },
    )

    try:
        scaffold_output = build_s1_contract_scaffold(
            S1CanonicalContractScaffoldRequest(
                contract_id=request.contract_id,
                dataset_name=request.dataset_name,
                source_kind=request.source_kind,
                schema_version=request.schema_version,
                strict_validation=request.strict_validation,
                lineage_required=request.lineage_required,
                owner_team=request.owner_team,
                correlation_id=correlation_id,
            )
        )

        plan_event_id = _new_s1_event_id()
        logger.info(
            "contract_validation_s1_contract_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": plan_event_id,
                "contract_id": scaffold_output.contract_id,
                "dataset_name": scaffold_output.dataset_name,
                "schema_version": scaffold_output.canonical_contract.get("schema_version"),
                "lineage_required": scaffold_output.canonical_contract.get("lineage_required"),
            },
        )

        completed_event_id = _new_s1_event_id()
        logger.info(
            "contract_validation_s1_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "contract_id": scaffold_output.contract_id,
                "dataset_name": scaffold_output.dataset_name,
                "status": scaffold_output.status,
            },
        )

        pontos_integracao = dict(scaffold_output.pontos_integracao)
        pontos_integracao["contract_validation_service_module"] = (
            "app.services.contract_validation_service.execute_s1_contract_validation_service"
        )
        pontos_integracao["contract_validation_service_telemetry_module"] = (
            "app.services.contract_validation_service"
        )

        return S1ContractValidationServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S1,
            correlation_id=correlation_id,
            status=scaffold_output.status,
            contract_id=scaffold_output.contract_id,
            dataset_name=scaffold_output.dataset_name,
            canonical_contract=dict(scaffold_output.canonical_contract),
            execucao={
                "status": "not_started",
                "decision_reason": "s1_scaffold_ready_for_core_integration",
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "contract_ready_event_id": plan_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold_output.to_dict(),
        )
    except S1ContractScaffoldError as exc:
        failed_event_id = _new_s1_event_id()
        logger.warning(
            "contract_validation_s1_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S1ContractValidationServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S1ContractValidationServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s1_event_id()
        logger.error(
            "contract_validation_s1_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S1ContractValidationServiceError(
            code="CONTRACT_VALIDATION_S1_FLOW_FAILED",
            message=f"Falha ao executar fluxo CONT S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do CONT S1.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def build_s1_contract_validation_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    event_id: str,
    stage: str = "service",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable CONT Sprint 1 error detail for API responses.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable error explanation.
        action: Suggested next action for diagnosis/remediation.
        correlation_id: Correlation identifier for cross-layer tracing.
        event_id: Service event identifier for log lookup.
        stage: Flow stage where the error happened.
        context: Optional diagnostics context payload.

    Returns:
        dict[str, Any]: Stable API error detail payload.
    """

    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "event_id": event_id,
        "stage": stage,
        "context": context or {},
    }


def _new_s1_event_id() -> str:
    return f"conts1evt-{uuid4().hex[:12]}"
