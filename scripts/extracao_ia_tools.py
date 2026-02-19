"""Operational tools for XIA Sprint 1, Sprint 2, Sprint 3, and Sprint 4 extraction flows.

This script offers small, verifiable commands for runbook operations:
1. Validate XIA Sprint 1/Sprint 2/Sprint 3 input contracts.
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

from app.services.etl_extract_ai_service import (  # noqa: E402
    S1AIExtractServiceError,
    S2AIExtractServiceError,
    S3AIExtractServiceError,
    S4AIExtractServiceError,
    execute_s1_extract_ai_service,
    execute_s2_extract_ai_service,
    execute_s3_extract_ai_service,
    execute_s4_extract_ai_service,
)
from etl.extract.ai.s1_core import (  # noqa: E402
    S1AIExtractCoreError,
    execute_s1_ai_extract_main_flow,
)
from etl.extract.ai.s1_validation import (  # noqa: E402
    S1AIExtractValidationError,
    S1AIExtractValidationInput,
    validate_s1_extract_ai_flow_output_contract,
    validate_s1_extract_ai_input_contract,
)
from etl.extract.ai.s2_core import (  # noqa: E402
    S2AIExtractCoreError,
    execute_s2_ai_extract_main_flow,
)
from etl.extract.ai.s2_validation import (  # noqa: E402
    S2AIExtractValidationError,
    S2AIExtractValidationInput,
    validate_s2_extract_ai_flow_output_contract,
    validate_s2_extract_ai_input_contract,
)
from etl.extract.ai.s3_core import (  # noqa: E402
    S3AIExtractCoreError,
    execute_s3_ai_extract_main_flow,
)
from etl.extract.ai.s3_validation import (  # noqa: E402
    S3AIExtractValidationError,
    S3AIExtractValidationInput,
    validate_s3_extract_ai_flow_output_contract,
    validate_s3_extract_ai_input_contract,
)
from etl.extract.ai.s4_core import (  # noqa: E402
    S4AIExtractCoreError,
    execute_s4_ai_extract_main_flow,
)
from etl.extract.ai.s4_validation import (  # noqa: E402
    S4AIExtractValidationError,
    S4AIExtractValidationInput,
    validate_s4_extract_ai_flow_output_contract,
    validate_s4_extract_ai_input_contract,
)


logger = logging.getLogger("npbb.extracao_ia.tools")


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
    """Build CLI parser for XIA Sprint 1, Sprint 2, Sprint 3, and Sprint 4 commands."""

    parser = argparse.ArgumentParser(prog="extracao_ia_tools")
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
        help="Validate XIA Sprint 1 input contract.",
    )
    _add_s1_common_args(validate_parser, required=True)

    simulate_core_parser = sub.add_parser(
        "s1:simulate-core",
        help="Simulate XIA Sprint 1 core flow and validate output contract.",
    )
    _add_s1_common_args(simulate_core_parser, required=True)

    simulate_service_parser = sub.add_parser(
        "s1:simulate-service",
        help="Simulate XIA Sprint 1 service flow and validate output contract.",
    )
    _add_s1_common_args(simulate_service_parser, required=True)

    runbook_parser = sub.add_parser(
        "s1:runbook-check",
        help="Run one complete local XIA Sprint 1 runbook check.",
    )
    _add_s1_common_args(runbook_parser, required=False)
    runbook_parser.set_defaults(
        source_id="SRC_TMJ_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        document_profile_hint="pdf_digital",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="section",
        max_tokens_output=2048,
        temperature=0.0,
        correlation_id=None,
    )

    s2_validate_parser = sub.add_parser(
        "s2:validate-input",
        help="Validate XIA Sprint 2 input contract.",
    )
    _add_s2_common_args(s2_validate_parser, required=True)

    s2_simulate_core_parser = sub.add_parser(
        "s2:simulate-core",
        help="Simulate XIA Sprint 2 core flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_core_parser, required=True)

    s2_simulate_service_parser = sub.add_parser(
        "s2:simulate-service",
        help="Simulate XIA Sprint 2 service flow and validate output contract.",
    )
    _add_s2_common_args(s2_simulate_service_parser, required=True)

    s2_runbook_parser = sub.add_parser(
        "s2:runbook-check",
        help="Run one complete local XIA Sprint 2 runbook check.",
    )
    _add_s2_common_args(s2_runbook_parser, required=False)
    s2_runbook_parser.set_defaults(
        source_id="SRC_TMJ_XLSX_2025",
        source_kind="xlsx",
        source_uri="file:///tmp/tmj_2025.xlsx",
        document_profile_hint="xlsx_non_standard",
        tabular_layout_hint="header_shifted",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="sheet",
        max_tokens_output=3072,
        temperature=0.0,
        correlation_id=None,
    )

    s3_validate_parser = sub.add_parser(
        "s3:validate-input",
        help="Validate XIA Sprint 3 input contract.",
    )
    _add_s3_common_args(s3_validate_parser, required=True)

    s3_simulate_core_parser = sub.add_parser(
        "s3:simulate-core",
        help="Simulate XIA Sprint 3 core flow and validate output contract.",
    )
    _add_s3_common_args(s3_simulate_core_parser, required=True)

    s3_simulate_service_parser = sub.add_parser(
        "s3:simulate-service",
        help="Simulate XIA Sprint 3 service flow and validate output contract.",
    )
    _add_s3_common_args(s3_simulate_service_parser, required=True)

    s3_runbook_parser = sub.add_parser(
        "s3:runbook-check",
        help="Run one complete local XIA Sprint 3 runbook check.",
    )
    _add_s3_common_args(s3_runbook_parser, required=False)
    s3_runbook_parser.set_defaults(
        source_id="SRC_TMJ_PDFSCAN_2025",
        source_kind="pdf_scan",
        source_uri="file:///tmp/tmj_2025_scan.pdf",
        document_profile_hint="pdf_scan_document",
        image_preprocess_hint="ocr_enhanced",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="page",
        max_tokens_output=4096,
        temperature=0.0,
        correlation_id=None,
    )

    s4_validate_parser = sub.add_parser(
        "s4:validate-input",
        help="Validate XIA Sprint 4 input contract.",
    )
    _add_s4_common_args(s4_validate_parser, required=True)

    s4_simulate_core_parser = sub.add_parser(
        "s4:simulate-core",
        help="Simulate XIA Sprint 4 core flow and validate output contract.",
    )
    _add_s4_common_args(s4_simulate_core_parser, required=True)

    s4_simulate_service_parser = sub.add_parser(
        "s4:simulate-service",
        help="Simulate XIA Sprint 4 service flow and validate output contract.",
    )
    _add_s4_common_args(s4_simulate_service_parser, required=True)

    s4_runbook_parser = sub.add_parser(
        "s4:runbook-check",
        help="Run one complete local XIA Sprint 4 runbook check.",
    )
    _add_s4_common_args(s4_runbook_parser, required=False)
    s4_runbook_parser.set_defaults(
        source_id="SRC_TMJ_S4_PDF_2025",
        source_kind="pdf",
        source_uri="file:///tmp/tmj_2025.pdf",
        quality_profile_hint="strict_textual",
        consolidation_scope="cross_format_event",
        output_normalization_profile="canonical_fields_v1",
        ia_model_provider="openai",
        ia_model_name="gpt-4.1-mini",
        chunk_strategy="page",
        max_tokens_output=4096,
        temperature=0.0,
        correlation_id=None,
    )
    return parser


def _add_s1_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common XIA Sprint 1 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by bounded AI extraction (pdf, docx).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--document-profile-hint",
        default=None,
        help="Optional document profile hint (pdf_digital, docx_textual, etc).",
    )
    parser.add_argument(
        "--ia-model-provider",
        default="openai",
        help="Model provider (openai, azure_openai, anthropic, local).",
    )
    parser.add_argument(
        "--ia-model-name",
        default="gpt-4.1-mini",
        help="Model name used by extraction flow.",
    )
    parser.add_argument(
        "--chunk-strategy",
        default="section",
        help="Chunking strategy (section, page, paragraph).",
    )
    parser.add_argument(
        "--max-tokens-output",
        type=int,
        default=2048,
        help="Maximum output tokens allowed in one extraction pass.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Model temperature between 0 and 1.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s2_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common XIA Sprint 2 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by Sprint 2 extraction (pptx, xlsx, csv).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--document-profile-hint",
        default=None,
        help=(
            "Optional document profile hint "
            "(pptx_social_metrics, pptx_slide_text, xlsx_non_standard, csv_non_standard)."
        ),
    )
    parser.add_argument(
        "--tabular-layout-hint",
        default=None,
        help="Optional table layout hint (header_in_row_1, header_shifted, multi_header, unknown).",
    )
    parser.add_argument(
        "--ia-model-provider",
        default="openai",
        help="Model provider (openai, azure_openai, anthropic, local).",
    )
    parser.add_argument(
        "--ia-model-name",
        default="gpt-4.1-mini",
        help="Model name used by extraction flow.",
    )
    parser.add_argument(
        "--chunk-strategy",
        default="sheet",
        help="Chunking strategy (slide, sheet, row_block).",
    )
    parser.add_argument(
        "--max-tokens-output",
        type=int,
        default=3072,
        help="Maximum output tokens allowed in one extraction pass.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Model temperature between 0 and 1.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s3_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common XIA Sprint 3 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by Sprint 3 extraction (pdf_scan, jpg, png).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--document-profile-hint",
        default=None,
        help=(
            "Optional document profile hint "
            "(pdf_scan_document, image_document, image_id_document)."
        ),
    )
    parser.add_argument(
        "--image-preprocess-hint",
        default=None,
        help="Optional preprocess hint (none, deskew, denoise, ocr_enhanced).",
    )
    parser.add_argument(
        "--ia-model-provider",
        default="openai",
        help="Model provider (openai, azure_openai, anthropic, local).",
    )
    parser.add_argument(
        "--ia-model-name",
        default="gpt-4.1-mini",
        help="Model name used by extraction flow.",
    )
    parser.add_argument(
        "--chunk-strategy",
        default="page",
        help="Chunking strategy (page, image, region).",
    )
    parser.add_argument(
        "--max-tokens-output",
        type=int,
        default=4096,
        help="Maximum output tokens allowed in one extraction pass.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Model temperature between 0 and 1.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s4_common_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    """Register common XIA Sprint 4 input arguments in one parser."""

    parser.add_argument("--source-id", required=required, help="Stable source identifier.")
    parser.add_argument(
        "--source-kind",
        required=required,
        help="Source kind used by Sprint 4 calibrated extraction (pdf, docx, pptx, xlsx, csv, pdf_scan, jpg, png).",
    )
    parser.add_argument(
        "--source-uri",
        required=required,
        help="Source URI or path used for operational traceability.",
    )
    parser.add_argument(
        "--quality-profile-hint",
        default="strict_textual",
        help="Quality calibration profile (strict_textual, table_sensitive, ocr_resilient, multimodal_document).",
    )
    parser.add_argument(
        "--consolidation-scope",
        default="single_source",
        help="Consolidation scope (single_source, batch_session, cross_format_event).",
    )
    parser.add_argument(
        "--output-normalization-profile",
        default="canonical_fields_v1",
        help="Output normalization profile (canonical_fields_v1, canonical_fields_v2).",
    )
    parser.add_argument(
        "--ia-model-provider",
        default="openai",
        help="Model provider (openai, azure_openai, anthropic, local).",
    )
    parser.add_argument(
        "--ia-model-name",
        default="gpt-4.1-mini",
        help="Model name used by extraction flow.",
    )
    parser.add_argument(
        "--chunk-strategy",
        default="section",
        help="Chunking strategy (section, page, paragraph, slide, sheet, row_block, image, region).",
    )
    parser.add_argument(
        "--max-tokens-output",
        type=int,
        default=4096,
        help="Maximum output tokens allowed in one extraction pass.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Model temperature between 0 and 1.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _build_validation_input_from_args(args: argparse.Namespace) -> S1AIExtractValidationInput:
    """Build XIA Sprint 1 validation input from parsed CLI args."""

    return S1AIExtractValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        document_profile_hint=(str(args.document_profile_hint).strip() if args.document_profile_hint else None),
        ia_model_provider=str(args.ia_model_provider),
        ia_model_name=str(args.ia_model_name),
        chunk_strategy=str(args.chunk_strategy),
        max_tokens_output=int(args.max_tokens_output),
        temperature=float(args.temperature),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s2_validation_input_from_args(args: argparse.Namespace) -> S2AIExtractValidationInput:
    """Build XIA Sprint 2 validation input from parsed CLI args."""

    return S2AIExtractValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        document_profile_hint=(str(args.document_profile_hint).strip() if args.document_profile_hint else None),
        tabular_layout_hint=(str(args.tabular_layout_hint).strip() if args.tabular_layout_hint else None),
        ia_model_provider=str(args.ia_model_provider),
        ia_model_name=str(args.ia_model_name),
        chunk_strategy=str(args.chunk_strategy),
        max_tokens_output=int(args.max_tokens_output),
        temperature=float(args.temperature),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s3_validation_input_from_args(args: argparse.Namespace) -> S3AIExtractValidationInput:
    """Build XIA Sprint 3 validation input from parsed CLI args."""

    return S3AIExtractValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        document_profile_hint=(str(args.document_profile_hint).strip() if args.document_profile_hint else None),
        image_preprocess_hint=(str(args.image_preprocess_hint).strip() if args.image_preprocess_hint else None),
        ia_model_provider=str(args.ia_model_provider),
        ia_model_name=str(args.ia_model_name),
        chunk_strategy=str(args.chunk_strategy),
        max_tokens_output=int(args.max_tokens_output),
        temperature=float(args.temperature),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _build_s4_validation_input_from_args(args: argparse.Namespace) -> S4AIExtractValidationInput:
    """Build XIA Sprint 4 validation input from parsed CLI args."""

    return S4AIExtractValidationInput(
        source_id=str(args.source_id),
        source_kind=str(args.source_kind),
        source_uri=str(args.source_uri),
        quality_profile_hint=str(args.quality_profile_hint),
        consolidation_scope=str(args.consolidation_scope),
        output_normalization_profile=str(args.output_normalization_profile),
        ia_model_provider=str(args.ia_model_provider),
        ia_model_name=str(args.ia_model_name),
        chunk_strategy=str(args.chunk_strategy),
        max_tokens_output=int(args.max_tokens_output),
        temperature=float(args.temperature),
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
        event_name="xia_s1_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={"source_kind": payload.source_kind},
    )
    result = validate_s1_extract_ai_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="xia_s1_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s1:validate-input", "result": result.to_dict()}


def _run_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-core` command and return output payload."""

    payload = _build_validation_input_from_args(args)
    validation = validate_s1_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s1_simulate_core_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind},
    )

    core_output = execute_s1_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s1_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": core_output.get("source_kind"),
            "chunk_count": core_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s1_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s1_simulate_service_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind},
    )

    service_output = execute_s1_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s1_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s1_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": service_output.get("source_kind"),
            "chunk_count": service_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s1_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s1_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s1_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s1_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s1_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s1_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "source_kind": service_output.get("source_kind"),
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
        event_name="xia_s2_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )
    result = validate_s2_extract_ai_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="xia_s2_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s2:validate-input", "result": result.to_dict()}


