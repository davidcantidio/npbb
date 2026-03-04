"""Compatibility re-export for shared lead ETL not-null checks."""

from core.leads_etl.validate.checks_not_null import NotNullCheck, build_not_null_checks

__all__ = ["NotNullCheck", "build_not_null_checks"]
