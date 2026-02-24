"""DOCX-as-spec utilities.

Goal: treat a Word template as a versioned, executable "data contract" that can
be extracted, validated, diffed, and rendered into planning artifacts.
"""

from .docx_figures_tables import (
    extract_figures,
    extract_figures_from_docx,
    extract_tables,
    extract_tables_from_docx,
)
from .docx_sections import DocxSectionExtractor, find_nearest_section_title
from .mapping_loader import load_mapping
from .mapping_models import (
    MappingContract,
    MappingSpec,
    MappingSchemaError,
    MartContract,
    MartOutputField,
    RequirementMapping,
    SourceRef,
    ValidationRule,
    load_mapping_contract,
    normalize_mart_name,
    normalize_target_field,
    parse_mapping_contract,
)
from .mapping_validate import render_findings_json, render_findings_markdown, validate_mapping_coverage
from .policy import (
    DEFAULT_REQUIRED_SECTIONS,
    DOCX_SPEC_ARTIFACT_PATH,
    MAPPING_YAML_DEFAULT_PATH,
    MIN_SUPPORTED_MAPPING_SCHEMA_VERSION,
    MIN_SUPPORTED_SPEC_SCHEMA_VERSION,
    REQUIREMENTS_MAPPING_ARTIFACT_PATH,
    SPEC_DIFF_JSON_ARTIFACT_PATH,
    SPEC_DIFF_MD_ARTIFACT_PATH,
    SPEC_POLICY_VERSION,
    change_process_steps,
    is_spec_schema_version_supported,
    parse_major_minor,
)
from .render_mapping_md import render_mapping_md
from .render_markdown import render_docx_as_spec_md
from .spec_checks import check_duplicates, check_required_sections
from .spec_diff import DiffReport, diff_specs, render_diff_json, render_diff_markdown
from .spec_gate import evaluate_spec_gate, render_spec_gate_summary, run_spec_gate
from .spec_models import (
    CHECKLIST_COLUMNS,
    Finding,
    FindingSeverity,
    MANDATORY_SHOWS_BY_DAY_ITEM,
    SPEC_REQUIRED_SECTION_MISSING,
    SPEC_SECTION_AMBIGUOUS_TITLE,
    SPEC_SECTION_DUPLICATE_TITLE,
    DocxChecklistRow,
    DocxFigure,
    DocxSection,
    DocxSpec,
    DocxTable,
)

__all__ = [
    "DocxFigure",
    "DocxChecklistRow",
    "DocxSection",
    "DocxSpec",
    "DocxTable",
    "CHECKLIST_COLUMNS",
    "MANDATORY_SHOWS_BY_DAY_ITEM",
    "SPEC_REQUIRED_SECTION_MISSING",
    "SPEC_SECTION_DUPLICATE_TITLE",
    "SPEC_SECTION_AMBIGUOUS_TITLE",
    "FindingSeverity",
    "Finding",
    "check_required_sections",
    "check_duplicates",
    "DiffReport",
    "diff_specs",
    "render_diff_json",
    "render_diff_markdown",
    "evaluate_spec_gate",
    "run_spec_gate",
    "render_spec_gate_summary",
    "DocxSectionExtractor",
    "find_nearest_section_title",
    "SourceRef",
    "ValidationRule",
    "RequirementMapping",
    "MartOutputField",
    "MartContract",
    "MappingContract",
    "MappingSpec",
    "MappingSchemaError",
    "SPEC_POLICY_VERSION",
    "MIN_SUPPORTED_SPEC_SCHEMA_VERSION",
    "MIN_SUPPORTED_MAPPING_SCHEMA_VERSION",
    "DOCX_SPEC_ARTIFACT_PATH",
    "REQUIREMENTS_MAPPING_ARTIFACT_PATH",
    "SPEC_DIFF_MD_ARTIFACT_PATH",
    "SPEC_DIFF_JSON_ARTIFACT_PATH",
    "MAPPING_YAML_DEFAULT_PATH",
    "DEFAULT_REQUIRED_SECTIONS",
    "parse_major_minor",
    "is_spec_schema_version_supported",
    "change_process_steps",
    "normalize_target_field",
    "normalize_mart_name",
    "load_mapping",
    "validate_mapping_coverage",
    "render_findings_json",
    "render_findings_markdown",
    "render_mapping_md",
    "parse_mapping_contract",
    "load_mapping_contract",
    "extract_figures",
    "extract_figures_from_docx",
    "extract_tables",
    "extract_tables_from_docx",
    "render_docx_as_spec_md",
]
