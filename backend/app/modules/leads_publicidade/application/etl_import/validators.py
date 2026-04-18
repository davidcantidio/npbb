"""Validation helpers for normalized ETL lead payloads."""

from __future__ import annotations

import re
from collections.abc import Mapping

from app.utils.cpf import is_valid_cpf as _is_valid_cpf_any_format


MALFORMED_EMAIL_REASON = "email malformado"
MISSING_CPF_REASON = "CPF ausente"
INVALID_CPF_REASON = "CPF inválido"

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(value: object) -> bool:
    """Return True when a provided normalized email has a basic valid shape."""

    if not isinstance(value, str):
        return False
    return bool(_EMAIL_RE.fullmatch(value))


def is_valid_cpf(value: object) -> bool:
    """Return True when a normalized CPF passes the canonical backend rules."""

    if not isinstance(value, str):
        return False
    if len(value) != 11 or not value.isdigit():
        return False
    return _is_valid_cpf_any_format(value)


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
