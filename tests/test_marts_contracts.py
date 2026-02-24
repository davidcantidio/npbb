"""Contract and smoke tests for report mart SQL views.

This suite validates that:
1. every configured `mart_report_*` contract matches actual view columns/types;
2. smoke queries execute without errors for all configured marts;
3. rank/order fields used by report rendering are stable and monotonic.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sqlite3
import sys


def _load_run_views_module():
    """Load `reports/sql/run_views.py` module by file path."""

    module_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "run_views.py"
    spec = importlib.util.spec_from_file_location("tmj_run_views_contracts", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Falha ao carregar reports/sql/run_views.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _create_base_tables(connection: sqlite3.Connection) -> None:
    """Create minimal SQLite schema required by all report mart views."""

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
          presentes INTEGER NULL,
          ausentes INTEGER NULL,
          invalidos INTEGER NULL,
          bloqueados INTEGER NULL
        );

        CREATE TABLE optin_transactions (
          id INTEGER PRIMARY KEY,
          session_id INTEGER NOT NULL,
          source_id TEXT NULL,
          purchase_date TEXT NULL,
          purchase_at TEXT NULL,
          ticket_qty INTEGER NULL,
          person_key_hash TEXT NULL,
          ticket_category_norm TEXT NULL
        );

        CREATE TABLE ticket_sales (
          id INTEGER PRIMARY KEY,
          session_id INTEGER NOT NULL,
          source_id TEXT NULL,
          sold_total INTEGER NULL,
          net_sold_total INTEGER NULL
        );

        CREATE TABLE ticket_category_segment_map (
          id INTEGER PRIMARY KEY,
          ticket_category_norm TEXT NOT NULL,
          segment TEXT NOT NULL
        );

        CREATE TABLE sources (
          id INTEGER PRIMARY KEY,
          source_id TEXT NOT NULL,
          kind TEXT NOT NULL,
          uri TEXT NOT NULL,
          display_name TEXT NULL,
          is_active INTEGER NOT NULL,
          file_sha256 TEXT NULL,
          file_size_bytes INTEGER NULL,
          file_mtime_utc TEXT NULL
        );

        CREATE TABLE ingestions (
          id INTEGER PRIMARY KEY,
          source_pk INTEGER NOT NULL,
          extractor_name TEXT NULL,
          status TEXT NOT NULL,
          started_at TEXT NOT NULL,
          finished_at TEXT NULL,
          records_read INTEGER NULL,
          records_loaded INTEGER NULL,
          notes TEXT NULL,
          error_message TEXT NULL,
          created_at TEXT NOT NULL
        );
        """
    )


def _seed_base_data(connection: sqlite3.Connection) -> None:
    """Insert deterministic sample data used by mart smoke/ordering checks."""

    connection.executescript(
        """
        INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
        VALUES
          (1, 100, 'TMJ2025_2025-12-12_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00'),
          (2, 100, 'TMJ2025_2025-12-13_SHOW', 'Show 13/12', 'NOTURNO_SHOW', '2025-12-13', '2025-12-13 20:00:00'),
          (3, 100, 'TMJ2025_2025-12-14_SHOW', 'Show 14/12', 'NOTURNO_SHOW', '2025-12-14', '2025-12-14 20:00:00');

        INSERT INTO attendance_access_control (id, session_id, source_id, ingressos_validos, presentes, ausentes, invalidos, bloqueados)
        VALUES
          (10, 1, 'SRC_PDF_ACCESS', 100, 90, 10, 2, 1),
          (11, 2, 'SRC_PDF_ACCESS', 50, 40, 10, 1, 0);

        INSERT INTO ticket_category_segment_map (id, ticket_category_norm, segment)
        VALUES
          (1, 'FUNCIONARIOS BB', 'FUNCIONARIO_BB'),
          (2, 'INTEIRA', 'PUBLICO_GERAL');

        INSERT INTO optin_transactions (id, session_id, source_id, purchase_date, purchase_at, ticket_qty, person_key_hash, ticket_category_norm)
        VALUES
          (1, 1, 'SRC_XLSX_OPTIN', '2025-10-14', '2025-10-14 09:00:00', 2, 'A', 'FUNCIONARIOS BB'),
          (2, 1, 'SRC_XLSX_OPTIN', '2025-10-14', '2025-10-14 10:00:00', 1, 'A', 'FUNCIONARIOS BB'),
          (3, 1, 'SRC_XLSX_OPTIN', '2025-10-15', '2025-10-15 09:00:00', 3, 'B', 'INTEIRA'),
          (4, 2, 'SRC_XLSX_OPTIN2', '2025-10-16', '2025-10-16 09:00:00', 2, 'C', 'SEM_MAPEAMENTO');

        INSERT INTO ticket_sales (id, session_id, source_id, sold_total, net_sold_total)
        VALUES
          (20, 1, 'SRC_CSV_VENDAS', 120, 118),
          (21, 2, 'SRC_CSV_VENDAS', 80, 79);

        INSERT INTO sources (id, source_id, kind, uri, display_name, is_active, file_sha256, file_size_bytes, file_mtime_utc)
        VALUES
          (1, 'SRC_XLSX_OPTIN', 'xlsx', 'file:///optin.xlsx', 'optin.xlsx', 1, '', 111, '2025-12-10 09:00:00'),
          (2, 'SRC_XLSX_OPTIN2', 'xlsx', 'file:///optin2.xlsx', 'optin2.xlsx', 1, '', 112, '2025-12-10 09:05:00'),
          (3, 'SRC_PDF_ACCESS', 'pdf', 'file:///access.pdf', 'access.pdf', 1, '', 113, '2025-12-10 09:10:00');

        INSERT INTO ingestions (id, source_pk, extractor_name, status, started_at, finished_at, records_read, records_loaded, notes, error_message, created_at)
        VALUES
          (100, 1, 'extract_xlsx_v1', 'PARTIAL', '2025-12-11 09:00:00', '2025-12-11 09:10:00', 10, 8, 'layout drift', '', '2025-12-11 09:10:00'),
          (101, 1, 'extract_xlsx_v2', 'SUCCESS', '2025-12-11 10:00:00', '2025-12-11 10:10:00', 11, 11, 'ok', '', '2025-12-11 10:10:00'),
          (102, 2, 'extract_xlsx', 'FAILED', '2025-12-11 08:00:00', '2025-12-11 08:05:00', 12, 0, 'schema mismatch', 'missing col', '2025-12-11 08:05:00');
        """
    )


