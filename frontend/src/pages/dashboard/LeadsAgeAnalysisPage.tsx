import { Alert, Box, Button, CircularProgress, Stack, Typography } from "@mui/material";

import { AgeAnalysisFilters } from "../../components/dashboard/AgeAnalysisFilters";
import { AgeAnalysisKpiGrid } from "../../components/dashboard/AgeAnalysisKpiGrid";
import { AgeDistributionChart } from "../../components/dashboard/AgeDistributionChart";
import { ConsolidatedPanel } from "../../components/dashboard/ConsolidatedPanel";
import { EventsAgeTable } from "../../components/dashboard/EventsAgeTable";
import { useAgeAnalysis } from "../../hooks/useAgeAnalysis";
import { useAuth } from "../../store/auth";
import { useAgeAnalysisFilters } from "./useAgeAnalysisFilters";
import { useReferenciaEventos } from "./useReferenciaEventos";

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
  const { data, isLoading, error, refetch } = useAgeAnalysis(queryFilters);

  const isEmpty = data !== null && data.consolidado.base_total === 0;
  const eventosTotal = data?.por_evento.length ?? 0;

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={900}>
          Analise etaria por evento
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Painel consolidado com distribuicao etaria por evento, foco em clientes BB e apoio a filtro
          por periodo.
        </Typography>
      </Box>

      <AgeAnalysisFilters
        value={draftFilters}
        eventOptions={eventOptions}
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
          <AgeAnalysisKpiGrid
            data={data}
            eventosTotal={eventosTotal}
            appliedFilters={appliedFilters}
          />

          <ConsolidatedPanel data={data.consolidado} />
          <AgeDistributionChart events={data.por_evento} />
          <EventsAgeTable events={data.por_evento} onSelectEvento={handleSelectEvento} />

          {isEmpty ? (
            <Alert severity="info">Nenhum lead encontrado para os filtros aplicados.</Alert>
          ) : null}
        </>
      ) : null}
    </Stack>
  );
}
