import type { AgeAnalysisResponse } from "../types/dashboard";

export type AgeAnalysisViewModel = {
  ageReferenceLabel: string;
  generatedAtLabel: string;
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
  };
}
