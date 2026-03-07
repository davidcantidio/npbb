import { Box, Divider, Paper, Stack, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";

import { formatDateRange } from "./landingHelpers";
import { getCardPaperSx } from "./landingStyle";
import type {
  AboutEventCardProps,
  BrandSummaryCardProps,
  LandingPreviewChecklistItem,
} from "./landingSections.types";

export function AboutEventCard({ data, aboutDescription, pageTextColor }: AboutEventCardProps) {
  return (
    <Paper elevation={0} sx={getCardPaperSx(data.template.color_primary)}>
      <Stack spacing={2}>
        <Typography variant="h5">{data.template.hero_layout === "editorial" ? "Programacao e contexto" : "Sobre o evento"}</Typography>
        <Typography variant="body1" color="text.secondary">
          {aboutDescription}
        </Typography>
        <Divider />
        <Stack spacing={1}>
          <Typography variant="body2" color="text.secondary">
            <strong style={{ color: pageTextColor }}>Quando:</strong> {formatDateRange(data.evento.data_inicio, data.evento.data_fim)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong style={{ color: pageTextColor }}>Onde:</strong> {data.evento.cidade} - {data.evento.estado}
          </Typography>
          {data.acesso.url_promotor ? (
            <Typography variant="body2" color="text.secondary">
              <strong style={{ color: pageTextColor }}>Link do promotor:</strong> {data.acesso.url_promotor}
            </Typography>
          ) : null}
        </Stack>
      </Stack>
    </Paper>
  );
}

export function BrandSummaryCard({ data, isPreview }: BrandSummaryCardProps) {
  return (
    <Paper elevation={0} sx={getCardPaperSx(data.template.color_primary)}>
      <Stack spacing={2}>
        <Typography variant="h6">Marca BB</Typography>
        <Typography variant="body2" color="text.secondary">
          {data.marca.tagline}
        </Typography>
        {isPreview ? (
          <Typography variant="body2" color="text.secondary">
            Template: {data.template.tema} · Tom: {data.template.tone_of_voice}
          </Typography>
        ) : null}
      </Stack>
    </Paper>
  );
}

export function PreviewChecklistCard({
  checklist,
  primaryColor,
}: {
  checklist: LandingPreviewChecklistItem[];
  primaryColor: string;
}) {
  if (!checklist.length) {
    return null;
  }

  return (
    <Paper elevation={0} sx={getCardPaperSx(primaryColor)}>
      <Stack spacing={2}>
        <Typography variant="h6">Checklist minimo da ativacao</Typography>
        {checklist.map((item) => (
          <Box
            key={item.label}
            sx={{
              p: 1.5,
              borderRadius: 3,
              border: `1px solid ${item.ok ? alpha("#16A34A", 0.28) : alpha("#F59E0B", 0.35)}`,
              bgcolor: item.ok ? alpha("#16A34A", 0.06) : alpha("#F59E0B", 0.08),
            }}
          >
            <Typography variant="body2" fontWeight={800}>
              {item.ok ? "OK" : "Pendente"} · {item.label}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {item.helper}
            </Typography>
          </Box>
        ))}
      </Stack>
    </Paper>
  );
}
