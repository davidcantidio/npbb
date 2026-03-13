import { useMemo } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Paper,
  Snackbar,
  Stack,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../../components/eventos/EventWizardStepper";
import { useAuth } from "../../store/auth";
import { useSnackbarFeedback } from "../../hooks/useSnackbarFeedback";
import {
  AtivacaoFormSection,
  AtivacoesTable,
  AtivacaoViewDialog,
  DeleteAtivacaoDialog,
} from "./components";
import { useEventAtivacoesData } from "./hooks";

export default function EventAtivacoesPage() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const { snackbar, setSnackbar, copyToClipboard, handleSnackbarClose } = useSnackbarFeedback();

  const data = useEventAtivacoesData(token, eventoId, {
    showSuccess: (msg) => setSnackbar({ open: true, message: msg, severity: "success" }),
    showError: (msg) => setSnackbar({ open: true, message: msg, severity: "error" }),
  });

  const subtitle = useMemo(() => {
    if (!data.isValidEventoId) return "Configure as ativacoes do evento.";
    if (data.evento?.nome) return `Configure as ativacoes do evento "${data.evento.nome}".`;
    return `Configure as ativacoes do evento #${eventoId}.`;
  }, [data.evento?.nome, eventoId, data.isValidEventoId]);

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={3} sx={{ mb: 2 }} />

      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Ativações
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {data.isValidEventoId ? (
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/gamificacao`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: "none" }}
            >
              Voltar
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/questionario`}
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Próximo
            </Button>
          </Stack>
        ) : null}
      </Stack>

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {!token ? (
          <Alert severity="warning">Voce precisa estar autenticado para acessar esta pagina.</Alert>
        ) : !data.isValidEventoId ? (
          <Alert severity="warning">Evento invalido.</Alert>
        ) : data.outOfScope ? (
          <Alert severity="warning">Evento nao encontrado ou fora do seu escopo.</Alert>
        ) : data.error ? (
          <Alert severity="error">{data.error}</Alert>
        ) : data.loading ? (
          <Box sx={{ py: 2, display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Box>
        ) : (
          <Stack spacing={3}>
            <AtivacaoFormSection
              form={data.createForm}
              onFormChange={data.setCreateFormField}
              gamificacoes={data.gamificacoes}
              disabled={data.formDisabled}
              isEditing={data.isEditing}
              editing={data.editing}
              evento={data.evento}
              eventoId={eventoId}
              createError={data.createError}
              nomeRequiredError={data.nomeRequiredError}
              onSubmit={data.handleSubmit}
              onReset={data.resetForm}
              isBusy={data.isBusy}
              creating={data.creating}
              saving={data.saving}
            />

            <Divider />

            <Typography variant="subtitle1" fontWeight={900}>
              Ativações adicionadas
            </Typography>

            <AtivacoesTable
              ativacoes={data.ativacoes}
              gamificacaoNameById={data.gamificacaoNameById}
              canAct={data.canAct}
              isBusy={data.isBusy}
              onEdit={data.startEdit}
              onView={data.setViewing}
              onDelete={data.openDelete}
            />
          </Stack>
        )}
      </Paper>

      <AtivacaoViewDialog
        open={Boolean(data.viewing)}
        ativacao={data.viewing}
        gamificacaoNameById={data.gamificacaoNameById}
        onClose={() => data.setViewing(null)}
        onCopy={copyToClipboard}
      />

      <DeleteAtivacaoDialog
        open={data.deleteOpen}
        ativacao={data.deletingTarget}
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
