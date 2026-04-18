"""Public canonical lead-row contract shared by backend and ETL."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from ._adapters import adapt_backend_payload, adapt_etl_payload
from ._coercions import coerce_lead_field
from ._field_catalog import LEAD_ROW_EXCLUDED_FIELDS, LEAD_ROW_FIELDS


class LeadRow(BaseModel):
    """Contrato canónico de entrada para uma linha de lead reutilizável.

    Campos como ``cpf`` e ``email`` permanecem opcionais no modelo para
    compatibilidade com payloads parciais e leituras legadas. Nos fluxos de
    importação de leads (legado e ETL), cada linha importável exige CPF
    válido; a validação aplicada após materializar ``LeadRow`` rejeita CPF
    ausente ou inválido antes de persistir.
    """

    model_config = ConfigDict(extra="forbid")

    id_salesforce: str | None = None
    nome: str | None = None
    sobrenome: str | None = None
    email: str | None = None
    telefone: str | None = None
    cpf: str | None = None
    rg: str | None = None
    data_nascimento: date | None = None
    evento_nome: str | None = None
    sessao: str | None = None
    data_compra: datetime | None = None
    opt_in: str | None = None
    opt_in_id: str | None = None
    opt_in_flag: bool | None = None
    metodo_entrega: str | None = None
    endereco_rua: str | None = None
    endereco_numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cep: str | None = None
    cidade: str | None = None
    estado: str | None = None
    genero: str | None = None
    codigo_promocional: str | None = None
    ingresso_tipo: str | None = None
    ingresso_qtd: int | None = None
    fonte_origem: str | None = None
    is_cliente_bb: bool | None = None
    is_cliente_estilo: bool | None = None

    @field_validator(*LEAD_ROW_FIELDS, mode="before")
    @classmethod
    def _coerce_known_fields(cls, value: Any, info: ValidationInfo) -> Any:
        return coerce_lead_field(info.field_name, value)


def backend_payload_to_lead_row(payload: Mapping[str, Any]) -> LeadRow:
    """Adapt a backend payload into the canonical lead-row contract."""

    return LeadRow.model_validate(adapt_backend_payload(payload))


def etl_payload_to_lead_row(payload: Mapping[str, Any]) -> LeadRow:
    """Adapt an ETL payload into the canonical lead-row contract."""

    return LeadRow.model_validate(adapt_etl_payload(payload))


__all__ = [
    "LeadRow",
    "LEAD_ROW_FIELDS",
    "LEAD_ROW_EXCLUDED_FIELDS",
    "backend_payload_to_lead_row",
    "etl_payload_to_lead_row",
    "coerce_lead_field",
]
