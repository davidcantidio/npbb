export type DashboardIconKey = "age-analysis" | "event-closure" | "event-conversion";

export type DashboardDomain = "leads" | "eventos";

export type DashboardManifestEntry = {
  id: string;
  route: string;
  domain: DashboardDomain;
  name: string;
  icon: DashboardIconKey;
  description: string;
  enabled: boolean;
};

export type AgeRangeKey = "faixa_18_25" | "faixa_26_40" | "faixa_18_40" | "fora_18_40";

export type DominantAgeRangeKey = AgeRangeKey | "sem_info";
export type DominantRangeStatus = "resolved" | "tied" | "empty";
export const AGE_ANALYSIS_RESPONSE_VERSION = 2;

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
  faixa_18_40: FaixaEtariaMetrics;
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
  base_com_idade_volume: number;
  base_bb_coberta_volume: number;
  leads_proponente: number;
  leads_ativacao: number;
  leads_canal_desconhecido: number;
  clientes_bb_volume: number | null;
  clientes_bb_pct: number | null;
  nao_clientes_bb_volume: number | null;
  nao_clientes_bb_pct: number | null;
  bb_indefinido_volume: number;
  cobertura_bb_pct: number;
  faixas: AgeBreakdown;
  faixa_dominante: DominantAgeRangeKey;
  faixa_dominante_status: DominantRangeStatus;
};

export type TopEventoAgeAnalysis = {
  evento_id: number;
  evento_nome: string;
  base_leads: number;
  faixa_dominante: DominantAgeRangeKey;
};

export type ConsolidadoAgeAnalysis = {
  base_total: number;
  base_com_idade_volume: number;
  base_bb_coberta_volume: number;
  leads_proponente: number;
  leads_ativacao: number;
  leads_canal_desconhecido: number;
  clientes_bb_volume: number | null;
  clientes_bb_pct: number | null;
  nao_clientes_bb_volume: number | null;
  nao_clientes_bb_pct: number | null;
  bb_indefinido_volume: number;
  cobertura_bb_pct: number;
  faixas: AgeBreakdown;
  top_eventos: TopEventoAgeAnalysis[];
  media_por_evento: number;
  mediana_por_evento: number;
  concentracao_top3_pct: number;
  faixa_dominante_status: DominantRangeStatus;
};

export type CompletenessMetrics = {
  base_vinculos: number;
  sem_cpf_volume: number;
  sem_cpf_pct: number;
  sem_data_nascimento_volume: number;
  sem_data_nascimento_pct: number;
  sem_nome_completo_volume: number;
  sem_nome_completo_pct: number;
};

export type OrigemQualidadeRow = CompletenessMetrics & {
  source_kind: string;
  label: string;
};

export type LineageMixRow = {
  source_kind: string;
  label: string;
  volume: number;
  pct: number;
};

export type ConfiancaConsolidado = {
  base_vinculos: number;
  base_com_idade_volume: number;
  base_bb_coberta_volume: number;
  dedupe_candidate_volume: number;
  dedupe_suppressed_volume: number;
  dedupe_suppressed_pct: number;
  event_name_candidate_volume: number;
  ambiguous_event_name_volume: number;
  ambiguous_event_name_pct: number;
  event_name_missing_volume: number;
  event_name_missing_pct: number;
  evento_nome_backfill_habilitado: boolean;
  lineage_mix: LineageMixRow[];
};

export type AgeAnalysisInsights = {
  resumo: string[];
  alertas: string[];
  flags: string[];
};

export type AgeAnalysisResponse = {
  version: number;
  generated_at: string;
  age_reference_date: string;
  filters: {
    data_inicio: string | null;
    data_fim: string | null;
    evento_id: number | null;
  };
  por_evento: EventoAgeAnalysis[];
  consolidado: ConsolidadoAgeAnalysis;
  qualidade_consolidado: CompletenessMetrics;
  confianca_consolidado: ConfiancaConsolidado;
  qualidade_por_origem: OrigemQualidadeRow[];
  insights: AgeAnalysisInsights;
};
