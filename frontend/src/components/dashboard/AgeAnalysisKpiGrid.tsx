import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import PersonOffRoundedIcon from "@mui/icons-material/PersonOffRounded";
import TimelineRoundedIcon from "@mui/icons-material/TimelineRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import { Box, Grid, Stack } from "@mui/material";

import type { AgeAnalysisResponse } from "../../types/dashboard";
import { formatInteger, formatPercent } from "../../utils/ageAnalysis";
import { KpiCard } from "./KpiCard";

type AgeAnalysisKpiGridProps = {
  data: AgeAnalysisResponse;
};

const T_LEADS = "Quantidade de vinculos com data de nascimento suficiente para calcular a idade.";

function optionalFaixa(
  vol: number | null | undefined,
  pct: number | null | undefined,
  hiddenLabel: string,
) {
  if (vol == null || pct == null) return { value: hiddenLabel, ok: false as const };
  return { value: `${formatInteger(vol)} (${formatPercent(pct)})`, ok: true as const };
}

export function AgeAnalysisKpiGrid({ data }: AgeAnalysisKpiGridProps) {
  const c = data.consolidado;
  const f1840c = optionalFaixa(
    c.clientes_bb_faixa_18_40_volume,
    c.clientes_bb_faixa_18_40_pct,
    "Oculto por cobertura BB",
  );
  const foraC = optionalFaixa(
    c.clientes_bb_fora_18_40_volume,
    c.clientes_bb_fora_18_40_pct,
    "Oculto por cobertura BB",
  );
  const f1840n = optionalFaixa(
    c.nao_clientes_bb_faixa_18_40_volume,
    c.nao_clientes_bb_faixa_18_40_pct,
    "Oculto por cobertura BB",
  );
  const foraN = optionalFaixa(
    c.nao_clientes_bb_fora_18_40_volume,
    c.nao_clientes_bb_fora_18_40_pct,
    "Oculto por cobertura BB",
  );

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <KpiCard
          title="Leads válidos"
          value={`${formatInteger(c.base_com_idade_volume)} (${formatPercent(
            (c.base_com_idade_volume / Math.max(c.base_total, 1)) * 100,
          )})`}
          contentAlign="center"
          titleTooltip={T_LEADS}
          icon={<TimelineRoundedIcon fontSize="small" />}
          ariaLabel="Leads com idade conhecida no filtro"
        />
      </Grid>

      <Grid item xs={12}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <KpiCard
                title="Clientes BB"
                value={
                  c.clientes_bb_volume == null
                    ? "Oculto por cobertura"
                    : `${formatInteger(c.clientes_bb_volume)} (${formatPercent(c.clientes_bb_pct ?? 0)})`
                }
                subtitle="Sobre vinculos consolidados."
                contentAlign="center"
                icon={<VerifiedRoundedIcon fontSize="small" />}
                ariaLabel="Total de vinculos classificados como clientes BB"
              />
              <Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <KpiCard
                      title="18 a 40 anos"
                      value={f1840c.value}
                      subtitle={
                        f1840c.ok
                          ? "Sobre base com idade (de clientes BB)."
                          : "Dados nao exibidos quando a cobertura BB esta abaixo do limiar."
                      }
                      contentAlign="center"
                      icon={<TimelineRoundedIcon fontSize="small" />}
                      ariaLabel="Clientes BB entre 18 e 40 anos com idade conhecida"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <KpiCard
                      title="Fora de 18-40"
                      value={foraC.value}
                      subtitle={
                        foraC.ok
                          ? "Sobre base com idade (de clientes BB)."
                          : "Dados nao exibidos quando a cobertura BB esta abaixo do limiar."
                      }
                      contentAlign="center"
                      icon={<InsightsRoundedIcon fontSize="small" />}
                      ariaLabel="Clientes BB fora da faixa 18-40 com idade conhecida"
                    />
                  </Grid>
                </Grid>
              </Box>
            </Stack>
          </Grid>

          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <KpiCard
                title="Nao clientes BB"
                value={
                  c.nao_clientes_bb_volume == null
                    ? "Oculto por cobertura"
                    : `${formatInteger(c.nao_clientes_bb_volume)} (${formatPercent(c.nao_clientes_bb_pct ?? 0)})`
                }
                subtitle="Sobre vinculos consolidados."
                contentAlign="center"
                titleTooltip="Nao clientes BB so aparecem quando a cobertura BB atinge o limiar minimo."
                icon={<PersonOffRoundedIcon fontSize="small" />}
                ariaLabel="Total de vinculos classificados como nao clientes BB"
              />
              <Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <KpiCard
                      title="18 a 40 anos"
                      value={f1840n.value}
                      subtitle={
                        f1840n.ok
                          ? "Sobre base com idade (de nao clientes BB)."
                          : "Dados nao exibidos quando a cobertura BB esta abaixo do limiar."
                      }
                      contentAlign="center"
                      icon={<TimelineRoundedIcon fontSize="small" />}
                      ariaLabel="Nao clientes BB entre 18 e 40 anos com idade conhecida"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <KpiCard
                      title="Fora de 18-40"
                      value={foraN.value}
                      subtitle={
                        foraN.ok
                          ? "Sobre base com idade (de nao clientes BB)."
                          : "Dados nao exibidos quando a cobertura BB esta abaixo do limiar."
                      }
                      contentAlign="center"
                      icon={<InsightsRoundedIcon fontSize="small" />}
                      ariaLabel="Nao clientes BB fora da faixa 18-40 com idade conhecida"
                    />
                  </Grid>
                </Grid>
              </Box>
            </Stack>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
