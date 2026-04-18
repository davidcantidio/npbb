"""Schemas de listagem de leads."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class LeadListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    long_running: bool = Field(
        default=False,
        description="Sinal interno para listagens pesadas, como exportacao CSV paginada.",
    )
    data_inicio: date | None = Field(
        default=None,
        description="Inicio inclusivo (UTC) para filtrar por data de criacao do lead.",
    )
    data_fim: date | None = Field(
        default=None,
        description="Fim inclusivo (UTC) para filtrar por data de criacao do lead.",
    )
    evento_id: int | None = Field(
        default=None,
        ge=1,
        description="Filtra pela conversao mais recente do lead ou pelo evento de origem do lote.",
    )


class LeadListItemRead(BaseModel):
    id: int
    nome: str | None = None
    sobrenome: str | None = None
    email: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    evento_nome: str | None = None
    cidade: str | None = None
    estado: str | None = None
    data_compra: datetime | None = None
    data_criacao: datetime
    evento_convertido_id: int | None = None
    evento_convertido_nome: str | None = None
    tipo_conversao: str | None = None
    data_conversao: datetime | None = None
    # Personal document fields
    rg: str | None = None
    genero: str | None = None
    is_cliente_bb: bool | None = None
    is_cliente_estilo: bool | None = None
    # Address fields
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cep: str | None = None
    # Exportacao CSV (layout tipo pivot / data 2.csv)
    data_nascimento: date | None = None
    data_evento: str | None = Field(
        default=None,
        description="Data do evento priorizando a conversao mais recente e com fallback do evento de origem.",
    )
    soma_de_ano_evento: int | None = Field(
        default=None,
        description="Ano da data do evento (coluna 'Soma de ano_evento' no export).",
    )
    tipo_evento: str | None = None
    local_evento: str | None = Field(
        default=None,
        description="Cidade-UF do evento priorizando a conversao mais recente e com fallback do evento de origem.",
    )
    faixa_etaria: str | None = None
    soma_de_idade: int | None = Field(
        default=None,
        description="Idade na data de referencia do evento (coluna 'Soma de idade').",
    )
    origem: str | None = Field(
        default=None,
        description="Proponente ou Ativação (lote de importação / fonte do lead).",
    )


class LeadListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[LeadListItemRead]
