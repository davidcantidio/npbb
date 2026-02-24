"""Canonical fact model for ticket sales ruler.

This fact stores sold-ticket metrics and must stay separated from:
- validated entries (`attendance_access_control`)
- opt-in accepted transactions (`optin_transactions`)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class FctTicketSales(SQLModel, table=True):
    """Canonical ticket-sales fact for one session/source ingestion.

    Notes:
        - `sold_total` is the official sold ruler for commercial volume.
        - `lineage_ref_id` preserves source location/evidence for audit.
    """

    __tablename__ = "ticket_sales"
    __table_args__ = ({"extend_existing": True},)

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="event_sessions.id", index=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)

    sold_total: Optional[int] = None
    refunded_total: Optional[int] = None
    net_sold_total: Optional[int] = None
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))

