"""Canonical fact model for Eventim opt-in accepted transactions.

This fact stores opt-in transactions as a dedicated ruler slice. It must not
replace validated entries or sold-ticket facts.
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


class FctOptinTransaction(SQLModel, table=True):
    """Canonical opt-in fact by session/source ingestion.

    Notes:
        - `optin_flag` marks accepted/not-accepted for the transaction.
        - `qty` should represent ticket quantity tied to the opt-in row.
        - `lineage_ref_id` ensures traceability to source location/evidence.
    """

    __tablename__ = "optin_transactions"
    __table_args__ = ({"extend_existing": True},)

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="event_sessions.id", index=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)

    purchase_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    optin_flag: Optional[bool] = None
    optin_status: Optional[str] = Field(default=None, max_length=80)
    qty: Optional[int] = None
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))

