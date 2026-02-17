"""Operational service for CONT Sprint 1 and Sprint 2 contract scaffolding.

This module executes Sprint 1 and Sprint 2 scaffold contracts for canonical
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
    from core.contracts.s2_core import (
        S2CanonicalContractCoreError,
        S2CanonicalContractCoreInput,
        execute_s2_contract_validation_main_flow,
    )
    from core.contracts.s2_scaffold import (
        S2CanonicalContractScaffoldRequest,
    )
    from core.contracts.s1_core import (
        S1CanonicalContractCoreError,
        S1CanonicalContractCoreInput,
        execute_s1_contract_validation_main_flow,
    )
    from core.contracts.s1_scaffold import (
        S1CanonicalContractScaffoldRequest,
    )
except ModuleNotFoundError:  # pragma: no cover
    npbb_root = Path(__file__).resolve().parents[3]
    if str(npbb_root) not in sys.path:
        sys.path.insert(0, str(npbb_root))
    from core.contracts.s2_core import (
        S2CanonicalContractCoreError,
        S2CanonicalContractCoreInput,
        execute_s2_contract_validation_main_flow,
    )
    from core.contracts.s2_scaffold import (
        S2CanonicalContractScaffoldRequest,
    )
    from core.contracts.s1_core import (
        S1CanonicalContractCoreError,
        S1CanonicalContractCoreInput,
        execute_s1_contract_validation_main_flow,
    )
    from core.contracts.s1_scaffold import (
        S1CanonicalContractScaffoldRequest,
    )


logger = logging.getLogger("app.services.contract_validation")

SERVICE_CONTRACT_VERSION_S1 = "cont.s1.service.v1"
SERVICE_CONTRACT_VERSION_S2 = "cont.s2.service.v1"


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


class S2ContractValidationServiceError(RuntimeError):
    """Raised when CONT Sprint 2 service flow fails."""

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


@dataclass(frozen=True, slots=True)
class S2ContractValidationServiceOutput:
    """Output contract returned by CONT Sprint 2 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    contract_id: str
    dataset_name: str
    validation_profile: dict[str, Any]
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
            "validation_profile": self.validation_profile,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s1_contract_validation_service(
    request: S1CanonicalContractScaffoldRequest,
) -> S1ContractValidationServiceOutput:
    """Execute CONT Sprint 1 main-flow service with actionable diagnostics.

    Args:
        request: CONT Sprint 1 input contract with canonical metadata and
            strict validation flags.

    Returns:
        S1ContractValidationServiceOutput: Stable Sprint 1 service output with
            canonical contract metadata and observability identifiers.

    Raises:
        S1ContractValidationServiceError: If main-flow validation fails or an
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
        core_output = execute_s1_contract_validation_main_flow(
            _to_s1_core_input(request=request, correlation_id=correlation_id)
        )

        plan_event_id = _new_s1_event_id()
        logger.info(
            "contract_validation_s1_contract_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": plan_event_id,
                "contract_id": core_output.contract_id,
                "dataset_name": core_output.dataset_name,
                "schema_version": core_output.canonical_contract.get("schema_version"),
                "lineage_required": core_output.canonical_contract.get("lineage_required"),
            },
        )

        completed_event_id = _new_s1_event_id()
        logger.info(
            "contract_validation_s1_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "contract_id": core_output.contract_id,
                "dataset_name": core_output.dataset_name,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["contract_validation_service_module"] = (
            "app.services.contract_validation_service.execute_s1_contract_validation_service"
        )
        pontos_integracao["contract_validation_service_telemetry_module"] = (
            "app.services.contract_validation_service"
        )

        return S1ContractValidationServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S1,
            correlation_id=correlation_id,
            status=core_output.status,
            contract_id=core_output.contract_id,
            dataset_name=core_output.dataset_name,
            canonical_contract=dict(core_output.canonical_contract),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "contract_ready_event_id": plan_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade["flow_completed_event_id"],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S1CanonicalContractCoreError as exc:
        failed_event_id = _new_s1_event_id()
        logger.warning(
            "contract_validation_s1_main_flow_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "failed_stage": exc.stage,
                "core_event_id": exc.event_id,
            },
        )
        raise S1ContractValidationServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
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


def execute_s2_contract_validation_service(
    request: S2CanonicalContractScaffoldRequest,
) -> S2ContractValidationServiceOutput:
    """Execute CONT Sprint 2 scaffold service with actionable diagnostics.

    Args:
        request: CONT Sprint 2 input contract with strict schema/domain
            validation metadata.

    Returns:
        S2ContractValidationServiceOutput: Stable Sprint 2 service output with
            validation profile and observability identifiers.

    Raises:
        S2ContractValidationServiceError: If scaffold validation fails or an
            unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"cont-s2-{uuid4().hex[:12]}"
    started_event_id = _new_s2_event_id()
    logger.info(
        "contract_validation_s2_flow_started",
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
        core_output = execute_s2_contract_validation_main_flow(
            _to_s2_core_input(request=request, correlation_id=correlation_id)
        )

        validation_profile_event_id = _new_s2_event_id()
        logger.info(
            "contract_validation_s2_profile_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": validation_profile_event_id,
                "contract_id": core_output.contract_id,
                "dataset_name": core_output.dataset_name,
                "required_fields_count": core_output.validation_profile.get("required_fields_count"),
                "domain_rules_count": core_output.validation_profile.get("domain_rules_count"),
            },
        )

        completed_event_id = _new_s2_event_id()
        logger.info(
            "contract_validation_s2_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "contract_id": core_output.contract_id,
                "dataset_name": core_output.dataset_name,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["contract_validation_service_module"] = (
            "app.services.contract_validation_service.execute_s2_contract_validation_service"
        )
        pontos_integracao["contract_validation_service_telemetry_module"] = (
            "app.services.contract_validation_service"
        )

        return S2ContractValidationServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S2,
            correlation_id=correlation_id,
            status=core_output.status,
            contract_id=core_output.contract_id,
            dataset_name=core_output.dataset_name,
            validation_profile=dict(core_output.validation_profile),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "validation_profile_ready_event_id": validation_profile_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade["flow_completed_event_id"],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S2CanonicalContractCoreError as exc:
        failed_event_id = _new_s2_event_id()
        logger.warning(
            "contract_validation_s2_main_flow_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
                "failed_stage": exc.stage,
                "core_event_id": exc.event_id,
            },
        )
        raise S2ContractValidationServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event_id,
        ) from exc
    except S2ContractValidationServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s2_event_id()
        logger.error(
            "contract_validation_s2_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S2ContractValidationServiceError(
            code="CONTRACT_VALIDATION_S2_FLOW_FAILED",
            message=f"Falha ao executar fluxo CONT S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do CONT S2.",
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


def _new_s2_event_id() -> str:
    return f"conts2evt-{uuid4().hex[:12]}"


def _to_s1_core_input(
    *,
    request: S1CanonicalContractScaffoldRequest,
    correlation_id: str,
) -> S1CanonicalContractCoreInput:
    return S1CanonicalContractCoreInput(
        contract_id=request.contract_id,
        dataset_name=request.dataset_name,
        source_kind=request.source_kind,
        schema_version=request.schema_version,
        strict_validation=request.strict_validation,
        lineage_required=request.lineage_required,
        owner_team=request.owner_team,
        correlation_id=correlation_id,
    )


def _to_s2_core_input(
    *,
    request: S2CanonicalContractScaffoldRequest,
    correlation_id: str,
) -> S2CanonicalContractCoreInput:
    return S2CanonicalContractCoreInput(
        contract_id=request.contract_id,
        dataset_name=request.dataset_name,
        source_kind=request.source_kind,
        schema_version=request.schema_version,
        strict_validation=request.strict_validation,
        lineage_required=request.lineage_required,
        owner_team=request.owner_team,
        schema_required_fields=request.schema_required_fields,
        domain_constraints=request.domain_constraints,
        correlation_id=correlation_id,
    )
