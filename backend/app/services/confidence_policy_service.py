"""Operational service for CONF Sprint 1, Sprint 2, and Sprint 3 policies.

This module executes CONF Sprint 1 and Sprint 2 main-flow contracts, plus
CONF Sprint 3 scaffold contracts, and emits structured operational logs with
actionable errors for integration layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

try:  # pragma: no cover - import style depends on execution cwd
    from core.confidence.s1_core import (
        S1ConfidenceCoreError,
        S1ConfidenceCoreInput,
        execute_s1_confidence_policy_main_flow,
    )
    from core.confidence.s1_scaffold import (
        S1ConfidenceScaffoldRequest,
    )
    from core.confidence.s2_core import (
        S2ConfidenceCoreError,
        S2ConfidenceCoreInput,
        execute_s2_confidence_policy_main_flow,
    )
    from core.confidence.s2_scaffold import (
        S2ConfidenceScaffoldRequest,
    )
    from core.confidence.s3_scaffold import (
        S3ConfidenceScaffoldError,
        S3ConfidenceScaffoldRequest,
        build_s3_confidence_scaffold,
    )
except ModuleNotFoundError:  # pragma: no cover
    npbb_root = Path(__file__).resolve().parents[3]
    if str(npbb_root) not in sys.path:
        sys.path.insert(0, str(npbb_root))
    from core.confidence.s1_core import (
        S1ConfidenceCoreError,
        S1ConfidenceCoreInput,
        execute_s1_confidence_policy_main_flow,
    )
    from core.confidence.s1_scaffold import (
        S1ConfidenceScaffoldRequest,
    )
    from core.confidence.s2_core import (
        S2ConfidenceCoreError,
        S2ConfidenceCoreInput,
        execute_s2_confidence_policy_main_flow,
    )
    from core.confidence.s2_scaffold import (
        S2ConfidenceScaffoldRequest,
    )
    from core.confidence.s3_scaffold import (
        S3ConfidenceScaffoldError,
        S3ConfidenceScaffoldRequest,
        build_s3_confidence_scaffold,
    )


logger = logging.getLogger("app.services.confidence_policy")

SERVICE_CONTRACT_VERSION_S1 = "conf.s1.service.v1"
SERVICE_CONTRACT_VERSION_S2 = "conf.s2.service.v1"
SERVICE_CONTRACT_VERSION_S3 = "conf.s3.service.v1"


class S1ConfidencePolicyServiceError(RuntimeError):
    """Raised when CONF Sprint 1 service flow fails."""

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


class S2ConfidencePolicyServiceError(RuntimeError):
    """Raised when CONF Sprint 2 service flow fails."""

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


class S3ConfidencePolicyServiceError(RuntimeError):
    """Raised when CONF Sprint 3 service flow fails."""

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
class S1ConfidencePolicyServiceOutput:
    """Output contract returned by CONF Sprint 1 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    policy_id: str
    dataset_name: str
    confidence_policy: dict[str, Any]
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
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "confidence_policy": self.confidence_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S2ConfidencePolicyServiceOutput:
    """Output contract returned by CONF Sprint 2 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    policy_id: str
    dataset_name: str
    decision_policy: dict[str, Any]
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
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "decision_policy": self.decision_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S3ConfidencePolicyServiceOutput:
    """Output contract returned by CONF Sprint 3 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    policy_id: str
    dataset_name: str
    decision_policy: dict[str, Any]
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
            "policy_id": self.policy_id,
            "dataset_name": self.dataset_name,
            "decision_policy": self.decision_policy,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s1_confidence_policy_service(
    request: S1ConfidenceScaffoldRequest,
) -> S1ConfidencePolicyServiceOutput:
    """Execute CONF Sprint 1 main-flow service with actionable diagnostics.

    Args:
        request: CONF Sprint 1 input contract with field-level scoring policy
            metadata and decision thresholds.

    Returns:
        S1ConfidencePolicyServiceOutput: Stable Sprint 1 service output with
            policy metadata and observability identifiers.

    Raises:
        S1ConfidencePolicyServiceError: If main-flow scoring fails or an
            unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"conf-s1-{uuid4().hex[:12]}"
    started_event_id = _new_s1_event_id()
    logger.info(
        "confidence_policy_s1_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": request.policy_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "decision_mode": request.decision_mode,
        },
    )

    try:
        core_output = execute_s1_confidence_policy_main_flow(
            _to_s1_core_input(request=request, correlation_id=correlation_id)
        )

        policy_ready_event_id = _new_s1_event_id()
        logger.info(
            "confidence_policy_s1_profile_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": policy_ready_event_id,
                "policy_id": core_output.policy_id,
                "dataset_name": core_output.dataset_name,
                "entity_kind": core_output.confidence_policy.get("entity_kind"),
                "field_weights_count": core_output.confidence_policy.get("field_weights_count"),
            },
        )

        completed_event_id = _new_s1_event_id()
        logger.info(
            "confidence_policy_s1_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": core_output.policy_id,
                "dataset_name": core_output.dataset_name,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
                "decision": core_output.execucao.get("decision"),
                "confidence_score": core_output.execucao.get("confidence_score"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["confidence_policy_service_module"] = (
            "app.services.confidence_policy_service.execute_s1_confidence_policy_service"
        )
        pontos_integracao["confidence_policy_service_telemetry_module"] = (
            "app.services.confidence_policy_service"
        )

        return S1ConfidencePolicyServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S1,
            correlation_id=correlation_id,
            status=core_output.status,
            policy_id=core_output.policy_id,
            dataset_name=core_output.dataset_name,
            confidence_policy=dict(core_output.confidence_policy),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "policy_profile_ready_event_id": policy_ready_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade[
                    "flow_completed_event_id"
                ],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S1ConfidenceCoreError as exc:
        failed_event_id = _new_s1_event_id()
        logger.warning(
            "confidence_policy_s1_main_flow_error",
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
        raise S1ConfidencePolicyServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event_id,
        ) from exc
    except S1ConfidencePolicyServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s1_event_id()
        logger.error(
            "confidence_policy_s1_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S1ConfidencePolicyServiceError(
            code="CONFIDENCE_POLICY_S1_FLOW_FAILED",
            message=f"Falha ao executar fluxo CONF S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/main-flow do CONF S1.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def execute_s2_confidence_policy_service(
    request: S2ConfidenceScaffoldRequest,
) -> S2ConfidencePolicyServiceOutput:
    """Execute CONF Sprint 2 main-flow service with actionable diagnostics.

    Args:
        request: CONF Sprint 2 input contract with auto/review/gap policy
            metadata and operational decision limits.

    Returns:
        S2ConfidencePolicyServiceOutput: Stable Sprint 2 service output with
            decision policy and observability identifiers.

    Raises:
        S2ConfidencePolicyServiceError: If main-flow decision execution fails
            or an unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"conf-s2-{uuid4().hex[:12]}"
    started_event_id = _new_s2_event_id()
    logger.info(
        "confidence_policy_s2_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": request.policy_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "decision_mode": request.decision_mode,
            "gap_escalation_required": request.gap_escalation_required,
        },
    )

    try:
        core_output = execute_s2_confidence_policy_main_flow(
            _to_s2_core_input(request=request, correlation_id=correlation_id)
        )

        policy_ready_event_id = _new_s2_event_id()
        logger.info(
            "confidence_policy_s2_profile_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": policy_ready_event_id,
                "policy_id": core_output.policy_id,
                "dataset_name": core_output.dataset_name,
                "entity_kind": core_output.decision_policy.get("entity_kind"),
                "field_weights_count": core_output.decision_policy.get("field_weights_count"),
                "gap_threshold": core_output.decision_policy.get("thresholds", {}).get("gap"),
            },
        )

        completed_event_id = _new_s2_event_id()
        logger.info(
            "confidence_policy_s2_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": core_output.policy_id,
                "dataset_name": core_output.dataset_name,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
                "decision": core_output.execucao.get("decision"),
                "confidence_score": core_output.execucao.get("confidence_score"),
                "gap_escalation_triggered": core_output.execucao.get(
                    "gap_escalation_triggered"
                ),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["confidence_policy_service_module"] = (
            "app.services.confidence_policy_service.execute_s2_confidence_policy_service"
        )
        pontos_integracao["confidence_policy_service_telemetry_module"] = (
            "app.services.confidence_policy_service"
        )

        return S2ConfidencePolicyServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S2,
            correlation_id=correlation_id,
            status=core_output.status,
            policy_id=core_output.policy_id,
            dataset_name=core_output.dataset_name,
            decision_policy=dict(core_output.decision_policy),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "policy_profile_ready_event_id": policy_ready_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade[
                    "flow_completed_event_id"
                ],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S2ConfidenceCoreError as exc:
        failed_event_id = _new_s2_event_id()
        logger.warning(
            "confidence_policy_s2_main_flow_error",
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
        raise S2ConfidencePolicyServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event_id,
        ) from exc
    except S2ConfidencePolicyServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s2_event_id()
        logger.error(
            "confidence_policy_s2_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S2ConfidencePolicyServiceError(
            code="CONFIDENCE_POLICY_S2_FLOW_FAILED",
            message=f"Falha ao executar fluxo CONF S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada/main-flow do CONF S2.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def execute_s3_confidence_policy_service(
    request: S3ConfidenceScaffoldRequest,
) -> S3ConfidencePolicyServiceOutput:
    """Execute CONF Sprint 3 scaffold service with actionable diagnostics.

    Args:
        request: CONF Sprint 3 input contract with critical-field guardrails
            metadata and operational routing rules.

    Returns:
        S3ConfidencePolicyServiceOutput: Stable Sprint 3 service output with
            decision policy and observability identifiers.

    Raises:
        S3ConfidencePolicyServiceError: If scaffold validation fails or an
            unexpected service error happens.
    """

    correlation_id = request.correlation_id or f"conf-s3-{uuid4().hex[:12]}"
    started_event_id = _new_s3_event_id()
    logger.info(
        "confidence_policy_s3_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "policy_id": request.policy_id,
            "dataset_name": request.dataset_name,
            "entity_kind": request.entity_kind,
            "schema_version": request.schema_version,
            "decision_mode": request.decision_mode,
            "critical_violation_route": request.critical_violation_route,
        },
    )

    try:
        scaffold = build_s3_confidence_scaffold(
            _to_s3_scaffold_input(request=request, correlation_id=correlation_id)
        )

        policy_ready_event_id = _new_s3_event_id()
        logger.info(
            "confidence_policy_s3_profile_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": policy_ready_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "entity_kind": scaffold.decision_policy.get("entity_kind"),
                "critical_fields_count": (
                    scaffold.decision_policy.get("critical_fields_policy", {}).get(
                        "critical_fields_count"
                    )
                ),
                "critical_violation_route": (
                    scaffold.decision_policy.get("critical_fields_policy", {}).get(
                        "critical_violation_route"
                    )
                ),
            },
        )

        completed_event_id = _new_s3_event_id()
        logger.info(
            "confidence_policy_s3_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "status": scaffold.status,
                "execution_status": "ready",
                "critical_override_required": (
                    scaffold.decision_policy.get("critical_fields_policy", {}).get(
                        "critical_override_required"
                    )
                ),
            },
        )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["confidence_policy_service_module"] = (
            "app.services.confidence_policy_service.execute_s3_confidence_policy_service"
        )
        pontos_integracao["confidence_policy_service_telemetry_module"] = (
            "app.services.confidence_policy_service"
        )

        return S3ConfidencePolicyServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S3,
            correlation_id=correlation_id,
            status=scaffold.status,
            policy_id=scaffold.policy_id,
            dataset_name=scaffold.dataset_name,
            decision_policy=dict(scaffold.decision_policy),
            execucao={
                "status": "ready",
                "decision_reason": "scaffold_only_critical_fields_contract",
                "critical_override_required": bool(
                    scaffold.decision_policy.get("critical_fields_policy", {}).get(
                        "critical_override_required",
                        False,
                    )
                ),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "policy_profile_ready_event_id": policy_ready_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S3ConfidenceScaffoldError as exc:
        failed_event_id = _new_s3_event_id()
        logger.warning(
            "confidence_policy_s3_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S3ConfidencePolicyServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S3ConfidencePolicyServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s3_event_id()
        logger.error(
            "confidence_policy_s3_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3ConfidencePolicyServiceError(
            code="CONFIDENCE_POLICY_S3_FLOW_FAILED",
            message=f"Falha ao executar fluxo CONF S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do CONF S3.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def _new_s1_event_id() -> str:
    return f"confs1evt-{uuid4().hex[:12]}"


def _new_s2_event_id() -> str:
    return f"confs2evt-{uuid4().hex[:12]}"


def _new_s3_event_id() -> str:
    return f"confs3evt-{uuid4().hex[:12]}"


def _to_s1_core_input(
    *,
    request: S1ConfidenceScaffoldRequest,
    correlation_id: str,
) -> S1ConfidenceCoreInput:
    return S1ConfidenceCoreInput(
        policy_id=request.policy_id,
        dataset_name=request.dataset_name,
        entity_kind=request.entity_kind,
        schema_version=request.schema_version,
        owner_team=request.owner_team,
        field_weights=request.field_weights,
        default_weight=request.default_weight,
        auto_approve_threshold=request.auto_approve_threshold,
        manual_review_threshold=request.manual_review_threshold,
        missing_field_penalty=request.missing_field_penalty,
        decision_mode=request.decision_mode,
        correlation_id=correlation_id,
    )


def _to_s2_core_input(
    *,
    request: S2ConfidenceScaffoldRequest,
    correlation_id: str,
) -> S2ConfidenceCoreInput:
    return S2ConfidenceCoreInput(
        policy_id=request.policy_id,
        dataset_name=request.dataset_name,
        entity_kind=request.entity_kind,
        schema_version=request.schema_version,
        owner_team=request.owner_team,
        field_weights=request.field_weights,
        default_weight=request.default_weight,
        auto_approve_threshold=request.auto_approve_threshold,
        manual_review_threshold=request.manual_review_threshold,
        gap_threshold=request.gap_threshold,
        missing_field_penalty=request.missing_field_penalty,
        decision_mode=request.decision_mode,
        gap_escalation_required=request.gap_escalation_required,
        max_manual_review_queue=request.max_manual_review_queue,
        correlation_id=correlation_id,
    )


def _to_s3_scaffold_input(
    *,
    request: S3ConfidenceScaffoldRequest,
    correlation_id: str,
) -> S3ConfidenceScaffoldRequest:
    return S3ConfidenceScaffoldRequest(
        policy_id=request.policy_id,
        dataset_name=request.dataset_name,
        entity_kind=request.entity_kind,
        schema_version=request.schema_version,
        owner_team=request.owner_team,
        field_weights=request.field_weights,
        default_weight=request.default_weight,
        auto_approve_threshold=request.auto_approve_threshold,
        manual_review_threshold=request.manual_review_threshold,
        gap_threshold=request.gap_threshold,
        missing_field_penalty=request.missing_field_penalty,
        decision_mode=request.decision_mode,
        gap_escalation_required=request.gap_escalation_required,
        max_manual_review_queue=request.max_manual_review_queue,
        critical_fields=request.critical_fields,
        min_critical_fields_present=request.min_critical_fields_present,
        critical_field_penalty=request.critical_field_penalty,
        critical_violation_route=request.critical_violation_route,
        critical_override_required=request.critical_override_required,
        correlation_id=correlation_id,
    )
