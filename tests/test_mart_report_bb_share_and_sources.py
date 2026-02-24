"""Unit tests for `mart_report_bb_share` and `mart_report_sources` SQL views."""

from __future__ import annotations

from pathlib import Path
import sqlite3


def _load_sql_file(name: str) -> str:
    """Read SQL file from `reports/sql/marts` folder."""

    sql_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "marts" / name
    return sql_path.read_text(encoding="utf-8")


def _create_bb_share_tables(connection: sqlite3.Connection) -> None:
    """Create minimal tables required by bb-share mart view."""

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
          source_id TEXT NULL,
          ticket_category_norm TEXT NULL,
          ticket_qty INTEGER NULL,
          person_key_hash TEXT NULL
        );

        CREATE TABLE ticket_category_segment_map (
          id INTEGER PRIMARY KEY,
          ticket_category_norm TEXT NOT NULL,
          segment TEXT NOT NULL
        );
        """
    )


def _create_sources_tables(connection: sqlite3.Connection) -> None:
    """Create minimal tables required by sources mart view."""

    connection.executescript(
        """
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


def test_mart_report_bb_share_returns_canonical_segments_with_percentages() -> None:
    """BB share view should return canonical segments and opt-in ruler labels."""

    with sqlite3.connect(":memory:") as connection:
        _create_bb_share_tables(connection)
        connection.executescript(
            """
            INSERT INTO event_sessions (id, event_id, session_key, session_name, session_type, session_date, session_start_at)
            VALUES
              (1, 100, 'TMJ2025_2025-12-12_SHOW', 'Show 12/12', 'NOTURNO_SHOW', '2025-12-12', '2025-12-12 21:00:00');

            INSERT INTO ticket_category_segment_map (id, ticket_category_norm, segment)
            VALUES
              (1, 'FUNCIONARIOS BB', 'FUNCIONARIO_BB'),
              (2, 'INTEIRA', 'PUBLICO_GERAL');

            INSERT INTO optin_transactions (id, session_id, source_id, ticket_category_norm, ticket_qty, person_key_hash)
            VALUES
              (1, 1, 'SRC_XLSX_1', 'FUNCIONARIOS BB', 2, 'A'),
              (2, 1, 'SRC_XLSX_1', 'INTEIRA', 3, 'B'),
              (3, 1, 'SRC_XLSX_2', 'SEM_MAPEAMENTO', 1, 'C');
            """
        )
        connection.executescript(_load_sql_file("mart_report_bb_share.sql"))

        rows = connection.execute(
            """
            SELECT
              segment_canonical,
              tickets_qty,
              tickets_qty_total,
              share_pct,
              metric_type,
              audience_measure,
              source_ids
            FROM mart_report_bb_share
            WHERE session_id = 1
            ORDER BY segment_canonical
            """
        ).fetchall()

    assert len(rows) == 3
    assert rows[0] == ("DESCONHECIDO", 1, 6, 16.6667, "optin_aceitos", "optin_aceitos", "SRC_XLSX_2")
    assert rows[1] == ("FUNCIONARIO_BB", 2, 6, 33.3333, "optin_aceitos", "optin_aceitos", "SRC_XLSX_1")
    assert rows[2] == ("PUBLICO_GERAL", 3, 6, 50.0, "optin_aceitos", "optin_aceitos", "SRC_XLSX_1")


def test_mart_report_sources_returns_sources_with_latest_ingestion_status() -> None:
    """Sources view should expose latest run status and methodological notes."""

    with sqlite3.connect(":memory:") as connection:
        _create_sources_tables(connection)
        connection.executescript(
            """
            INSERT INTO sources (id, source_id, kind, uri, display_name, is_active, file_sha256, file_size_bytes, file_mtime_utc)
            VALUES
              (1, 'SRC_PDF_ACESSO', 'pdf', 'file:///acesso.pdf', 'acesso.pdf', 1, '', 100, '2025-12-10 10:00:00'),
              (2, 'SRC_XLSX_OPTIN', 'xlsx', 'file:///optin.xlsx', 'optin.xlsx', 1, '', 120, '2025-12-10 10:05:00'),
              (3, 'SRC_PPTX_SOCIAL', 'pptx', 'file:///social.pptx', 'social.pptx', 1, '', 140, '2025-12-10 10:10:00');

            INSERT INTO ingestions (id, source_pk, extractor_name, status, started_at, finished_at, records_read, records_loaded, notes, error_message, created_at)
            VALUES
              (10, 1, 'extract_pdf_v1', 'PARTIAL', '2025-12-11 09:00:00', '2025-12-11 09:10:00', 80, 70, 'layout drift', '', '2025-12-11 09:10:00'),
              (11, 1, 'extract_pdf_v2', 'SUCCESS', '2025-12-11 10:00:00', '2025-12-11 10:10:00', 85, 85, 'ok', '', '2025-12-11 10:10:00'),
              (12, 2, 'extract_xlsx', 'FAILED', '2025-12-11 08:00:00', '2025-12-11 08:05:00', 100, 0, 'schema mismatch', 'missing column', '2025-12-11 08:05:00');
            """
        )
        connection.executescript(_load_sql_file("mart_report_sources.sql"))

        rows = connection.execute(
            """
            SELECT
              source_id,
              latest_ingestion_id,
              latest_status,
              limitation_note,
              evidence_note,
              audience_measure,
              row_rank
            FROM mart_report_sources
            ORDER BY row_rank
            """
        ).fetchall()

    assert len(rows) == 3

    first = rows[0]
    assert first[0] == "SRC_PDF_ACESSO"
    assert first[1] == 11
    assert first[2] == "SUCCESS"
    assert "sem falha critica" in first[3].lower()
    assert first[4] == "evidence: source_id + latest_ingestion_id"
    assert first[5] == "nao_aplicavel"
    assert first[6] == 1

    second = rows[1]
    assert second[0] == "SRC_PPTX_SOCIAL"
    assert second[1] is None
    assert second[2] == ""
    assert "sem execucao de ingestao" in second[3].lower()
    assert second[4] == "evidence: source_id"
    assert second[5] == "nao_aplicavel"
    assert second[6] == 2

    third = rows[2]
    assert third[0] == "SRC_XLSX_OPTIN"
    assert third[1] == 12
    assert third[2] == "FAILED"
    assert "falhou" in third[3].lower()
    assert third[4] == "evidence: source_id + latest_ingestion_id"
    assert third[5] == "nao_aplicavel"
    assert third[6] == 3

