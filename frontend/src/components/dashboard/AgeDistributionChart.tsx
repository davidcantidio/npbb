import { Box, Card, CardContent, Typography } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
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

const X_AXIS_MAX_LABEL_LENGTH = 18;
const CHART_MIN_WIDTH = 720;
const CHART_WIDTH_PER_EVENT = 110;
const HORIZONTAL_SCROLL_THRESHOLD = 10;
const CHART_HEIGHT_MIN = 260;
const CHART_HEIGHT_MAX = 420;
const CHART_HEIGHT_VIEWPORT_RATIO = 0.42;
const VIEWPORT_WIDTH_PADDING = 96;

type ViewportSize = {
  width: number;
  height: number;
};

function getViewportSize(): ViewportSize {
  if (typeof window === "undefined") {
    return { width: 1280, height: 900 };
  }

  return { width: window.innerWidth, height: window.innerHeight };
}

export function getResponsiveChartHeight(viewportHeight: number) {
  const estimatedHeight = Math.round(viewportHeight * CHART_HEIGHT_VIEWPORT_RATIO);
  return Math.min(CHART_HEIGHT_MAX, Math.max(CHART_HEIGHT_MIN, estimatedHeight));
}

export function buildChartData(events: EventoAgeAnalysis[]): ChartRow[] {
  return events.map((event) => ({
    eventoId: event.evento_id,
    eventoNome: event.evento_nome,
    eventoNomeCurto: truncateLabel(event.evento_nome, X_AXIS_MAX_LABEL_LENGTH),
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

export function CustomTooltip({
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
  const data = useMemo(() => buildChartData(events), [events]);
  const [viewportSize, setViewportSize] = useState<ViewportSize>(() => getViewportSize());

  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleResize = () => {
      setViewportSize(getViewportSize());
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const shouldEnableHorizontalScroll = data.length > HORIZONTAL_SCROLL_THRESHOLD;
  const nonScrollableWidth = Math.max(
    Math.min(viewportSize.width - VIEWPORT_WIDTH_PADDING, 1200),
    320,
  );
  const chartWidth = shouldEnableHorizontalScroll
    ? Math.max(CHART_MIN_WIDTH, data.length * CHART_WIDTH_PER_EVENT)
    : nonScrollableWidth;
  const chartHeight = getResponsiveChartHeight(viewportSize.height);

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
          <Box
            data-testid="age-distribution-chart-scroll"
            data-scroll-enabled={shouldEnableHorizontalScroll ? "true" : "false"}
            sx={{ overflowX: shouldEnableHorizontalScroll ? "auto" : "hidden", overflowY: "hidden" }}
          >
            <Box
              data-testid="age-distribution-chart-canvas"
              data-chart-height={chartHeight}
              data-chart-width={chartWidth}
              sx={{ width: chartWidth, height: chartHeight }}
            >
              <BarChart
                width={chartWidth}
                height={chartHeight}
                data={data}
                margin={{ top: 8, right: 24, left: 0, bottom: 12 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="eventoNomeCurto" interval={0} tickMargin={10} />
                <YAxis allowDecimals={false} width={80} label={{ value: "Volume de leads", angle: -90 }} />
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
