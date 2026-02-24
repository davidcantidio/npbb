"""Unit tests for agenda-master session seed/update service."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.etl_registry import (  # noqa: E402
    IngestionRun,
    IngestionStatus,
    Source,
    SourceKind,
)
from app.models.events_sessions import Event, EventSession  # noqa: E402
from app.services.session_seed_from_agenda import upsert_event_sessions_from_agenda  # noqa: E402
from etl.transform.agenda_loader import load_agenda_master  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for seed tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_tables(engine) -> None:  # noqa: ANN001
    """Create minimal table set used by agenda seed service."""

    SQLModel.metadata.create_all(
        engine,
        tables=[
            Event.__table__,
            EventSession.__table__,
            Source.__table__,
            IngestionRun.__table__,
        ],
    )


def _write_agenda(path: Path, show_name: str) -> Path:
    """Write a minimal agenda master YAML fixture."""

    path.write_text(
        "\n".join(
            [
                "version: 1",
                "sessions:",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T10:00:00-03:00",
                "    type: diurno_gratuito",
                "    name: Programacao Diurna 12/12",
                "    session_key: TMJ2025_20251212_DIURNO",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T20:00:00-03:00",
                "    type: noturno_show",
                f"    name: {show_name}",
                "    session_key: TMJ2025_20251212_SHOW",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_upsert_event_sessions_from_agenda_creates_rows_and_registry_run(tmp_path: Path) -> None:
    """Agenda seed should create sessions and register ingestion audit run."""

    engine = _make_engine()
    _create_tables(engine)
    agenda_path = _write_agenda(tmp_path / "agenda_master.yml", "Show 12/12")
    agenda = load_agenda_master(agenda_path)

    with Session(engine) as session:
        session.add(Event(id=2025, event_key="TMJ2025", event_name="Festival TMJ 2025"))
        session.commit()

        summary = upsert_event_sessions_from_agenda(session, agenda, actor="qa_user")

        assert summary.created_count == 2
        assert summary.updated_count == 0
        assert summary.unchanged_count == 0
        assert len(summary.diffs) == 2

        seeded_rows = session.exec(select(EventSession).order_by(EventSession.session_start_at)).all()
        assert len(seeded_rows) == 2

        source = session.exec(select(Source)).first()
        assert source is not None
        assert source.kind == SourceKind.CONFIG

        run = session.get(IngestionRun, summary.ingestion_id)
        assert run is not None
        assert run.status == IngestionStatus.SUCCESS
        notes = json.loads(run.notes or "{}")
        assert notes["actor"] == "qa_user"
        assert notes["created"] == 2
        assert notes["updated"] == 0


def test_upsert_event_sessions_from_agenda_is_idempotent(tmp_path: Path) -> None:
    """Running seed twice with same agenda should not duplicate rows."""

    engine = _make_engine()
    _create_tables(engine)
    agenda_path = _write_agenda(tmp_path / "agenda_master.yml", "Show 12/12")
    agenda = load_agenda_master(agenda_path)

    with Session(engine) as session:
        session.add(Event(id=2025, event_key="TMJ2025", event_name="Festival TMJ 2025"))
        session.commit()

        first = upsert_event_sessions_from_agenda(session, agenda, actor="seed_bot")
        second = upsert_event_sessions_from_agenda(session, agenda, actor="seed_bot")

        assert first.created_count == 2
        assert second.created_count == 0
        assert second.updated_count == 0
        assert second.unchanged_count == 2

        rows = session.exec(select(EventSession)).all()
        assert len(rows) == 2


def test_upsert_event_sessions_from_agenda_tracks_updates_with_diff(tmp_path: Path) -> None:
    """When agenda changes session name, service should update row and emit field diff."""

    engine = _make_engine()
    _create_tables(engine)

    first_path = _write_agenda(tmp_path / "agenda_v1.yml", "Show 12/12")
    second_path = _write_agenda(tmp_path / "agenda_v2.yml", "Show 12/12 - Atualizado")

    first_agenda = load_agenda_master(first_path)
    second_agenda = load_agenda_master(second_path)

    with Session(engine) as session:
        session.add(Event(id=2025, event_key="TMJ2025", event_name="Festival TMJ 2025"))
        session.commit()

        upsert_event_sessions_from_agenda(session, first_agenda, actor="planner")
        summary = upsert_event_sessions_from_agenda(session, second_agenda, actor="planner")

        assert summary.created_count == 0
        assert summary.updated_count == 1
        assert summary.unchanged_count == 1
        updated = [item for item in summary.diffs if item.action == "updated"]
        assert len(updated) == 1
        assert any(change.field == "session_name" for change in updated[0].changes)

        show_row = session.exec(
            select(EventSession).where(EventSession.session_key == "TMJ2025_20251212_SHOW")
        ).first()
        assert show_row is not None
        assert show_row.session_name == "Show 12/12 - Atualizado"
