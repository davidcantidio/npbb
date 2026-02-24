"""Safe metric calculators for TMJ audience-derived indicators.

This module centralizes percent math and basic guard validations used by
derived report metrics, avoiding duplicated formulas and inconsistent bounds.
"""

from __future__ import annotations

from math import isfinite
from typing import Mapping


BB_SEGMENT_KEYS: frozenset[str] = frozenset(
    {
        "CLIENTE_BB",
        "CARTAO_BB",
        "FUNCIONARIO_BB",
    }
)


class MetricCalculationError(ValueError):
    """Raised when a derived metric cannot be calculated safely."""


def _coerce_non_negative_number(value: int | float | None, field_name: str) -> float:
    """Coerce one numeric value and enforce non-negative domain.

    Args:
        value: Raw numeric input.
        field_name: Input field name used in actionable error messages.

    Returns:
        Floating-point value in non-negative domain.

    Raises:
        MetricCalculationError: If value is null, not numeric, not finite,
            or is negative.
    """

    if value is None:
        raise MetricCalculationError(
            f"{field_name} invalido: valor nulo. Como corrigir: informar numero >= 0."
        )

    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise MetricCalculationError(
            f"{field_name} invalido: valor nao numerico. Como corrigir: informar numero >= 0."
        ) from exc
    if not isfinite(coerced):
        raise MetricCalculationError(
            f"{field_name} invalido: valor nao finito. Como corrigir: informar numero real."
        )
    if coerced < 0:
        raise MetricCalculationError(
            f"{field_name} invalido: valor negativo. Como corrigir: usar dominio >= 0."
        )
    return coerced


def safe_percent(
    numerator: int | float | None,
    denominator: int | float | None,
    *,
    decimals: int = 4,
) -> float | None:
    """Safely compute `numerator/denominator * 100`.

    Args:
        numerator: Numerator value.
        denominator: Denominator value.
        decimals: Number of decimal places for deterministic rounding.

    Returns:
        Percentage value in 0..+inf rounded to `decimals`, or `None` when
        denominator is zero.

    Raises:
        MetricCalculationError: If inputs are invalid or decimals is negative.
    """

    if decimals < 0:
        raise MetricCalculationError(
            "Parametro decimals invalido. Como corrigir: usar inteiro >= 0."
        )

    num_value = _coerce_non_negative_number(numerator, "numerator")
    den_value = _coerce_non_negative_number(denominator, "denominator")
    if den_value == 0:
        return None

    return round((num_value / den_value) * 100.0, decimals)


def validate_percent_bounds(
    value: float | None,
    *,
    min_value: float = 0.0,
    max_value: float = 100.0,
) -> float | None:
    """Validate percent bounds for derived report metrics.

    Args:
        value: Candidate percent value.
        min_value: Minimum accepted bound (inclusive).
        max_value: Maximum accepted bound (inclusive).

    Returns:
        Original value when valid, preserving `None` as no-data.

    Raises:
        MetricCalculationError: If bounds are invalid or value is outside bounds.
    """

    if min_value > max_value:
        raise MetricCalculationError(
            "Bounds invalidos. Como corrigir: definir min_value <= max_value."
        )

    if value is None:
        return None

    if not isfinite(value):
        raise MetricCalculationError(
            "Percentual invalido: valor nao finito. Como corrigir: validar origem da divisao."
        )

    if value < min_value or value > max_value:
        raise MetricCalculationError(
            f"Percentual fora do intervalo [{min_value}, {max_value}]. "
            "Como corrigir: revisar numerador/denominador e regra da metrica."
        )

    return value


def compute_comparecimento(
    presentes: int | float | None,
    validos: int | float | None,
    *,
    decimals: int = 4,
) -> float | None:
    """Compute comparecimento percent from validated audience counters.

    Formula:
    - comparecimento = presentes / validos * 100

    Args:
        presentes: Number of present attendees.
        validos: Number of validated records used as denominator.
        decimals: Number of decimal places in rounded output.

    Returns:
        Comparecimento percent in [0, 100], or `None` when `validos` is zero.

    Raises:
        MetricCalculationError: If inputs are invalid or output violates bounds.
    """

    presentes_value = _coerce_non_negative_number(presentes, "presentes")
    validos_value = _coerce_non_negative_number(validos, "validos")
    if validos_value == 0:
        return None
    if presentes_value > validos_value:
        raise MetricCalculationError(
            "presentes maior que validos. Como corrigir: reconciliar fonte de acesso."
        )

    result = safe_percent(presentes_value, validos_value, decimals=decimals)
    return validate_percent_bounds(result)


def compute_share_bb(
    segment_counts: Mapping[str, int | float | None],
    *,
    decimals: int = 4,
) -> float | None:
    """Compute BB share percent from segment count distribution.

    BB share definition:
    - numerator: sum of CLIENTE_BB + CARTAO_BB + FUNCIONARIO_BB
    - denominator: sum of all segments

    Args:
        segment_counts: Segment -> count mapping.
        decimals: Number of decimal places in rounded output.

    Returns:
        BB share percent in [0, 100], or `None` when total is zero.

    Raises:
        MetricCalculationError: If inputs are empty/invalid or output is invalid.
    """

    if not segment_counts:
        raise MetricCalculationError(
            "segment_counts vazio. Como corrigir: informar contagens por segmento."
        )

    bb_total = 0.0
    total = 0.0
    for raw_key, raw_count in segment_counts.items():
        count_value = _coerce_non_negative_number(raw_count, f"segment_counts[{raw_key!r}]")
        total += count_value
        normalized_key = str(raw_key or "").strip().upper()
        if normalized_key in BB_SEGMENT_KEYS:
            bb_total += count_value

    if total == 0:
        return None
    if bb_total > total:
        raise MetricCalculationError(
            "Soma BB maior que total de segmentos. Como corrigir: revisar agregacoes."
        )

    result = safe_percent(bb_total, total, decimals=decimals)
    return validate_percent_bounds(result)
