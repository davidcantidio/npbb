import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getAgeAnalysis } from "../services/dashboard_age_analysis";
import { toApiErrorMessage } from "../services/http";
import { useAuth } from "../store/auth";
import type { AgeAnalysisFiltersQuery, AgeAnalysisResponse } from "../types/dashboard";

type UseAgeAnalysisResult = {
  data: AgeAnalysisResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
};

function normalizeFilters(filters: AgeAnalysisFiltersQuery): AgeAnalysisFiltersQuery {
  const normalized: AgeAnalysisFiltersQuery = {};

  if (typeof filters.evento_id === "number") {
    normalized.evento_id = filters.evento_id;
  }
  if (filters.data_inicio) {
    normalized.data_inicio = filters.data_inicio;
  }
  if (filters.data_fim) {
    normalized.data_fim = filters.data_fim;
  }

  return normalized;
}

export function useAgeAnalysis(filters: AgeAnalysisFiltersQuery = {}): UseAgeAnalysisResult {
  const { token } = useAuth();
  const requestIdRef = useRef(0);
  const normalizedFilters = useMemo(() => normalizeFilters(filters), [filters]);
  const filtersKey = useMemo(() => JSON.stringify(normalizedFilters), [normalizedFilters]);

  const [data, setData] = useState<AgeAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (!token) {
      setData(null);
      setIsLoading(false);
      setError("Usuario nao autenticado.");
      return;
    }

    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;
    setIsLoading(true);
    setError(null);

    try {
      const response = await getAgeAnalysis(token, normalizedFilters);
      if (requestIdRef.current !== requestId) return;
      setData(response);
    } catch (requestError) {
      if (requestIdRef.current !== requestId) return;
      setData(null);
      setError(toApiErrorMessage(requestError, "Nao foi possivel carregar a analise etaria."));
    } finally {
      if (requestIdRef.current === requestId) {
        setIsLoading(false);
      }
    }
  }, [normalizedFilters, token]);

  useEffect(() => {
    void refetch();
  }, [filtersKey, refetch]);

  return {
    data,
    isLoading,
    error,
    refetch,
  };
}
