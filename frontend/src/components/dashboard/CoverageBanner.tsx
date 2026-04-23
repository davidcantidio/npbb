import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import { Alert, Box, Stack, Typography, useTheme } from "@mui/material";
import { alpha } from "@mui/material/styles";

import { formatPercent } from "../../utils/ageAnalysis";
import {
  BB_COVERAGE_DANGER_THRESHOLD,
  BB_COVERAGE_WARNING_THRESHOLD,
  getCoverageStatus,
  type CoverageStatus,
} from "../../utils/coverage";

type CoverageBannerProps = {
  coverage: number;
  thresholdWarning?: number;
  thresholdDanger?: number;
  dismissible?: boolean;
  onDismiss?: () => void;
  variant?: "default" | "compact";
  scope?: "consolidated" | "event";
};

function getCoverageMessage(status: CoverageStatus, scope: "consolidated" | "event") {
  if (status === "danger") {
    return scope === "event"
      ? "Dados de vinculo BB indisponiveis para este evento - realize o cruzamento com a base de dados do Banco."
      : "Dados de vinculo BB indisponiveis neste recorte - realize o cruzamento com a base de dados do Banco.";
  }
  return "Dados parcialmente disponiveis. Realize o cruzamento completo com a base do Banco.";
}

export function CoverageBanner({
  coverage,
  thresholdWarning = BB_COVERAGE_WARNING_THRESHOLD,
  thresholdDanger = BB_COVERAGE_DANGER_THRESHOLD,
  dismissible = false,
  onDismiss,
  variant = "default",
  scope = "consolidated",
}: CoverageBannerProps) {
  const theme = useTheme();
  const status = getCoverageStatus(coverage, { warning: thresholdWarning, danger: thresholdDanger });
  if (status === "normal") return null;

  const isDanger = status === "danger";
  const message = getCoverageMessage(status, scope);
  const label = isDanger ? "Cobertura critica" : "Cobertura parcial";
  const isDark = theme.palette.mode === "dark";
  const backgroundColor = isDanger
    ? alpha(theme.palette.error.main, isDark ? 0.2 : 0.12)
    : alpha(theme.palette.warning.main, isDark ? 0.22 : 0.14);
  const foregroundColor = theme.palette.text.primary;
  const iconColor = isDanger ? theme.palette.error.main : theme.palette.warning.main;

  if (variant === "compact") {
    return (
      <Stack
        data-testid={`coverage-banner-${status}-compact`}
        spacing={0.75}
        sx={{ mt: 0.5, maxWidth: 320, alignItems: "flex-start" }}
      >
        <Typography variant="caption" color="text.secondary">
          Cobertura BB: {formatPercent(coverage)}
        </Typography>
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            gap: 0.75,
            px: 1,
            py: 0.75,
            borderRadius: 1.5,
            bgcolor: backgroundColor,
            color: foregroundColor,
            "& .MuiSvgIcon-root": { color: iconColor },
          }}
        >
          <Box sx={{ display: "flex", pt: 0.1 }}>
            {isDanger ? <ErrorOutlineRoundedIcon fontSize="inherit" /> : <WarningAmberRoundedIcon fontSize="inherit" />}
          </Box>
          <Stack spacing={0.1}>
            <Typography variant="caption" fontWeight={700}>
              {label}
            </Typography>
            <Typography variant="caption">{message}</Typography>
          </Stack>
        </Box>
      </Stack>
    );
  }

  return (
    <Alert
      data-testid={`coverage-banner-${status}-default`}
      severity={isDanger ? "error" : "warning"}
      onClose={dismissible && onDismiss ? onDismiss : undefined}
      icon={isDanger ? <ErrorOutlineRoundedIcon fontSize="inherit" /> : <WarningAmberRoundedIcon fontSize="inherit" />}
      sx={{
        bgcolor: backgroundColor,
        color: foregroundColor,
        "& .MuiAlert-icon": {
          color: iconColor,
        },
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
        <Typography variant="body2" fontWeight={700}>
          Cobertura BB: {formatPercent(coverage)}
        </Typography>
        <Typography variant="body2">{message}</Typography>
      </Box>
    </Alert>
  );
}

export type { CoverageBannerProps };
