"""Operational service for CONF Sprint 1 confidence policy scaffolding.

This module executes CONF Sprint 1 scaffold contracts for field-level
confidence policy and emits structured operational logs with actionable errors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

try:  # pragma: no cover - import style depends on execution cwd
    from core.confidence.s1_scaffold import (
        S1ConfidenceScaffoldError,
        S1ConfidenceScaffoldRequest,
        build_s1_confidence_scaffold,
    )
except ModuleNotFoundError:  # pragma: no cover
    npbb_root = Path(__file__).resolve().parents[3]
    if str(npbb_root) not in sys.path:
        sys.path.insert(0, str(npbb_root))
    from core.confidence.s1_scaffold import (
        S1ConfidenceScaffoldError,
        S1ConfidenceScaffoldRequest,
        build_s1_confidence_scaffold,
    )


logger = logging.getLogger("app.services.confidence_policy")

SERVICE_CONTRACT_VERSION_S1 = "conf.s1.service.v1"


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


def execute_s1_confidence_policy_service(
    request: S1ConfidenceScaffoldRequest,
) -> S1ConfidencePolicyServiceOutput:
    """Execute CONF Sprint 1 scaffold service with actionable diagnostics.

    Args:
        request: CONF Sprint 1 input contract with field-level scoring policy
            metadata and decision thresholds.

    Returns:
        S1ConfidencePolicyServiceOutput: Stable Sprint 1 service output with
            policy metadata and observability identifiers.

    Raises:
        S1ConfidencePolicyServiceError: If scaffold validation fails or an
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
        scaffold = build_s1_confidence_scaffold(
            _to_s1_scaffold_input(request=request, correlation_id=correlation_id)
        )

        policy_ready_event_id = _new_s1_event_id()
        logger.info(
            "confidence_policy_s1_profile_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": policy_ready_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "entity_kind": scaffold.confidence_policy.get("entity_kind"),
                "field_weights_count": scaffold.confidence_policy.get("field_weights_count"),
            },
        )

        completed_event_id = _new_s1_event_id()
        logger.info(
            "confidence_policy_s1_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "policy_id": scaffold.policy_id,
                "dataset_name": scaffold.dataset_name,
                "status": scaffold.status,
                "execution_status": "ready",
            },
        )

        pontos_integracao = dict(scaffold.pontos_integracao)
        pontos_integracao["confidence_policy_service_module"] = (
            "app.services.confidence_policy_service.execute_s1_confidence_policy_service"
        )
        pontos_integracao["confidence_policy_service_telemetry_module"] = (
            "app.services.confidence_policy_service"
        )

        return S1ConfidencePolicyServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S1,
            correlation_id=correlation_id,
            status=scaffold.status,
            policy_id=scaffold.policy_id,
            dataset_name=scaffold.dataset_name,
            confidence_policy=dict(scaffold.confidence_policy),
            execucao={
                "status": "ready",
                "decision_reason": "scaffold_only_base_contract",
                "field_weights_count": int(scaffold.confidence_policy.get("field_weights_count", 0)),
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "policy_profile_ready_event_id": policy_ready_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold.to_dict(),
        )
    except S1ConfidenceScaffoldError as exc:
        failed_event_id = _new_s1_event_id()
        logger.warning(
            "confidence_policy_s1_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S1ConfidencePolicyServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
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
            action="Revisar logs operacionais e validar contrato de entrada do CONF S1.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def _new_s1_event_id() -> str:
    return f"confs1evt-{uuid4().hex[:12]}"


def _to_s1_scaffold_input(
    *,
    request: S1ConfidenceScaffoldRequest,
    correlation_id: str,
) -> S1ConfidenceScaffoldRequest:
    return S1ConfidenceScaffoldRequest(
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
