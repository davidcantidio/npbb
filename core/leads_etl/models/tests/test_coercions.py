"""Tests for numeric cell coercion (Excel float CPF, etc.)."""

from __future__ import annotations

import pytest

from core.leads_etl.models._coercions import coerce_lead_field
from core.leads_etl.models.lead_row import etl_payload_to_lead_row


def test_coerce_cpf_float_excel_like_strips_decimal_suffix() -> None:
    assert coerce_lead_field("cpf", 52998224725.0) == "52998224725"


def test_coerce_cpf_int() -> None:
    assert coerce_lead_field("cpf", 52998224725) == "52998224725"


def test_coerce_cpf_string_punctuation_unchanged() -> None:
    assert coerce_lead_field("cpf", "529.982.247-25") == "52998224725"


def test_coerce_cpf_nan_returns_none() -> None:
    assert coerce_lead_field("cpf", float("nan")) is None


def test_coerce_cpf_inf_returns_none() -> None:
    assert coerce_lead_field("cpf", float("inf")) is None


def test_coerce_telefone_float() -> None:
    assert coerce_lead_field("telefone", 11987654321.0) == "11987654321"


def test_etl_payload_cpf_float_materializes_valid_row() -> None:
    row = etl_payload_to_lead_row(
        {
            "cpf": 52998224725.0,
            "evento": "Festival",
        }
    )
    assert row.cpf == "52998224725"


@pytest.mark.parametrize(
    "numpy_ctor",
    [
        pytest.param(lambda v: __import__("numpy").float64(v), id="float64"),
        pytest.param(lambda v: __import__("numpy").int64(v), id="int64"),
    ],
)
def test_coerce_cpf_numpy_numeric(numpy_ctor) -> None:
    pytest.importorskip("numpy")
    assert coerce_lead_field("cpf", numpy_ctor(52998224725)) == "52998224725"
