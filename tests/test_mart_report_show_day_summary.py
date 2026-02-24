"""Unit tests for `mart_report_show_day_summary` SQL view."""

from __future__ import annotations

from pathlib import Path
import sqlite3


def _load_sql_file(name: str) -> str:
    """Read SQL file from `reports/sql/marts` folder."""

    sql_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / name
    return sql_path.read_text(encoding="utf-8")


def _create_base_tables(connection: sqlite3.Connection) -> None:
    """Create minimal canonical/registry schema required by show-day summary view."""

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
          source_id TEXT NULL,
          ingressos_validos INTEGER NULL,
          presentes INTEGER NULL
        );

        CREATE TABLE optin_transactions (
          id INTEGER PRIMARY KEY,
          session_id INTEGER NOT NULL,
          source_id TEXT NULL
        );

        CREATE TABLE ticket_sales (
          id INTEGER PRIMARY KEY,
          session_id INTEGER NOT NULL,
          source_id TEXT NULL,
          sold_total INTEGER NULL,
          net_sold_total INTEGER NULL
        );

        CREATE TABLE sources (
          id INTEGER PRIMARY KEY,
          source_id TEXT NOT NULL,
          kind TEXT NOT NULL,
          uri TEXT NOT NULL
        );

        CREATE TABLE ingestions (
          id INTEGER PRIMARY KEY,
          source_pk INTEGER NOT NULL,
          extractor_name TEXT NULL,
          status TEXT NULL,
          started_at TEXT NULL
        );
        """
    )


def test_mart_report_show_day_summary_returns_statuses_by_day_and_ruler() -> None:
    """Show-day summary should expose explicit coverage status for each ruler."""

    with sqlite3.connect(":memory:") as connection:
        _create_base_tables(connection)
        connection.executescript(
            """
            INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
            VALUES
              (1, 100, 'TMJ2025_20251212_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00'),
              (2, 100, 'TMJ2025_20251213_SHOW', 'Show 13/12', 'NOTURNO_SHOW', '2025-12-13', '2025-12-13 20:00:00');

            INSERT INTO attendance_access_control (id, session_id, source_id, ingressos_validos, presentes)
            VALUES
              (10, 1, 'SRC_ACESSO_NOTURNO_20251212_SHOW', 100, 90);

            INSERT INTO optin_transactions (id, session_id, source_id)
            VALUES
              (20, 1, 'SRC_OPTIN_NOTURNO_20251212_SHOW');

            INSERT INTO ticket_sales (id, session_id, source_id, sold_total, net_sold_total)
            VALUES
              (30, 1, 'SRC_VENDAS_NOTURNO_20251212_SHOW', 120, 118);

            INSERT INTO sources (id, source_id, kind, uri)
            VALUES
              (1, 'SRC_ACESSO_NOTURNO_20251213_SHOW', 'pdf', 'file:///access_13.pdf'),
              (2, 'SRC_OPTIN_NOTURNO_20251213_SHOW', 'xlsx', 'file:///optin_13.xlsx');

            INSERT INTO ingestions (id, source_pk, extractor_name, status, started_at)
            VALUES
              (100, 1, 'extract_pdf_access', 'FAILED', '2025-12-11 10:00:00'),
              (101, 2, 'extract_xlsx_optin', 'PARTIAL', '2025-12-11 10:05:00');
            """
        )
        connection.executescript(_load_sql_file("mart_report_show_day_summary.sql"))

        rows = connection.execute(
            """
            SELECT
              dia,
              sessao,
              status_access_control,
              status_optin,
              status_ticket_sales,
              source_ids_access_control,
              source_ids_optin,
              source_ids_ticket_sales,
              observacoes,
              row_rank
            FROM mart_report_show_day_summary
            ORDER BY row_rank
            """
        ).fetchall()

    assert len(rows) == 3

    day_12 = rows[0]
    assert day_12[0] == "2025-12-12"
    assert day_12[2] == "ok"
    assert day_12[3] == "ok"
    assert day_12[4] == "ok"
    assert day_12[5] == "SRC_ACESSO_NOTURNO_20251212_SHOW"
    assert day_12[6] == "SRC_OPTIN_NOTURNO_20251212_SHOW"
    assert day_12[7] == "SRC_VENDAS_NOTURNO_20251212_SHOW"
    assert day_12[8] == ""
    assert day_12[9] == 1

    day_13 = rows[1]
    assert day_13[0] == "2025-12-13"
    assert day_13[2] == "partial"
    assert day_13[3] == "partial"
    assert day_13[4] == "gap"
    assert day_13[5] == "SRC_ACESSO_NOTURNO_20251213_SHOW"
    assert day_13[6] == "SRC_OPTIN_NOTURNO_20251213_SHOW"
    assert day_13[7] == ""
    assert "falta_entradas_validadas" in day_13[8]
    assert "falta_optin_aceitos_recorte" in day_13[8]
    assert "falta_vendidos_total" in day_13[8]
    assert day_13[9] == 2

    day_14 = rows[2]
    assert day_14[0] == "2025-12-14"
    assert day_14[2] == "gap"
    assert day_14[3] == "gap"
    assert day_14[4] == "gap"
    assert "sessao_show_ausente_no_catalogo" in day_14[8]
    assert day_14[9] == 3

