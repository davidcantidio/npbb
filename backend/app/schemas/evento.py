"""Esquemas Pydantic para leitura de eventos."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic import model_validator


class EventoListItem(BaseModel):
    id: int
    qr_code_url: Optional[str] = None
    nome: str

    data_inicio_prevista: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    cidade: str
    estado: str

    diretoria_id: Optional[int] = None
    agencia_id: int
    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoRead(BaseModel):
    id: int
    thumbnail: Optional[str] = None
    divisao_demandante: Optional[str] = None
    qr_code_url: Optional[str] = None

    nome: str
    descricao: str

    data_inicio_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None

    concorrencia: bool
    cidade: str
    estado: str

    agencia_id: int
    diretoria_id: Optional[int] = None
    gestor_id: Optional[int] = None
    tipo_id: int
    subtipo_id: Optional[int] = None

    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoCreate(BaseModel):
    nome: str
    descricao: str
    concorrencia: bool = False
    cidade: str
    estado: str

    agencia_id: int | None = None
    diretoria_id: int | None = None
    gestor_id: int | None = None

    tipo_id: int
    subtipo_id: int | None = None

    status: str = "Previsto"

    thumbnail: Optional[str] = None
    divisao_demandante: Optional[str] = None
    qr_code_url: Optional[str] = None

    data_inicio_prevista: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.data_inicio_prevista and self.data_fim_prevista:
            if self.data_fim_prevista < self.data_inicio_prevista:
                raise ValueError("data_fim_prevista deve ser maior/igual a data_inicio_prevista")
        if self.data_inicio_realizada and self.data_fim_realizada:
            if self.data_fim_realizada < self.data_inicio_realizada:
                raise ValueError("data_fim_realizada deve ser maior/igual a data_inicio_realizada")
        return self


class EventoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    concorrencia: bool | None = None
    cidade: str | None = None
    estado: str | None = None

    agencia_id: int | None = None
    diretoria_id: int | None = None
    gestor_id: int | None = None

    tipo_id: int | None = None
    subtipo_id: int | None = None

    status: str | None = None

    thumbnail: str | None = None
    divisao_demandante: str | None = None
    qr_code_url: str | None = None

    data_inicio_prevista: date | None = None
    data_fim_prevista: date | None = None
    data_inicio_realizada: date | None = None
    data_fim_realizada: date | None = None

    publico_projetado: int | None = None
    publico_realizado: int | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.data_inicio_prevista and self.data_fim_prevista:
            if self.data_fim_prevista < self.data_inicio_prevista:
                raise ValueError("data_fim_prevista deve ser maior/igual a data_inicio_prevista")
        if self.data_inicio_realizada and self.data_fim_realizada:
            if self.data_fim_realizada < self.data_inicio_realizada:
                raise ValueError("data_fim_realizada deve ser maior/igual a data_inicio_realizada")
        return self
