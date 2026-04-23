import SearchOffRoundedIcon from "@mui/icons-material/SearchOffRounded";
import { Alert, Box, Button, Snackbar, Stack, Typography } from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import { AgeAnalysisFilters, ALL_EVENTS_OPTION_ID } from "../../../components/dashboard/AgeAnalysisFilters";
import { AgeAnalysisKpiGrid } from "../../../components/dashboard/AgeAnalysisKpiGrid";
import { AgeDistributionChart } from "../../../components/dashboard/AgeDistributionChart";
import { ChannelMixChart } from "../../../components/dashboard/ChannelMixChart";
import { ChartSkeleton } from "../../../components/dashboard/ChartSkeleton";
import { ConfidenceSummaryCard } from "../../../components/dashboard/ConfidenceSummaryCard";
import { CoverageBanner } from "../../../components/dashboard/CoverageBanner";
import { DataQualityTable } from "../../../components/dashboard/DataQualityTable";
import { EventsAgeTable } from "../../../components/dashboard/EventsAgeTable";
import { KpiCardSkeleton } from "../../../components/dashboard/KpiCardSkeleton";
import { TableSkeleton } from "../../../components/dashboard/TableSkeleton";
import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { buildAgeAnalysisViewModel } from "../../../utils/ageAnalysisViewModel";
import { useAgeAnalysisFilters } from "./useAgeAnalysisFilters";
import type { ReferenciaEvento } from "../../../services/leads_import";
import { useAuth } from "../../../store/auth";
import { useReferenciaEventos } from "../shared";

const ALL_EVENTS_OPTION: ReferenciaEvento = {
  id: ALL_EVENTS_OPTION_ID,
  nome: "Todos os eventos",
  data_inicio_prevista: null,
};

function EmptyState({ detail }: { detail?: string | null }) {
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
      {detail ? (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {detail}
        </Typography>
      ) : null}
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
    handleClearFilters,
    handleSelectEvento,
  } = useAgeAnalysisFilters();
  const { eventOptions, isLoadingEvents, eventsError } = useReferenciaEventos(token);
  const eventOptionsWithAll = useMemo(
    () => [ALL_EVENTS_OPTION, ...eventOptions.filter((option) => option.id !== ALL_EVENTS_OPTION_ID)],
    [eventOptions],
  );
  const invalidEventoOption = useMemo(() => {
    if (draftFilters.evento_id === null) return null;
    const selected = eventOptionsWithAll.find((option) => option.id === draftFilters.evento_id);
    if (selected || isLoadingEvents) return null;
    return {
      id: draftFilters.evento_id,
      nome: `Evento indisponivel (#${draftFilters.evento_id})`,
      data_inicio_prevista: null,
    } satisfies ReferenciaEvento;
  }, [draftFilters.evento_id, eventOptionsWithAll, isLoadingEvents]);
  const { data, isLoading, isRefreshing, error, lastSuccessfulAt, refetch } = useAgeAnalysis(queryFilters);

  const [isCoverageBannerDismissed, setIsCoverageBannerDismissed] = useState(false);
  const [isErrorToastOpen, setIsErrorToastOpen] = useState(false);
  const queryFiltersKey = useMemo(() => JSON.stringify(queryFilters), [queryFilters]);
  const viewModel = useMemo(() => (data ? buildAgeAnalysisViewModel(data) : null), [data]);

  useEffect(() => {
    setIsCoverageBannerDismissed(false);
  }, [queryFiltersKey]);

  useEffect(() => {
    setIsErrorToastOpen(Boolean(error));
  }, [error]);

  const isEmpty = Boolean(data && data.consolidado.base_total === 0);
  const showInitialLoadingState = isLoading && !data;

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
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
        invalidEventoOption={invalidEventoOption}
        onChange={setDraftFilters}
        onClear={handleClearFilters}
      />

      {eventsError ? <Alert severity="warning">{eventsError}</Alert> : null}
      {data && (isRefreshing || error) ? (
        <Alert
          severity={error ? "warning" : "info"}
          action={
            <Button color="inherit" size="small" onClick={() => void refetch()}>
              Atualizar
            </Button>
          }
        >
          {isRefreshing
            ? "Atualizando a analise. Os dados atuais permanecem visiveis ate a nova resposta chegar."
            : `Mostrando o ultimo resultado valido de ${
                lastSuccessfulAt ? new Date(lastSuccessfulAt).toLocaleString("pt-BR") : "momento anterior"
              } porque a atualizacao falhou.`}
        </Alert>
      ) : null}
      <Snackbar
        open={Boolean(error) && !data && isErrorToastOpen}
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        onClose={(_, reason) => {
          if (reason === "clickaway") return;
          setIsErrorToastOpen(false);
        }}
      >
        <Alert
          severity="error"
          variant="filled"
          onClose={() => setIsErrorToastOpen(false)}
          action={
            <Button color="inherit" size="small" onClick={() => void refetch()}>
              Tentar novamente
            </Button>
          }
          sx={{ alignItems: "center" }}
        >
          {error}
        </Alert>
      </Snackbar>

      {showInitialLoadingState ? (
        <Stack spacing={3}>
          <Box
            sx={{
              display: "grid",
              gap: 2,
              gridTemplateColumns: {
                xs: "minmax(0, 1fr)",
                sm: "repeat(2, minmax(0, 1fr))",
                xl: "repeat(4, minmax(0, 1fr))",
              },
            }}
          >
            {Array.from({ length: 12 }).map((_, index) => (
              <KpiCardSkeleton key={index} />
            ))}
          </Box>
          <ChartSkeleton />
          <TableSkeleton />
        </Stack>
      ) : null}

      {data ? (
        <>
          {!isCoverageBannerDismissed && !isEmpty ? (
            <CoverageBanner
              coverage={data.consolidado.cobertura_bb_pct}
              dismissible
              onDismiss={() => setIsCoverageBannerDismissed(true)}
            />
          ) : null}

          {isEmpty ? (
            <EmptyState detail={data.insights.alertas[0] ?? null} />
          ) : (
            <>
              {viewModel ? <ConfidenceSummaryCard data={data} viewModel={viewModel} /> : null}
              <AgeAnalysisKpiGrid data={data} eventosTotal={data.por_evento.length} appliedFilters={appliedFilters} />
              <AgeDistributionChart events={data.por_evento} />
              <ChannelMixChart events={data.por_evento} />
              <DataQualityTable
                consolidated={data.qualidade_consolidado}
                rows={data.qualidade_por_origem}
              />
              <EventsAgeTable events={data.por_evento} onSelectEvento={handleSelectEvento} />
            </>
          )}
        </>
      ) : null}
    </Stack>
  );
}
