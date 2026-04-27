import { fetchWithAuth, handleApiResponse } from "./http";

/**
 * Servidor le/parseia ficheiros grandes do lote; o timeout HTTP por defeito (20s) e insuficiente
 * com XLSX pesados, DB lenta ou GET de estado do lote durante o pipeline Gold (locks / fila).
 * O estado do pipeline na UI usa polling com backoff quando step/pct ficam estagnados (Task 5).
 * GETs de estado (getLeadBatch, preview, colunas) partilham o mesmo limite: durante insert_leads
 * com dezenas de milhares de linhas a resposta pode demorar >15s sem o pipeline estar falho.
 */
const LEAD_BATCH_FILE_IO_TIMEOUT_MS = 120_000;
const LEAD_BATCH_STATUS_TIMEOUT_MS = 120_000;
const LEAD_BATCH_READINESS_TIMEOUT_MS = 20_000;
export const LEADS_EXPORT_TIMEOUT_MS = 15 * 60_000;
/** GET /leads com filtros (intervalo de datas do evento, busca, evento, origem) dispara COUNT/joins pesados; 20s corta o pedido. */
export const LEADS_LIST_FILTERED_TIMEOUT_MS = 600_000;
export const DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON =
  "Vincule uma agencia ao evento antes de importar leads de ativacao.";

type LeadGoldLogLevel = "info" | "warn" | "error";

function logLeadGoldFlow(level: LeadGoldLogLevel, event: string, context: Record<string, unknown>) {
  const payload = {
    ...context,
    ts: new Date().toISOString(),
  };
  const logger = level === "error" ? console.error : level === "warn" ? console.warn : console.info;
  logger(`[lead-gold-flow] ${event}`, payload);
}

function describeLeadGoldError(error: unknown) {
  if (error instanceof Error) {
    const details: Record<string, unknown> = {
      name: error.name,
      message: error.message,
    };
    const maybeCode = (error as { code?: unknown }).code;
    const maybeStatus = (error as { status?: unknown }).status;
    if (typeof maybeCode === "string") {
      details.code = maybeCode;
    }
    if (typeof maybeStatus === "number") {
      details.status = maybeStatus;
    }
    return details;
  }
  return { error };
}

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
    timeoutMs: LEAD_BATCH_READINESS_TIMEOUT_MS,
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
  sheet_name?: string | null;
  available_sheets?: string[];
};

export type LeadImportEtlHeaderRequired = {
  status: "header_required";
  message: string;
  max_row: number;
  scanned_rows: number;
  required_fields: string[];
  available_sheets?: string[];
  active_sheet?: string | null;
};

