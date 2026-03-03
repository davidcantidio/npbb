"""Canonical fact model for validated attendance (access control).

This fact represents the official attendance ruler derived from access-control
sources (turnstile/validated entries) and must stay separated from:
- ticket sales ruler
- opt-in accepted ruler
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, Numeric
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class FctAttendanceAccessControl(SQLModel, table=True):
    """Canonical attendance fact for validated entries per session.

    Notes:
        - `session_id` links metric to canonical event session.
        - `lineage_ref_id` links metric to source location/evidence.
        - This table should not be used to represent sold tickets or opt-in.
        - `comparecimento_pct` may be loaded either as fraction (0..1) or
          percentage (0..100); reconciliation checks normalize both formats.
    """

    __tablename__ = "attendance_access_control"
    __table_args__ = ({"extend_existing": True},)

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="event_sessions.id")
    source_id: str = Field(max_length=160, foreign_key="sources.source_id")
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestions.id")
    lineage_ref_id: Optional[int] = Field(default=None, foreign_key="lineage_refs.id", index=True)

    ingressos_validos: Optional[int] = None
    presentes: Optional[int] = None
    ausentes: Optional[int] = None
    invalidos: Optional[int] = None
    bloqueados: Optional[int] = None
    comparecimento_pct: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(7, 4), nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
