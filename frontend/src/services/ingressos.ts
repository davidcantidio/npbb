import { API_BASE_URL } from "./http";

type IngressoAtivoListItem = {
  cota_id: number;
  evento_id: number;
  evento_nome: string;
  diretoria_id: number;
  diretoria_nome: string;
  total: number;
  usados: number;
  disponiveis: number;
  data_inicio?: string | null;
  data_fim?: string | null;
};

type SolicitacaoIngressoCreate = {
  cota_id: number;
  tipo: "SELF" | "TERCEIRO";
  indicado_email?: string | null;
};

type SolicitacaoIngressoRead = {
  id: number;
  cota_id: number;
  solicitante_email: string;
  indicado_email: string | null;
  status: string;
  created_at: string;
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

export async function listIngressosAtivos(token: string): Promise<IngressoAtivoListItem[]> {
  const res = await fetch(`${API_BASE_URL}/ingressos/ativos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<IngressoAtivoListItem[]>(res);
}

export async function criarSolicitacaoIngresso(
  token: string,
  payload: SolicitacaoIngressoCreate,
): Promise<SolicitacaoIngressoRead> {
  const res = await fetch(`${API_BASE_URL}/ingressos/solicitacoes`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<SolicitacaoIngressoRead>(res);
}

export type { IngressoAtivoListItem, SolicitacaoIngressoCreate, SolicitacaoIngressoRead };
