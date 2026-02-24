"""Tests for the DOCX spec extraction contract.

This module validates structural extraction from a minimal DOCX fixture:
headings, figure captions, tables, and checklist markdown rendering.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from core.spec.docx_figures_tables import extract_figures_from_docx, extract_tables_from_docx
from core.spec.docx_sections import DocxSectionExtractor
from core.spec.render_markdown import render_docx_as_spec_md
from core.spec.spec_models import MANDATORY_SHOWS_BY_DAY_ITEM, DocxSpec


def _fixture_docx_path() -> Path:
    """Return the path of the minimal DOCX fixture used by these tests."""
    return Path("tests/fixtures/docx/min_template.docx")


def test_extract_sections_from_min_template() -> None:
    """Extract sections from fixture and validate heading structure."""
    sections = DocxSectionExtractor().extract_sections(_fixture_docx_path())

    assert len(sections) == 2
    assert sections[0].level == 1
    assert sections[0].title == "Contexto do evento"
    assert "Texto contextual de abertura." in sections[0].body_lines
    assert sections[1].level == 2
    assert sections[1].title == "Publico por sessao"


def test_extract_figures_from_min_template() -> None:
    """Extract figure inventory and ensure nearest section association works."""
    extractor = DocxSectionExtractor()
    sections = extractor.extract_sections(_fixture_docx_path())
    figures = extract_figures_from_docx(_fixture_docx_path(), sections)

    assert len(figures) == 1
    assert figures[0].caption == "Figura 1 - Entradas validadas por dia"
    assert figures[0].section_title == "Contexto do evento"


def test_extract_tables_from_min_template() -> None:
    """Extract table inventory with headers and table shape from fixture."""
    tables = extract_tables_from_docx(_fixture_docx_path())

    assert len(tables) == 1
    assert tables[0].n_cols == 3
    assert tables[0].n_rows == 2
    assert tables[0].header_cells == ["Metrica", "Dia", "Valor"]
    assert tables[0].section_title == "Publico por sessao"


def test_render_docx_as_spec_markdown_from_min_template() -> None:
    """Render markdown checklist and validate required structural rows."""
    extractor = DocxSectionExtractor()
    sections = extractor.extract_sections(_fixture_docx_path())
    figures = extract_figures_from_docx(_fixture_docx_path(), sections)
    tables = extract_tables_from_docx(_fixture_docx_path())
    spec = DocxSpec(
        source_path=str(_fixture_docx_path()),
        extracted_at=datetime.now(timezone.utc),
        sections=sections,
        figures=figures,
        tables=tables,
    )

    markdown = render_docx_as_spec_md(spec)

    assert "## Checklist (Contrato de Dados)" in markdown
    assert "| Secao (DOCX) | Metrica/Conteudo esperado | Granularidade (evento/dia/sessao) | Tabelas/campos necessarios | Fonte atual no DOCX | Status |" in markdown
    assert "Contexto do evento" in markdown
    assert MANDATORY_SHOWS_BY_DAY_ITEM in markdown
