import { Box, Card, CardContent, ToggleButton, ToggleButtonGroup, Typography, useTheme } from "@mui/material";
import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";

import type { EventoAgeAnalysis } from "../../types/dashboard";
import { formatInteger, formatPercent, truncateLabel } from "../../utils/ageAnalysis";

type ChannelMixChartProps = {
  events: EventoAgeAnalysis[];
};

type ChannelChartMode = "pct" | "volume";

const X_AXIS_MAX = 16;
const CHART_HEIGHT = 280;

function pctPart(part: number, total: number) {
  if (total <= 0) return 0;
  return Math.round((part / total) * 100 * 100) / 100;
}

export function ChannelMixChart({ events }: ChannelMixChartProps) {
  const theme = useTheme();
  const [mode, setMode] = useState<ChannelChartMode>("pct");
  const data = useMemo(
    () =>
      events.map((event) => ({
        nome: truncateLabel(event.evento_nome, X_AXIS_MAX),
        nomeCompleto: event.evento_nome,
        proponente_volume: event.leads_proponente,
        ativacao_volume: event.leads_ativacao,
        sem_canal_volume: event.leads_canal_desconhecido,
        proponente_pct: pctPart(event.leads_proponente, event.base_leads),
        ativacao_pct: pctPart(event.leads_ativacao, event.base_leads),
        sem_canal_pct: pctPart(event.leads_canal_desconhecido, event.base_leads),
      })),
    [events],
  );

  if (data.length === 0) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle1" fontWeight={800}>
            Mix de canal
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Nenhum evento para exibir.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const axisTick = { fill: theme.palette.text.secondary, fontSize: 12 };

  return (
    <Card variant="outlined" component="section" aria-label="Grafico de vinculos por canal">
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            gap: 2,
            alignItems: { xs: "flex-start", md: "center" },
            flexDirection: { xs: "column", md: "row" },
            mb: 2,
          }}
        >
          <Box>
            <Typography variant="subtitle1" fontWeight={800}>
              Mix de canal por evento
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Composicao relativa por canal na base total do evento, com alternancia para volume absoluto.
            </Typography>
          </Box>
          <ToggleButtonGroup
            size="small"
            value={mode}
            exclusive
            onChange={(_, value: ChannelChartMode | null) => {
              if (value) setMode(value);
            }}
            aria-label="Modo do grafico de canal"
          >
            <ToggleButton value="pct">Composicao</ToggleButton>
            <ToggleButton value="volume">Volume</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        <Box sx={{ width: "100%", overflowX: "auto" }}>
          <BarChart
            width={Math.max(480, data.length * 96)}
            height={CHART_HEIGHT}
            data={data}
            margin={{ top: 8, right: 16, left: 8, bottom: 8 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke={theme.palette.divider}
            />
            <XAxis
              dataKey="nome"
              interval={0}
              tickMargin={8}
              tick={axisTick}
              stroke={theme.palette.divider}
            />
            <YAxis
              allowDecimals={mode === "pct"}
              width={56}
              domain={mode === "pct" ? [0, 100] : undefined}
              tick={axisTick}
              stroke={theme.palette.divider}
              label={{
                value: mode === "pct" ? "% da base total" : "Vinculos",
                angle: -90,
                position: "insideLeft",
                fill: theme.palette.text.secondary,
                fontSize: 12,
              }}
            />
            <Tooltip
              formatter={(value, key, item) => {
                const numericValue = Number(value ?? 0);
                const row = item?.payload as Record<string, number> | undefined;
                if (mode === "pct") {
                  const dataKey = String(key ?? "");
                  const volumeKey = dataKey.replace("_pct", "_volume") as
                    | "proponente_volume"
                    | "ativacao_volume"
                    | "sem_canal_volume";
                  const volume = Number(row?.[volumeKey] ?? 0);
                  return [`${formatPercent(numericValue)} • ${formatInteger(volume)}`, ""];
                }
                const dataKey = String(key ?? "");
                const pctKey = dataKey.replace("_volume", "_pct") as
                  | "proponente_pct"
                  | "ativacao_pct"
                  | "sem_canal_pct";
                const pct = Number(row?.[pctKey] ?? 0);
                return [`${formatInteger(numericValue)} • ${formatPercent(pct)}`, ""];
              }}
              labelFormatter={(_, payload) => {
                const row = payload?.[0]?.payload as { nomeCompleto?: string } | undefined;
                return row?.nomeCompleto ?? "";
              }}
            />
            <Legend wrapperStyle={{ color: theme.palette.text.secondary, fontSize: 12 }} />
            <Bar
              dataKey={mode === "pct" ? "proponente_pct" : "proponente_volume"}
              stackId="canal"
              fill="#1565c0"
              name="Proponente"
            />
            <Bar
              dataKey={mode === "pct" ? "ativacao_pct" : "ativacao_volume"}
              stackId="canal"
              fill="#2e7d32"
              name="Ativacao"
            />
            <Bar
              dataKey={mode === "pct" ? "sem_canal_pct" : "sem_canal_volume"}
              stackId="canal"
              fill="#9e9e9e"
              name="Canal nao classificado"
            />
          </BarChart>
        </Box>
      </CardContent>
    </Card>
  );
}
