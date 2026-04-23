"""Map core DQ results to backend preview payload."""

from __future__ import annotations

from typing import Any

from core.leads_etl.validate.framework import CheckReport

from .contracts import EtlPreviewDQItem


def _extract_sample(result_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("sample_duplicates", "findings_sample", "sample_row"):
        value = result_evidence.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            return [value]
    return []


def map_check_report(report: CheckReport) -> tuple[EtlPreviewDQItem, ...]:
    items: list[EtlPreviewDQItem] = []
    for result in report.results:
        sample = _extract_sample(result.evidence)
        affected_rows = int(
            result.evidence.get("null_critical_rows")
            or result.evidence.get("duplicate_total_rows")
            or result.evidence.get("finding_count")
            or result.evidence.get("duplicate_group_count")
            or (1 if result.status.value == "fail" else 0)
        )
        items.append(
            EtlPreviewDQItem(
                check_name=result.check_id,
                severity=result.severity.value,
                affected_rows=affected_rows,
                sample=sample[:5],
                check_id=result.check_id,
                message=result.message,
            )
        )
    return tuple(items)
