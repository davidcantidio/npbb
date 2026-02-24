"""Persistence model for ETL data-quality check outcomes.

This module stores normalized results produced by the ETL DQ framework so each
`ingestion_id` has auditable quality findings over time.
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


class DQCheckSeverity(str, Enum):
    """Controlled severity domain for persisted DQ results."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DQCheckStatus(str, Enum):
    """Controlled status domain for persisted DQ check execution output."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class DQCheckResult(SQLModel, table=True):
    """Persisted row for one DQ framework check result.

    Args:
        ingestion_id: Ingestion execution identifier under validation.
        source_id: Optional source identifier associated with the finding.
        lineage_ref_id: Optional lineage reference for source location evidence.
        check_id: Stable check identifier.
        severity: Severity level (`info`, `warning`, `error`).
        status: Check status (`pass`, `fail`, `skip`).
        message: Actionable message for operators.
        details_json: Optional JSON payload with evidence/lineage details.
        created_at: UTC creation timestamp.
    """

    __tablename__ = "dq_check_result"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    source_id: Optional[str] = Field(
        default=None,
        foreign_key="sources.source_id",
        max_length=160,
        index=True,
    )
    lineage_ref_id: Optional[int] = Field(
        default=None,
        foreign_key="lineage_refs.id",
        index=True,
    )
    check_id: str = Field(max_length=220, index=True)
    severity: DQCheckSeverity = Field(
        sa_column=Column(
            sa.Enum(
                DQCheckSeverity,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=16,
            ),
            nullable=False,
            index=True,
        )
    )
    status: DQCheckStatus = Field(
        sa_column=Column(
            sa.Enum(
                DQCheckStatus,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
                length=16,
            ),
            nullable=False,
            index=True,
        )
    )
    message: str = Field(max_length=500)
    details_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
