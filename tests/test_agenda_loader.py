"""Unit tests for master agenda loader and schema validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.sessions import SessionType
from etl.transform.agenda_loader import AgendaMasterError, load_agenda_master


def test_load_default_agenda_master_has_required_session_types() -> None:
    """Bundled YAML agenda should load and expose day/night session types."""

    agenda = load_agenda_master()

    assert agenda.version == 1
    assert len(agenda.sessions) >= 6
    session_types = {session.session_type for session in agenda.sessions}
    assert SessionType.DIURNO_GRATUITO in session_types
    assert SessionType.NOTURNO_SHOW in session_types


def test_load_agenda_master_yaml_validates_required_fields(tmp_path: Path) -> None:
    """Loader should reject YAML entries with missing required fields."""

    path = tmp_path / "agenda_bad.yml"
    path.write_text(
        "\n".join(
            [
                "version: 1",
                "sessions:",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T20:00:00",
                "    type: noturno_show",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(AgendaMasterError, match="name"):
        load_agenda_master(path)


def test_load_agenda_master_rejects_date_datetime_mismatch(tmp_path: Path) -> None:
    """Loader should fail when session_date differs from start_at date."""

    path = tmp_path / "agenda_mismatch.yml"
    path.write_text(
        "\n".join(
            [
                "version: 1",
                "sessions:",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-13T20:00:00",
                "    type: noturno_show",
                "    name: Show deslocado",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(AgendaMasterError, match="inconsistente"):
        load_agenda_master(path)


def test_load_agenda_master_csv_supports_same_schema(tmp_path: Path) -> None:
    """Loader should accept CSV input with required columns."""

    path = tmp_path / "agenda.csv"
    path.write_text(
        "\n".join(
            [
                "event_id,session_date,start_at,type,name,session_key",
                "2025,2025-12-12,2025-12-12T10:00:00,diurno_gratuito,Programacao Diurna 12/12,TMJ2025_DIURNO_12",
                "2025,2025-12-12,2025-12-12T20:00:00,noturno_show,Show 12/12,TMJ2025_SHOW_12",
            ]
        ),
        encoding="utf-8",
    )

    agenda = load_agenda_master(path)
    assert agenda.version == 1
    assert len(agenda.sessions) == 2
    assert agenda.sessions[0].session_type in {
        SessionType.DIURNO_GRATUITO,
        SessionType.NOTURNO_SHOW,
    }


def test_load_agenda_master_rejects_duplicates(tmp_path: Path) -> None:
    """Loader should fail fast when duplicate sessions are present."""

    path = tmp_path / "agenda_dup.yml"
    path.write_text(
        "\n".join(
            [
                "version: 1",
                "sessions:",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T20:00:00",
                "    type: noturno_show",
                "    name: Show 12/12",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T20:00:00",
                "    type: noturno_show",
                "    name: Show 12/12",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(AgendaMasterError, match="duplicada"):
        load_agenda_master(path)
