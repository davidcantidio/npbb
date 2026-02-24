import {
  EVENTOS_API_BASE_URL,
  handleDeleteResponse,
  handleResponse,
  parseJsonSafe,
  requestWithAuth,
} from "./http";

export type EventoListItem = {
  id: number;
  qr_code_url?: string | null;
  nome: string;
  investimento?: string | number | null;
  data_inicio_prevista?: string | null;
  data_fim_prevista?: string | null;
  data_inicio_realizada?: string | null;
  data_fim_realizada?: string | null;
  cidade: string;
  estado: string;
  diretoria_id?: number | null;
  agencia_id?: number | null;
  status_id: number;
  data_health?: DataHealth | null;
  created_at: string;
  updated_at: string;
};

export type DataHealth = {
  version: number;
  score: number | null;
  band: string;
  missing_fields: string[];
  filled_weight: number;
  total_weight: number;
  urgency_factor: number;
  last_calculated_at: string;
};

export type EventoRead = {
  id: number;
  thumbnail?: string | null;
  divisao_demandante_id?: number | null;
  qr_code_url?: string | null;
  nome: string;
  descricao?: string | null;
  investimento?: string | number | null;
  data_inicio_prevista?: string | null;
  data_fim_prevista?: string | null;
  data_inicio_realizada?: string | null;
  data_fim_realizada?: string | null;
  publico_projetado?: number | null;
  publico_realizado?: number | null;
  concorrencia: boolean;
  cidade: string;
  estado: string;
  agencia_id?: number | null;
  diretoria_id?: number | null;
  gestor_id?: number | null;
  tipo_id?: number | null;
  subtipo_id?: number | null;
  tag_ids: number[];
  territorio_ids: number[];
  status_id: number;
  created_at: string;
  updated_at: string;
};

export type EventoCreate = {
  nome: string;
  descricao?: string | null;
  investimento?: string | number | null;
  concorrencia?: boolean;
  cidade: string;
  estado: string;
  agencia_id?: number;
  diretoria_id?: number;
  gestor_id?: number;
  tipo_id?: number;
  subtipo_id?: number;
  tag_ids?: number[];
  territorio_ids?: number[];
  status_id?: number;
  thumbnail?: string | null;
  divisao_demandante_id?: number | null;
  qr_code_url?: string | null;
  data_inicio_prevista: string;
  data_fim_prevista?: string | null;
  data_inicio_realizada?: string | null;
  data_fim_realizada?: string | null;
  publico_projetado?: number | null;
  publico_realizado?: number | null;
};

export type EventoUpdate = Partial<EventoCreate> & {
  tag_ids?: number[] | null;
  territorio_ids?: number[] | null;
};

export type ImportEventosCsvError = {
  line: number;
  field: string;
  message: string;
  value?: string | null;
};

export type ImportEventosCsvResult = {
  total: number;
  success: number;
  failed: number;
  errors: ImportEventosCsvError[];
};

export type TipoEvento = {
  id: number;
  nome: string;
};

export type SubtipoEvento = {
  id: number;
  tipo_id: number;
  nome: string;
};

export type Territorio = {
  id: number;
  nome: string;
};

export type Tag = {
  id: number;
  nome: string;
};

export type StatusEvento = {
  id: number;
  nome: string;
};

export type Diretoria = {
  id: number;
  nome: string;
};

export type DivisaoDemandante = {
  id: number;
  nome: string;
};

