"""Report manifest helpers for Word report generation.

The manifest is a machine-readable JSON artifact generated alongside the DOCX
output, designed for audit and replay use cases.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .placeholders_mapping import WordPlaceholdersMapping
from .render_lineage import normalize_lineage_refs


REPORT_MANIFEST_SCHEMA_VERSION = 1
DEFAULT_REPORT_MANIFEST_FILENAME = "report_manifest.json"


def default_report_manifest_path(output_docx_path: Path | str) -> Path:
    """Return the default manifest path for a DOCX output.

    Args:
        output_docx_path: Generated DOCX path.

    Returns:
        Default manifest file path in the same output directory.
    """

    output_path = Path(output_docx_path)
    return output_path.parent / DEFAULT_REPORT_MANIFEST_FILENAME


def _safe_int(value: Any, *, default: int = 0) -> int:
    """Return integer value with fallback default."""

    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _summarize_dq_report(dq_report: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build DQ summary section for the report manifest.

    Args:
        dq_report: Optional DQ report payload.

    Returns:
        Dictionary with severity counters and gap/inconsistency counts.
    """

    summary_payload: dict[str, Any] = {
        "error": 0,
        "warning": 0,
        "info": 0,
        "gap_count": 0,
        "inconsistency_count": 0,
    }
    if dq_report is None:
        return summary_payload

    summary = dq_report.get("summary")
    if isinstance(summary, Mapping):
        summary_payload["error"] = _safe_int(summary.get("error"), default=0)
        summary_payload["warning"] = _safe_int(summary.get("warning"), default=0)
        summary_payload["info"] = _safe_int(summary.get("info"), default=0)

    sections = dq_report.get("sections")
    if not isinstance(sections, Mapping):
        return summary_payload

    inconsistencies = sections.get("inconsistencies")
    if isinstance(inconsistencies, Sequence) and not isinstance(
        inconsistencies, (str, bytes, bytearray)
    ):
        summary_payload["inconsistency_count"] = len(list(inconsistencies))

    gaps_by_dataset = sections.get("gaps_by_dataset")
    if isinstance(gaps_by_dataset, Mapping):
        gap_count = 0
        for value in gaps_by_dataset.values():
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
                gap_count += len(list(value))
        summary_payload["gap_count"] = gap_count

    return summary_payload


def _build_template_version(template_path: Path) -> str:
    """Build a deterministic template version string.

    Args:
        template_path: Template DOCX path.

    Returns:
        Version string composed from file name and mtime.
    """

    mtime = int(template_path.stat().st_mtime)
    return f"{template_path.name}@{mtime}"


def _extract_query_meta(result: Any) -> tuple[bool, int | None, bool | None]:
    """Extract query metadata from runner result envelope.

    Args:
        result: Query result object/dict from mart runner.

    Returns:
        Tuple `(executed, row_count, cached)`.
    """

    if result is None:
        return (False, None, None)

    rows: Sequence[Any] | None = None
    cached: bool | None = None

    if isinstance(result, Mapping):
        rows_raw = result.get("rows")
        if isinstance(rows_raw, Sequence) and not isinstance(rows_raw, (str, bytes, bytearray)):
            rows = rows_raw
        if "cached" in result:
            cached = bool(result.get("cached"))
    else:
        rows_raw = getattr(result, "rows", None)
        if isinstance(rows_raw, Sequence) and not isinstance(rows_raw, (str, bytes, bytearray)):
            rows = rows_raw
        if hasattr(result, "cached"):
            cached = bool(getattr(result, "cached"))

    if rows is None:
        return (True, None, cached)
    return (True, len(list(rows)), cached)


