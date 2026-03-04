import { API_BASE_URL } from "./http";

export type PublicidadeImportSuggestion = {
  coluna: string;
  campo: string | null;
  confianca: number | null;
};

export type PublicidadeAliasHit = {
  id: number;
  domain: string;
  field_name: string;
  source_value: string;
  source_normalized: string;
  canonical_value?: string | null;
  canonical_ref_id?: number | null;
};

export type PublicidadeImportPreview = {
  filename: string;
  headers: string[];
  rows: string[][];
  delimiter: string | null;
  start_index: number;
  suggestions: PublicidadeImportSuggestion[];
  samples_by_column: string[][];
  alias_hits?: Array<PublicidadeAliasHit | null>;
};

export type PublicidadeImportError = {
  line: number;
  field: string;
  message: string;
  value?: string | null;
};

export type PublicidadeImportReport = {
  filename: string;
  received_rows: number;
  valid_rows: number;
  staged_inserted: number;
  staged_skipped: number;
  upsert_inserted: number;
  upsert_updated: number;
  unresolved_event_id: number;
  errors: PublicidadeImportError[];
};

export type PublicidadeEventReference = {
  id: number;
  nome: string;
  external_project_code?: string | null;
};

export type PublicidadeAliasRead = {
  id: number;
  domain: string;
  field_name: string;
  source_value: string;
  source_normalized: string;
  canonical_value?: string | null;
  canonical_ref_id?: number | null;
  created_at: string;
  updated_at: string;
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

export async function previewPublicidadeImport(
  token: string,
  file: File,
  sampleRows = 10,
): Promise<PublicidadeImportPreview> {
  const form = new FormData();
  form.append("file", file);
  form.append("sample_rows", String(sampleRows));
  const res = await fetch(`${API_BASE_URL}/publicidade/import/preview`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return handleResponse<PublicidadeImportPreview>(res);
}

export async function validatePublicidadeMapping(
  token: string,
  mappings: PublicidadeImportSuggestion[],
): Promise<{ ok: boolean }> {
  const res = await fetch(`${API_BASE_URL}/publicidade/import/validate`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(mappings),
  });
  return handleResponse<{ ok: boolean }>(res);
}

export async function runPublicidadeImport(
  token: string,
  file: File,
  mappings: PublicidadeImportSuggestion[],
  dryRun = false,
): Promise<PublicidadeImportReport> {
  const form = new FormData();
  form.append("file", file);
  form.append("mappings_json", JSON.stringify(mappings));
  form.append("dry_run", String(dryRun));
  const res = await fetch(`${API_BASE_URL}/publicidade/import`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return handleResponse<PublicidadeImportReport>(res);
}

export async function listPublicidadeReferenciaEventos(token: string): Promise<PublicidadeEventReference[]> {
  const res = await fetch(`${API_BASE_URL}/publicidade/referencias/eventos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<PublicidadeEventReference[]>(res);
}

export async function getPublicidadeAlias(
  token: string,
  fieldName: string,
  valorOrigem: string,
): Promise<PublicidadeAliasRead | null> {
  const query = new URLSearchParams({
    field_name: fieldName,
    valor_origem: valorOrigem,
  });
  const res = await fetch(`${API_BASE_URL}/publicidade/aliases?${query.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<PublicidadeAliasRead | null>(res);
}

export async function upsertPublicidadeAlias(
  token: string,
  payload: {
    field_name: string;
    valor_origem: string;
    canonical_value?: string | null;
    canonical_ref_id?: number | null;
  },
): Promise<PublicidadeAliasRead> {
  const res = await fetch(`${API_BASE_URL}/publicidade/aliases`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<PublicidadeAliasRead>(res);
}
