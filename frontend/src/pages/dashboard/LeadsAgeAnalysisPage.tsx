import CalendarMonthRoundedIcon from "@mui/icons-material/CalendarMonthRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Grid,
  Stack,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { AgeAnalysisFilters } from "../../components/dashboard/AgeAnalysisFilters";
import { AgeDistributionChart } from "../../components/dashboard/AgeDistributionChart";
import { ConsolidatedPanel } from "../../components/dashboard/ConsolidatedPanel";
import { EventsAgeTable } from "../../components/dashboard/EventsAgeTable";
import { KpiCard } from "../../components/dashboard/KpiCard";
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

export default function LeadsAgeAnalysisPage() {
  const { token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const appliedFilters = useMemo(() => readFiltersFromSearchParams(searchParams), [searchParams]);
  const [draftFilters, setDraftFilters] = useState<AgeAnalysisFilterFormValues>(appliedFilters);
  const [eventOptions, setEventOptions] = useState<ReferenciaEvento[]>([]);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [eventsError, setEventsError] = useState<string | null>(null);

  const queryFilters = useMemo(() => toQueryFilters(appliedFilters), [appliedFilters]);
  const { data, isLoading, error, refetch } = useAgeAnalysis(queryFilters);

  useEffect(() => {
    setDraftFilters(appliedFilters);
  }, [appliedFilters]);

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

  const handleApplyFilters = () => {
    if (invalidDateRange) return;
    setSearchParams(buildSearchParams(draftFilters), { replace: true });
  };

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

  const hasData = Boolean(data);
  const isEmpty = hasData && baseTotal === 0;

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
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} xl={3}>
              <KpiCard
                title="Base total"
                value={formatInteger(data.consolidado.base_total)}
                subtitle="Leads no filtro aplicado."
                helperText={`Gerado em ${new Date(data.generated_at).toLocaleString("pt-BR")}`}
                icon={<GroupsRoundedIcon fontSize="small" />}
              />
            </Grid>
            <Grid item xs={12} sm={6} xl={3}>
              <KpiCard
                title="Clientes BB"
                value={
                  data.consolidado.clientes_bb_volume === null
                    ? "—"
                    : formatInteger(data.consolidado.clientes_bb_volume)
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
                title="Faixa dominante"
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

          {isEmpty ? (
            <Alert severity="info">Nenhum lead encontrado para os filtros aplicados.</Alert>
          ) : null}
        </>
      ) : null}
    </Stack>
  );
}