def _prepare_marts_database() -> tuple[sqlite3.Connection, object]:
    """Build an in-memory database with marts applied and return helper module."""

    run_views = _load_run_views_module()
    connection = sqlite3.connect(":memory:")
    _create_base_tables(connection)
    _seed_base_data(connection)

    sql_dir = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts"
    sql_files = run_views.discover_sql_files(sql_dir)
    run_views.apply_sql_files(connection, sql_files)
    return connection, run_views


def test_marts_contracts_match_configured_columns_and_types() -> None:
    """Configured contracts should match actual output schema of all marts."""

    connection, run_views = _prepare_marts_database()
    try:
        contracts_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / "contracts.yml"
        contracts = run_views.load_view_contracts(contracts_path)
        findings = run_views.validate_view_contracts(connection, contracts)
    finally:
        connection.close()

    assert contracts, "expected at least one mart contract"
    assert findings == ()


def test_marts_smoke_queries_execute_and_rank_fields_are_stable() -> None:
    """All marts should execute with smoke queries and stable monotonic rank fields."""

    connection, run_views = _prepare_marts_database()
    try:
        contracts_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / "contracts.yml"
        contracts = run_views.load_view_contracts(contracts_path)
        for view_name in contracts:
            connection.execute(f"SELECT * FROM {view_name} LIMIT 5").fetchall()

        attendance_ranks = [row[0] for row in connection.execute(
            "SELECT session_rank FROM mart_report_attendance_by_session ORDER BY session_rank"
        ).fetchall()]
        curves_ranks = [row[0] for row in connection.execute(
            "SELECT row_rank FROM mart_report_presale_curves ORDER BY row_rank"
        ).fetchall()]
        ops_ranks = [row[0] for row in connection.execute(
            "SELECT session_rank FROM mart_report_presale_ops ORDER BY session_rank"
        ).fetchall()]
        bb_share_ranks = [row[0] for row in connection.execute(
            "SELECT row_rank FROM mart_report_bb_share ORDER BY row_rank"
        ).fetchall()]
        sources_ranks = [row[0] for row in connection.execute(
            "SELECT row_rank FROM mart_report_sources ORDER BY row_rank"
        ).fetchall()]
        show_day_ranks = [row[0] for row in connection.execute(
            "SELECT row_rank FROM mart_report_show_day_summary ORDER BY row_rank"
        ).fetchall()]
    finally:
        connection.close()

    assert attendance_ranks == sorted(attendance_ranks)
    assert curves_ranks == sorted(curves_ranks)
    assert ops_ranks == sorted(ops_ranks)
    assert bb_share_ranks == sorted(bb_share_ranks)
    assert sources_ranks == sorted(sources_ranks)
    assert show_day_ranks == sorted(show_day_ranks)
