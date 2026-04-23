"""Unit tests for ETL CSV delimiter heuristics."""

from __future__ import annotations

from app.modules.lead_imports.application.etl_import.extract import _detect_csv_delimiter_robust


def test_detect_csv_delimiter_prefers_tab_when_tab_dominates_first_line() -> None:
    sample = "CPF\tEmail\tNome\n52998224725\ta@b.co\tX\n"
    assert _detect_csv_delimiter_robust(sample) == "\t"


def test_detect_csv_delimiter_tie_comma_semicolon_prefers_comma() -> None:
    # Igual numero de virgulas e ponto-e-virgula na primeira linha: convencao do parser ETL -> virgula.
    sample = "a,b;c\n52998224725,foo@example.com,\n"
    assert _detect_csv_delimiter_robust(sample) == ","
