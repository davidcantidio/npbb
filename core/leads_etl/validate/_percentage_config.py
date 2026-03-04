"""Percentage-check configuration parsing for the shared lead ETL core."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

import sqlalchemy as sa
import yaml

from ._contracts import Check, CheckContext, Severity


DEFAULT_DATASETS_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "datasets.yml"


class PercentageCheckConfigError(ValueError):
    """Raised when percentage-check configuration is invalid."""


@dataclass(frozen=True)
class PercentSumRuleConfig:
    rule_id: str
    group_by: tuple[str, ...]
    target_sum: Decimal = Decimal("100")
    tolerance: Decimal = Decimal("1")
    min_items: int = 2


@dataclass(frozen=True)
class PercentageCheckConfig:
    dataset_id: str
    table: str
    severity: Severity
    ingestion_id_column: str
    source_id_column: str
    lineage_ref_id_column: str
    value_column: str
    unit_column: str
    percent_units: tuple[str, ...]
    status_column: str | None
    allowed_statuses: tuple[str, ...]
    require_lineage: bool
    lower_bound: Decimal
    upper_bound: Decimal
    sum_rules: tuple[PercentSumRuleConfig, ...]


def _as_non_empty_str(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise PercentageCheckConfigError(
            f"Campo invalido no percentage_checks: {field}. Como corrigir: informar texto nao vazio."
        )
    return text


def _as_str_list(value: Any, field: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise PercentageCheckConfigError(f"Campo {field!r} deve ser lista no percentage_checks.")
    seen: set[str] = set()
    output: list[str] = []
    for item in value:
        text = _as_non_empty_str(item, f"{field}[]")
        if text not in seen:
            seen.add(text)
            output.append(text)
    if not output and not allow_empty:
        raise PercentageCheckConfigError(f"Campo {field!r} nao pode ser vazio no percentage_checks.")
    return tuple(output)


def _as_decimal(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise PercentageCheckConfigError(f"Campo {field!r} invalido no percentage_checks: {value!r}.") from exc


def _as_severity(value: Any) -> Severity:
    try:
        return Severity(_as_non_empty_str(value, "severity").lower())
    except ValueError as exc:
        raise PercentageCheckConfigError("Campo 'severity' invalido no percentage_checks. Como corrigir: usar info|warning|error.") from exc


def _parse_sum_rule(entry: Mapping[str, Any], index: int) -> PercentSumRuleConfig:
    if not isinstance(entry, Mapping):
        raise PercentageCheckConfigError(f"sum_rules[{index}] invalido. Como corrigir: usar objeto YAML.")
    min_items = int(entry.get("min_items", 2))
    tolerance = _as_decimal(entry.get("tolerance", "1"), "tolerance")
    if min_items <= 0:
        raise PercentageCheckConfigError(f"Campo min_items invalido em sum_rules[{index}]. Como corrigir: usar inteiro > 0.")
    if tolerance < 0:
        raise PercentageCheckConfigError(f"Campo tolerance invalido em sum_rules[{index}]. Nao pode ser negativo.")
    return PercentSumRuleConfig(rule_id=_as_non_empty_str(entry.get("rule_id", f"sum_rule_{index}"), "rule_id"), group_by=_as_str_list(entry.get("group_by"), "group_by"), target_sum=_as_decimal(entry.get("target_sum", "100"), "target_sum"), tolerance=tolerance, min_items=min_items)


def _parse_percentage_entry(entry: Mapping[str, Any], index: int) -> PercentageCheckConfig:
    if not isinstance(entry, Mapping):
        raise PercentageCheckConfigError(f"percentage_checks[{index}] invalido. Como corrigir: usar objeto YAML.")
    lower_bound = _as_decimal(entry.get("lower_bound", "0"), "lower_bound")
    upper_bound = _as_decimal(entry.get("upper_bound", "100"), "upper_bound")
    if lower_bound > upper_bound:
        raise PercentageCheckConfigError(f"Bounds invalidos em percentage_checks[{index}]: lower_bound > upper_bound.")
    allowed_statuses = tuple(status.lower() for status in _as_str_list(entry.get("allowed_statuses", ["ok"]), "allowed_statuses", allow_empty=True))
    return PercentageCheckConfig(dataset_id=_as_non_empty_str(entry.get("dataset_id"), "dataset_id"), table=_as_non_empty_str(entry.get("table"), "table"), severity=_as_severity(entry.get("severity", "error")), ingestion_id_column=_as_non_empty_str(entry.get("ingestion_id_column", "ingestion_id"), "ingestion_id_column"), source_id_column=_as_non_empty_str(entry.get("source_id_column", "source_id"), "source_id_column"), lineage_ref_id_column=_as_non_empty_str(entry.get("lineage_ref_id_column", "lineage_ref_id"), "lineage_ref_id_column"), value_column=_as_non_empty_str(entry.get("value_column", "metric_value"), "value_column"), unit_column=_as_non_empty_str(entry.get("unit_column", "unit"), "unit_column"), percent_units=tuple(unit.lower() for unit in _as_str_list(entry.get("percent_units", ["percent"]), "percent_units")), status_column=(str(entry.get("status_column")).strip() or None) if entry.get("status_column") is not None else None, allowed_statuses=allowed_statuses, require_lineage=bool(entry.get("require_lineage", True)), lower_bound=lower_bound, upper_bound=upper_bound, sum_rules=tuple(_parse_sum_rule(rule_entry, rule_idx) for rule_idx, rule_entry in enumerate(entry.get("sum_rules", []), start=1)))


def load_percentage_check_configs(path: Path | str | None = None) -> tuple[PercentageCheckConfig, ...]:
    """Load percentage-check dataset configs from `datasets.yml`."""

    config_path = Path(path) if path is not None else DEFAULT_DATASETS_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Dataset config YAML not found: {config_path}")
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, Mapping):
        raise PercentageCheckConfigError("datasets.yml invalido. Como corrigir: estrutura raiz deve ser objeto YAML.")
    raw_entries = payload.get("percentage_checks", [])
    if raw_entries in (None, ""):
        return ()
    if not isinstance(raw_entries, list):
        raise PercentageCheckConfigError("Campo 'percentage_checks' invalido. Como corrigir: usar lista de objetos.")
    parsed: list[PercentageCheckConfig] = []
    seen_ids: set[str] = set()
    for idx, entry in enumerate(raw_entries, start=1):
        config = _parse_percentage_entry(entry, idx)
        if config.dataset_id in seen_ids:
            raise PercentageCheckConfigError(f"dataset_id duplicado em percentage_checks: {config.dataset_id!r}")
        seen_ids.add(config.dataset_id)
        parsed.append(config)
    return tuple(parsed)


def resolve_lineage_payload(row_mapping: Mapping[str, Any], *, source_id_column: str, lineage_ref_id_column: str) -> dict[str, Any]:
    """Extract lineage payload from row/group mappings."""

    lineage: dict[str, Any] = {}
    if row_mapping.get(source_id_column) is not None:
        lineage["source_id"] = row_mapping.get(source_id_column)
    try:
        raw_lineage = row_mapping.get(lineage_ref_id_column)
        if raw_lineage is not None and int(raw_lineage) > 0:
            lineage["lineage_ref_id"] = int(raw_lineage)
    except (TypeError, ValueError):
        pass
    return lineage


class BasePercentageCheck(Check):
    """Base helpers for percentage checks."""

    def __init__(self, config: PercentageCheckConfig) -> None:
        self.config = config

    def _build_base_filtered_stmt(self, context: CheckContext, table: sa.Table, *, include_value_not_null: bool = True) -> Any:
        conditions: list[Any] = []
        if self.config.ingestion_id_column in table.c and context.ingestion_id is not None:
            conditions.append(table.c[self.config.ingestion_id_column] == context.ingestion_id)
        conditions.append(sa.func.lower(sa.cast(table.c[self.config.unit_column], sa.String)).in_(list(self.config.percent_units)))
        if self.config.status_column and self.config.status_column in table.c and self.config.allowed_statuses:
            conditions.append(sa.func.lower(sa.cast(table.c[self.config.status_column], sa.String)).in_(list(self.config.allowed_statuses)))
        if include_value_not_null:
            conditions.append(table.c[self.config.value_column].is_not(None))
        stmt = sa.select(*table.c).select_from(table)
        return stmt.where(sa.and_(*conditions)) if conditions else stmt

    def _ensure_columns(self, table: sa.Table, *, required: tuple[str, ...]) -> tuple[bool, list[str]]:
        missing = [column for column in required if column not in table.c]
        return (len(missing) == 0, missing)

