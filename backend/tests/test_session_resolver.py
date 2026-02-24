"""Tests for staging-to-session resolver service."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import sys

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.models import EventSession, EventSessionType  # noqa: E402
from app.services.session_resolver import resolve_session_reference  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for resolver tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal event-session table required by resolver."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            EventSession.__table__,
        ],
    )


def test_resolve_session_reference_creates_session_from_raw_fields() -> None:
    """Resolver should create and return session_id when fields are sufficient."""
    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        result = resolve_session_reference(
            session,
            event_id=None,
            raw_session_fields={
                "source_id": "SRC_OPTIN_DOZE",
                "session_name": "Show 12/12",
                "dt_hr_compra": datetime(2025, 12, 12, 19, 0, 0),
            },
        )
        assert result.session_id is not None
        assert result.finding is None

        stored = session.exec(select(EventSession).where(EventSession.id == result.session_id)).first()
        assert stored is not None
        assert stored.session_date == date(2025, 12, 12)
        assert stored.session_type == EventSessionType.NOTURNO_SHOW


def test_resolve_session_reference_returns_finding_when_date_is_missing() -> None:
    """Resolver should return actionable finding when session date cannot be inferred."""
    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        result = resolve_session_reference(
            session,
            event_id=None,
            raw_session_fields={
                "source_id": "SRC_SOCIAL_METRICS",
                "session_name": "Midias e alcance",
            },
        )
        assert result.session_id is None
        assert result.finding is not None
        assert result.finding.code == "SESSION_DATE_MISSING"
        assert "Como corrigir" in result.finding.message


def test_resolve_session_reference_returns_ambiguous_finding() -> None:
    """Resolver should return ambiguous finding when multiple candidates match."""
    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        session.add(
            EventSession(
                session_key="TMJ2025_20251212_SHOW_A",
                session_name="Show A",
                session_type=EventSessionType.NOTURNO_SHOW,
                session_date=date(2025, 12, 12),
            )
        )
        session.add(
            EventSession(
                session_key="TMJ2025_20251212_SHOW_B",
                session_name="Show B",
                session_type=EventSessionType.NOTURNO_SHOW,
                session_date=date(2025, 12, 12),
            )
        )
        session.commit()

        result = resolve_session_reference(
            session,
            event_id=None,
            raw_session_fields={
                "source_id": "SRC_SOCIAL_METRICS_DOZE",
                "session_date": "2025-12-12",
                "session_type": "NOTURNO_SHOW",
            },
        )
        assert result.session_id is None
        assert result.finding is not None
        assert result.finding.code == "SESSION_AMBIGUOUS"
        assert "Como corrigir" in result.finding.message
