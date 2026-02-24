"""Snapshot tests for DOCX-as-spec rendered markdown artifacts."""

from __future__ import annotations

from pathlib import Path

import yaml

from core.spec.mapping_loader import load_mapping
from core.spec.render_mapping_md import render_mapping_md
from core.spec.render_markdown import build_initial_checklist_rows, render_docx_as_spec_md
from etl.cli_spec import _build_spec
from scripts.run_spec_checks import main as run_spec_checks_main


def _docx_fixture() -> Path:
    """Return fixture DOCX used by snapshot tests."""
    return Path("tests/fixtures/docx/min_template.docx")


def _mapping_fixture() -> Path:
    """Return fixture mapping used by snapshot tests."""
    return Path("tests/fixtures/spec/mapping_min.yml")


def _golden_dir() -> Path:
    """Return golden snapshots directory."""
    return Path("tests/golden/spec")


def _assert_or_update_snapshot(path: Path, content: str, update_snapshots: bool) -> None:
    """Assert snapshot content or update it when flag is enabled."""
    if update_snapshots:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return
    assert path.exists(), f"Snapshot file missing: {path}"
    expected = path.read_text(encoding="utf-8")
    assert content == expected


def _render_checklist_snapshot() -> str:
    """Render checklist markdown snapshot content from DOCX fixture."""
    spec = _build_spec(_docx_fixture())
    return render_docx_as_spec_md(spec)


def _render_mapping_snapshot() -> str:
    """Render mapping markdown snapshot content from fixtures."""
    spec = _build_spec(_docx_fixture())
    checklist = build_initial_checklist_rows(spec)
    mapping = load_mapping(_mapping_fixture())
    return render_mapping_md(checklist, mapping)


def _write_mapping_for_pass_case(path: Path) -> None:
    """Write mapping YAML aligned with min_template headings for pass-case gate tests."""
    payload = {
        "schema_version": "1.0",
        "spec_source": "tests/golden/spec/00_docx_as_spec.md",
        "requirements": [
            {
                "requirement_id": "REQ-CONTEXTO",
                "item_docx": "Contexto do evento",
                "target_field": "event_sessions.session_name",
                "calculation_rule": "MAX(session_name)",
                "sources": [{"source_id": "src_contexto", "location": "docx heading Contexto"}],
                "validations": [
                    {
                        "rule_id": "VAL-CONTEXTO",
                        "rule_type": "not_null",
                        "severity": "error",
                        "expression": "session_name IS NOT NULL",
                    }
                ],
            },
            {
                "requirement_id": "REQ-PUBLICO-SESSAO",
                "item_docx": "Publico por sessao",
                "target_field": "attendance_access_control.entries_validated",
                "calculation_rule": "SUM(entries_validated)",
                "sources": [{"source_id": "src_publico", "location": "tabela fixture"}],
                "validations": [
                    {
                        "rule_id": "VAL-PUBLICO",
                        "rule_type": "reconciliation",
                        "severity": "error",
                        "expression": "entries_validated >= 0",
                    }
                ],
            },
            {
                "requirement_id": "REQ-SHOWS",
                "item_docx": "Shows por dia (12/12, 13/12, 14/12)",
                "target_field": "mart_report_show_day_summary.coverage_status",
                "calculation_rule": "CASE WHEN has_access_control THEN 'OK' ELSE 'GAP' END",
                "sources": [{"source_id": "src_shows", "location": "item obrigatorio"}],
                "validations": [
                    {
                        "rule_id": "VAL-SHOWS",
                        "rule_type": "reconciliation",
                        "severity": "error",
                        "expression": "coverage_status IN ('OK','GAP','INCONSISTENTE')",
                    }
                ],
            },
        ],
        "marts": [
            {
                "mart_name": "mart_report_show_day_summary",
                "grain": "evento_dia_sessao",
                "description": "Resumo de cobertura",
                "requirement_ids": ["REQ-CONTEXTO", "REQ-PUBLICO-SESSAO", "REQ-SHOWS"],
                "output_fields": [
                    {
                        "field": "coverage_status",
                        "source": "public.mart_report_show_day_summary.coverage_status",
                        "rule": "Regra de cobertura",
                    }
                ],
            }
        ],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def test_checklist_markdown_snapshot(update_snapshots: bool) -> None:
    """Checklist markdown output must match golden snapshot."""
    _assert_or_update_snapshot(
        _golden_dir() / "00_docx_as_spec.md",
        _render_checklist_snapshot(),
        update_snapshots,
    )


def test_mapping_markdown_snapshot(update_snapshots: bool) -> None:
    """Mapping markdown output must match golden snapshot."""
    _assert_or_update_snapshot(
        _golden_dir() / "03_requirements_to_schema_mapping.md",
        _render_mapping_snapshot(),
        update_snapshots,
    )


def test_run_spec_checks_updates_snapshots_only_with_explicit_flag(tmp_path: Path) -> None:
    """Local script updates goldens only when `--update-snapshots` flag is provided."""
    docx_path = _docx_fixture()
    mapping_path = tmp_path / "mapping_pass.yml"
    _write_mapping_for_pass_case(mapping_path)
    out_dir = tmp_path / "out"
    golden_dir = tmp_path / "golden"

    rc_no_update = run_spec_checks_main(
        [
            "--docx",
            str(docx_path),
            "--mapping",
            str(mapping_path),
            "--out-dir",
            str(out_dir),
            "--golden-dir",
            str(golden_dir),
            "--required-section",
            "Contexto do evento",
            "--required-section",
            "Publico por sessao",
        ]
    )
    assert rc_no_update == 0
    assert not (golden_dir / "00_docx_as_spec.md").exists()
    assert not (golden_dir / "03_requirements_to_schema_mapping.md").exists()

    rc_update = run_spec_checks_main(
        [
            "--docx",
            str(docx_path),
            "--mapping",
            str(mapping_path),
            "--out-dir",
            str(out_dir),
            "--golden-dir",
            str(golden_dir),
            "--required-section",
            "Contexto do evento",
            "--required-section",
            "Publico por sessao",
            "--update-snapshots",
        ]
    )
    assert rc_update == 0
    assert (golden_dir / "00_docx_as_spec.md").exists()
    assert (golden_dir / "03_requirements_to_schema_mapping.md").exists()
