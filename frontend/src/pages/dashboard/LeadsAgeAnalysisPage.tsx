import CalendarMonthRoundedIcon from "@mui/icons-material/CalendarMonthRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import SearchOffRoundedIcon from "@mui/icons-material/SearchOffRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import {
  Alert,
  Box,
  Button,
  Grid,
  Snackbar,
  Stack,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ALL_EVENTS_OPTION_ID, AgeAnalysisFilters } from "../../components/dashboard/AgeAnalysisFilters";
import { AgeDistributionChart } from "../../components/dashboard/AgeDistributionChart";
import { ChartSkeleton } from "../../components/dashboard/ChartSkeleton";
import { ConsolidatedPanel } from "../../components/dashboard/ConsolidatedPanel";
import { CoverageBanner } from "../../components/dashboard/CoverageBanner";
import { EventsAgeTable } from "../../components/dashboard/EventsAgeTable";
import { InfoTooltip } from "../../components/dashboard/InfoTooltip";
import { KpiCard } from "../../components/dashboard/KpiCard";
import { KpiCardSkeleton } from "../../components/dashboard/KpiCardSkeleton";
import { TableSkeleton } from "../../components/dashboard/TableSkeleton";
import { useAgeAnalysis } from "../../hooks/useAgeAnalysis";
import { listReferenciaEventos, type ReferenciaEvento } from "../../services/leads_import";
import { toApiErrorMessage } from "../../services/http";
import { useAuth } from "../../store/auth";
import type { AgeAnalysisFilterFormValues, AgeAnalysisFiltersQuery } from "../../types/dashboard";
import {
  formatInteger,
  formatPercent,
  getDominantAgeRangeLabel,
  getDominantRangeFromBreakdown,
} from "../../utils/ageAnalysis";
import {
  BB_COVERAGE_DANGER_THRESHOLD,
  BB_COVERAGE_WARNING_THRESHOLD,
  hasPartialBbData,
} from "../../utils/coverage";

const EMPTY_FILTERS: AgeAnalysisFilterFormValues = {
  evento_id: null,
  data_inicio: "",
  data_fim: "",
};

const ALL_EVENTS_OPTION: ReferenciaEvento = {
  id: ALL_EVENTS_OPTION_ID,
  nome: "Todos os eventos",
  data_inicio_prevista: null,
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

function PartialDataNote() {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.25 }}>
      <Typography variant="caption" color="text.secondary">
        (dados parciais)
      </Typography>
      <InfoTooltip
        label="Dados parciais"
        description="Dados parciais: a cobertura BB esta abaixo do limiar minimo para exibir a metrica com seguranca."
      />
    </Box>
  );
}

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

function AgeAnalysisLoadingState() {
  return (
    <Stack spacing={2}>
      <Grid container spacing={2}>
        {Array.from({ length: 4 }).map((_, index) => (
          <Grid key={`kpi-skeleton-${index}`} item xs={12} sm={6} xl={3}>
            <KpiCardSkeleton />
          </Grid>
        ))}
      </Grid>
      <ChartSkeleton />
      <TableSkeleton />
    </Stack>
  );
}

