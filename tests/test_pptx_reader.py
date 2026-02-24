"""Unit tests for PPTX base reader and slide iteration."""

from __future__ import annotations

from pathlib import Path

import pytest

from etl.extract.pptx_reader import (
    PptxDependencyMissingError,
    PptxReaderError,
    iter_slides,
)


pptx = pytest.importorskip("pptx")
Inches = pytest.importorskip("pptx.util").Inches


def _build_sample_pptx(path: Path) -> None:
    """Create a minimal PPTX with text and table content for parser tests."""
    presentation = pptx.Presentation()

    slide1 = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide1.shapes.title.text = "Midias e Alcance"
    slide1.placeholders[1].text = "Impressoes totais: 1000"

    slide2 = presentation.slides.add_slide(presentation.slide_layouts[5])
    slide2.shapes.title.text = "Social Listening"
    table = slide2.shapes.add_table(
        rows=2,
        cols=2,
        left=Inches(0.8),
        top=Inches(1.6),
        width=Inches(6.2),
        height=Inches(1.4),
    ).table
    table.cell(0, 0).text = "Metrica"
    table.cell(0, 1).text = "Valor"
    table.cell(1, 0).text = "Sentimento positivo"
    table.cell(1, 1).text = "78%"

    presentation.save(path)


def test_iter_slides_reads_texts_and_table_cells(tmp_path: Path) -> None:
    """Iterator should return deck-order slides with normalized text inventory."""
    pptx_path = tmp_path / "sample.pptx"
    _build_sample_pptx(pptx_path)

    slides = list(iter_slides(pptx_path))

    assert len(slides) == 2
    assert slides[0].slide_number == 1
    assert slides[1].slide_number == 2
    assert slides[0].lineage_location == "slide:1"
    assert slides[1].lineage_location == "slide:2"
    assert "Midias e Alcance" in slides[0].text_items
    assert "Impressoes totais: 1000" in slides[0].text_items
    assert "Social Listening" in slides[1].text_items
    assert "Metrica" in slides[1].text_items
    assert "Sentimento positivo" in slides[1].text_items
    assert "78%" in slides[1].text_items


def test_iter_slides_raises_actionable_error_for_invalid_file(tmp_path: Path) -> None:
    """Reader should raise actionable exception when file is not valid PPTX."""
    invalid_path = tmp_path / "invalid.pptx"
    invalid_path.write_text("not a zip-based office file", encoding="utf-8")

    with pytest.raises(PptxReaderError, match="Falha ao abrir PPTX"):
        list(iter_slides(invalid_path))


def test_iter_slides_raises_actionable_error_for_missing_file(tmp_path: Path) -> None:
    """Reader should raise actionable exception when source path is missing."""
    missing_path = tmp_path / "missing.pptx"

    with pytest.raises(PptxReaderError, match="nao encontrado"):
        list(iter_slides(missing_path))


def test_iter_slides_can_force_xml_fallback_mode(tmp_path: Path) -> None:
    """Reader should support explicit XML fallback mode."""
    pptx_path = tmp_path / "sample_xml_mode.pptx"
    _build_sample_pptx(pptx_path)

    slides = list(iter_slides(pptx_path, prefer_xml_fallback=True))

    assert len(slides) == 2
    assert slides[0].slide_number == 1
    assert slides[0].lineage_location == "slide:1"
    assert "Midias e Alcance" in slides[0].text_items


def test_iter_slides_falls_back_when_python_pptx_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reader should use XML fallback automatically on dependency failure."""
    pptx_path = tmp_path / "sample_fallback.pptx"
    _build_sample_pptx(pptx_path)

    def _raise_dependency_missing(_: Path):
        raise PptxDependencyMissingError("Dependencia ausente")

    monkeypatch.setattr("etl.extract.pptx_reader._iter_slides_python_pptx", _raise_dependency_missing)
    slides = list(iter_slides(pptx_path))

    assert len(slides) == 2
    assert slides[1].slide_number == 2
    assert slides[1].lineage_location == "slide:2"
    assert "Social Listening" in slides[1].text_items
