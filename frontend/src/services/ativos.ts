import { API_BASE_URL } from "./http";

export type AtivoListItem = {
  id: number;
  evento_id: number;
  evento_nome: string;
  diretoria_id: number;
  diretoria_nome: string;
  total: number;
  usados: number;
  disponiveis: number;
  percentual_usado: number;
  data_inicio?: string | null;
  data_fim?: string | null;
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

export async function listAtivos(
  token: string,
  params?: {
    skip?: number;
    limit?: number;
    evento_id?: number;
    diretoria_id?: number;
    data?: string;
  },
): Promise<{ items: AtivoListItem[]; total: number | null }> {
  const qs = new URLSearchParams();
  if (typeof params?.skip === "number") qs.set("skip", String(params.skip));
  if (typeof params?.limit === "number") qs.set("limit", String(params.limit));
  if (typeof params?.evento_id === "number") qs.set("evento_id", String(params.evento_id));
  if (typeof params?.diretoria_id === "number") qs.set("diretoria_id", String(params.diretoria_id));
  if (params?.data) qs.set("data", params.data);

  const url = `${API_BASE_URL}/ativos${qs.toString() ? `?${qs.toString()}` : ""}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  const items = await handleResponse<AtivoListItem[]>(res);
  const totalHeader = res.headers.get("X-Total-Count");
  const total = totalHeader ? Number(totalHeader) : null;
  return { items, total: Number.isFinite(total) ? total : null };
}

export async function atribuirCota(
  token: string,
  payload: { evento_id: number; diretoria_id: number; quantidade: number },
): Promise<AtivoListItem> {
  const res = await fetch(
    `${API_BASE_URL}/ativos/${payload.evento_id}/${payload.diretoria_id}/atribuir`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ quantidade: payload.quantidade }),
    },
  );
  return handleResponse<AtivoListItem>(res);
}

export async function deleteAtivo(token: string, cotaId: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/ativos/${cotaId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (res.status === 204) return;

  const text = await res.text();
  const data = await parseJsonSafe(text);
  const detail = (data as any)?.detail ?? res.statusText;
  throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
}

export async function exportAtivosCsv(
  token: string,
  params?: {
    evento_id?: number;
    diretoria_id?: number;
    data?: string;
  },
): Promise<{ blob: Blob; filename: string }> {
  const qs = new URLSearchParams();
  if (typeof params?.evento_id === "number") qs.set("evento_id", String(params.evento_id));
  if (typeof params?.diretoria_id === "number") qs.set("diretoria_id", String(params.diretoria_id));
  if (params?.data) qs.set("data", params.data);

  const url = `${API_BASE_URL}/ativos/export/csv${qs.toString() ? `?${qs.toString()}` : ""}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });

  if (!res.ok) {
    const text = await res.text();
    const data = await parseJsonSafe(text);
    const detail = (data as any)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  const blob = await res.blob();
  const filename =
    parseFilenameFromContentDisposition(res.headers.get("content-disposition")) || "ativos.csv";

  return { blob, filename };
}
