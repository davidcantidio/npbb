import type { ReactNode } from "react";
import { Box, Card, CardContent, LinearProgress, Stack, Typography } from "@mui/material";

import { InfoTooltip } from "./InfoTooltip";

type KpiCardTrendDirection = "up" | "down" | "neutral";

type KpiCardTrend = {
  value: ReactNode;
  direction?: KpiCardTrendDirection;
  label?: ReactNode;
};

type KpiCardProps = {
  title: string;
  value: ReactNode;
  subtitle?: ReactNode;
  helperText?: ReactNode;
  icon: ReactNode;
  progressValue?: number | null;
  progressLabel?: string;
  titleTooltip?: string;
  trend?: KpiCardTrend;
};

export function KpiCard({
  title,
  value,
  subtitle,
  helperText,
  icon,
  progressValue,
  progressLabel,
  titleTooltip,
  trend,
}: KpiCardProps) {
  const normalizedProgress =
    typeof progressValue === "number" ? Math.min(Math.max(progressValue, 0), 100) : null;
  const shouldWrapValue = typeof value === "string" || typeof value === "number";
  const shouldWrapSubtitle = typeof subtitle === "string" || typeof subtitle === "number";
  const shouldWrapHelperText = typeof helperText === "string" || typeof helperText === "number";
  const shouldWrapTrendValue = typeof trend?.value === "string" || typeof trend?.value === "number";
  const shouldWrapTrendLabel = typeof trend?.label === "string" || typeof trend?.label === "number";
  const trendColor =
    trend?.direction === "up"
      ? "success.main"
      : trend?.direction === "down"
        ? "error.main"
        : "text.secondary";
  const trendMarker = trend?.direction === "up" ? "+" : trend?.direction === "down" ? "-" : "~";

  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={2}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
            <Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                <Typography variant="overline" color="text.secondary">
                  {title}
                </Typography>
                {titleTooltip ? <InfoTooltip label={title} description={titleTooltip} /> : null}
              </Box>
              {shouldWrapValue ? (
                <Typography variant="h5" fontWeight={800}>
                  {value}
                </Typography>
              ) : (
                value
              )}
            </Box>
            <Box
              sx={{
                width: 44,
                height: 44,
                borderRadius: 2,
                display: "grid",
                placeItems: "center",
                bgcolor: "primary.50",
                color: "primary.main",
                flexShrink: 0,
              }}
            >
              {icon}
            </Box>
          </Box>

          {subtitle && shouldWrapSubtitle ? (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          ) : subtitle ? (
            <Box>{subtitle}</Box>
          ) : null}

          {normalizedProgress !== null ? (
            <Stack spacing={0.75}>
              <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {progressLabel || "Cobertura"}
                </Typography>
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

          {trend ? (
            <Stack spacing={0.25}>
              {trend.label && shouldWrapTrendLabel ? (
                <Typography variant="caption" color="text.secondary">
                  {trend.label}
                </Typography>
              ) : trend.label ? (
                <Box>{trend.label}</Box>
              ) : null}
              <Box sx={{ display: "inline-flex", alignItems: "center", gap: 0.5, color: trendColor }}>
                <Typography variant="caption" fontWeight={700}>
                  {trendMarker}
                </Typography>
                {shouldWrapTrendValue ? (
                  <Typography variant="caption" fontWeight={700}>
                    {trend.value}
                  </Typography>
                ) : (
                  <Box>{trend.value}</Box>
                )}
              </Box>
            </Stack>
          ) : null}

          {helperText && shouldWrapHelperText ? (
            <Typography variant="caption" color="text.secondary">
              {helperText}
            </Typography>
          ) : helperText ? (
            <Box>{helperText}</Box>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
