"""Compatibility checks between legacy ETL imports and the shared lead core."""

from __future__ import annotations

from datetime import datetime, timezone

from core.leads_etl.transform.column_normalize import (
    ColumnNormalizationConfig as CoreColumnNormalizationConfig,
    normalize_column_names as core_normalize_column_names,
)
from core.leads_etl.transform.segment_mapper import (
    Segment as CoreSegment,
    load_segment_mapping as core_load_segment_mapping,
    map_ticket_category_with_finding as core_map_ticket_category_with_finding,
)
from core.leads_etl.validate.checks_access_control import (
    AccessControlReconciliationCheck as CoreAccessControlReconciliationCheck,
)
from core.leads_etl.validate.checks_cross_source import (
    CrossSourceInconsistencyCheck as CoreCrossSourceInconsistencyCheck,
)
from core.leads_etl.validate.checks_duplicates import DuplicateCheck as CoreDuplicateCheck
from core.leads_etl.validate.checks_not_null import NotNullCheck as CoreNotNullCheck
from core.leads_etl.validate.checks_percentages import (
    PercentBoundsCheck as CorePercentBoundsCheck,
    PercentSumCheck as CorePercentSumCheck,
    load_percentage_check_configs as core_load_percentage_check_configs,
)
from core.leads_etl.validate.checks_schema import (
    DatasetCheckConfig as CoreDatasetCheckConfig,
    SchemaCheck as CoreSchemaCheck,
    load_dataset_check_configs as core_load_dataset_check_configs,
)
from core.leads_etl.validate.framework import (
    CheckReport as CoreCheckReport,
    CheckResult as CoreCheckResult,
    CheckRunner as CoreCheckRunner,
    CheckStatus as CoreCheckStatus,
    Severity as CoreSeverity,
    parse_fail_on as core_parse_fail_on,
    render_report_json as core_render_report_json,
    render_report_markdown as core_render_report_markdown,
)
from core.leads_etl.validate.render_dq_report import (
    render_dq_report as core_render_dq_report,
    render_dq_report_json as core_render_dq_report_json,
)
from etl.transform.column_normalize import (
    ColumnNormalizationConfig as LegacyColumnNormalizationConfig,
    normalize_column_names as legacy_normalize_column_names,
)
from etl.transform.segment_mapper import (
    Segment as LegacySegment,
    load_segment_mapping as legacy_load_segment_mapping,
    map_ticket_category_with_finding as legacy_map_ticket_category_with_finding,
)
from etl.validate.checks_access_control import (
    AccessControlReconciliationCheck as LegacyAccessControlReconciliationCheck,
)
from etl.validate.checks_cross_source import (
    CrossSourceInconsistencyCheck as LegacyCrossSourceInconsistencyCheck,
)
from etl.validate.checks_duplicates import DuplicateCheck as LegacyDuplicateCheck
from etl.validate.checks_not_null import NotNullCheck as LegacyNotNullCheck
from etl.validate.checks_percentages import (
    PercentBoundsCheck as LegacyPercentBoundsCheck,
    PercentSumCheck as LegacyPercentSumCheck,
    load_percentage_check_configs as legacy_load_percentage_check_configs,
)
from etl.validate.checks_schema import (
    DatasetCheckConfig as LegacyDatasetCheckConfig,
    SchemaCheck as LegacySchemaCheck,
    load_dataset_check_configs as legacy_load_dataset_check_configs,
)
from etl.validate.framework import (
    CheckReport as LegacyCheckReport,
    CheckResult as LegacyCheckResult,
    CheckRunner as LegacyCheckRunner,
    CheckStatus as LegacyCheckStatus,
    Severity as LegacySeverity,
    parse_fail_on as legacy_parse_fail_on,
    render_report_json as legacy_render_report_json,
    render_report_markdown as legacy_render_report_markdown,
)
from etl.validate.render_dq_report import (
    render_dq_report as legacy_render_dq_report,
    render_dq_report_json as legacy_render_dq_report_json,
)


def _sample_report() -> CoreCheckReport:
    return CoreCheckReport(
        ingestion_id=501,
        generated_at=datetime(2026, 3, 3, 12, 0, 0, tzinfo=timezone.utc),
        fail_on=CoreSeverity.ERROR,
        exit_code=1,
        summary={
            "total": 1,
            "pass": 0,
            "fail": 1,
            "skip": 0,
            "info": 0,
            "warning": 0,
            "error": 1,
        },
        results=(
            CoreCheckResult(
                check_id="dq.schema.compat",
                status=CoreCheckStatus.FAIL,
                severity=CoreSeverity.ERROR,
                message="Compat payload",
                ingestion_id=501,
                evidence={"dataset_id": "compat_dataset"},
                lineage={"source_id": "SRC_COMPAT", "lineage_ref_id": 101},
            ),
        ),
    )


def test_transform_legacy_paths_delegate_to_core() -> None:
    assert LegacyColumnNormalizationConfig is CoreColumnNormalizationConfig
    assert LegacySegment is CoreSegment

    raw_columns = [" CPF ", "Cpf", "Opt In", "", None]
    aliases = {"opt_in": "optin_status"}
    legacy_columns = legacy_normalize_column_names(
        raw_columns,
        config=LegacyColumnNormalizationConfig(case="lower"),
        aliases=aliases,
    )
    core_columns = core_normalize_column_names(
        raw_columns,
        config=CoreColumnNormalizationConfig(case="lower"),
        aliases=aliases,
    )

    assert legacy_columns == core_columns
    assert legacy_load_segment_mapping() == core_load_segment_mapping()
    assert legacy_map_ticket_category_with_finding(
        "Categoria Inexistente XYZ"
    ) == core_map_ticket_category_with_finding("Categoria Inexistente XYZ")


def test_validation_loaders_and_check_exports_delegate_to_core() -> None:
    assert LegacyDatasetCheckConfig is CoreDatasetCheckConfig
    assert LegacySchemaCheck is CoreSchemaCheck
    assert LegacyNotNullCheck is CoreNotNullCheck
    assert LegacyDuplicateCheck is CoreDuplicateCheck
    assert LegacyAccessControlReconciliationCheck is CoreAccessControlReconciliationCheck
    assert LegacyPercentBoundsCheck is CorePercentBoundsCheck
    assert LegacyPercentSumCheck is CorePercentSumCheck
    assert LegacyCrossSourceInconsistencyCheck is CoreCrossSourceInconsistencyCheck
    assert legacy_load_dataset_check_configs() == core_load_dataset_check_configs()
    assert legacy_load_percentage_check_configs() == core_load_percentage_check_configs()


def test_framework_and_renderers_delegate_to_core() -> None:
    report = _sample_report()

    assert LegacySeverity is CoreSeverity
    assert LegacyCheckStatus is CoreCheckStatus
    assert LegacyCheckResult is CoreCheckResult
    assert LegacyCheckReport is CoreCheckReport
    assert LegacyCheckRunner is CoreCheckRunner
    assert legacy_parse_fail_on("warning") == core_parse_fail_on("warning")
    assert legacy_render_report_json(report) == core_render_report_json(report)
    assert legacy_render_report_markdown(report) == core_render_report_markdown(report)
    assert legacy_render_dq_report(report) == core_render_dq_report(report)
    assert legacy_render_dq_report_json(report) == core_render_dq_report_json(report)
