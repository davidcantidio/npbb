import { API_BASE_URL, fetchWithAuth, handleApiResponse } from "./http";

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

/**
 * Lead representation used in frontend listing tables.
 */
export type LeadListItem = {
  id: number;
  nome: string | null;
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

  const res = await fetchWithAuth(`${API_BASE_URL}/leads/import/preview`, {
    method: "POST",
    token,
    body: form,
    timeoutMs: 60_000,
    retries: 0,
  });
  return handleApiResponse<LeadImportPreview>(res);
}

/**
 * Validates selected mappings before import execution.
 * @param token Bearer token used for authorization.
 * @param mappings Mapping suggestions confirmed by the user.
 * @returns Validation result from backend.
 * @throws Error When mappings are invalid or request fails.
 */
export async function validateLeadMapping(
  token: string,
  mappings: LeadImportSuggestion[],
): Promise<{ ok: boolean }> {
  const res = await fetchWithAuth(`${API_BASE_URL}/leads/import/validate`, {
    method: "POST",
    token,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(mappings),
    retries: 0,
  });
  return handleApiResponse<{ ok: boolean }>(res);
}

/**
 * Lists reference events available for mapping helpers.
 * @param token Bearer token used for authorization.
 * @returns Event reference options.
 * @throws Error When request fails.
 */
export async function listReferenciaEventos(token: string): Promise<Array<{ id: number; nome: string }>> {
  const res = await fetchWithAuth(`${API_BASE_URL}/leads/referencias/eventos`, { token });
  return handleApiResponse<Array<{ id: number; nome: string }>>(res);
}

/**
 * Lists reference cities available for mapping helpers.
 * @param token Bearer token used for authorization.
 * @returns City reference values.
 * @throws Error When request fails.
 */
export async function listReferenciaCidades(token: string): Promise<string[]> {
  const res = await fetchWithAuth(`${API_BASE_URL}/leads/referencias/cidades`, { token });
  return handleApiResponse<string[]>(res);
}

/**
 * Lists reference states (UF) available for mapping helpers.
 * @param token Bearer token used for authorization.
 * @returns State reference values.
 * @throws Error When request fails.
 */
export async function listReferenciaEstados(token: string): Promise<string[]> {
  const res = await fetchWithAuth(`${API_BASE_URL}/leads/referencias/estados`, { token });
  return handleApiResponse<string[]>(res);
}

/**
 * Lists reference genders available for mapping helpers.
 * @param token Bearer token used for authorization.
 * @returns Gender reference values.
 * @throws Error When request fails.
 */
export async function listReferenciaGeneros(token: string): Promise<string[]> {
  const res = await fetchWithAuth(`${API_BASE_URL}/leads/referencias/generos`, { token });
  return handleApiResponse<string[]>(res);
}

/**
 * Persists an alias confirmed during mapping review.
 * @param token Bearer token used for authorization.
 * @param payload Alias payload to persist.
 * @returns Persisted alias entity from backend.
 * @throws Error When request fails.
 */
export async function createLeadAlias(
  token: string,
  payload: { tipo: string; valor_origem: string; canonical_value?: string | null; evento_id?: number | null },
): Promise<{
  id: number;
  tipo: string;
  valor_origem: string;
  valor_normalizado: string;
  canonical_value?: string | null;
  evento_id?: number | null;
}> {
  const res = await fetchWithAuth(`${API_BASE_URL}/leads/aliases`, {
    method: "POST",
    token,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    retries: 0,
  });
  return handleApiResponse(res);
}

/**
 * Executes assisted lead import with confirmed mappings.
 * @param token Bearer token used for authorization.
 * @param file Source CSV/XLSX file to import.
 * @param mappings Mapping definitions validated by user.
 * @param fonte_origem Optional source label associated to imported leads.
 * @returns Import summary with created/updated/skipped counters.
 * @throws Error When import request fails.
 */
export async function runLeadImport(
  token: string,
  file: File,
  mappings: LeadImportSuggestion[],
  fonte_origem?: string,
): Promise<{ filename: string; created: number; updated: number; skipped: number }> {
  const form = new FormData();
  form.append("file", file);
  form.append("mappings_json", JSON.stringify(mappings));
  if (fonte_origem) form.append("fonte_origem", fonte_origem);

  const res = await fetchWithAuth(`${API_BASE_URL}/leads/import`, {
    method: "POST",
    token,
    body: form,
    timeoutMs: 60_000,
    retries: 0,
  });
  return handleApiResponse<{ filename: string; created: number; updated: number; skipped: number }>(res);
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
  params?: { page?: number; page_size?: number },
): Promise<LeadListResponse> {
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.page_size) qs.set("page_size", String(params.page_size));
  const url = `${API_BASE_URL}/leads${qs.toString() ? `?${qs}` : ""}`;

  const res = await fetchWithAuth(url, { token });
  return handleApiResponse<LeadListResponse>(res);
}
