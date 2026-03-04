"""Compatibility re-export for shared lead ETL column normalization."""

from core.leads_etl.transform.column_normalize import (
    ColumnNormalizationConfig,
    normalize_column_name,
    normalize_column_names,
)

__all__ = [
    "ColumnNormalizationConfig",
    "normalize_column_name",
    "normalize_column_names",
]

