"""Unit tests for the canonical LeadRow contract."""

from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from core.leads_etl.models.lead_row import LEAD_ROW_EXCLUDED_FIELDS, LEAD_ROW_FIELDS, LeadRow


EXPECTED_FIELDS = (
    "id_salesforce",
    "nome",
    "sobrenome",
    "email",
    "telefone",
    "cpf",
    "data_nascimento",
    "evento_nome",
    "sessao",
    "data_compra",
    "opt_in",
    "opt_in_id",
    "opt_in_flag",
    "metodo_entrega",
    "endereco_rua",
    "endereco_numero",
    "bairro",
    "cep",
    "cidade",
    "estado",
    "genero",
    "codigo_promocional",
    "ingresso_tipo",
    "ingresso_qtd",
    "fonte_origem",
)


def test_lead_row_freezes_documented_inventory() -> None:
    assert LEAD_ROW_FIELDS == EXPECTED_FIELDS
    assert set(LEAD_ROW_EXCLUDED_FIELDS) == {
        "id",
        "data_criacao",
        "data_compra_data",
        "data_compra_hora",
    }
    assert all(reason.strip() for reason in LEAD_ROW_EXCLUDED_FIELDS.values())


def test_lead_row_coerces_critical_fields_without_changing_baseline_semantics() -> None:
    row = LeadRow.model_validate(
        {
            "email": " Pessoa@Example.COM ",
            "cpf": "123.456.789-00",
            "telefone": "+55 (11) 91234-5678",
            "cep": "70.000-123",
            "estado": " sp ",
            "data_nascimento": "31/12/1999",
            "data_compra": "2025-01-02 10:30",
            "ingresso_qtd": " 02 ",
            "opt_in_flag": "sim",
            "nome": "  Alice  ",
        }
    )

    assert row.email == "pessoa@example.com"
    assert row.cpf == "12345678900"
    assert row.telefone == "5511912345678"
    assert row.cep == "70000123"
    assert row.estado == "SP"
    assert row.data_nascimento == date(1999, 12, 31)
    assert row.data_compra == datetime(2025, 1, 2, 10, 30)
    assert row.ingresso_qtd == 2
    assert row.opt_in_flag is True
    assert row.nome == "Alice"


def test_lead_row_turns_blank_values_into_none() -> None:
    row = LeadRow.model_validate({"email": "   ", "nome": "", "ingresso_qtd": " "})

    assert row.email is None
    assert row.nome is None
    assert row.ingresso_qtd is None


def test_lead_row_forbids_unknown_keys() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        LeadRow.model_validate({"email": "lead@example.com", "unknown_field": "x"})
