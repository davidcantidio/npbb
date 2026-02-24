"""Unit tests for pre-sale mart views (`curves` and `ops`)."""

from __future__ import annotations

from pathlib import Path
import sqlite3


def _create_base_tables(connection: sqlite3.Connection) -> None:
    """Create minimal canonical tables required by pre-sale views."""

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

        CREATE TABLE optin_transactions (
          id INTEGER PRIMARY KEY,
          session_id INTEGER NOT NULL,
          purchase_date TEXT NULL,
          purchase_at TEXT NULL,
          ticket_qty INTEGER NULL,
          person_key_hash TEXT NULL
        );
        """
    )


def _load_sql_file(name: str) -> str:
    """Read SQL file from reports/sql/marts directory."""

    sql_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / name
    return sql_path.read_text(encoding="utf-8")


def test_presale_curves_returns_daily_and_cumulative_series() -> None:
    """Curves view should expose daily and cumulative metrics per session/day."""

    with sqlite3.connect(":memory:") as connection:
        _create_base_tables(connection)
        connection.executescript(
            """
            INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
            VALUES
              (1, 100, 'TMJ2025_2025-12-12_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00'),
              (2, 100, 'TMJ2025_2025-12-13_SHOW', 'Show 13/12', 'NOTURNO_SHOW', '2025-12-13', '2025-12-13 20:00:00');

            INSERT INTO optin_transactions (id, session_id, purchase_date, purchase_at, ticket_qty, person_key_hash)
            VALUES
              (1, 1, '2025-10-14', '2025-10-14 09:00:00', 2, 'A'),
              (2, 1, '2025-10-14', '2025-10-14 10:00:00', 1, 'A'),
              (3, 1, '2025-10-15', '2025-10-15 09:00:00', 3, 'B'),
              (4, 1, '2025-10-15', '2025-10-15 11:00:00', 1, 'C'),
              (5, 2, NULL, '2025-10-16 12:00:00', 2, 'D');
            """
        )
        connection.executescript(_load_sql_file("mart_report_presale_curves.sql"))

        rows = connection.execute(
            """
            SELECT
              session_id,
              purchase_day,
              tx_count_day,
              tickets_qty_day,
              buyers_unique_day,
              tickets_qty_cum,
              tx_count_cum,
              metric_type,
              audience_measure,
              row_rank
            FROM mart_report_presale_curves
            ORDER BY row_rank
            """
        ).fetchall()

    assert len(rows) == 3

    assert rows[0] == (1, "2025-10-14", 2, 3, 1, 3, 2, "optin_aceitos", "optin_aceitos", 1)
    assert rows[1] == (1, "2025-10-15", 2, 4, 2, 7, 4, "optin_aceitos", "optin_aceitos", 2)
    assert rows[2] == (2, "2025-10-16", 1, 2, 1, 2, 1, "optin_aceitos", "optin_aceitos", 3)


def test_presale_ops_returns_operational_indicators_per_session() -> None:
    """Ops view should return one row per session with buyer-level indicators."""

    with sqlite3.connect(":memory:") as connection:
        _create_base_tables(connection)
        connection.executescript(
            """
            INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
            VALUES
              (1, 100, 'TMJ2025_2025-12-12_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00'),
              (2, 100, 'TMJ2025_2025-12-13_SHOW', 'Show 13/12', 'NOTURNO_SHOW', '2025-12-13', '2025-12-13 20:00:00'),
              (3, 100, 'TMJ2025_2025-12-14_SHOW', 'Show 14/12', 'NOTURNO_SHOW', '2025-12-14', '2025-12-14 20:00:00');

            INSERT INTO optin_transactions (id, session_id, purchase_date, purchase_at, ticket_qty, person_key_hash)
            VALUES
              (1, 1, '2025-10-14', '2025-10-14 09:00:00', 2, 'A'),
              (2, 1, '2025-10-14', '2025-10-14 10:00:00', 1, 'A'),
              (3, 1, '2025-10-15', '2025-10-15 09:00:00', 3, 'B'),
              (4, 1, '2025-10-15', '2025-10-15 11:00:00', 1, 'C'),
              (5, 2, '2025-10-16', '2025-10-16 12:00:00', 2, NULL);
            """
        )
        connection.executescript(_load_sql_file("mart_report_presale_ops.sql"))

        rows = connection.execute(
            """
            SELECT
              session_id,
              tx_count_total,
              tickets_qty_total,
              buyers_unique_total,
              avg_tickets_per_tx,
              avg_tickets_per_buyer,
              buyers_multi_purchase_count,
              buyers_multi_purchase_pct,
              has_person_key,
              metric_type,
              audience_measure,
              session_rank
            FROM mart_report_presale_ops
            ORDER BY session_rank
            """
        ).fetchall()

    assert len(rows) == 3

    first = rows[0]
    assert first[0] == 1
    assert first[1] == 4
    assert first[2] == 7
    assert first[3] == 3
    assert first[4] == 1.75
    assert first[5] == 2.3333
    assert first[6] == 1
    assert first[7] == 33.3333
    assert first[8] == 1
    assert first[9] == "optin_aceitos"
    assert first[10] == "optin_aceitos"
    assert first[11] == 1

    second = rows[1]
    assert second[0] == 2
    assert second[1] == 1
    assert second[2] == 2
    assert second[3] == 0
    assert second[4] == 2.0
    assert second[5] is None
    assert second[6] == 0
    assert second[7] is None
    assert second[8] == 0
    assert second[9] == "optin_aceitos"
    assert second[10] == "optin_aceitos"
    assert second[11] == 2

    third = rows[2]
    assert third[0] == 3
    assert third[1] == 0
    assert third[2] == 0
    assert third[3] == 0
    assert third[4] is None
    assert third[5] is None
    assert third[6] == 0
    assert third[7] is None
    assert third[8] == 0
    assert third[11] == 3

