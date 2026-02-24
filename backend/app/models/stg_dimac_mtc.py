"""Staging models for DIMAC/MTC PDF metric extraction (gap-aware).

These tables persist extracted metric candidates with ingestion and lineage
traceability. A candidate can be:
- `ok`: parsed metric with evidence and lineage reference
- `gap`: missing/invalid evidence or value, explicitly recorded for audit
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, Numeric, Text, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class MetricExtractionStatus(str, Enum):
    """Extraction status domain for DIMAC/MTC staged metrics."""

    OK = "ok"
    GAP = "gap"


class StgDimacMetric(SQLModel, table=True):
    """Staging row extracted from DIMAC PDF metrics."""

    __tablename__ = "stg_dimac_metrics"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "ingestion_id",
            "metric_key",
            name="uq_stg_dimac_source_ingestion_metric",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: Optional[int] = Field(default=None, foreign_key="lineage_refs.id", index=True)

    metric_key: str = Field(max_length=200, index=True)
    metric_label: Optional[str] = Field(default=None, max_length=200)
    metric_value: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(20, 6), nullable=True),
    )
    metric_value_raw: Optional[str] = Field(default=None, max_length=120)
    unit: str = Field(max_length=40)
    status: MetricExtractionStatus = Field(
        sa_column=Column(
            sa.Enum(
                MetricExtractionStatus,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=8,
            ),
            nullable=False,
            index=True,
        )
    )
    gap_reason: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    pdf_page: Optional[int] = Field(default=None, index=True)
    location_value: Optional[str] = Field(default=None, max_length=40)
    evidence_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    extraction_rule: str = Field(max_length=500)

    raw_payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))


class StgMtcMetric(SQLModel, table=True):
    """Staging row extracted from MTC PDF metrics."""

    __tablename__ = "stg_mtc_metrics"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "ingestion_id",
            "metric_key",
            name="uq_stg_mtc_source_ingestion_metric",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: Optional[int] = Field(default=None, foreign_key="lineage_refs.id", index=True)

    metric_key: str = Field(max_length=200, index=True)
    metric_label: Optional[str] = Field(default=None, max_length=200)
    metric_value: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(20, 6), nullable=True),
    )
    metric_value_raw: Optional[str] = Field(default=None, max_length=120)
    unit: str = Field(max_length=40)
    status: MetricExtractionStatus = Field(
        sa_column=Column(
            sa.Enum(
                MetricExtractionStatus,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=8,
            ),
            nullable=False,
            index=True,
        )
    )
    gap_reason: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    pdf_page: Optional[int] = Field(default=None, index=True)
    location_value: Optional[str] = Field(default=None, max_length=40)
    evidence_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    extraction_rule: str = Field(max_length=500)

    raw_payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
