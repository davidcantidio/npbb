"""Schemas de listagem de leads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LeadListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


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


class LeadListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[LeadListItemRead]
