"""Operational service for XIA Sprint 1 AI extraction main flow.

This module executes Sprint 1 contracts for bounded AI extraction on digital
PDF and DOCX files and emits structured operational logs with actionable
errors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

try:  # pragma: no cover - import style depends on execution cwd
    from etl.extract.ai.s1_core import (
        S1AIExtractCoreError,
        S1AIExtractCoreInput,
        execute_s1_ai_extract_main_flow,
    )
    from etl.extract.ai.s1_scaffold import (
        S1AIExtractScaffoldRequest,
    )
    from etl.extract.ai.s2_scaffold import (
        S2AIExtractScaffoldRequest,
    )
    from etl.extract.ai.s2_core import (
        S2AIExtractCoreError,
        S2AIExtractCoreInput,
        execute_s2_ai_extract_main_flow,
    )
    from etl.extract.ai.s3_scaffold import (
        S3AIExtractScaffoldRequest,
    )
    from etl.extract.ai.s4_scaffold import (
        S4AIExtractScaffoldError,
        S4AIExtractScaffoldRequest,
        build_s4_ai_extract_scaffold_contract,
    )
    from etl.extract.ai.s3_core import (
        S3AIExtractCoreError,
        S3AIExtractCoreInput,
        execute_s3_ai_extract_main_flow,
    )
except ModuleNotFoundError:  # pragma: no cover
    npbb_root = Path(__file__).resolve().parents[3]
    if str(npbb_root) not in sys.path:
        sys.path.insert(0, str(npbb_root))
    from etl.extract.ai.s1_core import (
        S1AIExtractCoreError,
        S1AIExtractCoreInput,
        execute_s1_ai_extract_main_flow,
    )
    from etl.extract.ai.s1_scaffold import (
        S1AIExtractScaffoldRequest,
    )
    from etl.extract.ai.s2_scaffold import (
        S2AIExtractScaffoldRequest,
    )
    from etl.extract.ai.s2_core import (
        S2AIExtractCoreError,
        S2AIExtractCoreInput,
        execute_s2_ai_extract_main_flow,
    )
    from etl.extract.ai.s3_scaffold import (
        S3AIExtractScaffoldRequest,
    )
    from etl.extract.ai.s4_scaffold import (
        S4AIExtractScaffoldError,
        S4AIExtractScaffoldRequest,
        build_s4_ai_extract_scaffold_contract,
    )
    from etl.extract.ai.s3_core import (
        S3AIExtractCoreError,
        S3AIExtractCoreInput,
        execute_s3_ai_extract_main_flow,
    )


logger = logging.getLogger("app.services.etl_extract_ai")

SERVICE_CONTRACT_VERSION_S1 = "xia.s1.service.v1"
SERVICE_CONTRACT_VERSION_S2 = "xia.s2.service.v1"
SERVICE_CONTRACT_VERSION_S3 = "xia.s3.service.v1"
SERVICE_CONTRACT_VERSION_S4 = "xia.s4.service.v1"


class S1AIExtractServiceError(RuntimeError):
    """Raised when XIA Sprint 1 service flow fails."""

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


class S2AIExtractServiceError(RuntimeError):
    """Raised when XIA Sprint 2 service flow fails."""

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


class S3AIExtractServiceError(RuntimeError):
    """Raised when XIA Sprint 3 service flow fails."""

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


class S4AIExtractServiceError(RuntimeError):
    """Raised when XIA Sprint 4 service flow fails."""

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
class S1AIExtractServiceOutput:
    """Output contract returned by XIA Sprint 1 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    extraction_plan: dict[str, Any]
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "extraction_plan": self.extraction_plan,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S2AIExtractServiceOutput:
    """Output contract returned by XIA Sprint 2 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    extraction_plan: dict[str, Any]
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "extraction_plan": self.extraction_plan,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S3AIExtractServiceOutput:
    """Output contract returned by XIA Sprint 3 service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    extraction_plan: dict[str, Any]
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "extraction_plan": self.extraction_plan,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


