"""Unit tests for Word placeholders mapping loader and schema validation."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from reports.word import (
    PlaceholderMappingError,
    PlaceholderRenderType,
    load_placeholders_mapping,
)
from reports.word.placeholders_mapping import DEFAULT_PLACEHOLDERS_MAPPING_PATH


def _write_yaml(path: Path, content: str) -> Path:
    """Write temporary YAML content for mapping validation tests."""

    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_load_default_word_placeholders_mapping_contract() -> None:
    """Default mapping should load and expose typed placeholder bindings."""

    mapping = load_placeholders_mapping(DEFAULT_PLACEHOLDERS_MAPPING_PATH)

    assert mapping.version == 1
    assert len(mapping.placeholders) >= 1
    first = mapping.placeholders[0]
    assert first.placeholder_id
    assert first.mart_name.startswith("mart_report_")
    assert isinstance(first.params, dict)
    assert isinstance(first.render_type, PlaceholderRenderType)


def test_default_mapping_contains_show_coverage_table_placeholder() -> None:
    """Default mapping should expose dedicated show-coverage table placeholder."""

    mapping = load_placeholders_mapping(DEFAULT_PLACEHOLDERS_MAPPING_PATH)
    binding = mapping.by_id("SHOW__COVERAGE__TABLE")

    assert binding.mart_name == "mart_report_show_day_summary"
    assert binding.render_type is PlaceholderRenderType.TABLE
    assert binding.params["columns"] == [
        "dia",
        "sessao",
        "status_access_control",
        "status_optin",
        "status_ticket_sales",
        "observacoes",
    ]


def test_load_placeholders_mapping_rejects_invalid_render_type(tmp_path: Path) -> None:
    """Loader should fail with actionable message for unsupported render_type."""

    yaml_path = _write_yaml(
        tmp_path / "invalid_render_type.yml",
        """
        version: 1
        placeholders:
          - placeholder_id: PUBLICO__ATTENDANCE__TABLE
            mart_name: mart_report_attendance_by_session
            params: {}
            render_type: chart
        """,
    )

    with pytest.raises(PlaceholderMappingError, match="render_type invalido"):
        load_placeholders_mapping(yaml_path)


def test_load_placeholders_mapping_rejects_duplicate_placeholder_id(tmp_path: Path) -> None:
    """Loader should fail when two placeholders share the same id."""

    yaml_path = _write_yaml(
        tmp_path / "duplicate.yml",
        """
        version: 1
        placeholders:
          - placeholder_id: PUBLICO__ATTENDANCE__TABLE
            mart_name: mart_report_attendance_by_session
            params: {}
            render_type: table
          - placeholder_id: PUBLICO__ATTENDANCE__TABLE
            mart_name: mart_report_sources
            params: {}
            render_type: text
        """,
    )

    with pytest.raises(PlaceholderMappingError, match="duplicado"):
        load_placeholders_mapping(yaml_path)


def test_load_placeholders_mapping_rejects_invalid_placeholder_naming(tmp_path: Path) -> None:
    """Loader should enforce placeholder naming convention aligned to sections."""

    yaml_path = _write_yaml(
        tmp_path / "invalid_placeholder_name.yml",
        """
        version: 1
        placeholders:
          - placeholder_id: publico_attendance
            mart_name: mart_report_attendance_by_session
            params: {}
            render_type: table
        """,
    )

    with pytest.raises(PlaceholderMappingError, match="placeholder_id invalido"):
        load_placeholders_mapping(yaml_path)


def test_load_placeholders_mapping_rejects_invalid_params_value_type(tmp_path: Path) -> None:
    """Loader should reject unsupported param value types with clear guidance."""

    yaml_path = _write_yaml(
        tmp_path / "invalid_params.yml",
        """
        version: 1
        placeholders:
          - placeholder_id: FONTES__SUMMARY__TEXT
            mart_name: mart_report_sources
            params:
              nested:
                foo: bar
            render_type: text
        """,
    )

    with pytest.raises(PlaceholderMappingError, match="tipo de parametro invalido"):
        load_placeholders_mapping(yaml_path)


def test_load_placeholders_mapping_accepts_list_params_for_contract_fields(tmp_path: Path) -> None:
    """Loader should accept scalar lists in params for table/chart contracts."""

    yaml_path = _write_yaml(
        tmp_path / "list_params.yml",
        """
        version: 1
        placeholders:
          - placeholder_id: PUBLICO__ATTENDANCE__TABLE
            mart_name: mart_report_attendance_by_session
            params:
              columns:
                - sessao
                - presentes
                - validos
            render_type: table
        """,
    )

    mapping = load_placeholders_mapping(yaml_path)
    binding = mapping.by_id("PUBLICO__ATTENDANCE__TABLE")
    assert binding.params["columns"] == ["sessao", "presentes", "validos"]
