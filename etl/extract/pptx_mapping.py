"""Config loader for PPTX slide-to-metric mapping rules.

This module defines a typed, versioned contract used to map slide content to
metrics without hardcoding extractor logic. Each rule can target a slide by:
- explicit `slide_number`, and/or
- `title_regex` matching the slide title.

Guidance for evidences:
- Keep `extraction_rule` aligned with the label shown in the slide.
- When extracting values, persist the label text as evidence for lineage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Pattern

import yaml


class PptxMappingSchemaError(ValueError):
    """Raised when PPTX metric mapping YAML does not follow required schema."""


@dataclass(frozen=True)
class PptxMappingRule:
    """Typed mapping rule used by PPTX metric extraction.

    Attributes:
        metric_name: Canonical metric identifier (snake_case recommended).
        platform: Source platform or channel (for example: instagram, x, tv).
        unit: Metric unit (for example: count, percent, currency_brl).
        extraction_rule: Human-readable extraction strategy and evidence label.
        slide_number: Optional one-based fixed slide position.
        title_regex: Optional regex to match slide title when position varies.
        title_pattern: Compiled regex object derived from `title_regex`.
    """

    metric_name: str
    platform: str
    unit: str
    extraction_rule: str
    slide_number: int | None = None
    title_regex: str | None = None
    title_pattern: Pattern[str] | None = field(default=None, repr=False, compare=False)

    def matches(self, *, slide_number: int, slide_title: str) -> bool:
        """Return whether this rule applies to one slide context."""
        matches_number = self.slide_number is None or self.slide_number == slide_number
        if not matches_number:
            return False
        if self.title_pattern is None:
            return True
        return bool(self.title_pattern.search(slide_title or ""))


@dataclass(frozen=True)
class PptxMetricsMapping:
    """Top-level typed mapping payload loaded from YAML."""

    schema_version: str
    rules: list[PptxMappingRule]


def _err(path: str, message: str) -> PptxMappingSchemaError:
    """Build schema error with JSONPath-like field context."""
    return PptxMappingSchemaError(f"{path}: {message}")


def _require_dict(value: Any, path: str) -> dict[str, Any]:
    """Require mapping value."""
    if not isinstance(value, dict):
        raise _err(path, f"expected mapping/dict, got {type(value).__name__}")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    """Require list value."""
    if not isinstance(value, list):
        raise _err(path, f"expected list, got {type(value).__name__}")
    return value


def _require_non_empty_str(parent: dict[str, Any], key: str, path: str) -> str:
    """Extract required non-empty string field from parent mapping."""
    if key not in parent:
        raise _err(f"{path}.{key}", "missing required field")
    value = parent[key]
    if not isinstance(value, str):
        raise _err(f"{path}.{key}", f"expected string, got {type(value).__name__}")
    clean = value.strip()
    if not clean:
        raise _err(f"{path}.{key}", "must be a non-empty string")
    return clean


def _parse_optional_positive_int(parent: dict[str, Any], key: str, path: str) -> int | None:
    """Parse optional positive integer field."""
    if key not in parent or parent[key] is None:
        return None
    value = parent[key]
    if isinstance(value, bool):
        raise _err(f"{path}.{key}", "expected positive integer, got bool")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise _err(f"{path}.{key}", f"expected positive integer, got {type(value).__name__}") from exc
    if number <= 0:
        raise _err(f"{path}.{key}", "must be a positive integer")
    return number


def _parse_optional_regex(parent: dict[str, Any], key: str, path: str) -> tuple[str | None, Pattern[str] | None]:
    """Parse and compile optional regex with actionable errors."""
    if key not in parent or parent[key] is None:
        return None, None
    value = parent[key]
    if not isinstance(value, str):
        raise _err(f"{path}.{key}", f"expected string regex, got {type(value).__name__}")
    regex = value.strip()
    if not regex:
        raise _err(f"{path}.{key}", "must be a non-empty regex string")
    try:
        pattern = re.compile(regex, flags=re.IGNORECASE)
    except re.error as exc:
        raise _err(f"{path}.{key}", f"invalid regex ({exc})") from exc
    return regex, pattern


def _parse_rules(items: Any, path: str) -> list[PptxMappingRule]:
    """Parse rule entries and validate minimum targeting constraints."""
    rows = _require_list(items, path)
    if not rows:
        raise _err(path, "must contain at least one rule")

    parsed: list[PptxMappingRule] = []
    seen_keys: set[tuple[str, str]] = set()
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        metric_name = _require_non_empty_str(data, "metric_name", row_path)
        platform = _require_non_empty_str(data, "platform", row_path)
        dedupe_key = (metric_name.casefold(), platform.casefold())
        if dedupe_key in seen_keys:
            raise _err(
                f"{row_path}.metric_name",
                f"duplicated metric/platform pair '{metric_name}/{platform}'",
            )
        seen_keys.add(dedupe_key)

        slide_number = _parse_optional_positive_int(data, "slide_number", row_path)
        title_regex, title_pattern = _parse_optional_regex(data, "title_regex", row_path)
        if slide_number is None and title_pattern is None:
            raise _err(
                row_path,
                "at least one target must be provided: slide_number or title_regex",
            )

        parsed.append(
            PptxMappingRule(
                metric_name=metric_name,
                platform=platform,
                unit=_require_non_empty_str(data, "unit", row_path),
                extraction_rule=_require_non_empty_str(data, "extraction_rule", row_path),
                slide_number=slide_number,
                title_regex=title_regex,
                title_pattern=title_pattern,
            )
        )
    return parsed


def parse_pptx_mapping(payload: Any) -> PptxMetricsMapping:
    """Validate and parse raw YAML payload into typed PPTX mapping config.

    Args:
        payload: Parsed YAML object (expected mapping with `schema_version` and
            `rules` list).

    Returns:
        Typed :class:`PptxMetricsMapping` object.

    Raises:
        PptxMappingSchemaError: If required fields are missing, types are
            invalid, or rule regex patterns cannot compile.
    """

    root = _require_dict(payload, "$")
    schema_version = _require_non_empty_str(root, "schema_version", "$")
    rules = _parse_rules(root.get("rules"), "$.rules")
    return PptxMetricsMapping(schema_version=schema_version, rules=rules)


def _yaml_error_with_location(path: Path, exc: yaml.YAMLError) -> PptxMappingSchemaError:
    """Build YAML syntax error with line/column details when available."""
    mark = getattr(exc, "problem_mark", None)
    problem = getattr(exc, "problem", None)
    if mark is not None:
        line = mark.line + 1
        column = mark.column + 1
        detail = problem or str(exc)
        return PptxMappingSchemaError(f"{path}:{line}:{column}: invalid YAML syntax ({detail})")
    return PptxMappingSchemaError(f"{path}: invalid YAML syntax ({exc})")


def load_pptx_mapping(path: str | Path) -> PptxMetricsMapping:
    """Load PPTX metric mapping YAML and return validated typed rules.

    Args:
        path: YAML path for mapping config, usually
            `npbb/etl/extract/config/pptx_metrics.yml`.

    Returns:
        Parsed and validated :class:`PptxMetricsMapping`.

    Raises:
        FileNotFoundError: If mapping path does not exist.
        PptxMappingSchemaError: If YAML syntax/schema validation fails.
    """

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"PPTX mapping YAML not found: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise _yaml_error_with_location(yaml_path, exc) from exc
    return parse_pptx_mapping(payload)
