"""Operational tools for ORQ Sprint 1, Sprint 2, and Sprint 3 flows.

This script offers small, verifiable commands for runbook operations:
1. Validate ORQ Sprint 1/Sprint 2/Sprint 3 input contracts.
2. Simulate core and service flow execution.
3. Execute end-to-end runbook checks with stable sample inputs.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.etl_orchestrator_service import (  # noqa: E402
    S1OrchestratorServiceError,
    S2OrchestratorServiceError,
    S3OrchestratorServiceError,
    execute_s1_orchestrator_service,
    execute_s2_orchestrator_service,
    execute_s3_orchestrator_service,
)
from etl.orchestrator.s1_core import (  # noqa: E402
    S1OrchestratorCoreError,
    execute_s1_orchestrator_main_flow,
)
from etl.orchestrator.s1_validation import (  # noqa: E402
    S1OrchestratorValidationError,
    S1OrchestratorValidationInput,
    validate_s1_orchestrator_flow_output_contract,
    validate_s1_orchestrator_input_contract,
)
from etl.orchestrator.s2_core import (  # noqa: E402
    S2OrchestratorCoreError,
    execute_s2_orchestrator_main_flow,
)
from etl.orchestrator.s2_validation import (  # noqa: E402
    S2OrchestratorValidationError,
    S2OrchestratorValidationInput,
    validate_s2_orchestrator_flow_output_contract,
    validate_s2_orchestrator_input_contract,
)
from etl.orchestrator.s3_core import (  # noqa: E402
    S3OrchestratorCoreError,
    execute_s3_orchestrator_main_flow,
)
from etl.orchestrator.s3_validation import (  # noqa: E402
    S3OrchestratorValidationError,
    S3OrchestratorValidationInput,
    validate_s3_orchestrator_flow_output_contract,
    validate_s3_orchestrator_input_contract,
)


logger = logging.getLogger("npbb.orquestrador_hibrido.tools")


class ToolExecutionError(RuntimeError):
    """Raised when a runbook command fails with actionable context."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Return serializable payload for CLI output."""

        return {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "context": self.context,
        }


