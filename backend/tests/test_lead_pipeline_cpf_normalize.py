"""lead_pipeline CPF normalization parity with Excel numeric cells."""

from __future__ import annotations

import math

import pytest

from lead_pipeline.normalization import digits_only, is_valid_cpf, normalize_cpf


def test_normalize_cpf_float_excel_cell() -> None:
    assert normalize_cpf(52998224725.0) == "52998224725"
    assert is_valid_cpf(52998224725.0) is True


def test_normalize_cpf_string_punctuation() -> None:
    assert normalize_cpf("529.982.247-25") == "52998224725"


def test_digits_only_float_no_extra_digit() -> None:
    assert digits_only(52998224725.0) == "52998224725"


def test_normalize_cpf_nan_empty() -> None:
    assert normalize_cpf(float("nan")) == ""
    assert is_valid_cpf(float("nan")) is False


def test_normalize_cpf_inf_empty() -> None:
    assert normalize_cpf(math.inf) == ""
