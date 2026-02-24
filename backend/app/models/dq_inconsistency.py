"""Persistence model for cross-source metric inconsistencies.

This table stores DQ findings classified as `INCONSISTENTE` when the same
metric key has conflicting values across distinct sources.
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


class DQInconsistencyStatus(str, Enum):
    """Controlled status domain for cross-source inconsistency records."""

    INCONSISTENTE = "inconsistente"


class DQInconsistencySeverity(str, Enum):
    """Controlled severity domain for inconsistency findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DQInconsistency(SQLModel, table=True):
    """Persisted row for one cross-source inconsistency finding.

    Args:
        ingestion_id: Ingestion execution identifier under analysis.
        check_id: Stable checker identifier that produced this row.
        dataset_id: Dataset label used by the cross-source check.
        metric_key: Metric key with conflicting values.
        unit: Optional metric unit (`percent`, `count`, etc.).
        status: Controlled status (`inconsistente`).
        severity: Controlled severity (`info`, `warning`, `error`).
        values_json: JSON payload with values grouped by source.
        sources_json: JSON array with involved source IDs.
        lineage_refs_json: Optional JSON array with lineage reference IDs.
        evidence_json: Optional JSON payload with additional evidence.
        suggested_action: Actionable operator instruction.
        created_at: UTC creation timestamp.
    """

    __tablename__ = "dq_inconsistency"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    check_id: str = Field(max_length=220, index=True)
    dataset_id: str = Field(max_length=120, index=True)
    metric_key: str = Field(max_length=220, index=True)
    unit: Optional[str] = Field(default=None, max_length=40)
    status: DQInconsistencyStatus = Field(
        sa_column=Column(
            sa.Enum(
                DQInconsistencyStatus,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=16,
            ),
            nullable=False,
            index=True,
        )
    )
    severity: DQInconsistencySeverity = Field(
        sa_column=Column(
            sa.Enum(
                DQInconsistencySeverity,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=16,
            ),
            nullable=False,
            index=True,
        )
    )
    values_json: str = Field(sa_column=Column(Text, nullable=False))
    sources_json: str = Field(sa_column=Column(Text, nullable=False))
    lineage_refs_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    evidence_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    suggested_action: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))