def _build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for ORQ Sprint 1, Sprint 2, and Sprint 3 commands."""

    parser = argparse.ArgumentParser(prog="orquestrador_hibrido_tools")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logger level for operational traces.",
    )
    parser.add_argument(
        "--output-format",
        default="pretty",
        choices=("pretty", "json"),
        help="Command output format.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser(
        "s1:validate-input",
        help="Validate ORQ Sprint 1 input contract.",
    )
    _add_s1_common_args(validate_parser, required=True)

    simulate_core_parser = sub.add_parser(
        "s1:simulate-core",
        help="Simulate ORQ Sprint 1 core flow and validate output contract.",
    )
    _add_s1_common_args(simulate_core_parser, required=True)

    simulate_service_parser = sub.add_parser(
        "s1:simulate-service",
        help="Simulate ORQ Sprint 1 service flow and validate output contract.",
    )
    _add_s1_common_args(simulate_service_parser, required=True)

    runbook_parser = sub.add_parser(
        "s1:runbook-check",
        help="Run one complete local ORQ Sprint 1 runbook check.",
    )
    _add_s1_common_args(runbook_parser, required=False)
    runbook_parser.set_defaults(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        profile_strategy_hint="hybrid",
        ia_habilitada="true",
        permitir_fallback_manual="true",
        correlation_id=None,
    )

    s2_validate_parser = sub.add_parser(
        "s2:validate-input",
        help="Validate ORQ Sprint 2 input contract.",
    )
    _add_s2_common_args(s2_validate_parser, required=True)

    s2_simulate_core_parser = sub.add_parser(
        "s2:simulate-core",
        help="Simulate ORQ Sprint 2 core flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_core_parser, required=True)

    s2_simulate_service_parser = sub.add_parser(
        "s2:simulate-service",
        help="Simulate ORQ Sprint 2 service flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_service_parser, required=True)

    s2_runbook_parser = sub.add_parser(
        "s2:runbook-check",
        help="Run one complete local ORQ Sprint 2 runbook check.",
    )
    _add_s2_common_args(s2_runbook_parser, required=False)
    s2_runbook_parser.set_defaults(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="hybrid_pdf_extract",
        ia_habilitada="true",
        permitir_fallback_manual="true",
        retry_attempts=1,
        timeout_seconds=240,
        correlation_id=None,
    )

    s3_validate_parser = sub.add_parser(
        "s3:validate-input",
        help="Validate ORQ Sprint 3 input contract.",
    )
    _add_s3_common_args(s3_validate_parser, required=True)

    s3_simulate_core_parser = sub.add_parser(
        "s3:simulate-core",
        help="Simulate ORQ Sprint 3 core flow and validate output contract.",
    )
    _add_s3_common_args(s3_simulate_core_parser, required=True)

    s3_simulate_service_parser = sub.add_parser(
        "s3:simulate-service",
        help="Simulate ORQ Sprint 3 service flow and validate output contract.",
    )
    _add_s3_common_args(s3_simulate_service_parser, required=True)

    s3_runbook_parser = sub.add_parser(
        "s3:runbook-check",
        help="Run one complete local ORQ Sprint 3 runbook check.",
    )
    _add_s3_common_args(s3_runbook_parser, required=False)
    s3_runbook_parser.set_defaults(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        rota_selecionada="agent_first_extract",
        agent_habilitado="true",
        permitir_fallback_deterministico="true",
        permitir_fallback_manual="true",
        retry_attempts=1,
        timeout_seconds=240,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_reset_timeout_seconds=180,
        correlation_id=None,
    )
    return parser


def _add_s1_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common ORQ Sprint 1 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by routing policy (pdf, xlsx, csv, pptx, docx, other).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--profile-strategy-hint",
        default=None,
        help="Optional PDF profile hint (text_table, ocr_or_assisted, hybrid, manual_assisted).",
    )
    parser.add_argument(
        "--ia-habilitada",
        default="true",
        choices=("true", "false"),
        help="Whether IA-assisted routing is enabled.",
    )
    parser.add_argument(
        "--permitir-fallback-manual",
        default="true",
        choices=("true", "false"),
        help="Whether manual fallback route is enabled.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s2_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common ORQ Sprint 2 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by deterministic-first policy (pdf, xlsx, csv, pptx, docx, other).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--rota-selecionada",
        required=required,
        help=(
            "Selected route (deterministic_tabular_extract, deterministic_pdf_extract, "
            "ia_assisted_pdf_extract, hybrid_pdf_extract, hybrid_document_extract, manual_assistido_review)."
        ),
    )
    parser.add_argument(
        "--ia-habilitada",
        default="true",
        choices=("true", "false"),
        help="Whether IA-assisted fallback routes are enabled.",
    )
    parser.add_argument(
        "--permitir-fallback-manual",
        default="true",
        choices=("true", "false"),
        help="Whether manual fallback route is enabled.",
    )
    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=0,
        help="Current retry attempts already consumed before dispatch.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="Route timeout budget in seconds.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s3_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common ORQ Sprint 3 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by agent-first policy (pdf, xlsx, csv, pptx, docx, other).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--rota-selecionada",
        required=required,
        help=(
            "Selected route (agent_first_extract, agent_pdf_extract, agent_tabular_extract, "
            "agent_document_extract, manual_assistido_review)."
        ),
    )
    parser.add_argument(
        "--agent-habilitado",
        default="true",
        choices=("true", "false"),
        help="Whether agent-first routes are enabled.",
    )
    parser.add_argument(
        "--permitir-fallback-deterministico",
        default="true",
        choices=("true", "false"),
        help="Whether deterministic fallback routes are enabled.",
    )
    parser.add_argument(
        "--permitir-fallback-manual",
        default="true",
        choices=("true", "false"),
        help="Whether manual fallback route is enabled.",
    )
    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=0,
        help="Current retry attempts already consumed before dispatch.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=240,
        help="Route timeout budget in seconds.",
    )
    parser.add_argument(
        "--circuit-breaker-failure-threshold",
        type=int,
        default=3,
        help="Consecutive failure threshold before opening circuit breaker.",
    )
    parser.add_argument(
        "--circuit-breaker-reset-timeout-seconds",
        type=int,
        default=180,
        help="Time window to allow circuit breaker reset.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _as_bool(value: str) -> bool:
    """Convert CLI boolean string to Python bool."""

    return str(value).strip().lower() == "true"


def _build_validation_input_from_args(args: argparse.Namespace) -> S1OrchestratorValidationInput:
    """Build ORQ Sprint 1 validation input from parsed CLI args."""

    return S1OrchestratorValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        profile_strategy_hint=(
            str(args.profile_strategy_hint).strip() if args.profile_strategy_hint else None
        ),
        ia_habilitada=_as_bool(args.ia_habilitada),
        permitir_fallback_manual=_as_bool(args.permitir_fallback_manual),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s2_validation_input_from_args(args: argparse.Namespace) -> S2OrchestratorValidationInput:
    """Build ORQ Sprint 2 validation input from parsed CLI args."""

    return S2OrchestratorValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        rota_selecionada=str(args.rota_selecionada),
        ia_habilitada=_as_bool(args.ia_habilitada),
        permitir_fallback_manual=_as_bool(args.permitir_fallback_manual),
        retry_attempts=int(args.retry_attempts),
        timeout_seconds=int(args.timeout_seconds),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s3_validation_input_from_args(args: argparse.Namespace) -> S3OrchestratorValidationInput:
    """Build ORQ Sprint 3 validation input from parsed CLI args."""

    return S3OrchestratorValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        rota_selecionada=str(args.rota_selecionada),
        agent_habilitado=_as_bool(args.agent_habilitado),
        permitir_fallback_deterministico=_as_bool(args.permitir_fallback_deterministico),
        permitir_fallback_manual=_as_bool(args.permitir_fallback_manual),
        retry_attempts=int(args.retry_attempts),
        timeout_seconds=int(args.timeout_seconds),
        circuit_breaker_failure_threshold=int(args.circuit_breaker_failure_threshold),
        circuit_breaker_reset_timeout_seconds=int(args.circuit_breaker_reset_timeout_seconds),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _log_event(
    *,
    level: int,
    event_name: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Emit one operational event for this tool."""

    logger.log(
        level,
        event_name,
        extra={
            "correlation_id": correlation_id,
            "context": context or {},
        },
    )


