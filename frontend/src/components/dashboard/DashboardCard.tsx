import ArrowOutwardRoundedIcon from "@mui/icons-material/ArrowOutwardRounded";
import { Box, Card, CardActionArea, CardContent, Chip, Stack, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";
import { Link as RouterLink } from "react-router-dom";

import { getDashboardIcon } from "./dashboardIconMap";
import type { DashboardManifestEntry } from "../../types/dashboard";

type DashboardCardProps = {
  entry: DashboardManifestEntry;
};

export function DashboardCard({ entry }: DashboardCardProps) {
  const Icon = getDashboardIcon(entry.icon);
  const cardRootTestId = `dashboard-card-root-${entry.id}`;
  const cardIconTestId = `dashboard-card-icon-${entry.id}`;
  const cardLinkTestId = `dashboard-card-link-${entry.id}`;

  const content = (
    <CardContent sx={{ height: "100%" }}>
      <Stack spacing={2} sx={{ height: "100%" }}>
        <Box sx={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 1.5 }}>
          <Box
            data-testid={cardIconTestId}
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2,
              display: "grid",
              placeItems: "center",
              bgcolor: (theme) =>
                entry.enabled
                  ? alpha(theme.palette.primary.main, theme.palette.mode === "dark" ? 0.16 : 0.08)
                  : alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.1 : 0.06),
              color: entry.enabled ? "primary.main" : "text.secondary",
            }}
          >
            <Icon fontSize="small" />
          </Box>
          {entry.enabled ? (
            <ArrowOutwardRoundedIcon color="primary" fontSize="small" />
          ) : (
            <Chip label="Em breve" size="small" variant="outlined" sx={{ fontWeight: 700 }} />
          )}
        </Box>

        <Box>
          <Typography variant="subtitle1" fontWeight={800}>
            {entry.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
            {entry.description}
          </Typography>
        </Box>

        <Typography variant="caption" color="text.secondary" sx={{ mt: "auto" }}>
          Dominio: {entry.domain}
        </Typography>
      </Stack>
    </CardContent>
  );

  if (!entry.enabled) {
    return (
      <Card
        data-testid={cardRootTestId}
        variant="outlined"
        sx={{
          height: "100%",
          opacity: 0.78,
          bgcolor: "grey.50",
          cursor: "default",
        }}
      >
        {content}
      </Card>
    );
  }

  return (
    <Card
      data-testid={cardRootTestId}
      variant="outlined"
      sx={{
        height: "100%",
        transition: "transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease",
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow: 3,
          borderColor: "primary.main",
        },
      }}
    >
      <CardActionArea
        data-testid={cardLinkTestId}
        component={RouterLink}
        to={entry.route}
        sx={{ alignItems: "stretch", display: "block", height: "100%" }}
      >
        {content}
      </CardActionArea>
    </Card>
  );
}