function parseFilenameFromContentDisposition(value: string | null): string | null {
  if (!value) return null;
  const matchStar = value.match(/filename\*\s*=\s*UTF-8''([^;]+)/i);
  if (matchStar?.[1]) {
    try {
      return decodeURIComponent(matchStar[1].replace(/(^\"|\"$)/g, ""));
    } catch {
      return matchStar[1].replace(/(^\"|\"$)/g, "");
    }
  }

  const match = value.match(/filename\s*=\s*\"?([^\";]+)\"?/i);
  return match?.[1] ?? null;
}

/**
 * Lists eventos using filters and pagination.
 * @param token Auth token.
 * @param params Optional query filters.
 * @returns Event items plus optional total from response headers.
 */
export async function listEventos(
  token: string,
  params?: {
    skip?: number;
    limit?: number;
    search?: string;
    estado?: string;
    cidade?: string;
    data?: string;
    data_inicio?: string;
    data_fim?: string;
    diretoria_id?: number;
  },
): Promise<{ items: EventoListItem[]; total: number | null }> {
  const qs = new URLSearchParams();
  if (typeof params?.skip === "number") qs.set("skip", String(params.skip));
  if (typeof params?.limit === "number") qs.set("limit", String(params.limit));
  if (params?.search) qs.set("search", params.search);
  if (params?.estado) qs.set("estado", params.estado);
  if (params?.cidade) qs.set("cidade", params.cidade);
  if (params?.data) qs.set("data", params.data);
  if (params?.data_inicio) qs.set("data_inicio", params.data_inicio);
  if (params?.data_fim) qs.set("data_fim", params.data_fim);
  if (typeof params?.diretoria_id === "number") qs.set("diretoria_id", String(params.diretoria_id));

  const path = `/evento${qs.toString() ? `?${qs.toString()}` : ""}`;
  const res = await requestWithAuth(path, { token });
  const items = await handleResponse<EventoListItem[]>(res);
  const totalHeader = res.headers.get("X-Total-Count");
  const total = totalHeader ? Number(totalHeader) : null;
  return { items, total: Number.isFinite(total) ? total : null };
}

/**
 * Exports eventos as CSV for the provided filters.
 * @param token Auth token.
 * @param params Optional query filters.
 * @returns CSV blob and filename.
 * @throws Error when export fails.
 */
export async function exportEventosCsv(
  token: string,
  params?: {
    skip?: number;
    limit?: number;
    search?: string;
    estado?: string;
    cidade?: string;
    data?: string;
    data_inicio?: string;
    data_fim?: string;
    diretoria_id?: number;
  },
): Promise<{ blob: Blob; filename: string }> {
  const qs = new URLSearchParams();
  if (typeof params?.skip === "number") qs.set("skip", String(params.skip));
  if (typeof params?.limit === "number") qs.set("limit", String(params.limit));
  if (params?.search) qs.set("search", params.search);
  if (params?.estado) qs.set("estado", params.estado);
  if (params?.cidade) qs.set("cidade", params.cidade);
  if (params?.data) qs.set("data", params.data);
  if (params?.data_inicio) qs.set("data_inicio", params.data_inicio);
  if (params?.data_fim) qs.set("data_fim", params.data_fim);
  if (typeof params?.diretoria_id === "number") qs.set("diretoria_id", String(params.diretoria_id));

  const res = await requestWithAuth(`/evento/export/csv${qs.toString() ? `?${qs.toString()}` : ""}`, {
    token,
  });

  if (!res.ok) {
    const text = await res.text();
    const data = await parseJsonSafe(text);
    const detail = (data as { detail?: unknown } | null)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  const blob = await res.blob();
  const filename =
    parseFilenameFromContentDisposition(res.headers.get("content-disposition")) || "eventos.csv";

  return { blob, filename };
}

/**
 * Imports a CSV file of eventos.
 * @param token Auth token.
 * @param file CSV file.
 * @returns Import summary from backend.
 */
export async function importEventosCsv(token: string, file: File): Promise<ImportEventosCsvResult> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await requestWithAuth("/evento/import/csv", {
    token,
    method: "POST",
    body: formData,
  });
  return handleResponse<ImportEventosCsvResult>(res);
}

/**
 * Fetches full evento details by id.
 * @param token Auth token.
 * @param id Event id.
 * @returns Evento details.
 */
export async function getEvento(token: string, id: number): Promise<EventoRead> {
  const res = await requestWithAuth(`/evento/${id}`, { token });
  return handleResponse<EventoRead>(res);
}

/**
 * Creates an evento.
 * @param token Auth token.
 * @param payload Event creation payload.
 * @returns Created evento.
 */
export async function createEvento(token: string, payload: EventoCreate): Promise<EventoRead> {
  const res = await requestWithAuth("/evento/", {
    token,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventoRead>(res);
}

/**
 * Updates an existing evento.
 * @param token Auth token.
 * @param id Event id.
 * @param payload Partial update payload.
 * @returns Updated evento.
 */
export async function updateEvento(
  token: string,
  id: number,
  payload: EventoUpdate,
): Promise<EventoRead> {
  const res = await requestWithAuth(`/evento/${id}`, {
    token,
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventoRead>(res);
}

/**
 * Deletes an evento by id.
 * @param token Auth token.
 * @param id Event id.
 */
export async function deleteEvento(token: string, id: number): Promise<void> {
  const res = await requestWithAuth(`/evento/${id}`, {
    token,
    method: "DELETE",
  });
  await handleDeleteResponse(res);
}

/**
 * Lists available tipos de evento.
 * @param token Auth token.
 * @returns Tipo list.
 */
export async function listTiposEvento(token: string): Promise<TipoEvento[]> {
  const res = await requestWithAuth("/evento/all/tipos-evento", { token });
  return handleResponse<TipoEvento[]>(res);
}

/**
 * Lists subtipos optionally filtered by tipo.
 * @param token Auth token.
 * @param params Optional subtype filters.
 * @returns Subtipo list.
 */
export async function listSubtiposEvento(
  token: string,
  params?: { tipo_id?: number; search?: string },
): Promise<SubtipoEvento[]> {
  const qs = new URLSearchParams();
  if (typeof params?.tipo_id === "number") qs.set("tipo_id", String(params.tipo_id));
  if (params?.search) qs.set("search", params.search);

  const res = await requestWithAuth(`/evento/all/subtipos-evento${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<SubtipoEvento[]>(res);
}

/**
 * Lists territorios with optional search.
 * @param token Auth token.
 * @param search Optional search query.
 * @returns Territorio list.
 */
export async function listTerritorios(token: string, search?: string): Promise<Territorio[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await requestWithAuth(`/evento/all/territorios${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<Territorio[]>(res);
}

/**
 * Lists tags with optional search.
 * @param token Auth token.
 * @param search Optional search query.
 * @returns Tag list.
 */
export async function listTags(token: string, search?: string): Promise<Tag[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await requestWithAuth(`/evento/all/tags${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<Tag[]>(res);
}

/**
 * Creates a new tag.
 * @param token Auth token.
 * @param nome Tag name.
 * @returns Created tag.
 */
export async function createTag(token: string, nome: string): Promise<Tag> {
  const res = await requestWithAuth("/evento/tags", {
    token,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome }),
  });
  return handleResponse<Tag>(res);
}

/**
 * Lists status de evento with optional search.
 * @param token Auth token.
 * @param search Optional search query.
 * @returns Status list.
 */
export async function listStatusEvento(token: string, search?: string): Promise<StatusEvento[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await requestWithAuth(`/evento/all/status-evento${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<StatusEvento[]>(res);
}

/**
 * Lists diretorias with optional search.
 * @param token Auth token.
 * @param search Optional search query.
 * @returns Diretoria list.
 */
export async function listDiretorias(token: string, search?: string): Promise<Diretoria[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await requestWithAuth(`/evento/all/diretorias${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<Diretoria[]>(res);
}

/**
 * Lists divisoes demandantes with optional search.
 * @param token Auth token.
 * @param search Optional search query.
 * @returns Divisoes list.
 */
export async function listDivisoesDemandantes(
  token: string,
  search?: string,
): Promise<DivisaoDemandante[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await requestWithAuth(
    `/evento/all/divisoes-demandantes${qs.toString() ? `?${qs}` : ""}`,
    { token },
  );
  return handleResponse<DivisaoDemandante[]>(res);
}

/**
 * Lists available UFs for eventos.
 * @param token Auth token.
 * @returns UF list.
 */
export async function listEstados(token: string): Promise<string[]> {
  const res = await requestWithAuth("/evento/all/estados", { token });
  return handleResponse<string[]>(res);
}

/**
 * Lists cidades optionally filtered by UF.
 * @param token Auth token.
 * @param estado Optional UF filter.
 * @returns Cidade list.
 */
export async function listCidades(token: string, estado?: string): Promise<string[]> {
  const qs = new URLSearchParams();
  if (estado) qs.set("estado", estado);

  const res = await requestWithAuth(`/evento/all/cidades${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<string[]>(res);
}

export { EVENTOS_API_BASE_URL };

