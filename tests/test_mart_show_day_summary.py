"""Tests for show-day summary mart view behavior and contract columns."""

from __future__ import annotations

from pathlib import Path
import sqlite3

import yaml


def _load_sql_file(name: str) -> str:
    """Read SQL file from `reports/sql/marts` directory."""

    sql_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / name
    return sql_path.read_text(encoding="utf-8")


def _load_show_day_contract() -> list[dict[str, str]]:
    """Load show-day summary view contract columns from YAML."""

    path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / "contracts.yml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for view in payload.get("views", []):
        if view.get("name") == "mart_report_show_day_summary":
            return list(view.get("columns", []))
    raise AssertionError("Contrato de mart_report_show_day_summary nao encontrado em contracts.yml")


def _normalize_sql_type(value: str) -> str:
    """Normalize SQL type label for deterministic contract assertion."""

    normalized = " ".join(str(value or "").strip().lower().split())
    aliases = {
        "int": "integer",
        "bigint": "integer",
        "smallint": "integer",
        "varchar": "text",
        "char": "text",
    }
    return aliases.get(normalized, normalized)


def _create_base_tables(connection: sqlite3.Connection) -> None:
    """Create minimal schema needed by show-day summary mart view."""

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


def test_mart_show_day_summary_contract_columns_match_view_output() -> None:
    """View output columns/types should match dedicated contract in `contracts.yml`."""

    contract_columns = _load_show_day_contract()
    expected_names = [str(item["name"]) for item in contract_columns]
    expected_types = [str(item["type"]) for item in contract_columns]

    with sqlite3.connect(":memory:") as connection:
        _create_base_tables(connection)
        connection.executescript(_load_sql_file("mart_report_show_day_summary.sql"))
        rows = connection.execute("PRAGMA table_info('mart_report_show_day_summary')").fetchall()

    actual_names = [str(item[1]) for item in rows]
    actual_types = [str(item[2]) for item in rows]

    assert actual_names == expected_names
    assert [_normalize_sql_type(item) for item in actual_types] == [
        _normalize_sql_type(item) for item in expected_types
    ]


def test_mart_show_day_summary_basic_status_behavior_for_12_and_14() -> None:
    """View should expose explicit status per ruler for show days with missing data."""

    with sqlite3.connect(":memory:") as connection:
        _create_base_tables(connection)
        connection.executescript(
            """
            INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
            VALUES
              (1, 2025, 'TMJ2025_20251212_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00');

            INSERT INTO attendance_access_control (id, session_id, source_id, ingressos_validos, presentes)
            VALUES
              (1, 1, 'SRC_ACESSO_NOTURNO_20251212_SHOW', 100, 90);
            """
        )
        connection.executescript(_load_sql_file("mart_report_show_day_summary.sql"))

        rows = connection.execute(
            """
            SELECT
              dia,
              status_access_control,
              status_optin,
              status_ticket_sales,
              observacoes
            FROM mart_report_show_day_summary
            ORDER BY row_rank
            """
        ).fetchall()

    assert len(rows) == 3

    row_12 = rows[0]
    assert row_12[0] == "2025-12-12"
    assert row_12[1] == "ok"
    assert row_12[2] == "partial"
    assert row_12[3] == "gap"
    assert "falta_optin_aceitos_recorte" in row_12[4]
    assert "falta_vendidos_total" in row_12[4]

    row_14 = rows[2]
    assert row_14[0] == "2025-12-14"
    assert row_14[1] == "gap"
    assert row_14[2] == "gap"
    assert row_14[3] == "gap"
    assert "sessao_show_ausente_no_catalogo" in row_14[4]