def _run_s2_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:simulate-core` command and return output payload."""

    payload = _build_s2_validation_input_from_args(args)
    validation = validate_s2_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s2_simulate_core_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )

    core_output = execute_s2_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s2_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": core_output.get("source_kind"),
            "chunk_count": core_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s2_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s2_simulate_service_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )

    service_output = execute_s2_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s2_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s2_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": service_output.get("source_kind"),
            "chunk_count": service_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s2_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s2_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s2_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s2_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s2_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s2_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "source_kind": service_output.get("source_kind"),
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
        event_name="xia_s3_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )
    result = validate_s3_extract_ai_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="xia_s3_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s3:validate-input", "result": result.to_dict()}


def _run_s3_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:simulate-core` command and return output payload."""

    payload = _build_s3_validation_input_from_args(args)
    validation = validate_s3_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s3_simulate_core_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )

    core_output = execute_s3_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s3_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s3_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": core_output.get("source_kind"),
            "chunk_count": core_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s3_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s3_simulate_service_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )

    service_output = execute_s3_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s3_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s3_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": service_output.get("source_kind"),
            "chunk_count": service_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s3_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s3_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s3_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s3_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s3_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s3_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "source_kind": service_output.get("source_kind"),
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
        event_name="xia_s4_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )
    result = validate_s4_extract_ai_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="xia_s4_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "route_preview": result.route_preview},
    )
    return {"command": "s4:validate-input", "result": result.to_dict()}


def _run_s4_simulate_core(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:simulate-core` command and return output payload."""

    payload = _build_s4_validation_input_from_args(args)
    validation = validate_s4_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s4_simulate_core_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )

    core_output = execute_s4_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s4_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s4_simulate_core_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": core_output.get("source_kind"),
            "chunk_count": core_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s4_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id
    _log_event(
        level=logging.INFO,
        event_name="xia_s4_simulate_service_started",
        correlation_id=correlation_id,
        context={"source_kind": payload.source_kind, "chunk_strategy": payload.chunk_strategy},
    )

    service_output = execute_s4_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    output_validation = validate_s4_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s4_simulate_service_completed",
        correlation_id=correlation_id,
        context={
            "status": output_validation.status,
            "source_kind": service_output.get("source_kind"),
            "chunk_count": service_output.get("execucao", {}).get("chunk_count"),
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
    validation = validate_s4_extract_ai_input_contract(payload)
    correlation_id = validation.correlation_id

    core_output = execute_s4_ai_extract_main_flow(
        payload.to_core_input(correlation_id=correlation_id)
    ).to_dict()
    core_output_validation = validate_s4_extract_ai_flow_output_contract(
        core_output,
        correlation_id=correlation_id,
    )

    service_output = execute_s4_extract_ai_service(
        payload.to_scaffold_request(correlation_id=correlation_id)
    ).to_dict()
    service_output_validation = validate_s4_extract_ai_flow_output_contract(
        service_output,
        correlation_id=correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="xia_s4_runbook_check_completed",
        correlation_id=correlation_id,
        context={
            "core_status": core_output_validation.status,
            "service_status": service_output_validation.status,
            "source_kind": service_output.get("source_kind"),
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
        print(f" - source_kind: {service.get('output', {}).get('source_kind')}")
        print(f" - core_validation_status: {core.get('validation', {}).get('status')}")
        print(f" - service_validation_status: {service.get('validation', {}).get('status')}")
        return

    input_validation = payload.get("input_validation", {})
    flow_output = payload.get("flow_output", {})
    output_validation = payload.get("output_validation", {})
    print(f" - correlation_id: {input_validation.get('correlation_id')}")
    print(f" - input_status: {input_validation.get('status')}")
    print(f" - flow_status: {flow_output.get('status')}")
    print(f" - source_kind: {flow_output.get('source_kind')}")
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
    """Run operational tool commands for XIA Sprint 1, Sprint 2, Sprint 3, and Sprint 4.

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
                correlation_id=f"xia-tool-{uuid4().hex[:12]}",
            )
        _render_output(payload, output_format=str(args.output_format))
        return 0
    except (
        S1AIExtractValidationError,
        S2AIExtractValidationError,
        S3AIExtractValidationError,
        S4AIExtractValidationError,
    ) as exc:
        _log_event(
            level=logging.WARNING,
            event_name="xia_tool_validation_failed",
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
        S1AIExtractCoreError,
        S1AIExtractServiceError,
        S2AIExtractCoreError,
        S2AIExtractServiceError,
        S3AIExtractCoreError,
        S3AIExtractServiceError,
        S4AIExtractCoreError,
        S4AIExtractServiceError,
    ) as exc:
        _log_event(
            level=logging.ERROR,
            event_name="xia_tool_flow_failed",
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
        correlation_id = f"xia-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="xia_tool_unexpected_error",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        _render_error(
            ToolExecutionError(
                code="XIA_TOOL_UNEXPECTED_ERROR",
                message=f"Falha inesperada na ferramenta de extracao IA: {type(exc).__name__}",
                action="Reexecute com --log-level DEBUG e revise os logs operacionais.",
                correlation_id=correlation_id,
            ),
            output_format=str(args.output_format),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
