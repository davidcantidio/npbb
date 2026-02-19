"""Operational tools for CONT Sprint 1, Sprint 2, Sprint 3, and Sprint 4 flows.

This script provides small, verifiable runbook commands to:
1. validate CONT Sprint 1/Sprint 2/Sprint 3/Sprint 4 input contracts;
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

from app.services.contract_validation_service import (  # noqa: E402
    S1ContractValidationServiceError,
    S2ContractValidationServiceError,
    S3ContractValidationServiceError,
    S4ContractValidationServiceError,
    execute_s1_contract_validation_service,
    execute_s2_contract_validation_service,
    execute_s3_contract_validation_service,
    execute_s4_contract_validation_service,
)
from core.contracts.s1_core import (  # noqa: E402
    S1CanonicalContractCoreError,
    execute_s1_contract_validation_main_flow,
)
from core.contracts.s1_validation import (  # noqa: E402
    S1CanonicalContractValidationError,
    S1CanonicalContractValidationInput,
    validate_s1_contract_flow_output_contract,
    validate_s1_contract_input_contract,
)
from core.contracts.s2_core import (  # noqa: E402
    S2CanonicalContractCoreError,
    execute_s2_contract_validation_main_flow,
)
from core.contracts.s2_validation import (  # noqa: E402
    S2CanonicalContractValidationError,
    S2CanonicalContractValidationInput,
    validate_s2_contract_flow_output_contract,
    validate_s2_contract_input_contract,
)
from core.contracts.s3_core import (  # noqa: E402
    S3CanonicalContractCoreError,
    execute_s3_contract_validation_main_flow,
)
from core.contracts.s4_core import (  # noqa: E402
    S4CanonicalContractCoreError,
    execute_s4_contract_validation_main_flow,
)
from core.contracts.s3_validation import (  # noqa: E402
    S3CanonicalContractValidationError,
    S3CanonicalContractValidationInput,
    validate_s3_contract_flow_output_contract,
    validate_s3_contract_input_contract,
)
from core.contracts.s4_validation import (  # noqa: E402
    S4CanonicalContractValidationError,
    S4CanonicalContractValidationInput,
    validate_s4_contract_flow_output_contract,
    validate_s4_contract_input_contract,
)


logger = logging.getLogger("npbb.contract_tools")


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
    """Build CLI parser for CONT Sprint 1, Sprint 2, Sprint 3, and Sprint 4 commands."""

    parser = argparse.ArgumentParser(prog="contract_tools")
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
        help="Validate CONT Sprint 1 input contract.",
    )
    _add_s1_common_args(validate_parser, required=True)

    simulate_core_parser = sub.add_parser(
        "s1:simulate-core",
        help="Simulate CONT Sprint 1 core flow and validate output contract.",
    )
    _add_s1_common_args(simulate_core_parser, required=True)

    simulate_service_parser = sub.add_parser(
        "s1:simulate-service",
        help="Simulate CONT Sprint 1 service flow and validate output contract.",
    )
    _add_s1_common_args(simulate_service_parser, required=True)

    runbook_parser = sub.add_parser(
        "s1:runbook-check",
        help="Run one complete local CONT Sprint 1 runbook check.",
    )
    _add_s1_common_args(runbook_parser, required=False)
    runbook_parser.set_defaults(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v1",
        strict_validation="true",
        lineage_required="true",
        owner_team="etl",
        correlation_id=None,
    )

    s2_validate_parser = sub.add_parser(
        "s2:validate-input",
        help="Validate CONT Sprint 2 input contract.",
    )
    _add_s2_common_args(s2_validate_parser, required=True)

    s2_simulate_core_parser = sub.add_parser(
        "s2:simulate-core",
        help="Simulate CONT Sprint 2 core flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_core_parser, required=True)

    s2_simulate_service_parser = sub.add_parser(
        "s2:simulate-service",
        help="Simulate CONT Sprint 2 service flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_service_parser, required=True)

    s2_runbook_parser = sub.add_parser(
        "s2:runbook-check",
        help="Run one complete local CONT Sprint 2 runbook check.",
    )
    _add_s2_common_args(s2_runbook_parser, required=False)
    s2_runbook_parser.set_defaults(
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v2",
        strict_validation="true",
        lineage_required="true",
        owner_team="etl",
        schema_required_fields="record_id,event_ts,source_id,payload_checksum",
        domain_constraint=("record_id=not_null", "source_id=crm|app"),
        correlation_id=None,
    )

    s3_validate_parser = sub.add_parser(
        "s3:validate-input",
        help="Validate CONT Sprint 3 input contract.",
    )
    _add_s3_common_args(s3_validate_parser, required=True)

    s3_simulate_core_parser = sub.add_parser(
        "s3:simulate-core",
        help="Simulate CONT Sprint 3 core flow and validate output contract.",
    )
    _add_s3_common_args(s3_simulate_core_parser, required=True)

    s3_simulate_service_parser = sub.add_parser(
        "s3:simulate-service",
        help="Simulate CONT Sprint 3 service flow and validate output contract.",
    )
    _add_s3_common_args(s3_simulate_service_parser, required=True)

    s3_runbook_parser = sub.add_parser(
        "s3:runbook-check",
        help="Run one complete local CONT Sprint 3 runbook check.",
    )
    _add_s3_common_args(s3_runbook_parser, required=False)
    s3_runbook_parser.set_defaults(
        contract_id="CONT_STG_OPTIN_V3",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v3",
        strict_validation="true",
        lineage_required="true",
        owner_team="etl",
        schema_required_fields="record_id,event_ts,source_id,payload_checksum",
        lineage_field_requirement=("record_id=crm.orders.id", "source_id=crm.sources.origin_system"),
        metric_lineage_requirement=("optin_total=crm.optin.total",),
        correlation_id=None,
    )

    s4_validate_parser = sub.add_parser(
        "s4:validate-input",
        help="Validate CONT Sprint 4 input contract.",
    )
    _add_s4_common_args(s4_validate_parser, required=True)

    s4_simulate_core_parser = sub.add_parser(
        "s4:simulate-core",
        help="Simulate CONT Sprint 4 core flow and validate output contract.",
    )
    _add_s4_common_args(s4_simulate_core_parser, required=True)

    s4_simulate_service_parser = sub.add_parser(
        "s4:simulate-service",
        help="Simulate CONT Sprint 4 service flow and validate output contract.",
    )
    _add_s4_common_args(s4_simulate_service_parser, required=True)

    s4_runbook_parser = sub.add_parser(
        "s4:runbook-check",
        help="Run one complete local CONT Sprint 4 runbook check.",
    )
    _add_s4_common_args(s4_runbook_parser, required=False)
    s4_runbook_parser.set_defaults(
        contract_id="CONT_STG_OPTIN_V4",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v4",
        strict_validation="true",
        lineage_required="true",
        owner_team="etl",
        schema_required_fields="record_id,event_ts,source_id,payload_checksum",
        lineage_field_requirement=("record_id=crm.orders.id", "source_id=crm.sources.origin_system"),
        metric_lineage_requirement=("optin_total=crm.optin.total",),
        compatibility_mode="strict_backward",
        previous_contract_versions="v3",
        regression_gate_required="true",
        regression_suite_version="s4",
        max_regression_failures=0,
        breaking_change_policy="block",
        deprecation_window_days=0,
        correlation_id=None,
    )

    return parser


def _add_s1_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common CONT Sprint 1 input arguments in one parser."""

    parser.add_argument("--contract-id", required=required, help="Stable canonical contract id.")
    parser.add_argument("--dataset-name", required=required, help="Dataset name for contract ownership.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind (pdf, docx, pptx, xlsx, csv, api, manual, other).",
    )
    parser.add_argument(
        "--schema-version",
        default="v1",
        help="Schema version in vN format.",
    )
    parser.add_argument(
        "--strict-validation",
        default="true",
        choices=("true", "false"),
        help="Whether strict validation is enabled.",
    )
    parser.add_argument(
        "--lineage-required",
        default="true",
        choices=("true", "false"),
        help="Whether lineage_ref_id is mandatory.",
    )
    parser.add_argument(
        "--owner-team",
        default="etl",
        help="Owner team used by contract governance.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s2_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common CONT Sprint 2 input arguments in one parser."""

    _add_s1_common_args(parser, required=required)
    parser.add_argument(
        "--schema-required-fields",
        default="record_id,event_ts,source_id,payload_checksum",
        help="Comma-separated list of required schema fields.",
    )
    parser.add_argument(
        "--domain-constraint",
        action="append",
        default=[],
        help="Domain constraint rule in format field=value1|value2 (can be repeated).",
    )


def _add_s3_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common CONT Sprint 3 input arguments in one parser."""

    _add_s1_common_args(parser, required=required)
    parser.add_argument(
        "--schema-required-fields",
        default="record_id,event_ts,source_id,payload_checksum",
        help="Comma-separated list of required schema fields.",
    )
    parser.add_argument(
        "--lineage-field-requirement",
        action="append",
        default=[],
        help="Field lineage rule in format field=ref1|ref2 (can be repeated).",
    )
    parser.add_argument(
        "--metric-lineage-requirement",
        action="append",
        default=[],
        help="Metric lineage rule in format metric=ref1|ref2 (can be repeated).",
    )


def _add_s4_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common CONT Sprint 4 input arguments in one parser."""

    _add_s3_common_args(parser, required=required)
    parser.add_argument(
        "--compatibility-mode",
        default="strict_backward",
        choices=("strict_backward", "backward_with_deprecation", "forward_and_backward"),
        help="Compatibility policy mode for version transitions.",
    )
    parser.add_argument(
        "--previous-contract-versions",
        default="v3",
        help="Comma-separated previous schema versions (ex: v2,v3).",
    )
    parser.add_argument(
        "--regression-gate-required",
        default="true",
        choices=("true", "false"),
        help="Whether regression gate is mandatory before release.",
    )
    parser.add_argument(
        "--regression-suite-version",
        default="s4",
        help="Regression suite version identifier.",
    )
    parser.add_argument(
        "--max-regression-failures",
        type=int,
        default=0,
        help="Maximum number of tolerated regression failures.",
    )
    parser.add_argument(
        "--breaking-change-policy",
        default="block",
        choices=("block", "allow_with_waiver"),
        help="Policy applied when breaking changes are detected.",
    )
    parser.add_argument(
        "--deprecation-window-days",
        type=int,
        default=0,
        help="Deprecation window in days for backward_with_deprecation mode.",
    )


def _as_bool(value: str) -> bool:
    """Convert CLI boolean string to Python bool."""

    return str(value).strip().lower() == "true"


def _build_validation_input_from_args(args: argparse.Namespace) -> S1CanonicalContractValidationInput:
    """Build CONT Sprint 1 validation input from parsed CLI args."""

    return S1CanonicalContractValidationInput(
        contract_id=str(args.contract_id),
        dataset_name=str(args.dataset_name),
        source_kind=str(args.source_kind),
        schema_version=str(args.schema_version),
        strict_validation=_as_bool(str(args.strict_validation)),
        lineage_required=_as_bool(str(args.lineage_required)),
        owner_team=str(args.owner_team),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _parse_required_fields(raw: str) -> tuple[str, ...]:
    values = [item.strip() for item in str(raw).split(",") if item.strip()]
    if not values:
        return ("record_id", "event_ts", "source_id", "payload_checksum")
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return tuple(unique)


def _parse_domain_constraints(raw_constraints: list[str]) -> dict[str, tuple[str, ...]]:
    constraints: dict[str, tuple[str, ...]] = {}
    for rule in raw_constraints:
        text = str(rule).strip()
        if not text:
            continue
        if "=" not in text:
            raise ToolExecutionError(
                code="INVALID_DOMAIN_CONSTRAINT_FORMAT",
                message=f"Regra de dominio invalida: {text}",
                action="Use --domain-constraint no formato campo=valor1|valor2.",
                correlation_id=f"cont-tool-{uuid4().hex[:12]}",
            )
        field, values_raw = text.split("=", 1)
        field_name = field.strip()
        values = [item.strip() for item in values_raw.split("|") if item.strip()]
        if not field_name or not values:
            raise ToolExecutionError(
                code="INVALID_DOMAIN_CONSTRAINT_FORMAT",
                message=f"Regra de dominio invalida: {text}",
                action="Use --domain-constraint no formato campo=valor1|valor2.",
                correlation_id=f"cont-tool-{uuid4().hex[:12]}",
            )
        constraints[field_name] = tuple(values)
    return constraints


def _parse_lineage_constraints(
    raw_constraints: list[str],
    *,
    option_name: str,
    error_code: str,
) -> dict[str, tuple[str, ...]]:
    constraints: dict[str, tuple[str, ...]] = {}
    for rule in raw_constraints:
        text = str(rule).strip()
        if not text:
            continue
        if "=" not in text:
            raise ToolExecutionError(
                code=error_code,
                message=f"Regra de linhagem invalida: {text}",
                action=f"Use {option_name} no formato chave=valor1|valor2.",
                correlation_id=f"cont-tool-{uuid4().hex[:12]}",
            )
        key, values_raw = text.split("=", 1)
        name = key.strip()
        values = [item.strip() for item in values_raw.split("|") if item.strip()]
        if not name or not values:
            raise ToolExecutionError(
                code=error_code,
                message=f"Regra de linhagem invalida: {text}",
                action=f"Use {option_name} no formato chave=valor1|valor2.",
                correlation_id=f"cont-tool-{uuid4().hex[:12]}",
            )
        unique_values: list[str] = []
        for value in values:
            if value not in unique_values:
                unique_values.append(value)
        constraints[name] = tuple(unique_values)
    return constraints


def _parse_previous_contract_versions(raw: str) -> tuple[str, ...]:
    values = [item.strip().lower() for item in str(raw).split(",") if item.strip()]
    if not values:
        raise ToolExecutionError(
            code="INVALID_PREVIOUS_CONTRACT_VERSIONS_FORMAT",
            message="previous_contract_versions nao pode ser vazio",
            action="Use --previous-contract-versions com versoes no formato vN (ex: v3 ou v2,v3).",
            correlation_id=f"cont-tool-{uuid4().hex[:12]}",
        )
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return tuple(unique)


def _build_s2_validation_input_from_args(args: argparse.Namespace) -> S2CanonicalContractValidationInput:
    """Build CONT Sprint 2 validation input from parsed CLI args."""

    return S2CanonicalContractValidationInput(
        contract_id=str(args.contract_id),
        dataset_name=str(args.dataset_name),
        source_kind=str(args.source_kind),
        schema_version=str(args.schema_version),
        strict_validation=_as_bool(str(args.strict_validation)),
        lineage_required=_as_bool(str(args.lineage_required)),
        owner_team=str(args.owner_team),
        schema_required_fields=_parse_required_fields(str(args.schema_required_fields)),
        domain_constraints=_parse_domain_constraints(list(args.domain_constraint)),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s3_validation_input_from_args(args: argparse.Namespace) -> S3CanonicalContractValidationInput:
    """Build CONT Sprint 3 validation input from parsed CLI args."""

    return S3CanonicalContractValidationInput(
        contract_id=str(args.contract_id),
        dataset_name=str(args.dataset_name),
        source_kind=str(args.source_kind),
        schema_version=str(args.schema_version),
        strict_validation=_as_bool(str(args.strict_validation)),
        lineage_required=_as_bool(str(args.lineage_required)),
        owner_team=str(args.owner_team),
        schema_required_fields=_parse_required_fields(str(args.schema_required_fields)),
        lineage_field_requirements=_parse_lineage_constraints(
            list(args.lineage_field_requirement),
            option_name="--lineage-field-requirement",
            error_code="INVALID_LINEAGE_FIELD_REQUIREMENT_FORMAT",
        ),
        metric_lineage_requirements=_parse_lineage_constraints(
            list(args.metric_lineage_requirement),
            option_name="--metric-lineage-requirement",
            error_code="INVALID_METRIC_LINEAGE_REQUIREMENT_FORMAT",
        ),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s4_validation_input_from_args(args: argparse.Namespace) -> S4CanonicalContractValidationInput:
    """Build CONT Sprint 4 validation input from parsed CLI args."""

    return S4CanonicalContractValidationInput(
        contract_id=str(args.contract_id),
        dataset_name=str(args.dataset_name),
        source_kind=str(args.source_kind),
        schema_version=str(args.schema_version),
        strict_validation=_as_bool(str(args.strict_validation)),
        lineage_required=_as_bool(str(args.lineage_required)),
        owner_team=str(args.owner_team),
        schema_required_fields=_parse_required_fields(str(args.schema_required_fields)),
        lineage_field_requirements=_parse_lineage_constraints(
            list(args.lineage_field_requirement),
            option_name="--lineage-field-requirement",
            error_code="INVALID_LINEAGE_FIELD_REQUIREMENT_FORMAT",
        ),
        metric_lineage_requirements=_parse_lineage_constraints(
            list(args.metric_lineage_requirement),
            option_name="--metric-lineage-requirement",
            error_code="INVALID_METRIC_LINEAGE_REQUIREMENT_FORMAT",
        ),
        compatibility_mode=str(args.compatibility_mode),
        previous_contract_versions=_parse_previous_contract_versions(
            str(args.previous_contract_versions)
        ),
        regression_gate_required=_as_bool(str(args.regression_gate_required)),
        regression_suite_version=str(args.regression_suite_version),
        max_regression_failures=int(args.max_regression_failures),
        breaking_change_policy=str(args.breaking_change_policy),
        deprecation_window_days=int(args.deprecation_window_days),
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
        event_name="cont_s1_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
        },
    )
    result = validate_s1_contract_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="cont_s1_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s1:validate-input", "result": result.to_dict()}


def _run_s1_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-core` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s1_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
        },
    )

    core_output = execute_s1_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s1_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": core_output.get("contract_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
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
    validation = validate_s1_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s1_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
        },
    )

    service_output = execute_s1_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s1_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": service_output.get("contract_id"),
            "execution_status": service_output.get("execucao", {}).get("status"),
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
    validation = validate_s1_contract_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s1_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s1_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s1_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s1_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s1_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "contract_id": service_output.get("contract_id"),
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
        event_name="cont_s2_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
        },
    )
    result = validate_s2_contract_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="cont_s2_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s2:validate-input", "result": result.to_dict()}


def _run_s2_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:simulate-core` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    validation = validate_s2_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s2_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
        },
    )

    core_output = execute_s2_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s2_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": core_output.get("contract_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
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
    validation = validate_s2_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s2_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
        },
    )

    service_output = execute_s2_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s2_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": service_output.get("contract_id"),
            "execution_status": service_output.get("execucao", {}).get("status"),
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
    validation = validate_s2_contract_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s2_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s2_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s2_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s2_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s2_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "contract_id": service_output.get("contract_id"),
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
        event_name="cont_s3_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
        },
    )
    result = validate_s3_contract_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="cont_s3_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s3:validate-input", "result": result.to_dict()}


