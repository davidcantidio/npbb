"""Render helpers for DQ reports consumed by operational and Word layers.

This module transforms framework check outputs into a compact contract with:
- errors and warnings lists;
- inconsistencies (`INCONSISTENTE`) list;
- gaps grouped by dataset;
- short actionable fields including lineage/location when available.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from .framework import CheckReport, CheckResult, CheckStatus, Severity


@dataclass(frozen=True)
class _ReportEnvelope:
    """Normalized report envelope used by renderers."""

    ingestion_id: int | None
    generated_at: datetime
    fail_on: Severity | None
    exit_code: int
    summary: dict[str, int]
    results: tuple[CheckResult, ...]


def _normalize_envelope(report_or_results: CheckReport | Sequence[CheckResult]) -> _ReportEnvelope:
    """Normalize `CheckReport` or plain results list into one envelope.

    Args:
        report_or_results: Full framework report or sequence of check results.

    Returns:
        Internal envelope with report metadata and normalized results.
    """

    if isinstance(report_or_results, CheckReport):
        return _ReportEnvelope(
            ingestion_id=report_or_results.ingestion_id,
            generated_at=report_or_results.generated_at,
            fail_on=report_or_results.fail_on,
            exit_code=report_or_results.exit_code,
            summary=dict(report_or_results.summary),
            results=tuple(report_or_results.results),
        )

    results = tuple(report_or_results)
    ingestion_id: int | None = None
    for result in results:
        if result.ingestion_id is not None:
            ingestion_id = result.ingestion_id
            break

    summary = {
        "total": len(results),
        "pass": 0,
        "fail": 0,
        "skip": 0,
        "info": 0,
        "warning": 0,
        "error": 0,
    }
    for result in results:
        summary[result.status.value] += 1
        summary[result.severity.value] += 1

    return _ReportEnvelope(
        ingestion_id=ingestion_id,
        generated_at=datetime.now(timezone.utc),
        fail_on=None,
        exit_code=0,
        summary=summary,
        results=results,
    )


def _normalize_dataset_id(check_id: str, evidence: Mapping[str, Any]) -> str:
    """Resolve dataset identifier from evidence and fallback check id."""

    from_evidence = str(evidence.get("dataset_id") or "").strip()
    if from_evidence:
        return from_evidence
    if check_id.startswith("dq.") and "." in check_id:
        parts = check_id.split(".")
        if len(parts) >= 3:
            return parts[2]
    return "unknown"


def _extract_source_id(result: CheckResult) -> str | None:
    """Extract source identifier from lineage/evidence payload."""

    lineage_source = result.lineage.get("source_id")
    if isinstance(lineage_source, str) and lineage_source.strip():
        return lineage_source.strip()

    evidence_source = result.evidence.get("source_id")
    if isinstance(evidence_source, str) and evidence_source.strip():
        return evidence_source.strip()

    return None


def _extract_lineage_ref_id(result: CheckResult) -> int | None:
    """Extract optional lineage reference identifier from payloads."""

    raw = result.lineage.get("lineage_ref_id")
    if raw is None:
        raw = result.evidence.get("lineage_ref_id")
    try:
        if raw is None:
            return None
        parsed = int(raw)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _extract_location(result: CheckResult) -> str | None:
    """Extract a location string from lineage/evidence when available."""

    for key in ("location", "location_value", "location_raw"):
        value = result.lineage.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key in ("location", "location_value", "location_raw"):
        value = result.evidence.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    page = result.evidence.get("pdf_page")
    if page is not None:
        return f"page:{page}"
    slide = result.evidence.get("slide_number")
    if slide is not None:
        return f"slide:{slide}"
    sheet = result.evidence.get("sheet_name")
    if isinstance(sheet, str) and sheet.strip():
        return f"sheet:{sheet.strip()}"
    return None


def _extract_evidence_text(result: CheckResult) -> str | None:
    """Extract human-readable evidence text from lineage/evidence payloads."""

    lineage_evidence = result.lineage.get("evidence_text")
    if isinstance(lineage_evidence, str) and lineage_evidence.strip():
        return lineage_evidence.strip()

    for key in ("evidence_text", "evidence", "title", "label"):
        value = result.evidence.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_from_findings(evidence: Mapping[str, Any], field_name: str) -> Any:
    """Extract first non-empty field value from findings sample payload."""

    findings = evidence.get("findings_sample")
    if not isinstance(findings, list):
        return None
    for finding in findings:
        if not isinstance(finding, Mapping):
            continue
        value = finding.get(field_name)
        if value is not None:
            return value
    return None


def _is_inconsistency(result: CheckResult) -> bool:
    """Return `True` when result represents cross-source inconsistency."""

    status = str(result.evidence.get("status") or "").strip().lower()
    if status == "inconsistente":
        return True
    if "cross_source.inconsistency" in result.check_id.lower():
        return result.status == CheckStatus.FAIL
    findings = result.evidence.get("findings_sample")
    if isinstance(findings, list):
        for item in findings:
            if not isinstance(item, Mapping):
                continue
            finding_status = str(item.get("status") or "").strip().lower()
            if finding_status == "inconsistente":
                return True
    return False


def _is_gap(result: CheckResult) -> bool:
    """Return `True` when result indicates a GAP/missing-data scenario."""

    if "gap" in result.check_id.lower():
        return True
    status = str(result.evidence.get("status") or "").strip().lower()
    if status == "gap":
        return True
    gap_keys = {
        "gap_reason",
        "missing_table",
        "missing_columns",
        "missing_datasets",
        "missing_sources",
        "missing_sections",
    }
    return any(key in result.evidence for key in gap_keys)


def _to_word_item(result: CheckResult) -> dict[str, Any]:
    """Convert one check result to compact payload item for report sections."""

    evidence = result.evidence if isinstance(result.evidence, Mapping) else {}
    session_id = evidence.get("session_id")
    if session_id is None:
        session_id = _extract_from_findings(evidence, "session_id")
    metric_key = evidence.get("metric_key")
    if metric_key is None:
        metric_key = _extract_from_findings(evidence, "metric_key")

    item = {
        "check_id": result.check_id,
        "status": result.status.value,
        "severity": result.severity.value,
        "dataset_id": _normalize_dataset_id(result.check_id, evidence),
        "message": result.message,
        "session_id": session_id,
        "metric_key": metric_key,
        "source_id": _extract_source_id(result),
        "location": _extract_location(result),
        "lineage_ref_id": _extract_lineage_ref_id(result),
        "evidence_text": _extract_evidence_text(result),
    }
    suggested_action = evidence.get("suggested_action")
    if isinstance(suggested_action, str) and suggested_action.strip():
        item["suggested_action"] = suggested_action.strip()
    return item


def _build_sections(results: Iterable[CheckResult]) -> dict[str, Any]:
    """Build structured report sections for downstream consumers."""

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    inconsistencies: list[dict[str, Any]] = []
    gaps_by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for result in results:
        item = _to_word_item(result)
        if result.status == CheckStatus.FAIL and result.severity == Severity.ERROR:
            errors.append(item)
        if result.status == CheckStatus.FAIL and result.severity == Severity.WARNING:
            warnings.append(item)
        if _is_inconsistency(result):
            inconsistencies.append(item)
        if _is_gap(result):
            gaps_by_dataset[item["dataset_id"]].append(item)

    def _item_sort_key(item: Mapping[str, Any]) -> tuple[str, str, str, str]:
        return (
            str(item.get("dataset_id") or ""),
            str(item.get("check_id") or ""),
            str(item.get("source_id") or ""),
            str(item.get("location") or ""),
        )

    errors.sort(key=_item_sort_key)
    warnings.sort(key=_item_sort_key)
    inconsistencies.sort(key=_item_sort_key)
    ordered_gaps = {
        dataset_id: sorted(items, key=_item_sort_key)
        for dataset_id, items in sorted(gaps_by_dataset.items(), key=lambda entry: entry[0])
    }

    return {
        "errors": errors,
        "warnings": warnings,
        "inconsistencies": inconsistencies,
        "gaps_by_dataset": ordered_gaps,
    }


def render_dq_report_json(
    report_or_results: CheckReport | Sequence[CheckResult],
    *,
    coverage_section: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Render DQ report payload as dictionary for API/Word integrations.

    Args:
        report_or_results: Full framework report or plain list of check results.

    Returns:
        Dict payload with base report metadata and grouped sections.
    """

    envelope = _normalize_envelope(report_or_results)
    sections = _build_sections(envelope.results)

    sections_payload = {
        **sections,
        "coverage": dict(coverage_section) if coverage_section is not None else None,
    }

    return {
        "ingestion_id": envelope.ingestion_id,
        "generated_at": envelope.generated_at.isoformat(),
        "fail_on": envelope.fail_on.value if envelope.fail_on else None,
        "exit_code": envelope.exit_code,
        "summary": envelope.summary,
        "results": [result.to_dict() for result in envelope.results],
        "sections": sections_payload,
    }


