"""Unit tests for `mart_report_attendance_by_session` SQL view."""

from __future__ import annotations

from pathlib import Path
import sqlite3


def _create_base_tables(connection: sqlite3.Connection) -> None:
    """Create minimal canonical tables required by attendance mart view."""

    connection.executescript(
        """
        CREATE TABLE event_sessions (
          id INTEGER PRIMARY KEY,
          event_id INTEGER NULL,
          session_key TEXT NOT NULL,
          session_name TEXT NOT NULL,
          session_type TEXT NOT NULL,
          session_date TEXT NOT NULL,
          session_start_at TEXT NULL
        );

        CREATE TABLE attendance_access_control (
          id INTEGER PRIMARY KEY,
          session_id INTEGER NOT NULL,
          ingressos_validos INTEGER NULL,
          presentes INTEGER NULL,
          ausentes INTEGER NULL,
          invalidos INTEGER NULL,
          bloqueados INTEGER NULL
        );
        """
    )


def test_attendance_view_returns_one_row_per_session_and_comparecimento() -> None:
    """View should aggregate attendance by session and expose ruler labels."""

    sql_path = (
        Path(__file__).resolve().parents[1]
        / "reports"
        / "sql"
        / "marts"
        / "mart_report_attendance_by_session.sql"
    )
    script = sql_path.read_text(encoding="utf-8")

    with sqlite3.connect(":memory:") as connection:
        _create_base_tables(connection)
        connection.executescript(
            """
            INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
            VALUES
              (1, 100, 'TMJ2025_2025-12-12_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00'),
              (2, 100, 'TMJ2025_2025-12-13_SHOW', 'Show 13/12', 'NOTURNO_SHOW', '2025-12-13', '2025-12-13 20:00:00');

            INSERT INTO attendance_access_control (id, session_id, ingressos_validos, presentes, ausentes, invalidos, bloqueados)
            VALUES
              (10, 1, 100, 80, 20, 2, 1),
              (11, 1, 20, 18, 2, 0, 0);
            """
        )
        connection.executescript(script)

        rows = connection.execute(
            """
            SELECT
              session_id,
              ingressos_validos,
              presentes,
              ausentes,
              comparecimento_pct,
              metric_type,
              audience_measure,
              session_rank
            FROM mart_report_attendance_by_session
            ORDER BY session_rank
            """
        ).fetchall()

    assert len(rows) == 2

    first = rows[0]
    assert first[0] == 1
    assert first[1] == 120
    assert first[2] == 98
    assert first[3] == 22
    assert first[4] == 81.6667
    assert first[5] == "entradas_validadas"
    assert first[6] == "entradas_validadas"
    assert first[7] == 1

    second = rows[1]
    assert second[0] == 2
    assert second[1] == 0
    assert second[2] == 0
    assert second[3] == 0
    assert second[4] is None
    assert second[5] == "entradas_validadas"
    assert second[6] == "entradas_validadas"
    assert second[7] == 2

