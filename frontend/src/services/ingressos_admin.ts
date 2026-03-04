import { API_BASE_URL } from "./http";

type SolicitacaoIngressoAdminListItem = {
  id: number;
  evento_id: number;
  evento_nome: string;
  diretoria_id: number;
  diretoria_nome: string;
  solicitante_email: string;
  indicado_email: string | null;
  tipo: "SELF" | "TERCEIRO";
  status: "SOLICITADO" | "CANCELADO";
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

export async function listSolicitacoesIngressos(
  token: string,
  params?: {
    evento_id?: number;
    diretoria_id?: number;
    status?: "SOLICITADO" | "CANCELADO";
    data?: string;
  },
): Promise<SolicitacaoIngressoAdminListItem[]> {
  const qs = new URLSearchParams();
  if (typeof params?.evento_id === "number") qs.set("evento_id", String(params.evento_id));
  if (typeof params?.diretoria_id === "number") qs.set("diretoria_id", String(params.diretoria_id));
  if (params?.status) qs.set("status", params.status);
  if (params?.data) qs.set("data", params.data);

  const url = `${API_BASE_URL}/ingressos/solicitacoes${qs.toString() ? `?${qs}` : ""}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  return handleResponse<SolicitacaoIngressoAdminListItem[]>(res);
}

export type { SolicitacaoIngressoAdminListItem };
