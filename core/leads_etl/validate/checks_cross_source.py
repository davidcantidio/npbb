"""Public cross-source inconsistency API for shared lead ETL validation."""

from ._cross_source_impl import CrossSourceDatasetSpec, CrossSourceInconsistencyCheck
from ._cross_source_persistence import persist_cross_source_inconsistencies

__all__ = [
    "CrossSourceDatasetSpec",
    "CrossSourceInconsistencyCheck",
    "persist_cross_source_inconsistencies",
]

