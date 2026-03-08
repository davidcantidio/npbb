"""Schemas do endpoint de analise etaria do dashboard."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

AGE_ANALYSIS_RESPONSE_EXAMPLE = {
    "version": 1,
    "generated_at": "2026-03-08T12:00:00Z",
    "filters": {
        "data_inicio": "2026-01-01",
        "data_fim": "2026-01-31",
        "evento_id": 42,
    },
    "por_evento": [
        {
            "evento_id": 42,
            "evento_nome": "Festival BB Sao Paulo",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "base_leads": 120,
            "clientes_bb_volume": 78,
            "clientes_bb_pct": 65.0,
            "cobertura_bb_pct": 95.0,
            "faixas": {
                "faixa_18_25": {"volume": 30, "pct": 27.27},
                "faixa_26_40": {"volume": 60, "pct": 54.55},
                "fora_18_40": {"volume": 20, "pct": 18.18},
                "sem_info_volume": 10,
                "sem_info_pct_da_base": 8.33,
            },
            "faixa_dominante": "faixa_26_40",
        }
    ],
    "consolidado": {
        "base_total": 120,
        "clientes_bb_volume": 78,
        "clientes_bb_pct": 65.0,
        "cobertura_bb_pct": 95.0,
        "faixas": {
            "faixa_18_25": {"volume": 30, "pct": 27.27},
            "faixa_26_40": {"volume": 60, "pct": 54.55},
            "fora_18_40": {"volume": 20, "pct": 18.18},
            "sem_info_volume": 10,
            "sem_info_pct_da_base": 8.33,
        },
        "top_eventos": [
            {
                "evento_id": 42,
                "evento_nome": "Festival BB Sao Paulo",
                "base_leads": 120,
                "faixa_dominante": "faixa_26_40",
            }
        ],
        "media_por_evento": 120.0,
        "mediana_por_evento": 120.0,
        "concentracao_top3_pct": 100.0,
    },
}


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
    model_config = ConfigDict(json_schema_extra={"example": AGE_ANALYSIS_RESPONSE_EXAMPLE})

    version: int = 1
    generated_at: datetime
    filters: AgeAnalysisFilters
    por_evento: list[EventoAgeAnalysis]
    consolidado: ConsolidadoAgeAnalysis
