import type { LandingField } from "../../services/landing_public";

export function formatDateRange(start?: string | null, end?: string | null) {
  const formatter = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
  const parseDate = (value?: string | null) => {
    if (!value?.trim()) return null;
    const normalized = value.trim();
    const localDateMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(normalized);
    if (localDateMatch) {
      const [, year, month, day] = localDateMatch;
      return new Date(Number(year), Number(month) - 1, Number(day));
    }
    const parsed = new Date(normalized);
    if (Number.isNaN(parsed.getTime())) return null;
    return parsed;
  };

  if (!start && !end) return "Data a confirmar";
  const startDate = parseDate(start);
  const endDate = parseDate(end);
  const startLabel = startDate ? formatter.format(startDate) : null;
  const endLabel = endDate ? formatter.format(endDate) : null;
  if (startLabel && endLabel) return `${startLabel} - ${endLabel}`;
  return startLabel || endLabel || "Data a confirmar";
}

export function getFieldLabel(field: LandingField) {
  return field.required ? `${field.label} *` : field.label;
}
