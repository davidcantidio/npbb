import { Box, Card, CardContent, ToggleButton, ToggleButtonGroup, Typography, useTheme } from "@mui/material";
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";

import type { EventoAgeAnalysis } from "../../types/dashboard";
import { AGE_RANGE_META, formatInteger, formatPercent, truncateLabel } from "../../utils/ageAnalysis";

type AgeDistributionChartProps = {
  events: EventoAgeAnalysis[];
};

export type AgeChartMode = "pct" | "volume";

type ChartRow = {
  eventoId: number;
  eventoNome: string;
  eventoNomeCurto: string;
  faixa_18_25_volume: number;
  faixa_26_40_volume: number;
  fora_18_40_volume: number;
  sem_info_volume: number;
  faixa_18_25_pct_total: number;
  faixa_26_40_pct_total: number;
  fora_18_40_pct_total: number;
  sem_info_pct_total: number;
};

const X_AXIS_MAX_LABEL_LENGTH = 18;
const CHART_MIN_WIDTH = 720;
const CHART_WIDTH_PER_EVENT = 110;
const HORIZONTAL_SCROLL_THRESHOLD = 10;
const CHART_HEIGHT_MIN = 260;
const CHART_HEIGHT_MAX = 420;
const CHART_HEIGHT_VIEWPORT_RATIO = 0.42;
const VIEWPORT_WIDTH_PADDING = 96;
/** Alinha com `DRAWER_WIDTH` em AppLayout — fallback antes do ResizeObserver medir a coluna. */
const LAYOUT_DRAWER_WIDTH_ESTIMATE = 240;

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

function pctPart(part: number, total: number) {
  if (total <= 0) return 0;
  return Math.round((part / total) * 100 * 100) / 100;
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
    faixa_18_25_volume: event.faixas.faixa_18_25.volume,
    faixa_26_40_volume: event.faixas.faixa_26_40.volume,
    fora_18_40_volume: event.faixas.fora_18_40.volume,
    sem_info_volume: event.faixas.sem_info_volume,
    faixa_18_25_pct_total: pctPart(event.faixas.faixa_18_25.volume, event.base_leads),
    faixa_26_40_pct_total: pctPart(event.faixas.faixa_26_40.volume, event.base_leads),
    fora_18_40_pct_total: pctPart(event.faixas.fora_18_40.volume, event.base_leads),
    sem_info_pct_total: pctPart(event.faixas.sem_info_volume, event.base_leads),
  }));
}

export function CustomTooltip({
  active,
  payload,
  label,
  mode = "pct",
}: {
  active?: boolean;
  payload?: Array<{ payload?: ChartRow }>;
  label?: string;
  mode?: AgeChartMode;
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;
  if (!row) return null;

  const sections: Array<{
    key: "faixa_18_25" | "faixa_26_40" | "fora_18_40" | "sem_info";
    volume: number;
    pct: number;
  }> = [
    { key: "faixa_18_25", volume: row.faixa_18_25_volume, pct: row.faixa_18_25_pct_total },
    { key: "faixa_26_40", volume: row.faixa_26_40_volume, pct: row.faixa_26_40_pct_total },
    { key: "fora_18_40", volume: row.fora_18_40_volume, pct: row.fora_18_40_pct_total },
    { key: "sem_info", volume: row.sem_info_volume, pct: row.sem_info_pct_total },
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
            {mode === "pct"
              ? `${formatPercent(section.pct)} • ${formatInteger(section.volume)}`
              : `${formatInteger(section.volume)} • ${formatPercent(section.pct)}`}
          </Typography>
        </Box>
      ))}
    </Box>
  );
}

