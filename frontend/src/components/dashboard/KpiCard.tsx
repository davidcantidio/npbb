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
  ariaLabel,
}: KpiCardProps) {
  const normalizedProgress =
    typeof progressValue === "number" ? Math.min(Math.max(progressValue, 0), 100) : null;

  return (
    <Card
      variant="outlined"
      component="section"
      aria-label={ariaLabel ?? title}
      sx={{ height: "100%" }}
    >
      <CardContent>
        <Stack spacing={2}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
            <Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
                <Typography variant="overline" color="text.secondary">
                  {title}
                </Typography>
                {titleTooltip ? <InfoTooltip label={title} description={titleTooltip} /> : null}
              </Box>
              <Typography variant="h5" fontWeight={800}>
                {value}
              </Typography>
            </Box>
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
          </Box>

          {subtitle ? (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          ) : null}

          {normalizedProgress !== null ? (
            <Stack spacing={0.75}>
              <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    {progressLabel || "Cobertura"}
                  </Typography>
                  {progressTooltip ? (
                    <InfoTooltip
                      label={progressLabel || "Cobertura"}
                      description={progressTooltip}
                    />
                  ) : null}
                </Box>
                <Typography variant="caption" fontWeight={700}>
                  {normalizedProgress.toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={normalizedProgress}
                sx={{ height: 8, borderRadius: 999 }}
              />
            </Stack>
          ) : null}

          {helperText ? (
            <Typography variant="caption" color="text.secondary">
              {helperText}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
