"""Lineage rendering helpers for Word report sections.

This module normalizes lineage references and renders audit-friendly
lineage paragraphs (source + location + evidence) for tables and figures.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LineageRef:
    """Typed lineage reference used by report renderers.

    Args:
        source_id: Source identifier (file/source registry id).
        location: Source location (page/slide/sheet/range).
        evidence_text: Evidence text proving the metric origin.

    Raises:
        ValueError: If any required field is empty.
    """

    source_id: str
    location: str
    evidence_text: str

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("LineageRef.source_id deve ser texto nao vazio.")
        if not self.location.strip():
            raise ValueError("LineageRef.location deve ser texto nao vazio.")
        if not self.evidence_text.strip():
            raise ValueError("LineageRef.evidence_text deve ser texto nao vazio.")


class LineageRenderError(ValueError):
    """Raised when lineage normalization/rendering fails."""


def normalize_lineage_refs(lineage_refs: Any) -> list[LineageRef]:
    """Normalize lineage references from typed or dict-like input.

    Accepted item formats:
    - `LineageRef`
    - mapping with keys:
      - source id: `source_id` or `source`
      - location: `location` or `location_value`
      - evidence: `evidence_text`, `evidence` or `evidencia`

    Args:
        lineage_refs: Raw lineage list.

    Returns:
        Normalized lineage refs list.

    Raises:
        LineageRenderError: If input type is invalid.
    """

    if lineage_refs is None:
        return []
    if not isinstance(lineage_refs, Sequence) or isinstance(lineage_refs, (str, bytes, bytearray)):
        raise LineageRenderError("lineage_refs invalido: esperado list[LineageRef|dict].")

    normalized: list[LineageRef] = []
    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(lineage_refs):
        if isinstance(item, LineageRef):
            ref = item
        elif isinstance(item, Mapping):
            source_id = str(item.get("source_id", item.get("source", ""))).strip()
            location = str(item.get("location", item.get("location_value", ""))).strip()
            evidence = str(
                item.get("evidence_text", item.get("evidence", item.get("evidencia", "")))
            ).strip()
            if not source_id or not location or not evidence:
                continue
            try:
                ref = LineageRef(
                    source_id=source_id,
                    location=location,
                    evidence_text=evidence,
                )
            except ValueError as exc:
                raise LineageRenderError(
                    f"lineage_refs[{index}] invalido: {exc}"
                ) from exc
        else:
            raise LineageRenderError(
                f"lineage_refs[{index}] invalido: esperado LineageRef ou dict."
            )

        key = (ref.source_id, ref.location, ref.evidence_text)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(ref)

    return normalized


def extract_lineage_refs_from_rows(rows: Sequence[Mapping[str, Any]]) -> list[LineageRef]:
    """Extract lineage refs from mart rows when lineage columns are present.

    Args:
        rows: Query rows returned by one mart/view.

    Returns:
        Normalized lineage refs list extracted from row columns.
    """

    raw_refs: list[dict[str, Any]] = []
    for row in rows:
        source_id = row.get("source_id", row.get("source"))
        location = row.get("location", row.get("location_value"))
        evidence = row.get("evidence_text", row.get("evidence", row.get("evidencia")))
        raw_refs.append(
            {
                "source_id": source_id,
                "location": location,
                "evidence_text": evidence,
            }
        )
    return normalize_lineage_refs(raw_refs)


def render_lineage_block(
    lineage_refs: Sequence[LineageRef] | Sequence[Mapping[str, Any]] | None,
    *,
    placeholder_id: str,
    artifact_type: str,
) -> list[str]:
    """Render lineage paragraph lines for one table/figure block.

    Args:
        lineage_refs: Optional lineage refs list.
        placeholder_id: Placeholder identifier tied to the rendered artifact.
        artifact_type: Artifact type (`table` or `figure`).

    Returns:
        List of paragraph lines ready to be inserted into DOCX.
    """

    refs = normalize_lineage_refs(lineage_refs)
    header = f"[Linhagem] {artifact_type} | placeholder={placeholder_id}"
    if refs:
        lines = [header]
        lines.extend(
            (
                f"- source_id={ref.source_id} | "
                f"location={ref.location} | "
                f"evidence_text={ref.evidence_text}"
            )
            for ref in refs
        )
        return lines

    return [
        header,
        (
            "- GAP: linhagem ausente para o artefato. "
            "Necessario informar source_id + location + evidence_text."
        ),
    ]
