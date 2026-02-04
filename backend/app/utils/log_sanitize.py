"""Helpers para sanitizar logs e evitar vazamento de PII."""

from __future__ import annotations

import re

MAX_LOG_LEN = 300

EMAIL_RE = re.compile(r"\b([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)
CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
PHONE_RE = re.compile(r"\b(?:\+?55\s*)?\(?\d{2}\)?\s*\d{4,5}-?\d{4}\b")
LONG_DIGITS_RE = re.compile(r"\b\d{5,}\b")


def _mask_email(match: re.Match[str]) -> str:
    local = match.group(1) or ""
    domain = match.group(2) or ""
    if not local:
        return f"***@{domain}"
    return f"{local[0]}***@{domain}"


def _mask_long_digits(match: re.Match[str]) -> str:
    value = match.group(0)
    tail = value[-2:] if len(value) >= 2 else ""
    return f"***{tail}"


def sanitize_text(text: str) -> str:
    """Mascara PII comum e limita o tamanho do log."""
    if not text:
        return ""
    sanitized = EMAIL_RE.sub(_mask_email, text)
    sanitized = CPF_RE.sub("***.***.***-**", sanitized)
    sanitized = PHONE_RE.sub("** ****-****", sanitized)
    sanitized = LONG_DIGITS_RE.sub(_mask_long_digits, sanitized)
    sanitized = sanitized.strip()
    if len(sanitized) > MAX_LOG_LEN:
        sanitized = sanitized[: MAX_LOG_LEN - 3].rstrip() + "..."
    return sanitized


def sanitize_exception(exc: Exception) -> str:
    """Retorna o tipo da excecao + mensagem sanitizada (sem PII)."""
    if exc is None:
        return ""
    message = sanitize_text(str(exc))
    name = type(exc).__name__
    if message:
        combined = f"{name}: {message}"
    else:
        combined = name
    if len(combined) > MAX_LOG_LEN:
        combined = combined[: MAX_LOG_LEN - 3].rstrip() + "..."
    return combined
