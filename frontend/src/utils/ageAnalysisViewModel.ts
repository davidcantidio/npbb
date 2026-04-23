import type { AgeAnalysisResponse } from "../types/dashboard";
import { formatInteger, formatPercent } from "./ageAnalysis";

export type AgeAnalysisViewModel = {
  ageReferenceLabel: string;
  generatedAtLabel: string;
  lineageSummary: string;
  executiveHighlights: string[];
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("pt-BR");
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("pt-BR");
}

export function buildAgeAnalysisViewModel(data: AgeAnalysisResponse): AgeAnalysisViewModel {
  const confidence = data.confianca_consolidado;
  const lineageSummary =
    confidence.lineage_mix.length > 0
      ? confidence.lineage_mix
          .map((row) => `${row.label}: ${formatInteger(row.volume)} (${formatPercent(row.pct)})`)
          .join(" | ")
      : "Sem lineage disponivel para o filtro.";

  return {
    ageReferenceLabel: formatDate(data.age_reference_date),
    generatedAtLabel: formatDateTime(data.generated_at),
    lineageSummary,
    executiveHighlights: [
      `Base utilizavel: ${formatInteger(data.consolidado.base_com_idade_volume)} com idade e ${formatInteger(
        data.consolidado.base_bb_coberta_volume,
      )} com cobertura BB.`,
      `Lineage consolidada: ${lineageSummary}`,
    ],
  };
}
