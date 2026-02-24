"""Tests for PDF access-control extractor and staging loader."""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select
import yaml

from etl.extract import pdf_access_control


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source  # noqa: E402
from app.models.models import EventSession  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for access-control tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry + lineage + staging tables for tests."""
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


def _write_text_access_control_pdf(path: Path) -> None:
    """Write one-page text PDF with lines parsable by text fallback logic."""
    stream = (
        b"BT /F1 12 Tf 72 750 Td "
        b"(Sessao Ingressos Validos Invalidos Bloqueados Presentes Ausentes Comparecimento) Tj "
        b"0 -20 Td (Show 12/12 100 2 1 90 10 90%) Tj "
        b"0 -20 Td (Show 13/12 120 3 0 100 20 83,3%) Tj "
        b"ET"
    )
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


def _write_image_pdf(path: Path) -> None:
    """Write one-page image-only PDF for non-extractable scenario tests."""
    image = Image.new("RGB", (500, 300), color=(255, 255, 255))
    image.save(path, "PDF")


def _write_positioned_access_control_pdf_for_assisted(path: Path) -> None:
    """Write PDF where automatic parser fails but assisted spec can parse."""
    stream = (
        b"BT /F1 12 Tf "
        b"1 0 0 1 70 740 Tm (Sessao) Tj "
        b"1 0 0 1 230 740 Tm (Validos) Tj "
        b"1 0 0 1 285 740 Tm (Invalidos) Tj "
        b"1 0 0 1 350 740 Tm (Bloqueados) Tj "
        b"1 0 0 1 415 740 Tm (Presentes) Tj "
        b"1 0 0 1 470 740 Tm (Ausentes) Tj "
        b"1 0 0 1 525 740 Tm (Comparecimento) Tj "
        b"1 0 0 1 70 715 Tm (NoiteShowA) Tj "
        b"1 0 0 1 230 715 Tm (100) Tj "
        b"1 0 0 1 285 715 Tm (2) Tj "
        b"1 0 0 1 350 715 Tm (1) Tj "
        b"1 0 0 1 415 715 Tm (90) Tj "
        b"1 0 0 1 470 715 Tm (10) Tj "
        b"1 0 0 1 525 715 Tm (90%) Tj "
        b"1 0 0 1 70 695 Tm (NoiteShowB) Tj "
        b"1 0 0 1 230 695 Tm (120) Tj "
        b"1 0 0 1 285 695 Tm (3) Tj "
        b"1 0 0 1 350 695 Tm (0) Tj "
        b"1 0 0 1 415 695 Tm (100) Tj "
        b"1 0 0 1 470 695 Tm (20) Tj "
        b"1 0 0 1 525 695 Tm (83,3%) Tj "
        b"ET"
    )
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


def _write_assisted_spec(path: Path) -> None:
    """Write assisted YAML spec used by fallback integration test."""
    payload = {
        "schema_version": "1.0",
        "tables": [
            {
                "table_id": "access_control_default",
                "dataset": "access_control",
                "pages": [1],
                "bbox": [40, 20, 560, 780],
                "header_rows": 1,
                "evidence_label": "Tabela assistida de controle de acesso",
                "columns": [
                    {"name": "session_name", "x_min": 40, "x_max": 210},
                    {"name": "ingressos_validos", "x_min": 210, "x_max": 270},
                    {"name": "invalidos", "x_min": 270, "x_max": 320},
                    {"name": "bloqueados", "x_min": 320, "x_max": 380},
                    {"name": "presentes", "x_min": 380, "x_max": 440},
                    {"name": "ausentes", "x_min": 440, "x_max": 500},
                    {"name": "comparecimento_pct", "x_min": 500, "x_max": 560},
                ],
                "postprocess": {
                    "ingressos_validos": "int",
                    "invalidos": "int",
                    "bloqueados": "int",
                    "presentes": "int",
                    "ausentes": "int",
                    "comparecimento_pct": "percent",
                },
            }
        ],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_extract_access_control_pdf_parses_rows_from_text_fallback(tmp_path: Path) -> None:
    """Extractor should produce canonical rows from text-based PDF fallback parsing."""
    pdf_path = tmp_path / "access_control_text.pdf"
    _write_text_access_control_pdf(pdf_path)

    rows = list(pdf_access_control.extract_access_control_pdf(pdf_path))

    assert len(rows) == 2
    by_session = {row["session_name"]: row for row in rows}
    assert by_session["Show 12/12"]["ingressos_validos"] == 100
    assert by_session["Show 12/12"]["presentes"] == 90
    assert str(by_session["Show 13/12"]["comparecimento_pct"]) == "83.3"
    assert all(row["pdf_page"] == 1 for row in rows)


def test_load_access_control_pdf_to_staging_persists_rows_and_lineage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should persist access-control staging rows with page lineage refs."""
    pdf_path = tmp_path / "access_control_load.pdf"
    _write_text_access_control_pdf(pdf_path)

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_access_control, "engine", engine)

    summary = pdf_access_control.load_access_control_pdf_to_staging(
        source_id="src_access_control_treze",
        pdf_path=pdf_path,
        lineage_policy="required",
        severity_on_missing="failed",
    )

    assert summary["source_id"] == "SRC_ACCESS_CONTROL_TREZE"
    assert summary["rows_loaded"] == 2
    assert summary["status"] == IngestionStatus.SUCCESS.value

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.SUCCESS

        rows = session.exec(select(StgAccessControlSession).order_by(StgAccessControlSession.id)).all()
        assert len(rows) == 2
        assert all(row.lineage_ref_id > 0 for row in rows)
        assert all(row.session_id is not None for row in rows)
        assert all(row.pdf_page == 1 for row in rows)


