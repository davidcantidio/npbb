export type DashboardIconKey =
  | "age-analysis"
  | "event-closure"
  | "event-conversion"
  | "media-coverage";

export type DashboardDomain = "leads" | "eventos" | "publicidade";

export type DashboardManifestEntry = {
  id: string;
  route: string;
  domain: DashboardDomain;
  name: string;
  icon: DashboardIconKey;
  description: string;
  enabled: boolean;
};

export type AgeRangeKey = "faixa_18_25" | "faixa_26_40" | "fora_18_40";

export type DominantAgeRangeKey = AgeRangeKey | "sem_info";

export type AgeAnalysisFiltersQuery = {
  evento_id?: number;
  data_inicio?: string;
  data_fim?: string;
};

export type AgeAnalysisFilterFormValues = {
  evento_id: number | null;
  data_inicio: string;
  data_fim: string;
};

export type FaixaEtariaMetrics = {
  volume: number;
  pct: number;
};

export type AgeBreakdown = {
  faixa_18_25: FaixaEtariaMetrics;
  faixa_26_40: FaixaEtariaMetrics;
  fora_18_40: FaixaEtariaMetrics;
  sem_info_volume: number;
  sem_info_pct_da_base: number;
};

export type EventoAgeAnalysis = {
  evento_id: number;
  evento_nome: string;
  cidade: string;
  estado: string;
  base_leads: number;
  clientes_bb_volume: number | null;
  clientes_bb_pct: number | null;
  cobertura_bb_pct: number;
  faixas: AgeBreakdown;
  faixa_dominante: DominantAgeRangeKey;
};

export type TopEventoAgeAnalysis = {
  evento_id: number;
  evento_nome: string;
  base_leads: number;
  faixa_dominante: DominantAgeRangeKey;
};

export type ConsolidadoAgeAnalysis = {
  base_total: number;
  clientes_bb_volume: number | null;
  clientes_bb_pct: number | null;
  cobertura_bb_pct: number;
  faixas: AgeBreakdown;
  top_eventos: TopEventoAgeAnalysis[];
  media_por_evento: number;
  mediana_por_evento: number;
  concentracao_top3_pct: number;
};

export type AgeAnalysisResponse = {
  version: number;
  generated_at: string;
  filters: {
    data_inicio: string | null;
    data_fim: string | null;
    evento_id: number | null;
  };
  por_evento: EventoAgeAnalysis[];
  consolidado: ConsolidadoAgeAnalysis;
};
