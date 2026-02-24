"""High-level loader for DOCX mapping contracts.

This module is the single entrypoint used by ETL/report tooling to load the
YAML mapping as a typed and normalized source of truth.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .mapping_models import MappingSchemaError, MappingSpec, parse_mapping_contract


def _yaml_error_with_location(path: Path, exc: yaml.YAMLError) -> MappingSchemaError:
    """Build a parser error message including line/column when available."""
    mark = getattr(exc, "problem_mark", None)
    problem = getattr(exc, "problem", None)
    if mark is not None:
        line = mark.line + 1
        column = mark.column + 1
        detail = problem or str(exc)
        return MappingSchemaError(f"{path}:{line}:{column}: invalid YAML syntax ({detail})")
    return MappingSchemaError(f"{path}: invalid YAML syntax ({exc})")


def load_mapping(path: str | Path, *, default_schema: str = "public") -> MappingSpec:
    """Load mapping YAML into a normalized, typed mapping specification.

    Args:
        path: File path to mapping YAML.
        default_schema: Schema applied when target references use `table.field`.

    Returns:
        Parsed `MappingSpec` with normalized target references.

    Raises:
        FileNotFoundError: If path does not exist.
        MappingSchemaError: If YAML syntax or schema validation fails.
    """
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"Mapping YAML not found: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise _yaml_error_with_location(yaml_path, exc) from exc
    return parse_mapping_contract(payload, default_schema=default_schema)
