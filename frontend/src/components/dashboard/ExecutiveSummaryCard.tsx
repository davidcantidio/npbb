import { Alert, Card, CardContent, Stack, Typography } from "@mui/material";

import type { AgeAnalysisInsights } from "../../types/dashboard";

type ExecutiveSummaryCardProps = {
  insights: AgeAnalysisInsights;
  highlights?: string[];
};

export function ExecutiveSummaryCard({ insights, highlights = [] }: ExecutiveSummaryCardProps) {
  return (
    <Card variant="outlined" component="section" aria-label="Leitura dos resultados">
      <CardContent>
        <Typography variant="subtitle1" fontWeight={800} sx={{ mb: 1.5 }}>
          Leitura dos resultados
        </Typography>
        {highlights.length > 0 ? (
          <Stack spacing={1} sx={{ mb: 2 }}>
            {highlights.map((line) => (
              <Alert key={line} severity="info" variant="outlined">
                {line}
              </Alert>
            ))}
          </Stack>
        ) : null}
        <Stack component="ul" spacing={1} sx={{ m: 0, pl: 2.5, listStyle: "disc" }}>
          {insights.resumo.map((line) => (
            <Typography key={line} component="li" variant="body2" color="text.primary">
              {line}
            </Typography>
          ))}
        </Stack>
        {insights.alertas.length > 0 ? (
          <Stack spacing={1} sx={{ mt: 2 }}>
            {insights.alertas.map((alerta) => (
              <Alert key={alerta} severity="warning" variant="outlined">
                {alerta}
              </Alert>
            ))}
          </Stack>
        ) : null}
      </CardContent>
    </Card>
  );
}
