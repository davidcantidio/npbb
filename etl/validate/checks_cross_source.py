"""Compatibility re-export for shared lead ETL cross-source checks."""

from core.leads_etl.validate.checks_cross_source import (
    CrossSourceDatasetSpec,
    CrossSourceInconsistencyCheck,
    persist_cross_source_inconsistencies,
)

__all__ = [
    "CrossSourceDatasetSpec",
    "CrossSourceInconsistencyCheck",
    "persist_cross_source_inconsistencies",
]
