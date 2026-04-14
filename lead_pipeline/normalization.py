from __future__ import annotations

from datetime import date
from enum import Enum
import re
import unicodedata

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


def digits_only(value: str) -> str:
    return re.sub(r"\D+", "", str(value or ""))


def normalize_cpf(value: str) -> str:
    return digits_only(value)


def _calc_cpf_check_digit(numbers: list[int], *, start_weight: int) -> int:
    total = 0
    weight = start_weight
    for number in numbers:
        total += number * weight
        weight -= 1
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(value: str) -> bool:
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


def normalize_phone(value: str) -> str:
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


def parse_date(value: str) -> str | None:
    text = str(value or "").strip()
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
