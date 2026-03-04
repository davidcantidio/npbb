"""Renderer helpers for DQ reports in the shared lead ETL core."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from ._contracts import CheckReport, CheckResult, CheckStatus, Severity
from ._report_sections import build_sections


@dataclass(frozen=True)
class ReportEnvelope:
    ingestion_id: int | None
    generated_at: datetime
    fail_on: Severity | None
    exit_code: int
    summary: dict[str, int]
    results: tuple[CheckResult, ...]


def normalize_envelope(report_or_results: CheckReport | Sequence[CheckResult]) -> ReportEnvelope:
    """Normalize `CheckReport` or plain results list into one envelope."""

    if isinstance(report_or_results, CheckReport):
        return ReportEnvelope(ingestion_id=report_or_results.ingestion_id, generated_at=report_or_results.generated_at, fail_on=report_or_results.fail_on, exit_code=report_or_results.exit_code, summary=dict(report_or_results.summary), results=tuple(report_or_results.results))
    results = tuple(report_or_results)
    ingestion_id = next((result.ingestion_id for result in results if result.ingestion_id is not None), None)
    summary = {"total": len(results), "pass": 0, "fail": 0, "skip": 0, "info": 0, "warning": 0, "error": 0}
    for result in results:
        summary[result.status.value] += 1
        summary[result.severity.value] += 1
    return ReportEnvelope(ingestion_id=ingestion_id, generated_at=datetime.now(timezone.utc), fail_on=None, exit_code=0, summary=summary, results=results)


def render_dq_report_json(report_or_results: CheckReport | Sequence[CheckResult], *, coverage_section: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Render DQ report payload as dictionary for API/Word integrations."""

    envelope = normalize_envelope(report_or_results)
    sections = build_sections(envelope.results)
    return {"ingestion_id": envelope.ingestion_id, "generated_at": envelope.generated_at.isoformat(), "fail_on": envelope.fail_on.value if envelope.fail_on else None, "exit_code": envelope.exit_code, "summary": envelope.summary, "results": [result.to_dict() for result in envelope.results], "sections": {**sections, "coverage": dict(coverage_section) if coverage_section is not None else None}}


def render_dq_report(report_or_results: CheckReport | Sequence[CheckResult], *, coverage_section: Mapping[str, Any] | None = None) -> str:
    """Render DQ report in markdown with grouped sections and evidence hints."""

    payload = render_dq_report_json(report_or_results, coverage_section=coverage_section)
    sections = payload["sections"]
    lines = ["# DQ Report", "", f"- ingestion_id: {payload['ingestion_id']}", f"- generated_at: {payload['generated_at']}", f"- fail_on: {payload['fail_on'] or 'none'}", f"- exit_code: {payload['exit_code']}", f"- total: {payload['summary'].get('total', 0)}", f"- pass: {payload['summary'].get('pass', 0)}", f"- fail: {payload['summary'].get('fail', 0)}", f"- skip: {payload['summary'].get('skip', 0)}", ""]
    _append_items(lines, "Errors", sections.get("errors", []))
    _append_items(lines, "Warnings", sections.get("warnings", []))
    _append_items(lines, "Inconsistencias", sections.get("inconsistencies", []))
    _append_gaps(lines, sections.get("gaps_by_dataset", {}))
    _append_coverage(lines, sections.get("coverage"))
    lines.extend(["## Word Ready", "- highlights_curtos:", f"  - erros={len(sections.get('errors', []))} warnings={len(sections.get('warnings', []))} inconsistencias={len(sections.get('inconsistencies', []))}", "- listas: usar `sections.errors`, `sections.warnings`, `sections.inconsistencies` e `sections.gaps_by_dataset`", ""])
    return "\n".join(lines)


def _append_items(lines: list[str], title: str, items: Sequence[Mapping[str, Any]]) -> None:
    lines.append(f"## {title}")
    if not items:
        lines.extend(["- nenhum", ""])
        return
    for item in items:
        lines.append(f"- [{item.get('severity')}/{item.get('status')}] {item.get('check_id')}: {item.get('message')}")
        lines.append(f"  Fonte: {item.get('source_id') or 'n/a'} | Local: {item.get('location') or 'n/a'} | Evidencia: {item.get('evidence_text') or 'n/a'}")
        if item.get("suggested_action"):
            lines.append(f"  Acao sugerida: {item.get('suggested_action')}")
    lines.append("")


def _append_gaps(lines: list[str], gaps: Mapping[str, Sequence[Mapping[str, Any]]]) -> None:
    lines.append("## Gaps Por Dataset")
    if not gaps:
        lines.extend(["- nenhum", ""])
        return
    for dataset_id in sorted(gaps):
        lines.append(f"### {dataset_id}")
        for item in gaps[dataset_id]:
            lines.append(f"- {item.get('check_id')}: {item.get('message')}")
            lines.append(f"  Fonte: {item.get('source_id') or 'n/a'} | Local: {item.get('location') or 'n/a'} | Evidencia: {item.get('evidence_text') or 'n/a'}")
        lines.append("")


def _append_coverage(lines: list[str], coverage: Mapping[str, Any] | None) -> None:
    if not isinstance(coverage, Mapping):
        return
    summary = coverage.get("summary", {})
    lines.extend(["## Coverage", f"- status: {coverage.get('status', 'n/a')}", f"- total_sessions: {summary.get('total_sessions', 0)}", f"- ok_sessions: {summary.get('ok_sessions', 0)}", f"- partial_sessions: {summary.get('partial_sessions', 0)}", f"- gap_sessions: {summary.get('gap_sessions', 0)}"])
    coverage_sessions = coverage.get("sessions", [])
    if isinstance(coverage_sessions, list) and coverage_sessions:
        lines.extend(["| session_key | status | missing_datasets |", "| --- | --- | --- |"])
        for session_item in coverage_sessions:
            if not isinstance(session_item, Mapping):
                continue
            missing = session_item.get("missing_datasets") or []
            missing_text = ", ".join(str(item) for item in missing) if isinstance(missing, list) else str(missing)
            lines.append(f"| {session_item.get('session_key')} | {session_item.get('status')} | {missing_text or '-'} |")
    lines.append("")

