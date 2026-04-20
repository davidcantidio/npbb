/**
 * Presets de trimestre civil (Q1–Q4) para o filtro de datas da lista de leads.
 * Datas em YYYY-MM-DD para uso direto em inputs type="date".
 */

export function quarterDateRangeISO(year: number, quarter: 1 | 2 | 3 | 4): { start: string; end: string } {
  const table: Record<1 | 2 | 3 | 4, readonly [number, number, number, number]> = {
    1: [1, 1, 3, 31],
    2: [4, 1, 6, 30],
    3: [7, 1, 9, 30],
    4: [10, 1, 12, 31],
  };
  const pad = (n: number) => String(n).padStart(2, "0");
  const [sm, sd, em, ed] = table[quarter];
  return {
    start: `${year}-${pad(sm)}-${pad(sd)}`,
    end: `${year}-${pad(em)}-${pad(ed)}`,
  };
}

export function inferActiveQuarter(
  dataInicio: string,
  dataFim: string,
  year: number,
): 1 | 2 | 3 | 4 | null {
  for (const q of [1, 2, 3, 4] as const) {
    const { start, end } = quarterDateRangeISO(year, q);
    if (dataInicio === start && dataFim === end) return q;
  }
  return null;
}
