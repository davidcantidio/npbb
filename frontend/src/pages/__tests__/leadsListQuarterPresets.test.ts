import { describe, expect, it } from "vitest";

import { inferActiveQuarter, quarterDateRangeISO } from "../leads/leadsListQuarterPresets";

describe("quarterDateRangeISO", () => {
  it("retorna intervalos inclusivos corretos para 2026", () => {
    expect(quarterDateRangeISO(2026, 1)).toEqual({ start: "2026-01-01", end: "2026-03-31" });
    expect(quarterDateRangeISO(2026, 2)).toEqual({ start: "2026-04-01", end: "2026-06-30" });
    expect(quarterDateRangeISO(2026, 3)).toEqual({ start: "2026-07-01", end: "2026-09-30" });
    expect(quarterDateRangeISO(2026, 4)).toEqual({ start: "2026-10-01", end: "2026-12-31" });
  });
});

describe("inferActiveQuarter", () => {
  it("identifica o trimestre quando as datas coincidem com o preset do ano", () => {
    expect(inferActiveQuarter("2026-07-01", "2026-09-30", 2026)).toBe(3);
    expect(inferActiveQuarter("2026-01-01", "2026-03-31", 2026)).toBe(1);
  });

  it("retorna null quando o intervalo não é exatamente um trimestre", () => {
    expect(inferActiveQuarter("2026-07-01", "2026-09-15", 2026)).toBeNull();
    expect(inferActiveQuarter("", "", 2026)).toBeNull();
  });
});