def _run_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:validate-input` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={"source_kind": payload.source_kind},
    )
    result = validate_s1_orchestrator_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s1:validate-input", "result": result.to_dict()}


def _run_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-core` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_simulate_core_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind},
    )

    core_output = execute_s1_orchestrator_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_orchestrator_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "route": core_output.get("rota_selecionada"),
        },
    )
    return {
        "command": "s1:simulate-core",
        "input_validation": validation.to_dict(),
        "flow_output": core_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_simulate_service(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-service` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_simulate_service_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind},
    )

    service_output = execute_s1_orchestrator_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_orchestrator_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "route": service_output.get("rota_selecionada"),
        },
    )
    return {
        "command": "s1:simulate-service",
        "input_validation": validation.to_dict(),
        "flow_output": service_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:runbook-check` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s1_orchestrator_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s1_orchestrator_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s1_orchestrator_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s1_orchestrator_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s1_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "route": service_output.get("rota_selecionada"),
        },
    )
    return {
        "command": "s1:runbook-check",
        "input_validation": validation.to_dict(),
        "core_flow": {
            "output": core_output,
            "validation": core_output_validation.to_dict(),
        },
        "service_flow": {
            "output": service_output,
            "validation": service_output_validation.to_dict(),
        },
    }


def _run_s2_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:validate-input` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "source_kind": payload.source_kind,
            "rota_selecionada": payload.rota_selecionada,
        },
    )
    result = validate_s2_orchestrator_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s2:validate-input", "result": result.to_dict()}


def _run_s2_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:simulate-core` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    validation = validate_s2_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "source_kind": payload.source_kind,
            "rota_selecionada": payload.rota_selecionada,
        },
    )

    core_output = execute_s2_orchestrator_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_orchestrator_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "route": core_output.get("rota_selecionada"),
        },
    )
    return {
        "command": "s2:simulate-core",
        "input_validation": validation.to_dict(),
        "flow_output": core_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s2_simulate_service(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:simulate-service` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    validation = validate_s2_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "source_kind": payload.source_kind,
            "rota_selecionada": payload.rota_selecionada,
        },
    )

    service_output = execute_s2_orchestrator_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_orchestrator_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "route": service_output.get("rota_selecionada"),
        },
    )
    return {
        "command": "s2:simulate-service",
        "input_validation": validation.to_dict(),
        "flow_output": service_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s2_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:runbook-check` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    validation = validate_s2_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s2_orchestrator_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s2_orchestrator_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s2_orchestrator_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s2_orchestrator_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s2_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "route": service_output.get("rota_selecionada"),
        },
    )
    return {
        "command": "s2:runbook-check",
        "input_validation": validation.to_dict(),
        "core_flow": {
            "output": core_output,
            "validation": core_output_validation.to_dict(),
        },
        "service_flow": {
            "output": service_output,
            "validation": service_output_validation.to_dict(),
        },
    }


