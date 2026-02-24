"""Unit tests for PDF profile, assisted specs and access-control fallback.

This suite validates:
- PDF classifier behavior on small fixtures,
- assisted PDF table spec loading/extraction,
- access-control loader fallback/partial behavior with actionable messages.
"""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from etl.extract import pdf_access_control
from etl.extract.pdf_assisted_specs import extract_with_spec, load_pdf_table_specs
from etl.extract.pdf_classify import PdfClassificationError, classify_pdf


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source  # noqa: E402
from app.models.models import EventSession  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "pdf"
MIN_TABLE_PDF = FIXTURES_DIR / "min_table.pdf"
TABLE_SPECS_MIN = FIXTURES_DIR / "table_specs_min.yml"


def _make_engine():
    """Create isolated in-memory SQLite engine for PDF extractor tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry/lineage/staging tables used by loader tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            EventSession.__table__,
            StgAccessControlSession.__table__,
        ],
    )


def _write_image_pdf(path: Path) -> None:
    """Write one-page image-only PDF for non-extractable scenario testing."""
    image = Image.new("RGB", (500, 300), color=(255, 255, 255))
    image.save(path, "PDF")


def test_classify_pdf_min_table_fixture_detects_text_strategy() -> None:
    """Classifier should detect text-based profile on min table fixture."""
    profile = classify_pdf(MIN_TABLE_PDF)

    assert profile.page_count == 1
    assert profile.has_text is True
    assert profile.pages_with_text == 1
    assert profile.suggested_strategy == "text_table"


def test_assisted_specs_fixture_extracts_rows_from_min_table_pdf() -> None:
    """Assisted spec loader/extractor should parse fixture rows with evidence."""
    specs = load_pdf_table_specs(TABLE_SPECS_MIN)
    rows = extract_with_spec(MIN_TABLE_PDF, specs, table_id="access_control_default")

    assert len(rows) == 2
    assert rows[0]["session_name"] == "NoiteShowA"
    assert rows[0]["ingressos_validos"] == 100
    assert str(rows[1]["comparecimento_pct"]) == "83.3"
    assert rows[0]["pdf_page"] == 1
    assert "bbox=" in str(rows[0]["evidence_text"])


def test_access_control_loader_uses_assisted_fallback_when_automatic_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should fallback to assisted specs when automatic extraction fails."""
    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_access_control, "engine", engine)

    summary = pdf_access_control.load_access_control_pdf_to_staging(
        source_id="src_pdf_access_control_fixture_doze",
        pdf_path=MIN_TABLE_PDF,
        assisted_spec_path=TABLE_SPECS_MIN,
        assisted_table_id="access_control_default",
        non_extractable_severity="partial",
    )

    assert summary["source_id"] == "SRC_PDF_ACCESS_CONTROL_FIXTURE_DOZE"
    assert summary["rows_loaded"] == 2
    assert summary["findings_count"] == 0
    assert summary["status"] == IngestionStatus.SUCCESS.value

    with Session(engine) as session:
        rows = session.exec(
            select(StgAccessControlSession).order_by(StgAccessControlSession.id)
        ).all()
        assert len(rows) == 2
        assert rows[0].lineage_ref_id > 0
        assert rows[0].evidence_text and "bbox=" in rows[0].evidence_text


def test_access_control_loader_marks_partial_with_actionable_message_for_scan_pdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should return partial status and actionable guidance for scan PDFs."""
    pdf_path = tmp_path / "scan.pdf"
    _write_image_pdf(pdf_path)

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_access_control, "engine", engine)

    summary = pdf_access_control.load_access_control_pdf_to_staging(
        source_id="src_pdf_access_control_scan",
        pdf_path=pdf_path,
        non_extractable_severity="partial",
    )

    assert summary["source_id"] == "SRC_PDF_ACCESS_CONTROL_SCAN"
    assert summary["status"] == IngestionStatus.PARTIAL.value
    assert summary["rows_loaded"] == 0
    assert summary["findings_count"] >= 1

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.PARTIAL
        assert run.notes is not None
        assert "Como corrigir" in run.notes


def test_classify_pdf_invalid_file_raises_actionable_error(tmp_path: Path) -> None:
    """Classifier should fail with actionable message on invalid PDF payload."""
    invalid_path = tmp_path / "invalid.pdf"
    invalid_path.write_text("not a valid pdf payload", encoding="utf-8")

    with pytest.raises(PdfClassificationError, match="Falha ao abrir PDF"):
        classify_pdf(invalid_path)
