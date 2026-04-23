import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getAgeAnalysis } from "../services/dashboard_age_analysis";
import { toApiErrorMessage } from "../services/http";
import { useAuth } from "../store/auth";
import {
  AGE_ANALYSIS_RESPONSE_VERSION,
  type AgeAnalysisFiltersQuery,
  type AgeAnalysisResponse,
} from "../types/dashboard";

type UseAgeAnalysisResult = {
  data: AgeAnalysisResponse | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  lastSuccessfulAt: string | null;
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

function validateAgeAnalysisResponse(payload: AgeAnalysisResponse): AgeAnalysisResponse {
  if (payload.version !== AGE_ANALYSIS_RESPONSE_VERSION) {
    throw new Error(
      `Contrato da analise etaria incompatível. Esperado v${AGE_ANALYSIS_RESPONSE_VERSION}, recebido v${payload.version}.`,
    );
  }

  if (!payload.age_reference_date || !payload.confianca_consolidado || !payload.qualidade_consolidado) {
    throw new Error("Resposta da analise etaria sem os campos obrigatorios de confianca.");
  }

  return payload;
}

export function useAgeAnalysis(filters: AgeAnalysisFiltersQuery = {}): UseAgeAnalysisResult {
  const { token } = useAuth();
  const requestIdRef = useRef(0);
  const dataRef = useRef<AgeAnalysisResponse | null>(null);
  const normalizedFilters = useMemo(() => normalizeFilters(filters), [filters]);
  const filtersKey = useMemo(() => JSON.stringify(normalizedFilters), [normalizedFilters]);

  const [data, setData] = useState<AgeAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSuccessfulAt, setLastSuccessfulAt] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (!token) {
      dataRef.current = null;
      setData(null);
      setIsLoading(false);
      setIsRefreshing(false);
      setLastSuccessfulAt(null);
      setError("Usuario nao autenticado.");
      return;
    }

    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;
    const hasCachedData = dataRef.current !== null;
    setIsLoading(!hasCachedData);
    setIsRefreshing(hasCachedData);
    setError(null);

    try {
      const response = validateAgeAnalysisResponse(await getAgeAnalysis(token, normalizedFilters));
      if (requestIdRef.current !== requestId) return;
      dataRef.current = response;
      setData(response);
      setLastSuccessfulAt(response.generated_at);
    } catch (requestError) {
      if (requestIdRef.current !== requestId) return;
      setError(toApiErrorMessage(requestError, "Nao foi possivel carregar a analise etaria."));
      if (!dataRef.current) {
        setData(null);
      }
    } finally {
      if (requestIdRef.current === requestId) {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    }
  }, [normalizedFilters, token]);

  useEffect(() => {
    void refetch();
  }, [filtersKey, refetch]);

  return {
    data,
    isLoading,
    isRefreshing,
    error,
    lastSuccessfulAt,
    refetch,
  };
}
