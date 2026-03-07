import type { ReactNode } from "react";
import { Box, Card, CardContent, LinearProgress, Stack, Typography } from "@mui/material";

type KpiCardProps = {
  title: string;
  value: string;
  subtitle?: string;
  helperText?: string;
  icon: ReactNode;
  progressValue?: number | null;
  progressLabel?: string;
};

export function KpiCard({
  title,
  value,
  subtitle,
  helperText,
  icon,
  progressValue,
  progressLabel,
}: KpiCardProps) {
  const normalizedProgress =
    typeof progressValue === "number" ? Math.min(Math.max(progressValue, 0), 100) : null;

  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={2}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
            <Box>
              <Typography variant="overline" color="text.secondary">
                {title}
              </Typography>
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
                bgcolor: "primary.50",
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