def _run_s3_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:simulate-core` command and return output payload."""

    payload = _build_s3_validation_input_from_args(args)
    validation = validate_s3_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s3_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
        },
    )

    core_output = execute_s3_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s3_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s3_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": core_output.get("contract_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
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
    validation = validate_s3_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s3_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
        },
    )

    service_output = execute_s3_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s3_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s3_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": service_output.get("contract_id"),
            "execution_status": service_output.get("execucao", {}).get("status"),
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
    validation = validate_s3_contract_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s3_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s3_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s3_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s3_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s3_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "contract_id": service_output.get("contract_id"),
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


def _run_s4_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:validate-input` command and return output payload."""

    payload = _build_s4_validation_input_from_args(args)
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "compatibility_mode": payload.compatibility_mode,
        },
    )
    result = validate_s4_contract_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s4:validate-input", "result": result.to_dict()}


def _run_s4_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:simulate-core` command and return output payload."""

    payload = _build_s4_validation_input_from_args(args)
    validation = validate_s4_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_simulate_core_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
            "compatibility_mode": payload.compatibility_mode,
            "regression_gate_required": payload.regression_gate_required,
        },
    )

    core_output = execute_s4_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s4_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": core_output.get("contract_id"),
            "execution_status": core_output.get("execucao", {}).get("status"),
            "compatibility_result": core_output.get("execucao", {}).get("compatibility_result"),
            "regression_gate_passed": core_output.get("execucao", {}).get("regression_gate_passed"),
        },
    )
    return {
        "command": "s4:simulate-core",
        "input_validation": validation.to_dict(),
        "flow_output": core_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s4_simulate_service(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:simulate-service` command and return output payload."""

    payload = _build_s4_validation_input_from_args(args)
    validation = validate_s4_contract_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_simulate_service_started",
        correlation_id=correlation_id,
        context={
            "contract_id": payload.contract_id,
            "dataset_name": payload.dataset_name,
            "source_kind": payload.source_kind,
            "strict_validation": payload.strict_validation,
            "lineage_required": payload.lineage_required,
            "compatibility_mode": payload.compatibility_mode,
            "regression_gate_required": payload.regression_gate_required,
        },
    )

    service_output = execute_s4_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s4_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "contract_id": service_output.get("contract_id"),
            "execution_status": service_output.get("execucao", {}).get("status"),
            "compatibility_result": service_output.get("execucao", {}).get("compatibility_result"),
            "regression_gate_passed": service_output.get("execucao", {}).get("regression_gate_passed"),
        },
    )
    return {
        "command": "s4:simulate-service",
        "input_validation": validation.to_dict(),
        "flow_output": service_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s4_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:runbook-check` command and return output payload."""

    payload = _build_s4_validation_input_from_args(args)
    validation = validate_s4_contract_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s4_contract_validation_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s4_contract_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s4_contract_validation_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s4_contract_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="cont_s4_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "contract_id": service_output.get("contract_id"),
        },
    )
    return {
        "command": "s4:runbook-check",
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

    if command in {"s1:runbook-check", "s2:runbook-check", "s3:runbook-check", "s4:runbook-check"}:
        validation = payload.get("input_validation", {})
        core = payload.get("core_flow", {})
        service = payload.get("service_flow", {})
        core_output = core.get("output", {})
        print(f" - correlation_id: {validation.get('correlation_id')}")
        print(f" - input_status: {validation.get('status')}")
        print(f" - core_output_status: {core_output.get('status')}")
        print(f" - service_output_status: {service.get('output', {}).get('status')}")
        print(f" - contract_id: {service.get('output', {}).get('contract_id')}")
        print(f" - core_validation_status: {core.get('validation', {}).get('status')}")
        print(f" - service_validation_status: {service.get('validation', {}).get('status')}")
        return

    input_validation = payload.get("input_validation", {})
    flow_output = payload.get("flow_output", {})
    output_validation = payload.get("output_validation", {})
    print(f" - correlation_id: {input_validation.get('correlation_id')}")
    print(f" - input_status: {input_validation.get('status')}")
    print(f" - flow_status: {flow_output.get('status')}")
    print(f" - contract_id: {flow_output.get('contract_id')}")
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
    """Run operational tool commands for CONT Sprint 1, Sprint 2, Sprint 3, and Sprint 4.

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
        elif args.command == "s3:validate-input":
            payload = _run_s3_validate_input(args)
        elif args.command == "s3:simulate-core":
            payload = _run_s3_simulate_core(args)
        elif args.command == "s3:simulate-service":
            payload = _run_s3_simulate_service(args)
        elif args.command == "s3:runbook-check":
            payload = _run_s3_runbook_check(args)
        elif args.command == "s4:validate-input":
            payload = _run_s4_validate_input(args)
        elif args.command == "s4:simulate-core":
            payload = _run_s4_simulate_core(args)
        elif args.command == "s4:simulate-service":
            payload = _run_s4_simulate_service(args)
        elif args.command == "s4:runbook-check":
            payload = _run_s4_runbook_check(args)
        else:
            raise ToolExecutionError(
                code="UNKNOWN_COMMAND",
                message=f"Comando nao suportado: {args.command}",
                action="Use --help para listar comandos disponiveis.",
                correlation_id=f"cont-tool-{uuid4().hex[:12]}",
            )
        _render_output(payload, output_format=str(args.output_format))
        return 0
    except (
        S1CanonicalContractValidationError,
        S2CanonicalContractValidationError,
        S3CanonicalContractValidationError,
        S4CanonicalContractValidationError,
    ) as exc:
        _log_event(
            level=logging.WARNING,
            event_name="cont_tool_validation_failed",
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
        S1CanonicalContractCoreError,
        S2CanonicalContractCoreError,
        S3CanonicalContractCoreError,
        S4CanonicalContractCoreError,
        S1ContractValidationServiceError,
        S2ContractValidationServiceError,
        S3ContractValidationServiceError,
        S4ContractValidationServiceError,
    ) as exc:
        _log_event(
            level=logging.ERROR,
            event_name="cont_tool_flow_failed",
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
        correlation_id = f"cont-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="cont_tool_unexpected_error",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        _render_error(
            ToolExecutionError(
                code="CONT_TOOL_UNEXPECTED_ERROR",
                message=f"Falha inesperada na ferramenta de contrato canonico: {type(exc).__name__}",
                action="Reexecute com --log-level DEBUG e revise os logs operacionais.",
                correlation_id=correlation_id,
            ),
            output_format=str(args.output_format),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