@dataclass(frozen=True, slots=True)
class S4AIExtractServiceOutput:
    """Output contract returned by XIA Sprint 4 scaffold service flow."""

    contrato_versao: str
    correlation_id: str
    status: str
    source_id: str
    source_kind: str
    source_uri: str
    extraction_plan: dict[str, Any]
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
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "extraction_plan": self.extraction_plan,
            "execucao": self.execucao,
            "pontos_integracao": self.pontos_integracao,
            "observabilidade": self.observabilidade,
            "scaffold": self.scaffold,
        }


def execute_s1_extract_ai_service(
    request: S1AIExtractScaffoldRequest,
) -> S1AIExtractServiceOutput:
    """Execute XIA Sprint 1 main-flow service with actionable diagnostics.

    Args:
        request: XIA Sprint 1 input contract with source metadata and AI
            extraction parameters.

    Returns:
        S1AIExtractServiceOutput: Stable Sprint 1 service output with
            extraction plan, execution diagnostics, and observability
            identifiers.

    Raises:
        S1AIExtractServiceError: If main-flow validation fails or an unexpected
            service error happens.
    """

    correlation_id = request.correlation_id or f"xia-s1-{uuid4().hex[:12]}"
    started_event_id = _new_s1_event_id()
    logger.info(
        "etl_extract_ai_s1_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "ia_model_provider": request.ia_model_provider,
            "chunk_strategy": request.chunk_strategy,
        },
    )

    try:
        core_output = execute_s1_ai_extract_main_flow(
            _to_s1_core_input(request=request, correlation_id=correlation_id)
        )

        plan_event_id = _new_s1_event_id()
        logger.info(
            "etl_extract_ai_s1_plan_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": plan_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "ia_model_provider": core_output.extraction_plan.get("ia_model_provider"),
                "chunk_strategy": core_output.extraction_plan.get("chunk_strategy"),
                "chunk_count": core_output.execucao.get("chunk_count"),
            },
        )

        completed_event_id = _new_s1_event_id()
        logger.info(
            "etl_extract_ai_s1_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["extract_ai_service_module"] = (
            "app.services.etl_extract_ai_service.execute_s1_extract_ai_service"
        )
        pontos_integracao["extract_ai_service_telemetry_module"] = (
            "app.services.etl_extract_ai_service"
        )

        return S1AIExtractServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S1,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            extraction_plan=dict(core_output.extraction_plan),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "plan_ready_event_id": plan_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade["flow_completed_event_id"],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S1AIExtractCoreError as exc:
        failed_event_id = _new_s1_event_id()
        logger.warning(
            "etl_extract_ai_s1_main_flow_error",
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
        raise S1AIExtractServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S1AIExtractServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s1_event_id()
        logger.error(
            "etl_extract_ai_s1_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S1AIExtractServiceError(
            code="ETL_EXTRACT_AI_S1_FLOW_FAILED",
            message=f"Falha ao executar fluxo principal XIA S1: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do XIA S1.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def build_s1_extract_ai_error_detail(
    *,
    code: str,
    message: str,
    action: str,
    correlation_id: str,
    event_id: str,
    stage: str = "service",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build actionable XIA Sprint 1 error detail for API responses.

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


def execute_s2_extract_ai_service(
    request: S2AIExtractScaffoldRequest,
) -> S2AIExtractServiceOutput:
    """Execute XIA Sprint 2 scaffold service with actionable diagnostics.

    Args:
        request: XIA Sprint 2 input contract with source metadata and AI
            extraction parameters for PPTX and non-standardized XLSX/CSV.

    Returns:
        S2AIExtractServiceOutput: Stable Sprint 2 service output with
            extraction plan and observability identifiers.

    Raises:
        S2AIExtractServiceError: If scaffold validation fails or an unexpected
            service error happens.
    """

    correlation_id = request.correlation_id or f"xia-s2-{uuid4().hex[:12]}"
    started_event_id = _new_s2_event_id()
    logger.info(
        "etl_extract_ai_s2_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "ia_model_provider": request.ia_model_provider,
            "chunk_strategy": request.chunk_strategy,
        },
    )

    try:
        core_output = execute_s2_ai_extract_main_flow(
            _to_s2_core_input(request=request, correlation_id=correlation_id)
        )

        plan_event_id = _new_s2_event_id()
        logger.info(
            "etl_extract_ai_s2_plan_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": plan_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "ia_model_provider": core_output.extraction_plan.get("ia_model_provider"),
                "chunk_strategy": core_output.extraction_plan.get("chunk_strategy"),
                "chunk_count": core_output.execucao.get("chunk_count"),
            },
        )

        completed_event_id = _new_s2_event_id()
        logger.info(
            "etl_extract_ai_s2_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["extract_ai_service_module"] = (
            "app.services.etl_extract_ai_service.execute_s2_extract_ai_service"
        )
        pontos_integracao["extract_ai_service_telemetry_module"] = (
            "app.services.etl_extract_ai_service"
        )

        return S2AIExtractServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S2,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            extraction_plan=dict(core_output.extraction_plan),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "plan_ready_event_id": plan_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade["flow_completed_event_id"],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S2AIExtractCoreError as exc:
        failed_event_id = _new_s2_event_id()
        logger.warning(
            "etl_extract_ai_s2_main_flow_error",
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
        raise S2AIExtractServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event_id,
        ) from exc
    except S2AIExtractServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s2_event_id()
        logger.error(
            "etl_extract_ai_s2_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S2AIExtractServiceError(
            code="ETL_EXTRACT_AI_S2_FLOW_FAILED",
            message=f"Falha ao executar fluxo XIA S2: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do XIA S2.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def execute_s3_extract_ai_service(
    request: S3AIExtractScaffoldRequest,
) -> S3AIExtractServiceOutput:
    """Execute XIA Sprint 3 scaffold service with actionable diagnostics.

    Args:
        request: XIA Sprint 3 input contract with source metadata and AI
            extraction parameters for PDF scan and JPG/PNG documents.

    Returns:
        S3AIExtractServiceOutput: Stable Sprint 3 service output with
            extraction plan and observability identifiers.

    Raises:
        S3AIExtractServiceError: If scaffold validation fails or an unexpected
            service error happens.
    """

    correlation_id = request.correlation_id or f"xia-s3-{uuid4().hex[:12]}"
    started_event_id = _new_s3_event_id()
    logger.info(
        "etl_extract_ai_s3_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "ia_model_provider": request.ia_model_provider,
            "chunk_strategy": request.chunk_strategy,
        },
    )

    try:
        core_output = execute_s3_ai_extract_main_flow(
            _to_s3_core_input(request=request, correlation_id=correlation_id)
        )

        plan_event_id = _new_s3_event_id()
        logger.info(
            "etl_extract_ai_s3_plan_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": plan_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "ia_model_provider": core_output.extraction_plan.get("ia_model_provider"),
                "chunk_strategy": core_output.extraction_plan.get("chunk_strategy"),
                "chunk_count": core_output.execucao.get("chunk_count"),
            },
        )

        completed_event_id = _new_s3_event_id()
        logger.info(
            "etl_extract_ai_s3_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": core_output.source_id,
                "source_kind": core_output.source_kind,
                "status": core_output.status,
                "execution_status": core_output.execucao.get("status"),
            },
        )

        pontos_integracao = dict(core_output.pontos_integracao)
        pontos_integracao["extract_ai_service_module"] = (
            "app.services.etl_extract_ai_service.execute_s3_extract_ai_service"
        )
        pontos_integracao["extract_ai_service_telemetry_module"] = (
            "app.services.etl_extract_ai_service"
        )

        return S3AIExtractServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S3,
            correlation_id=correlation_id,
            status=core_output.status,
            source_id=core_output.source_id,
            source_kind=core_output.source_kind,
            source_uri=core_output.source_uri,
            extraction_plan=dict(core_output.extraction_plan),
            execucao=dict(core_output.execucao),
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "plan_ready_event_id": plan_event_id,
                "flow_completed_event_id": completed_event_id,
                "main_flow_started_event_id": core_output.observabilidade["flow_started_event_id"],
                "main_flow_completed_event_id": core_output.observabilidade["flow_completed_event_id"],
            },
            scaffold=dict(core_output.scaffold),
        )
    except S3AIExtractCoreError as exc:
        failed_event_id = _new_s3_event_id()
        logger.warning(
            "etl_extract_ai_s3_main_flow_error",
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
        raise S3AIExtractServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage=exc.stage,
            event_id=failed_event_id,
        ) from exc
    except S3AIExtractServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s3_event_id()
        logger.error(
            "etl_extract_ai_s3_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S3AIExtractServiceError(
            code="ETL_EXTRACT_AI_S3_FLOW_FAILED",
            message=f"Falha ao executar fluxo XIA S3: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do XIA S3.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def execute_s4_extract_ai_service(
    request: S4AIExtractScaffoldRequest,
) -> S4AIExtractServiceOutput:
    """Execute XIA Sprint 4 scaffold service with actionable diagnostics.

    Args:
        request: XIA Sprint 4 input contract with source metadata and quality
            calibration parameters.

    Returns:
        S4AIExtractServiceOutput: Stable Sprint 4 scaffold service output with
            extraction plan and observability identifiers.

    Raises:
        S4AIExtractServiceError: If scaffold validation fails or an unexpected
            service error happens.
    """

    correlation_id = request.correlation_id or f"xia-s4-{uuid4().hex[:12]}"
    started_event_id = _new_s4_event_id()
    logger.info(
        "etl_extract_ai_s4_flow_started",
        extra={
            "correlation_id": correlation_id,
            "event_id": started_event_id,
            "source_id": request.source_id,
            "source_kind": request.source_kind,
            "quality_profile_hint": request.quality_profile_hint,
            "consolidation_scope": request.consolidation_scope,
            "ia_model_provider": request.ia_model_provider,
        },
    )

    try:
        scaffold_output = build_s4_ai_extract_scaffold_contract(
            S4AIExtractScaffoldRequest(
                source_id=request.source_id,
                source_kind=request.source_kind,
                source_uri=request.source_uri,
                quality_profile_hint=request.quality_profile_hint,
                consolidation_scope=request.consolidation_scope,
                output_normalization_profile=request.output_normalization_profile,
                ia_model_provider=request.ia_model_provider,
                ia_model_name=request.ia_model_name,
                chunk_strategy=request.chunk_strategy,
                max_tokens_output=request.max_tokens_output,
                temperature=request.temperature,
                correlation_id=correlation_id,
            )
        )

        plan_event_id = _new_s4_event_id()
        logger.info(
            "etl_extract_ai_s4_plan_ready",
            extra={
                "correlation_id": correlation_id,
                "event_id": plan_event_id,
                "source_id": scaffold_output.source_id,
                "source_kind": scaffold_output.source_kind,
                "quality_profile_hint": scaffold_output.extraction_plan.get("quality_profile_hint"),
                "consolidation_scope": scaffold_output.extraction_plan.get("consolidation_scope"),
                "output_normalization_profile": scaffold_output.extraction_plan.get(
                    "output_normalization_profile"
                ),
            },
        )

        completed_event_id = _new_s4_event_id()
        logger.info(
            "etl_extract_ai_s4_flow_completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": completed_event_id,
                "source_id": scaffold_output.source_id,
                "source_kind": scaffold_output.source_kind,
                "status": scaffold_output.status,
            },
        )

        pontos_integracao = dict(scaffold_output.pontos_integracao)
        pontos_integracao["extract_ai_service_module"] = (
            "app.services.etl_extract_ai_service.execute_s4_extract_ai_service"
        )
        pontos_integracao["extract_ai_service_telemetry_module"] = (
            "app.services.etl_extract_ai_service"
        )

        return S4AIExtractServiceOutput(
            contrato_versao=SERVICE_CONTRACT_VERSION_S4,
            correlation_id=correlation_id,
            status=scaffold_output.status,
            source_id=scaffold_output.source_id,
            source_kind=scaffold_output.source_kind,
            source_uri=scaffold_output.source_uri,
            extraction_plan=dict(scaffold_output.extraction_plan),
            execucao={
                "status": "not_started",
                "decision_reason": "s4_scaffold_ready_for_core_integration",
                "chunk_count": 0,
            },
            pontos_integracao=pontos_integracao,
            observabilidade={
                "flow_started_event_id": started_event_id,
                "plan_ready_event_id": plan_event_id,
                "flow_completed_event_id": completed_event_id,
            },
            scaffold=scaffold_output.to_dict(),
        )
    except S4AIExtractScaffoldError as exc:
        failed_event_id = _new_s4_event_id()
        logger.warning(
            "etl_extract_ai_s4_scaffold_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "recommended_action": exc.action,
            },
        )
        raise S4AIExtractServiceError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            stage="scaffold",
            event_id=failed_event_id,
        ) from exc
    except S4AIExtractServiceError:
        raise
    except Exception as exc:
        failed_event_id = _new_s4_event_id()
        logger.error(
            "etl_extract_ai_s4_flow_unexpected_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": failed_event_id,
                "error_type": type(exc).__name__,
            },
        )
        raise S4AIExtractServiceError(
            code="ETL_EXTRACT_AI_S4_FLOW_FAILED",
            message=f"Falha ao executar fluxo XIA S4: {type(exc).__name__}",
            action="Revisar logs operacionais e validar contrato de entrada do XIA S4.",
            correlation_id=correlation_id,
            stage="service",
            event_id=failed_event_id,
        ) from exc


