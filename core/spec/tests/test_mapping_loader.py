"""Tests for mapping loader normalization and YAML parse diagnostics."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.spec.mapping_loader import load_mapping
from core.spec.mapping_models import MappingSchemaError


def _write_yaml(tmp_path: Path, content: str) -> Path:
    """Write helper YAML content to a temporary file."""
    path = tmp_path / "mapping.yml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_mapping_normalizes_target_field_and_mart_name(tmp_path: Path) -> None:
    """Loader normalizes `table.field` refs and mart names to a canonical form."""
    mapping_yaml = """
schema_version: "1.0"
spec_source: "docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md"
requirements:
  - requirement_id: "REQ-001"
    item_docx: "Shows por dia (12/12, 13/12, 14/12)"
    target_field: "Attendance_Access_Control.Entries_Validated"
    calculation_rule: "SUM(entries_validated)"
    sources:
      - source_id: "pdf_access_control_2025_12_12"
        location: "pagina 1 / tabela Presencas"
    validations:
      - rule_id: "VAL-001"
        rule_type: "not_null"
        severity: "error"
        expression: "entries_validated IS NOT NULL"
marts:
  - mart_name: "MART_REPORT_SHOW_DAY_SUMMARY"
    grain: "evento_dia_sessao"
    description: "Resumo por dia/sessao"
    requirement_ids: ["REQ-001"]
    output_fields:
      - field: "entries_validated"
        source: "attendance_access_control.entries_validated"
        rule: "Soma por sessao"
"""
    path = _write_yaml(tmp_path, mapping_yaml)

    spec = load_mapping(path)

    assert spec.requirements[0].target_field == "public.attendance_access_control.entries_validated"
    assert spec.marts[0].mart_name == "mart_report_show_day_summary"


def test_load_mapping_respects_custom_default_schema(tmp_path: Path) -> None:
    """Loader applies the provided default schema for `table.field` refs."""
    mapping_yaml = """
schema_version: "1.0"
spec_source: "docs/spec.md"
requirements:
  - requirement_id: "REQ-001"
    item_docx: "Publico do evento"
    target_field: "attendance_access_control.entries_validated"
    calculation_rule: "SUM(entries_validated)"
    sources:
      - source_id: "src"
        location: "aba X"
    validations:
      - rule_id: "VAL-001"
        rule_type: "not_null"
        severity: "error"
        expression: "entries_validated IS NOT NULL"
marts:
  - mart_name: "mart_report_publico"
    grain: "evento_dia_sessao"
    description: "Resumo"
    requirement_ids: ["REQ-001"]
    output_fields:
      - field: "entries_validated"
        source: "attendance_access_control.entries_validated"
        rule: "Soma"
"""
    path = _write_yaml(tmp_path, mapping_yaml)

    spec = load_mapping(path, default_schema="analytics")

    assert spec.requirements[0].target_field == "analytics.attendance_access_control.entries_validated"


def test_load_mapping_reports_yaml_line_and_column_on_parse_error(tmp_path: Path) -> None:
    """YAML syntax errors include file path plus line and column when available."""
    broken_yaml = """
schema_version: "1.0"
spec_source: "docs/spec.md"
requirements
  - requirement_id: "REQ-001"
"""
    path = _write_yaml(tmp_path, broken_yaml)

    with pytest.raises(MappingSchemaError, match=r"mapping\.yml:\d+:\d+: invalid YAML syntax"):
        load_mapping(path)
