"""TMJ 2025 session catalog helpers.

This module standardizes:
- session keys (stable identifiers),
- session naming,
- and session type classification (diurno gratuito vs noturno show).

It is intentionally conservative: it will only infer what can be derived from
existing fields (source_id patterns and datetimes). Operators can still
manually create sessions when a day is "expected" but no source exists.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from sqlmodel import Session, select

from app.models.models import EventSession, EventSessionType


TMJ2025_PREFIX = "TMJ2025"

_DAY_WORD_TO_NUM = {
    "DOZE": 12,
    "TREZE": 13,
    "QUATORZE": 14,
}

_RE_DAY_WORD = re.compile(r"_(DOZE|TREZE|QUATORZE)\b", flags=re.IGNORECASE)


def tmj2025_session_key(session_date: date, session_type: EventSessionType) -> str:
    """Build a stable TMJ 2025 session key.

    Examples:
        TMJ2025_20251212_SHOW
        TMJ2025_20251212_DIURNO
    """
    if session_type == EventSessionType.DIURNO_GRATUITO:
        suffix = "DIURNO"
    elif session_type == EventSessionType.NOTURNO_SHOW:
        suffix = "SHOW"
    else:
        suffix = "OUTRO"
    return f"{TMJ2025_PREFIX}_{session_date.strftime('%Y%m%d')}_{suffix}"


def default_session_name(session_date: date, session_type: EventSessionType) -> str:
    """Return a canonical human-readable session name."""
    if session_type == EventSessionType.DIURNO_GRATUITO:
        base = "Diurno gratuito"
    elif session_type == EventSessionType.NOTURNO_SHOW:
        base = "Noturno show"
    else:
        base = "Sessao"
    return f"{base} - {session_date.isoformat()}"


def infer_session_type_from_source_id(source_id: str) -> EventSessionType:
    """Infer session type based on `source_id` convention (best-effort)."""
    sid = (source_id or "").upper()
    if "DIURNO" in sid or "GRATUITO" in sid:
        return EventSessionType.DIURNO_GRATUITO
    if "NOTURNO" in sid or "SHOW" in sid:
        return EventSessionType.NOTURNO_SHOW
    return EventSessionType.OUTRO


def tmj2025_date_from_source_id(source_id: str) -> Optional[date]:
    """Infer TMJ 2025 date from a `source_id` that contains DOZE/TREZE/QUATORZE."""
    sid = (source_id or "").upper()
    m = _RE_DAY_WORD.search(sid)
    if not m:
        return None
    day_word = m.group(1).upper()
    day_num = _DAY_WORD_TO_NUM.get(day_word)
    if not day_num:
        return None
    return date(2025, 12, int(day_num))


def get_or_create_tmj2025_session(
    session: Session,
    *,
    event_id: int | None,
    session_date: date,
    session_type: EventSessionType,
    session_start_at: datetime | None = None,
    session_end_at: datetime | None = None,
    session_name: str | None = None,
    source_of_truth_source_id: str | None = None,
) -> EventSession:
    """Upsert an EventSession for TMJ 2025 using the stable session_key."""
    key = tmj2025_session_key(session_date, session_type)
    row = session.exec(select(EventSession).where(EventSession.session_key == key)).first()
    if row is None:
        row = EventSession(
            event_id=event_id,
            session_key=key,
            session_name=session_name or default_session_name(session_date, session_type),
            session_type=session_type,
            session_date=session_date,
            session_start_at=session_start_at,
            session_end_at=session_end_at,
            source_of_truth_source_id=source_of_truth_source_id,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row

    # Update missing fields (best-effort; do not clobber operator overrides).
    if event_id is not None and row.event_id is None:
        row.event_id = event_id
    if session_name and (not row.session_name or row.session_name == default_session_name(session_date, session_type)):
        row.session_name = session_name
    if session_start_at is not None and row.session_start_at is None:
        row.session_start_at = session_start_at
    if session_end_at is not None and row.session_end_at is None:
        row.session_end_at = session_end_at
    if source_of_truth_source_id and row.source_of_truth_source_id is None:
        row.source_of_truth_source_id = source_of_truth_source_id
    if row.session_type != session_type:
        # Keep the latest inferred type, but only if it was previously OUTRO.
        if row.session_type == EventSessionType.OUTRO:
            row.session_type = session_type

    session.add(row)
    session.commit()
    session.refresh(row)
    return row

