"""Operational tools for WORK Sprint 1 human-review workbench flow.

This script provides small, verifiable runbook commands to:
1. validate WORK Sprint 1 input contracts;
2. simulate core execution and API integration;
3. execute one end-to-end local runbook check.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.routers.revisao_humana import (  # noqa: E402
    RevisaoHumanaS1ExecuteBody,
    RevisaoHumanaS1PrepareBody,
    execute_workbench_revisao_s1,
    prepare_workbench_revisao_s1,
)
from frontend.src.features.revisao_humana.s1_core import (  # noqa: E402
    S1WorkbenchCoreError,
    execute_workbench_revisao_s1_main_flow,
)
from frontend.src.features.revisao_humana.s1_validation import (  # noqa: E402
    S1WorkbenchValidationError,
    S1WorkbenchValidationInput,
    validate_workbench_revisao_s1_input_contract,
    validate_workbench_revisao_s1_output_contract,
)


logger = logging.getLogger("npbb.revisao_humana.tools")


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
    """Build CLI parser for WORK Sprint 1 commands."""

    parser = argparse.ArgumentParser(prog="revisao_humana_tools")
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
        help="Validate WORK Sprint 1 input contract.",
    )
    _add_s1_common_args(validate_parser, required=True)

    simulate_core_parser = sub.add_parser(
        "s1:simulate-core",
        help="Simulate WORK Sprint 1 core flow and validate output contract.",
    )
    _add_s1_common_args(simulate_core_parser, required=True)

    simulate_api_parser = sub.add_parser(
        "s1:simulate-api",
        help="Simulate WORK Sprint 1 API prepare/execute integration and validate output.",
    )
    _add_s1_common_args(simulate_api_parser, required=True)

    runbook_parser = sub.add_parser(
        "s1:runbook-check",
        help="Run one complete local WORK Sprint 1 runbook check.",
    )
    _add_s1_common_args(runbook_parser, required=False)
    runbook_parser.set_defaults(
        workflow_id="WORK_REVIEW_LEAD_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        required_field=("nome", "email", "telefone"),
        evidence_source=("crm", "formulario"),
        default_priority="media",
        sla_hours=24,
        max_queue_size=1000,
        auto_assignment_enabled="true",
        reviewer_role=("operador", "supervisor"),
        correlation_id=None,
    )
    return parser


def _add_s1_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common WORK Sprint 1 input arguments in one parser."""

    parser.add_argument("--workflow-id", required=required, help="Stable workbench workflow id.")
    parser.add_argument("--dataset-name", required=required, help="Dataset name for queue ownership.")
    parser.add_argument(
        "--entity-kind",
        default="lead",
        help="Entity kind (lead, evento, ingresso, generic).",
    )
    parser.add_argument(
        "--schema-version",
        default="v1",
        help="Schema version in vN format.",
    )
    parser.add_argument(
        "--owner-team",
        default="etl",
        help="Owner team used by queue governance.",
    )
    parser.add_argument(
        "--required-field",
        action="append",
        default=[],
        help="Required field name (can be repeated).",
    )
    parser.add_argument(
        "--evidence-source",
        action="append",
        default=[],
        help="Evidence source name (can be repeated).",
    )
    parser.add_argument(
        "--default-priority",
        default="media",
        choices=("baixa", "media", "alta", "critica"),
        help="Default queue priority.",
    )
    parser.add_argument(
        "--sla-hours",
        type=int,
        default=24,
        help="SLA window in hours.",
    )
    parser.add_argument(
        "--max-queue-size",
        type=int,
        default=1000,
        help="Maximum queue size for one build pass.",
    )
    parser.add_argument(
        "--auto-assignment-enabled",
        default="true",
        choices=("true", "false"),
        help="Whether auto assignment is enabled.",
    )
    parser.add_argument(
        "--reviewer-role",
        action="append",
        default=[],
        help="Reviewer role (can be repeated).",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _as_bool(value: str) -> bool:
    """Convert CLI boolean string to Python bool."""

    return str(value).strip().lower() == "true"


def _parse_optional_tuple(raw_values: list[str]) -> tuple[str, ...] | None:
    values = [str(value).strip() for value in raw_values if str(value).strip()]
    if not values:
        return None
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return tuple(unique)


def _build_validation_input_from_args(args: argparse.Namespace) -> S1WorkbenchValidationInput:
    """Build WORK Sprint 1 validation input from parsed CLI args."""

    return S1WorkbenchValidationInput(
        workflow_id=str(args.workflow_id),
        dataset_name=str(args.dataset_name),
        entity_kind=str(args.entity_kind),
        schema_version=str(args.schema_version),
        owner_team=str(args.owner_team),
        required_fields=_parse_optional_tuple(list(args.required_field)),
        evidence_sources=_parse_optional_tuple(list(args.evidence_source)),
        default_priority=str(args.default_priority),
        sla_hours=int(args.sla_hours),
        max_queue_size=int(args.max_queue_size),
        auto_assignment_enabled=_as_bool(str(args.auto_assignment_enabled)),
        reviewer_roles=_parse_optional_tuple(list(args.reviewer_role)),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_prepare_body(
    *,
    payload: S1WorkbenchValidationInput,
    correlation_id: str,
) -> RevisaoHumanaS1PrepareBody:
    return RevisaoHumanaS1PrepareBody(
        workflow_id=payload.workflow_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        owner_team=payload.owner_team,
        required_fields=list(payload.required_fields) if payload.required_fields is not None else None,
        evidence_sources=list(payload.evidence_sources) if payload.evidence_sources is not None else None,
        default_priority=payload.default_priority,
        sla_hours=payload.sla_hours,
        max_queue_size=payload.max_queue_size,
        auto_assignment_enabled=payload.auto_assignment_enabled,
        reviewer_roles=list(payload.reviewer_roles) if payload.reviewer_roles is not None else None,
        correlation_id=correlation_id,
    )


def _build_execute_body(
    *,
    payload: S1WorkbenchValidationInput,
    correlation_id: str,
) -> RevisaoHumanaS1ExecuteBody:
    return RevisaoHumanaS1ExecuteBody(
        workflow_id=payload.workflow_id,
        dataset_name=payload.dataset_name,
        entity_kind=payload.entity_kind,
        schema_version=payload.schema_version,
        owner_team=payload.owner_team,
        required_fields=list(payload.required_fields) if payload.required_fields is not None else None,
        evidence_sources=list(payload.evidence_sources) if payload.evidence_sources is not None else None,
        default_priority=payload.default_priority,
        sla_hours=payload.sla_hours,
        max_queue_size=payload.max_queue_size,
        auto_assignment_enabled=payload.auto_assignment_enabled,
        reviewer_roles=list(payload.reviewer_roles) if payload.reviewer_roles is not None else None,
        correlation_id=correlation_id,
    )


def _log_event(
    *,
    level: int,
    event_name: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Emit one tool operational event."""

    logger.log(
        level,
        event_name,
        extra={
            "correlation_id": correlation_id,
            "context": context or {},
        },
    )


def _run_s1_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:validate-input` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    _log_event(
        level=logging.INFO,
        event_name="work_s1_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
        },
    )
    result = validate_workbench_revisao_s1_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="work_s1_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s1:validate-input", "result": result.to_dict()}


def _run_s1_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-core` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_workbench_revisao_s1_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="work_s1_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "default_priority": payload.default_priority,
            "max_queue_size": payload.max_queue_size,
        },
    )

    core_output = execute_workbench_revisao_s1_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_workbench_revisao_s1_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="work_s1_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "workflow_id": core_output.get("workflow_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
            "generated_items": core_output.get("execucao", {}).get("generated_items"),
        },
    )
    return {
        "command": "s1:simulate-core",
        "input_validation": validation.to_dict(),
        "flow_output": core_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s1_simulate_api(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-api` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_workbench_revisao_s1_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="work_s1_simulate_api_started",
        correlation_id=correlation_id,
        context={
            "workflow_id": payload.workflow_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "default_priority": payload.default_priority,
            "max_queue_size": payload.max_queue_size,
        },
    )

    prepare_output = prepare_workbench_revisao_s1(
        _build_prepare_body(payload=payload, correlation_id=correlation_id)
    )
    if str(prepare_output.get("status", "")).strip().lower() != "ready":
        raise ToolExecutionError(
            code="INVALID_PREPARE_STATUS",
            message=f"Status inesperado no prepare WORK S1: {prepare_output.get('status')}",
            action="Revisar rota /internal/revisao-humana/s1/prepare e contrato de scaffold.",
            correlation_id=correlation_id,
            context={"prepare_status": str(prepare_output.get("status", ""))},
        )

    api_output = execute_workbench_revisao_s1(
        _build_execute_body(payload=payload, correlation_id=correlation_id)
    )
    output_validation = validate_workbench_revisao_s1_output_contract(
        api_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="work_s1_simulate_api_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "workflow_id": api_output.get("workflow_id"),
            "prepare_status": prepare_output.get("status"),
            "execution_status": api_output.get("execucao", {}).get("status"),
            "generated_items": api_output.get("execucao", {}).get("generated_items"),
        },
    )
    return {
        "command": "s1:simulate-api",
        "input_validation": validation.to_dict(),
        "prepare_output": prepare_output,
        "flow_output": api_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s1_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:runbook-check` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_workbench_revisao_s1_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_workbench_revisao_s1_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_workbench_revisao_s1_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    prepare_output = prepare_workbench_revisao_s1(
        _build_prepare_body(payload=payload, correlation_id=correlation_id)
    )
    if str(prepare_output.get("status", "")).strip().lower() != "ready":
        raise ToolExecutionError(
            code="INVALID_PREPARE_STATUS",
            message=f"Status inesperado no prepare WORK S1: {prepare_output.get('status')}",
            action="Revisar rota /internal/revisao-humana/s1/prepare e contrato de scaffold.",
            correlation_id=correlation_id,
            context={"prepare_status": str(prepare_output.get("status", ""))},
        )

    api_output = execute_workbench_revisao_s1(
        _build_execute_body(payload=payload, correlation_id=correlation_id)
    )
    api_output_validation = validate_workbench_revisao_s1_output_contract(
        api_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="work_s1_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "api_status": api_output_validation.status,
            "workflow_id": api_output.get("workflow_id"),
            "prepare_status": prepare_output.get("status"),
        },
    )
    return {
        "command": "s1:runbook-check",
        "input_validation": validation.to_dict(),
        "core_flow": {
            "output": core_output,
            "validation": core_output_validation.to_dict(),
        },
        "api_prepare": prepare_output,
        "api_flow": {
            "output": api_output,
            "validation": api_output_validation.to_dict(),
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

    if command == "s1:runbook-check":
        validation = payload.get("input_validation", {})
        core = payload.get("core_flow", {})
        api_prepare = payload.get("api_prepare", {})
        api_flow = payload.get("api_flow", {})
        api_output = api_flow.get("output", {})
        print(f" - correlation_id: {validation.get('correlation_id')}")
        print(f" - input_status: {validation.get('status')}")
        print(f" - core_output_status: {core.get('output', {}).get('status')}")
        print(f" - api_prepare_status: {api_prepare.get('status')}")
        print(f" - api_output_status: {api_output.get('status')}")
        print(f" - workflow_id: {api_output.get('workflow_id')}")
        print(f" - core_validation_status: {core.get('validation', {}).get('status')}")
        print(f" - api_validation_status: {api_flow.get('validation', {}).get('status')}")
        return

    if command == "s1:simulate-api":
        input_validation = payload.get("input_validation", {})
        prepare_output = payload.get("prepare_output", {})
        flow_output = payload.get("flow_output", {})
        output_validation = payload.get("output_validation", {})
        print(f" - correlation_id: {input_validation.get('correlation_id')}")
        print(f" - input_status: {input_validation.get('status')}")
        print(f" - prepare_status: {prepare_output.get('status')}")
        print(f" - flow_status: {flow_output.get('status')}")
        print(f" - workflow_id: {flow_output.get('workflow_id')}")
        print(f" - output_layer: {output_validation.get('layer')}")
        print(f" - output_status: {output_validation.get('status')}")
        return

    input_validation = payload.get("input_validation", {})
    flow_output = payload.get("flow_output", {})
    output_validation = payload.get("output_validation", {})
    print(f" - correlation_id: {input_validation.get('correlation_id')}")
    print(f" - input_status: {input_validation.get('status')}")
    print(f" - flow_status: {flow_output.get('status')}")
    print(f" - workflow_id: {flow_output.get('workflow_id')}")
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
    """Return consistent error context for validation/core/API exceptions."""

    context: dict[str, Any] = {}
    if hasattr(error, "observability_event_id") and getattr(error, "observability_event_id"):
        context["observability_event_id"] = str(getattr(error, "observability_event_id"))
    if hasattr(error, "event_id") and getattr(error, "event_id"):
        context["event_id"] = str(getattr(error, "event_id"))
    if hasattr(error, "stage") and getattr(error, "stage"):
        context["stage"] = str(getattr(error, "stage"))
    return context


def _extract_http_exception_payload(exc: HTTPException) -> dict[str, Any]:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = str(detail.get("code", "WORK_S1_HTTP_ERROR"))
    message = str(detail.get("message", str(exc.detail)))
    action = str(
        detail.get(
            "action",
            "Revisar payload e logs dos endpoints internos de revisao humana.",
        )
    )
    correlation_id = str(detail.get("correlation_id") or f"work-tool-{uuid4().hex[:12]}")
    context: dict[str, Any] = {"status_code": int(exc.status_code)}
    if "stage" in detail:
        context["stage"] = str(detail["stage"])
    if "event_id" in detail and detail["event_id"] is not None:
        context["event_id"] = str(detail["event_id"])
    if "field" in detail and detail["field"] is not None:
        context["field"] = str(detail["field"])
    return {
        "code": code,
        "message": message,
        "action": action,
        "correlation_id": correlation_id,
        "context": context,
    }


def main(argv: list[str] | None = None) -> int:
    """Run operational tool commands for WORK Sprint 1.

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
            payload = _run_s1_validate_input(args)
        elif args.command == "s1:simulate-core":
            payload = _run_s1_simulate_core(args)
        elif args.command == "s1:simulate-api":
            payload = _run_s1_simulate_api(args)
        elif args.command == "s1:runbook-check":
            payload = _run_s1_runbook_check(args)
        else:
            raise ToolExecutionError(
                code="UNKNOWN_COMMAND",
                message=f"Comando nao suportado: {args.command}",
                action="Use --help para listar comandos disponiveis.",
                correlation_id=f"work-tool-{uuid4().hex[:12]}",
            )
        _render_output(payload, output_format=str(args.output_format))
        return 0
    except S1WorkbenchValidationError as exc:
        _log_event(
            level=logging.WARNING,
            event_name="work_tool_validation_failed",
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
    except S1WorkbenchCoreError as exc:
        _log_event(
            level=logging.ERROR,
            event_name="work_tool_core_failed",
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
    except HTTPException as exc:
        payload = _extract_http_exception_payload(exc)
        _log_event(
            level=logging.ERROR,
            event_name="work_tool_api_failed",
            correlation_id=str(payload["correlation_id"]),
            context={
                "error_code": str(payload["code"]),
                "status_code": payload["context"].get("status_code"),
                "stage": payload["context"].get("stage"),
            },
        )
        _render_error(
            ToolExecutionError(
                code=str(payload["code"]),
                message=str(payload["message"]),
                action=str(payload["action"]),
                correlation_id=str(payload["correlation_id"]),
                context=dict(payload["context"]),
            ),
            output_format=str(args.output_format),
        )
        return 1
    except ValidationError as exc:
        correlation_id = f"work-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="work_tool_payload_validation_failed",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        _render_error(
            ToolExecutionError(
                code="WORK_S1_TOOL_PAYLOAD_VALIDATION_ERROR",
                message="Falha de validacao de payload na ferramenta operacional WORK S1.",
                action="Revisar argumentos CLI e campos obrigatorios da rota simulada.",
                correlation_id=correlation_id,
                context={"errors": exc.errors()},
            ),
            output_format=str(args.output_format),
        )
        return 1
    except ToolExecutionError as exc:
        _render_error(exc, output_format=str(args.output_format))
        return 1
    except Exception as exc:  # noqa: BLE001
        correlation_id = f"work-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="work_tool_unexpected_error",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        _render_error(
            ToolExecutionError(
                code="WORK_S1_TOOL_UNEXPECTED_ERROR",
                message=f"Falha inesperada na ferramenta WORK S1: {type(exc).__name__}",
                action="Reexecute com --log-level DEBUG e revise os logs operacionais.",
                correlation_id=correlation_id,
            ),
            output_format=str(args.output_format),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

