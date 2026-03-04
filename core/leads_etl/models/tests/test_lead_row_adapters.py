"""Adapter tests for canonical LeadRow materialization."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from core.leads_etl.models._errors import LeadRowAdapterError
from core.leads_etl.models.lead_row import backend_payload_to_lead_row, etl_payload_to_lead_row


def test_backend_payload_to_lead_row_materializes_canonical_shape() -> None:
    row = backend_payload_to_lead_row(
        {
            "email": " Lead@Example.COM ",
            "cpf": "529.982.247-25",
            "data_nascimento": "1990-01-01",
            "data_compra": "03/02/2025 13:45:59",
            "evento_nome": "Festival",
            "fonte_origem": "import-manual",
        }
    )

    assert row.email == "lead@example.com"
    assert row.cpf == "52998224725"
    assert row.data_nascimento == date(1990, 1, 1)
    assert row.data_compra == datetime(2025, 2, 3, 13, 45, 59)
    assert row.evento_nome == "Festival"
    assert row.fonte_origem == "import-manual"


def test_backend_payload_to_lead_row_rejects_persistence_only_fields() -> None:
    with pytest.raises(LeadRowAdapterError, match="persistencia ou derivados"):
        backend_payload_to_lead_row(
            {
                "email": "lead@example.com",
                "data_compra_data": "2025-01-01",
            }
        )


def test_etl_payload_to_lead_row_applies_alias_mapping_and_coercion() -> None:
    row = etl_payload_to_lead_row(
        {
            "email": " Lead@Example.COM ",
            "evento": "Festival ETL",
            "sexo": "F",
            "dt_hr_compra": "2025-01-02 10:30",
            "qtd_ingresso": "03",
            "ingresso": "VIP",
        }
    )

    assert row.email == "lead@example.com"
    assert row.evento_nome == "Festival ETL"
    assert row.genero == "F"
    assert row.data_compra == datetime(2025, 1, 2, 10, 30)
    assert row.ingresso_qtd == 3
    assert row.ingresso_tipo == "VIP"


def test_etl_payload_to_lead_row_rejects_staging_and_hashed_payloads() -> None:
    with pytest.raises(LeadRowAdapterError, match="staging/canonical"):
        etl_payload_to_lead_row(
            {
                "email": "lead@example.com",
                "source_id": "SRC_XLSX",
                "cpf_hash": "a" * 64,
                "__sheet_name": "Leads",
            }
        )
