from __future__ import annotations

from app.models.models import Lead
from app.modules.leads_publicidade.application.lead_merge_policy import (
    lead_field_has_value,
    merge_lead_payload_fill_missing,
)


def test_lead_field_has_value() -> None:
    assert lead_field_has_value("x") is True
    assert lead_field_has_value("  x  ") is True
    assert lead_field_has_value("") is False
    assert lead_field_has_value("   ") is False
    assert lead_field_has_value(None) is False
    assert lead_field_has_value(0) is True
    assert lead_field_has_value(False) is True


def test_merge_fill_missing_writes_only_empty_slots() -> None:
    lead = Lead(
        email="a@example.com",
        cpf="52998224725",
        nome="Nome Original",
        telefone=None,
        cidade="",
        evento_nome="Evento A",
    )
    merge_lead_payload_fill_missing(
        lead,
        {
            "nome": "Nome Novo",
            "telefone": "11999999999",
            "cidade": "Sao Paulo",
            "evento_nome": "Evento B",
            "genero": "F",
        },
    )
    assert lead.nome == "Nome Original"
    assert lead.telefone == "11999999999"
    assert lead.cidade == "Sao Paulo"
    assert lead.evento_nome == "Evento A"
    assert lead.genero == "F"


def test_merge_second_pass_gold_style_two_payloads_same_lead() -> None:
    lead = Lead(email="g@example.com", cpf="52998224725", nome="Primeiro", evento_nome="Ev1")
    merge_lead_payload_fill_missing(lead, {"nome": "Segundo Lote", "telefone": "11888888888"})
    assert lead.nome == "Primeiro"
    assert lead.telefone == "11888888888"
    merge_lead_payload_fill_missing(lead, {"nome": "Terceiro", "telefone": "11777777777"})
    assert lead.nome == "Primeiro"
    assert lead.telefone == "11888888888"
