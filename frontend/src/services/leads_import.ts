import { fetchWithAuth, handleApiResponse } from "./http";

/**
 * Servidor le/parseia ficheiros grandes do lote; o timeout HTTP por defeito (20s) e insuficiente
 * com XLSX pesados, DB lenta ou GET de estado do lote durante o pipeline Gold (locks / fila).
 */
const LEAD_BATCH_FILE_IO_TIMEOUT_MS = 120_000;
const LEAD_BATCH_STATUS_TIMEOUT_MS = 15_000;

export type ApiReadiness = {
  status: "ready";
  database?: {
    status: "ok";
    elapsed_ms?: number;
    endpoint?: Record<string, unknown>;
  };
};

export async function getApiReadiness(): Promise<ApiReadiness> {
  const res = await fetchWithAuth("/health/ready", {
    timeoutMs: 8_000,
    retries: 0,
  });
  return handleApiResponse<ApiReadiness>(res);
}

/**
 * Suggested mapping between an imported column and a canonical lead field.
 */
export type LeadImportSuggestion = {
  coluna: string;
  campo: string | null;
  confianca: number | null;
};

/**
 * Preview payload returned by backend before final lead import execution.
 */
export type LeadImportPreview = {
  filename: string;
  headers: string[];
  rows: string[][];
  delimiter: string;
  start_index: number;
  suggestions: LeadImportSuggestion[];
  samples_by_column: string[][];
  alias_hits?: Array<{
    tipo: string;
    valor_origem: string;
    canonical_value?: string | null;
    evento_id?: number | null;
  } | null>;
};

export type LeadImportEtlSeverity = "error" | "warning" | "info";

export type LeadImportEtlDQCheckResult = {
  check_name: string;
  severity: LeadImportEtlSeverity;
  affected_rows: number;
  sample: Array<Record<string, unknown>>;
  check_id?: string | null;
  message?: string | null;
};

export type LeadImportEtlHeaderColumn = {
  column_index: number;
  column_letter: string;
  source_value: string;
};

export type LeadImportEtlPreviewReady = {
  status: "previewed";
  session_token: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  dq_report: LeadImportEtlDQCheckResult[];
};

export type LeadImportEtlHeaderRequired = {
  status: "header_required";
  message: string;
  max_row: number;
  scanned_rows: number;
  required_fields: string[];
};

export type LeadImportEtlCpfColumnRequired = {
  status: "cpf_column_required";
  message: string;
  header_row: number;
  columns: LeadImportEtlHeaderColumn[];
  required_fields: string[];
};

export type LeadImportEtlPreview =
  | LeadImportEtlPreviewReady
  | LeadImportEtlHeaderRequired
  | LeadImportEtlCpfColumnRequired;

// Kept for compatibility with existing imports/tests.
export type LeadImportEtlPreviewResponse = LeadImportEtlPreview;

export type LeadImportEtlFieldAliasSelection = {
  column_index?: number;
  source_value?: string | null;
};

export type LeadImportEtlPreviewOptions = {
  headerRow?: number;
  fieldAliases?: Record<string, LeadImportEtlFieldAliasSelection>;
};

export type LeadImportEtlResult = {
  session_token: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  strict: boolean;
  status: "previewed" | "committed" | "expired" | "rejected";
  dq_report: LeadImportEtlDQCheckResult[];
};

export type OrigemLoteLeadBatch = "proponente" | "ativacao";

export type CreateLeadBatchPayload = {
  plataforma_origem: string;
  data_envio: string;
  quem_enviou?: string;
  /** Evento associado ao lote (opcional na API; obrigatório no fluxo Bronze do shell de importação). */
  evento_id?: number;
  /** Origem declarada no upload Bronze (default proponente). */
  origem_lote?: OrigemLoteLeadBatch;
  /** Quando origem_lote=proponente: bilheteria ou entrada_evento. */
  tipo_lead_proponente?: "bilheteria" | "entrada_evento";
  /** Obrigatório quando origem_lote=ativacao; deve pertencer ao evento_id. */
  ativacao_id?: number;
  file: File;
};

