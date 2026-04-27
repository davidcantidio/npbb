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
      <Chip
        label={label}
        size="small"
        variant="outlined"
        sx={{
          maxWidth: "100%",
          width: "100%",
          height: "auto",
          justifyContent: "flex-start",
          "& .MuiChip-label": {
            display: "block",
            textAlign: "left",
            whiteSpace: "normal",
            py: 0.75,
            px: 0.5,
            lineHeight: 1.35,
          },
        }}
      />
    </Tooltip>
  );
}

export function ConfidenceSummaryCard({ data, viewModel, sx }: ConfidenceSummaryCardProps) {
  const quality = data.qualidade_consolidado;
  const confidence = data.confianca_consolidado;
  const consolidado = data.consolidado;

  const overline = "Sobre vinculos consolidados.";

  return (
    <Card
      variant="outlined"
      component="section"
      aria-labelledby="confianca-cobertura-heading"
      sx={[
        {
          maxWidth: "100%",
          width: "100%",
          flex: 1,
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
        },
        ...(sx ? (Array.isArray(sx) ? sx : [sx]) : []),
      ]}
    >
      <CardContent
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minHeight: 0,
          py: 1.5,
          px: 2,
          alignItems: "stretch",
          "&:last-child": { pb: 1.5 },
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, flexShrink: 0, mb: 1.25, textAlign: "left" }}>
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

        <Stack direction="column" alignItems="stretch" useFlexGap spacing={2}>
          <MetricChip
            label={`Total na base: ${formatInteger(confidence.base_vinculos)}`}
            tooltip={`Gerado em ${viewModel.generatedAtLabel}`}
          />
          <MetricChip
            label={`Sem conexao com evento: ${formatInteger(confidence.leads_sem_conexao_evento_volume)} (${formatPercent(
              confidence.leads_sem_conexao_evento_pct,
            )})`}
            tooltip="Leads distintos sem vinculo canonico a um evento; o consolidado por evento conta vinculos (um lead pode repetir em varios eventos)."
          />
          <MetricChip
            label={`Sem definicao de cliente BB: ${formatInteger(consolidado.bb_indefinido_volume)} (${formatPercent(
              consolidado.bb_indefinido_pct,
            )})`}
            tooltip="Vinculos lead-evento em que o status de cliente BB ainda nao foi definido; percentual sobre a base de vinculos consolidada."
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