def test_load_access_control_pdf_marks_partial_when_pdf_is_not_extractable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should mark ingestion as partial with guidance for scan/image PDFs."""
    pdf_path = tmp_path / "access_control_scan.pdf"
    _write_image_pdf(pdf_path)

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_access_control, "engine", engine)

    summary = pdf_access_control.load_access_control_pdf_to_staging(
        source_id="src_access_control_scan",
        pdf_path=pdf_path,
        non_extractable_severity="partial",
    )

    assert summary["source_id"] == "SRC_ACCESS_CONTROL_SCAN"
    assert summary["rows_loaded"] == 0
    assert summary["findings_count"] >= 1
    assert summary["status"] == IngestionStatus.PARTIAL.value

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.PARTIAL
        assert run.notes and "findings=" in run.notes


def test_load_access_control_pdf_uses_assisted_spec_when_automatic_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should use assisted YAML spec when automatic extraction returns no rows."""
    pdf_path = tmp_path / "access_control_assisted.pdf"
    spec_path = tmp_path / "pdf_specs.yml"
    _write_positioned_access_control_pdf_for_assisted(pdf_path)
    _write_assisted_spec(spec_path)

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pdf_access_control, "engine", engine)

    summary = pdf_access_control.load_access_control_pdf_to_staging(
        source_id="src_access_control_assisted_doze",
        pdf_path=pdf_path,
        assisted_spec_path=spec_path,
        assisted_table_id="access_control_default",
        non_extractable_severity="partial",
    )

    assert summary["source_id"] == "SRC_ACCESS_CONTROL_ASSISTED_DOZE"
    assert summary["rows_loaded"] == 2
    assert summary["findings_count"] == 0
    assert summary["status"] == IngestionStatus.SUCCESS.value

    with Session(engine) as session:
        rows = session.exec(select(StgAccessControlSession).order_by(StgAccessControlSession.id)).all()
        assert len(rows) == 2
        assert rows[0].session_name == "NoiteShowA"
        assert rows[0].session_id is not None
        assert rows[0].lineage_ref_id > 0
        assert rows[0].evidence_text and "bbox=" in rows[0].evidence_text
