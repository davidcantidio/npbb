"""Schema drift checks driven by dataset YAML configuration.

This module provides:
- `DatasetCheckConfig` contract for dataset-level DQ checks;
- YAML loader for `etl/validate/config/datasets.yml`;
- `SchemaCheck` implementation to validate required columns per table.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import sqlalchemy as sa
import yaml

from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity


DEFAULT_DATASETS_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "datasets.yml"


class DatasetCheckConfigError(ValueError):
    """Raised when dataset check configuration is invalid."""


@dataclass(frozen=True)
class DatasetCheckConfig:
    """Configuration contract for one dataset quality-check target.

    Args:
        dataset_id: Stable identifier used in check IDs.
        table: Target database table name.
        domain: Domain label (`staging`/`canonical`) for evidence grouping.
        severity: Severity level for schema/not-null failures.
        required_columns: Columns expected to exist in target table.
        critical_not_null_columns: Columns that must not be NULL.
        duplicate_key_sets: Optional key sets for duplicate detection checks.
        ingestion_id_column: Optional ingestion column for scoped checks.
        source_id_column: Optional source column for lineage hints.
        lineage_ref_id_column: Optional lineage reference column for hints.
    """

    dataset_id: str
    table: str
    domain: str
    severity: Severity
    required_columns: tuple[str, ...]
    critical_not_null_columns: tuple[str, ...]
    duplicate_key_sets: tuple[tuple[str, ...], ...] = ()
    ingestion_id_column: str = "ingestion_id"
    source_id_column: str = "source_id"
    lineage_ref_id_column: str = "lineage_ref_id"


def _as_non_empty_string(value: Any, field_name: str) -> str:
    """Validate and normalize one required non-empty string field.

    Args:
        value: Input value from parsed YAML.
        field_name: Field name for actionable error messages.

    Returns:
        Trimmed string value.

    Raises:
        DatasetCheckConfigError: If value is not a non-empty string.
    """

    text = str(value or "").strip()
    if not text:
        raise DatasetCheckConfigError(
            f"Campo obrigatorio invalido em dataset config: {field_name}. "
            "Como corrigir: informar texto nao vazio."
        )
    return text


def _as_column_list(value: Any, field_name: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    """Validate one YAML list of column names.

    Args:
        value: Input list from YAML payload.
        field_name: Field name for actionable validation errors.
        allow_empty: Whether an empty list is accepted.

    Returns:
        Deduplicated tuple of normalized column names preserving order.

    Raises:
        DatasetCheckConfigError: If list is malformed or empty when required.
    """

    if not isinstance(value, list):
        raise DatasetCheckConfigError(
            f"Campo {field_name!r} deve ser lista de colunas no datasets.yml."
        )

    seen: set[str] = set()
    output: list[str] = []
    for entry in value:
        column = _as_non_empty_string(entry, f"{field_name}[]")
        if column in seen:
            continue
        seen.add(column)
        output.append(column)

    if not output and not allow_empty:
        raise DatasetCheckConfigError(
            f"Campo {field_name!r} nao pode ser vazio no datasets.yml."
        )
    return tuple(output)


def _coerce_severity(value: Any) -> Severity:
    """Parse and validate severity value from YAML payload.

    Args:
        value: Raw YAML severity value.

    Returns:
        Controlled framework severity enum.

    Raises:
        DatasetCheckConfigError: If severity is unsupported.
    """

    raw = _as_non_empty_string(value, "severity").lower()
    try:
        return Severity(raw)
    except ValueError as exc:
        raise DatasetCheckConfigError(
            "Campo 'severity' invalido no datasets.yml. "
            "Como corrigir: usar info|warning|error."
        ) from exc


def _as_duplicate_key_sets(value: Any) -> tuple[tuple[str, ...], ...]:
    """Validate and parse duplicate key sets from YAML dataset config.

    Args:
        value: Raw `duplicate_key_sets` field from one dataset config.

    Returns:
        Tuple of key sets, where each key set is a tuple of column names.

    Raises:
        DatasetCheckConfigError: If structure is invalid.
    """

    if value is None:
        return ()
    if not isinstance(value, list):
        raise DatasetCheckConfigError(
            "Campo 'duplicate_key_sets' deve ser lista de listas de colunas."
        )

    parsed_sets: list[tuple[str, ...]] = []
    for index, entry in enumerate(value, start=1):
        columns = _as_column_list(entry, f"duplicate_key_sets[{index}]")
        parsed_sets.append(columns)
    return tuple(parsed_sets)


def _parse_dataset_entry(entry: Mapping[str, Any], index: int) -> DatasetCheckConfig:
    """Parse one dataset entry from YAML payload.

    Args:
        entry: Dataset object from YAML list.
        index: One-based list position used in validation messages.

    Returns:
        Parsed dataset configuration object.

    Raises:
        DatasetCheckConfigError: If entry is malformed.
    """

    if not isinstance(entry, Mapping):
        raise DatasetCheckConfigError(
            f"Item datasets[{index}] invalido. Como corrigir: usar objeto YAML."
        )

    required_columns = _as_column_list(entry.get("required_columns"), "required_columns")
    critical_not_null_columns = _as_column_list(
        entry.get("critical_not_null_columns"),
        "critical_not_null_columns",
        allow_empty=True,
    )

    if critical_not_null_columns:
        missing_in_required = sorted(set(critical_not_null_columns) - set(required_columns))
        if missing_in_required:
            raise DatasetCheckConfigError(
                "Columns em critical_not_null_columns devem existir em required_columns. "
                f"dataset={entry.get('dataset_id')!r} missing={missing_in_required}."
            )

    return DatasetCheckConfig(
        dataset_id=_as_non_empty_string(entry.get("dataset_id"), "dataset_id"),
        table=_as_non_empty_string(entry.get("table"), "table"),
        domain=_as_non_empty_string(entry.get("domain"), "domain"),
        severity=_coerce_severity(entry.get("severity", "error")),
        required_columns=required_columns,
        critical_not_null_columns=critical_not_null_columns,
        duplicate_key_sets=_as_duplicate_key_sets(entry.get("duplicate_key_sets")),
        ingestion_id_column=_as_non_empty_string(
            entry.get("ingestion_id_column", "ingestion_id"),
            "ingestion_id_column",
        ),
        source_id_column=_as_non_empty_string(
            entry.get("source_id_column", "source_id"),
            "source_id_column",
        ),
        lineage_ref_id_column=_as_non_empty_string(
            entry.get("lineage_ref_id_column", "lineage_ref_id"),
            "lineage_ref_id_column",
        ),
    )


def load_dataset_check_configs(path: Path | str | None = None) -> tuple[DatasetCheckConfig, ...]:
    """Load schema/not-null dataset configs from YAML file.

    Args:
        path: Optional YAML path. Defaults to bundled `datasets.yml`.

    Returns:
        Tuple of validated dataset check configs.

    Raises:
        FileNotFoundError: If config file does not exist.
        DatasetCheckConfigError: If payload is invalid.
    """

    config_path = Path(path) if path is not None else DEFAULT_DATASETS_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Dataset config YAML not found: {config_path}")

    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, Mapping):
        raise DatasetCheckConfigError(
            "datasets.yml invalido. Como corrigir: estrutura raiz deve ser objeto YAML."
        )

    datasets = payload.get("datasets")
    if not isinstance(datasets, list):
        raise DatasetCheckConfigError(
            "datasets.yml invalido. Como corrigir: campo 'datasets' deve ser lista."
        )

    parsed: list[DatasetCheckConfig] = []
    seen_ids: set[str] = set()
    for idx, entry in enumerate(datasets, start=1):
        config = _parse_dataset_entry(entry, idx)
        if config.dataset_id in seen_ids:
            raise DatasetCheckConfigError(
                f"dataset_id duplicado em datasets.yml: {config.dataset_id!r}"
            )
        seen_ids.add(config.dataset_id)
        parsed.append(config)
    return tuple(parsed)


class SchemaCheck(Check):
    """Validate required columns for one dataset target table."""

    def __init__(self, dataset_config: DatasetCheckConfig) -> None:
        """Create one schema check bound to dataset configuration.

        Args:
            dataset_config: Dataset check configuration loaded from YAML.
        """

        self.dataset_config = dataset_config
        self.check_id = f"dq.schema.{dataset_config.dataset_id}"
        self.description = (
            "Valida schema esperado da tabela por dataset para detectar drift."
        )

    def run(self, context: CheckContext) -> CheckResult:
        """Execute schema drift validation against configured table.

        Args:
            context: Check execution context with DB session resource.

        Returns:
            `CheckResult` with pass/fail and actionable evidence.
        """

        session = context.require_resource("session")
        inspector = sa.inspect(session.get_bind())
        table_name = self.dataset_config.table

        if table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.dataset_config.severity,
                message=(
                    "Tabela de dataset nao encontrada. Como corrigir: "
                    "validar migration e nome da tabela no datasets.yml."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "domain": self.dataset_config.domain,
                    "table": table_name,
                    "missing_table": True,
                },
            )

        present_columns = {
            str(item["name"]).strip()
            for item in inspector.get_columns(table_name)
            if item.get("name") is not None
        }
        missing_columns = sorted(
            column for column in self.dataset_config.required_columns if column not in present_columns
        )
        if missing_columns:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.dataset_config.severity,
                message=(
                    "Schema incompleto para dataset. Como corrigir: "
                    "alinhar migration/modelo com required_columns."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "domain": self.dataset_config.domain,
                    "table": table_name,
                    "missing_columns": missing_columns,
                    "required_columns": list(self.dataset_config.required_columns),
                },
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Schema esperado encontrado para dataset.",
            ingestion_id=context.ingestion_id,
            evidence={
                "dataset_id": self.dataset_config.dataset_id,
                "domain": self.dataset_config.domain,
                "table": table_name,
                "required_columns_count": len(self.dataset_config.required_columns),
            },
        )


def build_schema_checks(configs: Sequence[DatasetCheckConfig]) -> tuple[SchemaCheck, ...]:
    """Build one `SchemaCheck` per dataset config.

    Args:
        configs: Dataset check configs loaded from YAML.

    Returns:
        Tuple of schema checks preserving config order.
    """

    return tuple(SchemaCheck(config) for config in configs)
