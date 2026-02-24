"""ORM model for ETL metric lineage references.

This model stores the minimum anti-hallucination contract fields:
- source identifier
- ingestion run identifier
- source location type/value
- evidence text
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class LineageLocationType(str, Enum):
    """Supported source location domains for lineage references."""

    PAGE = "page"
    SLIDE = "slide"
    SHEET = "sheet"
    RANGE = "range"


class LineageRef(SQLModel, table=True):
    """Lineage reference for one metric evidence record.

    `location_value` must follow canonical format by `location_type`:
    - page: `page:<numero>`
    - slide: `slide:<numero>`
    - sheet: `sheet:<nome>`
    - range: `range:<A1>:<D20>`
    """

    __tablename__ = "lineage_refs"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestions.id", index=True)
    location_type: LineageLocationType = Field(
        sa_column=Column(
            sa.Enum(
                LineageLocationType,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=16,
            ),
            nullable=False,
            index=True,
        )
    )
    location_value: str = Field(max_length=200)
    evidence_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