export type LeadBatch = {
  id: number;
  enviado_por: number;
  plataforma_origem: string;
  data_envio: string;
  data_upload: string;
  nome_arquivo_original: string;
  stage: "bronze" | "silver" | "gold";
  evento_id: number | null;
  origem_lote: OrigemLoteLeadBatch;
  tipo_lead_proponente: string | null;
  ativacao_id: number | null;
  pipeline_status: "pending" | "pass" | "pass_with_warnings" | "fail";
  pipeline_progress: PipelineProgress | null;
  pipeline_report: PipelineReport | null;
  created_at: string;
};

export type PipelineProgressStep =
  | "queued"
  | "silver_csv"
  | "source_adapt"
  | "event_taxonomy"
  | "normalize_rows"
  | "dedupe"
  | "contract_check"
  | "write_outputs"
  | "insert_leads";

export type PipelineProgress = {
  step: PipelineProgressStep;
  label: string;
  pct: number | null;
  updated_at: string;
};

export type BirthDateControlIssue =
  | "missing"
  | "unparseable"
  | "future"
  | "before_min";

export type BirthDateControlEntry = {
  source_file: string;
  source_sheet: string;
  source_row: number;
  issue: BirthDateControlIssue;
};

export type LocalidadeControleEntry = {
  source_file: string;
  source_sheet: string;
  source_row: number;
  issue: string;
  matched_by?: string | null;
  raw_value?: string | null;
  raw_cidade?: string | null;
  raw_estado?: string | null;
  raw_local?: string | null;
};

/** Linha da planilha/arquivo de origem associada a um problema na pipeline Gold. */
export type PipelineSourceRowRef = {
  source_file: string;
  source_sheet: string;
  source_row: number;
};

export type PipelineInvalidRecord = PipelineSourceRowRef & {
  motivo_rejeicao: string;
  row_data?: Record<string, string>;
};

export type PipelineReport = {
  lote_id: string;
  run_timestamp: string;
  totals: {
    raw_rows: number;
    valid_rows: number;
    discarded_rows: number;
  };
  quality_metrics: {
    cpf_invalid_discarded: number;
    telefone_invalid: number;
    data_evento_invalid: number;
    data_nascimento_invalid: number;
    data_nascimento_missing: number;
    duplicidades_cpf_evento: number;
    cidade_fora_mapeamento: number;
    localidade_invalida: number;
    localidade_nao_resolvida: number;
    localidade_fora_brasil: number;
    localidade_cidade_uf_inconsistente: number;
  };
  gate: {
    status: "PASS" | "PASS_WITH_WARNINGS" | "FAIL";
    decision: "promote" | "hold";
    fail_reasons: string[];
    warnings: string[];
  };
  failure_context?: {
    step?: string;
    stage?: string;
    exception_type?: string;
    detail?: string;
    message?: string;
  };
  data_nascimento_controle?: BirthDateControlEntry[];
  localidade_controle?: LocalidadeControleEntry[];
  /** Registros descartados na normalização/dedup (motivos separados por `;`). */
  invalid_records?: PipelineInvalidRecord[];
  cidade_fora_mapeamento_controle?: PipelineSourceRowRef[];
};

export type ExecutarPipelineResult = {
  batch_id: number;
  status: "queued";
};

export type LeadBatchPreview = {
  headers: string[];
  rows: string[][];
  total_rows: number;
};

/**
 * Lead representation used in frontend listing tables.
 */
