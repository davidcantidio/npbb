import { listLeads, type LeadListItem } from "../../services/leads_import";

/** Max supported by GET /leads (backend LeadListQuery.page_size le=100). */
export const LEADS_EXPORT_PAGE_SIZE = 100;

export type AppliedLeadsListFilters = {
  data_inicio: string;
  data_fim: string;
  evento_id: number | null;
};

/** Cabecalhos iguais ao arquivo data 2.csv (pivot). */
export const LEADS_LIST_CSV_HEADERS = [
  "evento",
  "data_evento",
  "Soma de ano_evento",
  "cliente",
  "cod_sexo",
  "cpf",
  "data_nascimento",
  "faixa_etaria",
  "Soma de idade",
  "local",
  "tipo_evento",
] as const;

function formatDateTime(iso: string | null | undefined) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

/** Mesmos valores visiveis da tabela (6 colunas). */
export function getLeadListDisplayCells(row: LeadListItem): [string, string, string, string, string, string] {
  return [
    row.nome ?? "—",
    row.email ?? "—",
    formatDateTime(row.data_criacao),
    row.evento_convertido_nome ?? "—",
    row.evento_nome ?? "—",
    [row.cidade, row.estado].filter(Boolean).join(" / ") || "—",
  ];
}

/** Data no formato do pivot: YYYY-MM-DD 00:00:00 */
function formatDataPivot(isoDate: string | null | undefined): string {
  if (!isoDate) return "";
  const slice = isoDate.slice(0, 10);
  if (/^\d{4}-\d{2}-\d{2}$/.test(slice)) return `${slice} 00:00:00`;
  return isoDate;
}

/** Local como no data 2.csv: "Cidade – UF" (travessao en). */
function formatLocalPivot(cidade: string | null | undefined, estado: string | null | undefined): string {
  const c = cidade?.trim();
  const e = estado?.trim();
  if (!c && !e) return "";
  if (c && e) return `${c} \u2013 ${e}`;
  return c ?? e ?? "";
}

function clienteCell(isClienteBb: boolean | null | undefined): string {
  if (isClienteBb === null || isClienteBb === undefined) return "";
  return String(isClienteBb);
}

/** Linha CSV alinhada a data 2.csv. */
export function getLeadListCsvCells(row: LeadListItem): readonly string[] {
  return [
    row.evento_convertido_nome ?? "",
    row.data_evento ?? "",
    row.soma_de_ano_evento != null ? String(row.soma_de_ano_evento) : "",
    clienteCell(row.is_cliente_bb ?? null),
    row.genero ?? "",
    row.cpf ?? "",
    formatDataPivot(row.data_nascimento ?? null),
    row.faixa_etaria ?? "",
    row.soma_de_idade != null ? String(row.soma_de_idade) : "",
    formatLocalPivot(row.cidade, row.estado),
    row.tipo_evento ?? "",
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

function listParamsForExport(page: number, appliedFilters: AppliedLeadsListFilters) {
  return {
    page,
    page_size: LEADS_EXPORT_PAGE_SIZE,
    ...(appliedFilters.data_inicio ? { data_inicio: appliedFilters.data_inicio } : {}),
    ...(appliedFilters.data_fim ? { data_fim: appliedFilters.data_fim } : {}),
    ...(typeof appliedFilters.evento_id === "number" ? { evento_id: appliedFilters.evento_id } : {}),
  };
}

/**
 * Loads every lead row matching the same filters as the list UI, using API pagination.
 */
export async function fetchAllLeadsMatchingFilters(
  token: string,
  appliedFilters: AppliedLeadsListFilters,
): Promise<LeadListItem[]> {
  const first = await listLeads(token, listParamsForExport(1, appliedFilters));
  const all: LeadListItem[] = [...first.items];
  let page = 2;
  while (all.length < first.total) {
    const res = await listLeads(token, listParamsForExport(page, appliedFilters));
    if (res.items.length === 0) break;
    all.push(...res.items);
    page += 1;
  }
  return all;
}

/** Local calendar YYYY-MM-DD for default export filename. */
export function leadsExportCsvFilename(date = new Date()): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `leads-${y}-${m}-${d}.csv`;
}
