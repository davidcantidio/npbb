import { Alert, Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";

import type { AgeAnalysisResponse } from "../../types/dashboard";
import { formatInteger, formatPercent } from "../../utils/ageAnalysis";
import type { AgeAnalysisViewModel } from "../../utils/ageAnalysisViewModel";

type ConfidenceSummaryCardProps = {
  data: AgeAnalysisResponse;
  viewModel: AgeAnalysisViewModel;
};

function MetricBlock({
  label,
  value,
  helperText,
}: {
  label: string;
  value: string;
  helperText: string;
}) {
  return (
    <Box
      sx={{
        border: 1,
        borderColor: "divider",
        borderRadius: 2,
        px: 1.5,
        py: 1.25,
        minWidth: 0,
      }}
    >
      <Typography variant="overline" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h6" fontWeight={800}>
        {value}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {helperText}
      </Typography>
    </Box>
  );
}

export function ConfidenceSummaryCard({ data, viewModel }: ConfidenceSummaryCardProps) {
  const quality = data.qualidade_consolidado;
  const confidence = data.confianca_consolidado;

  return (
    <Card variant="outlined" component="section" aria-label="Resumo de confianca e cobertura">
      <CardContent>
        <Stack spacing={2}>
          <Box>
            <Typography variant="subtitle1" fontWeight={800}>
              Confianca e cobertura
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
              Leitura executiva da base consolidada: denominadores, lineage e riscos de merge antes da interpretacao.
            </Typography>
          </Box>

          <Box
            sx={{
              display: "grid",
              gap: 1.5,
              gridTemplateColumns: {
                xs: "minmax(0, 1fr)",
                md: "repeat(3, minmax(0, 1fr))",
              },
            }}
          >
            <MetricBlock
              label="Base consolidada"
              value={formatInteger(confidence.base_vinculos)}
              helperText={`Gerado em ${viewModel.generatedAtLabel}`}
            />
            <MetricBlock
              label="Base com idade"
              value={`${formatInteger(confidence.base_com_idade_volume)} (${formatPercent(
                (confidence.base_com_idade_volume / Math.max(confidence.base_vinculos, 1)) * 100,
              )})`}
              helperText={`Idade de referencia: ${viewModel.ageReferenceLabel}`}
            />
            <MetricBlock
              label="Base BB coberta"
              value={`${formatInteger(confidence.base_bb_coberta_volume)} (${formatPercent(
                data.consolidado.cobertura_bb_pct,
              )})`}
              helperText="Percentual sobre vinculos consolidados."
            />
          </Box>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            <Chip
              label={`Sem CPF: ${formatInteger(quality.sem_cpf_volume)} (${formatPercent(quality.sem_cpf_pct)})`}
              variant="outlined"
            />
            <Chip
              label={`Sem nascimento: ${formatInteger(quality.sem_data_nascimento_volume)} (${formatPercent(
                quality.sem_data_nascimento_pct,
              )})`}
              variant="outlined"
            />
            <Chip
              label={`Sem nome completo: ${formatInteger(quality.sem_nome_completo_volume)} (${formatPercent(
                quality.sem_nome_completo_pct,
              )})`}
              variant="outlined"
            />
          </Stack>

          <Box>
            <Typography variant="body2" fontWeight={700}>
              Lineage consolidada
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {viewModel.lineageSummary}
            </Typography>
          </Box>

          <Box
            sx={{
              display: "grid",
              gap: 1.5,
              gridTemplateColumns: {
                xs: "minmax(0, 1fr)",
                lg: "repeat(2, minmax(0, 1fr))",
              },
            }}
          >
            <MetricBlock
              label="Deduplicacao"
              value={`${formatInteger(confidence.dedupe_suppressed_volume)} (${formatPercent(
                confidence.dedupe_suppressed_pct,
              )})`}
              helperText={`Sobre ${formatInteger(confidence.dedupe_candidate_volume)} candidatos ao merge.`}
            />
            <MetricBlock
              label="Ambiguidade por nome"
              value={`${formatInteger(confidence.ambiguous_event_name_volume)} (${formatPercent(
                confidence.ambiguous_event_name_pct,
              )})`}
              helperText={`Sobre ${formatInteger(confidence.event_name_candidate_volume)} candidatos por nome.`}
            />
          </Box>

          <Stack spacing={1}>
            {viewModel.confidenceNotes.map((note) => (
              <Alert key={note} severity={note.startsWith("Sem alertas") ? "success" : "warning"} variant="outlined">
                {note}
              </Alert>
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
