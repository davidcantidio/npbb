"""Core ingestion registry package.

Provides typed contracts and actionable error types to standardize source and
ingestion tracking across ETL components.
"""

from .errors import (
    DuplicateSourceError,
    IngestionNotFoundError,
    InvalidIngestionStatusError,
    InvalidStatusTransitionError,
    RegistryError,
    SourceFileError,
    SourceFileNotFoundError,
    SourceFilePermissionError,
    SourceNotFoundError,
)
from .lineage_policy import (
    LINEAGE_MISSING_SEVERITIES,
    LINEAGE_REQUIREMENTS,
    LineageMissingSeverity,
    LineagePolicy,
    LineagePolicyResult,
    LineageRequirement,
    evaluate_lineage_policy,
)
from .location_ref import format_location, parse_location
from .types import (
    IngestionId,
    IngestionRecord,
    IngestionStatus,
    LOCATION_TYPES,
    LocationType,
    RegistryReader,
    RegistryRepository,
    RegistryWriter,
    SourceId,
    SourceKind,
    SourceRecord,
    TERMINAL_INGESTION_STATUSES,
)

__all__ = [
    "SourceId",
    "IngestionId",
    "SourceKind",
    "IngestionStatus",
    "LocationType",
    "LOCATION_TYPES",
    "TERMINAL_INGESTION_STATUSES",
    "SourceRecord",
    "IngestionRecord",
    "RegistryReader",
    "RegistryWriter",
    "RegistryRepository",
    "RegistryError",
    "SourceNotFoundError",
    "IngestionNotFoundError",
    "DuplicateSourceError",
    "InvalidIngestionStatusError",
    "InvalidStatusTransitionError",
    "SourceFileError",
    "SourceFileNotFoundError",
    "SourceFilePermissionError",
    "format_location",
    "parse_location",
    "LineageRequirement",
    "LineageMissingSeverity",
    "LINEAGE_REQUIREMENTS",
    "LINEAGE_MISSING_SEVERITIES",
    "LineagePolicy",
    "LineagePolicyResult",
    "evaluate_lineage_policy",
]
