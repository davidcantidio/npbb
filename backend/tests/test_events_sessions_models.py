"""Tests for canonical `events` and `event_sessions` dimension models."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

from sqlalchemy import inspect
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.events_sessions import Event, EventSession, EventSessionType


def _make_engine():
    """Create isolated in-memory SQLite engine for model tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_events_sessions_tables_have_required_indexes_and_unique() -> None:
    """Dimension tables should expose required indexes and unique constraints."""
    engine = _make_engine()
    SQLModel.metadata.create_all(engine, tables=[Event.__table__, EventSession.__table__])

    inspector = inspect(engine)
    event_indexes = {idx["name"] for idx in inspector.get_indexes("events")}
    session_indexes = {idx["name"] for idx in inspector.get_indexes("event_sessions")}
    session_uniques = {uq["name"] for uq in inspector.get_unique_constraints("event_sessions")}

    assert any(name.endswith("event_key") for name in event_indexes)
    assert any(name.endswith("event_name") for name in event_indexes)
    assert any(name.endswith("event_id") for name in session_indexes)
    assert any(name.endswith("session_date") for name in session_indexes)
    assert any(name.endswith("session_type") for name in session_indexes)
    assert "uq_event_sessions_session_key" in session_uniques
    assert "uq_event_sessions_event_start_type" in session_uniques


def test_event_session_can_be_persisted_and_linked_to_event() -> None:
    """EventSession rows should persist and link to Event via `event_id`."""
    engine = _make_engine()
    SQLModel.metadata.create_all(engine, tables=[Event.__table__, EventSession.__table__])

    with Session(engine) as session:
        event = Event(
            event_key="TMJ2025",
            event_name="Festival Tamo Junto BB 2025",
            event_start_date=date(2025, 12, 12),
            event_end_date=date(2025, 12, 14),
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        row = EventSession(
            event_id=event.id,
            session_key="TMJ2025_20251213_SHOW",
            session_name="Noturno show - 2025-12-13",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 13),
        )
        session.add(row)
        session.commit()

        stored = session.exec(
            select(EventSession).where(EventSession.session_key == "TMJ2025_20251213_SHOW")
        ).first()
        assert stored is not None
        assert stored.event_id == event.id
        assert stored.session_type == EventSessionType.NOTURNO_SHOW
