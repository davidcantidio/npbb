"""Staging model for social/media metrics extracted from PPTX slides.

This table stores mapping-driven metrics before canonical normalization and
ensures traceability for each number via:
- ingestion run (`ingestion_id`),
- source catalog (`source_id`),
- lineage reference (`lineage_ref_id`, `location_type=slide`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, Numeric, Text, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class StgSocialMetric(SQLModel, table=True):
    """Staging row extracted from PPTX social/media metric slides."""

    __tablename__ = "stg_social_metrics"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "ingestion_id",
            "platform",
            "metric_name",
            "slide_number",
            name="uq_stg_social_metrics_source_ingestion_metric_slide",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)
    event_id: Optional[int] = Field(default=None, index=True)
    session_id: Optional[int] = Field(default=None, foreign_key="event_sessions.id", index=True)

    slide_number: int = Field(index=True)
    slide_title: Optional[str] = Field(default=None, max_length=400)
    location_value: str = Field(max_length=32)

    platform: str = Field(max_length=120, index=True)
    metric_name: str = Field(max_length=160, index=True)
    metric_value: Decimal = Field(
        sa_column=Column(Numeric(20, 6), nullable=False)
    )
    metric_value_raw: Optional[str] = Field(default=None, max_length=80)
    unit: str = Field(max_length=40)

    evidence_label: str = Field(max_length=200)
    evidence_text: str = Field(sa_column=Column(Text, nullable=False))
    extraction_rule: str = Field(max_length=500)
    session_resolution_finding: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    raw_payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
