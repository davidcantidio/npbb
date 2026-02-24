"""Unit tests for `reports/sql/run_views.py` mart runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sqlite3
import sys


def _load_run_views_module():
    """Load run_views module from file path for isolated unit tests."""

    module_path = Path(__file__).resolve().parents[1] / "reports" / "sql" / "run_views.py"
    spec = importlib.util.spec_from_file_location("tmj_run_views", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Falha ao carregar reports/sql/run_views.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_sql_and_contract(tmp_path: Path, *, wrong_contract: bool = False) -> tuple[Path, Path]:
    """Write minimal SQL/contract files used by runner tests."""

    sql_dir = tmp_path / "marts"
    sql_dir.mkdir(parents=True, exist_ok=True)
    (sql_dir / "001_mart_report_healthcheck.sql").write_text(
        "\n".join(
            [
                "DROP VIEW IF EXISTS mart_report_healthcheck;",
                "CREATE VIEW mart_report_healthcheck AS",
                "SELECT",
                "  CAST('tmj2025_healthcheck' AS TEXT) AS section_key,",
                "  CAST('ok' AS TEXT) AS status;",
            ]
        ),
        encoding="utf-8",
    )

    contracts_path = sql_dir / "contracts.yml"
    if wrong_contract:
        contracts_payload = (
            "version: 1\n"
            "views:\n"
            "  - name: mart_report_healthcheck\n"
            "    columns:\n"
            "      - name: section_key\n"
            "        type: text\n"
            "      - name: status_missing\n"
            "        type: text\n"
        )
    else:
        contracts_payload = (
            "version: 1\n"
            "views:\n"
            "  - name: mart_report_healthcheck\n"
            "    columns:\n"
            "      - name: section_key\n"
            "        type: text\n"
            "      - name: status\n"
            "        type: text\n"
        )
    contracts_path.write_text(contracts_payload, encoding="utf-8")
    return sql_dir, contracts_path


def test_run_view_pipeline_applies_sql_and_validates_contract(tmp_path: Path) -> None:
    """Runner should apply SQL view files and validate expected columns/types."""

    run_views = _load_run_views_module()
    sql_dir, contracts_path = _write_sql_and_contract(tmp_path)
    db_path = tmp_path / "tmj_marts.db"

    summary = run_views.run_view_pipeline(
        db_url=f"sqlite:///{db_path}",
        sql_dir=sql_dir,
        contracts_path=contracts_path,
    )

    assert summary.findings == ()
    assert summary.applied_files == ("001_mart_report_healthcheck.sql",)
    assert summary.validated_views == ("mart_report_healthcheck",)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT section_key, status FROM mart_report_healthcheck"
        ).fetchone()
    assert row == ("tmj2025_healthcheck", "ok")


def test_run_view_pipeline_reports_contract_column_mismatch(tmp_path: Path) -> None:
    """Runner should emit findings when contract columns diverge from view output."""

    run_views = _load_run_views_module()
    sql_dir, contracts_path = _write_sql_and_contract(tmp_path, wrong_contract=True)
    db_path = tmp_path / "tmj_marts.db"

    summary = run_views.run_view_pipeline(
        db_url=f"sqlite:///{db_path}",
        sql_dir=sql_dir,
        contracts_path=contracts_path,
    )

    assert len(summary.findings) == 1
    assert summary.findings[0].code == "VIEW_COLUMNS_MISMATCH"
    assert summary.findings[0].view_name == "mart_report_healthcheck"