export function AgeDistributionChart({ events }: AgeDistributionChartProps) {
  const theme = useTheme();
  const data = useMemo(() => buildChartData(events), [events]);
  const [mode, setMode] = useState<AgeChartMode>("pct");
  const [viewportSize, setViewportSize] = useState<ViewportSize>(() => getViewportSize());
  const [containerWidth, setContainerWidth] = useState(0);
  const chartHostRef = useRef<HTMLDivElement>(null);

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

  useLayoutEffect(() => {
    if (typeof window === "undefined" || data.length === 0) return;

    const el = chartHostRef.current;
    if (!el) return;

    const applyWidth = (width: number) => {
      const rounded = Math.round(width);
      if (rounded <= 0) return;
      setContainerWidth((prev) => (prev === rounded ? prev : rounded));
    };

    // jsdom: larguras instáveis com Recharts; testes usam largura fixa coerente com o viewport mockado.
    if (import.meta.env.VITEST) {
      applyWidth(960);
      return;
    }

    applyWidth(el.getBoundingClientRect().width);

    if (typeof ResizeObserver === "undefined") return;

    const ro = new ResizeObserver((entries) => {
      applyWidth(entries[0]?.contentRect.width ?? 0);
    });
    ro.observe(el);

    return () => {
      ro.disconnect();
    };
  }, [data.length]);

  const shouldEnableHorizontalScroll = data.length > HORIZONTAL_SCROLL_THRESHOLD;
  const measuredWidth =
    containerWidth > 0
      ? containerWidth
      : Math.max(
          viewportSize.width - VIEWPORT_WIDTH_PADDING - LAYOUT_DRAWER_WIDTH_ESTIMATE,
          320,
        );
  const nonScrollableWidth = Math.max(Math.min(measuredWidth, 1200), 320);
  const chartWidth = shouldEnableHorizontalScroll
    ? Math.max(CHART_MIN_WIDTH, data.length * CHART_WIDTH_PER_EVENT)
    : nonScrollableWidth;
  const chartHeight = getResponsiveChartHeight(viewportSize.height);
  const yAxisLabel = mode === "pct" ? "% da base total" : "Vinculos";

  const axisTick = { fill: theme.palette.text.secondary, fontSize: 12 };

  return (
    <Card variant="outlined" component="section" aria-label="Grafico de distribuicao etaria">
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
              Distribuicao etaria por evento
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Composicao por faixa etaria sobre a base total do evento, com alternancia para volume absoluto.
            </Typography>
          </Box>
          <ToggleButtonGroup
            size="small"
            value={mode}
            exclusive
            onChange={(_, value: AgeChartMode | null) => {
              if (value) setMode(value);
            }}
            aria-label="Modo do grafico etario"
          >
            <ToggleButton value="pct">Composicao</ToggleButton>
            <ToggleButton value="volume">Volume</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {data.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Nenhum evento disponivel para exibir no grafico.
          </Typography>
        ) : (
          <Box ref={chartHostRef} sx={{ width: "100%", minWidth: 0 }}>
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
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke={theme.palette.divider}
                  />
                  <XAxis
                    dataKey="eventoNomeCurto"
                    interval={0}
                    tickMargin={10}
                    tick={axisTick}
                    stroke={theme.palette.divider}
                  />
                  <YAxis
                    allowDecimals={mode === "pct"}
                    width={80}
                    domain={mode === "pct" ? [0, 100] : undefined}
                    tick={axisTick}
                    stroke={theme.palette.divider}
                    label={{
                      value: yAxisLabel,
                      angle: -90,
                      position: "insideLeft",
                      fill: theme.palette.text.secondary,
                      fontSize: 12,
                    }}
                  />
                  <Tooltip content={<CustomTooltip mode={mode} />} />
                  <Legend wrapperStyle={{ color: theme.palette.text.secondary, fontSize: 12 }} />
                  <Bar
                    dataKey={mode === "pct" ? "faixa_18_25_pct_total" : "faixa_18_25_volume"}
                    stackId="idade"
                    fill={AGE_RANGE_META.faixa_18_25.color}
                    name={AGE_RANGE_META.faixa_18_25.label}
                  />
                  <Bar
                    dataKey={mode === "pct" ? "faixa_26_40_pct_total" : "faixa_26_40_volume"}
                    stackId="idade"
                    fill={AGE_RANGE_META.faixa_26_40.color}
                    name={AGE_RANGE_META.faixa_26_40.label}
                  />
                  <Bar
                    dataKey={mode === "pct" ? "fora_18_40_pct_total" : "fora_18_40_volume"}
                    stackId="idade"
                    fill={AGE_RANGE_META.fora_18_40.color}
                    name={AGE_RANGE_META.fora_18_40.label}
                  />
                  <Bar
                    dataKey={mode === "pct" ? "sem_info_pct_total" : "sem_info_volume"}
                    stackId="idade"
                    fill={AGE_RANGE_META.sem_info.color}
                    name={AGE_RANGE_META.sem_info.label}
                  />
                </BarChart>
              </Box>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
