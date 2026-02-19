"""Operational tools for CONF Sprint 1 and Sprint 2 confidence policy flows.

This script provides small, verifiable runbook commands to:
1. validate CONF Sprint 1/Sprint 2 input contracts;
2. simulate core and service flow execution;
3. execute end-to-end local runbook checks.
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

from app.services.confidence_policy_service import (  # noqa: E402
    S1ConfidencePolicyServiceError,
    S2ConfidencePolicyServiceError,
    execute_s1_confidence_policy_service,
    execute_s2_confidence_policy_service,
)
from core.confidence.s1_core import (  # noqa: E402
    S1ConfidenceCoreError,
    execute_s1_confidence_policy_main_flow,
)
from core.confidence.s1_validation import (  # noqa: E402
    S1ConfidenceValidationError,
    S1ConfidenceValidationInput,
    validate_s1_confidence_input_contract,
    validate_s1_confidence_output_contract,
)
from core.confidence.s2_core import (  # noqa: E402
    S2ConfidenceCoreError,
    execute_s2_confidence_policy_main_flow,
)
from core.confidence.s2_validation import (  # noqa: E402
    S2ConfidenceValidationError,
    S2ConfidenceValidationInput,
    validate_s2_confidence_input_contract,
    validate_s2_confidence_output_contract,
)


logger = logging.getLogger("npbb.confidence_tools")


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
    """Build CLI parser for CONF Sprint 1 and Sprint 2 commands."""

    parser = argparse.ArgumentParser(prog="confidence_tools")
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
        help="Validate CONF Sprint 1 input contract.",
    )
    _add_s1_common_args(validate_parser, required=True)

    simulate_core_parser = sub.add_parser(
        "s1:simulate-core",
        help="Simulate CONF Sprint 1 core flow and validate output contract.",
    )
    _add_s1_common_args(simulate_core_parser, required=True)

    simulate_service_parser = sub.add_parser(
        "s1:simulate-service",
        help="Simulate CONF Sprint 1 service flow and validate output contract.",
    )
    _add_s1_common_args(simulate_service_parser, required=True)

    runbook_parser = sub.add_parser(
        "s1:runbook-check",
        help="Run one complete local CONF Sprint 1 runbook check.",
    )
    _add_s1_common_args(runbook_parser, required=False)
    runbook_parser.set_defaults(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weight=("nome=0.2", "email=0.3", "telefone=0.2", "documento=0.3"),
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        missing_field_penalty=0.10,
        decision_mode="weighted_threshold",
        correlation_id=None,
    )

    s2_validate_parser = sub.add_parser(
        "s2:validate-input",
        help="Validate CONF Sprint 2 input contract.",
    )
    _add_s2_common_args(s2_validate_parser, required=True)

    s2_simulate_core_parser = sub.add_parser(
        "s2:simulate-core",
        help="Simulate CONF Sprint 2 core flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_core_parser, required=True)

    s2_simulate_service_parser = sub.add_parser(
        "s2:simulate-service",
        help="Simulate CONF Sprint 2 service flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_service_parser, required=True)

    s2_runbook_parser = sub.add_parser(
        "s2:runbook-check",
        help="Run one complete local CONF Sprint 2 runbook check.",
    )
    _add_s2_common_args(s2_runbook_parser, required=False)
    s2_runbook_parser.set_defaults(
        policy_id="CONF_LEAD_POLICY_V2",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v2",
        owner_team="etl",
        field_weight=("nome=0.2", "email=0.3", "telefone=0.2", "documento=0.3"),
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="auto_review_gap",
        gap_escalation_required="true",
        max_manual_review_queue=500,
        correlation_id=None,
    )

    return parser


def _add_s1_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common CONF Sprint 1 input arguments in one parser."""

    parser.add_argument("--policy-id", required=required, help="Stable confidence policy id.")
    parser.add_argument("--dataset-name", required=required, help="Dataset name for policy ownership.")
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
        help="Owner team used by confidence policy governance.",
    )
    parser.add_argument(
        "--field-weight",
        action="append",
        default=[],
        help="Field weight rule in format field=weight (can be repeated).",
    )
    parser.add_argument(
        "--default-weight",
        type=float,
        default=1.0,
        help="Default weight for fields not listed in field_weights.",
    )
    parser.add_argument(
        "--auto-approve-threshold",
        type=float,
        default=0.85,
        help="Confidence threshold for automatic approval.",
    )
    parser.add_argument(
        "--manual-review-threshold",
        type=float,
        default=0.60,
        help="Confidence threshold for manual review.",
    )
    parser.add_argument(
        "--missing-field-penalty",
        type=float,
        default=0.10,
        help="Penalty applied when required fields are missing.",
    )
    parser.add_argument(
        "--decision-mode",
        default="weighted_threshold",
        choices=("weighted_threshold", "threshold"),
        help="Decision policy mode.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s2_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common CONF Sprint 2 input arguments in one parser."""

    parser.add_argument("--policy-id", required=required, help="Stable confidence policy id.")
    parser.add_argument("--dataset-name", required=required, help="Dataset name for policy ownership.")
    parser.add_argument(
        "--entity-kind",
        default="lead",
        help="Entity kind (lead, evento, ingresso, generic).",
    )
    parser.add_argument(
        "--schema-version",
        default="v2",
        help="Schema version in vN format.",
    )
    parser.add_argument(
        "--owner-team",
        default="etl",
        help="Owner team used by confidence policy governance.",
    )
    parser.add_argument(
        "--field-weight",
        action="append",
        default=[],
        help="Field weight rule in format field=weight (can be repeated).",
    )
    parser.add_argument(
        "--default-weight",
        type=float,
        default=1.0,
        help="Default weight for fields not listed in field_weights.",
    )
    parser.add_argument(
        "--auto-approve-threshold",
        type=float,
        default=0.85,
        help="Confidence threshold for automatic approval.",
    )
    parser.add_argument(
        "--manual-review-threshold",
        type=float,
        default=0.60,
        help="Confidence threshold for manual review.",
    )
    parser.add_argument(
        "--gap-threshold",
        type=float,
        default=0.40,
        help="Confidence threshold for gap routing.",
    )
    parser.add_argument(
        "--missing-field-penalty",
        type=float,
        default=0.10,
        help="Penalty applied when required fields are missing.",
    )
    parser.add_argument(
        "--decision-mode",
        default="auto_review_gap",
        choices=("auto_review_gap", "weighted_auto_review_gap"),
        help="Decision policy mode.",
    )
    parser.add_argument(
        "--gap-escalation-required",
        default="true",
        choices=("true", "false"),
        help="Whether gap escalation is required when manual queue overflows.",
    )
    parser.add_argument(
        "--max-manual-review-queue",
        type=int,
        default=500,
        help="Maximum tolerated manual review queue before escalation to gap.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _as_bool(value: str) -> bool:
    """Convert CLI boolean string to Python bool."""

    return str(value).strip().lower() == "true"


def _parse_field_weights(raw_rules: list[str]) -> dict[str, float] | None:
    rules = [str(rule).strip() for rule in raw_rules if str(rule).strip()]
    if not rules:
        return None

    field_weights: dict[str, float] = {}
    for rule in rules:
        if "=" not in rule:
            raise ToolExecutionError(
                code="INVALID_FIELD_WEIGHT_FORMAT",
                message=f"Regra de peso invalida: {rule}",
                action="Use --field-weight no formato campo=0.25.",
                correlation_id=f"conf-tool-{uuid4().hex[:12]}",
            )
        field_name_raw, weight_raw = rule.split("=", 1)
        field_name = field_name_raw.strip()
        if not field_name:
            raise ToolExecutionError(
                code="INVALID_FIELD_WEIGHT_FORMAT",
                message=f"Regra de peso invalida: {rule}",
                action="Use --field-weight no formato campo=0.25.",
                correlation_id=f"conf-tool-{uuid4().hex[:12]}",
            )
        try:
            weight = float(weight_raw.strip())
        except ValueError as exc:
            raise ToolExecutionError(
                code="INVALID_FIELD_WEIGHT_VALUE",
                message=f"Peso numerico invalido para campo '{field_name}': {weight_raw}",
                action="Informe peso numerico entre 0.0 e 1.0.",
                correlation_id=f"conf-tool-{uuid4().hex[:12]}",
            ) from exc
        field_weights[field_name] = weight

    return field_weights


def _build_validation_input_from_args(args: argparse.Namespace) -> S1ConfidenceValidationInput:
    """Build CONF Sprint 1 validation input from parsed CLI args."""

    return S1ConfidenceValidationInput(
        policy_id=str(args.policy_id),
        dataset_name=str(args.dataset_name),
        entity_kind=str(args.entity_kind),
        schema_version=str(args.schema_version),
        owner_team=str(args.owner_team),
        field_weights=_parse_field_weights(list(args.field_weight)),
        default_weight=float(args.default_weight),
        auto_approve_threshold=float(args.auto_approve_threshold),
        manual_review_threshold=float(args.manual_review_threshold),
        missing_field_penalty=float(args.missing_field_penalty),
        decision_mode=str(args.decision_mode),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s2_validation_input_from_args(args: argparse.Namespace) -> S2ConfidenceValidationInput:
    """Build CONF Sprint 2 validation input from parsed CLI args."""

    return S2ConfidenceValidationInput(
        policy_id=str(args.policy_id),
        dataset_name=str(args.dataset_name),
        entity_kind=str(args.entity_kind),
        schema_version=str(args.schema_version),
        owner_team=str(args.owner_team),
        field_weights=_parse_field_weights(list(args.field_weight)),
        default_weight=float(args.default_weight),
        auto_approve_threshold=float(args.auto_approve_threshold),
        manual_review_threshold=float(args.manual_review_threshold),
        gap_threshold=float(args.gap_threshold),
        missing_field_penalty=float(args.missing_field_penalty),
        decision_mode=str(args.decision_mode),
        gap_escalation_required=_as_bool(str(args.gap_escalation_required)),
        max_manual_review_queue=int(args.max_manual_review_queue),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
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
        event_name="conf_s1_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "policy_id": payload.policy_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
        },
    )
    result = validate_s1_confidence_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="conf_s1_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s1:validate-input", "result": result.to_dict()}


def _run_s1_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-core` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_confidence_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="conf_s1_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "policy_id": payload.policy_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "decision_mode": payload.decision_mode,
        },
    )

    core_output = execute_s1_confidence_policy_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_confidence_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="conf_s1_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "policy_id": core_output.get("policy_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
            "decision": core_output.get("execucao", {}).get("decision"),
        },
    )
    return {
        "command": "s1:simulate-core",
        "input_validation": validation.to_dict(),
        "flow_output": core_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s1_simulate_service(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-service` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_confidence_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="conf_s1_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "policy_id": payload.policy_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "decision_mode": payload.decision_mode,
        },
    )

    service_output = execute_s1_confidence_policy_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_confidence_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="conf_s1_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "policy_id": service_output.get("policy_id"),
            "execution_status": service_output.get("execucao", {}).get("status"),
            "decision": service_output.get("execucao", {}).get("decision"),
        },
    )
    return {
        "command": "s1:simulate-service",
        "input_validation": validation.to_dict(),
        "flow_output": service_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s1_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:runbook-check` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_confidence_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s1_confidence_policy_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s1_confidence_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s1_confidence_policy_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s1_confidence_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="conf_s1_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "policy_id": service_output.get("policy_id"),
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
        event_name="conf_s2_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "policy_id": payload.policy_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
        },
    )
    result = validate_s2_confidence_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="conf_s2_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s2:validate-input", "result": result.to_dict()}


def _run_s2_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:simulate-core` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    validation = validate_s2_confidence_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="conf_s2_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "policy_id": payload.policy_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "decision_mode": payload.decision_mode,
            "gap_escalation_required": payload.gap_escalation_required,
            "max_manual_review_queue": payload.max_manual_review_queue,
        },
    )

    core_output = execute_s2_confidence_policy_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_confidence_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="conf_s2_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "policy_id": core_output.get("policy_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
            "decision": core_output.get("execucao", {}).get("decision"),
            "confidence_score": core_output.get("execucao", {}).get("confidence_score"),
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
    validation = validate_s2_confidence_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="conf_s2_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "policy_id": payload.policy_id,
            "dataset_name": payload.dataset_name,
            "entity_kind": payload.entity_kind,
            "decision_mode": payload.decision_mode,
            "gap_escalation_required": payload.gap_escalation_required,
            "max_manual_review_queue": payload.max_manual_review_queue,
        },
    )

    service_output = execute_s2_confidence_policy_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_confidence_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="conf_s2_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "policy_id": service_output.get("policy_id"),
            "execution_status": service_output.get("execucao", {}).get("status"),
            "decision": service_output.get("execucao", {}).get("decision"),
            "confidence_score": service_output.get("execucao", {}).get("confidence_score"),
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
    validation = validate_s2_confidence_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s2_confidence_policy_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s2_confidence_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s2_confidence_policy_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s2_confidence_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="conf_s2_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "policy_id": service_output.get("policy_id"),
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

    if command in {"s1:runbook-check", "s2:runbook-check"}:
        validation = payload.get("input_validation", {})
        core = payload.get("core_flow", {})
        service = payload.get("service_flow", {})
        service_output = service.get("output", {})
        print(f" - correlation_id: {validation.get('correlation_id')}")
        print(f" - input_status: {validation.get('status')}")
        print(f" - core_output_status: {core.get('output', {}).get('status')}")
        print(f" - service_output_status: {service_output.get('status')}")
        print(f" - policy_id: {service_output.get('policy_id')}")
        print(f" - core_validation_status: {core.get('validation', {}).get('status')}")
        print(f" - service_validation_status: {service.get('validation', {}).get('status')}")
        return

    input_validation = payload.get("input_validation", {})
    flow_output = payload.get("flow_output", {})
    output_validation = payload.get("output_validation", {})
    print(f" - correlation_id: {input_validation.get('correlation_id')}")
    print(f" - input_status: {input_validation.get('status')}")
    print(f" - flow_status: {flow_output.get('status')}")
    print(f" - policy_id: {flow_output.get('policy_id')}")
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
    """Run operational tool commands for CONF Sprint 1 and Sprint 2.

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
        elif args.command == "s1:simulate-service":
            payload = _run_s1_simulate_service(args)
        elif args.command == "s1:runbook-check":
            payload = _run_s1_runbook_check(args)
        elif args.command == "s2:validate-input":
            payload = _run_s2_validate_input(args)
        elif args.command == "s2:simulate-core":
            payload = _run_s2_simulate_core(args)
        elif args.command == "s2:simulate-service":
            payload = _run_s2_simulate_service(args)
        elif args.command == "s2:runbook-check":
            payload = _run_s2_runbook_check(args)
        else:
            raise ToolExecutionError(
                code="UNKNOWN_COMMAND",
                message=f"Comando nao suportado: {args.command}",
                action="Use --help para listar comandos disponiveis.",
                correlation_id=f"conf-tool-{uuid4().hex[:12]}",
            )
        _render_output(payload, output_format=str(args.output_format))
        return 0
    except (S1ConfidenceValidationError, S2ConfidenceValidationError) as exc:
        _log_event(
            level=logging.WARNING,
            event_name="conf_tool_validation_failed",
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
        S1ConfidenceCoreError,
        S2ConfidenceCoreError,
        S1ConfidencePolicyServiceError,
        S2ConfidencePolicyServiceError,
    ) as exc:
        _log_event(
            level=logging.ERROR,
            event_name="conf_tool_flow_failed",
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
        correlation_id = f"conf-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="conf_tool_unexpected_error",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        _render_error(
            ToolExecutionError(
                code="CONF_TOOL_UNEXPECTED_ERROR",
                message=f"Falha inesperada na ferramenta de confianca: {type(exc).__name__}",
                action="Reexecute com --log-level DEBUG e revise os logs operacionais.",
                correlation_id=correlation_id,
            ),
            output_format=str(args.output_format),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
