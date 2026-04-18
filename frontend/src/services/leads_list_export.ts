import { fetchWithAuth } from "./http";

export const LEADS_LIST_EXPORT_TIMEOUT_MS = 15 * 60_000;

export type LeadsListExportParams = {
  data_inicio?: string;
  data_fim?: string;
  evento_id?: number | null;
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

function extractErrorMessage(text: string, fallback: string): string {
  if (!text) return fallback;
  try {
    const data = JSON.parse(text) as { detail?: unknown } | null;
    const detail = data?.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object" && !Array.isArray(detail)) {
      const message = (detail as { message?: unknown }).message;
      if (typeof message === "string" && message.trim()) return message;
    }
  } catch {
    // fall back to raw text
  }
  return text.trim() || fallback;
}

export async function exportLeadsListCsv(
  token: string,
  params: LeadsListExportParams = {},
): Promise<{ blob: Blob; filename: string } | null> {
  const qs = new URLSearchParams();
  if (params.data_inicio) qs.set("data_inicio", params.data_inicio);
  if (params.data_fim) qs.set("data_fim", params.data_fim);
  if (typeof params.evento_id === "number") qs.set("evento_id", String(params.evento_id));

  const res = await fetchWithAuth(`/leads/export/csv${qs.toString() ? `?${qs.toString()}` : ""}`, {
    token,
    timeoutMs: LEADS_LIST_EXPORT_TIMEOUT_MS,
  });

  if (res.status === 204) return null;

  if (!res.ok) {
    const text = await res.text();
    throw new Error(extractErrorMessage(text, "Nao foi possivel exportar os leads."));
  }

  const blob = await res.blob();
  const filename =
    parseFilenameFromContentDisposition(res.headers.get("content-disposition")) ||
    `leads-${new Date().toISOString().slice(0, 10)}.csv`;

  return { blob, filename };
}
