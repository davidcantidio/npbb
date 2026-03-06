from __future__ import annotations

from datetime import date
import re
import unicodedata

import pandas as pd

from .constants import HEADER_SYNONYMS


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
