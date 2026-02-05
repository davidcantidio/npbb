"""Schemas para o relatorio agregado do dashboard de leads."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DashboardLeadsReportQuery(BaseModel):
    data_inicio: date | None = None
    data_fim: date | None = None
    evento_id: int | None = Field(default=None, ge=1)
    evento_nome: str | None = Field(default=None, min_length=1, max_length=150)

    @model_validator(mode="after")
    def validate_range(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser maior/igual a data_inicio")
        if not self.evento_id and not self.evento_nome:
            raise ValueError("evento_id ou evento_nome obrigatorio")
        return self


class DashboardLeadsReportFilters(BaseModel):
    data_inicio: date | None
    data_fim: date | None
    evento_id: int | None
    evento_nome: str | None


class DashboardLeadsReportBigNumbers(BaseModel):
    total_leads: int
    total_compras: int
    total_publico: int
    taxa_conversao: float
    criterio_publico: str
    criterio_compras: str


class DashboardLeadsDistribuicaoItem(BaseModel):
    faixa: str
    total: int
    percentual: float


class DashboardLeadsPerfilPublico(BaseModel):
    distribuicao_idade: list[DashboardLeadsDistribuicaoItem]
    distribuicao_genero: list[DashboardLeadsDistribuicaoItem]
    percent_sem_idade: float
    percent_sem_genero: float


class DashboardLeadsClientesBB(BaseModel):
    total_clientes_bb: int
    percentual_clientes_bb: float
    criterio_usado: str


class DashboardLeadsPreVenda(BaseModel):
    janela_pre_venda: str | None
    volume_pre_venda: int
    volume_venda_geral: int
    observacao: str | None


class DashboardLeadsRedes(BaseModel):
    status: Literal["sem_dados", "ok"]
    observacao: str | None = None
    metricas: dict[str, float] | None = None


class DashboardLeadsReportResponse(BaseModel):
    version: int = 1
    generated_at: datetime
    filters: DashboardLeadsReportFilters
    big_numbers: DashboardLeadsReportBigNumbers
    perfil_publico: DashboardLeadsPerfilPublico
    clientes_bb: DashboardLeadsClientesBB
    pre_venda: DashboardLeadsPreVenda
    redes: DashboardLeadsRedes
    dados_faltantes: list[str] = []
