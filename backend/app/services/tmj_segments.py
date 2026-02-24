"""Ticket category -> BB relationship segment mapping (TMJ canonicalization).

The mapping is intentionally auditable:
- a table (`ticket_category_segment_map`) stores normalized category strings,
- rows can be operator-edited,
- and missing categories can be auto-populated with inferred defaults.

This module provides:
- normalization helpers,
- inference heuristics (best-effort),
- and upsert utilities for the mapping table.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional, Tuple

from sqlmodel import Session, select

from app.models.models import BbRelationshipSegment, TicketCategorySegmentMap


def _to_ascii_upper(value: str) -> str:
    raw = (value or "").strip()
    norm = unicodedata.normalize("NFKD", raw)
    ascii_s = "".join(ch for ch in norm if ord(ch) < 128)
    ascii_s = ascii_s.upper()
    ascii_s = re.sub(r"\s+", " ", ascii_s).strip()
    return ascii_s


def normalize_ticket_category(value: str) -> str:
    """Normalize a raw ticket category to a stable matching key."""
    return _to_ascii_upper(value)


def infer_bb_relationship_segment(category_raw: str | None) -> Tuple[BbRelationshipSegment, str]:
    """Infer canonical BB segment from a ticket category label (best-effort).

    Returns:
        (segment, rule) where `rule` describes the heuristic used.
    """
    norm = normalize_ticket_category(category_raw or "")
    if not norm:
        return (BbRelationshipSegment.DESCONHECIDO, "empty")

    if "FUNCION" in norm and "BB" in norm:
        return (BbRelationshipSegment.FUNCIONARIO_BB, "contains:FUNCION+BB")

    # Prefer the more specific "cartao" bucket when present.
    if "CARTAO" in norm and "BB" in norm:
        return (BbRelationshipSegment.CARTAO_BB, "contains:CARTAO+BB")

    if "CLIENTE" in norm and "BB" in norm:
        return (BbRelationshipSegment.CLIENTE_BB, "contains:CLIENTE+BB")

    # Generic ticket types (inteira/meia etc) are treated as publico geral by default.
    if any(token in norm for token in ["INTEIRA", "MEIA", "DESCONTO", "OUTRAS MEIAS"]):
        return (BbRelationshipSegment.PUBLICO_GERAL, "contains:GENERIC_TICKET")

    return (BbRelationshipSegment.DESCONHECIDO, "fallback:unknown")


def get_segment_mapping(
    session: Session, *, ticket_category_norm: str
) -> Optional[TicketCategorySegmentMap]:
    """Get mapping row by normalized category."""
    key = normalize_ticket_category(ticket_category_norm)
    return session.exec(
        select(TicketCategorySegmentMap).where(TicketCategorySegmentMap.ticket_category_norm == key)
    ).first()


def ensure_segment_mappings(
    session: Session, *, categories_raw: Iterable[str | None]
) -> list[TicketCategorySegmentMap]:
    """Ensure mapping table has entries for all given categories (inferred when missing)."""
    created: list[TicketCategorySegmentMap] = []
    for raw in categories_raw:
        if raw is None:
            continue
        raw_str = str(raw).strip()
        if not raw_str:
            continue
        norm = normalize_ticket_category(raw_str)

        exists = session.exec(
            select(TicketCategorySegmentMap).where(TicketCategorySegmentMap.ticket_category_norm == norm)
        ).first()
        if exists is not None:
            continue

        segment, rule = infer_bb_relationship_segment(raw_str)
        row = TicketCategorySegmentMap(
            ticket_category_raw=raw_str,
            ticket_category_norm=norm,
            segment=segment,
            inferred=True,
            inference_rule=rule,
        )
        session.add(row)
        created.append(row)

    if created:
        session.commit()
        for row in created:
            session.refresh(row)
    return created

