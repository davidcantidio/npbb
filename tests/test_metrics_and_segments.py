"""Unit tests for metrics, segments, and basic reconciliation guardrails."""

from __future__ import annotations

import math

import pytest

from core.metrics import (
    MetricCalculationError,
    MetricGuardrailError,
    compute_comparecimento,
    enforce_mart_metric_guardrails,
    safe_percent,
    validate_mart_metric_guardrails,
    validate_percent_bounds,
)
from etl.transform.segment_mapper import (
    Segment,
    map_ticket_category_to_segment,
    map_ticket_category_with_finding,
)


def test_safe_percent_handles_zero_denominator_and_null_inputs() -> None:
    """safe_percent should return None for denominator zero and fail on nulls."""

    assert safe_percent(10, 0) is None

    with pytest.raises(MetricCalculationError, match="valor nulo"):
        safe_percent(None, 10)

    with pytest.raises(MetricCalculationError, match="valor nulo"):
        safe_percent(10, None)


def test_safe_percent_and_bounds_cover_valid_and_invalid_percentages() -> None:
    """Percent helper and bounds validator should enforce report-safe values."""

    value = safe_percent(25, 100, decimals=2)
    assert value == 25.00
    assert validate_percent_bounds(value) == 25.00

    with pytest.raises(MetricCalculationError, match="fora do intervalo"):
        validate_percent_bounds(120.0)

    with pytest.raises(MetricCalculationError, match="nao finito"):
        validate_percent_bounds(math.nan)


def test_comparecimento_reconciliation_rejects_presentes_maior_que_validos() -> None:
    """Reconciliation should fail when presentes exceeds validos."""

    assert compute_comparecimento(70, 100, decimals=1) == 70.0

    with pytest.raises(MetricCalculationError, match="presentes maior que validos"):
        compute_comparecimento(101, 100)


def test_segment_mapper_handles_known_and_unknown_categories() -> None:
    """Segment mapper should return mapped segment or unknown with finding."""

    assert map_ticket_category_to_segment("Funcionarios BB") == Segment.FUNCIONARIO_BB
    assert map_ticket_category_to_segment("Categoria nao catalogada") == Segment.DESCONHECIDO

    unknown = map_ticket_category_with_finding("Categoria nao catalogada")
    assert unknown.segment == Segment.DESCONHECIDO
    assert unknown.finding is not None
    assert unknown.finding.code == "SEGMENT_CATEGORY_UNKNOWN"


def test_guardrails_require_metric_type_and_block_unlabeled_rows() -> None:
    """Guardrails should detect missing metric_type and block enforcement."""

    rows = [
        {
            "metric_key": "comparecimento",
            "metric_type": "",
            "source_name": "pdf_access_control",
            "source_label": "controle acesso",
        }
    ]
    findings = validate_mart_metric_guardrails(rows)
    assert len(findings) == 1
    assert findings[0].code == "METRIC_TYPE_MISSING"

    with pytest.raises(MetricGuardrailError):
        enforce_mart_metric_guardrails(rows)
