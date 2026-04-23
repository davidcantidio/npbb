import type { AgeAnalysisResponse } from "../types/dashboard";
import { formatInteger } from "./ageAnalysis";

export type AgeAnalysisViewModel = {
  ageReferenceLabel: string;
  generatedAtLabel: string;
  executiveHighlights: string[];
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("pt-BR");
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("pt-BR");
}

export function buildAgeAnalysisViewModel(data: AgeAnalysisResponse): AgeAnalysisViewModel {
  return {
    ageReferenceLabel: formatDate(data.age_reference_date),
    generatedAtLabel: formatDateTime(data.generated_at),
    executiveHighlights: [
      `Base utilizavel: ${formatInteger(data.consolidado.base_com_idade_volume)} com idade e ${formatInteger(
        data.consolidado.base_bb_coberta_volume,
      )} com cobertura BB.`,
    ],
  };
}
