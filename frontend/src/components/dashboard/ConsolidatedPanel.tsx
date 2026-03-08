import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Stack,
  Typography,
} from "@mui/material";

import type { ConsolidadoAgeAnalysis } from "../../types/dashboard";
import { formatDecimal, formatInteger, formatPercent, getDominantAgeRangeLabel } from "../../utils/ageAnalysis";
import { InfoTooltip } from "./InfoTooltip";

type ConsolidatedPanelProps = {
  data: ConsolidadoAgeAnalysis;
};

const TOOLTIP_COPY = {
  dominantRange: "Faixa etária com maior volume de leads neste evento",
  average: "Soma dos volumes dividida pela quantidade de eventos",
  median:
    "Volume central quando os eventos são ordenados por tamanho. Quando poucos eventos são muito grandes, a mediana é mais representativa do tamanho típico.",
  top3: "Percentual da base total representada pelos 3 maiores eventos",
} as const;

function formatRoundedInteger(value: number) {
  return formatInteger(Math.round(value));
}

function StatWithTooltip({
  label,
  value,
  tooltip,
}: {
  label: string;
  value: string;
  tooltip: string;
}) {
  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <InfoTooltip label={label} description={tooltip} />
      </Box>
      <Typography variant="h6" fontWeight={800}>
        {value}
      </Typography>
    </Box>
  );
}

export function ConsolidatedPanel({ data }: ConsolidatedPanelProps) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <Stack spacing={1.5}>
              <Typography variant="subtitle1" fontWeight={800}>
                Top 3 eventos por volume
              </Typography>
              {data.top_eventos.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Nenhum evento encontrado para os filtros aplicados.
                </Typography>
              ) : (
                data.top_eventos.map((evento, index) => (
                  <Box
                    key={evento.evento_id}
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: 2,
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: "grey.50",
                    }}
                  >
                    <Box sx={{ minWidth: 0 }}>
                      <Typography variant="body2" fontWeight={700} noWrap>
                        {index + 1}
                        {"\u00BA"} {evento.evento_nome}
                      </Typography>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          Faixa dominante: {getDominantAgeRangeLabel(evento.faixa_dominante)}
                        </Typography>
                        <InfoTooltip
                          label="Faixa dominante"
                          description={TOOLTIP_COPY.dominantRange}
                        />
                      </Box>
                    </Box>
                    <Stack alignItems="flex-end" spacing={0.25}>
                      <Chip label={formatInteger(evento.base_leads)} size="small" variant="outlined" />
                      <Typography variant="caption" color="text.secondary">
                        {formatPercent(
                          data.base_total > 0 ? (evento.base_leads / data.base_total) * 100 : 0,
                        )}
                      </Typography>
                    </Stack>
                  </Box>
                ))
              )}
            </Stack>
          </Grid>

          <Grid item xs={12} lg={6}>
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={800}>
                Estatisticas consolidadas
              </Typography>
              <Divider />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <StatWithTooltip
                    label="Media por evento"
                    value={formatDecimal(data.media_por_evento)}
                    tooltip={TOOLTIP_COPY.average}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <StatWithTooltip
                    label="Mediana por evento"
                    value={formatRoundedInteger(data.mediana_por_evento)}
                    tooltip={TOOLTIP_COPY.median}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
                      <Typography variant="caption" color="text.secondary">
                        Concentracao Top 3
                      </Typography>
                      <InfoTooltip
                        label="Concentracao Top 3"
                        description={TOOLTIP_COPY.top3}
                      />
                    </Box>
                    <Typography variant="h6" fontWeight={800}>
                      {formatPercent(data.concentracao_top3_pct)}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Stack>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
