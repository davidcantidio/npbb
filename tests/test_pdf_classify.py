"""Tests for PDF profile classification and registry logging."""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from etl.extract.pdf_classify import PdfClassificationError, classify_pdf, classify_pdf_with_registry


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db import database as db_database  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for PDF classify tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry tables used by classify_pdf_with_registry."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
        ],
    )


def _write_text_pdf(path: Path) -> None:
    """Write one-page text PDF using a minimal manual PDF structure."""
    text_stream = b"BT /F1 24 Tf 72 720 Td (Hello PDF text profile) Tj ET"
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
            b"endobj\n"
        ),
        (
            b"4 0 obj\n"
            + f"<< /Length {len(text_stream)} >>\n".encode("ascii")
            + b"stream\n"
            + text_stream
            + b"\nendstream\nendobj\n"
        ),
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    content = bytearray(header)
    offsets: list[int] = [0]
    for obj in objects:
        offsets.append(len(content))
        content.extend(obj)

    xref_start = len(content)
    content.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    content.extend(
        (
            f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    path.write_bytes(bytes(content))


def _write_image_pdf(path: Path) -> None:
    """Write one-page image PDF for scan-like classification tests."""
    image = Image.new("RGB", (400, 250), color=(255, 255, 255))
    image.save(path, "PDF")


def test_classify_pdf_detects_text_profile(tmp_path: Path) -> None:
    """Classifier should detect text-based PDF profile and strategy."""
    pdf_path = tmp_path / "text_profile.pdf"
    _write_text_pdf(pdf_path)

    profile = classify_pdf(pdf_path)

    assert profile.page_count == 1
    assert profile.has_text is True
    assert profile.pages_with_text == 1
    assert profile.text_like_pages >= 1
    assert profile.suggested_strategy == "text_table"


def test_classify_pdf_detects_image_profile(tmp_path: Path) -> None:
    """Classifier should detect image/scanned profile from image-only PDF."""
    pdf_path = tmp_path / "image_profile.pdf"
    _write_image_pdf(pdf_path)

    profile = classify_pdf(pdf_path)

    assert profile.page_count == 1
    assert profile.has_images is True
    assert profile.pages_with_images >= 1
    assert profile.suggested_strategy in {"ocr_or_assisted", "hybrid"}


def test_classify_pdf_with_registry_writes_summary_to_ingestion_notes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Registry wrapper should persist ingestion run with profile summary notes."""
    pdf_path = tmp_path / "profile_registry.pdf"
    _write_text_pdf(pdf_path)

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(db_database, "engine", engine)

    result = classify_pdf_with_registry(
        source_id="src_pdf_profile_doze",
        pdf_path=pdf_path,
    )

    assert result["source_id"] == "SRC_PDF_PROFILE_DOZE"
    assert result["profile"]["page_count"] == 1
    assert result["profile"]["has_text"] is True

    with Session(engine) as session:
        run = session.get(IngestionRun, result["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.SUCCESS
        assert run.notes and "pdf_profile=" in run.notes


def test_classify_pdf_raises_actionable_error_for_invalid_file(tmp_path: Path) -> None:
    """Classifier should fail with actionable message for invalid PDFs."""
    invalid_path = tmp_path / "invalid.pdf"
    invalid_path.write_text("not a valid pdf payload", encoding="utf-8")

    with pytest.raises(PdfClassificationError, match="Falha ao abrir PDF"):
        classify_pdf(invalid_path)
