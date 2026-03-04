"""Compatibility re-export for shared lead ETL segment mapping."""

from core.leads_etl.transform.segment_mapper import (
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
    "Segment",
    "SegmentMappingError",
    "SegmentMappingFinding",
    "SegmentMappingResult",
    "normalize_ticket_category",
    "load_segment_mapping",
    "map_ticket_category_to_segment",
    "map_ticket_category_with_finding",
]

