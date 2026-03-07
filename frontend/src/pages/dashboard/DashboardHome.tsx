import { Box, Typography } from "@mui/material";

import { DashboardCard } from "../../components/dashboard/DashboardCard";
import { DASHBOARD_MANIFEST } from "../../config/dashboardManifest";

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
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, minmax(0, 1fr))",
            lg: "repeat(3, minmax(0, 1fr))",
          },
        }}
      >
        {DASHBOARD_MANIFEST.map((entry) => (
          <DashboardCard key={entry.id} entry={entry} />
        ))}
      </Box>
    </Box>
  );
}
