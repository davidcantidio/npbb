"""Schemas do endpoint de analise etaria do dashboard."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

AGE_ANALYSIS_RESPONSE_EXAMPLE = {
    "version": 2,
    "generated_at": "2026-03-08T12:00:00Z",
    "age_reference_date": "2026-03-08",
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
            "base_com_idade_volume": 110,
            "base_bb_coberta_volume": 108,
            "leads_proponente": 40,
            "leads_ativacao": 80,
            "leads_canal_desconhecido": 0,
            "clientes_bb_volume": 78,
            "clientes_bb_pct": 65.0,
            "nao_clientes_bb_volume": 30,
            "nao_clientes_bb_pct": 25.0,
            "bb_indefinido_volume": 12,
            "cobertura_bb_pct": 95.0,
            "faixas": {
                "faixa_18_25": {"volume": 30, "pct": 27.27},
                "faixa_26_40": {"volume": 60, "pct": 54.55},
                "faixa_18_40": {"volume": 90, "pct": 81.82},
                "fora_18_40": {"volume": 20, "pct": 18.18},
                "sem_info_volume": 10,
                "sem_info_pct_da_base": 8.33,
            },
            "faixa_dominante": "faixa_26_40",
            "faixa_dominante_status": "resolved",
        }
    ],
    "consolidado": {
        "base_total": 120,
        "base_com_idade_volume": 110,
        "base_bb_coberta_volume": 108,
        "leads_proponente": 40,
        "leads_ativacao": 80,
        "leads_canal_desconhecido": 0,
        "clientes_bb_volume": 78,
        "clientes_bb_pct": 65.0,
        "nao_clientes_bb_volume": 30,
        "nao_clientes_bb_pct": 25.0,
        "bb_indefinido_volume": 12,
        "cobertura_bb_pct": 95.0,
        "faixas": {
            "faixa_18_25": {"volume": 30, "pct": 27.27},
            "faixa_26_40": {"volume": 60, "pct": 54.55},
            "faixa_18_40": {"volume": 90, "pct": 81.82},
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
        "faixa_dominante_status": "resolved",
    },
    "qualidade_consolidado": {
        "base_vinculos": 120,
        "sem_cpf_volume": 5,
        "sem_cpf_pct": 4.17,
        "sem_data_nascimento_volume": 10,
        "sem_data_nascimento_pct": 8.33,
        "sem_nome_completo_volume": 3,
        "sem_nome_completo_pct": 2.5,
    },
    "qualidade_por_origem": [
        {
            "source_kind": "ativacao",
            "label": "Ativacao (captacao)",
            "base_vinculos": 80,
            "sem_cpf_volume": 2,
            "sem_cpf_pct": 2.5,
            "sem_data_nascimento_volume": 6,
            "sem_data_nascimento_pct": 7.5,
            "sem_nome_completo_volume": 1,
            "sem_nome_completo_pct": 1.25,
        }
    ],
    "confianca_consolidado": {
        "base_vinculos": 120,
        "base_com_idade_volume": 110,
        "base_bb_coberta_volume": 108,
        "dedupe_candidate_volume": 132,
        "dedupe_suppressed_volume": 12,
        "dedupe_suppressed_pct": 9.09,
        "event_name_candidate_volume": 18,
        "ambiguous_event_name_volume": 2,
        "ambiguous_event_name_pct": 11.11,
        "event_name_missing_volume": 1,
        "event_name_missing_pct": 5.56,
        "evento_nome_backfill_habilitado": True,
        "lineage_mix": [
            {
                "source_kind": "ativacao",
                "label": "Ativacao (captacao)",
                "volume": 80,
                "pct": 66.67,
            },
            {
                "source_kind": "lead_batch",
                "label": "Importacao (pipeline)",
                "volume": 30,
                "pct": 25.0,
            },
            {
                "source_kind": "evento_nome_backfill",
                "label": "Correspondencia por nome do evento",
                "volume": 10,
                "pct": 8.33,
            },
        ],
    },
    "insights": {
        "resumo": [
            "Base consolidada de 120 vinculos lead-evento em 1 evento(s).",
            "Distribuicao por canal: 80 ativacao, 40 proponente.",
        ],
        "alertas": [
            "Cobertura BB abaixo do limiar em alguns recortes; percentuais de cliente podem estar ocultos.",
        ],
        "flags": ["bb_coverage_low"],
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
    faixa_18_40: FaixaEtariaMetrics = Field(
        description="Soma das faixas 18-25 e 26-40; percentual sobre base com idade."
    )
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
    base_com_idade_volume: int = Field(
        description="Quantidade de vinculos com data de nascimento suficiente para classificar idade."
    )
    base_bb_coberta_volume: int = Field(
        description="Quantidade de vinculos com is_cliente_bb preenchido."
    )
    leads_proponente: int = Field(description="Vinculos com tipo_lead bilheteria ou entrada_evento.")
    leads_ativacao: int = Field(description="Vinculos com tipo_lead ativacao.")
    leads_canal_desconhecido: int = Field(
        description="Vinculos sem tipo_lead classificavel como proponente ou ativacao."
    )
    clientes_bb_volume: int | None = Field(
        default=None,
        description="Quantidade de clientes BB. Nulo quando a cobertura BB e insuficiente.",
    )
    clientes_bb_pct: float | None = Field(
        default=None,
        description="Percentual de clientes BB sobre a base total do evento.",
    )
    nao_clientes_bb_volume: int | None = Field(
        default=None,
        description="Leads com is_cliente_bb=false. Nulo quando cobertura BB abaixo do limiar.",
    )
    nao_clientes_bb_pct: float | None = Field(
        default=None,
        description="Percentual de nao clientes BB sobre a base total. Nulo quando cobertura BB abaixo do limiar.",
    )
    bb_indefinido_volume: int = Field(
        description="Leads com is_cliente_bb nulo (cruzamento pendente ou sem dado)."
    )
    cobertura_bb_pct: float = Field(
        description="Percentual de leads com is_cliente_bb preenchido."
    )
    faixas: AgeBreakdown
    faixa_dominante: str = Field(
        description="Faixa com maior volume no evento, incluindo sem_info quando aplicavel."
    )
    faixa_dominante_status: str = Field(
        description="resolved quando ha uma faixa dominante unica; tied em caso de empate; empty sem base."
    )


class TopEventoAgeAnalysis(BaseModel):
    evento_id: int
    evento_nome: str
    base_leads: int
    faixa_dominante: str


class ConsolidadoAgeAnalysis(BaseModel):
    base_total: int
    base_com_idade_volume: int
    base_bb_coberta_volume: int
    leads_proponente: int
    leads_ativacao: int
    leads_canal_desconhecido: int
    clientes_bb_volume: int | None = Field(
        default=None,
        description="Quantidade consolidada de clientes BB. Nulo quando a cobertura BB e insuficiente.",
    )
    clientes_bb_pct: float | None = Field(
        default=None,
        description="Percentual consolidado de clientes BB sobre a base total.",
    )
    nao_clientes_bb_volume: int | None = Field(
        default=None,
        description="Consolidado de is_cliente_bb=false. Nulo quando cobertura BB abaixo do limiar.",
    )
    nao_clientes_bb_pct: float | None = Field(
        default=None,
        description="Percentual consolidado de nao clientes BB. Nulo quando cobertura BB abaixo do limiar.",
    )
    bb_indefinido_volume: int
    cobertura_bb_pct: float = Field(
        description="Percentual consolidado de leads com is_cliente_bb preenchido."
    )
    faixas: AgeBreakdown
    top_eventos: list[TopEventoAgeAnalysis]
    media_por_evento: float
    mediana_por_evento: float
    concentracao_top3_pct: float
    faixa_dominante_status: str
    clientes_bb_base_idade_volume: int | None = Field(
        default=None,
        description="Vinculos clientes BB com idade conhecida; denominador dos percentuais abaixo.",
    )
    clientes_bb_faixa_18_40_volume: int | None = None
    clientes_bb_faixa_18_40_pct: float | None = None
    clientes_bb_fora_18_40_volume: int | None = None
    clientes_bb_fora_18_40_pct: float | None = None
    nao_clientes_bb_base_idade_volume: int | None = Field(
        default=None,
        description="Vinculos nao clientes BB com idade conhecida; denominador dos percentuais abaixo.",
    )
    nao_clientes_bb_faixa_18_40_volume: int | None = None
    nao_clientes_bb_faixa_18_40_pct: float | None = None
    nao_clientes_bb_fora_18_40_volume: int | None = None
    nao_clientes_bb_fora_18_40_pct: float | None = None


class CompletenessMetrics(BaseModel):
    base_vinculos: int
    sem_cpf_volume: int
    sem_cpf_pct: float
    sem_data_nascimento_volume: int
    sem_data_nascimento_pct: float
    sem_nome_completo_volume: int
    sem_nome_completo_pct: float


class OrigemQualidadeRow(BaseModel):
    source_kind: str
    label: str
    base_vinculos: int
    sem_cpf_volume: int
    sem_cpf_pct: float
    sem_data_nascimento_volume: int
    sem_data_nascimento_pct: float
    sem_nome_completo_volume: int
    sem_nome_completo_pct: float


class LineageMixRow(BaseModel):
    source_kind: str
    label: str
    volume: int
    pct: float


class ConfiancaConsolidado(BaseModel):
    base_vinculos: int
    base_com_idade_volume: int
    base_bb_coberta_volume: int
    dedupe_candidate_volume: int
    dedupe_suppressed_volume: int
    dedupe_suppressed_pct: float
    event_name_candidate_volume: int
    ambiguous_event_name_volume: int
    ambiguous_event_name_pct: float
    event_name_missing_volume: int
    event_name_missing_pct: float
    evento_nome_backfill_habilitado: bool
    lineage_mix: list[LineageMixRow]


class AgeAnalysisInsights(BaseModel):
    resumo: list[str]
    alertas: list[str]
    flags: list[str] = Field(default_factory=list)


class AgeAnalysisResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": AGE_ANALYSIS_RESPONSE_EXAMPLE})

    version: int = 2
    generated_at: datetime
    age_reference_date: date
    filters: AgeAnalysisFilters
    por_evento: list[EventoAgeAnalysis]
    consolidado: ConsolidadoAgeAnalysis
    qualidade_consolidado: CompletenessMetrics
    confianca_consolidado: ConfiancaConsolidado
    qualidade_por_origem: list[OrigemQualidadeRow]
    insights: AgeAnalysisInsights
