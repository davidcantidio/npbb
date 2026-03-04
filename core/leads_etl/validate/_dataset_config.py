"""Dataset config parsing shared by core lead ETL validation checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from ._contracts import Severity


DEFAULT_DATASETS_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "datasets.yml"


class DatasetCheckConfigError(ValueError):
    """Raised when dataset check configuration is invalid."""


@dataclass(frozen=True)
class DatasetCheckConfig:
    """Configuration contract for one dataset quality-check target."""

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
    text = str(value or "").strip()
    if not text:
        raise DatasetCheckConfigError(
            f"Campo obrigatorio invalido em dataset config: {field_name}. "
            "Como corrigir: informar texto nao vazio."
        )
    return text


def _as_column_list(value: Any, field_name: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise DatasetCheckConfigError(
            f"Campo {field_name!r} deve ser lista de colunas no datasets.yml."
        )
    seen: set[str] = set()
    output: list[str] = []
    for entry in value:
        column = _as_non_empty_string(entry, f"{field_name}[]")
        if column not in seen:
            seen.add(column)
            output.append(column)
    if not output and not allow_empty:
        raise DatasetCheckConfigError(
            f"Campo {field_name!r} nao pode ser vazio no datasets.yml."
        )
    return tuple(output)


def _coerce_severity(value: Any) -> Severity:
    raw = _as_non_empty_string(value, "severity").lower()
    try:
        return Severity(raw)
    except ValueError as exc:
        raise DatasetCheckConfigError(
            "Campo 'severity' invalido no datasets.yml. "
            "Como corrigir: usar info|warning|error."
        ) from exc


def _as_duplicate_key_sets(value: Any) -> tuple[tuple[str, ...], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise DatasetCheckConfigError(
            "Campo 'duplicate_key_sets' deve ser lista de listas de colunas."
        )
    return tuple(
        _as_column_list(entry, f"duplicate_key_sets[{index}]")
        for index, entry in enumerate(value, start=1)
    )


def _parse_dataset_entry(entry: Mapping[str, Any], index: int) -> DatasetCheckConfig:
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
        ingestion_id_column=_as_non_empty_string(entry.get("ingestion_id_column", "ingestion_id"), "ingestion_id_column"),
        source_id_column=_as_non_empty_string(entry.get("source_id_column", "source_id"), "source_id_column"),
        lineage_ref_id_column=_as_non_empty_string(
            entry.get("lineage_ref_id_column", "lineage_ref_id"),
            "lineage_ref_id_column",
        ),
    )


def load_dataset_check_configs(path: Path | str | None = None) -> tuple[DatasetCheckConfig, ...]:
    """Load schema/not-null dataset configs from YAML file."""

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

