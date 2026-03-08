export const BB_COVERAGE_WARNING_THRESHOLD = 80;
export const BB_COVERAGE_DANGER_THRESHOLD = 20;

export type CoverageStatus = "normal" | "warning" | "danger";

type CoverageThresholds = {
  warning: number;
  danger: number;
};

export function getCoverageStatus(
  coverage: number | null | undefined,
  thresholds: CoverageThresholds = {
    warning: BB_COVERAGE_WARNING_THRESHOLD,
    danger: BB_COVERAGE_DANGER_THRESHOLD,
  },
): CoverageStatus {
  if (typeof coverage !== "number" || Number.isNaN(coverage)) return "danger";
  if (coverage < thresholds.danger) return "danger";
  if (coverage < thresholds.warning) return "warning";
  return "normal";
}

export function hasPartialBbData(
  clientesBbVolume: number | null,
  clientesBbPct: number | null,
  coverage: number,
  thresholds: CoverageThresholds = {
    warning: BB_COVERAGE_WARNING_THRESHOLD,
    danger: BB_COVERAGE_DANGER_THRESHOLD,
  },
) {
  if (clientesBbVolume !== null && clientesBbPct !== null) return false;
  return getCoverageStatus(coverage, thresholds) !== "normal";
}
