"""Shared transform helpers for lead ETL flows."""

from .column_normalize import (
    ColumnNormalizationConfig,
    normalize_column_name,
    normalize_column_names,
)
from .segment_mapper import (
    Segment,
    SegmentMappingError,
    SegmentMappingFinding,
    SegmentMappingResult,
    load_segment_mapping,
    map_ticket_category_to_segment,
    map_ticket_category_with_finding,
    normalize_ticket_category,
)

__all__ = [
    "ColumnNormalizationConfig",
    "normalize_column_name",
    "normalize_column_names",
    "Segment",
    "SegmentMappingError",
    "SegmentMappingFinding",
    "SegmentMappingResult",
    "normalize_ticket_category",
    "load_segment_mapping",
    "map_ticket_category_to_segment",
    "map_ticket_category_with_finding",
]

