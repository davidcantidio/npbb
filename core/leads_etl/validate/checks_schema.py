"""Public schema-check API for shared lead ETL validation."""

from ._dataset_config import (
    DatasetCheckConfig,
    DatasetCheckConfigError,
    load_dataset_check_configs,
)
from ._schema_check_impl import SchemaCheck, build_schema_checks

__all__ = [
    "DatasetCheckConfig",
    "DatasetCheckConfigError",
    "SchemaCheck",
    "build_schema_checks",
    "load_dataset_check_configs",
]

