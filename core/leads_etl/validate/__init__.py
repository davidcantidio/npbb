"""Shared validation helpers for lead ETL flows."""

from .checks_access_control import AccessControlReconciliationCheck, AccessControlRuleFinding
from .checks_cross_source import (
    CrossSourceDatasetSpec,
    CrossSourceInconsistencyCheck,
    persist_cross_source_inconsistencies,
)
from .checks_duplicates import DuplicateCheck, DuplicateCheckSpec, build_duplicate_checks
from .checks_not_null import NotNullCheck, build_not_null_checks
from .checks_percentages import (
    PercentBoundsCheck,
    PercentSumCheck,
    PercentSumRuleConfig,
    PercentageCheckConfig,
    PercentageCheckConfigError,
    build_percentage_checks,
    load_percentage_check_configs,
)
from .checks_schema import (
    DatasetCheckConfig,
    DatasetCheckConfigError,
    SchemaCheck,
    build_schema_checks,
    load_dataset_check_configs,
)
from .framework import (
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
from .render_dq_report import render_dq_report, render_dq_report_json

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
    "DatasetCheckConfig",
    "DatasetCheckConfigError",
    "SchemaCheck",
    "NotNullCheck",
    "DuplicateCheck",
    "DuplicateCheckSpec",
    "AccessControlReconciliationCheck",
    "AccessControlRuleFinding",
    "PercentBoundsCheck",
    "PercentSumCheck",
    "PercentSumRuleConfig",
    "PercentageCheckConfig",
    "PercentageCheckConfigError",
    "CrossSourceDatasetSpec",
    "CrossSourceInconsistencyCheck",
    "persist_cross_source_inconsistencies",
    "load_dataset_check_configs",
    "load_percentage_check_configs",
    "build_schema_checks",
    "build_not_null_checks",
    "build_duplicate_checks",
    "build_percentage_checks",
    "render_dq_report",
    "render_dq_report_json",
]
