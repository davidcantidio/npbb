"""Compatibility re-export for shared lead ETL schema checks."""

from core.leads_etl.validate.checks_schema import (
    DatasetCheckConfig,
    DatasetCheckConfigError,
    SchemaCheck,
    build_schema_checks,
    load_dataset_check_configs,
)

__all__ = [
    "DatasetCheckConfig",
    "DatasetCheckConfigError",
    "SchemaCheck",
    "build_schema_checks",
    "load_dataset_check_configs",
]