export type LeadImportEtlCpfColumnRequired = {
  status: "cpf_column_required";
  message: string;
  header_row: number;
  columns: LeadImportEtlHeaderColumn[];
  required_fields: string[];
  available_sheets?: string[];
  active_sheet?: string | null;
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

/** Limite alinhado ao backend (`ETL_MAX_SCAN_ROWS_CAP`). */
export const LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP = 500;

export type LeadImportEtlPreviewOptions = {
  headerRow?: number;
  fieldAliases?: Record<string, LeadImportEtlFieldAliasSelection>;
  sheetName?: string;
  maxScanRows?: number;
};

export type LeadImportEtlPersistenceFailure = {
  row_number: number;
  reason: string;
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
  status: "previewed" | "committed" | "expired" | "rejected" | "partial_failure";
  dq_report: LeadImportEtlDQCheckResult[];
  persistence_failures: LeadImportEtlPersistenceFailure[];
};

export type OrigemLoteLeadBatch = "proponente" | "ativacao";

export type LeadImportMetadataHint = {
  arquivo_sha256: string;
  source_batch_id: number;
  plataforma_origem: string;
  data_envio: string;
  origem_lote: OrigemLoteLeadBatch | null;
  enrichment_only: boolean;
  tipo_lead_proponente: "bilheteria" | "entrada_evento" | null;
  evento_id: number | null;
  ativacao_id: number | null;
  confidence: "exact_hash_match";
  source_created_at: string;
};

export type LeadBatchIntakeItemPayload = {
  client_row_id: string;
  plataforma_origem: string;
  data_envio: string;
  evento_id?: number;
  origem_lote?: OrigemLoteLeadBatch;
  enrichment_only?: boolean;
  tipo_lead_proponente?: "bilheteria" | "entrada_evento";
  ativacao_id?: number;
  file: File;
};

export type LeadBatchIntakePayload = {
  items: LeadBatchIntakeItemPayload[];
};

export type CreateLeadBatchPayload = {
  plataforma_origem: string;
  data_envio: string;
  quem_enviou?: string;
  /** Evento associado ao lote (opcional na API; obrigatório no fluxo Bronze do shell de importação). */
  evento_id?: number;
  /** Origem declarada no upload Bronze; pode ser omitida em enrichment_only. */
  origem_lote?: OrigemLoteLeadBatch | null;
  /** Quando true: envia para o fluxo de enriquecimento sem evento. */
  enrichment_only?: boolean;
  /** Contexto opcional da classificação do lead; obrigatório apenas no fluxo com evento + proponente. */
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
  origem_lote: OrigemLoteLeadBatch | null;
  enrichment_only: boolean;
  tipo_lead_proponente: string | null;
  ativacao_id: number | null;
  pipeline_status: "pending" | "pass" | "pass_with_warnings" | "fail" | "stalled";
  pipeline_progress: PipelineProgress | null;
  pipeline_report: PipelineReport | null;
  created_at: string;
  /** Segundos sem atualizacao de progresso antes de considerar orfao (API). */
  gold_pipeline_stale_after_seconds?: number | null;
  /** True quando o backend considera o progresso Gold obsoleto (worker morto). */
  gold_pipeline_progress_is_stale?: boolean | null;
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
  reclaimed_stale_lock?: boolean;
};

export type LeadBatchPreview = {
  headers: string[];
  rows: string[][];
  total_rows: number;
};

export type LeadBatchIntakeItemResult = {
  client_row_id: string;
  batch: LeadBatch;
  preview: LeadBatchPreview;
  hint_applied: LeadImportMetadataHint | null;
};

export type LeadBatchIntakeResult = {
  items: LeadBatchIntakeItemResult[];
};

export type LeadImportEtlJobStatus =
  | "queued"
  | "running"
  | "header_required"
  | "cpf_column_required"
  | "previewed"
  | "commit_queued"
  | "committing"
  | "committed"
  | "partial_failure"
  | "failed";

export type LeadImportEtlJobProgress = {
  phase: "preview" | "commit";
  label: string;
  pct: number | null;
  updated_at: string;
};

export type LeadImportEtlJob = {
  job_id: string;
  evento_id: number;
  filename: string;
  status: LeadImportEtlJobStatus;
  strict: boolean;
  preview_session_token?: string | null;
  progress?: LeadImportEtlJobProgress | null;
  preview_result?: LeadImportEtlPreview | null;
  commit_result?: LeadImportEtlResult | null;
  error_code?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
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
  local_evento?: string | null;
  faixa_etaria?: string | null;
  soma_de_idade?: number | null;
  /** Proponente | Ativação (export CSV / listagem). */
  origem?: string | null;
  /** Datas do evento priorizando conversão mais recente; senão evento de origem do lote (ISO). */
  evento_inicio_prevista?: string | null;
  evento_fim_prevista?: string | null;
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

export type LeadListOrigin = "proponente" | "ativacao";
export type LeadListSortBy = "data_criacao" | "nome" | "email" | "evento" | "origem" | "local";
export type LeadListSortDir = "asc" | "desc";

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
  if (payload.origem_lote != null) {
    form.append("origem_lote", payload.origem_lote);
  }
  if (payload.enrichment_only != null) {
    form.append("enrichment_only", String(Boolean(payload.enrichment_only)));
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

export async function createLeadBatchIntake(
  token: string,
  payload: LeadBatchIntakePayload,
): Promise<LeadBatchIntakeResult> {
  const form = new FormData();
  const manifest = {
    items: payload.items.map((item) => ({
      client_row_id: item.client_row_id,
      plataforma_origem: item.plataforma_origem,
      data_envio: item.data_envio,
      ...(item.evento_id != null ? { evento_id: item.evento_id } : {}),
      ...(item.origem_lote != null ? { origem_lote: item.origem_lote } : {}),
      enrichment_only: Boolean(item.enrichment_only),
      ...(item.tipo_lead_proponente ? { tipo_lead_proponente: item.tipo_lead_proponente } : {}),
      ...(item.ativacao_id != null ? { ativacao_id: item.ativacao_id } : {}),
      file_name: item.file.name,
    })),
  };
  form.append("manifest_json", JSON.stringify(manifest));
  payload.items.forEach((item) => {
    form.append("files", item.file, item.file.name);
  });

  const res = await fetchWithAuth("/leads/batches/intake", {
    method: "POST",
    token,
    body: form,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
    retries: 0,
  });
  return handleApiResponse<LeadBatchIntakeResult>(res);
}

export async function getLeadImportMetadataHint(
  token: string,
  arquivoSha256: string,
): Promise<LeadImportMetadataHint | null> {
  const normalizedHash = arquivoSha256.trim().toLowerCase();
  const res = await fetchWithAuth(
    `/leads/batches/import-hint?arquivo_sha256=${encodeURIComponent(normalizedHash)}`,
    {
      token,
      retries: 0,
      timeoutMs: LEAD_BATCH_STATUS_TIMEOUT_MS,
    },
  );
  if (res.status === 204) {
    return null;
  }
  return handleApiResponse<LeadImportMetadataHint>(res);
}

export async function computeFileSha256Hex(file: Blob): Promise<string> {
  if (!globalThis.crypto?.subtle) {
    throw new Error("Web Crypto indisponivel para SHA-256.");
  }
  const buffer = await file.arrayBuffer();
  const digest = await globalThis.crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

export function normalizeLeadImportHintDateInput(value: string | null | undefined): string {
  const raw = String(value ?? "").trim();
  if (!raw) return "";
  if (raw.length >= 10 && raw[4] === "-" && raw[7] === "-") {
    return raw.slice(0, 10);
  }

  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? "" : parsed.toISOString().slice(0, 10);
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
  if (options?.sheetName?.trim()) {
    form.append("sheet_name", options.sheetName.trim());
  }
  if (options?.maxScanRows != null && Number.isFinite(options.maxScanRows)) {
    form.append("max_scan_rows", String(Math.floor(options.maxScanRows)));
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

export async function startLeadImportEtlJob(
  token: string,
  file: File,
  eventoId: number,
  strict = false,
  options?: LeadImportEtlPreviewOptions,
): Promise<{ job_id: string; status: "queued" }> {
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
  if (options?.sheetName?.trim()) {
    form.append("sheet_name", options.sheetName.trim());
  }
  if (options?.maxScanRows != null && Number.isFinite(options.maxScanRows)) {
    form.append("max_scan_rows", String(Math.floor(options.maxScanRows)));
  }
  const res = await fetchWithAuth("/leads/import/etl/jobs", {
    method: "POST",
    token,
    body: form,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
    retries: 0,
  });
  return handleApiResponse<{ job_id: string; status: "queued" }>(res);
}

export async function getLeadImportEtlJob(token: string, jobId: string): Promise<LeadImportEtlJob> {
  const res = await fetchWithAuth(`/leads/import/etl/jobs/${jobId}`, {
    token,
    retries: 0,
    timeoutMs: LEAD_BATCH_STATUS_TIMEOUT_MS,
  });
  return handleApiResponse<LeadImportEtlJob>(res);
}

export async function reprocessLeadImportEtlJobPreview(
  token: string,
  jobId: string,
  options?: LeadImportEtlPreviewOptions,
): Promise<{ job_id: string; status: "queued" }> {
  const body = {
    header_row: options?.headerRow,
    field_aliases: options?.fieldAliases ?? {},
    sheet_name: options?.sheetName?.trim() || undefined,
    max_scan_rows:
      options?.maxScanRows != null && Number.isFinite(options.maxScanRows)
        ? Math.floor(options.maxScanRows)
        : undefined,
  };
  const res = await fetchWithAuth(`/leads/import/etl/jobs/${jobId}/reprocess-preview`, {
    method: "POST",
    token,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<{ job_id: string; status: "queued" }>(res);
}

export async function commitLeadImportEtlJob(
  token: string,
  jobId: string,
  forceWarnings = false,
): Promise<{ job_id: string; status: "commit_queued" }> {
  const res = await fetchWithAuth(`/leads/import/etl/jobs/${jobId}/commit`, {
    method: "POST",
    token,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      force_warnings: forceWarnings,
    }),
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<{ job_id: string; status: "commit_queued" }>(res);
}

/**
 * Evento option returned by the reference endpoint — includes date for label formatting.
 */
export type ReferenciaEvento = {
  id: number;
  nome: string;
  data_inicio_prevista: string | null;
  agencia_id?: number | null;
  supports_activation_import?: boolean;
  activation_import_block_reason?: string | null;
  /** Distinct leads com registro em `lead_evento` para este evento (Gold). */
  leads_count?: number;
};

export function supportsActivationImport(evento: Pick<ReferenciaEvento, "supports_activation_import"> | null | undefined) {
  return evento?.supports_activation_import ?? true;
}

export function getActivationImportBlockReason(
  evento: Pick<ReferenciaEvento, "activation_import_block_reason"> | null | undefined,
) {
  return evento?.activation_import_block_reason ?? null;
}

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

export type BatchColumnOccurrence = {
  batch_id: number;
  file_name: string;
  coluna_original: string;
  amostras: string[];
  campo_sugerido: string | null;
  confianca: ColumnConfidence;
  evento_id: number | null;
  plataforma_origem: string;
};

export type BatchColumnGroup = {
  chave_agregada: string;
  nome_exibicao: string;
  variantes: string[];
  aparece_em_arquivos: number;
  ocorrencias: BatchColumnOccurrence[];
  campo_sugerido: string | null;
  confianca: ColumnConfidence;
  warnings: string[];
};

export type ColunasBatchResponse = {
  batch_ids: number[];
  primary_batch_id: number | null;
  aggregation_rule: string;
  colunas: BatchColumnGroup[];
  warnings: string[];
  blockers: string[];
  blocked_batch_ids: number[];
};

export type MapearBatchPayload = {
  evento_id: number | null;
  mapeamento: Record<string, string>;
};

export type MapearBatchResult = {
  batch_id: number;
  silver_count: number;
  stage: string;
};

export type MapearLotesBatchPayload = {
  batch_ids: number[];
  mapeamento: Record<string, string>;
};

export type MapearLotesBatchItem = {
  batch_id: number;
  silver_count: number;
  stage: string;
};

export type MapearLotesBatchResult = {
  batch_ids: number[];
  primary_batch_id: number;
  total_silver_count: number;
  results: MapearLotesBatchItem[];
  stage: string;
};

export async function getLeadBatchColunas(token: string, batchId: number): Promise<ColunasResponse> {
  const res = await fetchWithAuth(`/leads/batches/${batchId}/colunas`, {
    token,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<ColunasResponse>(res);
}

export async function getLeadBatchColunasBatch(
  token: string,
  batchIds: number[],
): Promise<ColunasBatchResponse> {
  const res = await fetchWithAuth("/leads/batches/colunas", {
    method: "POST",
    token,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ batch_ids: batchIds }),
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<ColunasBatchResponse>(res);
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

export async function mapearLeadBatches(
  token: string,
  payload: MapearLotesBatchPayload,
): Promise<MapearLotesBatchResult> {
  const res = await fetchWithAuth("/leads/batches/mapear", {
    method: "POST",
    token,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  return handleApiResponse<MapearLotesBatchResult>(res);
}

export async function getLeadBatch(token: string, batchId: number): Promise<LeadBatch> {
  const path = `/leads/batches/${batchId}`;
  logLeadGoldFlow("info", "get-batch.request", {
    batchId,
    path,
    timeoutMs: LEAD_BATCH_STATUS_TIMEOUT_MS,
  });
  try {
    const res = await fetchWithAuth(path, {
      token,
      retries: 0,
      timeoutMs: LEAD_BATCH_STATUS_TIMEOUT_MS,
    });
    const data = await handleApiResponse<LeadBatch>(res);
    logLeadGoldFlow("info", "get-batch.response", {
      batchId,
      path,
      httpStatus: res.status,
      stage: data.stage,
      pipelineStatus: data.pipeline_status,
      pipelineStep: data.pipeline_progress?.step ?? null,
      pipelinePct: data.pipeline_progress?.pct ?? null,
      pipelineUpdatedAt: data.pipeline_progress?.updated_at ?? null,
    });
    return data;
  } catch (error) {
    logLeadGoldFlow("error", "get-batch.error", {
      batchId,
      path,
      timeoutMs: LEAD_BATCH_STATUS_TIMEOUT_MS,
      ...describeLeadGoldError(error),
    });
    throw error;
  }
}

export async function executarPipeline(
  token: string,
  batchId: number,
): Promise<ExecutarPipelineResult> {
  const path = `/leads/batches/${batchId}/executar-pipeline`;
  logLeadGoldFlow("info", "execute-pipeline.request", {
    batchId,
    path,
    timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
  });
  try {
    const res = await fetchWithAuth(path, {
      method: "POST",
      token,
      retries: 0,
      timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
    });
    const data = await handleApiResponse<ExecutarPipelineResult>(res);
    logLeadGoldFlow("info", "execute-pipeline.response", {
      batchId,
      path,
      httpStatus: res.status,
      status: data.status,
    });
    return data;
  } catch (error) {
    logLeadGoldFlow("error", "execute-pipeline.error", {
      batchId,
      path,
      timeoutMs: LEAD_BATCH_FILE_IO_TIMEOUT_MS,
      ...describeLeadGoldError(error),
    });
    throw error;
  }
}

/**
 * Lists leads with optional pagination controls.
 * @param token Bearer token used for authorization.
 * @param params Optional pagination arguments.
 * @returns Paginated lead list response.
 * @throws Error When request fails.
 */
function leadListUsesHeavyBackendQuery(
  params?: {
    data_inicio?: string;
    data_fim?: string;
    search?: string;
    evento_id?: number;
    origem?: LeadListOrigin;
    long_running?: boolean;
  },
): boolean {
  if (!params) return false;
  if (params.long_running) return true;
  if (params.data_inicio || params.data_fim) return true;
  if (typeof params.evento_id === "number") return true;
  if (params.origem) return true;
  if (params.search && params.search.trim().length >= 2) return true;
  return false;
}

export async function listLeads(
  token: string,
  params?: {
    page?: number;
    page_size?: number;
    data_inicio?: string;
    data_fim?: string;
    evento_id?: number;
    search?: string;
    origem?: LeadListOrigin;
    sort_by?: LeadListSortBy;
    sort_dir?: LeadListSortDir;
    long_running?: boolean;
    timeoutMs?: number;
    signal?: AbortSignal;
  },
): Promise<LeadListResponse> {
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.page_size) qs.set("page_size", String(params.page_size));
  if (params?.data_inicio) qs.set("data_inicio", params.data_inicio);
  if (params?.data_fim) qs.set("data_fim", params.data_fim);
  if (typeof params?.evento_id === "number") qs.set("evento_id", String(params.evento_id));
  if (params?.search) qs.set("search", params.search);
  if (params?.origem) qs.set("origem", params.origem);
  if (params?.sort_by) qs.set("sort_by", params.sort_by);
  if (params?.sort_dir) qs.set("sort_dir", params.sort_dir);
  const heavy = leadListUsesHeavyBackendQuery(params);
  if (heavy) qs.set("long_running", "true");
  const url = `/leads${qs.toString() ? `?${qs}` : ""}`;

  const resolvedTimeoutMs =
    typeof params?.timeoutMs === "number"
      ? params.timeoutMs
      : heavy
        ? LEADS_LIST_FILTERED_TIMEOUT_MS
        : undefined;

  const res = await fetchWithAuth(url, {
    token,
    ...(typeof resolvedTimeoutMs === "number" ? { timeoutMs: resolvedTimeoutMs } : {}),
    ...(params?.signal ? { signal: params.signal } : {}),
  });
  return handleApiResponse<LeadListResponse>(res);
}
