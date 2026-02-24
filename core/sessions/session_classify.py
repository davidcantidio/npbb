"""Deterministic session classification for TMJ canonical dimensions.

This module centralizes one controlled domain for session type classification:
- `diurno_gratuito`
- `noturno_show`
- `outro`

Heuristics are intentionally simple and transparent. If a master agenda
provides an explicit type, it can override heuristic inference.
"""

from __future__ import annotations

from enum import Enum
import re
from typing import Any, Mapping
import unicodedata


class SessionType(str, Enum):
    """Controlled session type domain used by canonical dimensions."""

    DIURNO_GRATUITO = "diurno_gratuito"
    NOTURNO_SHOW = "noturno_show"
    OUTRO = "outro"


_SESSION_TYPE_ALIASES: dict[str, SessionType] = {
    "diurno": SessionType.DIURNO_GRATUITO,
    "gratuito": SessionType.DIURNO_GRATUITO,
    "diurno_gratuito": SessionType.DIURNO_GRATUITO,
    "diurno gratuito": SessionType.DIURNO_GRATUITO,
    "noturno": SessionType.NOTURNO_SHOW,
    "show": SessionType.NOTURNO_SHOW,
    "noturno_show": SessionType.NOTURNO_SHOW,
    "noturno show": SessionType.NOTURNO_SHOW,
    "outro": SessionType.OUTRO,
}

_SHOW_KEYWORDS: tuple[str, ...] = (
    "show",
    "noturno",
    "headline",
)

_DAYTIME_KEYWORDS: tuple[str, ...] = (
    "diurno",
    "diurna",
    "gratuito",
    "gratuita",
    "day",
)


def _strip_accents(value: str) -> str:
    """Return `value` without diacritics."""

    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _normalize_text(value: str) -> str:
    """Normalize free text for deterministic keyword matching."""

    cleaned = _strip_accents(str(value or ""))
    cleaned = cleaned.casefold()
    cleaned = re.sub(r"[^a-z0-9_]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _as_mapping(raw: Any) -> Mapping[str, Any]:
    """Return `raw` as mapping when possible, else empty mapping."""

    if isinstance(raw, Mapping):
        return raw
    return {}


def _searchable_text(raw: Any) -> str:
    """Build normalized searchable text from string/mapping raw payload."""

    if isinstance(raw, str):
        return _normalize_text(raw)

    mapping = _as_mapping(raw)
    parts: list[str] = []
    for key in (
        "session_name",
        "sessao",
        "session",
        "title",
        "slide_title",
        "source_id",
        "session_type",
    ):
        value = mapping.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            parts.append(text)

    if parts:
        return _normalize_text(" ".join(parts))
    return _normalize_text(str(raw))


def coerce_session_type(value: str | SessionType) -> SessionType:
    """Coerce one value into the controlled `SessionType` domain.

    Args:
        value: Raw session type value from config/input.

    Returns:
        Coerced `SessionType`.

    Raises:
        ValueError: When value is outside the controlled domain.
    """

    if isinstance(value, SessionType):
        return value

    normalized = _normalize_text(value).replace(" ", "_")
    if normalized in _SESSION_TYPE_ALIASES:
        return _SESSION_TYPE_ALIASES[normalized]
    raise ValueError(
        "session_type invalido: "
        f"{value!r}. Valores aceitos: diurno_gratuito, noturno_show, outro."
    )


def classify_session(
    raw: str | Mapping[str, Any],
    *,
    agenda_session_type: str | SessionType | None = None,
) -> SessionType:
    """Classify one session into controlled domain using deterministic rules.

    Rule order:
    1. `agenda_session_type` override (master agenda).
    2. Explicit `session_type` field in `raw` mapping.
    3. Keyword heuristic over normalized text (`raw`).
    4. Fallback to `outro`.

    Args:
        raw: Raw session text or mapping.
        agenda_session_type: Optional explicit type from master agenda.

    Returns:
        Classified `SessionType`.

    Raises:
        ValueError: When override/explicit value is invalid.
    """

    if agenda_session_type is not None:
        return coerce_session_type(agenda_session_type)

    mapping = _as_mapping(raw)
    explicit_value = mapping.get("session_type")
    if explicit_value is not None and str(explicit_value).strip():
        return coerce_session_type(str(explicit_value))

    text = _searchable_text(raw)
    has_show = any(keyword in text for keyword in _SHOW_KEYWORDS)
    has_daytime = any(keyword in text for keyword in _DAYTIME_KEYWORDS)

    if has_show and not has_daytime:
        return SessionType.NOTURNO_SHOW
    if has_daytime and not has_show:
        return SessionType.DIURNO_GRATUITO
    return SessionType.OUTRO
