"""Normalizacao de valores para importacao de leads."""

from __future__ import annotations

from datetime import datetime, date


def _clean_digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _parse_date(value: str) -> date | None:
    raw = value.strip()
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_datetime(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
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
    if date_value:
        return datetime.combine(date_value, datetime.min.time())
    return None


def _parse_bool(value: str) -> bool | None:
    raw = value.strip().lower()
    if raw in {"1", "true", "t", "yes", "y", "sim", "s"}:
        return True
    if raw in {"0", "false", "f", "no", "n", "nao"}:
        return False
    return None


def coerce_field(field: str, value: str) -> object | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if field == "email":
        return text.lower()
    if field in {"cpf", "telefone", "cep"}:
        digits = _clean_digits(text)
        return digits or None
    if field == "data_nascimento":
        return _parse_date(text)
    if field == "data_compra":
        return _parse_datetime(text)
    if field == "ingresso_qtd":
        digits = _clean_digits(text)
        if not digits:
            return None
        try:
            return int(digits)
        except ValueError:
            return None
    if field == "opt_in_flag":
        return _parse_bool(text)
    if field == "estado":
        return text.upper()
    return text
