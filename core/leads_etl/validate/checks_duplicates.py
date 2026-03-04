"""Public duplicate check API for shared lead ETL validation."""

from ._duplicate_check_impl import DuplicateCheck, DuplicateCheckSpec, build_duplicate_checks

__all__ = ["DuplicateCheck", "DuplicateCheckSpec", "build_duplicate_checks"]
