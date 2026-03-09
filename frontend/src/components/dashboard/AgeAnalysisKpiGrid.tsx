import CalendarMonthRoundedIcon from "@mui/icons-material/CalendarMonthRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import { Grid } from "@mui/material";

import type { AgeAnalysisFilterFormValues, AgeAnalysisResponse } from "../../types/dashboard";
import { formatInteger, formatPercent, getDominantAgeRangeLabel, getDominantRangeFromBreakdown } from "../../utils/ageAnalysis";
import { KpiCard } from "./KpiCard";

type AgeAnalysisKpiGridProps = {
  data: AgeAnalysisResponse;
  eventosTotal: number;
  appliedFilters: AgeAnalysisFilterFormValues;
};

const KPI_TOOLTIP_COPY = {
  dominantRange: "Faixa etária com maior volume de leads neste evento",
  bbCoverage: "Percentual de leads com informação de vínculo BB disponível",
} as const;

export function AgeAnalysisKpiGrid({ data, eventosTotal, appliedFilters }: AgeAnalysisKpiGridProps) {
  const dominantConsolidatedRange = getDominantRangeFromBreakdown(data.consolidado.faixas);

  return (
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
          progressTooltip={KPI_TOOLTIP_COPY.bbCoverage}
        />
      </Grid>
      <Grid item xs={12} sm={6} xl={3}>
        <KpiCard
          title="Faixa Dominante"
          value={getDominantAgeRangeLabel(dominantConsolidatedRange)}
          titleTooltip={KPI_TOOLTIP_COPY.dominantRange}
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
  );
}
