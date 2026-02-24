"""Unit tests for PPTX metric mapping configuration loader."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from etl.extract.pptx_mapping import PptxMappingSchemaError, load_pptx_mapping


def _repo_config_path() -> Path:
    """Return repository default PPTX mapping config path."""
    return Path("etl/extract/config/pptx_metrics.yml")


def test_load_pptx_mapping_success_from_repo_config() -> None:
    """Loader should parse repository mapping config into typed rule objects."""
    mapping = load_pptx_mapping(_repo_config_path())

    assert mapping.schema_version == "1.0"
    assert len(mapping.rules) >= 1
    first_rule = mapping.rules[0]
    assert first_rule.metric_name
    assert first_rule.platform
    assert first_rule.unit
    assert first_rule.extraction_rule
    assert first_rule.slide_number is not None or first_rule.title_regex is not None


def test_load_pptx_mapping_fails_when_required_field_missing(tmp_path: Path) -> None:
    """Loader should fail with field path when required keys are missing."""
    payload = {
        "schema_version": "1.0",
        "rules": [
            {
                "slide_number": 3,
                "platform": "instagram",
                "unit": "count",
                "extraction_rule": "label:Alcance total",
            }
        ],
    }
    invalid_path = tmp_path / "pptx_metrics_missing.yml"
    invalid_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(PptxMappingSchemaError, match=r"\$\.rules\[0\]\.metric_name: missing required field"):
        load_pptx_mapping(invalid_path)


def test_load_pptx_mapping_fails_when_regex_is_invalid(tmp_path: Path) -> None:
    """Loader should fail with actionable error for invalid title regex."""
    payload = {
        "schema_version": "1.0",
        "rules": [
            {
                "metric_name": "media_reach_total",
                "platform": "instagram",
                "unit": "count",
                "title_regex": "[unclosed",
                "extraction_rule": "label:Alcance total",
            }
        ],
    }
    invalid_path = tmp_path / "pptx_metrics_bad_regex.yml"
    invalid_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(PptxMappingSchemaError, match=r"\$\.rules\[0\]\.title_regex: invalid regex"):
        load_pptx_mapping(invalid_path)


def test_load_pptx_mapping_fails_when_slide_and_regex_are_missing(tmp_path: Path) -> None:
    """Loader should reject rules without slide_number and title_regex."""
    payload = {
        "schema_version": "1.0",
        "rules": [
            {
                "metric_name": "social_positive_sentiment",
                "platform": "social_listening",
                "unit": "percent",
                "extraction_rule": "label:Sentimento positivo",
            }
        ],
    }
    invalid_path = tmp_path / "pptx_metrics_without_target.yml"
    invalid_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        PptxMappingSchemaError,
        match=r"\$\.rules\[0\]: at least one target must be provided: slide_number or title_regex",
    ):
        load_pptx_mapping(invalid_path)
