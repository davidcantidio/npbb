"""Casos de parse_date usados na pipeline Gold (Excel/JSON)."""

from __future__ import annotations

from lead_pipeline.normalization import parse_date


def test_parse_date_excel_serial_integer():
    assert parse_date("45321") == "2024-01-30"


def test_parse_date_excel_serial_float_string_from_json():
    assert parse_date("45321.0") == "2024-01-30"


def test_parse_date_iso_unchanged():
    assert parse_date("1990-01-15") == "1990-01-15"


def test_parse_date_yyyymmdd_compact():
    assert parse_date("19900115") == "1990-01-15"


def test_parse_date_nat_none_treated_as_empty():
    assert parse_date("NaT") == ""
    assert parse_date("nan") == ""
    assert parse_date("None") == ""


def test_parse_date_br_slash_dayfirst():
    assert parse_date("15/01/1990") == "1990-01-15"
