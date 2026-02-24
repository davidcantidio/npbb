"""Tests for DIMAC/MTC PDF extractors with gap-aware staging loads."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from etl.extract import pdf_dimac, pdf_mtc


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source  # noqa: E402
from app.models.stg_dimac_mtc import MetricExtractionStatus, StgDimacMetric, StgMtcMetric  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for DIMAC/MTC tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry + lineage + DIMAC/MTC staging tables for tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            StgDimacMetric.__table__,
            StgMtcMetric.__table__,
        ],
    )


def _write_text_pdf(path: Path, lines: list[str]) -> None:
    """Write one-page text PDF with one line per row.

    Args:
        path: Destination PDF path.
        lines: Text lines to place into PDF content stream.
    """

    stream_parts = [b"BT /F1 12 Tf 72 750 Td "]
    for index, line in enumerate(lines):
        escaped = (
            line.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        ).encode("latin-1", errors="ignore")
        if index > 0:
            stream_parts.append(b"0 -18 Td ")
        stream_parts.append(b"(" + escaped + b") Tj ")
    stream_parts.append(b"ET")
    stream = b"".join(stream_parts)

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
            + f"<< /Length {len(stream)} >>\n".encode("ascii")
            + b"stream\n"
            + stream
            + b"\nendstream\nendobj\n"
        ),
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    content = bytearray(header)
    offsets = [0]
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


def test_extract_dimac_pdf_metrics_returns_ok_and_gap(tmp_path: Path) -> None:
    """DIMAC extractor should emit ok rows and explicit gaps when anchors are missing."""
    pdf_path = tmp_path / "dimac_metrics.pdf"
    _write_text_pdf(
        pdf_path,
        [
            "Relatorio DIMAC TMJ 2025",
            "Distribuicao por faixa etaria 18-24: 32%",
            "Satisfacao geral do evento 91%",
        ],
    )

    candidates = list(pdf_dimac.extract_dimac_pdf_metrics(pdf_path))

    assert len(candidates) == 3
    by_key = {item.metric_key: item for item in candidates}
    assert by_key["dimac.profile.age_distribution"].status == "ok"
    assert str(by_key["dimac.profile.age_distribution"].metric_value) == "32"
    assert by_key["dimac.satisfaction.overall"].status == "ok"
    assert by_key["dimac.profile.gender_distribution"].status == "gap"
    assert by_key["dimac.profile.gender_distribution"].gap_reason == "anchor_not_found"


def test_load_dimac_pdf_to_staging_persists_ok_and_gap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DIMAC loader should persist both ok and gap rows, marking run as partial."""
    pdf_path = tmp_path / "dimac_staging.pdf"
    _write_text_pdf(
        pdf_path,
        [
            "Distribuicao por faixa etaria 18-24: 32%",
            "Satisfacao geral do evento 91%",
        ],
    )

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_dimac, "engine", engine)

    summary = pdf_dimac.load_dimac_pdf_to_staging(
        source_id="src_pdf_dimac_monitoramento",
        pdf_path=pdf_path,
        gap_severity="partial",
    )

    assert summary["source_id"] == "SRC_PDF_DIMAC_MONITORAMENTO"
    assert summary["metrics_loaded"] == 3
    assert summary["ok_count"] == 2
    assert summary["gap_count"] == 1
    assert summary["status"] == IngestionStatus.PARTIAL.value

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.PARTIAL

        rows = session.exec(select(StgDimacMetric).order_by(StgDimacMetric.id)).all()
        assert len(rows) == 3
        ok_rows = [row for row in rows if row.status == MetricExtractionStatus.OK]
        gap_rows = [row for row in rows if row.status == MetricExtractionStatus.GAP]
        assert len(ok_rows) == 2
        assert len(gap_rows) == 1
        assert all(row.lineage_ref_id is not None for row in ok_rows)
        assert gap_rows[0].lineage_ref_id is None
        assert gap_rows[0].gap_reason == "anchor_not_found"


def test_extract_mtc_pdf_metrics_returns_ok_candidate(tmp_path: Path) -> None:
    """MTC extractor should parse clipping metric from anchored text line."""
    pdf_path = tmp_path / "mtc_metrics.pdf"
    _write_text_pdf(
        pdf_path,
        [
            "Relatorio de imprensa MTC",
            "Clipping total de materias publicadas: 45",
        ],
    )

    candidates = list(pdf_mtc.extract_mtc_pdf_metrics(pdf_path))

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.metric_key == "mtc.press.clippings_summary"
    assert candidate.status == "ok"
    assert str(candidate.metric_value) == "45"
    assert candidate.pdf_page == 1


def test_load_mtc_pdf_to_staging_marks_gap_when_anchor_not_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MTC loader should record gap row when metric anchor is not found."""
    pdf_path = tmp_path / "mtc_gap.pdf"
    _write_text_pdf(
        pdf_path,
        [
            "Relatorio sem dados de midia",
            "Conteudo sem metrica numerica identificavel",
        ],
    )

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_mtc, "engine", engine)

    summary = pdf_mtc.load_mtc_pdf_to_staging(
        source_id="src_pdf_mtc_imprensa",
        pdf_path=pdf_path,
        gap_severity="partial",
    )

    assert summary["source_id"] == "SRC_PDF_MTC_IMPRENSA"
    assert summary["metrics_loaded"] == 1
    assert summary["ok_count"] == 0
    assert summary["gap_count"] == 1
    assert summary["status"] == IngestionStatus.PARTIAL.value

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.PARTIAL

        rows = session.exec(select(StgMtcMetric).order_by(StgMtcMetric.id)).all()
        assert len(rows) == 1
        assert rows[0].status == MetricExtractionStatus.GAP
        assert rows[0].lineage_ref_id is None
        assert rows[0].gap_reason == "anchor_not_found"
