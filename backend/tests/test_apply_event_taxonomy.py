"""Taxonomia de evento: aceita tipo já preenchido quando o nome não está no mapa fixo."""

from __future__ import annotations

import pandas as pd

from lead_pipeline.pipeline import _apply_event_taxonomy
from lead_pipeline.source_adapter import REJECT_REASON_COL


def test_passthrough_tipo_evento_when_evento_empty_and_tipo_set():
    df = pd.DataFrame(
        [
            {
                "evento": "",
                "tipo_evento": "Entretenimento",
                REJECT_REASON_COL: "",
            }
        ]
    )
    out, reasons = _apply_event_taxonomy(df)
    assert reasons == []
    assert out["tipo_evento"].tolist() == ["Entretenimento"]


def test_passthrough_tipo_evento_when_evento_unknown_name():
    df = pd.DataFrame(
        [
            {
                "evento": "Meu Festival XYZ",
                "tipo_evento": "Entretenimento",
                REJECT_REASON_COL: "",
            }
        ]
    )
    out, reasons = _apply_event_taxonomy(df)
    assert reasons == []
    assert out["tipo_evento"].tolist() == ["Entretenimento"]


def test_fail_evento_vazio_when_no_tipo():
    df = pd.DataFrame(
        [
            {
                "evento": "",
                "tipo_evento": "",
                REJECT_REASON_COL: "",
            }
        ]
    )
    out, reasons = _apply_event_taxonomy(df)
    assert any("EVENTO_VAZIO" in r for r in reasons)
    assert out["tipo_evento"].tolist() == [""]


def test_taxonomy_still_overrides_when_evento_matches():
    df = pd.DataFrame(
        [
            {
                "evento": "Park Challenge 2025",
                "tipo_evento": "Ignorado",
                REJECT_REASON_COL: "",
            }
        ]
    )
    out, reasons = _apply_event_taxonomy(df)
    assert reasons == []
    assert "ESPORTE" in out["tipo_evento"].iloc[0]
