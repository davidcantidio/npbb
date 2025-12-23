const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

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
  agencia_id: number;
  status_id: number;

  created_at: string;
  updated_at: string;
};

export type EventoRead = {
  id: number;
  thumbnail?: string | null;
  divisao_demandante_id?: number | null;
  qr_code_url?: string | null;
  nome: string;
  descricao: string;
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

  agencia_id: number;
  diretoria_id?: number | null;
  gestor_id?: number | null;
  tipo_id: number;
  subtipo_id?: number | null;

  tag_ids: number[];
  territorio_ids: number[];

  status_id: number;

  created_at: string;
  updated_at: string;
};

export type EventoCreate = {
  nome: string;
  descricao: string;
  investimento?: string | number | null;
  concorrencia?: boolean;
  cidade: string;
  estado: string;

  agencia_id?: number;
  diretoria_id?: number;
  gestor_id?: number;

  tipo_id: number;
  subtipo_id?: number;

  tag_ids?: number[];
  territorio_ids?: number[];

  status_id?: number;

  thumbnail?: string | null;
  divisao_demandante_id?: number | null;
  qr_code_url?: string | null;

  data_inicio_prevista?: string | null;
  data_fim_prevista?: string | null;

  publico_projetado?: number | null;
  publico_realizado?: number | null;
};

export type EventoUpdate = Partial<EventoCreate> & {
  tag_ids?: number[] | null;
  territorio_ids?: number[] | null;
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

  const url = `${API_BASE_URL}/evento${qs.toString() ? `?${qs.toString()}` : ""}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  const items = await handleResponse<EventoListItem[]>(res);
  const totalHeader = res.headers.get("X-Total-Count");
  const total = totalHeader ? Number(totalHeader) : null;
  return { items, total: Number.isFinite(total) ? total : null };
}

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

  const url = `${API_BASE_URL}/evento/export/csv${qs.toString() ? `?${qs.toString()}` : ""}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });

  if (!res.ok) {
    const text = await res.text();
    const data = await parseJsonSafe(text);
    const detail = (data as any)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  const blob = await res.blob();
  const filename =
    parseFilenameFromContentDisposition(res.headers.get("content-disposition")) || "eventos.csv";

  return { blob, filename };
}

export async function getEvento(token: string, id: number): Promise<EventoRead> {
  const res = await fetch(`${API_BASE_URL}/evento/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<EventoRead>(res);
}

export async function createEvento(token: string, payload: EventoCreate): Promise<EventoRead> {
  const res = await fetch(`${API_BASE_URL}/evento/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventoRead>(res);
}

export async function updateEvento(
  token: string,
  id: number,
  payload: EventoUpdate,
): Promise<EventoRead> {
  const res = await fetch(`${API_BASE_URL}/evento/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventoRead>(res);
}

export async function deleteEvento(token: string, id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/evento/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (res.status === 204) return;

  const text = await res.text();
  const data = await parseJsonSafe(text);
  const detail = (data as any)?.detail ?? res.statusText;
  throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
}

export async function listTiposEvento(token: string): Promise<TipoEvento[]> {
  const res = await fetch(`${API_BASE_URL}/evento/all/tipos-evento`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<TipoEvento[]>(res);
}

export async function listSubtiposEvento(
  token: string,
  params?: { tipo_id?: number; search?: string },
): Promise<SubtipoEvento[]> {
  const qs = new URLSearchParams();
  if (typeof params?.tipo_id === "number") qs.set("tipo_id", String(params.tipo_id));
  if (params?.search) qs.set("search", params.search);

  const res = await fetch(`${API_BASE_URL}/evento/all/subtipos-evento${qs.toString() ? `?${qs}` : ""}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<SubtipoEvento[]>(res);
}

export async function listTerritorios(token: string, search?: string): Promise<Territorio[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await fetch(`${API_BASE_URL}/evento/all/territorios${qs.toString() ? `?${qs}` : ""}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<Territorio[]>(res);
}

export async function listTags(token: string, search?: string): Promise<Tag[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await fetch(`${API_BASE_URL}/evento/all/tags${qs.toString() ? `?${qs}` : ""}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<Tag[]>(res);
}

export async function createTag(token: string, nome: string): Promise<Tag> {
  const res = await fetch(`${API_BASE_URL}/evento/tags`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ nome }),
  });
  return handleResponse<Tag>(res);
}

