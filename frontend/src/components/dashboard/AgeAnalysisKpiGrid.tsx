import AccountBalanceRoundedIcon from "@mui/icons-material/AccountBalanceRounded";
import CalendarMonthRoundedIcon from "@mui/icons-material/CalendarMonthRounded";
import CampaignRoundedIcon from "@mui/icons-material/CampaignRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import PersonOffRoundedIcon from "@mui/icons-material/PersonOffRounded";
import RuleRoundedIcon from "@mui/icons-material/RuleRounded";
import StorefrontRoundedIcon from "@mui/icons-material/StorefrontRounded";
import TimelineRoundedIcon from "@mui/icons-material/TimelineRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import { Grid } from "@mui/material";

import type { AgeAnalysisFilterFormValues, AgeAnalysisResponse } from "../../types/dashboard";
import { formatInteger, formatPercent, getDominantAgeRangeLabel } from "../../utils/ageAnalysis";
import { KpiCard } from "./KpiCard";

type AgeAnalysisKpiGridProps = {
  data: AgeAnalysisResponse;
  eventosTotal: number;
  appliedFilters: AgeAnalysisFilterFormValues;
};

const KPI_TOOLTIP_COPY = {
  baseTotal: "Volume consolidado de vinculos lead-evento no filtro atual.",
  baseComIdade: "Quantidade de vinculos com data de nascimento suficiente para calcular a idade.",
  baseBbCoberta: "Quantidade de vinculos com informacao BB preenchida no cruzamento atual.",
  canal: "Distribuicao de vinculos por classificacao de canal: proponente, ativacao ou nao classificado.",
  faixa1840: "Soma das faixas 18-25 e 26-40. Percentual sempre comunicado sobre a base com idade.",
  fora1840: "Leads fora de 18 a 40 anos dentro da base com idade conhecida.",
  naoCliente: "Nao clientes BB so aparecem quando a cobertura BB atinge o limiar minimo.",
  faixaDominante: "Faixa com maior volume na base consolidada. Em empate, trate como sinal fraco.",
} as const;

function formatOptionalMetric(value: number | null, pct: number | null) {
  if (value === null || pct === null) return "Oculto por cobertura";
  return `${formatInteger(value)} (${formatPercent(pct)})`;
}

function getDominantRangeTitle(data: AgeAnalysisResponse) {
  if (data.consolidado.faixa_dominante_status === "tied") {
    return "Empate tecnico";
  }

  const topEvento = data.consolidado.top_eventos[0];
  if (topEvento) {
    return getDominantAgeRangeLabel(topEvento.faixa_dominante);
  }

  return getDominantAgeRangeLabel("sem_info");
}

