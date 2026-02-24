"""Unit tests for `dq:run` CLI scaffold."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import sys

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from etl.validate import cli_dq  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for CLI tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_registry_tables(engine) -> None:  # noqa: ANN001
    """Create minimum ETL registry tables required by `dq:run` checks."""

    SQLModel.metadata.create_all(
        engine,
        tables=[Source.__table__, IngestionRun.__table__],
    )


def _create_event_sessions_table(engine) -> None:  # noqa: ANN001
    """Create minimal `event_sessions` table used by coverage evaluator."""

    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE event_sessions (
              id INTEGER PRIMARY KEY,
              event_id INTEGER NULL,
              session_key TEXT NOT NULL,
              session_name TEXT NOT NULL,
              session_type TEXT NOT NULL,
              session_date TEXT NOT NULL,
              session_start_at TEXT NULL,
              session_end_at TEXT NULL,
              source_of_truth_source_id TEXT NULL,
              created_at TEXT NULL,
              updated_at TEXT NULL
            );
            """
        )


def _seed_ingestion(engine, *, status: IngestionStatus) -> int:  # noqa: ANN001
    """Insert one source and one ingestion run returning run id."""

    with Session(engine) as session:
        source = Source(source_id="SRC_DQ_TEST", kind=SourceKind.XLSX, uri="file:///tmp/a.xlsx")
        session.add(source)
        session.commit()
        session.refresh(source)

        run = IngestionRun(
            source_pk=int(source.id),
            status=status,
            extractor_name="extract_xlsx_optin",
            notes="seed",
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return int(run.id)


def test_dq_run_cli_generates_json_markdown_and_exit_code_zero_for_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI should generate JSON/Markdown and return zero for successful checks."""

    engine = _make_engine()
    _create_registry_tables(engine)
    ingestion_id = _seed_ingestion(engine, status=IngestionStatus.SUCCESS)
    monkeypatch.setattr(cli_dq, "engine", engine)

    out_json = tmp_path / "dq.json"
    out_md = tmp_path / "dq.md"
    rc = cli_dq.main(
        [
            "dq:run",
            "--ingestion-id",
            str(ingestion_id),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ]
    )

    assert rc == 0
    assert out_json.exists()
    assert out_md.exists()
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["ingestion_id"] == ingestion_id
    assert payload["summary"]["fail"] == 0
    assert "dq.ingestion_exists" in {row["check_id"] for row in payload["results"]}
    assert "sections" in payload
    assert "errors" in payload["sections"]
    assert "warnings" in payload["sections"]
    assert "inconsistencies" in payload["sections"]
    assert "gaps_by_dataset" in payload["sections"]
    assert "alerts" in payload
    assert isinstance(payload["alerts"], list)


def test_dq_run_cli_returns_non_zero_when_ingestion_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI should fail with error severity when ingestion run does not exist."""

    engine = _make_engine()
    _create_registry_tables(engine)
    monkeypatch.setattr(cli_dq, "engine", engine)

    out_json = tmp_path / "dq_missing.json"
    rc = cli_dq.main(
        [
            "dq:run",
            "--ingestion-id",
            "999",
            "--out-json",
            str(out_json),
        ]
    )

    assert rc == 1
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    by_id = {row["check_id"]: row for row in payload["results"]}
    assert by_id["dq.ingestion_exists"]["status"] == "fail"
    assert by_id["dq.ingestion_exists"]["severity"] == "error"
    assert "alerts" in payload
    assert isinstance(payload["alerts"], list)


def test_dq_run_cli_fail_on_warning_blocks_partial_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI should return non-zero when `fail-on=warning` and status check warns."""

    engine = _make_engine()
    _create_registry_tables(engine)
    ingestion_id = _seed_ingestion(engine, status=IngestionStatus.PARTIAL)
    monkeypatch.setattr(cli_dq, "engine", engine)

    out_json = tmp_path / "dq_partial.json"
    rc = cli_dq.main(
        [
            "dq:run",
            "--ingestion-id",
            str(ingestion_id),
            "--out-json",
            str(out_json),
            "--fail-on",
            "warning",
        ]
    )

    assert rc == 1
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    by_id = {row["check_id"]: row for row in payload["results"]}
    assert by_id["dq.ingestion_status"]["severity"] == "warning"
    assert by_id["dq.ingestion_status"]["status"] == "fail"
    assert any(item["code"] == "ALERT_PARTIAL_INGESTION" for item in payload["alerts"])


def test_dq_run_cli_generates_request_list_outputs_from_show_gaps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI should generate Markdown/CSV request list from show coverage gaps."""

    engine = _make_engine()
    _create_registry_tables(engine)
    _create_event_sessions_table(engine)
    ingestion_id = _seed_ingestion(engine, status=IngestionStatus.SUCCESS)
    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO event_sessions (
              id,
              event_id,
              session_key,
              session_name,
              session_type,
              session_date,
              session_start_at
            ) VALUES (
              1,
              2025,
              'TMJ2025_20251212_SHOW',
              'Show 12/12',
              'NOTURNO_SHOW',
              '2025-12-12',
              '2025-12-12 21:00:00'
            );
            """
        )

    monkeypatch.setattr(cli_dq, "engine", engine)
    out_request_md = tmp_path / "request_list.md"
    out_request_csv = tmp_path / "request_list.csv"
    rc = cli_dq.main(
        [
            "dq:run",
            "--ingestion-id",
            str(ingestion_id),
            "--event-id",
            "2025",
            "--out-request-md",
            str(out_request_md),
            "--out-request-csv",
            str(out_request_csv),
        ]
    )

    assert rc == 0
    assert out_request_md.exists()
    assert out_request_csv.exists()

    markdown = out_request_md.read_text(encoding="utf-8")
    assert "Lista Do Que Pedir" in markdown
    assert "TMJ2025_20251212_SHOW" in markdown
    assert "access_control" in markdown
    assert "ticket_sales" in markdown

    rows = list(csv.DictReader(io.StringIO(out_request_csv.read_text(encoding="utf-8"))))
    datasets = {row["dataset"] for row in rows}
    assert datasets == {"access_control", "ticket_sales"}


def test_run_show_coverage_report_writes_json_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coverage helper should persist JSON artifact with contract version."""

    engine = _make_engine()
    _create_registry_tables(engine)
    _create_event_sessions_table(engine)
    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO event_sessions (
              id,
              event_id,
              session_key,
              session_name,
              session_type,
              session_date,
              session_start_at
            ) VALUES (
              1,
              2025,
              'TMJ2025_20251212_SHOW',
              'Show 12/12',
              'NOTURNO_SHOW',
              '2025-12-12',
              '2025-12-12 21:00:00'
            );
            """
        )

    monkeypatch.setattr(cli_dq, "engine", engine)
    out_json = tmp_path / "coverage_report.json"
    payload = cli_dq.run_show_coverage_report(event_id=2025, out_json=out_json)

    assert out_json.exists()
    assert payload["event_id"] == 2025
    assert payload["contract_version"] >= 1
    assert "sessions" in payload

    persisted = json.loads(out_json.read_text(encoding="utf-8"))
    assert persisted["contract_version"] == payload["contract_version"]
