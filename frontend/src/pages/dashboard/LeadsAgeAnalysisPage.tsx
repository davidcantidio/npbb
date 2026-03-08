import SearchOffRoundedIcon from "@mui/icons-material/SearchOffRounded";
import { Alert, Box, Button, CircularProgress, Stack, Typography } from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import { AgeAnalysisFilters, ALL_EVENTS_OPTION_ID } from "../../components/dashboard/AgeAnalysisFilters";
import { AgeAnalysisKpiGrid } from "../../components/dashboard/AgeAnalysisKpiGrid";
import { AgeDistributionChart } from "../../components/dashboard/AgeDistributionChart";
import { ConsolidatedPanel } from "../../components/dashboard/ConsolidatedPanel";
import { CoverageBanner } from "../../components/dashboard/CoverageBanner";
import { EventsAgeTable } from "../../components/dashboard/EventsAgeTable";
import { useAgeAnalysis } from "../../hooks/useAgeAnalysis";
import { useAgeAnalysisFilters } from "./useAgeAnalysisFilters";
import { useReferenciaEventos } from "./useReferenciaEventos";
import type { ReferenciaEvento } from "../../services/leads_import";
import { useAuth } from "../../store/auth";

const ALL_EVENTS_OPTION: ReferenciaEvento = {
  id: ALL_EVENTS_OPTION_ID,
  nome: "Todos os eventos",
  data_inicio_prevista: null,
};

function EmptyState() {
  return (
    <Box
      sx={{
        py: 8,
        px: 2,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        border: 1,
        borderColor: "divider",
        borderRadius: 3,
        bgcolor: "background.paper",
      }}
    >
      <SearchOffRoundedIcon sx={{ fontSize: 38, color: "text.secondary", mb: 1.25 }} />
      <Typography variant="h6" fontWeight={800}>
        Nenhum lead encontrado para os filtros aplicados
      </Typography>
    </Box>
  );
}

export default function LeadsAgeAnalysisPage() {
  const { token } = useAuth();
  const {
    appliedFilters,
    draftFilters,
    queryFilters,
    invalidDateRange,
    setDraftFilters,
    handleApplyFilters,
    handleClearFilters,
    handleSelectEvento,
  } = useAgeAnalysisFilters();
  const { eventOptions, isLoadingEvents, eventsError } = useReferenciaEventos(token);
  const eventOptionsWithAll = useMemo(
    () => [ALL_EVENTS_OPTION, ...eventOptions.filter((option) => option.id !== ALL_EVENTS_OPTION_ID)],
    [eventOptions],
  );
  const { data, isLoading, error, refetch } = useAgeAnalysis(queryFilters);

  const [isCoverageBannerDismissed, setIsCoverageBannerDismissed] = useState(false);
  const queryFiltersKey = useMemo(() => JSON.stringify(queryFilters), [queryFilters]);

  useEffect(() => {
    setIsCoverageBannerDismissed(false);
  }, [queryFiltersKey]);

  const isEmpty = Boolean(data && data.consolidado.base_total === 0);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={900}>
          Analise etaria por evento
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Painel consolidado com distribuicao etaria por evento, foco em clientes BB e apoio a filtro por periodo.
        </Typography>
      </Box>

      <AgeAnalysisFilters
        value={draftFilters}
        eventOptions={eventOptionsWithAll}
        isLoadingEvents={isLoadingEvents}
        hasInvalidRange={invalidDateRange}
        onChange={setDraftFilters}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
      />

      {eventsError ? <Alert severity="warning">{eventsError}</Alert> : null}
      {error ? (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={() => void refetch()}>
              Tentar novamente
            </Button>
          }
        >
          {error}
        </Alert>
      ) : null}

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress />
        </Box>
      ) : null}

      {!isLoading && data ? (
        <>
          {!isCoverageBannerDismissed && !isEmpty ? (
            <CoverageBanner
              coverage={data.consolidado.cobertura_bb_pct}
              dismissible
              onDismiss={() => setIsCoverageBannerDismissed(true)}
            />
          ) : null}

          {isEmpty ? (
            <EmptyState />
          ) : (
            <>
              <AgeAnalysisKpiGrid data={data} eventosTotal={data.por_evento.length} appliedFilters={appliedFilters} />
              <ConsolidatedPanel data={data.consolidado} />
              <AgeDistributionChart events={data.por_evento} />
              <EventsAgeTable events={data.por_evento} onSelectEvento={handleSelectEvento} />
            </>
          )}
        </>
      ) : null}
    </Stack>
  );
}
