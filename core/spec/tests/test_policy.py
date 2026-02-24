"""Unit tests for DOCX spec versioning policy."""

from __future__ import annotations

import pytest

from core.spec.policy import (
    DOCX_SPEC_ARTIFACT_PATH,
    MAPPING_YAML_DEFAULT_PATH,
    MIN_SUPPORTED_SPEC_SCHEMA_VERSION,
    REQUIREMENTS_MAPPING_ARTIFACT_PATH,
    SPEC_DIFF_JSON_ARTIFACT_PATH,
    SPEC_DIFF_MD_ARTIFACT_PATH,
    change_process_steps,
    is_spec_schema_version_supported,
    parse_major_minor,
)


def test_parse_major_minor_accepts_valid_format() -> None:
    """Version parser accepts valid `major.minor` values."""
    assert parse_major_minor("1.0") == (1, 0)
    assert parse_major_minor("1.9") == (1, 9)


def test_parse_major_minor_rejects_invalid_format() -> None:
    """Version parser rejects malformed values."""
    with pytest.raises(ValueError):
        parse_major_minor("1")
    with pytest.raises(ValueError):
        parse_major_minor("v1.0")
    with pytest.raises(ValueError):
        parse_major_minor("1.0.0")


def test_is_spec_schema_version_supported_follows_policy() -> None:
    """Support check enforces same major and minor >= minimum."""
    assert is_spec_schema_version_supported(MIN_SUPPORTED_SPEC_SCHEMA_VERSION) is True
    assert is_spec_schema_version_supported("1.1") is True
    assert is_spec_schema_version_supported("2.0") is False
    assert is_spec_schema_version_supported("1.0", min_supported="1.1") is False


def test_change_process_steps_reference_standard_artifacts() -> None:
    """Process steps explicitly reference default generated artifacts."""
    steps = "\n".join(change_process_steps())

    assert DOCX_SPEC_ARTIFACT_PATH in steps
    assert REQUIREMENTS_MAPPING_ARTIFACT_PATH in steps
    assert SPEC_DIFF_MD_ARTIFACT_PATH in steps
    assert SPEC_DIFF_JSON_ARTIFACT_PATH in steps
    assert MAPPING_YAML_DEFAULT_PATH in steps
