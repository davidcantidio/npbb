const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type LeadImportSuggestion = {
  coluna: string;
  campo: string | null;
  confianca: number | null;
};

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

async function parseJsonSafe(text: string) {
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return null;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  const text = await res.text();
  const data = await parseJsonSafe(text);
  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

export async function previewLeadImport(
  token: string,
  file: File,
  sampleRows = 10,
): Promise<LeadImportPreview> {
  const form = new FormData();
  form.append("file", file);
  form.append("sample_rows", String(sampleRows));

  const res = await fetch(`${API_BASE_URL}/leads/import/preview`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return handleResponse<LeadImportPreview>(res);
}

export async function validateLeadMapping(
  token: string,
  mappings: LeadImportSuggestion[],
): Promise<{ ok: boolean }> {
  const res = await fetch(`${API_BASE_URL}/leads/import/validate`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(mappings),
  });
  return handleResponse<{ ok: boolean }>(res);
}

export async function listReferenciaEventos(token: string): Promise<Array<{ id: number; nome: string }>> {
  const res = await fetch(`${API_BASE_URL}/leads/referencias/eventos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<Array<{ id: number; nome: string }>>(res);
}

export async function listReferenciaCidades(token: string): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/leads/referencias/cidades`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<string[]>(res);
}

export async function listReferenciaEstados(token: string): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/leads/referencias/estados`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<string[]>(res);
}

export async function listReferenciaGeneros(token: string): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/leads/referencias/generos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<string[]>(res);
}

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
  const res = await fetch(`${API_BASE_URL}/leads/aliases`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

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

  const res = await fetch(`${API_BASE_URL}/leads/import`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return handleResponse<{ filename: string; created: number; updated: number; skipped: number }>(res);
}
