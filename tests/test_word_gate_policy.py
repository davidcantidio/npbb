"""Unit tests for report publication gate policy."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from reports.word import (
    evaluate_report_gate,
    load_report_gate_policy,
    merge_show_coverage_gaps,
)


def _write_policy(path: Path, content: str) -> Path:
    """Write temporary gate policy YAML fixture."""

    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_evaluate_report_gate_blocks_on_critical_gap_token(tmp_path: Path) -> None:
    """Gate should block when critical GAP token is present and policy blocks output."""

    policy_path = _write_policy(
        tmp_path / "gate_block.yml",
        """
        version: 1
        block:
          enabled: true
          min_error_findings: 0
          critical_statuses: [GAP, INCONSISTENTE]
          critical_tokens: [show_14]
        partial:
          enabled: true
          statuses: [GAP, INCONSISTENTE]
          min_findings: 1
          banner_text: "PARCIAL"
        output:
          allow_partial_on_block: false
        """,
    )
    dq_report = {
        "summary": {"error": 0},
        "sections": {
            "gaps_by_dataset": {
                "show_14_access_control": [
                    {"message": "Sem fonte de controle de acesso"}
                ]
            }
        },
    }

    decision = evaluate_report_gate(dq_report, load_report_gate_policy(policy_path))
    assert decision.status == "block"
    assert decision.should_generate_output is False
    assert any("show_14_access_control" in blocker for blocker in decision.blockers)


def test_evaluate_report_gate_downgrades_to_partial_when_policy_allows(tmp_path: Path) -> None:
    """Gate should return partial when blocking finding exists but partial-on-block is enabled."""

    policy_path = _write_policy(
        tmp_path / "gate_partial.yml",
        """
        version: 1
        block:
          enabled: true
          min_error_findings: 0
          critical_statuses: [GAP]
          critical_tokens: [show_12]
        partial:
          enabled: true
          statuses: [GAP]
          min_findings: 1
          banner_text: "PARCIAL: revisar gaps"
        output:
          allow_partial_on_block: true
        """,
    )
    dq_report = {
        "summary": {"error": 0},
        "sections": {
            "gaps_by_dataset": {
                "show_12_access_control": [
                    {"message": "Sem arquivo oficial"}
                ]
            }
        },
    }

    decision = evaluate_report_gate(dq_report, load_report_gate_policy(policy_path))
    assert decision.status == "partial"
    assert decision.should_generate_output is True
    assert decision.status_note == "PARCIAL: revisar gaps"


def test_evaluate_report_gate_allows_when_no_blockers_or_partials(tmp_path: Path) -> None:
    """Gate should allow output when report has no GAP/INCONSISTENTE findings."""

    policy_path = _write_policy(
        tmp_path / "gate_allow.yml",
        """
        version: 1
        block:
          enabled: true
          min_error_findings: 1
          critical_statuses: [GAP, INCONSISTENTE]
          critical_tokens: [show_12, show_14]
        partial:
          enabled: true
          statuses: [GAP, INCONSISTENTE]
          min_findings: 1
          banner_text: "PARCIAL"
        output:
          allow_partial_on_block: false
        """,
    )
    dq_report = {
        "summary": {"error": 0},
        "sections": {
            "inconsistencies": [],
            "gaps_by_dataset": {},
        },
    }

    decision = evaluate_report_gate(dq_report, load_report_gate_policy(policy_path))
    assert decision.status == "allow"
    assert decision.should_generate_output is True


def test_evaluate_report_gate_marks_partial_for_critical_show_coverage_when_allowed(
    tmp_path: Path,
) -> None:
    """Gate should mark partial when show coverage is critical and policy allows partial."""

    policy_path = _write_policy(
        tmp_path / "gate_show_partial.yml",
        """
        version: 1
        block:
          enabled: true
          min_error_findings: 999
          critical_statuses: [GAP, INCONSISTENTE]
          critical_tokens: [unused]
        partial:
          enabled: true
          statuses: [GAP, INCONSISTENTE]
          min_findings: 1
          banner_text: "PARCIAL: show coverage critico"
        output:
          allow_partial_on_block: true
        show_coverage:
          enabled: true
          session_type: NOTURNO_SHOW
          critical_dataset: access_control
          critical_statuses: [GAP]
          required_placeholders: [SHOW__COVERAGE__TABLE, GAPS__SUMMARY__TEXT]
        """,
    )
    coverage_report = {
        "sessions": [
            {
                "session_key": "TMJ2025_20251214_SHOW",
                "session_date": "2025-12-14",
                "session_type": "NOTURNO_SHOW",
                "observed_datasets": ["optin"],
                "partial_datasets": [],
                "missing_datasets": ["access_control", "ticket_sales"],
            }
        ]
    }

    decision = evaluate_report_gate(
        {"summary": {"error": 0}, "sections": {"gaps_by_dataset": {}}},
        load_report_gate_policy(policy_path),
        coverage_report=coverage_report,
        template_placeholders=("SHOW__COVERAGE__TABLE", "GAPS__SUMMARY__TEXT"),
    )

    assert decision.status == "partial"
    assert decision.should_generate_output is True
    assert any("SHOW_COVERAGE_CRITICO" in finding for finding in decision.partial_findings)


def test_evaluate_report_gate_blocks_when_required_show_placeholders_are_missing(
    tmp_path: Path,
) -> None:
    """Gate should block if critical show coverage fails and required placeholders are absent."""

    policy_path = _write_policy(
        tmp_path / "gate_show_missing_placeholders.yml",
        """
        version: 1
        block:
          enabled: true
          min_error_findings: 0
          critical_statuses: [GAP]
          critical_tokens: [show]
        partial:
          enabled: true
          statuses: [GAP]
          min_findings: 1
          banner_text: "PARCIAL"
        output:
          allow_partial_on_block: true
        show_coverage:
          enabled: true
          session_type: NOTURNO_SHOW
          critical_dataset: access_control
          critical_statuses: [GAP]
          required_placeholders: [SHOW__COVERAGE__TABLE, GAPS__SUMMARY__TEXT]
        """,
    )
    coverage_report = {
        "sessions": [
            {
                "session_key": "TMJ2025_20251212_SHOW",
                "session_date": "2025-12-12",
                "session_type": "NOTURNO_SHOW",
                "observed_datasets": [],
                "partial_datasets": [],
                "missing_datasets": ["access_control"],
            }
        ]
    }

    decision = evaluate_report_gate(
        {"summary": {"error": 0}, "sections": {"gaps_by_dataset": {}}},
        load_report_gate_policy(policy_path),
        coverage_report=coverage_report,
        template_placeholders=("FONTES__SUMMARY__TEXT",),
    )

    assert decision.status == "block"
    assert decision.should_generate_output is False
    assert any("PLACEHOLDER_OBRIGATORIO_AUSENTE" in blocker for blocker in decision.blockers)


def test_merge_show_coverage_gaps_adds_missing_access_control_entries(tmp_path: Path) -> None:
    """Coverage merger should inject show-coverage GAP entries in DQ payload."""

    policy_path = _write_policy(
        tmp_path / "gate_show_merge.yml",
        """
        version: 1
        block:
          enabled: false
          min_error_findings: 0
          critical_statuses: [GAP]
          critical_tokens: [unused]
        partial:
          enabled: true
          statuses: [GAP]
          min_findings: 1
          banner_text: "PARCIAL"
        output:
          allow_partial_on_block: true
        show_coverage:
          enabled: true
          session_type: NOTURNO_SHOW
          critical_dataset: access_control
          critical_statuses: [GAP]
          required_placeholders: [SHOW__COVERAGE__TABLE, GAPS__SUMMARY__TEXT]
        """,
    )
    coverage_report = {
        "sessions": [
            {
                "session_key": "TMJ2025_20251214_SHOW",
                "session_date": "2025-12-14",
                "session_type": "NOTURNO_SHOW",
                "observed_datasets": ["optin"],
                "partial_datasets": [],
                "missing_datasets": ["access_control"],
            }
        ]
    }

    merged = merge_show_coverage_gaps(
        {"summary": {"error": 0}, "sections": {"gaps_by_dataset": {}}},
        coverage_report=coverage_report,
        policy=load_report_gate_policy(policy_path),
    )
    gaps = merged["sections"]["gaps_by_dataset"]
    keys = {key.casefold() for key in gaps}
    assert "tmj2025_20251214_show_access_control" in keys
