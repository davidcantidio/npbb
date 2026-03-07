import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import { Alert, Box, Chip, Paper, Stack, Typography } from "@mui/material";

export default function LeadsAgeAnalysisPlaceholder() {
  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={900}>
          Analise etaria por evento
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Estrutura de navegacao pronta para receber a visualizacao analitica na fase F3.
        </Typography>
      </Box>

      <Paper variant="outlined" sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <Box
              sx={{
                width: 44,
                height: 44,
                borderRadius: 2,
                display: "grid",
                placeItems: "center",
                bgcolor: "primary.50",
                color: "primary.main",
              }}
            >
              <InsightsRoundedIcon fontSize="small" />
            </Box>
            <Box>
              <Typography variant="subtitle1" fontWeight={800}>
                Modulo reservado
              </Typography>
              <Typography variant="body2" color="text.secondary">
                A rota ja esta protegida, navegavel e pronta para a camada de dados.
              </Typography>
            </Box>
            <Chip label="F3" color="primary" variant="outlined" sx={{ ml: "auto", fontWeight: 700 }} />
          </Box>

          <Alert severity="info">
            Esta pagina permanece como placeholder intencional nesta entrega para manter o escopo restrito
            a arquitetura do modulo dashboard.
          </Alert>
        </Stack>
      </Paper>
    </Stack>
  );
}
