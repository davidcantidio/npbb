"""Esquemas Pydantic para leitura de eventos."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic import model_validator


class DataHealthRead(BaseModel):
    version: int
    score: int | None
    band: str
    missing_fields: list[str] = Field(default_factory=list)
    filled_weight: int
    total_weight: int
    urgency_factor: float
    last_calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoListItem(BaseModel):
    id: int
    qr_code_url: Optional[str] = None
    external_project_code: Optional[str] = None
    nome: str
    investimento: Optional[Decimal] = None

    data_inicio_prevista: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    cidade: str
    estado: str

    diretoria_id: Optional[int] = None
    agencia_id: Optional[int] = None
    status_id: int
    data_health: DataHealthRead | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoRead(BaseModel):
    id: int
    thumbnail: Optional[str] = None
    template_override: Optional[str] = None
    cta_personalizado: Optional[str] = None
    descricao_curta: Optional[str] = None
    divisao_demandante_id: Optional[int] = None
    qr_code_url: Optional[str] = None
    external_project_code: Optional[str] = None

    nome: str
    descricao: Optional[str] = None
    investimento: Optional[Decimal] = None

    data_inicio_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None

    concorrencia: bool
    cidade: str
    estado: str

    agencia_id: Optional[int] = None
    diretoria_id: Optional[int] = None
    gestor_id: Optional[int] = None
    tipo_id: Optional[int] = None
    subtipo_id: Optional[int] = None

    tag_ids: list[int] = Field(default_factory=list)
    territorio_ids: list[int] = Field(default_factory=list)

    status_id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    investimento: Decimal | None = None
    concorrencia: bool = False
    cidade: str
    estado: str

    agencia_id: int | None = None
    diretoria_id: int | None = None
    gestor_id: int | None = None

    tipo_id: int | None = None
    subtipo_id: int | None = None

    tag_ids: list[int] = Field(default_factory=list)
    territorio_ids: list[int] = Field(default_factory=list)

    status_id: int | None = None

    thumbnail: Optional[str] = None
    template_override: Optional[str] = Field(default=None, max_length=50)
    cta_personalizado: Optional[str] = Field(default=None, max_length=200)
    descricao_curta: Optional[str] = Field(default=None, max_length=500)
    divisao_demandante_id: int | None = None
    qr_code_url: Optional[str] = None
    external_project_code: Optional[str] = None

    data_inicio_prevista: date
    data_fim_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None
    criar_ativacao_padrao_bb: bool = False

    model_config = ConfigDict(extra="forbid")

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
    investimento: Decimal | None = None
    concorrencia: bool | None = None
    cidade: str | None = None
    estado: str | None = None

    agencia_id: int | None = None
    diretoria_id: int | None = None
    gestor_id: int | None = None

    tipo_id: int | None = None
    subtipo_id: int | None = None

    tag_ids: list[int] | None = None
    territorio_ids: list[int] | None = None

    status_id: int | None = None

    thumbnail: str | None = None
    template_override: str | None = Field(default=None, max_length=50)
    cta_personalizado: str | None = Field(default=None, max_length=200)
    descricao_curta: str | None = Field(default=None, max_length=500)
    divisao_demandante_id: int | None = None
    qr_code_url: str | None = None
    external_project_code: str | None = None

    data_inicio_prevista: date | None = None
    data_fim_prevista: date | None = None
    data_inicio_realizada: date | None = None
    data_fim_realizada: date | None = None

    publico_projetado: int | None = None
    publico_realizado: int | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.data_inicio_prevista and self.data_fim_prevista:
            if self.data_fim_prevista < self.data_inicio_prevista:
                raise ValueError("data_fim_prevista deve ser maior/igual a data_inicio_prevista")
        if self.data_inicio_realizada and self.data_fim_realizada:
            if self.data_fim_realizada < self.data_inicio_realizada:
                raise ValueError("data_fim_realizada deve ser maior/igual a data_inicio_realizada")
        return self
