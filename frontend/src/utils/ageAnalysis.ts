import type { AgeBreakdown, AgeRangeKey, DominantAgeRangeKey, EventoAgeAnalysis } from "../types/dashboard";

export const AGE_RANGE_META: Record<
  DominantAgeRangeKey,
  {
    label: string;
    color: string;
  }
> = {
  faixa_18_25: {
    label: "18–25",
    color: "#1976d2",
  },
  faixa_26_40: {
    label: "26–40",
    color: "#2e7d32",
  },
  faixa_18_40: {
    label: "18–40",
    color: "#00838f",
  },
  fora_18_40: {
    label: "Fora de 18–40",
    color: "#ed6c02",
  },
  sem_info: {
    label: "Sem informacao",
    color: "#9e9e9e",
  },
};

const integerFormatter = new Intl.NumberFormat("pt-BR");
const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export function formatInteger(value: number) {
  return integerFormatter.format(value);
}

export function formatDecimal(value: number) {
  return decimalFormatter.format(value);
}

export function formatPercent(value: number | null | undefined) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return `${formatDecimal(value)}%`;
}

export function getDominantAgeRangeLabel(value: DominantAgeRangeKey) {
  return AGE_RANGE_META[value].label;
}

export function getDominantRangeFromBreakdown(breakdown: AgeBreakdown): DominantAgeRangeKey {
  const ranking: Array<{ key: DominantAgeRangeKey; value: number }> = [
    { key: "faixa_18_25", value: breakdown.faixa_18_25.volume },
    { key: "faixa_26_40", value: breakdown.faixa_26_40.volume },
    { key: "fora_18_40", value: breakdown.fora_18_40.volume },
    { key: "sem_info", value: breakdown.sem_info_volume },
  ];

  return ranking.sort((left, right) => right.value - left.value)[0]?.key ?? "sem_info";
}

export function getAgeBreakdownVolume(breakdown: AgeBreakdown, key: AgeRangeKey | "sem_info") {
  if (key === "sem_info") return breakdown.sem_info_volume;
  return breakdown[key].volume;
}

export function getAgeBreakdownPercent(breakdown: AgeBreakdown, key: AgeRangeKey | "sem_info") {
  if (key === "sem_info") return breakdown.sem_info_pct_da_base;
  return breakdown[key].pct;
}

export function truncateLabel(value: string, maxLength = 22) {
  if (value.length <= maxLength) return value;
  return `${value.slice(0, Math.max(maxLength - 1, 1)).trimEnd()}…`;
}

export function formatEventLocation(evento: Pick<EventoAgeAnalysis, "cidade" | "estado">) {
  return `${evento.cidade} - ${evento.estado}`;
}

export function buildEventLabel(evento: Pick<EventoAgeAnalysis, "evento_nome" | "cidade" | "estado">) {
  return `${evento.evento_nome} (${formatEventLocation(evento)})`;
}

function pctPart(part: number, total: number) {
  if (total <= 0) return 0;
  return Math.round((part / total) * 100 * 100) / 100;
}

export function getNonBbMetrics(evento: EventoAgeAnalysis) {
  if (evento.nao_clientes_bb_volume !== null && evento.nao_clientes_bb_pct !== null) {
    return { volume: evento.nao_clientes_bb_volume, pct: evento.nao_clientes_bb_pct };
  }
  if (evento.clientes_bb_volume === null || evento.clientes_bb_pct === null) {
    return { volume: null, pct: null };
  }
  const volume = Math.max(
    evento.base_leads - evento.clientes_bb_volume - evento.bb_indefinido_volume,
    0,
  );
  return {
    volume,
    pct: pctPart(volume, evento.base_leads),
  };
}
