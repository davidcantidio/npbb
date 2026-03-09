import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import type { AgeAnalysisFilterFormValues, AgeAnalysisFiltersQuery } from "../../types/dashboard";

const EMPTY_FILTERS: AgeAnalysisFilterFormValues = {
  evento_id: null,
  data_inicio: "",
  data_fim: "",
};

function parsePositiveInt(value: string | null) {
  if (!value) return null;
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return null;
  return parsed;
}

function readFiltersFromSearchParams(searchParams: URLSearchParams): AgeAnalysisFilterFormValues {
  return {
    evento_id: parsePositiveInt(searchParams.get("evento_id")),
    data_inicio: searchParams.get("data_inicio") ?? "",
    data_fim: searchParams.get("data_fim") ?? "",
  };
}

function toQueryFilters(filters: AgeAnalysisFilterFormValues): AgeAnalysisFiltersQuery {
  return {
    evento_id: typeof filters.evento_id === "number" ? filters.evento_id : undefined,
    data_inicio: filters.data_inicio || undefined,
    data_fim: filters.data_fim || undefined,
  };
}

function buildSearchParams(filters: AgeAnalysisFilterFormValues) {
  const searchParams = new URLSearchParams();

  if (typeof filters.evento_id === "number") {
    searchParams.set("evento_id", String(filters.evento_id));
  }
  if (filters.data_inicio) {
    searchParams.set("data_inicio", filters.data_inicio);
  }
  if (filters.data_fim) {
    searchParams.set("data_fim", filters.data_fim);
  }

  return searchParams;
}

function hasDateRangeError(filters: AgeAnalysisFilterFormValues) {
  if (!filters.data_inicio || !filters.data_fim) return false;
  return filters.data_fim < filters.data_inicio;
}

type UseAgeAnalysisFiltersResult = {
  appliedFilters: AgeAnalysisFilterFormValues;
  draftFilters: AgeAnalysisFilterFormValues;
  queryFilters: AgeAnalysisFiltersQuery;
  invalidDateRange: boolean;
  setDraftFilters: (value: AgeAnalysisFilterFormValues) => void;
  handleClearFilters: () => void;
  handleSelectEvento: (eventoId: number) => void;
};

function areFiltersEqual(left: AgeAnalysisFilterFormValues, right: AgeAnalysisFilterFormValues) {
  return (
    left.evento_id === right.evento_id &&
    left.data_inicio === right.data_inicio &&
    left.data_fim === right.data_fim
  );
}

export function useAgeAnalysisFilters(): UseAgeAnalysisFiltersResult {
  const [searchParams, setSearchParams] = useSearchParams();
  const appliedFilters = useMemo(() => readFiltersFromSearchParams(searchParams), [searchParams]);
  const [draftFilters, setDraftFilters] = useState<AgeAnalysisFilterFormValues>(appliedFilters);

  const queryFilters = useMemo(() => toQueryFilters(appliedFilters), [appliedFilters]);
  const invalidDateRange = hasDateRangeError(draftFilters);

  useEffect(() => {
    setDraftFilters((current) => (areFiltersEqual(current, appliedFilters) ? current : appliedFilters));
  }, [appliedFilters]);

  useEffect(() => {
    if (invalidDateRange || areFiltersEqual(draftFilters, appliedFilters)) return;
    setSearchParams(buildSearchParams(draftFilters), { replace: true });
  }, [appliedFilters, draftFilters, invalidDateRange, setSearchParams]);

  const handleClearFilters = () => {
    setDraftFilters(EMPTY_FILTERS);
    setSearchParams(new URLSearchParams(), { replace: true });
  };

  const handleSelectEvento = (eventoId: number) => {
    const nextFilters: AgeAnalysisFilterFormValues = {
      ...appliedFilters,
      evento_id: eventoId,
    };
    setDraftFilters(nextFilters);
    setSearchParams(buildSearchParams(nextFilters), { replace: true });
  };

  return {
    appliedFilters,
    draftFilters,
    queryFilters,
    invalidDateRange,
    setDraftFilters,
    handleClearFilters,
    handleSelectEvento,
  };
}
