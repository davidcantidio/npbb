import { fetchWithAuth, handleApiResponse } from "./http";
import type { AgeAnalysisFiltersQuery, AgeAnalysisResponse } from "../types/dashboard";

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
  });
  return handleApiResponse<AgeAnalysisResponse>(res);
}
