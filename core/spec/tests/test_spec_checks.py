"""Unit tests for DOCX spec completeness and duplicate-title checks."""

from __future__ import annotations

from datetime import datetime, timezone

from core.spec.spec_checks import check_duplicates, check_required_sections
from core.spec.spec_models import (
    DocxFigure,
    DocxSection,
    DocxSpec,
    DocxTable,
    SPEC_REQUIRED_SECTION_MISSING,
    SPEC_SECTION_AMBIGUOUS_TITLE,
    SPEC_SECTION_DUPLICATE_TITLE,
)


def _build_spec(sections: list[DocxSection]) -> DocxSpec:
    """Build a DocxSpec fixture with custom sections for checks."""
    return DocxSpec(
        source_path="template.docx",
        extracted_at=datetime.now(timezone.utc),
        sections=sections,
        figures=[],
        tables=[],
    )


def test_check_required_sections_reports_missing_items() -> None:
    """Required-sections check reports missing titles as error findings."""
    spec = _build_spec(
        [
            DocxSection(level=1, title="Contexto do evento", body_lines=[], start_paragraph_index=0),
            DocxSection(level=1, title="Objetivo do relatorio", body_lines=[], start_paragraph_index=3),
        ]
    )

    findings = check_required_sections(
        spec,
        required_sections=[
            "Contexto do evento",
            "Shows por dia (12/12, 13/12, 14/12)",
        ],
    )

    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert findings[0].code == SPEC_REQUIRED_SECTION_MISSING
    assert findings[0].item_docx == "Shows por dia (12/12, 13/12, 14/12)"


def test_check_duplicates_reports_exact_duplicate_titles() -> None:
    """Duplicate check flags exact repeated section titles as errors."""
    spec = _build_spec(
        [
            DocxSection(level=1, title="Contexto do evento", body_lines=[], start_paragraph_index=0),
            DocxSection(level=2, title="Contexto do evento", body_lines=[], start_paragraph_index=8),
        ]
    )

    findings = check_duplicates(spec)

    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert findings[0].code == SPEC_SECTION_DUPLICATE_TITLE
    assert "repetido" in findings[0].message


def test_check_duplicates_reports_ambiguous_variants() -> None:
    """Duplicate check flags ambiguous normalized titles as warnings."""
    spec = _build_spec(
        [
            DocxSection(level=1, title="1. Publico do evento", body_lines=[], start_paragraph_index=0),
            DocxSection(level=2, title="Publico do Evento", body_lines=[], start_paragraph_index=8),
        ]
    )

    findings = check_duplicates(spec)

    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert findings[0].code == SPEC_SECTION_AMBIGUOUS_TITLE
    assert "ambigu" in findings[0].message.casefold()


def test_spec_checks_return_empty_when_spec_is_consistent() -> None:
    """Checks return no findings for consistent spec and full required coverage."""
    spec = DocxSpec(
        source_path="template.docx",
        extracted_at=datetime.now(timezone.utc),
        sections=[
            DocxSection(level=1, title="Contexto do evento", body_lines=[], start_paragraph_index=0),
            DocxSection(level=1, title="Objetivo do relatorio", body_lines=[], start_paragraph_index=3),
        ],
        figures=[DocxFigure(caption="Figura 1 - Teste", paragraph_index=4, section_title="Objetivo do relatorio")],
        tables=[DocxTable(table_index=1, n_rows=2, n_cols=2, header_cells=["A", "B"], section_title="Objetivo do relatorio")],
    )

    required_findings = check_required_sections(
        spec,
        required_sections=["Contexto do evento", "Objetivo do relatorio"],
    )
    duplicate_findings = check_duplicates(spec)

    assert required_findings == []
    assert duplicate_findings == []
