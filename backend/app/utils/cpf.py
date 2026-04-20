"""Validacao e normalizacao de CPF (Cadastro de Pessoa Fisica).

Regras (MVP):
- Aceita CPF com ou sem pontuacao (ex.: "529.982.247-25" ou "52998224725").
- Normaliza para 11 digitos (somente numeros).
- Valida digitos verificadores (mod 11) + rejeita CPFs obviamente invalidos:
  - todos os digitos iguais (ex.: 00000000000)
  - sequencia conhecida usada como placeholder: 12345678909
"""

from __future__ import annotations

import math
import numbers
import re
from typing import Any

_NON_DIGITS_RE = re.compile(r"\D+")
_KNOWN_INVALID = {"12345678909"}


def _value_to_str_before_digits(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).strip()
    if isinstance(value, numbers.Integral):
        return str(int(value))
    if isinstance(value, numbers.Real):
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            return ""
        if numeric_value.is_integer():
            return str(int(numeric_value))
    return str(value).strip()


def normalize_cpf(value: Any) -> str:
    """Remove pontuacao e retorna somente numeros (pode retornar string vazia)."""
    text = _value_to_str_before_digits(value)
    return _NON_DIGITS_RE.sub("", text).strip()


def _calc_check_digit(numbers: list[int], *, start_weight: int) -> int:
    total = 0
    weight = start_weight
    for n in numbers:
        total += n * weight
        weight -= 1
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(value: Any, *, allow_known_invalid: bool = False) -> bool:
    """Retorna True se o CPF for valido (com base nos digitos verificadores)."""
    digits = normalize_cpf(value)
    if len(digits) != 11:
        return False
    if digits == digits[0] * 11:
        return False
    if not allow_known_invalid and digits in _KNOWN_INVALID:
        return False

    try:
        numbers = [int(ch) for ch in digits]
    except ValueError:
        return False

    first = _calc_check_digit(numbers[:9], start_weight=10)
    if first != numbers[9]:
        return False

    second = _calc_check_digit(numbers[:10], start_weight=11)
    if second != numbers[10]:
        return False

    return True


def validate_and_normalize_cpf(value: Any) -> str:
    """Valida e retorna CPF normalizado (11 digitos).

    Levanta ValueError em caso invalido (para uso em schemas Pydantic).
    """
    digits = normalize_cpf(value)
    if not is_valid_cpf(digits):
        raise ValueError("CPF invalido")
    return digits
