from __future__ import annotations

import math
import numbers
from datetime import date, datetime
from enum import Enum
import re
import unicodedata
from typing import Any

import pandas as pd

from .constants import HEADER_SYNONYMS

_KNOWN_INVALID_CPFS = {"12345678909"}
BIRTH_DATE_MIN = date(1900, 1, 1)


class BirthDateIssue(str, Enum):
    MISSING = "missing"
    UNPARSEABLE = "unparseable"
    FUTURE = "future"
    BEFORE_MIN = "before_min"


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def canonicalize_header(header: str) -> str:
    value = strip_accents(str(header).strip().lower())
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_header(header: str) -> str:
    canonical = canonicalize_header(header)
    return HEADER_SYNONYMS.get(canonical, canonical)


def _value_to_str_before_digits(value: Any) -> str:
    """Align with core.leads_etl coercions: Excel/pandas numeric cells must not become '... .0'."""

    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).strip()
    if isinstance(value, numbers.Integral):
        return str(int(value))
    if isinstance(value, numbers.Real):
        fv = float(value)
        if not math.isfinite(fv):
            return ""
        if fv.is_integer():
            return str(int(fv))
    return str(value).strip()


def digits_only(value: Any) -> str:
    return re.sub(r"\D+", "", _value_to_str_before_digits(value))


def normalize_cpf(value: Any) -> str:
    return digits_only(value)


def _calc_cpf_check_digit(numbers: list[int], *, start_weight: int) -> int:
    total = 0
    weight = start_weight
    for number in numbers:
        total += number * weight
        weight -= 1
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(value: Any) -> bool:
    # Keep parity with backend/app/utils/cpf.py without importing the app package.
    digits = normalize_cpf(value)
    if len(digits) != 11:
        return False
    if digits == digits[0] * 11:
        return False
    if digits in _KNOWN_INVALID_CPFS:
        return False

    numbers = [int(character) for character in digits]
    first = _calc_cpf_check_digit(numbers[:9], start_weight=10)
    if first != numbers[9]:
        return False

    second = _calc_cpf_check_digit(numbers[:10], start_weight=11)
    return second == numbers[10]


def normalize_phone(value: Any) -> str:
    return digits_only(value)


def normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def _normalize_dash_spacing(value: str) -> str:
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s*-\s*", " - ", value)
    return re.sub(r"\s+", " ", value).strip()


def city_key(value: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(str(value or "").strip().lower())).strip()


def normalize_local(value: str) -> str:
    normalized = _normalize_dash_spacing(str(value or "").strip())
    return re.sub(r"\s*-\s*", "-", normalized)


def _sanitize_date_input(value: str | object) -> str:
    """Normaliza entrada vinda de CSV/JSON (células vazias, NaN serializado, etc.)."""
    text = str(value or "").strip()
    lowered = text.lower()
    if lowered in {"", "nan", "nat", "none", "null"}:
        return ""
    return text


def _try_parse_excel_serial_date(text: str) -> str | None:
    """Datas armazenadas como número serial do Excel (ex.: 44927 ou 44927.0 em JSON)."""
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        return None
    try:
        serial = float(text.replace(",", "."))
    except ValueError:
        return None
    # Inteiros tipo 20250115 (YYYYMMDD) não são serial OLE; evita interpretação errada.
    if serial >= 10_000_000:
        return None
    # Faixa típica de seriais para datas entre ~1905 e ~2228 (Excel Windows).
    if not (2_000 <= serial <= 120_000):
        return None
    parsed = pd.to_datetime(serial, unit="D", origin="1899-12-30", errors="coerce")
    if pd.isna(parsed):
        return None
    parsed_date = parsed.date()
    if not (date(1900, 1, 1) <= parsed_date <= date(2100, 12, 31)):
        return None
    return parsed_date.isoformat()


def _try_parse_yyyymmdd_compact(text: str) -> str | None:
    if not re.fullmatch(r"\d{8}", text):
        return None
    try:
        return datetime.strptime(text, "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def parse_date(value: str | object) -> str | None:
    text = _sanitize_date_input(value)
    if not text:
        return ""
    iso_match = re.fullmatch(r"\d{4}-\d{2}-\d{2}", text)
    if iso_match:
        try:
            return date.fromisoformat(text).isoformat()
        except ValueError:
            return None
    iso_datetime_match = re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?",
        text,
    )
    if iso_datetime_match:
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=False)
        if pd.isna(parsed):
            return None
        return parsed.date().isoformat()
    compact = _try_parse_yyyymmdd_compact(text)
    if compact is not None:
        return compact
    excel_iso = _try_parse_excel_serial_date(text)
    if excel_iso is not None:
        return excel_iso
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def normalize_data_nascimento(raw: str, *, ref_date: date) -> tuple[str, BirthDateIssue | None]:
    """Normalize `data_nascimento` against the UTC reference date used by the pipeline."""

    parsed = parse_date(raw)
    if parsed == "":
        return "", BirthDateIssue.MISSING
    if parsed is None:
        return "", BirthDateIssue.UNPARSEABLE

    birth_date = date.fromisoformat(parsed)
    if birth_date < BIRTH_DATE_MIN:
        return "", BirthDateIssue.BEFORE_MIN
    if birth_date > ref_date:
        return "", BirthDateIssue.FUTURE
    return birth_date.isoformat(), None
