"""Pure coercion helpers for the canonical lead-row contract."""

from __future__ import annotations

import math
import numbers
from datetime import date, datetime
from typing import Any


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _value_to_str_for_digit_fields(value: Any) -> str | None:
    """Excel/pandas often yield int/float for CPF/telefone/CEP cells.

    ``str(52998224725.0)`` would add an extra digit when stripping non-digits;
    whole-valued floats/ints are stringified without a decimal part.
    """

    if value is None:
        return None
    if isinstance(value, bool):
        text = str(value).strip()
        return text or None
    if isinstance(value, numbers.Integral):
        return str(int(value))
    if isinstance(value, numbers.Real):
        fv = float(value)
        if not math.isfinite(fv):
            return None
        if fv.is_integer():
            return str(int(fv))
    text = str(value).strip()
    return text or None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    raw = _normalize_text(value)
    if raw is None:
        return None

    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    raw = _normalize_text(value)
    if raw is None:
        return None

    for fmt in (
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    date_value = _parse_date(raw)
    if date_value is not None:
        return datetime.combine(date_value, datetime.min.time())
    return None


def _parse_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value

    raw = _normalize_text(value)
    if raw is None:
        return None

    lowered = raw.lower()
    if lowered in {"1", "true", "t", "yes", "y", "sim", "s"}:
        return True
    if lowered in {"0", "false", "f", "no", "n", "nao"}:
        return False
    return None


def _coerce_ingresso_qtd(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value

    raw = _normalize_text(value)
    if raw is None:
        return None

    digits = _clean_digits(raw)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def coerce_lead_field(field: str, value: Any) -> Any | None:
    """Coerce one lead field preserving current backend import semantics."""

    name = str(field or "").strip()
    if not name:
        return _normalize_text(value)

    if name == "email":
        raw = _normalize_text(value)
        return raw.lower() if raw else None

    if name in {"cpf", "telefone", "cep"}:
        raw = _value_to_str_for_digit_fields(value)
        if raw is None:
            return None
        digits = _clean_digits(raw)
        return digits or None

    if name == "data_nascimento":
        return _parse_date(value)

    if name == "data_compra":
        return _parse_datetime(value)

    if name == "ingresso_qtd":
        return _coerce_ingresso_qtd(value)

    if name in {"opt_in_flag", "is_cliente_bb", "is_cliente_estilo"}:
        return _parse_bool(value)

    if name == "estado":
        raw = _normalize_text(value)
        return raw.upper() if raw else None

    return _normalize_text(value)
