"""Schemas para o dashboard de leads (GET /dashboard/leads)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DashboardLeadsQuery(BaseModel):
    data_inicio: date | None = None
    data_fim: date | None = None
    evento_id: int | None = Field(default=None, ge=1)
    # Deprecated: usar evento_id quando disponivel.
    evento_nome: str | None = Field(default=None, min_length=1, max_length=100)
    estado: str | None = Field(default=None, min_length=1, max_length=40)
    cidade: str | None = Field(default=None, min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=100)
    granularity: Literal["day", "month"] | None = None

    @model_validator(mode="after")
    def validate_range(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser maior/igual a data_inicio")
        return self


class DashboardLeadsFilters(BaseModel):
    data_inicio: date | None
    data_fim: date | None
    evento_id: int | None
    evento_nome: str | None
    estado: str | None
    cidade: str | None
    limit: int
    granularity: Literal["day", "month"]


class DashboardLeadsKpis(BaseModel):
    leads_total: int
    eventos_total: int
    ativacoes_total: int


class DashboardLeadsSeriesItem(BaseModel):
    periodo: str
    total: int


class DashboardLeadsSeries(BaseModel):
    granularity: Literal["day", "month"]
    leads: list[DashboardLeadsSeriesItem]


class DashboardLeadsRankEstado(BaseModel):
    estado: str
    total: int


class DashboardLeadsRankCidade(BaseModel):
    cidade: str
    total: int


class DashboardLeadsRankEvento(BaseModel):
    evento_id: int
    evento_nome: str
    total: int


class DashboardLeadsRankings(BaseModel):
    por_estado: list[DashboardLeadsRankEstado]
    por_cidade: list[DashboardLeadsRankCidade]
    por_evento: list[DashboardLeadsRankEvento]


class DashboardLeadsResponse(BaseModel):
    version: int = 1
    generated_at: datetime
    filters: DashboardLeadsFilters
    kpis: DashboardLeadsKpis
    series: DashboardLeadsSeries
    rankings: DashboardLeadsRankings
