import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Box, Card, CardContent, IconButton, Tooltip as MuiTooltip, Typography, useTheme } from "@mui/material";
import { useMemo } from "react";
import { Cell, Legend, Pie, PieChart, Tooltip as RechartsTooltip } from "recharts";
import type { TooltipContentProps } from "recharts";

import type { AgeAnalysisResponse } from "../../types/dashboard";
import { formatInteger, formatPercent } from "../../utils/ageAnalysis";

type ProponenteAtivacaoPieChartProps = {
  data: AgeAnalysisResponse;
};

type SliceRow = { name: string; value: number; fill: string };

function ProponenteAtivacaoTooltip({
  active,
  payload,
  baseTotal,
  sumPa,
}: {
  active?: boolean;
  payload?: ReadonlyArray<{ payload?: SliceRow }>;
  baseTotal: number;
  sumPa: number;
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;
  if (!row) return null;
  const vol = row.value;
  const pctOfPair = sumPa > 0 ? (vol / sumPa) * 100 : 0;
  const pctOfBase = baseTotal > 0 ? (vol / baseTotal) * 100 : 0;
  return (
    <Box
      sx={{
        px: 1.5,
        py: 1,
        bgcolor: "background.paper",
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        boxShadow: 1,
      }}
    >
      <Typography variant="body2" fontWeight={700}>
        {row.name}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {formatInteger(vol)} — {formatPercent(pctOfPair)} de proponente+ativacao; {formatPercent(pctOfBase)} da base
        total
      </Typography>
    </Box>
  );
}

export function ProponenteAtivacaoPieChart({ data }: ProponenteAtivacaoPieChartProps) {
  const theme = useTheme();
  const p = data.consolidado.leads_proponente;
  const a = data.consolidado.leads_ativacao;
  const baseTotal = data.consolidado.base_total;
  const sumPa = p + a;

  const chartData: SliceRow[] = useMemo(
    () => [
      { name: "Proponente", value: p, fill: theme.palette.primary.main },
      { name: "Ativacao", value: a, fill: theme.palette.info.main },
    ],
    [a, p, theme.palette.info.main, theme.palette.primary.main],
  );

  return (
    <Card
      variant="outlined"
      component="section"
      aria-labelledby="pie-proponente-ativacao-heading"
      sx={{
        overflow: "visible",
        flex: 1,
        minHeight: 0,
        width: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <CardContent
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minHeight: 0,
          overflow: "visible",
          "&:last-child": { pb: 2 },
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mb: 2, flexShrink: 0 }}>
          <Typography variant="subtitle1" fontWeight={800} component="h2" id="pie-proponente-ativacao-heading">
            Proponente e ativacao
          </Typography>
          <MuiTooltip
            title="Composicao entre os dois canais; percentuais do grafico sao sobre a soma (proponente + ativacao). Tooltip inclui comparacao com a base total."
            describeChild
          >
            <IconButton
              size="small"
              edge="end"
              aria-label="Explicacao do grafico Proponente e ativacao"
              sx={{ p: 0.25, color: "text.secondary" }}
            >
              <InfoOutlinedIcon fontSize="small" />
            </IconButton>
          </MuiTooltip>
        </Box>
        {sumPa <= 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
            Nenhum vinculo classificado como proponente ou ativacao no recorte.
          </Typography>
        ) : (
          <Box
            sx={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              minHeight: 0,
              width: "100%",
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                width: "100%",
                maxWidth: 380,
                overflow: "visible",
                // Evita corte de rótulos SVG do Recharts
                "& .recharts-surface, & .recharts-wrapper, & .recharts-legend-wrapper": { overflow: "visible" },
              }}
            >
            <PieChart
              width={360}
              height={280}
              margin={{ top: 24, right: 16, bottom: 40, left: 16 }}
            >
              <RechartsTooltip
                content={(props: TooltipContentProps) => (
                  <ProponenteAtivacaoTooltip
                    active={props.active}
                    payload={props.payload as ReadonlyArray<{ payload?: SliceRow }>}
                    baseTotal={baseTotal}
                    sumPa={sumPa}
                  />
                )}
              />
              <Legend
                verticalAlign="bottom"
                align="center"
                wrapperStyle={{ paddingTop: 8 }}
              />
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={48}
                outerRadius={82}
                paddingAngle={2}
                labelLine={false}
                // Só o percentual no anel; nomes completos na legenda (evita overflow com textos longos)
                label={({ percent }) => `${((percent ?? 0) * 100).toFixed(1).replace(".", ",")}%`}
              >
                {chartData.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Pie>
            </PieChart>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
