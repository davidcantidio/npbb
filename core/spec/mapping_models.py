"""Schema models and validators for DOCX-to-schema mapping contracts.

This module defines a versioned YAML contract that links each DOCX checklist
item to canonical fields and mart outputs, including sources and validations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal

import yaml


ValidationSeverity = Literal["error", "warning"]
ValidationType = Literal["not_null", "range", "reconciliation", "uniqueness", "custom"]
MartGrain = Literal["evento", "evento_dia", "evento_dia_sessao", "sessao"]

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MART_NAME_RE = re.compile(r"^mart_[a-z0-9_]+$")


class MappingSchemaError(ValueError):
    """Raised when a mapping YAML file does not match the required schema."""


@dataclass(frozen=True)
class SourceRef:
    """Lineage pointer for a metric source location."""

    source_id: str
    location: str

    def model_dump(self) -> Dict[str, str]:
        """Serialize to plain dict."""
        return {"source_id": self.source_id, "location": self.location}


@dataclass(frozen=True)
class ValidationRule:
    """Validation rule linked to a requirement mapping."""

    rule_id: str
    rule_type: ValidationType
    severity: ValidationSeverity
    expression: str

    def model_dump(self) -> Dict[str, str]:
        """Serialize to plain dict."""
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "severity": self.severity,
            "expression": self.expression,
        }


@dataclass(frozen=True)
class RequirementMapping:
    """Mapping between one DOCX item and one canonical target field."""

    requirement_id: str
    item_docx: str
    target_field: str
    calculation_rule: str
    sources: List[SourceRef]
    validations: List[ValidationRule]

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "requirement_id": self.requirement_id,
            "item_docx": self.item_docx,
            "target_field": self.target_field,
            "calculation_rule": self.calculation_rule,
            "sources": [s.model_dump() for s in self.sources],
            "validations": [v.model_dump() for v in self.validations],
        }


@dataclass(frozen=True)
class MartOutputField:
    """Output field contract for one mart/view."""

    field: str
    source: str
    rule: str

    def model_dump(self) -> Dict[str, str]:
        """Serialize to plain dict."""
        return {"field": self.field, "source": self.source, "rule": self.rule}


@dataclass(frozen=True)
class MartContract:
    """Contract definition for one mart/view used in reporting."""

    mart_name: str
    grain: MartGrain
    description: str
    requirement_ids: List[str]
    output_fields: List[MartOutputField]

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "mart_name": self.mart_name,
            "grain": self.grain,
            "description": self.description,
            "requirement_ids": list(self.requirement_ids),
            "output_fields": [f.model_dump() for f in self.output_fields],
        }


@dataclass(frozen=True)
class MappingContract:
    """Top-level mapping contract parsed from YAML."""

    schema_version: str
    spec_source: str
    requirements: List[RequirementMapping]
    marts: List[MartContract]

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "schema_version": self.schema_version,
            "spec_source": self.spec_source,
            "requirements": [r.model_dump() for r in self.requirements],
            "marts": [m.model_dump() for m in self.marts],
        }


MappingSpec = MappingContract


def _err(path: str, message: str) -> MappingSchemaError:
    """Build a schema error with JSONPath-like context."""
    return MappingSchemaError(f"{path}: {message}")


def _require_dict(value: Any, path: str) -> Dict[str, Any]:
    """Require a mapping object."""
    if not isinstance(value, dict):
        raise _err(path, f"expected mapping/dict, got {type(value).__name__}")
    return value


def _require_list(value: Any, path: str) -> List[Any]:
    """Require a list object."""
    if not isinstance(value, list):
        raise _err(path, f"expected list, got {type(value).__name__}")
    return value


def _require_non_empty_str(parent: Dict[str, Any], key: str, path: str) -> str:
    """Extract a required non-empty string field."""
    if key not in parent:
        raise _err(f"{path}.{key}", "missing required field")
    value = parent[key]
    if not isinstance(value, str):
        raise _err(f"{path}.{key}", f"expected string, got {type(value).__name__}")
    clean = value.strip()
    if not clean:
        raise _err(f"{path}.{key}", "must be a non-empty string")
    return clean


def normalize_target_field(value: str, path: str, *, default_schema: str) -> str:
    """Normalize field reference to canonical `schema.table.field`.

    Args:
        value: Raw reference string from YAML.
        path: JSONPath-like path used in validation messages.
        default_schema: Schema used when input is `table.field`.

    Returns:
        Canonical and lowercased field reference (`schema.table.field`).

    Raises:
        MappingSchemaError: If the reference does not follow accepted formats.
    """
    parts = [p.strip() for p in value.split(".") if p.strip()]
    if len(parts) == 2:
        schema_name = default_schema.strip()
        table_name, field_name = parts
    elif len(parts) == 3:
        schema_name, table_name, field_name = parts
    else:
        raise _err(path, "must follow 'table.field' or 'schema.table.field' format")

    for name, label in (
        (schema_name, "schema"),
        (table_name, "table"),
        (field_name, "field"),
    ):
        if not _IDENTIFIER_RE.fullmatch(name):
            raise _err(path, f"invalid {label} identifier '{name}'")

    return f"{schema_name.lower()}.{table_name.lower()}.{field_name.lower()}"


def normalize_mart_name(value: str, path: str) -> str:
    """Normalize mart/view name and validate naming convention."""
    normalized = value.strip().lower()
    if not _MART_NAME_RE.fullmatch(normalized):
        raise _err(path, "must match pattern 'mart_[a-z0-9_]+'")
    return normalized


def _parse_source_refs(items: Any, path: str) -> List[SourceRef]:
    """Parse `sources` list from mapping YAML."""
    rows = _require_list(items, path)
    if not rows:
        raise _err(path, "must contain at least one source reference")

    parsed: List[SourceRef] = []
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        parsed.append(
            SourceRef(
                source_id=_require_non_empty_str(data, "source_id", row_path),
                location=_require_non_empty_str(data, "location", row_path),
            )
        )
    return parsed


def _parse_validation_rules(items: Any, path: str) -> List[ValidationRule]:
    """Parse `validations` list from mapping YAML."""
    rows = _require_list(items, path)
    if not rows:
        raise _err(path, "must contain at least one validation rule")

    parsed: List[ValidationRule] = []
    allowed_types = {"not_null", "range", "reconciliation", "uniqueness", "custom"}
    allowed_severity = {"error", "warning"}
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        rule_type = _require_non_empty_str(data, "rule_type", row_path)
        severity = _require_non_empty_str(data, "severity", row_path)
        if rule_type not in allowed_types:
            raise _err(
                f"{row_path}.rule_type",
                f"invalid value '{rule_type}'. Allowed: {', '.join(sorted(allowed_types))}",
            )
        if severity not in allowed_severity:
            raise _err(
                f"{row_path}.severity",
                f"invalid value '{severity}'. Allowed: {', '.join(sorted(allowed_severity))}",
            )
        parsed.append(
            ValidationRule(
                rule_id=_require_non_empty_str(data, "rule_id", row_path),
                rule_type=rule_type,  # type: ignore[arg-type]
                severity=severity,  # type: ignore[arg-type]
                expression=_require_non_empty_str(data, "expression", row_path),
            )
        )
    return parsed


def _parse_requirements(items: Any, path: str, *, default_schema: str) -> List[RequirementMapping]:
    """Parse requirement mappings and validate required domains/types."""
    rows = _require_list(items, path)
    if not rows:
        raise _err(path, "must contain at least one requirement mapping")

    parsed: List[RequirementMapping] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        requirement_id = _require_non_empty_str(data, "requirement_id", row_path)
        if requirement_id in seen_ids:
            raise _err(f"{row_path}.requirement_id", f"duplicated requirement_id '{requirement_id}'")
        seen_ids.add(requirement_id)
        target_field = normalize_target_field(
            _require_non_empty_str(data, "target_field", row_path),
            f"{row_path}.target_field",
            default_schema=default_schema,
        )
        parsed.append(
            RequirementMapping(
                requirement_id=requirement_id,
                item_docx=_require_non_empty_str(data, "item_docx", row_path),
                target_field=target_field,
                calculation_rule=_require_non_empty_str(data, "calculation_rule", row_path),
                sources=_parse_source_refs(data.get("sources"), f"{row_path}.sources"),
                validations=_parse_validation_rules(data.get("validations"), f"{row_path}.validations"),
            )
        )
    return parsed


def _parse_output_fields(items: Any, path: str) -> List[MartOutputField]:
    """Parse output field contracts from one mart definition."""
    rows = _require_list(items, path)
    if not rows:
        raise _err(path, "must contain at least one output field")

    parsed: List[MartOutputField] = []
    seen_fields: set[str] = set()
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        field = _require_non_empty_str(data, "field", row_path)
        if field in seen_fields:
            raise _err(f"{row_path}.field", f"duplicated output field '{field}'")
        seen_fields.add(field)
        parsed.append(
            MartOutputField(
                field=field,
                source=_require_non_empty_str(data, "source", row_path),
                rule=_require_non_empty_str(data, "rule", row_path),
            )
        )
    return parsed


def _parse_marts(items: Any, path: str, valid_requirement_ids: set[str]) -> List[MartContract]:
    """Parse mart contracts and validate requirement references."""
    rows = _require_list(items, path)
    if not rows:
        raise _err(path, "must contain at least one mart contract")

    parsed: List[MartContract] = []
    allowed_grain = {"evento", "evento_dia", "evento_dia_sessao", "sessao"}
    seen_marts: set[str] = set()
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        mart_name = normalize_mart_name(
            _require_non_empty_str(data, "mart_name", row_path),
            f"{row_path}.mart_name",
        )
        if mart_name in seen_marts:
            raise _err(f"{row_path}.mart_name", f"duplicated mart_name '{mart_name}'")
        seen_marts.add(mart_name)

        grain = _require_non_empty_str(data, "grain", row_path)
        if grain not in allowed_grain:
            raise _err(
                f"{row_path}.grain",
                f"invalid value '{grain}'. Allowed: {', '.join(sorted(allowed_grain))}",
            )

        requirement_ids = _require_list(data.get("requirement_ids"), f"{row_path}.requirement_ids")
        if not requirement_ids:
            raise _err(f"{row_path}.requirement_ids", "must contain at least one requirement_id")
        bad_refs: List[str] = []
        clean_ids: List[str] = []
        for req_index, req_id in enumerate(requirement_ids):
            req_path = f"{row_path}.requirement_ids[{req_index}]"
            if not isinstance(req_id, str) or not req_id.strip():
                raise _err(req_path, f"expected non-empty string, got {type(req_id).__name__}")
            req_id_clean = req_id.strip()
            clean_ids.append(req_id_clean)
            if req_id_clean not in valid_requirement_ids:
                bad_refs.append(req_id_clean)
        if bad_refs:
            unique_bad = ", ".join(sorted(set(bad_refs)))
            raise _err(
                f"{row_path}.requirement_ids",
                f"unknown requirement_id reference(s): {unique_bad}",
            )

        parsed.append(
            MartContract(
                mart_name=mart_name,
                grain=grain,  # type: ignore[arg-type]
                description=_require_non_empty_str(data, "description", row_path),
                requirement_ids=clean_ids,
                output_fields=_parse_output_fields(data.get("output_fields"), f"{row_path}.output_fields"),
            )
        )
    return parsed


def parse_mapping_contract(payload: Any, *, default_schema: str = "public") -> MappingContract:
    """Validate and parse a mapping YAML payload.

    Args:
        payload: Parsed YAML object (typically `dict`).
        default_schema: Default schema for references provided as `table.field`.

    Returns:
        A validated `MappingContract`.

    Raises:
        MappingSchemaError: If required fields, domains, or types are invalid.
    """
    root = _require_dict(payload, "$")
    schema_version = _require_non_empty_str(root, "schema_version", "$")
    spec_source = _require_non_empty_str(root, "spec_source", "$")
    if not _IDENTIFIER_RE.fullmatch(default_schema):
        raise _err("$.default_schema", f"invalid default schema '{default_schema}'")
    requirements = _parse_requirements(
        root.get("requirements"),
        "$.requirements",
        default_schema=default_schema,
    )
    requirement_ids = {r.requirement_id for r in requirements}
    marts = _parse_marts(root.get("marts"), "$.marts", requirement_ids)
    return MappingContract(
        schema_version=schema_version,
        spec_source=spec_source,
        requirements=requirements,
        marts=marts,
    )


def load_mapping_contract(
    yaml_path: str | Path,
    *,
    default_schema: str = "public",
) -> MappingContract:
    """Load, validate, and parse a YAML mapping contract file.

    Args:
        yaml_path: Path to mapping YAML.
        default_schema: Default schema for references in `table.field` format.

    Returns:
        Parsed and validated `MappingContract`.

    Raises:
        FileNotFoundError: If the YAML path does not exist.
        MappingSchemaError: If YAML is invalid or schema validation fails.
    """
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"Mapping YAML not found: {path}")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise MappingSchemaError(f"{path}: invalid YAML syntax ({exc})") from exc
    return parse_mapping_contract(payload, default_schema=default_schema)
