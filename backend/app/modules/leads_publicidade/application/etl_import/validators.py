"""Validation helpers for normalized ETL lead payloads."""

from __future__ import annotations

import re
from collections.abc import Mapping


MALFORMED_EMAIL_REASON = "email malformado"
MISSING_CPF_REASON = "CPF ausente"
INVALID_CPF_REASON = "CPF inválido"

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(value: object) -> bool:
    """Return True when a provided normalized email has a basic valid shape."""

    if not isinstance(value, str):
        return False
    return bool(_EMAIL_RE.fullmatch(value))


def _calculate_cpf_check_digit(numbers: list[int], *, start_weight: int) -> int:
    total = sum(
        number * weight
        for number, weight in zip(numbers, range(start_weight, 1, -1), strict=False)
    )
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(value: object) -> bool:
    """Return True when a normalized CPF has valid Mod 11 check digits."""

    if not isinstance(value, str):
        return False
    if len(value) != 11 or not value.isdigit():
        return False
    if value == value[0] * 11:
        return False

    numbers = [int(character) for character in value]
    first = _calculate_cpf_check_digit(numbers[:9], start_weight=10)
    if first != numbers[9]:
        return False

    second = _calculate_cpf_check_digit(numbers[:10], start_weight=11)
    return second == numbers[10]


def validate_normalized_lead_payload(payload: Mapping[str, object]) -> list[str]:
    """Return deterministic validation failure reasons for a normalized lead payload."""

    reasons: list[str] = []
    email = payload.get("email")
    cpf = payload.get("cpf")

    if email not in (None, "") and not is_valid_email(email):
        reasons.append(MALFORMED_EMAIL_REASON)
    if not is_valid_cpf(cpf):
        reasons.append(MISSING_CPF_REASON if cpf in (None, "") else INVALID_CPF_REASON)

    return reasons


def format_validation_reasons(reasons: list[str]) -> str:
    """Format validation reasons for failed_rows reporting."""

    return "; ".join(reasons)
