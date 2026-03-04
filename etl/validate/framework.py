"""Compatibility re-export for the shared lead ETL validation framework."""

from core.leads_etl.validate.framework import (
    Check,
    CheckContext,
    CheckReport,
    CheckResult,
    CheckRunner,
    CheckStatus,
    Severity,
    parse_fail_on,
    persist_check_results,
    render_report_json,
    render_report_markdown,
)

__all__ = [
    "Severity",
    "CheckStatus",
    "CheckResult",
    "CheckContext",
    "Check",
    "CheckRunner",
    "CheckReport",
    "parse_fail_on",
    "persist_check_results",
    "render_report_json",
    "render_report_markdown",
]
