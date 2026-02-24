"""Deterministic session naming helpers.

This module normalizes heterogeneous session labels into stable names that can
be used across staging/canonical/report layers.
"""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any, Mapping

from .session_classify import SessionType, classify_session


_DATE_DDMMYYYY_RE = re.compile(
    r"\b(?P<day>\d{1,2})/(?P<month>\d{1,2})(?:/(?P<year>\d{2,4}))?\b"
)
_DATE_ISO_RE = re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\b")
_SPACE_RE = re.compile(r"\s+")


def _as_mapping(raw: Any) -> Mapping[str, Any]:
    """Return `raw` as mapping when possible, else empty mapping."""

    if isinstance(raw, Mapping):
        return raw
    return {}


def _clean_text(value: str) -> str:
    """Return text trimmed and with collapsed spaces."""

    return _SPACE_RE.sub(" ", str(value or "").strip())


def _extract_best_text(raw: str | Mapping[str, Any]) -> str:
    """Extract best candidate text for session naming from raw payload."""

    if isinstance(raw, str):
        return _clean_text(raw)

    mapping = _as_mapping(raw)
    for key in ("session_name", "sessao", "session", "title", "slide_title", "source_id"):
        value = mapping.get(key)
        if value is None:
            continue
        text = _clean_text(str(value))
        if text:
            return text
    return _clean_text(str(raw))


def _coerce_date_value(value: Any) -> date | None:
    """Coerce date-like values into `date`."""

    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = _clean_text(str(value))
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace(" ", "T")).date()
    except ValueError:
        return None


def _extract_date_from_text(text: str) -> date | None:
    """Extract date from `text` supporting `dd/mm[/yyyy]` and `yyyy-mm-dd`."""

    match_iso = _DATE_ISO_RE.search(text)
    if match_iso:
        try:
            return date(
                int(match_iso.group("year")),
                int(match_iso.group("month")),
                int(match_iso.group("day")),
            )
        except ValueError:
            return None

    match_ddmmyyyy = _DATE_DDMMYYYY_RE.search(text)
    if not match_ddmmyyyy:
        return None

    day = int(match_ddmmyyyy.group("day"))
    month = int(match_ddmmyyyy.group("month"))
    year_raw = match_ddmmyyyy.group("year")
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


def _extract_session_date(raw: str | Mapping[str, Any], text_hint: str) -> date | None:
    """Extract session date from structured fields first, then free text."""

    mapping = _as_mapping(raw)
    for key in (
        "session_date",
        "date",
        "datetime",
        "dt_hr_compra",
        "purchase_at",
        "data",
        "data_sessao",
    ):
        parsed = _coerce_date_value(mapping.get(key))
        if parsed is not None:
            return parsed

    return _extract_date_from_text(text_hint)


def normalize_session_name(
    raw: str | Mapping[str, Any],
    *,
    agenda_session_type: str | SessionType | None = None,
) -> str:
    """Normalize one session label into deterministic canonical name.

    Args:
        raw: Raw session string or mapping with session hints.
        agenda_session_type: Optional explicit session type override.

    Returns:
        Canonical session name with normalized spacing and stable label.
        Examples:
        - `noturno show - 2025-12-12`
        - `diurno gratuito - 2025-12-12`
        - `sessao sem nome`

    Raises:
        ValueError: When explicit/override session type is invalid.
    """

    text = _extract_best_text(raw)
    if not text:
        text = "sessao sem nome"

    session_type = classify_session(raw, agenda_session_type=agenda_session_type)
    session_date = _extract_session_date(raw, text)

    if session_type == SessionType.NOTURNO_SHOW:
        base_name = "noturno show"
    elif session_type == SessionType.DIURNO_GRATUITO:
        base_name = "diurno gratuito"
    else:
        base_name = text.casefold()

    if session_date is not None:
        return f"{base_name} - {session_date.isoformat()}"
    return _clean_text(base_name)

