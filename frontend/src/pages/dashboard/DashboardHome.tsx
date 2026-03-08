import { Box, Typography } from "@mui/material";

import { DashboardCard } from "../../components/dashboard/DashboardCard";
import { DASHBOARD_MANIFEST } from "../../config/dashboardManifest";

export const DASHBOARD_HOME_GRID_COLUMNS = {
  xs: "1fr",
  sm: "repeat(2, minmax(0, 1fr))",
  lg: "repeat(3, minmax(0, 1fr))",
} as const;

export default function DashboardHome() {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Box>
        <Typography variant="h4" fontWeight={900}>
          Painel de analises
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Selecione uma trilha analitica para navegar pelos dashboards disponiveis.
        </Typography>
      </Box>

      <Box
        data-testid="dashboard-home-card-grid"
        aria-label="Analises disponiveis"
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: DASHBOARD_HOME_GRID_COLUMNS,
        }}
      >
        {DASHBOARD_MANIFEST.map((entry) => (
          <DashboardCard key={entry.id} entry={entry} />
        ))}
      </Box>
    </Box>
  );
}
