"""Resolve staging records to canonical `event_sessions`.

This module centralizes session-resolution logic for staging loaders. The goal
is to map heterogeneous raw fields (XLSX/PDF/PPTX) into one canonical
`session_id` used by marts/reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
import sys
from typing import Any, Mapping

from sqlmodel import Session, select

from app.models.models import EventSession, EventSessionType
from app.services.tmj_sessions import (
    default_session_name,
    get_or_create_tmj2025_session,
    tmj2025_date_from_source_id,
)

try:  # pragma: no cover - import style depends on process cwd
    from core.sessions import SessionType, classify_session
except ModuleNotFoundError:  # pragma: no cover
    ROOT_DIR = Path(__file__).resolve().parents[3]
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    from core.sessions import SessionType, classify_session


_DATE_IN_TEXT_RE = re.compile(r"\b(?P<day>\d{1,2})/(?P<month>\d{1,2})(?:/(?P<year>\d{2,4}))?\b")


@dataclass(frozen=True)
class SessionResolutionFinding:
    """Actionable finding generated during session resolution."""

    code: str
    message: str
    details: dict[str, Any]


@dataclass(frozen=True)
class SessionResolution:
    """Session-resolution result for one staging record."""

    event_id: int | None
    session_id: int | None
    session_key: str | None
    finding: SessionResolutionFinding | None


def _coerce_date(value: Any) -> date | None:
    """Coerce values into `date` when possible."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace(" ", "T")).date()
    except ValueError:
        return None


def _extract_date_from_text(text: str) -> date | None:
    """Extract `dd/mm[/yyyy]` date from free text."""
    if not text:
        return None
    match = _DATE_IN_TEXT_RE.search(text)
    if not match:
        return None
    day = int(match.group("day"))
    month = int(match.group("month"))
    year_raw = match.group("year")
    if year_raw is None:
        year = 2025
    else:
        year = int(year_raw)
        if year < 100:
            year += 2000
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _pick_session_name(raw_session_fields: Mapping[str, Any]) -> str | None:
    """Pick the best human-readable session name from raw fields."""
    for key in ("session_name", "sessao", "session", "slide_title", "title"):
        value = raw_session_fields.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _resolve_session_date(raw_session_fields: Mapping[str, Any], source_id: str) -> date | None:
    """Resolve session date from explicit fields, text hints or source ID."""
    for key in ("session_date", "dt_hr_compra", "purchase_at", "datetime", "date"):
        parsed = _coerce_date(raw_session_fields.get(key))
        if parsed is not None:
            return parsed
    for text_key in ("session_name", "sessao", "slide_title", "title"):
        text = str(raw_session_fields.get(text_key) or "").strip()
        parsed = _extract_date_from_text(text)
        if parsed is not None:
            return parsed
    return tmj2025_date_from_source_id(source_id)


def _resolve_session_type(raw_session_fields: Mapping[str, Any], source_id: str) -> EventSessionType:
    """Resolve canonical session type using centralized deterministic classifier."""

    payload: dict[str, Any] = dict(raw_session_fields)
    payload["source_id"] = source_id
    agenda_override = raw_session_fields.get("agenda_session_type")
    session_type = classify_session(
        payload,
        agenda_session_type=str(agenda_override) if agenda_override is not None else None,
    )

    if session_type == SessionType.DIURNO_GRATUITO:
        return EventSessionType.DIURNO_GRATUITO
    if session_type == SessionType.NOTURNO_SHOW:
        return EventSessionType.NOTURNO_SHOW
    return EventSessionType.OUTRO


def _match_candidates_by_name(candidates: list[EventSession], session_name: str | None) -> list[EventSession]:
    """Filter candidate sessions by name similarity when available."""
    if not session_name:
        return candidates
    expected = session_name.casefold()
    exact = [row for row in candidates if row.session_name.casefold() == expected]
    if exact:
        return exact
    partial = [row for row in candidates if expected in row.session_name.casefold()]
    return partial or candidates


def resolve_session_reference(
    session: Session,
    event_id: int | None,
    raw_session_fields: Mapping[str, Any],
) -> SessionResolution:
    """Resolve or create canonical `event_sessions` row for one raw record.

    Args:
        session: Open SQLModel session.
        event_id: Optional event identifier associated with this record.
        raw_session_fields: Raw fields from extractor payload.

    Returns:
        SessionResolution with `session_id` when resolved; otherwise a finding.
    """

    source_id = str(raw_session_fields.get("source_id") or "").strip().upper()
    session_name = _pick_session_name(raw_session_fields)
    session_date = _resolve_session_date(raw_session_fields, source_id)
    session_type = _resolve_session_type(raw_session_fields, source_id)

    if session_date is None:
        finding = SessionResolutionFinding(
            code="SESSION_DATE_MISSING",
            message=(
                "Nao foi possivel resolver session_id: data da sessao ausente. "
                "Como corrigir: informar timestamp/data ou incluir dd/mm no nome da sessao."
            ),
            details={"source_id": source_id, "session_name": session_name},
        )
        return SessionResolution(
            event_id=event_id,
            session_id=None,
            session_key=None,
            finding=finding,
        )

    stmt = select(EventSession).where(
        EventSession.session_date == session_date,
        EventSession.session_type == session_type,
    )
    if event_id is not None:
        stmt = stmt.where(EventSession.event_id == event_id)
    candidates = session.exec(stmt).all()
    candidates = _match_candidates_by_name(candidates, session_name)

    if len(candidates) == 1:
        resolved = candidates[0]
        return SessionResolution(
            event_id=event_id,
            session_id=int(resolved.id),
            session_key=resolved.session_key,
            finding=None,
        )

    if len(candidates) > 1:
        finding = SessionResolutionFinding(
            code="SESSION_AMBIGUOUS",
            message=(
                "Nao foi possivel resolver session_id: mais de uma sessao candidata encontrada. "
                "Como corrigir: informar sessao com nome mais especifico ou chave de sessao."
            ),
            details={
                "source_id": source_id,
                "session_name": session_name,
                "session_date": session_date.isoformat(),
                "session_type": session_type.value,
                "candidate_ids": [int(row.id) for row in candidates if row.id is not None],
            },
        )
        return SessionResolution(
            event_id=event_id,
            session_id=None,
            session_key=None,
            finding=finding,
        )

    created = get_or_create_tmj2025_session(
        session,
        event_id=event_id,
        session_date=session_date,
        session_type=session_type,
        session_name=session_name or default_session_name(session_date, session_type),
        source_of_truth_source_id=None,
    )
    return SessionResolution(
        event_id=event_id,
        session_id=int(created.id),
        session_key=created.session_key,
        finding=None,
    )


def resolve_session_id(
    session: Session,
    event_id: int | None,
    raw_session_fields: Mapping[str, Any],
) -> int | None:
    """Resolve one `session_id` from raw staging fields.

    Args:
        session: Open SQLModel session.
        event_id: Optional event identifier.
        raw_session_fields: Raw extractor fields.

    Returns:
        Resolved `session_id` or `None` when unresolved.
    """

    result = resolve_session_reference(session, event_id, raw_session_fields)
    return result.session_id