def render_dq_report(
    report_or_results: CheckReport | Sequence[CheckResult],
    *,
    coverage_section: Mapping[str, Any] | None = None,
) -> str:
    """Render DQ report in markdown with grouped sections and evidence hints.

    Args:
        report_or_results: Full framework report or plain list of check results.

    Returns:
        Markdown string ready for operational review or Word ingestion helpers.
    """

    payload = render_dq_report_json(report_or_results, coverage_section=coverage_section)
    sections = payload["sections"]

    lines: list[str] = []
    lines.append("# DQ Report")
    lines.append("")
    lines.append(f"- ingestion_id: {payload['ingestion_id']}")
    lines.append(f"- generated_at: {payload['generated_at']}")
    lines.append(f"- fail_on: {payload['fail_on'] or 'none'}")
    lines.append(f"- exit_code: {payload['exit_code']}")
    lines.append(f"- total: {payload['summary'].get('total', 0)}")
    lines.append(f"- pass: {payload['summary'].get('pass', 0)}")
    lines.append(f"- fail: {payload['summary'].get('fail', 0)}")
    lines.append(f"- skip: {payload['summary'].get('skip', 0)}")
    lines.append("")

    def _append_items(title: str, items: Sequence[Mapping[str, Any]]) -> None:
        lines.append(f"## {title}")
        if not items:
            lines.append("- nenhum")
            lines.append("")
            return
        for item in items:
            lines.append(
                "- "
                + f"[{item.get('severity')}/{item.get('status')}] "
                + f"{item.get('check_id')}: {item.get('message')}"
            )
            lines.append(
                f"  Fonte: {item.get('source_id') or 'n/a'} | "
                f"Local: {item.get('location') or 'n/a'} | "
                f"Evidencia: {item.get('evidence_text') or 'n/a'}"
            )
            action = item.get("suggested_action")
            if action:
                lines.append(f"  Acao sugerida: {action}")
        lines.append("")

    _append_items("Errors", sections.get("errors", []))
    _append_items("Warnings", sections.get("warnings", []))
    _append_items("Inconsistencias", sections.get("inconsistencies", []))

    lines.append("## Gaps Por Dataset")
    gaps = sections.get("gaps_by_dataset", {})
    if not gaps:
        lines.append("- nenhum")
        lines.append("")
    else:
        for dataset_id in sorted(gaps):
            lines.append(f"### {dataset_id}")
            for item in gaps[dataset_id]:
                lines.append(f"- {item.get('check_id')}: {item.get('message')}")
                lines.append(
                    f"  Fonte: {item.get('source_id') or 'n/a'} | "
                    f"Local: {item.get('location') or 'n/a'} | "
                    f"Evidencia: {item.get('evidence_text') or 'n/a'}"
                )
            lines.append("")

    coverage = sections.get("coverage")
    if isinstance(coverage, Mapping):
        coverage_summary = coverage.get("summary", {})
        coverage_sessions = coverage.get("sessions", [])
        lines.append("## Coverage")
        lines.append(f"- status: {coverage.get('status', 'n/a')}")
        lines.append(f"- total_sessions: {coverage_summary.get('total_sessions', 0)}")
        lines.append(f"- ok_sessions: {coverage_summary.get('ok_sessions', 0)}")
        lines.append(f"- partial_sessions: {coverage_summary.get('partial_sessions', 0)}")
        lines.append(f"- gap_sessions: {coverage_summary.get('gap_sessions', 0)}")
        if isinstance(coverage_sessions, list) and coverage_sessions:
            lines.append("| session_key | status | missing_datasets |")
            lines.append("| --- | --- | --- |")
            for session_item in coverage_sessions:
                if not isinstance(session_item, Mapping):
                    continue
                missing = session_item.get("missing_datasets") or []
                if isinstance(missing, list):
                    missing_text = ", ".join(str(item) for item in missing) or "-"
                else:
                    missing_text = str(missing)
                lines.append(
                    f"| {session_item.get('session_key')} | "
                    f"{session_item.get('status')} | {missing_text} |"
                )
        lines.append("")

    lines.append("## Word Ready")
    lines.append("- highlights_curtos:")
    lines.append(
        f"  - erros={len(sections.get('errors', []))} "
        f"warnings={len(sections.get('warnings', []))} "
        f"inconsistencias={len(sections.get('inconsistencies', []))}"
    )
    lines.append("- listas: usar `sections.errors`, `sections.warnings`, `sections.inconsistencies` e `sections.gaps_by_dataset`")
    lines.append("")

    return "\n".join(lines)