export type LeadListItem = {
  id: number;
  nome: string | null;
  sobrenome: string | null;
  email: string | null;
  cpf: string | null;
  telefone: string | null;
  evento_nome: string | null;
  cidade: string | null;
  estado: string | null;
  data_compra: string | null;
  data_criacao: string;
  evento_convertido_id: number | null;
  evento_convertido_nome: string | null;
  tipo_conversao: string | null;
  data_conversao: string | null;
  // Personal document fields
  rg: string | null;
  genero: string | null;
  is_cliente_bb?: boolean | null;
  is_cliente_estilo?: boolean | null;
  // Address fields
  logradouro: string | null;
  numero: string | null;
  complemento: string | null;
  bairro: string | null;
  cep: string | null;
  /** Exportacao CSV (layout tipo pivot / data 2.csv) */
  data_nascimento?: string | null;
  data_evento?: string | null;
  soma_de_ano_evento?: number | null;
  tipo_evento?: string | null;
  faixa_etaria?: string | null;
  soma_de_idade?: number | null;
};

/**
 * Paginated lead response returned by backend listing endpoint.
 */
export type LeadListResponse = {
  page: number;
  page_size: number;
  total: number;
  items: LeadListItem[];
};

/**
 * Uploads a lead file and returns parsed preview metadata and suggestions.
 * @param token Bearer token used for authorization.
 * @param file Source CSV/XLSX file selected by user.
 * @param sampleRows Number of rows used by backend preview heuristics.
 * @returns Structured preview with headers, sample rows and mapping suggestions.
 * @throws Error When upload fails or backend returns non-success status.
 */
export async function previewLeadImport(
  token: string,
  file: File,
  sampleRows = 10,
): Promise<LeadImportPreview> {
  const form = new FormData();
  form.append("file", file);
  form.append("sample_rows", String(sampleRows));

  const res = await fetchWithAuth("/leads/import/preview", {
    method: "POST",
    token,
    body: form,
    timeoutMs: 60_000,
    retries: 0,
  });
  return handleApiResponse<LeadImportPreview>(res);
}

export async function createLeadBatch(
  token: string,
  payload: CreateLeadBatchPayload,
): Promise<LeadBatch> {
  const form = new FormData();
  form.append("file", payload.file);
  form.append("plataforma_origem", payload.plataforma_origem);
  form.append("data_envio", payload.data_envio);
  if (payload.evento_id != null && Number.isFinite(payload.evento_id)) {
    form.append("evento_id", String(payload.evento_id));
  }
  if (payload.origem_lote) {
    form.append("origem_lote", payload.origem_lote);
  }
  if (payload.tipo_lead_proponente) {
    form.append("tipo_lead_proponente", payload.tipo_lead_proponente);
  }
  if (payload.ativacao_id != null && Number.isFinite(payload.ativacao_id)) {
    form.append("ativacao_id", String(payload.ativacao_id));
  }
  if (payload.quem_enviou) {
    // Campo reservado para evolucao futura do contrato de API.
    form.append("quem_enviou", payload.quem_enviou);
  }

  const res = await fetchWithAuth("/leads/batches", {
    method: "POST",
    token,
    body: form,
    timeoutMs: 60_000,
    retries: 0,
  });
  return handleApiResponse<LeadBatch>(res);
}

export async function getLeadBatchPreview(token: string, batchId: number): Promise<LeadBatchPreview> {
  const res = await fetchWithAuth(`/leads/batches/${batchId}/preview`, {
    token,
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<LeadBatchPreview>(res);
}

export async function previewLeadImportEtl(
  token: string,
  file: File,
  eventoId: number,
  strict = false,
  options?: LeadImportEtlPreviewOptions,
): Promise<LeadImportEtlPreview> {
  const form = new FormData();
  form.append("file", file);
  form.append("evento_id", String(eventoId));
  form.append("strict", String(strict));
  if (options?.headerRow) {
    form.append("header_row", String(options.headerRow));
  }
  if (options?.fieldAliases && Object.keys(options.fieldAliases).length > 0) {
    form.append("field_aliases_json", JSON.stringify(options.fieldAliases));
  }

  const res = await fetchWithAuth("/leads/import/etl/preview", {
    method: "POST",
    token,
    body: form,
    timeoutMs: 60_000,
    retries: 0,
  });
  return handleApiResponse<LeadImportEtlPreview>(res);
}

export async function commitLeadImportEtl(
  token: string,
  sessionToken: string,
  eventoId: number,
  forceWarnings = false,
): Promise<LeadImportEtlResult> {
  const res = await fetchWithAuth("/leads/import/etl/commit", {
    method: "POST",
    token,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_token: sessionToken,
      evento_id: eventoId,
      force_warnings: forceWarnings,
    }),
    retries: 0,
  });
  return handleApiResponse<LeadImportEtlResult>(res);
}

