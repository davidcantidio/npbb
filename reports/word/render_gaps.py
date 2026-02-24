"""GAP/INCONSISTENTE section renderer for Word reports.

This module consumes DQ report JSON-like payloads and produces concise
text lines for a dedicated Word placeholder section.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import re
from typing import Any


class GapSectionRenderError(ValueError):
    """Raised when DQ report payload is invalid for GAP section rendering."""


_SHOW_DAY_PATTERNS = {
    "12/12": re.compile(r"(12/12|2025-12-12|show[_\s-]?12)", re.IGNORECASE),
    "13/12": re.compile(r"(13/12|2025-12-13|show[_\s-]?13)", re.IGNORECASE),
    "14/12": re.compile(r"(14/12|2025-12-14|show[_\s-]?14)", re.IGNORECASE),
}


def load_dq_report(dq_report_path: Path | str) -> dict[str, Any]:
    """Load DQ report JSON payload from file path.

    Args:
        dq_report_path: JSON file path.

    Returns:
        DQ report payload as dictionary.

    Raises:
        FileNotFoundError: If file does not exist.
        GapSectionRenderError: If JSON is invalid or root is not an object.
    """

    path = Path(dq_report_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo DQ report nao encontrado: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GapSectionRenderError(f"JSON invalido no DQ report: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise GapSectionRenderError("DQ report invalido: raiz deve ser objeto JSON.")
    return dict(payload)


def _coerce_entries(value: Any) -> list[Mapping[str, Any]]:
    """Coerce a sequence node into list of mapping entries.

    Args:
        value: Raw node expected to contain list[dict].

    Returns:
        List of mapping entries, ignoring invalid items.
    """

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _iter_gap_inconsistency_entries(dq_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract GAP/INCONSISTENTE entries from DQ report payload.

    Args:
        dq_report: DQ report dictionary.

    Returns:
        Normalized list of entries with `status`, `dataset_id`, and evidence fields.
    """

    sections = dq_report.get("sections")
    normalized: list[dict[str, Any]] = []

    if isinstance(sections, Mapping):
        inconsistencies = _coerce_entries(sections.get("inconsistencies"))
        for item in inconsistencies:
            normalized.append(
                {
                    "status": "INCONSISTENTE",
                    "dataset_id": str(item.get("dataset_id", item.get("dataset", "unknown"))),
                    "message": str(item.get("message", "")),
                    "source_id": str(item.get("source_id", item.get("source", ""))),
                    "location": str(item.get("location", item.get("location_value", ""))),
                    "evidence_text": str(item.get("evidence_text", item.get("evidence", ""))),
                }
            )

        gaps_by_dataset = sections.get("gaps_by_dataset")
        if isinstance(gaps_by_dataset, Mapping):
            for dataset_id, items in gaps_by_dataset.items():
                for item in _coerce_entries(items):
                    normalized.append(
                        {
                            "status": "GAP",
                            "dataset_id": str(item.get("dataset_id", dataset_id)),
                            "message": str(item.get("message", "")),
                            "source_id": str(item.get("source_id", item.get("source", ""))),
                            "location": str(item.get("location", item.get("location_value", ""))),
                            "evidence_text": str(
                                item.get("evidence_text", item.get("evidence", ""))
                            ),
                        }
                    )

    if normalized:
        return normalized

    # Fallback format: parse framework `results` entries when `sections` is absent.
    results = _coerce_entries(dq_report.get("results"))
    for result in results:
        evidence = result.get("evidence")
        if not isinstance(evidence, Mapping):
            evidence = {}
        lineage = result.get("lineage")
        if not isinstance(lineage, Mapping):
            lineage = {}

        status = str(evidence.get("status", "")).upper()
        if status not in {"GAP", "INCONSISTENTE"}:
            continue

        normalized.append(
            {
                "status": status,
                "dataset_id": str(evidence.get("dataset_id", "unknown")),
                "message": str(result.get("message", "")),
                "source_id": str(lineage.get("source_id", lineage.get("source", ""))),
                "location": str(lineage.get("location", lineage.get("location_value", ""))),
                "evidence_text": str(
                    lineage.get("evidence_text", lineage.get("evidence", ""))
                ),
            }
        )
    return normalized


def _truncate_text(value: str, *, max_len: int = 140) -> str:
    """Truncate text for compact layout-ready lines."""

    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _detect_show_days(*texts: str) -> set[str]:
    """Detect TMJ show-day mentions from one or more text snippets."""

    joined = " | ".join(str(text or "") for text in texts)
    days: set[str] = set()
    for day, pattern in _SHOW_DAY_PATTERNS.items():
        if pattern.search(joined):
            days.add(day)
    return days


def render_gaps_section(
    dq_report: Mapping[str, Any] | None,
    *,
    max_items: int = 10,
) -> list[str]:
    """Render GAP/INCONSISTENTE section lines from DQ payload.

    Args:
        dq_report: DQ report dictionary (JSON-like structure).
        max_items: Maximum number of finding lines.

    Returns:
        Layout-ready lines for Word text placeholder rendering.

    Raises:
        GapSectionRenderError: If report payload has invalid type.
    """

    if dq_report is None:
        return [
            "Secao GAP/INCONSISTENTE: relatorio DQ nao informado.",
            "GAP: sem insumos de DQ para listar lacunas e inconsistencias.",
        ]
    if not isinstance(dq_report, Mapping):
        raise GapSectionRenderError("dq_report invalido: esperado objeto/dict.")

    entries = _iter_gap_inconsistency_entries(dq_report)
    if not entries:
        return [
            "Secao GAP/INCONSISTENTE: nenhum item de GAP/INCONSISTENTE no DQ.",
            "Cobertura de shows por dia (12/12, 13/12, 14/12): sem gaps identificados.",
        ]

    status_counts = {"GAP": 0, "INCONSISTENTE": 0}
    coverage: dict[str, dict[str, str]] = {day: {} for day in ("12/12", "13/12", "14/12")}
    lines: list[str] = []

    for index, entry in enumerate(entries):
        status = str(entry.get("status", "")).upper()
        if status in status_counts:
            status_counts[status] += 1

        dataset_id = _truncate_text(str(entry.get("dataset_id", "unknown")))
        message = _truncate_text(str(entry.get("message", "")))
        source_id = _truncate_text(str(entry.get("source_id", "")) or "n/d")
        location = _truncate_text(str(entry.get("location", "")) or "n/d")
        evidence = _truncate_text(str(entry.get("evidence_text", "")) or message or "n/d")

        if index < max_items:
            lines.append(
                f"{status} | dataset={dataset_id} | source_id={source_id} | "
                f"location={location} | evidencia={evidence}"
            )

        matched_days = _detect_show_days(dataset_id, message, evidence)
        for day in matched_days:
            coverage[day] = {
                "status": status,
                "evidence": evidence,
            }

    header = (
        f"Resumo GAP/INCONSISTENTE: gaps={status_counts['GAP']} | "
        f"inconsistencias={status_counts['INCONSISTENTE']}"
    )

    coverage_lines = ["Cobertura de shows por dia (12/12, 13/12, 14/12):"]
    for day in ("12/12", "13/12", "14/12"):
        day_info = coverage.get(day, {})
        if day_info:
            coverage_lines.append(
                f"{day}: {day_info['status']} | evidencia={day_info['evidence']}"
            )
        else:
            coverage_lines.append(f"{day}: sem GAP/INCONSISTENTE identificado no DQ.")

    return [header, *lines, *coverage_lines]