export function AgeAnalysisKpiGrid({ data, eventosTotal, appliedFilters }: AgeAnalysisKpiGridProps) {
  const consolidated = data.consolidado;
  const fx = consolidated.faixas;
  const canalDesconhecidoPct =
    consolidated.base_total > 0
      ? (consolidated.leads_canal_desconhecido / consolidated.base_total) * 100
      : 0;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Base total"
          value={formatInteger(consolidated.base_total)}
          subtitle="Vinculos lead-evento no filtro."
          helperText={`Gerado em ${new Date(data.generated_at).toLocaleString("pt-BR")}`}
          titleTooltip={KPI_TOOLTIP_COPY.baseTotal}
          icon={<GroupsRoundedIcon fontSize="small" />}
          ariaLabel="Base total de vinculos lead-evento"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Base com idade"
          value={`${formatInteger(consolidated.base_com_idade_volume)} (${formatPercent(
            (consolidated.base_com_idade_volume / Math.max(consolidated.base_total, 1)) * 100,
          )})`}
          subtitle="Sobre vinculos consolidados."
          helperText={`Referencia etaria: ${new Date(data.age_reference_date).toLocaleDateString("pt-BR")}`}
          titleTooltip={KPI_TOOLTIP_COPY.baseComIdade}
          icon={<TimelineRoundedIcon fontSize="small" />}
          ariaLabel="Base consolidada com idade conhecida"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Base BB coberta"
          value={`${formatInteger(consolidated.base_bb_coberta_volume)} (${formatPercent(
            consolidated.cobertura_bb_pct,
          )})`}
          subtitle="Sobre vinculos consolidados."
          helperText={`BB indefinido: ${formatInteger(consolidated.bb_indefinido_volume)}`}
          titleTooltip={KPI_TOOLTIP_COPY.baseBbCoberta}
          icon={<VerifiedRoundedIcon fontSize="small" />}
          ariaLabel="Base consolidada com cobertura BB"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Proponente"
          value={formatInteger(consolidated.leads_proponente)}
          subtitle="Bilheteria e entrada_evento sobre vinculos."
          titleTooltip={KPI_TOOLTIP_COPY.canal}
          icon={<StorefrontRoundedIcon fontSize="small" />}
          ariaLabel="Total de vinculos do proponente"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Ativacao"
          value={formatInteger(consolidated.leads_ativacao)}
          subtitle="Captacao classificada como ativacao."
          titleTooltip={KPI_TOOLTIP_COPY.canal}
          icon={<CampaignRoundedIcon fontSize="small" />}
          ariaLabel="Total de vinculos da ativacao"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Canal nao classificado"
          value={`${formatInteger(consolidated.leads_canal_desconhecido)} (${formatPercent(canalDesconhecidoPct)})`}
          subtitle="Sobre vinculos consolidados."
          titleTooltip={KPI_TOOLTIP_COPY.canal}
          icon={<RuleRoundedIcon fontSize="small" />}
          ariaLabel="Total de vinculos sem classificacao de canal"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="18 a 40 anos"
          value={`${formatInteger(fx.faixa_18_40.volume)} (${formatPercent(fx.faixa_18_40.pct)})`}
          subtitle="Sobre base com idade."
          titleTooltip={KPI_TOOLTIP_COPY.faixa1840}
          icon={<TimelineRoundedIcon fontSize="small" />}
          ariaLabel="Leads na faixa etaria de 18 a 40 anos"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Fora de 18-40"
          value={`${formatInteger(fx.fora_18_40.volume)} (${formatPercent(fx.fora_18_40.pct)})`}
          subtitle="Sobre base com idade."
          titleTooltip={KPI_TOOLTIP_COPY.fora1840}
          icon={<InsightsRoundedIcon fontSize="small" />}
          ariaLabel="Leads fora da faixa de 18 a 40 anos com idade conhecida"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Clientes BB"
          value={formatOptionalMetric(consolidated.clientes_bb_volume, consolidated.clientes_bb_pct)}
          subtitle="Percentual sobre vinculos; pode ser ocultado."
          helperText={`Base BB coberta: ${formatInteger(consolidated.base_bb_coberta_volume)}`}
          icon={<VerifiedRoundedIcon fontSize="small" />}
          progressValue={consolidated.cobertura_bb_pct}
          progressLabel="Cobertura BB"
          ariaLabel="Quantidade de clientes BB"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Nao clientes BB"
          value={formatOptionalMetric(consolidated.nao_clientes_bb_volume, consolidated.nao_clientes_bb_pct)}
          subtitle="Percentual sobre vinculos; pode ser ocultado."
          titleTooltip={KPI_TOOLTIP_COPY.naoCliente}
          helperText={
            consolidated.nao_clientes_bb_volume === null
              ? "Oculto quando a cobertura BB fica abaixo do limiar."
              : `Base BB coberta: ${formatInteger(consolidated.base_bb_coberta_volume)}`
          }
          icon={<PersonOffRoundedIcon fontSize="small" />}
          ariaLabel="Quantidade de nao clientes BB"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
        <KpiCard
          title="Faixa dominante"
          value={getDominantRangeTitle(data)}
          titleTooltip={KPI_TOOLTIP_COPY.faixaDominante}
          subtitle={
            consolidated.faixa_dominante_status === "tied"
              ? "Empate entre faixas na base consolidada."
              : "Predominante na base consolidada."
          }
          helperText={
            data.consolidado.top_eventos[0]
              ? `Evento lider: ${data.consolidado.top_eventos[0].evento_nome}`
              : "Sem evento lider no filtro."
          }
          icon={<AccountBalanceRoundedIcon fontSize="small" />}
          ariaLabel="Faixa etaria dominante"
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4} xl={3}>
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
          ariaLabel="Quantidade de eventos no filtro"
        />
      </Grid>
    </Grid>
  );
}
