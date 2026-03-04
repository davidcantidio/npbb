"""Section-building helpers for rendered DQ reports."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping

from ._contracts import CheckResult, CheckStatus, Severity


def normalize_dataset_id(check_id: str, evidence: Mapping[str, Any]) -> str:
    """Resolve dataset identifier from evidence and fallback check id."""

    from_evidence = str(evidence.get("dataset_id") or "").strip()
    if from_evidence:
        return from_evidence
    parts = check_id.split(".")
    return parts[2] if check_id.startswith("dq.") and len(parts) >= 3 else "unknown"


def extract_source_id(result: CheckResult) -> str | None:
    lineage_source = result.lineage.get("source_id")
    if isinstance(lineage_source, str) and lineage_source.strip():
        return lineage_source.strip()
    evidence_source = result.evidence.get("source_id")
    if isinstance(evidence_source, str) and evidence_source.strip():
        return evidence_source.strip()
    return None


def extract_lineage_ref_id(result: CheckResult) -> int | None:
    raw = result.lineage.get("lineage_ref_id") if result.lineage.get("lineage_ref_id") is not None else result.evidence.get("lineage_ref_id")
    try:
        return int(raw) if raw is not None and int(raw) > 0 else None
    except (TypeError, ValueError):
        return None


def extract_location(result: CheckResult) -> str | None:
    for key in ("location", "location_value", "location_raw"):
        for payload in (result.lineage, result.evidence):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    if result.evidence.get("pdf_page") is not None:
        return f"page:{result.evidence.get('pdf_page')}"
    if result.evidence.get("slide_number") is not None:
        return f"slide:{result.evidence.get('slide_number')}"
    sheet = result.evidence.get("sheet_name")
    return f"sheet:{sheet.strip()}" if isinstance(sheet, str) and sheet.strip() else None


def extract_evidence_text(result: CheckResult) -> str | None:
    lineage_evidence = result.lineage.get("evidence_text")
    if isinstance(lineage_evidence, str) and lineage_evidence.strip():
        return lineage_evidence.strip()
    for key in ("evidence_text", "evidence", "title", "label"):
        value = result.evidence.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def extract_from_findings(evidence: Mapping[str, Any], field_name: str) -> Any:
    findings = evidence.get("findings_sample")
    if not isinstance(findings, list):
        return None
    for finding in findings:
        if isinstance(finding, Mapping) and finding.get(field_name) is not None:
            return finding.get(field_name)
    return None


def is_inconsistency(result: CheckResult) -> bool:
    if str(result.evidence.get("status") or "").strip().lower() == "inconsistente":
        return True
    if "cross_source.inconsistency" in result.check_id.lower():
        return result.status == CheckStatus.FAIL
    findings = result.evidence.get("findings_sample")
    return isinstance(findings, list) and any(str(item.get("status") or "").strip().lower() == "inconsistente" for item in findings if isinstance(item, Mapping))


def is_gap(result: CheckResult) -> bool:
    if "gap" in result.check_id.lower() or str(result.evidence.get("status") or "").strip().lower() == "gap":
        return True
    gap_keys = {"gap_reason", "missing_table", "missing_columns", "missing_datasets", "missing_sources", "missing_sections"}
    return any(key in result.evidence for key in gap_keys)


def to_word_item(result: CheckResult) -> dict[str, Any]:
    evidence = result.evidence if isinstance(result.evidence, Mapping) else {}
    item = {"check_id": result.check_id, "status": result.status.value, "severity": result.severity.value, "dataset_id": normalize_dataset_id(result.check_id, evidence), "message": result.message, "session_id": evidence.get("session_id") if evidence.get("session_id") is not None else extract_from_findings(evidence, "session_id"), "metric_key": evidence.get("metric_key") if evidence.get("metric_key") is not None else extract_from_findings(evidence, "metric_key"), "source_id": extract_source_id(result), "location": extract_location(result), "lineage_ref_id": extract_lineage_ref_id(result), "evidence_text": extract_evidence_text(result)}
    if isinstance(evidence.get("suggested_action"), str) and evidence.get("suggested_action").strip():
        item["suggested_action"] = evidence["suggested_action"].strip()
    return item


def build_sections(results: Iterable[CheckResult]) -> dict[str, Any]:
    """Build structured report sections for downstream consumers."""

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    inconsistencies: list[dict[str, Any]] = []
    gaps_by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        item = to_word_item(result)
        if result.status == CheckStatus.FAIL and result.severity == Severity.ERROR:
            errors.append(item)
        if result.status == CheckStatus.FAIL and result.severity == Severity.WARNING:
            warnings.append(item)
        if is_inconsistency(result):
            inconsistencies.append(item)
        if is_gap(result):
            gaps_by_dataset[item["dataset_id"]].append(item)
    sort_key = lambda item: (str(item.get("dataset_id") or ""), str(item.get("check_id") or ""), str(item.get("source_id") or ""), str(item.get("location") or ""))
    return {"errors": sorted(errors, key=sort_key), "warnings": sorted(warnings, key=sort_key), "inconsistencies": sorted(inconsistencies, key=sort_key), "gaps_by_dataset": {dataset_id: sorted(items, key=sort_key) for dataset_id, items in sorted(gaps_by_dataset.items(), key=lambda entry: entry[0])}}

