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
