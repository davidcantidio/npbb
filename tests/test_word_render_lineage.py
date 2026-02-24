"""Unit tests for Word lineage normalization and rendering helpers."""

from __future__ import annotations

from reports.word import (
    LineageRef,
    extract_lineage_refs_from_rows,
    normalize_lineage_refs,
    render_lineage_block,
)


def test_normalize_lineage_refs_accepts_dicts_and_deduplicates() -> None:
    """Normalizer should accept dict input and remove duplicate references."""

    refs = normalize_lineage_refs(
        [
            {
                "source_id": "pdf_access_12",
                "location": "page=3",
                "evidence_text": "Tabela Controle de Acesso",
            },
            {
                "source_id": "pdf_access_12",
                "location": "page=3",
                "evidence_text": "Tabela Controle de Acesso",
            },
            LineageRef(
                source_id="xlsx_optin",
                location="sheet=Resumo!A1:D20",
                evidence_text="Aba Resumo",
            ),
        ]
    )

    assert len(refs) == 2
    assert refs[0].source_id == "pdf_access_12"
    assert refs[1].source_id == "xlsx_optin"


def test_extract_lineage_refs_from_rows_reads_standard_columns() -> None:
    """Extractor should read lineage columns from mart rows when available."""

    refs = extract_lineage_refs_from_rows(
        [
            {
                "source_id": "pdf_access_13",
                "location_value": "page=5",
                "evidence": "Tabela por sessao",
                "presentes": 180,
            }
        ]
    )

    assert len(refs) == 1
    assert refs[0].source_id == "pdf_access_13"
    assert refs[0].location == "page=5"
    assert refs[0].evidence_text == "Tabela por sessao"


def test_render_lineage_block_returns_gap_when_lineage_is_missing() -> None:
    """Renderer should output explicit GAP line when lineage is absent."""

    lines = render_lineage_block(
        None,
        placeholder_id="PUBLICO__ATTENDANCE__TABLE",
        artifact_type="table",
    )

    assert lines[0] == "[Linhagem] table | placeholder=PUBLICO__ATTENDANCE__TABLE"
    assert "GAP: linhagem ausente" in lines[1]
