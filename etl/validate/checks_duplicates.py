"""Compatibility re-export for shared lead ETL duplicate checks."""

from core.leads_etl.validate.checks_duplicates import (
    DuplicateCheck,
    DuplicateCheckSpec,
    build_duplicate_checks,
)

__all__ = ["DuplicateCheck", "DuplicateCheckSpec", "build_duplicate_checks"]
