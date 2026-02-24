"""Metric lineage registry.

The lineage record is the audit bridge between:
- a metric (metric_key),
- a source (source_id),
- a location inside the source (page/slide/sheet/range),
- and a human-readable evidence string.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from sqlmodel import Session, select

from app.models.models import MetricLineage, Source, now_utc
from app.services.ingestion_registry import normalize_source_id


_RE_PAGE = re.compile(r"\b(pagina|page|p\.)\s*(\d+)\b", flags=re.IGNORECASE)
_RE_SLIDE = re.compile(r"\b(slide)\s*(\d+)\b", flags=re.IGNORECASE)
_RE_SHEET = re.compile(r"\b(aba|sheet)\s*[:=-]?\s*(.+)$", flags=re.IGNORECASE)
_RE_RANGE = re.compile(r"\b([A-Z]{1,3}\d+)\s*:\s*([A-Z]{1,3}\d+)\b")


def _to_ascii(text: str) -> str:
    text = text or ""
    norm = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in norm if ord(ch) < 128)


def normalize_location(raw: str) -> str:
    """Normalize a raw location string to a stable prefix format.

    Examples:
    - "pagina 12" -> "page:12"
    - "slide 3" -> "slide:3"
    - "aba Entidades" -> "sheet:entidades"
    - "A1:D20" -> "range:A1:D20"
    """
    s = (raw or "").strip()
    if not s:
        raise ValueError("location_raw vazio")

    ascii_s = _to_ascii(s).strip()

    m = _RE_PAGE.search(ascii_s)
    if m:
        return f"page:{int(m.group(2))}"

    m = _RE_SLIDE.search(ascii_s)
    if m:
        return f"slide:{int(m.group(2))}"

    m = _RE_SHEET.search(ascii_s)
    if m:
        name = m.group(2).strip()
        name = re.sub(r"\s+", " ", name)
        name = name.lower()
        return f"sheet:{name}"

    m = _RE_RANGE.search(ascii_s.upper())
    if m:
        return f"range:{m.group(1).upper()}:{m.group(2).upper()}"

    # Fallback: keep a cleaned version
    fallback = re.sub(r"\s+", " ", ascii_s).strip()
    return f"raw:{fallback}"


def register_metric_lineage(
    session: Session,
    *,
    metric_key: str,
    source_id: str,
    ingestion_id: Optional[int] = None,
    location_raw: str,
    evidence: Optional[str] = None,
    docx_section: Optional[str] = None,
) -> MetricLineage:
    """Persist a MetricLineage record."""
    metric_key_norm = (metric_key or "").strip()
    if not metric_key_norm:
        raise ValueError("metric_key vazio")

    sid = normalize_source_id(source_id)
    if session.get(Source, sid) is None:
        raise ValueError(f"Source nao registrada: {sid}")

    loc_raw = (location_raw or "").strip()
    loc_norm = normalize_location(loc_raw)

    row = MetricLineage(
        metric_key=metric_key_norm,
        docx_section=(docx_section or None),
        source_id=sid,
        ingestion_id=ingestion_id,
        location_raw=loc_raw,
        location_norm=loc_norm,
        evidence=evidence,
        created_at=now_utc(),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def list_metric_lineage(
    session: Session,
    *,
    metric_key: Optional[str] = None,
    source_id: Optional[str] = None,
    docx_section: Optional[str] = None,
    limit: int = 200,
) -> list[MetricLineage]:
    """List lineage entries with optional filters."""
    if limit <= 0 or limit > 5000:
        raise ValueError("limit invalido")

    stmt = select(MetricLineage).order_by(MetricLineage.created_at.desc()).limit(limit)
    if metric_key:
        stmt = stmt.where(MetricLineage.metric_key == metric_key)
    if source_id:
        stmt = stmt.where(MetricLineage.source_id == normalize_source_id(source_id))
    if docx_section:
        stmt = stmt.where(MetricLineage.docx_section == docx_section)
    return list(session.exec(stmt).all())