def build_report_manifest(
    *,
    event_id: int,
    template_path: Path | str,
    output_docx_path: Path | str,
    generated_at: datetime,
    mapping: WordPlaceholdersMapping,
    placeholder_replacements: Mapping[str, int] | None = None,
    placeholder_lineage: Mapping[str, Sequence[Any]] | None = None,
    mart_results: Mapping[str, Any] | None = None,
    dq_report: Mapping[str, Any] | None = None,
    coverage_governance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build report manifest dictionary.

    Args:
        event_id: Event identifier used to render report.
        template_path: Source template DOCX path.
        output_docx_path: Rendered DOCX output path.
        generated_at: UTC render timestamp.
        mapping: Placeholder mapping contract used in render.
        placeholder_replacements: Replacement count by placeholder id.
        placeholder_lineage: Lineage refs by placeholder id.
        mart_results: Optional mart query results by placeholder id.
        dq_report: Optional DQ report payload.
        coverage_governance: Optional governance metadata with versions/paths
            for agenda master and coverage contract used in preflight.

    Returns:
        Dictionary representing `report_manifest.json`.

    Raises:
        ValueError: If `generated_at` is not timezone-aware.
    """

    if generated_at.tzinfo is None:
        raise ValueError("generated_at deve ser timezone-aware (UTC).")

    template = Path(template_path)
    output_docx = Path(output_docx_path)
    replacements = dict(placeholder_replacements or {})
    lineage_by_placeholder = dict(placeholder_lineage or {})
    mart_result_by_placeholder = dict(mart_results or {})

    lineage_refs: list[dict[str, str]] = []
    lineage_key_to_id: dict[tuple[str, str, str], str] = {}

    def ensure_lineage_ref_id(source_id: str, location: str, evidence_text: str) -> str:
        key = (source_id, location, evidence_text)
        existing = lineage_key_to_id.get(key)
        if existing is not None:
            return existing
        lineage_ref_id = f"L{len(lineage_refs) + 1:04d}"
        lineage_key_to_id[key] = lineage_ref_id
        lineage_refs.append(
            {
                "lineage_ref_id": lineage_ref_id,
                "source_id": source_id,
                "location": location,
                "evidence_text": evidence_text,
            }
        )
        return lineage_ref_id

    placeholders_payload: list[dict[str, Any]] = []
    queries_payload: list[dict[str, Any]] = []
    marts_index: dict[str, dict[str, Any]] = {}

    for placeholder in mapping.placeholders:
        placeholder_id = placeholder.placeholder_id
        query_executed, query_row_count, query_cached = _extract_query_meta(
            mart_result_by_placeholder.get(placeholder_id)
        )

        normalized_lineage = normalize_lineage_refs(lineage_by_placeholder.get(placeholder_id))
        lineage_ref_ids = [
            ensure_lineage_ref_id(
                ref.source_id,
                ref.location,
                ref.evidence_text,
            )
            for ref in normalized_lineage
        ]

        replacement_count = int(replacements.get(placeholder_id, 0))
        rendered = replacement_count > 0

        placeholders_payload.append(
            {
                "placeholder_id": placeholder_id,
                "render_type": placeholder.render_type.value,
                "spec_item": placeholder.spec_item,
                "mart_name": placeholder.mart_name,
                "params": dict(placeholder.params),
                "replacement_count": replacement_count,
                "rendered": rendered,
                "lineage_ref_ids": lineage_ref_ids,
            }
        )

        queries_payload.append(
            {
                "placeholder_id": placeholder_id,
                "mart_name": placeholder.mart_name,
                "params": dict(placeholder.params),
                "executed": query_executed,
                "row_count": query_row_count,
                "cached": query_cached,
            }
        )

        mart_entry = marts_index.setdefault(
            placeholder.mart_name,
            {
                "mart_name": placeholder.mart_name,
                "placeholder_ids": [],
                "executed": False,
                "query_count": 0,
                "row_count_total": 0,
            },
        )
        mart_entry["placeholder_ids"].append(placeholder_id)
        if query_executed:
            mart_entry["executed"] = True
            mart_entry["query_count"] = int(mart_entry["query_count"]) + 1
        if query_row_count is not None:
            mart_entry["row_count_total"] = int(mart_entry["row_count_total"]) + int(
                query_row_count
            )

    marts_payload = []
    for mart_name in sorted(marts_index):
        mart_entry = marts_index[mart_name]
        marts_payload.append(
            {
                "mart_name": mart_entry["mart_name"],
                "placeholder_ids": sorted(set(mart_entry["placeholder_ids"])),
                "executed": bool(mart_entry["executed"]),
                "query_count": int(mart_entry["query_count"]),
                "row_count_total": int(mart_entry["row_count_total"]),
            }
        )

    sources = sorted({ref["source_id"] for ref in lineage_refs})
    manifest_generated_at = generated_at.astimezone(timezone.utc).isoformat()

    return {
        "schema_version": REPORT_MANIFEST_SCHEMA_VERSION,
        "event_id": int(event_id),
        "generated_at": manifest_generated_at,
        "output_docx_path": str(output_docx),
        "template": {
            "path": str(template),
            "name": template.name,
            "version": _build_template_version(template),
        },
        "mapping_version": int(mapping.version),
        "dq_summary": _summarize_dq_report(dq_report),
        "coverage_governance": dict(coverage_governance or {}),
        "placeholders": placeholders_payload,
        "queries": queries_payload,
        "marts": marts_payload,
        "sources": sources,
        "lineage_refs": lineage_refs,
    }


def write_report_manifest(manifest: Mapping[str, Any], path: Path | str) -> Path:
    """Write report manifest dictionary as UTF-8 JSON file.

    Args:
        manifest: Manifest payload dictionary.
        path: Target JSON file path.

    Returns:
        Final manifest path.

    Raises:
        OSError: If file cannot be written.
    """

    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(dict(manifest), ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return target_path
