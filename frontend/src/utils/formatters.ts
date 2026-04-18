/**
 * Formats a date string (ISO YYYY-MM-DD or ISO datetime) to Brazilian DD/MM/YYYY format.
 * Returns empty string if the value is null, undefined, or unparseable.
 */
export function formatDateBR(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return "";
  const day = String(d.getUTCDate()).padStart(2, "0");
  const month = String(d.getUTCMonth() + 1).padStart(2, "0");
  const year = d.getUTCFullYear();
  return `${day}/${month}/${year}`;
}

/**
 * Builds a display label for an evento option in a dropdown.
 * If data_inicio_prevista is present, returns "Nome — DD/MM/YYYY".
 * Otherwise returns just the name.
 */
export function formatEventoLabel(nome: string, data_inicio_prevista: string | null | undefined): string {
  const dateFmt = formatDateBR(data_inicio_prevista);
  return dateFmt ? `${nome} — ${dateFmt}` : nome;
}

/** Opção sintética “+ Criar evento rapidamente” nos Autocompletes de importação/mapeamento. */
const REFERENCIA_EVENTO_QUICK_CREATE_ID = -1;

export type ReferenciaEventoOptionLike = {
  id: number;
  nome: string;
  data_inicio_prevista?: string | null;
  leads_count?: number | null;
};

/**
 * Rótulo para opções de evento na importação: nome/data e, quando disponível, contagem de leads (lead_evento).
 */
export function formatReferenciaEventoOptionLabel(evento: ReferenciaEventoOptionLike): string {
  if (evento.id === REFERENCIA_EVENTO_QUICK_CREATE_ID) {
    return evento.nome;
  }
  const base = formatEventoLabel(evento.nome, evento.data_inicio_prevista);
  const n = evento.leads_count;
  if (typeof n !== "number" || !Number.isFinite(n) || n < 0) {
    return base;
  }
  const suffix = n === 1 ? "1 lead" : `${n} leads`;
  return `${base} — ${suffix}`;
}
