"""Canonical dimensions for event and session analytics.

This module defines the canonical dimensional contract used by TMJ ETL and
report marts:
- `events`: event-level dimension
- `event_sessions`: day/session-level dimension

All canonical facts should reference `event_sessions.id` using `session_id`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class EventSessionType(str, Enum):
    """Canonical session type domain for TMJ closures."""

    DIURNO_GRATUITO = "DIURNO_GRATUITO"
    NOTURNO_SHOW = "NOTURNO_SHOW"
    OUTRO = "OUTRO"


class Event(SQLModel, table=True):
    """Canonical event dimension used by report/session entities."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("event_key", name="uq_events_event_key"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    event_key: str = Field(max_length=120, index=True)
    event_name: str = Field(max_length=200, index=True)
    event_start_date: Optional[date] = None
    event_end_date: Optional[date] = None
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )


class EventSession(SQLModel, table=True):
    """Canonical session dimension for event/day/session granularity.

    Notes:
        Facts should reference this table using `session_id`.
    """

    __tablename__ = "event_sessions"
    __table_args__ = (
        UniqueConstraint("session_key", name="uq_event_sessions_session_key"),
        UniqueConstraint(
            "event_id",
            "session_start_at",
            "session_type",
            name="uq_event_sessions_event_start_type",
        ),
        {"extend_existing": True},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="events.id", index=True)

    session_key: str = Field(max_length=120, index=True)
    session_name: str = Field(max_length=200)
    session_type: EventSessionType = Field(index=True)
    session_date: date = Field(index=True)

    session_start_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    session_end_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )
