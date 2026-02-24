"""Percentage bounds and sum checks driven by YAML configuration.

This module validates percentage metrics for DIMAC/social/media datasets:
- bounds check (`0..100`) per extracted value;
- sum check (`~100`) per configurable group key.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

import sqlalchemy as sa
from sqlmodel import select
import yaml

from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity


DEFAULT_DATASETS_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "datasets.yml"


class PercentageCheckConfigError(ValueError):
    """Raised when percentage-check configuration is invalid."""


@dataclass(frozen=True)
class PercentSumRuleConfig:
    """Grouping rule for percentage-sum validation.

    Args:
        rule_id: Stable identifier used in check IDs/evidence.
        group_by: Group key columns used for sum reconciliation.
        target_sum: Expected sum value (usually 100).
        tolerance: Absolute allowed difference from target sum.
        min_items: Minimum group size required to apply sum check.
    """

    rule_id: str
    group_by: tuple[str, ...]
    target_sum: Decimal = Decimal("100")
    tolerance: Decimal = Decimal("1")
    min_items: int = 2


@dataclass(frozen=True)
class PercentageCheckConfig:
    """Dataset configuration for percentage checks.

    Args:
        dataset_id: Stable dataset identifier used in check IDs.
        table: Target table name.
        severity: Severity level used when findings are detected.
        ingestion_id_column: Optional ingestion scope column.
        source_id_column: Optional source-id column used for lineage payload.
        lineage_ref_id_column: Optional lineage-reference column.
        value_column: Numeric percentage value column.
        unit_column: Unit discriminator column.
        percent_units: Allowed unit labels representing percentages.
        status_column: Optional status discriminator column.
        allowed_statuses: Optional allowed status labels for evaluation.
        require_lineage: Whether percentage rows must carry lineage_ref_id.
        lower_bound: Inclusive lower bound for percentage values.
        upper_bound: Inclusive upper bound for percentage values.
        sum_rules: Configured sum rules by group key.
    """

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
    """Parse required non-empty string field.

    Args:
        value: Raw value from configuration payload.
        field: Field name used in actionable error messages.

    Returns:
        Trimmed non-empty string.

    Raises:
        PercentageCheckConfigError: If value is invalid.
    """

    text = str(value or "").strip()
    if not text:
        raise PercentageCheckConfigError(
            f"Campo invalido no percentage_checks: {field}. "
            "Como corrigir: informar texto nao vazio."
        )
    return text


def _as_str_list(value: Any, field: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    """Parse list of strings from configuration payload.

    Args:
        value: Raw list value.
        field: Field name for actionable error messages.
        allow_empty: Whether empty list is accepted.

    Returns:
        Deduplicated tuple preserving original order.

    Raises:
        PercentageCheckConfigError: If list is malformed.
    """

    if not isinstance(value, list):
        raise PercentageCheckConfigError(
            f"Campo {field!r} deve ser lista no percentage_checks."
        )
    seen: set[str] = set()
    output: list[str] = []
    for item in value:
        text = _as_non_empty_str(item, f"{field}[]")
        if text in seen:
            continue
        seen.add(text)
        output.append(text)
    if not output and not allow_empty:
        raise PercentageCheckConfigError(
            f"Campo {field!r} nao pode ser vazio no percentage_checks."
        )
    return tuple(output)


def _as_decimal(value: Any, field: str) -> Decimal:
    """Parse Decimal value from configuration payload.

    Args:
        value: Raw numeric value.
        field: Field name used in actionable error messages.

    Returns:
        Decimal parsed value.

    Raises:
        PercentageCheckConfigError: If conversion fails.
    """

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise PercentageCheckConfigError(
            f"Campo {field!r} invalido no percentage_checks: {value!r}."
        ) from exc


def _as_severity(value: Any) -> Severity:
    """Parse severity enum from raw config value."""

    raw = _as_non_empty_str(value, "severity").lower()
    try:
        return Severity(raw)
    except ValueError as exc:
        raise PercentageCheckConfigError(
            "Campo 'severity' invalido no percentage_checks. "
            "Como corrigir: usar info|warning|error."
        ) from exc


def _parse_sum_rule(entry: Mapping[str, Any], index: int) -> PercentSumRuleConfig:
    """Parse one percentage-sum rule entry.

    Args:
        entry: Raw sum-rule mapping.
        index: Rule index for actionable error context.

    Returns:
        Parsed sum-rule config.
    """

    if not isinstance(entry, Mapping):
        raise PercentageCheckConfigError(
            f"sum_rules[{index}] invalido. Como corrigir: usar objeto YAML."
        )
    rule_id = _as_non_empty_str(entry.get("rule_id", f"sum_rule_{index}"), "rule_id")
    group_by = _as_str_list(entry.get("group_by"), "group_by")
    target_sum = _as_decimal(entry.get("target_sum", "100"), "target_sum")
    tolerance = _as_decimal(entry.get("tolerance", "1"), "tolerance")
    min_items_raw = entry.get("min_items", 2)
    try:
        min_items = int(min_items_raw)
    except (TypeError, ValueError) as exc:
        raise PercentageCheckConfigError(
            f"Campo min_items invalido em sum_rules[{index}]: {min_items_raw!r}."
        ) from exc
    if min_items <= 0:
        raise PercentageCheckConfigError(
            f"Campo min_items invalido em sum_rules[{index}]. Como corrigir: usar inteiro > 0."
        )
    if tolerance < 0:
        raise PercentageCheckConfigError(
            f"Campo tolerance invalido em sum_rules[{index}]. Nao pode ser negativo."
        )
    return PercentSumRuleConfig(
        rule_id=rule_id,
        group_by=group_by,
        target_sum=target_sum,
        tolerance=tolerance,
        min_items=min_items,
    )


def _parse_percentage_entry(entry: Mapping[str, Any], index: int) -> PercentageCheckConfig:
    """Parse one percentage-check dataset entry.

    Args:
        entry: Raw dataset entry from YAML list.
        index: Dataset index for actionable error context.

    Returns:
        Parsed percentage check config object.
    """

    if not isinstance(entry, Mapping):
        raise PercentageCheckConfigError(
            f"percentage_checks[{index}] invalido. Como corrigir: usar objeto YAML."
        )
    sum_rules_raw = entry.get("sum_rules", [])
    if not isinstance(sum_rules_raw, list):
        raise PercentageCheckConfigError(
            f"Campo sum_rules invalido em percentage_checks[{index}]. Deve ser lista."
        )
    sum_rules = tuple(
        _parse_sum_rule(rule_entry, rule_idx)
        for rule_idx, rule_entry in enumerate(sum_rules_raw, start=1)
    )

    status_column_raw = entry.get("status_column")
    status_column = None
    if status_column_raw is not None:
        text = str(status_column_raw).strip()
        status_column = text or None

    allowed_statuses = _as_str_list(
        entry.get("allowed_statuses", ["ok"]),
        "allowed_statuses",
        allow_empty=True,
    )

    lower_bound = _as_decimal(entry.get("lower_bound", "0"), "lower_bound")
    upper_bound = _as_decimal(entry.get("upper_bound", "100"), "upper_bound")
    if lower_bound > upper_bound:
        raise PercentageCheckConfigError(
            f"Bounds invalidos em percentage_checks[{index}]: lower_bound > upper_bound."
        )

    return PercentageCheckConfig(
        dataset_id=_as_non_empty_str(entry.get("dataset_id"), "dataset_id"),
        table=_as_non_empty_str(entry.get("table"), "table"),
        severity=_as_severity(entry.get("severity", "error")),
        ingestion_id_column=_as_non_empty_str(
            entry.get("ingestion_id_column", "ingestion_id"),
            "ingestion_id_column",
        ),
        source_id_column=_as_non_empty_str(
            entry.get("source_id_column", "source_id"),
            "source_id_column",
        ),
        lineage_ref_id_column=_as_non_empty_str(
            entry.get("lineage_ref_id_column", "lineage_ref_id"),
            "lineage_ref_id_column",
        ),
        value_column=_as_non_empty_str(entry.get("value_column", "metric_value"), "value_column"),
        unit_column=_as_non_empty_str(entry.get("unit_column", "unit"), "unit_column"),
        percent_units=tuple(unit.lower() for unit in _as_str_list(entry.get("percent_units", ["percent"]), "percent_units")),
        status_column=status_column,
        allowed_statuses=tuple(status.lower() for status in allowed_statuses),
        require_lineage=bool(entry.get("require_lineage", True)),
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        sum_rules=sum_rules,
    )


def load_percentage_check_configs(path: Path | str | None = None) -> tuple[PercentageCheckConfig, ...]:
    """Load percentage-check dataset configs from `datasets.yml`.

    Args:
        path: Optional YAML path. Defaults to `etl/validate/config/datasets.yml`.

    Returns:
        Tuple of parsed percentage check configs. Empty tuple when key is absent.

    Raises:
        FileNotFoundError: If config file does not exist.
        PercentageCheckConfigError: If percentage config is malformed.
    """

    config_path = Path(path) if path is not None else DEFAULT_DATASETS_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Dataset config YAML not found: {config_path}")
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, Mapping):
        raise PercentageCheckConfigError(
            "datasets.yml invalido. Como corrigir: estrutura raiz deve ser objeto YAML."
        )
    raw_entries = payload.get("percentage_checks", [])
    if raw_entries in (None, ""):
        return ()
    if not isinstance(raw_entries, list):
        raise PercentageCheckConfigError(
            "Campo 'percentage_checks' invalido. Como corrigir: usar lista de objetos."
        )

    parsed: list[PercentageCheckConfig] = []
    seen_ids: set[str] = set()
    for idx, entry in enumerate(raw_entries, start=1):
        config = _parse_percentage_entry(entry, idx)
        if config.dataset_id in seen_ids:
            raise PercentageCheckConfigError(
                f"dataset_id duplicado em percentage_checks: {config.dataset_id!r}"
            )
        seen_ids.add(config.dataset_id)
        parsed.append(config)
    return tuple(parsed)


def _resolve_lineage_payload(
    row_mapping: Mapping[str, Any],
    *,
    source_id_column: str,
    lineage_ref_id_column: str,
) -> dict[str, Any]:
    """Extract lineage payload from row/group mappings."""

    lineage: dict[str, Any] = {}
    source_id = row_mapping.get(source_id_column)
    if source_id is not None:
        lineage["source_id"] = source_id
    raw_lineage = row_mapping.get(lineage_ref_id_column)
    try:
        if raw_lineage is not None:
            parsed = int(raw_lineage)
            if parsed > 0:
                lineage["lineage_ref_id"] = parsed
    except (TypeError, ValueError):
        pass
    return lineage


class _BasePercentageCheck(Check):
    """Base helpers for percentage checks."""

    def __init__(self, config: PercentageCheckConfig) -> None:
        self.config = config

    def _build_base_filtered_stmt(
        self,
        context: CheckContext,
        table: sa.Table,
        *,
        include_value_not_null: bool = True,
    ) -> Any:
        """Build base select statement scoped to percent rows."""

        conditions: list[Any] = []
        if self.config.ingestion_id_column in table.c and context.ingestion_id is not None:
            conditions.append(table.c[self.config.ingestion_id_column] == context.ingestion_id)

        unit_expr = sa.func.lower(sa.cast(table.c[self.config.unit_column], sa.String))
        conditions.append(unit_expr.in_(list(self.config.percent_units)))

        if self.config.status_column and self.config.status_column in table.c and self.config.allowed_statuses:
            status_expr = sa.func.lower(sa.cast(table.c[self.config.status_column], sa.String))
            conditions.append(status_expr.in_(list(self.config.allowed_statuses)))

        if include_value_not_null:
            conditions.append(table.c[self.config.value_column].is_not(None))

        stmt = select(*table.c).select_from(table)
        if conditions:
            stmt = stmt.where(sa.and_(*conditions))
        return stmt

    def _ensure_columns(self, table: sa.Table, *, required: Sequence[str]) -> tuple[bool, list[str]]:
        """Validate required table columns."""

        missing = [column for column in required if column not in table.c]
        return (len(missing) == 0, missing)


class PercentBoundsCheck(_BasePercentageCheck):
    """Validate percentage values are within configured bounds and lineage rules."""

    def __init__(self, config: PercentageCheckConfig) -> None:
        super().__init__(config)
        self.check_id = f"dq.percent.bounds.{config.dataset_id}"
        self.description = "Valida bounds de percentuais por dataset."

    def run(self, context: CheckContext) -> CheckResult:
        """Execute percentage bounds check for one dataset config."""

        session = context.require_resource("session")
        engine = session.get_bind()
        inspector = sa.inspect(engine)
        table_name = self.config.table
        if table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.config.severity,
                message=(
                    "Tabela de dataset nao encontrada para check de percentuais. "
                    "Como corrigir: validar migration e config percentage_checks."
                ),
                ingestion_id=context.ingestion_id,
                evidence={"dataset_id": self.config.dataset_id, "table": table_name, "missing_table": True},
            )

        table = sa.Table(table_name, sa.MetaData(), autoload_with=engine)
        ok, missing_columns = self._ensure_columns(
            table,
            required=(
                self.config.value_column,
                self.config.unit_column,
                self.config.source_id_column,
                self.config.lineage_ref_id_column,
            ),
        )
        if not ok:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.config.severity,
                message=(
                    "Schema incompleto para check de percentuais. Como corrigir: "
                    "alinhar tabela alvo com config percentage_checks."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.config.dataset_id,
                    "table": table_name,
                    "missing_columns": missing_columns,
                },
            )

        stmt = self._build_base_filtered_stmt(context, table, include_value_not_null=True)
        rows = [dict(row) for row in session.execute(stmt).mappings().all()]
        if not rows:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message="Check ignorado: nenhum percentual encontrado no escopo.",
                ingestion_id=context.ingestion_id,
                evidence={"dataset_id": self.config.dataset_id, "table": table_name, "scoped_rows": 0},
            )

        findings: list[dict[str, Any]] = []
        for row in rows:
            raw_value = row.get(self.config.value_column)
            try:
                value = Decimal(str(raw_value))
            except (InvalidOperation, ValueError, TypeError):
                findings.append(
                    {
                        "code": "PERCENT_VALUE_INVALID",
                        "value": raw_value,
                        "row_hint": {
                            "source_id": row.get(self.config.source_id_column),
                            "lineage_ref_id": row.get(self.config.lineage_ref_id_column),
                        },
                    }
                )
                continue

            if value < self.config.lower_bound or value > self.config.upper_bound:
                findings.append(
                    {
                        "code": "PERCENT_OUT_OF_BOUNDS",
                        "value": str(value),
                        "bounds": [str(self.config.lower_bound), str(self.config.upper_bound)],
                        "row_hint": {
                            "source_id": row.get(self.config.source_id_column),
                            "lineage_ref_id": row.get(self.config.lineage_ref_id_column),
                        },
                    }
                )

            if self.config.require_lineage:
                lineage_raw = row.get(self.config.lineage_ref_id_column)
                has_lineage = False
                try:
                    has_lineage = lineage_raw is not None and int(lineage_raw) > 0
                except (TypeError, ValueError):
                    has_lineage = False
                if not has_lineage:
                    findings.append(
                        {
                            "code": "PERCENT_MISSING_LINEAGE",
                            "value": str(value),
                            "row_hint": {
                                "source_id": row.get(self.config.source_id_column),
                                "lineage_ref_id": lineage_raw,
                            },
                        }
                    )

        if findings:
            sample = findings[:10]
            first_lineage = _resolve_lineage_payload(
                sample[0].get("row_hint", {}),
                source_id_column="source_id",
                lineage_ref_id_column="lineage_ref_id",
            )
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.config.severity,
                message=(
                    "Percentuais fora de bounds e/ou sem linhagem detectados. Como corrigir: "
                    "revisar parse da metrica e registro de lineage_ref."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.config.dataset_id,
                    "table": table_name,
                    "scoped_rows": len(rows),
                    "finding_count": len(findings),
                    "findings_sample": sample,
                },
                lineage=first_lineage,
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Percentuais em bounds e com linhagem no escopo.",
            ingestion_id=context.ingestion_id,
            evidence={
                "dataset_id": self.config.dataset_id,
                "table": table_name,
                "scoped_rows": len(rows),
                "finding_count": 0,
            },
        )


class PercentSumCheck(_BasePercentageCheck):
    """Validate grouped percentage sums against configured target values."""

    def __init__(self, config: PercentageCheckConfig, rule: PercentSumRuleConfig) -> None:
        super().__init__(config)
        self.rule = rule
        self.check_id = f"dq.percent.sum.{config.dataset_id}.{rule.rule_id}"
        self.description = "Valida soma de percentuais por grupo configurado."

    def run(self, context: CheckContext) -> CheckResult:
        """Execute grouped percentage-sum check for one sum rule."""

        session = context.require_resource("session")
        engine = session.get_bind()
        inspector = sa.inspect(engine)
        table_name = self.config.table
        if table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.config.severity,
                message=(
                    "Tabela de dataset nao encontrada para check de soma percentual. "
                    "Como corrigir: validar migration e config percentage_checks."
                ),
                ingestion_id=context.ingestion_id,
                evidence={"dataset_id": self.config.dataset_id, "table": table_name, "missing_table": True},
            )

        table = sa.Table(table_name, sa.MetaData(), autoload_with=engine)
        required_columns = (
            self.config.value_column,
            self.config.unit_column,
            self.config.source_id_column,
            self.config.lineage_ref_id_column,
            *self.rule.group_by,
        )
        ok, missing_columns = self._ensure_columns(table, required=required_columns)
        if not ok:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.config.severity,
                message=(
                    "Schema incompleto para check de soma de percentuais. Como corrigir: "
                    "alinhar group_by/value columns no dataset alvo."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.config.dataset_id,
                    "table": table_name,
                    "rule_id": self.rule.rule_id,
                    "missing_columns": missing_columns,
                },
            )

        conditions: list[Any] = []
        if self.config.ingestion_id_column in table.c and context.ingestion_id is not None:
            conditions.append(table.c[self.config.ingestion_id_column] == context.ingestion_id)
        unit_expr = sa.func.lower(sa.cast(table.c[self.config.unit_column], sa.String))
        conditions.append(unit_expr.in_(list(self.config.percent_units)))
        conditions.append(table.c[self.config.value_column].is_not(None))

        if self.config.status_column and self.config.status_column in table.c and self.config.allowed_statuses:
            status_expr = sa.func.lower(sa.cast(table.c[self.config.status_column], sa.String))
            conditions.append(status_expr.in_(list(self.config.allowed_statuses)))

        group_columns = [table.c[column_name] for column_name in self.rule.group_by]
        count_label = "item_count"
        sum_label = "sum_value"
        grouped_stmt = (
            select(
                *group_columns,
                sa.func.count().label(count_label),
                sa.func.sum(table.c[self.config.value_column]).label(sum_label),
                sa.func.min(table.c[self.config.source_id_column]).label("sample_source_id"),
                sa.func.min(table.c[self.config.lineage_ref_id_column]).label("sample_lineage_ref_id"),
            )
            .select_from(table)
            .where(sa.and_(*conditions))
            .group_by(*group_columns)
        )
        grouped_rows = [dict(row) for row in session.execute(grouped_stmt).mappings().all()]
        if not grouped_rows:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message="Check ignorado: nenhum grupo percentual encontrado no escopo.",
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.config.dataset_id,
                    "table": table_name,
                    "rule_id": self.rule.rule_id,
                    "group_count": 0,
                },
            )

        findings: list[dict[str, Any]] = []
        evaluated_groups = 0
        for group in grouped_rows:
            item_count = int(group.get(count_label) or 0)
            if item_count < self.rule.min_items:
                continue
            evaluated_groups += 1
            group_sum = Decimal(str(group.get(sum_label)))
            diff = abs(group_sum - self.rule.target_sum)
            if diff > self.rule.tolerance:
                group_key = {column: group.get(column) for column in self.rule.group_by}
                findings.append(
                    {
                        "code": "PERCENT_SUM_MISMATCH",
                        "rule_id": self.rule.rule_id,
                        "group_key": group_key,
                        "group_item_count": item_count,
                        "group_sum": str(group_sum),
                        "target_sum": str(self.rule.target_sum),
                        "tolerance": str(self.rule.tolerance),
                        "row_hint": {
                            "source_id": group.get("sample_source_id"),
                            "lineage_ref_id": group.get("sample_lineage_ref_id"),
                        },
                    }
                )

        if findings:
            sample = findings[:10]
            first_lineage = _resolve_lineage_payload(
                sample[0].get("row_hint", {}),
                source_id_column="source_id",
                lineage_ref_id_column="lineage_ref_id",
            )
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.config.severity,
                message=(
                    "Soma de percentuais inconsistente por grupo configurado. Como corrigir: "
                    "revisar metricas da pergunta/grupo e evidencias de origem."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.config.dataset_id,
                    "table": table_name,
                    "rule_id": self.rule.rule_id,
                    "group_count": len(grouped_rows),
                    "evaluated_groups": evaluated_groups,
                    "finding_count": len(findings),
                    "findings_sample": sample,
                },
                lineage=first_lineage,
            )

        if evaluated_groups == 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message=(
                    "Check ignorado: grupos com menos itens que o minimo para validar soma percentual."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.config.dataset_id,
                    "table": table_name,
                    "rule_id": self.rule.rule_id,
                    "group_count": len(grouped_rows),
                    "evaluated_groups": 0,
                    "min_items": self.rule.min_items,
                },
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Soma de percentuais consistente para grupos avaliados.",
            ingestion_id=context.ingestion_id,
            evidence={
                "dataset_id": self.config.dataset_id,
                "table": table_name,
                "rule_id": self.rule.rule_id,
                "group_count": len(grouped_rows),
                "evaluated_groups": evaluated_groups,
                "finding_count": 0,
            },
        )


def build_percentage_checks(
    configs: Sequence[PercentageCheckConfig],
) -> tuple[Check, ...]:
    """Build percentage checks (bounds + sum) from dataset configs.

    Args:
        configs: Parsed percentage-check configs.

    Returns:
        Tuple containing one bounds check and N sum checks per dataset.
    """

    checks: list[Check] = []
    for config in configs:
        checks.append(PercentBoundsCheck(config))
        for rule in config.sum_rules:
            checks.append(PercentSumCheck(config, rule))
    return tuple(checks)
