"""Unit tests for PPTX ZIP/XML fallback text extractor."""

from __future__ import annotations

from pathlib import Path
import zipfile

import pytest

from etl.extract.pptx_xml_fallback import PptxXmlFallbackError, iter_slide_text_blocks


def _write_minimal_pptx_zip(path: Path) -> None:
    """Write a minimal PPTX-like ZIP with two slide XML files."""
    slide_1_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:nvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>Midias e Alcance</a:t></a:r></a:p></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:nvPr/></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>Impressoes totais</a:t></a:r></a:p></p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""
    slide_2_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:nvSpPr><p:nvPr/></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>Social Listening</a:t></a:r></a:p></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:nvPr/></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>Sentimento positivo 78%</a:t></a:r></a:p></p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        # Add out of order to validate deterministic numeric ordering.
        archive.writestr("ppt/slides/slide2.xml", slide_2_xml)
        archive.writestr("ppt/slides/slide1.xml", slide_1_xml)


def test_iter_slide_text_blocks_extracts_deterministic_slide_payload(tmp_path: Path) -> None:
    """Fallback should parse slide title, texts and lineage per slide."""
    pptx_path = tmp_path / "fallback_test.pptx"
    _write_minimal_pptx_zip(pptx_path)

    slides = list(iter_slide_text_blocks(pptx_path))

    assert len(slides) == 2
    assert [slide.slide_number for slide in slides] == [1, 2]
    assert slides[0].slide_filename == "ppt/slides/slide1.xml"
    assert slides[0].slide_title == "Midias e Alcance"
    assert slides[0].texts == ["Impressoes totais"]
    assert slides[0].lineage_location == "slide:1"
    assert slides[1].slide_title == "Social Listening"
    assert slides[1].texts == ["Sentimento positivo 78%"]
    assert slides[1].lineage_location == "slide:2"


def test_iter_slide_text_blocks_raises_actionable_error_for_missing_file(tmp_path: Path) -> None:
    """Fallback should raise actionable error for missing source files."""
    missing = tmp_path / "missing.pptx"
    with pytest.raises(PptxXmlFallbackError, match="nao encontrado"):
        list(iter_slide_text_blocks(missing))


def test_iter_slide_text_blocks_raises_actionable_error_for_invalid_zip(tmp_path: Path) -> None:
    """Fallback should fail when source is not a valid ZIP/PPTX package."""
    invalid = tmp_path / "invalid.pptx"
    invalid.write_text("not-a-zip", encoding="utf-8")

    with pytest.raises(PptxXmlFallbackError, match="nao e ZIP valido"):
        list(iter_slide_text_blocks(invalid))