def _run_s3_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:validate-input` command and return output payload."""

    payload = _build_s3_validation_input_from_args(args)
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "source_kind": payload.source_kind,
            "rota_selecionada": payload.rota_selecionada,
            "circuit_breaker_failure_threshold": payload.circuit_breaker_failure_threshold,
        },
    )
    result = validate_s3_orchestrator_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s3:validate-input", "result": result.to_dict()}


def _run_s3_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:simulate-core` command and return output payload."""

    payload = _build_s3_validation_input_from_args(args)
    validation = validate_s3_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "source_kind": payload.source_kind,
            "rota_selecionada": payload.rota_selecionada,
            "circuit_breaker_failure_threshold": payload.circuit_breaker_failure_threshold,
        },
    )

    core_output = execute_s3_orchestrator_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s3_orchestrator_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "route": core_output.get("rota_selecionada"),
            "circuit_state": core_output.get("circuit_breaker", {}).get("state"),
        },
    )
    return {
        "command": "s3:simulate-core",
        "input_validation": validation.to_dict(),
        "flow_output": core_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s3_simulate_service(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:simulate-service` command and return output payload."""

    payload = _build_s3_validation_input_from_args(args)
    validation = validate_s3_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "source_kind": payload.source_kind,
            "rota_selecionada": payload.rota_selecionada,
            "circuit_breaker_failure_threshold": payload.circuit_breaker_failure_threshold,
        },
    )

    service_output = execute_s3_orchestrator_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s3_orchestrator_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "route": service_output.get("rota_selecionada"),
            "circuit_state": service_output.get("circuit_breaker", {}).get("state"),
        },
    )
    return {
        "command": "s3:simulate-service",
        "input_validation": validation.to_dict(),
        "flow_output": service_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s3_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:runbook-check` command and return output payload."""

    payload = _build_s3_validation_input_from_args(args)
    validation = validate_s3_orchestrator_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s3_orchestrator_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s3_orchestrator_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s3_orchestrator_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s3_orchestrator_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="orq_s3_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "route": service_output.get("rota_selecionada"),
            "circuit_state": service_output.get("circuit_breaker", {}).get("state"),
        },
    )
    return {
        "command": "s3:runbook-check",
        "input_validation": validation.to_dict(),
        "core_flow": {
            "output": core_output,
            "validation": core_output_validation.to_dict(),
        },
        "service_flow": {
            "output": service_output,
            "validation": service_output_validation.to_dict(),
        },
    }


def _render_output(payload: dict[str, Any], *, output_format: str) -> None:
    """Render command result payload in selected output format."""

    if output_format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return

    command = payload.get("command", "unknown")
    print(f"[OK] {command}")
    if "result" in payload:
        result = payload["result"]
        print(f" - correlation_id: {result.get('correlation_id')}")
        print(f" - status: {result.get('status')}")
        print(f" - route_preview: {result.get('route_preview')}")
        return

    if command in {"s1:runbook-check", "s2:runbook-check", "s3:runbook-check"}:
        validation = payload.get("input_validation", {})
        core = payload.get("core_flow", {})
        service = payload.get("service_flow", {})
        core_output = core.get("output", {})
        print(f" - correlation_id: {validation.get('correlation_id')}")
        print(f" - input_status: {validation.get('status')}")
        print(f" - core_output_status: {core_output.get('status')}")
        print(f" - service_output_status: {service.get('output', {}).get('status')}")
        print(f" - route: {service.get('output', {}).get('rota_selecionada')}")
        print(f" - core_validation_status: {core.get('validation', {}).get('status')}")
        print(f" - service_validation_status: {service.get('validation', {}).get('status')}")
        return

    input_validation = payload.get("input_validation", {})
    flow_output = payload.get("flow_output", {})
    output_validation = payload.get("output_validation", {})
    print(f" - correlation_id: {input_validation.get('correlation_id')}")
    print(f" - input_status: {input_validation.get('status')}")
    print(f" - flow_status: {flow_output.get('status')}")
    print(f" - route: {flow_output.get('rota_selecionada')}")
    print(f" - output_layer: {output_validation.get('layer')}")
    print(f" - output_status: {output_validation.get('status')}")


def _render_error(error: ToolExecutionError, *, output_format: str) -> None:
    """Render actionable command failure in selected output format."""

    payload = error.to_dict()
    if output_format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return
    print(f"[ERROR] {payload['code']}: {payload['message']}")
    print(f" - action: {payload['action']}")
    print(f" - correlation_id: {payload['correlation_id']}")
    if payload["context"]:
        print(f" - context: {payload['context']}")


def _context_from_error(error: Exception) -> dict[str, Any]:
    """Return consistent error context for validation/core/service exceptions."""

    context: dict[str, Any] = {}
    if hasattr(error, "observability_event_id") and getattr(error, "observability_event_id"):
        context["observability_event_id"] = str(getattr(error, "observability_event_id"))
    if hasattr(error, "event_id") and getattr(error, "event_id"):
        context["event_id"] = str(getattr(error, "event_id"))
    if hasattr(error, "stage") and getattr(error, "stage"):
        context["stage"] = str(getattr(error, "stage"))
    return context


def main(argv: list[str] | None = None) -> int:
    """Run operational tool commands for ORQ Sprint 1, Sprint 2, and Sprint 3.

    Args:
        argv: Optional CLI argument list.

    Returns:
        Exit code: `0` on success, `1` on expected operational failures.

    Raises:
        SystemExit: Propagated by argparse for invalid CLI usage.
    """

    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper()),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        if args.command == "s1:validate-input":
            payload = _run_validate_input(args)
        elif args.command == "s1:simulate-core":
            payload = _run_simulate_core(args)
        elif args.command == "s1:simulate-service":
            payload = _run_simulate_service(args)
        elif args.command == "s1:runbook-check":
            payload = _run_runbook_check(args)
        elif args.command == "s2:validate-input":
            payload = _run_s2_validate_input(args)
        elif args.command == "s2:simulate-core":
            payload = _run_s2_simulate_core(args)
        elif args.command == "s2:simulate-service":
            payload = _run_s2_simulate_service(args)
        elif args.command == "s2:runbook-check":
            payload = _run_s2_runbook_check(args)
        elif args.command == "s3:validate-input":
            payload = _run_s3_validate_input(args)
        elif args.command == "s3:simulate-core":
            payload = _run_s3_simulate_core(args)
        elif args.command == "s3:simulate-service":
            payload = _run_s3_simulate_service(args)
        elif args.command == "s3:runbook-check":
            payload = _run_s3_runbook_check(args)
        else:
            raise ToolExecutionError(
                code="UNKNOWN_COMMAND",
                message=f"Comando nao suportado: {args.command}",
                action="Use --help para listar comandos disponiveis.",
                correlation_id=f"orq-tool-{uuid4().hex[:12]}",
            )
        _render_output(payload, output_format=str(args.output_format))
        return 0
    except (
        S1OrchestratorValidationError,
        S2OrchestratorValidationError,
        S3OrchestratorValidationError,
    ) as exc:
        _log_event(
            level=logging.WARNING,
            event_name="orq_tool_validation_failed",
            correlation_id=exc.correlation_id,
            context={"error_code": exc.code, "stage": exc.stage},
        )
        _render_error(
            ToolExecutionError(
                code=exc.code,
                message=exc.message,
                action=exc.action,
                correlation_id=exc.correlation_id,
                context=_context_from_error(exc),
            ),
            output_format=str(args.output_format),
        )
        return 1
    except (
        S1OrchestratorCoreError,
        S1OrchestratorServiceError,
        S2OrchestratorCoreError,
        S2OrchestratorServiceError,
        S3OrchestratorCoreError,
        S3OrchestratorServiceError,
    ) as exc:
        _log_event(
            level=logging.ERROR,
            event_name="orq_tool_flow_failed",
            correlation_id=exc.correlation_id,
            context={"error_code": exc.code, "stage": exc.stage},
        )
        _render_error(
            ToolExecutionError(
                code=exc.code,
                message=exc.message,
                action=exc.action,
                correlation_id=exc.correlation_id,
                context=_context_from_error(exc),
            ),
            output_format=str(args.output_format),
        )
        return 1
    except ToolExecutionError as exc:
        _render_error(exc, output_format=str(args.output_format))
        return 1
    except Exception as exc:  # noqa: BLE001
        correlation_id = f"orq-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="orq_tool_unexpected_error",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        _render_error(
            ToolExecutionError(
                code="ORQ_TOOL_UNEXPECTED_ERROR",
                message=f"Falha inesperada na ferramenta do orquestrador: {type(exc).__name__}",
                action="Reexecute com --log-level DEBUG e revise os logs operacionais.",
                correlation_id=correlation_id,
            ),
            output_format=str(args.output_format),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
