"""Helpers to format and parse lineage location references.

This module standardizes `location_value` representation for lineage entries:
- `page:{number}`
- `slide:{number}`
- `sheet:{name}`
- `range:{start_cell}:{end_cell}`
"""

from __future__ import annotations

import re
from typing import Any

from .types import LOCATION_TYPES, LocationType


_CELL_RE = re.compile(r"^[A-Z]{1,3}[1-9][0-9]*$")
_PAGE_RE = re.compile(r"^page:([1-9][0-9]*)$")
_SLIDE_RE = re.compile(r"^slide:([1-9][0-9]*)$")
_SHEET_RE = re.compile(r"^sheet:(.+)$")
_RANGE_RE = re.compile(
    r"^range:([A-Z]{1,3}[1-9][0-9]*):([A-Z]{1,3}[1-9][0-9]*)$",
    flags=re.IGNORECASE,
)


def _coerce_location_type(location_type: str) -> LocationType:
    """Normalize and validate location type domain.

    Args:
        location_type: Raw location type input.

    Returns:
        Normalized location type in lowercase.

    Raises:
        ValueError: If location type is not supported.
    """

    normalized = (location_type or "").strip().lower()
    if normalized not in LOCATION_TYPES:
        raise ValueError(
            "location_type invalido. "
            "Como corrigir: usar um tipo suportado em {page, slide, sheet, range}."
        )
    return normalized  # type: ignore[return-value]


def _require_positive_int(raw: Any, *, field_name: str) -> int:
    """Validate a positive integer value used in page/slide references.

    Args:
        raw: Value to validate.
        field_name: Field name for actionable errors.

    Returns:
        Positive integer value.

    Raises:
        ValueError: If value is not a positive integer.
    """

    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} invalido: {raw!r}. "
            f"Como corrigir: informar {field_name} como inteiro positivo."
        ) from exc

    if value <= 0:
        raise ValueError(
            f"{field_name} invalido: {value}. "
            f"Como corrigir: informar {field_name} maior que zero."
        )
    return value


def _normalize_sheet_name(raw: Any) -> str:
    """Normalize and validate sheet name text.

    Args:
        raw: Raw sheet name.

    Returns:
        Lowercase, trimmed sheet name with normalized internal spaces.

    Raises:
        ValueError: If resulting name is empty.
    """

    name = re.sub(r"\s+", " ", str(raw or "")).strip().lower()
    if not name:
        raise ValueError("sheet name vazio. Como corrigir: informar nome de aba nao vazio.")
    return name


def _normalize_cell(raw: Any, *, field_name: str) -> str:
    """Normalize and validate spreadsheet cell reference.

    Args:
        raw: Raw cell input (for example: A1).
        field_name: Name for actionable error messages.

    Returns:
        Uppercase validated cell reference.

    Raises:
        ValueError: If cell reference does not match A1 notation.
    """

    cell = str(raw or "").strip().upper()
    if not _CELL_RE.match(cell):
        raise ValueError(
            f"{field_name} invalido: {raw!r}. "
            "Como corrigir: usar referencia A1 valida (ex.: A1, B20, AA300)."
        )
    return cell


def format_location(location_type: str, parts: dict[str, Any]) -> str:
    """Format a normalized `location_value` for lineage storage.

    Args:
        location_type: One of `page`, `slide`, `sheet`, `range`.
        parts: Components expected by type:
            - page: `{\"number\": int}`
            - slide: `{\"number\": int}`
            - sheet: `{\"name\": str}`
            - range: `{\"start\": str, \"end\": str}`

    Returns:
        Canonical location string.

    Raises:
        ValueError: If type is invalid or required parts are missing/invalid.
    """

    kind = _coerce_location_type(location_type)
    if kind == "page":
        number = _require_positive_int(parts.get("number"), field_name="page number")
        return f"page:{number}"
    if kind == "slide":
        number = _require_positive_int(parts.get("number"), field_name="slide number")
        return f"slide:{number}"
    if kind == "sheet":
        name = _normalize_sheet_name(parts.get("name"))
        return f"sheet:{name}"

    start = _normalize_cell(parts.get("start"), field_name="start cell")
    end = _normalize_cell(parts.get("end"), field_name="end cell")
    return f"range:{start}:{end}"


def parse_location(location_type: str, value: str) -> dict[str, Any]:
    """Parse a formatted `location_value` into structured components.

    Args:
        location_type: One of `page`, `slide`, `sheet`, `range`.
        value: Canonical location string to parse.

    Returns:
        Dictionary of parsed parts:
            - page/slide: `{\"number\": int}`
            - sheet: `{\"name\": str}`
            - range: `{\"start\": str, \"end\": str}`

    Raises:
        ValueError: If value does not match canonical format for the type.
    """

    kind = _coerce_location_type(location_type)
    raw = (value or "").strip()
    if kind == "page":
        match = _PAGE_RE.match(raw)
        if not match:
            raise ValueError(
                f"location_value invalido para page: {value!r}. "
                "Como corrigir: usar formato page:<inteiro_positivo>."
            )
        return {"number": int(match.group(1))}

    if kind == "slide":
        match = _SLIDE_RE.match(raw)
        if not match:
            raise ValueError(
                f"location_value invalido para slide: {value!r}. "
                "Como corrigir: usar formato slide:<inteiro_positivo>."
            )
        return {"number": int(match.group(1))}

    if kind == "sheet":
        match = _SHEET_RE.match(raw)
        if not match:
            raise ValueError(
                f"location_value invalido para sheet: {value!r}. "
                "Como corrigir: usar formato sheet:<nome_da_aba>."
            )
        return {"name": _normalize_sheet_name(match.group(1))}

    match = _RANGE_RE.match(raw)
    if not match:
        raise ValueError(
            f"location_value invalido para range: {value!r}. "
            "Como corrigir: usar formato range:<CELA_INICIO>:<CELA_FIM>."
        )
    return {"start": match.group(1).upper(), "end": match.group(2).upper()}