/**
 * Evento option returned by the reference endpoint — includes date for label formatting.
 */
export type ReferenciaEvento = {
  id: number;
  nome: string;
  data_inicio_prevista: string | null;
};

/**
 * Lists reference events available for mapping helpers.
 * @param token Bearer token used for authorization.
 * @returns Event reference options sorted by date descending.
 * @throws Error When request fails.
 */
export async function listReferenciaEventos(token: string): Promise<ReferenciaEvento[]> {
  const res = await fetchWithAuth("/leads/referencias/eventos", {
    token,
    timeoutMs: 60_000,
  });
  return handleApiResponse<ReferenciaEvento[]>(res);
}

// ---------------------------------------------------------------------------
// F2 — Silver mapping
// ---------------------------------------------------------------------------

export type ColumnConfidence = "exact_match" | "synonym_match" | "alias_match" | "none";

export type ColumnSuggestion = {
  coluna_original: string;
  campo_sugerido: string | null;
  confianca: ColumnConfidence;
};

export type ColunasResponse = {
  batch_id: number;
  colunas: ColumnSuggestion[];
};

export type MapearBatchPayload = {
  evento_id: number;
  mapeamento: Record<string, string>;
};

export type MapearBatchResult = {
  batch_id: number;
  silver_count: number;
  stage: string;
};

export async function getLeadBatchColunas(token: string, batchId: number): Promise<ColunasResponse> {
  const res = await fetchWithAuth(`/leads/batches/${batchId}/colunas`, {
    token,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<ColunasResponse>(res);
}

export async function mapearLeadBatch(
  token: string,
  batchId: number,
  payload: MapearBatchPayload,
): Promise<MapearBatchResult> {
  const res = await fetchWithAuth(`/leads/batches/${batchId}/mapear`, {
    method: "POST",
    token,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<MapearBatchResult>(res);
}

export async function getLeadBatch(token: string, batchId: number): Promise<LeadBatch> {
  const res = await fetchWithAuth(`/leads/batches/${batchId}`, {
    token,
    retries: 0,
    timeoutMs: LEAD_BATCH_STATUS_TIMEOUT_MS,
  });
  return handleApiResponse<LeadBatch>(res);
}

export async function executarPipeline(
  token: string,
  batchId: number,
): Promise<ExecutarPipelineResult> {
  const res = await fetchWithAuth(`/leads/batches/${batchId}/executar-pipeline`, {
    method: "POST",
    token,
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<ExecutarPipelineResult>(res);
}

/**
 * Lists leads with optional pagination controls.
 * @param token Bearer token used for authorization.
 * @param params Optional pagination arguments.
 * @returns Paginated lead list response.
 * @throws Error When request fails.
 */
export async function listLeads(
  token: string,
  params?: {
    page?: number;
    page_size?: number;
    data_inicio?: string;
    data_fim?: string;
    evento_id?: number;
  },
): Promise<LeadListResponse> {
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.page_size) qs.set("page_size", String(params.page_size));
  if (params?.data_inicio) qs.set("data_inicio", params.data_inicio);
  if (params?.data_fim) qs.set("data_fim", params.data_fim);
  if (typeof params?.evento_id === "number") qs.set("evento_id", String(params.evento_id));
  const url = `/leads${qs.toString() ? `?${qs}` : ""}`;

  const res = await fetchWithAuth(url, { token });
  return handleApiResponse<LeadListResponse>(res);
}
