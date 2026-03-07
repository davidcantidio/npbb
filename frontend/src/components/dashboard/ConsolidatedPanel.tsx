import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";

import type { ConsolidadoAgeAnalysis } from "../../types/dashboard";
import { formatDecimal, formatInteger, formatPercent, getDominantAgeRangeLabel } from "../../utils/ageAnalysis";

type ConsolidatedPanelProps = {
  data: ConsolidadoAgeAnalysis;
};

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
        <Tooltip title={tooltip}>
          <InfoOutlinedIcon sx={{ fontSize: 14, color: "text.secondary" }} />
        </Tooltip>
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
                        {index + 1}º {evento.evento_nome}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Faixa dominante: {getDominantAgeRangeLabel(evento.faixa_dominante)}
                      </Typography>
                    </Box>
                    <Chip
                      label={`${formatInteger(evento.base_leads)} • ${formatPercent(
                        data.base_total > 0 ? (evento.base_leads / data.base_total) * 100 : 0,
                      )}`}
                      size="small"
                      variant="outlined"
                    />
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
                    tooltip="Soma total dividida pela quantidade de eventos."
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <StatWithTooltip
                    label="Mediana por evento"
                    value={formatDecimal(data.mediana_por_evento)}
                    tooltip="Valor central ao ordenar eventos por volume."
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Concentracao Top 3
                    </Typography>
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
