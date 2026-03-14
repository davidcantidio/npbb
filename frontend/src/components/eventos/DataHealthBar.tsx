import { Box, Button, Stack, Tooltip, Typography, useTheme } from "@mui/material";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeartPulse } from "@fortawesome/free-solid-svg-icons";
import { useMemo } from "react";

export type DataHealthBand = "critical" | "low" | "medium" | "high" | "excellent" | "na";

export type DataHealthBarProps = {
  score: number | null;
  band: DataHealthBand;
  missing_preview?: string[];
  onClick?: () => void;
  onViewAll?: () => void;
  showChevron?: boolean;
};

function clampScore(value: number | null): number | null {
  if (value == null || !Number.isFinite(value)) return null;
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function DataHealthBar({
  score,
  band: _band,
  missing_preview,
  onClick,
  onViewAll,
  showChevron = true,
}: DataHealthBarProps) {
  const theme = useTheme();
  const safeScore = clampScore(score);

  const bandColor = useMemo(() => {
    if (safeScore == null) return theme.palette.grey[400];
    if (safeScore <= 33) return theme.palette.error.main;
    if (safeScore <= 50) return theme.palette.warning.main;
    if (safeScore <= 75) return theme.palette.warning.light;
    return theme.palette.success.main;
  }, [safeScore, theme.palette]);

  const missingList = Array.isArray(missing_preview) ? missing_preview.filter(Boolean) : [];
  const missingTop = missingList.slice(0, 3);
  const extraCount = Math.max(0, missingList.length - missingTop.length);

  const scoreLabel = safeScore == null ? "N/A" : `${safeScore}%`;
  const badgeHeight = 16;
  const badgeBg = safeScore == null ? theme.palette.grey[100] : bandColor;
  const badgeTextColor =
    safeScore == null ? theme.palette.text.secondary : theme.palette.getContrastText(bandColor);
  const ariaLabel =
    safeScore == null
      ? "Saúde dos dados indisponível"
      : `Saúde dos dados ${safeScore}%`;

  const tooltipContent = (
    <Box sx={{ p: 1, maxWidth: 280 }}>
      <Typography variant="body2" fontWeight={600}>
        Saúde dos dados
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.25 }}>
        Indica o quanto as informações do evento estão completas.
      </Typography>
      <Typography variant="body2" sx={{ mt: 0.75 }}>
        {missingTop.length ? `Faltando: ${missingTop.join(", ")}` : "Sem pendências"}
      </Typography>
      {extraCount > 0 && (
        <Typography variant="caption" color="text.secondary" display="block">
          +{extraCount} itens
        </Typography>
      )}
      {onViewAll && (
        <Button
          size="small"
          variant="text"
          onClick={(event) => {
            event.stopPropagation();
            onViewAll();
          }}
          sx={{ mt: 0.5, px: 0, textTransform: "none", fontWeight: 700 }}
        >
          Ver pendências
        </Button>
      )}
    </Box>
  );


  return (
    <Tooltip
      title={tooltipContent}
      arrow
      placement="top-start"
      enterDelay={200}
      leaveDelay={150}
      disableInteractive={false}
    >
      <Box
        component="button"
        type="button"
        onClick={onClick}
        onKeyDown={(event) => {
          if (!onClick) return;
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onClick();
          }
        }}
        aria-label={ariaLabel}
        sx={{
          px: 0,
          py: 0.15,
          m: 0,
          border: 0,
          textAlign: "left",
          backgroundColor: "transparent",
          font: "inherit",
          color: "inherit",
          appearance: "none",
          display: "block",
          width: "100%",
          cursor: onClick ? "pointer" : "default",
          borderRadius: 1,
          transition: "background-color 160ms ease",
          "&:hover": {
            backgroundColor: "rgba(0,0,0,0.04)",
          },
          "&:focus-visible": {
            outline: `2px solid ${theme.palette.primary.main}`,
            outlineOffset: 2,
          },
        }}
      >
        <Stack direction="row" alignItems="center" spacing={0.75} sx={{ flexWrap: "nowrap" }}>
          <Box
            component="span"
            sx={{
              color: safeScore == null ? theme.palette.grey[400] : bandColor,
              display: "inline-flex",
              alignItems: "center",
              fontSize: badgeHeight,
            }}
          >
            <FontAwesomeIcon icon={faHeartPulse} />
          </Box>
          <Box
            sx={{
              px: 0.7,
              height: badgeHeight,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: 999,
              bgcolor: badgeBg,
              minWidth: 46,
              textAlign: "center",
            }}
          >
            <Typography
              variant="caption"
              fontWeight={700}
              color={badgeTextColor}
              sx={{ fontSize: "0.75rem", lineHeight: 1 }}
            >
              {scoreLabel}
            </Typography>
          </Box>
          {showChevron ? <ChevronRightIcon fontSize="small" sx={{ color: "text.secondary" }} /> : null}
        </Stack>

      </Box>
    </Tooltip>
  );
}
