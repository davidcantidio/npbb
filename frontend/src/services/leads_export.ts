/**
 * Frontend service for exporting Gold-stage leads.
 *
 * Responsibilities:
 * - Call GET /leads/export/gold with optional evento_id and formato params.
 * - Return the Blob on success or null on HTTP 204 (no leads found).
 * - Extract the server-provided filename from Content-Disposition header.
 * - Trigger a browser download via a temporary <a> element.
 */

import { API_BASE_URL } from "./http";

export type ExportGoldParams = {
  evento_id?: number | null;
  formato?: "xlsx" | "csv";
};

/**
 * Calls the Gold export endpoint.
 *
 * @returns `{ blob, filename }` when leads exist, or `null` when HTTP 204.
 * @throws Error on non-200/204 responses.
 */
export async function exportLeadsGold(
  token: string,
  params: ExportGoldParams = {},
): Promise<{ blob: Blob; filename: string } | null> {
  const qs = new URLSearchParams();
  if (params.evento_id != null) qs.set("evento_id", String(params.evento_id));
  if (params.formato) qs.set("formato", params.formato);

  const url = `${API_BASE_URL}/leads/export/gold${qs.toString() ? `?${qs}` : ""}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (res.status === 204) return null;

  if (!res.ok) {
    let detail = "Erro ao exportar leads.";
    try {
      const json = await res.json();
      detail = json?.detail ?? detail;
    } catch {
      // ignore parse error
    }
    throw new Error(detail);
  }

  const blob = await res.blob();
  const filename = extractFilename(res.headers.get("content-disposition"), params.formato ?? "xlsx");
  return { blob, filename };
}

/**
 * Extracts the filename from a Content-Disposition header value.
 * Falls back to a generated name if the header is absent or unparseable.
 */
export function extractFilename(
  contentDisposition: string | null,
  formato: "xlsx" | "csv",
): string {
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^";\s]+)"?/i);
    if (match?.[1]) return match[1];
  }
  const today = new Date().toISOString().slice(0, 10);
  return `leads_ouro_todos_${today}.${formato}`;
}

/**
 * Triggers a browser file download using a temporary <a> element.
 * Creates and immediately removes the element from the DOM.
 */
export function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