export async function listStatusEvento(token: string, search?: string): Promise<StatusEvento[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await fetch(`${API_BASE_URL}/evento/all/status-evento${qs.toString() ? `?${qs}` : ""}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<StatusEvento[]>(res);
}

export type Diretoria = {
  id: number;
  nome: string;
};

export type DivisaoDemandante = {
  id: number;
  nome: string;
};

export async function listDiretorias(token: string, search?: string): Promise<Diretoria[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await fetch(`${API_BASE_URL}/evento/all/diretorias${qs.toString() ? `?${qs}` : ""}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<Diretoria[]>(res);
}

export async function listDivisoesDemandantes(
  token: string,
  search?: string,
): Promise<DivisaoDemandante[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await fetch(
    `${API_BASE_URL}/evento/all/divisoes-demandantes${qs.toString() ? `?${qs}` : ""}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  return handleResponse<DivisaoDemandante[]>(res);
}

export async function listEstados(token: string): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/evento/all/estados`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<string[]>(res);
}

export async function listCidades(token: string, estado?: string): Promise<string[]> {
  const qs = new URLSearchParams();
  if (estado) qs.set("estado", estado);

  const res = await fetch(`${API_BASE_URL}/evento/all/cidades${qs.toString() ? `?${qs}` : ""}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<string[]>(res);
}

export type FormularioTemplate = {
  id: number;
  nome: string;
};

export async function listFormularioTemplates(
  token: string,
  search?: string,
): Promise<FormularioTemplate[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await fetch(
    `${API_BASE_URL}/evento/all/formulario-templates${qs.toString() ? `?${qs}` : ""}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  return handleResponse<FormularioTemplate[]>(res);
}

export type FormularioCampo = {
  nome_campo: string;
  obrigatorio: boolean;
  ordem: number;
};

export type EventoFormConfigUrls = {
  url_landing: string;
  url_promotor: string;
  url_questionario: string;
  url_api: string;
};

export type EventoFormConfig = {
  evento_id: number;
  template_id: number | null;
  campos: FormularioCampo[];
  urls: EventoFormConfigUrls;
};

export async function getEventoFormConfig(token: string, eventoId: number): Promise<EventoFormConfig> {
  const res = await fetch(`${API_BASE_URL}/evento/${eventoId}/form-config`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<EventoFormConfig>(res);
}

export type UpdateEventoFormConfigPayload = {
  template_id?: number | null;
  campos?: FormularioCampo[];
};

export async function updateEventoFormConfig(
  token: string,
  eventoId: number,
  payload: UpdateEventoFormConfigPayload,
): Promise<EventoFormConfig> {
  const res = await fetch(`${API_BASE_URL}/evento/${eventoId}/form-config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventoFormConfig>(res);
}

export async function listFormularioCampos(token: string): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/evento/all/formulario-campos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<string[]>(res);
}

export const FORMULARIO_CAMPOS_POSSIVEIS_FALLBACK = [
  "CPF",
  "Nome",
  "Sobrenome",
  "Telefone",
  "Email",
  "Data de nascimento",
  "Endereco",
  "Interesses",
  "Genero",
  "Area de atuacao",
] as const;

export async function getFormularioCamposPossiveis(token: string): Promise<string[]> {
  try {
    return await listFormularioCampos(token);
  } catch {
    return [...FORMULARIO_CAMPOS_POSSIVEIS_FALLBACK];
  }
}

export type Gamificacao = {
  id: number;
  evento_id: number;
  nome: string;
  descricao: string;
  premio: string;
  titulo_feedback: string;
  texto_feedback: string;
};

export type CreateEventoGamificacaoPayload = {
  nome: string;
  descricao: string;
  premio: string;
  titulo_feedback: string;
  texto_feedback: string;
};

export type UpdateGamificacaoPayload = {
  nome?: string;
  descricao?: string;
  premio?: string;
  titulo_feedback?: string;
  texto_feedback?: string;
};

export async function listEventoGamificacoes(token: string, eventoId: number): Promise<Gamificacao[]> {
  const res = await fetch(`${API_BASE_URL}/evento/${eventoId}/gamificacoes`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<Gamificacao[]>(res);
}

export async function createEventoGamificacao(
  token: string,
  eventoId: number,
  payload: CreateEventoGamificacaoPayload,
): Promise<Gamificacao> {
  const res = await fetch(`${API_BASE_URL}/evento/${eventoId}/gamificacoes`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  return handleResponse<Gamificacao>(res);
}

export async function updateGamificacao(
  token: string,
  gamificacaoId: number,
  payload: UpdateGamificacaoPayload,
): Promise<Gamificacao> {
  const res = await fetch(`${API_BASE_URL}/gamificacao/${gamificacaoId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  return handleResponse<Gamificacao>(res);
}

export async function deleteGamificacao(token: string, gamificacaoId: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/gamificacao/${gamificacaoId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 204) return;
  await handleResponse<unknown>(res);
}
