import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import { Alert, Box, Chip, Stack, Typography } from "@mui/material";

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
};

function getCoverageMessage(status: CoverageStatus, variant: "default" | "compact") {
  if (status === "danger") {
    return variant === "compact"
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
}: CoverageBannerProps) {
  const status = getCoverageStatus(coverage, { warning: thresholdWarning, danger: thresholdDanger });
  if (status === "normal") return null;

  const isDanger = status === "danger";
  const message = getCoverageMessage(status, variant);
  const label = isDanger ? "Cobertura critica" : "Cobertura parcial";

  if (variant === "compact") {
    return (
      <Stack data-testid={`coverage-banner-${status}-compact`} spacing={0.75} sx={{ mt: 0.5 }}>
        <Typography variant="caption" color="text.secondary">
          Cobertura BB: {formatPercent(coverage)}
        </Typography>
        <Chip
          size="small"
          icon={isDanger ? <ErrorOutlineRoundedIcon /> : <WarningAmberRoundedIcon />}
          label={label}
          color={isDanger ? "error" : "warning"}
          variant="outlined"
          title={message}
          sx={{ width: "fit-content" }}
        />
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
        bgcolor: isDanger ? "#FEE2E2" : "#FEF3C7",
        color: isDanger ? "#991B1B" : "#92400E",
        "& .MuiAlert-icon": {
          color: isDanger ? "#991B1B" : "#92400E",
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
