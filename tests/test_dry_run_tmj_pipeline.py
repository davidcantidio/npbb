"""Tests for local TMJ dry-run pipeline orchestration script."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.dry_run_tmj_pipeline import main as dry_run_main


def test_dry_run_tmj_pipeline_generates_expected_outputs(tmp_path: Path) -> None:
    """Dry-run script should generate DQ, coverage, report and manifest artifacts."""

    out_dir = tmp_path / "dry_run_out"
    rc = dry_run_main(
        [
            "--out-dir",
            str(out_dir),
            "--fixtures-root",
            "tests/fixtures",
            "--agenda-path",
            "tests/fixtures/agenda/agenda_master_min.yml",
        ]
    )

    assert rc == 0
    dq_report = out_dir / "dq_report.json"
    coverage_report = out_dir / "coverage_report.json"
    report_docx = out_dir / "report.docx"
    manifest = out_dir / "manifest.json"

    assert dq_report.exists()
    assert coverage_report.exists()
    assert report_docx.exists()
    assert manifest.exists()

    dq_payload = json.loads(dq_report.read_text(encoding="utf-8"))
    coverage_payload = json.loads(coverage_report.read_text(encoding="utf-8"))
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))

    assert "summary" in dq_payload
    assert "sections" in dq_payload
    assert "sessions" in coverage_payload
    assert isinstance(coverage_payload["sessions"], list)
    assert manifest_payload["event_id"] == 2025


def test_dry_run_tmj_pipeline_fails_with_clear_message_when_fixture_missing(
    tmp_path: Path,
    capsys,
) -> None:
    """Dry-run should fail fast with actionable message for missing fixture file."""

    out_dir = tmp_path / "dry_run_error"
    rc = dry_run_main(
        [
            "--out-dir",
            str(out_dir),
            "--optin-xlsx",
            str(tmp_path / "missing_optin.xlsx"),
        ]
    )

    captured = capsys.readouterr()
    assert rc == 1
    assert "[ERROR]" in captured.out
    assert "Fixture nao encontrado" in captured.out
