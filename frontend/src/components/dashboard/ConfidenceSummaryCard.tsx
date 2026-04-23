import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Box, Card, CardContent, Chip, IconButton, Stack, Tooltip, Typography } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";

import type { AgeAnalysisResponse } from "../../types/dashboard";
import { formatInteger, formatPercent } from "../../utils/ageAnalysis";
import type { AgeAnalysisViewModel } from "../../utils/ageAnalysisViewModel";

type ConfidenceSummaryCardProps = {
  data: AgeAnalysisResponse;
  viewModel: AgeAnalysisViewModel;
  sx?: SxProps<Theme>;
};

type MetricChipProps = {
  label: string;
  tooltip: string;
};

function MetricChip({ label, tooltip }: MetricChipProps) {
  return (
    <Tooltip title={tooltip} describeChild>
      <Chip label={label} size="small" variant="outlined" sx={{ maxWidth: "100%" }} />
    </Tooltip>
  );
}

export function ConfidenceSummaryCard({ data, viewModel, sx }: ConfidenceSummaryCardProps) {
  const quality = data.qualidade_consolidado;
  const confidence = data.confianca_consolidado;

  const overline = "Sobre vinculos consolidados.";

  return (
    <Card
      variant="outlined"
      component="section"
      aria-labelledby="confianca-cobertura-heading"
      sx={[
        { alignSelf: "stretch", maxWidth: "100%" },
        ...(sx ? (Array.isArray(sx) ? sx : [sx]) : []),
      ]}
    >
      <CardContent
        sx={{
          py: 1.5,
          px: 2,
          "&:last-child": { pb: 1.5 },
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, flexShrink: 0, mb: 1.25 }}>
          <Typography id="confianca-cobertura-heading" variant="subtitle1" fontWeight={800} component="h2">
            Confianca e cobertura
          </Typography>
          <Tooltip
            title="Leitura executiva da base consolidada: denominadores antes da interpretacao."
            describeChild
          >
            <IconButton
              size="small"
              edge="end"
              aria-label="Explicacao do bloco Confianca e cobertura"
              sx={{ p: 0.25, color: "text.secondary" }}
            >
              <InfoOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ alignContent: "flex-start" }}>
          <MetricChip
            label={`Total na base: ${formatInteger(confidence.base_vinculos)}`}
            tooltip={`Gerado em ${viewModel.generatedAtLabel}`}
          />
          <MetricChip
            label={`Sem data de nascimento: ${formatInteger(quality.sem_data_nascimento_volume)} (${formatPercent(
              quality.sem_data_nascimento_pct,
            )})`}
            tooltip={overline}
          />
          <MetricChip
            label={`Sem Status de Cliente: ${formatInteger(confidence.base_bb_coberta_volume)} (${formatPercent(
              data.consolidado.cobertura_bb_pct,
            )})`}
            tooltip="Percentual sobre vinculos consolidados."
          />
          <MetricChip
            label={`Sem CPF: ${formatInteger(quality.sem_cpf_volume)} (${formatPercent(quality.sem_cpf_pct)})`}
            tooltip={overline}
          />
          <MetricChip
            label={`Sem nome completo: ${formatInteger(quality.sem_nome_completo_volume)} (${formatPercent(
              quality.sem_nome_completo_pct,
            )})`}
            tooltip={overline}
          />
        </Stack>
      </CardContent>
    </Card>
  );
}
