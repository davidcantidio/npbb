import { useMemo } from "react";
import {
  Alert,
  Box,
  CircularProgress,
  Divider,
  Paper,
  Snackbar,
  Stack,
  Typography,
} from "@mui/material";
import { useParams } from "react-router-dom";

import EventWizardStepper from "../../components/eventos/EventWizardStepper";
import { useAuth } from "../../store/auth";
import {
  CamposSection,
  EventLeadFormConfigHeader,
  GovernanceSection,
  LandingContextSection,
  PreviewSection,
  TemaSection,
  UrlsSection,
} from "./components";
import {
  useEventLeadFormConfigData,
  useGovernanceData,
  useLandingPreview,
  useSnackbarFeedback,
} from "./hooks";

export default function EventLeadFormConfigPage() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const { snackbar, setSnackbar, copyToClipboard, handleSnackbarClose } = useSnackbarFeedback();

  const configData = useEventLeadFormConfigData(token, eventoId, {
    showSuccess: (msg) => setSnackbar({ open: true, message: msg, severity: "success" }),
    showError: (msg) => setSnackbar({ open: true, message: msg, severity: "error" }),
  });

  const governanceData = useGovernanceData(token, eventoId);

  const previewPayload = useMemo(
    () => ({
      template_id: configData.templateId,
      template_override: configData.landingMeta.template_override.trim() || null,
      cta_personalizado: configData.landingMeta.cta_personalizado.trim() || null,
      descricao_curta: configData.landingMeta.descricao_curta.trim() || null,
      campos: configData.camposState.camposPayload,
    }),
    [
      configData.templateId,
      configData.landingMeta,
      configData.camposState.camposPayload,
    ],
  );

  const preview = useLandingPreview(
    token,
    eventoId,
    previewPayload,
    !!configData.config,
    configData.loading,
  );

  const handleSave = () => {
    void configData.handleSave(governanceData.loadGovernanceData);
  };

  const handleLandingMetaChange = (updates: Partial<{ template_override: string; cta_personalizado: string; descricao_curta: string }>) => {
    configData.setLandingMeta((prev) => ({ ...prev, ...updates }));
  };

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={1} sx={{ mb: 2 }} />

      <EventLeadFormConfigHeader
        eventoId={eventoId}
        config={configData.config}
        loading={configData.loading}
        saving={configData.saving}
        onSave={handleSave}
      />

      {configData.error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {configData.error}
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {configData.loading ? (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Stack>
        ) : configData.config ? (
          <Stack spacing={2}>
            <TemaSection
              templates={configData.templates}
              templateId={configData.templateId}
              onTemplateChange={configData.setTemplateId}
            />

            <LandingContextSection
              landingMeta={configData.landingMeta}
              onLandingMetaChange={handleLandingMetaChange}
            />

            <PreviewSection
              previewData={preview.previewData}
              previewLoading={preview.previewLoading}
              previewError={preview.previewError}
              onRefresh={preview.refreshPreview}
            />

            <GovernanceSection
              analyticsData={governanceData.analyticsData}
              auditItems={governanceData.auditItems}
              analyticsLoading={governanceData.analyticsLoading}
              auditLoading={governanceData.auditLoading}
            />

            <CamposSection
              camposPossiveisUniq={configData.camposState.camposPossiveisUniq}
              camposAtivos={configData.camposState.camposAtivos}
              camposObrigatorios={configData.camposState.camposObrigatorios}
              onToggleCampo={configData.camposState.toggleCampo}
              onSetObrigatorio={configData.camposState.setCampoObrigatorio}
            />

            <Divider />

            <UrlsSection
              urls={configData.config.urls}
              onCopy={copyToClipboard}
            />
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Nenhum dado para exibir.
          </Typography>
        )}
      </Paper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={2400}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
