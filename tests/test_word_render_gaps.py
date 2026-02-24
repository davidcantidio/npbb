"""Unit tests for GAP/INCONSISTENTE Word section renderer."""

from __future__ import annotations

import json
from pathlib import Path

from reports.word import load_dq_report, render_gaps_section


def test_render_gaps_section_includes_findings_and_show_day_coverage() -> None:
    """Renderer should include evidence lines and show-day GAP/INCONSISTENTE items."""

    dq_report = {
        "sections": {
            "inconsistencies": [
                {
                    "dataset_id": "show_12_dimac",
                    "message": "Conflito entre fonte A e B no show_12",
                    "source_id": "SRC_DIMAC_A",
                    "location": "page=12",
                    "evidence_text": "Tabela Share BB",
                }
            ],
            "gaps_by_dataset": {
                "show_14_access_control": [
                    {
                        "message": "Sem controle de acesso para 2025-12-14",
                        "source_id": "SRC_ACCESS",
                        "location_value": "page=0",
                        "evidence_text": "Arquivo nao recebido",
                    }
                ]
            },
        }
    }

    lines = render_gaps_section(dq_report)
    text = "\n".join(lines)

    assert "Resumo GAP/INCONSISTENTE" in text
    assert "INCONSISTENTE | dataset=show_12_dimac" in text
    assert "GAP | dataset=show_14_access_control" in text
    assert "source_id=SRC_DIMAC_A" in text
    assert "source_id=SRC_ACCESS" in text
    assert "Cobertura de shows por dia (12/12, 13/12, 14/12):" in text
    assert "12/12: INCONSISTENTE" in text
    assert "14/12: GAP" in text


def test_render_gaps_section_returns_gap_notice_when_dq_report_missing() -> None:
    """Renderer should return explicit GAP notice when DQ report is absent."""

    lines = render_gaps_section(None)
    text = "\n".join(lines)
    assert "relatorio DQ nao informado" in text
    assert "GAP: sem insumos de DQ" in text


def test_load_dq_report_reads_json_payload(tmp_path: Path) -> None:
    """Loader should read JSON object file and return dictionary payload."""

    payload_path = tmp_path / "dq_report.json"
    payload_path.write_text(
        json.dumps({"sections": {"errors": []}}),
        encoding="utf-8",
    )

    payload = load_dq_report(payload_path)
    assert payload["sections"]["errors"] == []
