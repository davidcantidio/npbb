import { API_BASE_URL } from "./http";

export type Agencia = {
  id: number;
  nome: string;
  dominio: string;
};

export async function listAgencias(params?: { search?: string; skip?: number; limit?: number }) {
  const qs = new URLSearchParams();
  if (params?.search) qs.set("search", params.search);
  if (typeof params?.skip === "number") qs.set("skip", String(params.skip));
  if (typeof params?.limit === "number") qs.set("limit", String(Math.min(params.limit, 200)));
  const url = `${API_BASE_URL}/agencias/${qs.toString() ? `?${qs.toString()}` : ""}`;

  const res = await fetch(url);
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as Agencia[];
}
