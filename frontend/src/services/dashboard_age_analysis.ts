import { fetchWithAuth, handleApiResponse } from "./http";
import type { AgeAnalysisFiltersQuery, AgeAnalysisResponse } from "../types/dashboard";

/** Consulta pesada; o defeito 20s+retry (acumulando ~40s) bloqueava eventos com muitos leads. */
const AGE_ANALYSIS_TIMEOUT_MS = 120_000;

function buildQueryString(filters: AgeAnalysisFiltersQuery) {
  const query = new URLSearchParams();

  if (typeof filters.evento_id === "number") {
    query.set("evento_id", String(filters.evento_id));
  }
  if (filters.data_inicio) {
    query.set("data_inicio", filters.data_inicio);
  }
  if (filters.data_fim) {
    query.set("data_fim", filters.data_fim);
  }

  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function getAgeAnalysis(
  token: string,
  filters: AgeAnalysisFiltersQuery = {},
): Promise<AgeAnalysisResponse> {
  const res = await fetchWithAuth(`/dashboard/leads/analise-etaria${buildQueryString(filters)}`, {
    token,
    timeoutMs: AGE_ANALYSIS_TIMEOUT_MS,
    retries: 0,
  });
  return handleApiResponse<AgeAnalysisResponse>(res);
}
