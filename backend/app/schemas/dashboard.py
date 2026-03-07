"""Schemas do endpoint de analise etaria do dashboard."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class AgeAnalysisQuery(BaseModel):
    data_inicio: date | None = Field(
        default=None,
        description="Data inicial do filtro sobre a criacao do lead.",
    )
    data_fim: date | None = Field(
        default=None,
        description="Data final do filtro sobre a criacao do lead.",
    )
    evento_id: int | None = Field(
        default=None,
        ge=1,
        description="Filtra a analise para um evento especifico.",
    )

    @model_validator(mode="after")
    def validate_range(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser maior/igual a data_inicio")
        return self


class AgeAnalysisFilters(BaseModel):
    data_inicio: date | None
    data_fim: date | None
    evento_id: int | None


class FaixaEtariaMetrics(BaseModel):
    volume: int = Field(description="Quantidade absoluta de leads na faixa.")
    pct: float = Field(
        description="Percentual da faixa sobre a base com data_nascimento informada."
    )


class AgeBreakdown(BaseModel):
    faixa_18_25: FaixaEtariaMetrics
    faixa_26_40: FaixaEtariaMetrics
    fora_18_40: FaixaEtariaMetrics
    sem_info_volume: int = Field(
        description="Quantidade de leads sem data_nascimento."
    )
    sem_info_pct_da_base: float = Field(
        description="Percentual de leads sem data_nascimento sobre a base total."
    )


class EventoAgeAnalysis(BaseModel):
    evento_id: int
    evento_nome: str
    cidade: str
    estado: str
    base_leads: int
    clientes_bb_volume: int | None = Field(
        default=None,
        description="Quantidade de clientes BB. Nulo quando a cobertura BB e insuficiente.",
    )
    clientes_bb_pct: float | None = Field(
        default=None,
        description="Percentual de clientes BB sobre a base total do evento.",
    )
    cobertura_bb_pct: float = Field(
        description="Percentual de leads com is_cliente_bb preenchido."
    )
    faixas: AgeBreakdown
    faixa_dominante: str = Field(
        description="Faixa com maior volume no evento, incluindo sem_info quando aplicavel."
    )


class TopEventoAgeAnalysis(BaseModel):
    evento_id: int
    evento_nome: str
    base_leads: int
    faixa_dominante: str


class ConsolidadoAgeAnalysis(BaseModel):
    base_total: int
    clientes_bb_volume: int | None = Field(
        default=None,
        description="Quantidade consolidada de clientes BB. Nulo quando a cobertura BB e insuficiente.",
    )
    clientes_bb_pct: float | None = Field(
        default=None,
        description="Percentual consolidado de clientes BB sobre a base total.",
    )
    cobertura_bb_pct: float = Field(
        description="Percentual consolidado de leads com is_cliente_bb preenchido."
    )
    faixas: AgeBreakdown
    top_eventos: list[TopEventoAgeAnalysis]
    media_por_evento: float
    mediana_por_evento: float
    concentracao_top3_pct: float


class AgeAnalysisResponse(BaseModel):
    version: int = 1
    generated_at: datetime
    filters: AgeAnalysisFilters
    por_evento: list[EventoAgeAnalysis]
    consolidado: ConsolidadoAgeAnalysis
