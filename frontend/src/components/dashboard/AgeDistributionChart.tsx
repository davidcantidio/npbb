import { Box, Card, CardContent, Typography } from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { EventoAgeAnalysis } from "../../types/dashboard";
import {
  AGE_RANGE_META,
  formatInteger,
  formatPercent,
  getAgeBreakdownPercent,
  truncateLabel,
} from "../../utils/ageAnalysis";

type AgeDistributionChartProps = {
  events: EventoAgeAnalysis[];
};

type ChartRow = {
  eventoId: number;
  eventoNome: string;
  eventoNomeCurto: string;
  faixa_18_25: number;
  faixa_26_40: number;
  fora_18_40: number;
  sem_info: number;
  faixa_18_25_pct: number;
  faixa_26_40_pct: number;
  fora_18_40_pct: number;
  sem_info_pct: number;
};

function buildChartData(events: EventoAgeAnalysis[]): ChartRow[] {
  return events.map((event) => ({
    eventoId: event.evento_id,
    eventoNome: event.evento_nome,
    eventoNomeCurto: truncateLabel(event.evento_nome, 18),
    faixa_18_25: event.faixas.faixa_18_25.volume,
    faixa_26_40: event.faixas.faixa_26_40.volume,
    fora_18_40: event.faixas.fora_18_40.volume,
    sem_info: event.faixas.sem_info_volume,
    faixa_18_25_pct: getAgeBreakdownPercent(event.faixas, "faixa_18_25"),
    faixa_26_40_pct: getAgeBreakdownPercent(event.faixas, "faixa_26_40"),
    fora_18_40_pct: getAgeBreakdownPercent(event.faixas, "fora_18_40"),
    sem_info_pct: getAgeBreakdownPercent(event.faixas, "sem_info"),
  }));
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ dataKey?: string; value?: number; payload?: ChartRow }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;
  if (!row) return null;

  const sections: Array<{
    key: "faixa_18_25" | "faixa_26_40" | "fora_18_40" | "sem_info";
    value: number;
    pct: number;
  }> = [
    { key: "faixa_18_25", value: row.faixa_18_25, pct: row.faixa_18_25_pct },
    { key: "faixa_26_40", value: row.faixa_26_40, pct: row.faixa_26_40_pct },
    { key: "fora_18_40", value: row.fora_18_40, pct: row.fora_18_40_pct },
    { key: "sem_info", value: row.sem_info, pct: row.sem_info_pct },
  ];

  return (
    <Box sx={{ bgcolor: "background.paper", border: 1, borderColor: "divider", p: 1.5, borderRadius: 2 }}>
      <Typography variant="subtitle2" fontWeight={800}>
        {row.eventoNome}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      {sections.map((section) => (
        <Box key={section.key} sx={{ display: "flex", justifyContent: "space-between", gap: 2, mt: 0.75 }}>
          <Typography variant="caption">{AGE_RANGE_META[section.key].label}</Typography>
          <Typography variant="caption" fontWeight={700}>
            {formatInteger(section.value)} • {formatPercent(section.pct)}
          </Typography>
        </Box>
      ))}
    </Box>
  );
}

export function AgeDistributionChart({ events }: AgeDistributionChartProps) {
  const data = buildChartData(events);
  const minWidth = Math.max(720, data.length * 110);

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="subtitle1" fontWeight={800}>
          Distribuicao etaria por evento
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Cada barra representa um evento. As cores seguem a mesma legenda usada no restante da analise.
        </Typography>

        {data.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Nenhum evento disponivel para exibir no grafico.
          </Typography>
        ) : (
          <Box sx={{ overflowX: "auto", overflowY: "hidden" }}>
            <Box sx={{ width: minWidth, height: 360 }}>
              <BarChart width={minWidth} height={360} data={data} margin={{ top: 8, right: 24, left: 0, bottom: 12 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="eventoNomeCurto" interval={0} tickMargin={10} />
                <YAxis allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar
                  dataKey="faixa_18_25"
                  stackId="idade"
                  fill={AGE_RANGE_META.faixa_18_25.color}
                  name={AGE_RANGE_META.faixa_18_25.label}
                />
                <Bar
                  dataKey="faixa_26_40"
                  stackId="idade"
                  fill={AGE_RANGE_META.faixa_26_40.color}
                  name={AGE_RANGE_META.faixa_26_40.label}
                />
                <Bar
                  dataKey="fora_18_40"
                  stackId="idade"
                  fill={AGE_RANGE_META.fora_18_40.color}
                  name={AGE_RANGE_META.fora_18_40.label}
                />
                <Bar
                  dataKey="sem_info"
                  stackId="idade"
                  fill={AGE_RANGE_META.sem_info.color}
                  name={AGE_RANGE_META.sem_info.label}
                />
              </BarChart>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
