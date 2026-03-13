import { Box, Paper, Stack, Typography } from "@mui/material";
import type {
  LandingAnalyticsSummary,
  LandingCustomizationAuditItem,
} from "../../../services/eventos";

type GovernanceSectionProps = {
  analyticsData: LandingAnalyticsSummary[];
  auditItems: LandingCustomizationAuditItem[];
  analyticsLoading: boolean;
  auditLoading: boolean;
};

export function GovernanceSection({
  analyticsData,
  auditItems,
  analyticsLoading,
  auditLoading,
}: GovernanceSectionProps) {
  return (
    <Box>
      <Typography variant="subtitle1" fontWeight={900} gutterBottom>
        Governanca e performance
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        Historico de customizacoes permitidas e leitura inicial do funil por template/CTA.
      </Typography>

      <Stack spacing={2}>
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography variant="subtitle2" fontWeight={800} gutterBottom>
            Analytics da landing
          </Typography>
          {analyticsLoading ? (
            <Typography variant="body2" color="text.secondary">
              Carregando metricas...
            </Typography>
          ) : analyticsData.length ? (
            <Stack spacing={1.5}>
              {analyticsData.map((item) => (
                <Box
                  key={`${item.categoria}-${item.tema}`}
                  sx={{ p: 1.5, borderRadius: 2, bgcolor: "action.hover" }}
                >
                  <Typography variant="body2" fontWeight={800}>
                    {item.tema} · {item.categoria}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Views: {item.page_views} · Inicios: {item.form_starts} · Envios:{" "}
                    {item.submit_successes} · Conversao:{" "}
                    {(item.conversion_rate * 100).toFixed(1)}%
                  </Typography>
                  {item.variants.length ? (
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                      sx={{ mt: 0.5 }}
                    >
                      Variantes:{" "}
                      {item.variants
                        .map(
                          (variant) =>
                            `${variant.cta_variant_id} (${variant.views} views / ${variant.successes} sucessos)`,
                        )
                        .join(" · ")}
                    </Typography>
                  ) : null}
                </Box>
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              Nenhum dado analitico registrado ainda para este evento.
            </Typography>
          )}
        </Paper>

        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography variant="subtitle2" fontWeight={800} gutterBottom>
            Auditoria de customizacao
          </Typography>
          {auditLoading ? (
            <Typography variant="body2" color="text.secondary">
              Carregando historico...
            </Typography>
          ) : auditItems.length ? (
            <Stack spacing={1.25}>
              {auditItems.map((item) => (
                <Box key={item.id} sx={{ p: 1.5, borderRadius: 2, bgcolor: "action.hover" }}>
                  <Typography variant="body2" fontWeight={800}>
                    {item.field_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Antes: {item.old_value || "vazio"} · Depois: {item.new_value || "vazio"}
                  </Typography>
                </Box>
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              Nenhuma customizacao auditada ate agora.
            </Typography>
          )}
        </Paper>
      </Stack>
    </Box>
  );
}
