"""Tests for assisted PDF table spec loader and extractor."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from etl.extract.pdf_assisted_specs import (
    PdfAssistedSpecsError,
    extract_with_spec,
    load_pdf_table_specs,
)


def _write_positioned_pdf(path: Path) -> None:
    """Write one-page PDF with positioned tokens aligned to column x ranges."""
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


def _write_specs_yaml(path: Path) -> None:
    """Write valid assisted spec YAML for access-control table extraction."""
    payload = {
        "schema_version": "1.0",
        "tables": [
            {
                "table_id": "access_control_default",
                "dataset": "access_control",
                "pages": [1],
                "bbox": [40, 20, 560, 780],
                "header_rows": 1,
                "evidence_label": "Tabela de controle de acesso (assistida)",
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


def test_load_pdf_table_specs_success(tmp_path: Path) -> None:
    """Spec loader should parse valid YAML into typed structure."""
    spec_path = tmp_path / "pdf_specs.yml"
    _write_specs_yaml(spec_path)

    specs = load_pdf_table_specs(spec_path)

    assert specs.schema_version == "1.0"
    assert len(specs.tables) == 1
    table = specs.tables[0]
    assert table.table_id == "access_control_default"
    assert table.pages == [1]
    assert len(table.columns) == 7


def test_load_pdf_table_specs_fails_when_required_field_missing(tmp_path: Path) -> None:
    """Spec loader should fail with actionable message for missing fields."""
    payload = {
        "schema_version": "1.0",
        "tables": [{"dataset": "access_control", "pages": [1], "bbox": [0, 0, 100, 100], "columns": []}],
    }
    spec_path = tmp_path / "invalid_specs.yml"
    spec_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(PdfAssistedSpecsError, match=r"\$\.tables\[0\]\.table_id: missing required field"):
        load_pdf_table_specs(spec_path)


def test_extract_with_spec_returns_rows_with_bbox_evidence(tmp_path: Path) -> None:
    """Spec extractor should parse rows and include page/bbox evidence metadata."""
    pdf_path = tmp_path / "assisted_source.pdf"
    spec_path = tmp_path / "pdf_specs.yml"
    _write_positioned_pdf(pdf_path)
    _write_specs_yaml(spec_path)

    specs = load_pdf_table_specs(spec_path)
    rows = extract_with_spec(pdf_path, specs, table_id="access_control_default")

    assert len(rows) == 2
    assert rows[0]["session_name"] == "NoiteShowA"
    assert rows[0]["ingressos_validos"] == 100
    assert str(rows[1]["comparecimento_pct"]) == "83.3"
    assert rows[0]["pdf_page"] == 1
    assert "bbox=" in str(rows[0]["evidence_text"])
    assert rows[0]["__spec_table_id"] == "access_control_default"