def _new_s1_event_id() -> str:
    return f"xias1evt-{uuid4().hex[:12]}"


def _new_s2_event_id() -> str:
    return f"xias2evt-{uuid4().hex[:12]}"


def _new_s3_event_id() -> str:
    return f"xias3evt-{uuid4().hex[:12]}"


def _new_s4_event_id() -> str:
    return f"xias4evt-{uuid4().hex[:12]}"


def _to_s1_core_input(
    *,
    request: S1AIExtractScaffoldRequest,
    correlation_id: str,
) -> S1AIExtractCoreInput:
    return S1AIExtractCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        document_profile_hint=request.document_profile_hint,
        ia_model_provider=request.ia_model_provider,
        ia_model_name=request.ia_model_name,
        chunk_strategy=request.chunk_strategy,
        max_tokens_output=request.max_tokens_output,
        temperature=request.temperature,
        correlation_id=correlation_id,
    )


def _to_s2_core_input(
    *,
    request: S2AIExtractScaffoldRequest,
    correlation_id: str,
) -> S2AIExtractCoreInput:
    return S2AIExtractCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        document_profile_hint=request.document_profile_hint,
        tabular_layout_hint=request.tabular_layout_hint,
        ia_model_provider=request.ia_model_provider,
        ia_model_name=request.ia_model_name,
        chunk_strategy=request.chunk_strategy,
        max_tokens_output=request.max_tokens_output,
        temperature=request.temperature,
        correlation_id=correlation_id,
    )


def _to_s3_core_input(
    *,
    request: S3AIExtractScaffoldRequest,
    correlation_id: str,
) -> S3AIExtractCoreInput:
    return S3AIExtractCoreInput(
        source_id=request.source_id,
        source_kind=request.source_kind,
        source_uri=request.source_uri,
        document_profile_hint=request.document_profile_hint,
        image_preprocess_hint=request.image_preprocess_hint,
        ia_model_provider=request.ia_model_provider,
        ia_model_name=request.ia_model_name,
        chunk_strategy=request.chunk_strategy,
        max_tokens_output=request.max_tokens_output,
        temperature=request.temperature,
        correlation_id=correlation_id,
    )
