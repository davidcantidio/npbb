"""Word report package for TMJ report generation.

This package contains the base renderer and helpers to generate
an output DOCX from a valid template, including minimal text placeholders.
"""

from .placeholders_mapping import (
    PlaceholderMappingError,
    PlaceholderRenderType,
    WordPlaceholderBinding,
    WordPlaceholdersMapping,
    ensure_mart_name,
    is_valid_mart_name,
    load_placeholders_mapping,
)
from .mart_query_runner import (
    MartQueryResult,
    MartQueryRunner,
    MartQueryRunnerError,
    rows_to_chart_payload,
    rows_to_table_payload,
    rows_to_text_payload,
)
from .render_text import (
    PlaceholderTextRenderError,
    placeholder_token,
    query_to_text_payload,
    render_text_placeholder,
)
from .render_table import (
    PlaceholderTableRenderError,
    render_table_placeholder,
)
from .render_figure import (
    PlaceholderFigureRenderError,
    render_figure_placeholder,
)
from .render_show_coverage import (
    SHOW_COVERAGE_LEGEND_LINES,
    SHOW_COVERAGE_PLACEHOLDER_ID,
    SHOW_COVERAGE_REQUIRED_COLUMNS,
    ShowCoverageRenderError,
    render_show_coverage_section,
    validate_show_coverage_columns,
)
from .render_gaps import (
    GapSectionRenderError,
    load_dq_report,
    render_gaps_section,
)
from .gate_policy import (
    DEFAULT_REPORT_GATE_POLICY_PATH,
    GateDecision,
    GateShowCoveragePolicy,
    ReportGatePolicy,
    ReportGatePolicyError,
    evaluate_report_gate,
    load_report_gate_policy,
    merge_show_coverage_gaps,
)
from .render_lineage import (
    LineageRef,
    LineageRenderError,
    extract_lineage_refs_from_rows,
    normalize_lineage_refs,
    render_lineage_block,
)
from .report_manifest import (
    DEFAULT_REPORT_MANIFEST_FILENAME,
    REPORT_MANIFEST_SCHEMA_VERSION,
    build_report_manifest,
    default_report_manifest_path,
    write_report_manifest,
)
from .template_validate import (
    TemplatePlaceholderFinding,
    find_placeholders,
    validate_template_placeholders,
)
from .renderer import WordReportRenderer

__all__ = [
    "WordReportRenderer",
    "PlaceholderRenderType",
    "PlaceholderMappingError",
    "WordPlaceholderBinding",
    "WordPlaceholdersMapping",
    "is_valid_mart_name",
    "ensure_mart_name",
    "load_placeholders_mapping",
    "MartQueryResult",
    "MartQueryRunner",
    "MartQueryRunnerError",
    "rows_to_text_payload",
    "rows_to_table_payload",
    "rows_to_chart_payload",
    "PlaceholderTextRenderError",
    "PlaceholderTableRenderError",
    "PlaceholderFigureRenderError",
    "ShowCoverageRenderError",
    "GapSectionRenderError",
    "DEFAULT_REPORT_GATE_POLICY_PATH",
    "ReportGatePolicy",
    "GateShowCoveragePolicy",
    "GateDecision",
    "ReportGatePolicyError",
    "load_report_gate_policy",
    "evaluate_report_gate",
    "merge_show_coverage_gaps",
    "LineageRef",
    "LineageRenderError",
    "load_dq_report",
    "render_gaps_section",
    "placeholder_token",
    "query_to_text_payload",
    "render_text_placeholder",
    "render_table_placeholder",
    "render_figure_placeholder",
    "SHOW_COVERAGE_PLACEHOLDER_ID",
    "SHOW_COVERAGE_REQUIRED_COLUMNS",
    "SHOW_COVERAGE_LEGEND_LINES",
    "validate_show_coverage_columns",
    "render_show_coverage_section",
    "normalize_lineage_refs",
    "extract_lineage_refs_from_rows",
    "render_lineage_block",
    "DEFAULT_REPORT_MANIFEST_FILENAME",
    "REPORT_MANIFEST_SCHEMA_VERSION",
    "default_report_manifest_path",
    "build_report_manifest",
    "write_report_manifest",
    "TemplatePlaceholderFinding",
    "find_placeholders",
    "validate_template_placeholders",
]