export default function LeadsAgeAnalysisPage() {
  const { token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const appliedFilters = useMemo(() => readFiltersFromSearchParams(searchParams), [searchParams]);
  const [draftFilters, setDraftFilters] = useState<AgeAnalysisFilterFormValues>(appliedFilters);
  const [eventOptions, setEventOptions] = useState<ReferenciaEvento[]>([]);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [isCoverageBannerDismissed, setIsCoverageBannerDismissed] = useState(false);
  const [errorToastOpen, setErrorToastOpen] = useState(false);
  const eventOptionsWithAll = useMemo(
    () => [ALL_EVENTS_OPTION, ...eventOptions.filter((option) => option.id !== ALL_EVENTS_OPTION_ID)],
    [eventOptions],
  );

  const queryFilters = useMemo(() => toQueryFilters(appliedFilters), [appliedFilters]);
  const queryFiltersKey = useMemo(() => JSON.stringify(queryFilters), [queryFilters]);
  const { data, isLoading, error, refetch } = useAgeAnalysis(queryFilters);

  useEffect(() => {
    setDraftFilters(appliedFilters);
  }, [appliedFilters]);

  useEffect(() => {
    setIsCoverageBannerDismissed(false);
  }, [queryFiltersKey]);

  useEffect(() => {
    if (!error) return;
    setErrorToastOpen(true);
  }, [error]);

  useEffect(() => {
    if (!token) return;

    let isActive = true;
    setIsLoadingEvents(true);
    setEventsError(null);

    listReferenciaEventos(token)
      .then((response) => {
        if (!isActive) return;
        setEventOptions(response);
      })
      .catch((requestError) => {
        if (!isActive) return;
        setEventsError(toApiErrorMessage(requestError, "Nao foi possivel carregar os eventos."));
      })
      .finally(() => {
        if (isActive) {
          setIsLoadingEvents(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [token]);

  const invalidDateRange = hasDateRangeError(draftFilters);
  const baseTotal = data?.consolidado.base_total ?? 0;
  const eventosTotal = data?.por_evento.length ?? 0;
  const dominantConsolidatedRange = data
    ? getDominantRangeFromBreakdown(data.consolidado.faixas)
    : "sem_info";

  const handleFiltersChange = (nextFilters: AgeAnalysisFilterFormValues) => {
    setDraftFilters(nextFilters);

    if (hasDateRangeError(nextFilters)) return;

    const nextSearchParams = buildSearchParams(nextFilters);
    if (nextSearchParams.toString() === searchParams.toString()) return;
    setSearchParams(nextSearchParams, { replace: true });
  };

  const handleClearFilters = () => {
    setDraftFilters(EMPTY_FILTERS);
    setSearchParams(new URLSearchParams(), { replace: true });
  };

  const handleSelectEvento = (eventoId: number) => {
    handleFiltersChange({
      ...draftFilters,
      evento_id: eventoId,
    });
  };

  const hasData = Boolean(data);
  const isEmpty = hasData && baseTotal === 0;
  const consolidatedPartialBbData = data
    ? hasPartialBbData(
        data.consolidado.clientes_bb_volume,
        data.consolidado.clientes_bb_pct,
        data.consolidado.cobertura_bb_pct,
        {
          warning: BB_COVERAGE_WARNING_THRESHOLD,
          danger: BB_COVERAGE_DANGER_THRESHOLD,
        },
      )
    : false;

  const handleRetry = () => {
    setErrorToastOpen(false);
    void refetch();
  };

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
        eventOptions={eventOptionsWithAll}
        isLoadingEvents={isLoadingEvents}
        hasInvalidRange={invalidDateRange}
        onChange={handleFiltersChange}
        onClear={handleClearFilters}
      />

      {eventsError ? <Alert severity="warning">{eventsError}</Alert> : null}

      {isLoading ? <AgeAnalysisLoadingState /> : null}

      {!isLoading && data && isEmpty ? <EmptyState /> : null}

      {!isLoading && data && !isEmpty ? (
        <>
          {!isCoverageBannerDismissed ? (
            <CoverageBanner
              coverage={data.consolidado.cobertura_bb_pct}
              thresholdWarning={BB_COVERAGE_WARNING_THRESHOLD}
              thresholdDanger={BB_COVERAGE_DANGER_THRESHOLD}
              dismissible
              onDismiss={() => setIsCoverageBannerDismissed(true)}
            />
          ) : null}

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} xl={3}>
              <KpiCard
                title="Base Total"
                value={formatInteger(data.consolidado.base_total)}
                subtitle="Leads no filtro aplicado."
                helperText={`Gerado em ${new Date(data.generated_at).toLocaleString("pt-BR")}`}
                icon={<GroupsRoundedIcon fontSize="small" />}
              />
            </Grid>
            <Grid item xs={12} sm={6} xl={3}>
              <KpiCard
                title="Clientes BB"
                titleTooltip="Percentual de leads com informacao de vinculo BB disponivel"
                value={
                  <Stack spacing={0.25}>
                    <Typography variant="h5" fontWeight={800}>
                      {data.consolidado.clientes_bb_volume === null
                        ? "—"
                        : formatInteger(data.consolidado.clientes_bb_volume)}
                    </Typography>
                    {consolidatedPartialBbData ? <PartialDataNote /> : null}
                  </Stack>
                }
                subtitle={`Percentual da base: ${formatPercent(data.consolidado.clientes_bb_pct)}`}
                helperText="Valores ficam indisponiveis quando a cobertura BB esta abaixo do limiar."
                icon={<VerifiedRoundedIcon fontSize="small" />}
                progressValue={data.consolidado.cobertura_bb_pct}
                progressLabel="Cobertura BB"
              />
            </Grid>
            <Grid item xs={12} sm={6} xl={3}>
              <KpiCard
                title="Faixa Dominante"
                titleTooltip="Faixa etaria com maior volume de leads na base consolidada"
                value={getDominantAgeRangeLabel(dominantConsolidatedRange)}
                subtitle="Faixa predominante considerando toda a base consolidada."
                helperText={
                  data.consolidado.top_eventos[0]
                    ? `Evento lider: ${data.consolidado.top_eventos[0].evento_nome}`
                    : "Sem evento lider no filtro."
                }
                icon={<InsightsRoundedIcon fontSize="small" />}
              />
            </Grid>
            <Grid item xs={12} sm={6} xl={3}>
              <KpiCard
                title="Eventos"
                value={formatInteger(eventosTotal)}
                subtitle="Eventos retornados para os filtros aplicados."
                helperText={
                  appliedFilters.data_inicio || appliedFilters.data_fim
                    ? `Periodo: ${appliedFilters.data_inicio || "inicio livre"} ate ${
                        appliedFilters.data_fim || "fim livre"
                      }`
                    : "Sem recorte de periodo."
                }
                icon={<CalendarMonthRoundedIcon fontSize="small" />}
              />
            </Grid>
          </Grid>

          <ConsolidatedPanel data={data.consolidado} />
          <AgeDistributionChart events={data.por_evento} />
          <EventsAgeTable events={data.por_evento} onSelectEvento={handleSelectEvento} />
        </>
      ) : null}

      <Snackbar
        open={Boolean(error) && errorToastOpen}
        autoHideDuration={7000}
        onClose={(_, reason) => {
          if (reason === "clickaway") return;
          setErrorToastOpen(false);
        }}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          severity="error"
          onClose={() => setErrorToastOpen(false)}
          action={
            <Button color="inherit" size="small" onClick={handleRetry}>
              Tentar novamente
            </Button>
          }
          sx={{ width: "100%" }}
        >
          {error}
        </Alert>
      </Snackbar>
    </Stack>
  );
}
