import type { LeadListItem } from "../../../services/leads_import";

export type AppliedLeadsListFilters = {
  search: string;
  data_inicio: string;
  data_fim: string;
  evento_id: number | null;
  origem: "proponente" | "ativacao" | null;
};

/** Cabecalhos identicos ao arquivo aurea_tour_2025_hevert(in).csv. */
export const LEADS_LIST_CSV_HEADERS = [
  "nome",
  "cpf",
  "data_nascimento",
  "email",
  "telefone",
  "origem",
  "evento",
  "local",
  "data_evento",
] as const;

/**
 * Contract for `/leads` CSV export:
 * - Export the same dataset rendered by the list page.
 * - The CSV contract matches `aurea_tour_2025_hevert(in).csv`.
 * - `evento` prefers the latest conversion event and falls back to the lead origin event.
 * - `local` and `data_evento` prefer the latest conversion event and fall back to the origin event.
 */
export function resolveLeadListExportEvent(row: LeadListItem): string {
  return row.evento_convertido_nome ?? row.evento_nome ?? "";
}

function formatDateTime(iso: string | null | undefined) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

/** Data ISO YYYY-MM-DD em pt-BR (sem deslocar por fuso). */
function formatIsoDatePt(ymd: string | null | undefined): string {
  if (!ymd?.trim()) return "—";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd.trim());
  if (!m) return ymd;
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function formatEventPeriod(inicio: string | null | undefined, fim: string | null | undefined): string {
  const hasIni = Boolean(inicio?.trim());
  const hasFim = Boolean(fim?.trim());
  if (!hasIni && !hasFim) return "—";
  if (hasIni && hasFim) return `${formatIsoDatePt(inicio)} – ${formatIsoDatePt(fim)}`;
  if (hasIni) return formatIsoDatePt(inicio);
  return formatIsoDatePt(fim);
}

/** Mesmos valores visiveis da tabela (8 colunas). */
export function getLeadListDisplayCells(row: LeadListItem): [
  string,
  string,
  string,
  string,
  string,
  string,
  string,
  string,
] {
  return [
    row.nome ?? "—",
    row.email ?? "—",
    formatDateTime(row.data_criacao),
    row.origem?.trim() ? row.origem : "—",
    formatEventPeriod(row.evento_inicio_prevista ?? null, row.evento_fim_prevista ?? null),
    row.evento_convertido_nome ?? "—",
    row.evento_nome ?? "—",
    [row.cidade, row.estado].filter(Boolean).join(" / ") || "—",
  ];
}

/** Datas no formato do arquivo de referencia: M/D/YYYY. */
function formatReferenceDate(isoDate: string | null | undefined): string {
  if (!isoDate) return "";
  const normalized = /^\d{4}-\d{2}-\d{2}$/.test(isoDate) ? `${isoDate}T00:00:00Z` : isoDate;
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return isoDate;
  return date.toLocaleDateString("en-US", { timeZone: "UTC" });
}

/** Linha CSV alinhada a aurea_tour_2025_hevert(in).csv. */
export function getLeadListCsvCells(row: LeadListItem): readonly string[] {
  return [
    row.nome ?? "",
    row.cpf ?? "",
    formatReferenceDate(row.data_nascimento ?? null),
    row.email ?? "",
    row.telefone ?? "",
    row.origem ?? "",
    resolveLeadListExportEvent(row),
    row.local_evento ?? "",
    formatReferenceDate(row.data_evento ?? null),
  ];
}

function escapeCsvField(value: string): string {
  if (/[",\r\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

export function buildLeadsListCsvContent(items: LeadListItem[]): string {
  const headerLine = LEADS_LIST_CSV_HEADERS.map((h) => escapeCsvField(h)).join(",");
  const dataLines = items.map((row) =>
    getLeadListCsvCells(row).map((cell) => escapeCsvField(cell)).join(","),
  );
  return `\uFEFF${[headerLine, ...dataLines].join("\r\n")}`;
}

/** Local calendar YYYY-MM-DD for default export filename. */
export function leadsExportCsvFilename(date = new Date()): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `leads-${y}-${m}-${d}.csv`;
}
