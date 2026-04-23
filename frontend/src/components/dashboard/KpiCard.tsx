import type { ReactNode } from "react";
import { Box, Card, CardContent, LinearProgress, Stack, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";
import { InfoTooltip } from "./InfoTooltip";

type KpiCardProps = {
  title: string;
  value: string;
  subtitle?: string;
  helperText?: string;
  icon: ReactNode;
  titleTooltip?: string;
  progressValue?: number | null;
  progressLabel?: string;
  progressTooltip?: string;
  /** `center`: ícone e bloco de métricas centralizados (grid de KPIs). `left`: cabeçalho com ícone à direita. */
  contentAlign?: "left" | "center";
  /** Rótulo acessível da região (ex.: nome do KPI para leitores de tela). */
  ariaLabel?: string;
};

export function KpiCard({
  title,
  value,
  subtitle,
  helperText,
  icon,
  titleTooltip,
  progressValue,
  progressLabel,
  progressTooltip,
  contentAlign = "left",
  ariaLabel,
}: KpiCardProps) {
  const normalizedProgress =
    typeof progressValue === "number" ? Math.min(Math.max(progressValue, 0), 100) : null;

  const iconBox = (
    <Box
      sx={{
        width: 44,
        height: 44,
        borderRadius: 2,
        display: "grid",
        placeItems: "center",
        bgcolor: (theme) => alpha(theme.palette.primary.main, theme.palette.mode === "dark" ? 0.16 : 0.08),
        color: "primary.main",
        flexShrink: 0,
      }}
    >
      {icon}
    </Box>
  );

  const titleRow = (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
      <Typography variant="overline" color="text.secondary">
        {title}
      </Typography>
      {titleTooltip ? <InfoTooltip label={title} description={titleTooltip} /> : null}
    </Box>
  );

  const progressBlock =
    normalizedProgress !== null ? (
      <Stack spacing={0.75} alignSelf="stretch" sx={{ width: "100%" }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              {progressLabel || "Cobertura"}
            </Typography>
            {progressTooltip ? (
              <InfoTooltip label={progressLabel || "Cobertura"} description={progressTooltip} />
            ) : null}
          </Box>
          <Typography variant="caption" fontWeight={700}>
            {normalizedProgress.toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={normalizedProgress} sx={{ height: 8, borderRadius: 999 }} />
      </Stack>
    ) : null;

  return (
    <Card
      variant="outlined"
      component="section"
      aria-label={ariaLabel ?? title}
      sx={{ height: "100%" }}
    >
      <CardContent>
        {contentAlign === "center" ? (
          <Stack alignItems="center" spacing={2} sx={{ textAlign: "center", width: "100%" }}>
            {iconBox}
            <Box sx={{ width: "100%" }}>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 0.75,
                  flexWrap: "wrap",
                }}
              >
                <Typography component="span" variant="overline" color="text.secondary">
                  {title}
                </Typography>
                {titleTooltip ? <InfoTooltip label={title} description={titleTooltip} /> : null}
              </Box>
              <Typography variant="h5" fontWeight={800} component="p" sx={{ mt: 0.5 }}>
                {value}
              </Typography>
            </Box>

            {subtitle ? (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            ) : null}

            {progressBlock}

            {helperText ? (
              <Typography variant="caption" color="text.secondary">
                {helperText}
              </Typography>
            ) : null}
          </Stack>
        ) : (
          <Stack spacing={2}>
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
              <Box>
                {titleRow}
                <Typography variant="h5" fontWeight={800}>
                  {value}
                </Typography>
              </Box>
              {iconBox}
            </Box>

            {subtitle ? (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            ) : null}

            {progressBlock}

            {helperText ? (
              <Typography variant="caption" color="text.secondary">
                {helperText}
              </Typography>
            ) : null}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}
