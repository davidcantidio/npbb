import { useMemo } from "react";
import {
  Alert,
  Box,
  Button,
  Stack,
  Snackbar,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../../components/eventos/EventWizardStepper";
import { useAuth } from "../../store/auth";
import { useSnackbarFeedback } from "../../hooks/useSnackbarFeedback";
import {
  GamificacaoFormSection,
  GamificacoesTable,
  DeleteGamificacaoDialog,
} from "./components";
import { useEventGamificacaoData } from "./hooks";

export default function EventGamificacaoPage() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const { snackbar, setSnackbar, handleSnackbarClose } = useSnackbarFeedback();

  const data = useEventGamificacaoData(token, eventoId, {
    showSuccess: (msg) => setSnackbar({ open: true, message: msg, severity: "success" }),
    showError: (msg) => setSnackbar({ open: true, message: msg, severity: "error" }),
  });

  const subtitle = useMemo(() => {
    if (!data.isValidEventoId) return "Evento inválido.";
    if (data.evento?.nome) return `Configure as gamificações do evento "${data.evento.nome}" (#${eventoId}).`;
    return `Configure as gamificações do evento #${eventoId}.`;
  }, [data.evento?.nome, eventoId, data.isValidEventoId]);

  const formDisabled = !data.canAct || data.loading;

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={2} sx={{ mb: 2 }} />

      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Gamificação
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {data.isValidEventoId ? (
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/formulario-lead`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: "none" }}
            >
              Voltar
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/ativacoes`}
              variant="contained"
              disabled={data.loading}
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Próximo
            </Button>
          </Stack>
        ) : null}
      </Stack>

      {data.error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {data.error}
        </Alert>
      )}

      <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="flex-start">
        <GamificacaoFormSection
          form={data.createForm}
          onFormChange={data.setCreateFormField}
          disabled={formDisabled}
          isEditing={data.isEditing}
          editing={data.editing}
          createError={data.createError}
          createAttempted={data.createAttempted}
          onSubmit={data.handleSubmit}
          onCancelEdit={data.cancelEdit}
          isBusy={data.isBusy}
          creating={data.creating}
          saving={data.saving}
        />

        <GamificacoesTable
          gamificacoes={data.gamificacoes}
          loading={data.loading}
          canAct={data.canAct}
          isBusy={data.isBusy}
          onEdit={data.startEdit}
          onDelete={data.openDelete}
        />
      </Stack>

      <DeleteGamificacaoDialog
        open={data.deleteOpen}
        gamificacao={data.deletingTarget}
        deleting={data.deleting}
        deleteError={data.deleteError}
        onClose={data.closeDelete}
        onConfirm={data.confirmDelete}
        hasToken={Boolean(token)}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        onClose={handleSnackbarClose}
      >
        <Alert
          severity={snackbar.severity}
          variant="filled"
          onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
