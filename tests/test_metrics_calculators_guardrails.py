"""Unit tests for metric calculators and mart guardrails."""

from __future__ import annotations

import math

import pytest

from core.metrics import (
    MetricCalculationError,
    MetricGuardrailError,
    compute_comparecimento,
    compute_share_bb,
    enforce_mart_metric_guardrails,
    safe_percent,
    validate_mart_metric_guardrails,
    validate_percent_bounds,
)


def test_safe_percent_and_comparecimento_calculate_stable_percentages() -> None:
    """Percent calculators should compute deterministic rounded values."""

    assert safe_percent(50, 200, decimals=2) == 25.00
    assert compute_comparecimento(80, 100, decimals=1) == 80.0


def test_safe_percent_and_comparecimento_handle_zero_or_invalid_domains() -> None:
    """Percent calculators should reject invalid domains and protect zero denominators."""

    assert safe_percent(1, 0) is None
    assert compute_comparecimento(0, 0) is None

    with pytest.raises(MetricCalculationError, match="presentes maior que validos"):
        compute_comparecimento(101, 100)


def test_validate_percent_bounds_rejects_non_finite_or_out_of_range() -> None:
    """Percent bound validator should fail on NaN and out-of-range values."""

    assert validate_percent_bounds(42.5) == 42.5
    assert validate_percent_bounds(None) is None

    with pytest.raises(MetricCalculationError, match="fora do intervalo"):
        validate_percent_bounds(120.0)

    with pytest.raises(MetricCalculationError, match="nao finito"):
        validate_percent_bounds(math.nan)


def test_compute_share_bb_uses_bb_segments_only() -> None:
    """BB share should use CLIENTE/CARTAO/FUNCIONARIO segments as numerator."""

    result = compute_share_bb(
        {
            "CLIENTE_BB": 20,
            "CARTAO_BB": 15,
            "FUNCIONARIO_BB": 5,
            "PUBLICO_GERAL": 60,
        },
        decimals=2,
    )
    assert result == 40.00


def test_compute_share_bb_rejects_invalid_counts() -> None:
    """Share computation should fail for negative or empty segment distributions."""

    with pytest.raises(MetricCalculationError, match="segment_counts vazio"):
        compute_share_bb({})

    with pytest.raises(MetricCalculationError, match="valor negativo"):
        compute_share_bb({"CLIENTE_BB": -1})


def test_guardrails_flag_missing_metric_type_and_unlabeled_mixed_sources() -> None:
    """Mart guardrails should produce actionable findings for required labels."""

    findings = validate_mart_metric_guardrails(
        [
            {
                "metric_key": "publico_total",
                "metric_type": "",
                "source_name": "pdf_access",
                "source_label": "",
            },
            {
                "metric_key": "share_bb",
                "metric_type": "percentual",
                "source_name": "xlsx_optin",
                "source_label": "",
            },
            {
                "metric_key": "share_bb",
                "metric_type": "percentual",
                "source_name": "pdf_access",
                "source_label": "",
            },
        ]
    )

    codes = {finding.code for finding in findings}
    assert "METRIC_TYPE_MISSING" in codes
    assert "MIXED_SOURCES_WITHOUT_LABEL" in codes


def test_guardrails_pass_with_metric_type_and_source_label() -> None:
    """Guardrail enforcement should pass when rows are fully labeled."""

    rows = [
        {
            "metric_key": "share_bb",
            "metric_type": "percentual",
            "source_name": "xlsx_optin",
            "source_label": "opt-in",
        },
        {
            "metric_key": "share_bb",
            "metric_type": "percentual",
            "source_name": "pdf_access",
            "source_label": "acesso",
        },
    ]
    assert validate_mart_metric_guardrails(rows) == []
    enforce_mart_metric_guardrails(rows)


def test_guardrails_enforce_raises_with_actionable_summary() -> None:
    """Guardrail enforce API should fail with actionable summary when invalid."""

    with pytest.raises(MetricGuardrailError, match="Findings"):
        enforce_mart_metric_guardrails(
            [
                {
                    "metric_key": "publico_total",
                    "metric_type": "",
                    "source_name": "pdf_access",
                    "source_label": "",
                }
            ]
        )

