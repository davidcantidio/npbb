"""Unit tests for session naming and classification helpers."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import sys

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from core.sessions import SessionType, classify_session, coerce_session_type, normalize_session_name

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.models import EventSession, EventSessionType  # noqa: E402
from app.services.session_resolver import resolve_session_id, resolve_session_reference  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for resolver scenarios."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal table set required by session resolver tests."""

    SQLModel.metadata.create_all(
        engine,
        tables=[EventSession.__table__],
    )


def test_coerce_session_type_accepts_controlled_domain() -> None:
    """Domain coercion accepts aliases and canonical values."""

    assert coerce_session_type("diurno_gratuito") == SessionType.DIURNO_GRATUITO
    assert coerce_session_type("diurno gratuito") == SessionType.DIURNO_GRATUITO
    assert coerce_session_type("NOTURNO_SHOW") == SessionType.NOTURNO_SHOW
    assert coerce_session_type("show") == SessionType.NOTURNO_SHOW
    assert coerce_session_type("outro") == SessionType.OUTRO


def test_coerce_session_type_rejects_invalid_value() -> None:
    """Domain coercion rejects unknown values with actionable error."""

    with pytest.raises(ValueError, match="session_type invalido"):
        coerce_session_type("vip_exclusivo")


def test_classify_session_uses_explicit_field() -> None:
    """Explicit mapping field has priority over heuristics."""

    raw = {
        "session_name": "Festival Tamo Junto",
        "session_type": "diurno_gratuito",
    }
    assert classify_session(raw) == SessionType.DIURNO_GRATUITO


def test_classify_session_uses_master_agenda_override() -> None:
    """Master agenda override must supersede raw text heuristics."""

    raw = {"session_name": "Ativacoes diurnas"}
    assert classify_session(raw, agenda_session_type="noturno_show") == SessionType.NOTURNO_SHOW


def test_classify_session_detects_noturno_show_from_source_id() -> None:
    """Heuristic should classify show sessions from source-id hints."""

    raw = {"source_id": "SRC_PDF_ACESSO_NOTURNO_TREZE"}
    assert classify_session(raw) == SessionType.NOTURNO_SHOW


def test_classify_session_detects_diurno_gratuito_from_text() -> None:
    """Heuristic should classify free daytime sessions from text hints."""

    raw = "Programacao diurna gratuita no parque"
    assert classify_session(raw) == SessionType.DIURNO_GRATUITO


def test_classify_session_returns_outro_for_ambiguous_text() -> None:
    """Ambiguous text containing daytime and show hints must fallback to outro."""

    raw = "Sessao diurna com show especial"
    assert classify_session(raw) == SessionType.OUTRO


def test_normalize_session_name_generates_canonical_noturno_with_date() -> None:
    """Normalization should produce deterministic canonical show name with date."""

    raw = {
        "session_name": "SHOW de Encerramento 12/12",
        "source_id": "SRC_PDF_ACESSO_NOTURNO_DOZE",
    }
    assert normalize_session_name(raw) == "noturno show - 2025-12-12"


def test_normalize_session_name_generates_canonical_diurno() -> None:
    """Normalization should produce deterministic canonical daytime name."""

    raw = {
        "session_name": "Atividades do Diurno Gratuito",
        "session_date": "2025-12-13",
    }
    assert normalize_session_name(raw) == "diurno gratuito - 2025-12-13"


def test_normalize_session_name_handles_empty_input() -> None:
    """Empty values should normalize to a stable fallback name."""

    assert normalize_session_name("   ") == "sessao sem nome"


def test_resolve_session_id_returns_id_for_complete_noturno_payload() -> None:
    """Resolver should return one session_id for complete payload with date/type hints."""

    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        session_id = resolve_session_id(
            session,
            event_id=None,
            raw_session_fields={
                "source_id": "SRC_OPTIN_NOTURNO_DOZE",
                "session_name": "Show 12/12",
                "dt_hr_compra": datetime(2025, 12, 12, 20, 0, 0),
            },
        )
        assert session_id is not None
        created = session.get(EventSession, int(session_id))
        assert created is not None
        assert created.session_type == EventSessionType.NOTURNO_SHOW
        assert created.session_date == date(2025, 12, 12)


def test_resolve_session_id_returns_none_for_incomplete_payload() -> None:
    """Resolver should return None when date cannot be inferred from incomplete input."""

    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        session_id = resolve_session_id(
            session,
            event_id=None,
            raw_session_fields={
                "source_id": "SRC_SOCIAL_METRICS",
                "session_name": "Relatorio de alcance",
            },
        )
        assert session_id is None


def test_resolve_session_reference_returns_ambiguous_finding_without_session_id() -> None:
    """Ambiguous candidates must produce finding and never return a wrong session_id."""

    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        session.add(
            EventSession(
                session_key="TMJ2025_20251213_SHOW_A",
                session_name="Show A",
                session_type=EventSessionType.NOTURNO_SHOW,
                session_date=date(2025, 12, 13),
            )
        )
        session.add(
            EventSession(
                session_key="TMJ2025_20251213_SHOW_B",
                session_name="Show B",
                session_type=EventSessionType.NOTURNO_SHOW,
                session_date=date(2025, 12, 13),
            )
        )
        session.commit()

        result = resolve_session_reference(
            session,
            event_id=None,
            raw_session_fields={
                "source_id": "SRC_SOCIAL_NOTURNO_TREZE",
                "session_date": "2025-12-13",
                "session_type": "NOTURNO_SHOW",
            },
        )
        assert result.session_id is None
        assert result.finding is not None
        assert result.finding.code == "SESSION_AMBIGUOUS"
        assert "Como corrigir" in result.finding.message
