import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  IconButton,
  Paper,
  Stack,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../components/eventos/EventWizardStepper";
import {
  createEventoGamificacao,
  deleteGamificacao,
  getEvento,
  listEventoGamificacoes,
  updateGamificacao,
  type CreateEventoGamificacaoPayload,
  type EventoRead,
  type Gamificacao,
} from "../services/eventos";
import { getEventApiErrorCode, getEventApiErrorMessage } from "../services/http_event_messages";
import { useAuth } from "../store/auth";

type CreateForm = CreateEventoGamificacaoPayload;

const EMPTY_FORM: CreateForm = {
  nome: "",
  descricao: "",
  premio: "",
  titulo_feedback: "",
  texto_feedback: "",
};

const MAX_LEN = {
  nome: 150,
  descricao: 240,
  premio: 200,
  titulo_feedback: 200,
  texto_feedback: 240,
} as const;

function normalizeText(value: string) {
  return String(value || "").trim();
}

function getApiErrorCode(err: unknown): string | null {
  return getEventApiErrorCode(err);
}


function getApiErrorMessage(err: unknown, fallback: string): string {
  return getEventApiErrorMessage(err, fallback);
}


export default function EventGamificacao() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [gamificacoes, setGamificacoes] = useState<Gamificacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfScope, setOutOfScope] = useState(false);

  const [createAttempted, setCreateAttempted] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const [editing, setEditing] = useState<Gamificacao | null>(null);
  const [saving, setSaving] = useState(false);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletingTarget, setDeletingTarget] = useState<Gamificacao | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error";
  }>({
    open: false,
    message: "",
    severity: "success",
  });

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setGamificacoes([]);

    Promise.all([getEvento(token, eventoId), listEventoGamificacoes(token, eventoId)])
      .then(([eventoRes, listRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setGamificacoes(listRes);
      })
      .catch((err: any) => {
        if (cancelled) return;
        const code = getApiErrorCode(err);
        if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
        setError(getApiErrorMessage(err, "Erro ao carregar gamificações."));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, eventoId, isValidEventoId]);

  const subtitle = useMemo(() => {
    if (!isValidEventoId) return "Evento inválido.";
    if (evento?.nome) return `Configure as gamificações do evento "${evento.nome}" (#${eventoId}).`;
    return `Configure as gamificações do evento #${eventoId}.`;
  }, [evento?.nome, eventoId, isValidEventoId]);

  const startEdit = (item: Gamificacao) => {
    setEditing(item);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm({
      nome: item.nome,
      descricao: item.descricao,
      premio: item.premio,
      titulo_feedback: item.titulo_feedback,
      texto_feedback: item.texto_feedback,
    });
  };

  const openDelete = (item: Gamificacao) => {
    setDeletingTarget(item);
    setDeleteError(null);
    setDeleteOpen(true);
  };

  const canAct = Boolean(token) && isValidEventoId && !outOfScope;
  const isEditing = Boolean(editing);
  const isBusy = creating || saving || deleting;

  const cancelEdit = () => {
    setEditing(null);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm(EMPTY_FORM);
  };

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

        {isValidEventoId ? (
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
              disabled={loading}
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Próximo
            </Button>
          </Stack>
        ) : null}
      </Stack>

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="flex-start">
        <Paper
          elevation={2}
          sx={{
            p: 3,
            borderRadius: 3,
            width: "100%",
            maxWidth: { xs: "100%", md: 420 },
            flexShrink: 0,
          }}
          >
          <Typography variant="h6" fontWeight={900} gutterBottom>
            {isEditing ? "Editar gamificação" : "Adicionar gamificação"}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {isEditing
              ? `Editando a gamificação "${editing?.nome || ""}" (#${editing?.id ?? ""}).`
              : "Cadastre gamificações do evento. Na etapa de Ativações você poderá selecionar uma delas (ou Nenhuma)."}
          </Typography>

          {createError && (
            <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
              {createError}
            </Alert>
          )}

          <Stack spacing={2}>
            <TextField
              label="Nome da gamificação"
              required
              value={createForm.nome}
              inputProps={{ maxLength: MAX_LEN.nome }}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, nome: e.target.value }))}
              disabled={!canAct || loading || creating || saving}
              fullWidth
              error={createAttempted && !normalizeText(createForm.nome)}
              helperText={createAttempted && !normalizeText(createForm.nome) ? "Informe o nome da gamificação." : "\u00A0"}
            />
            <TextField
              label="Descrição"
              required
              value={createForm.descricao}
              inputProps={{ maxLength: MAX_LEN.descricao }}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, descricao: e.target.value }))}
              disabled={!canAct || loading || creating || saving}
              multiline
              minRows={4}
              fullWidth
              error={createAttempted && !normalizeText(createForm.descricao)}
              helperText={
                <Box component="span" sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
                  <Box component="span">
                    {createAttempted && !normalizeText(createForm.descricao) ? "Informe a descrição." : "\u00A0"}
                  </Box>
                  <Box component="span">{`${createForm.descricao.length}/${MAX_LEN.descricao} caracteres`}</Box>
                </Box>
              }
            />
            <TextField
              label="Prêmio"
              required
              value={createForm.premio}
              inputProps={{ maxLength: MAX_LEN.premio }}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, premio: e.target.value }))}
              disabled={!canAct || loading || creating || saving}
              fullWidth
              error={createAttempted && !normalizeText(createForm.premio)}
              helperText={createAttempted && !normalizeText(createForm.premio) ? "Informe o prêmio." : "\u00A0"}
            />
            <TextField
              label="Título do feedback de sucesso"
              required
              value={createForm.titulo_feedback}
              inputProps={{ maxLength: MAX_LEN.titulo_feedback }}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, titulo_feedback: e.target.value }))}
              disabled={!canAct || loading || creating || saving}
              fullWidth
              error={createAttempted && !normalizeText(createForm.titulo_feedback)}
              helperText={
                createAttempted && !normalizeText(createForm.titulo_feedback)
                  ? "Informe o título do feedback."
                  : "\u00A0"
              }
            />
            <TextField
              label="Descrição do feedback de sucesso"
              required
              value={createForm.texto_feedback}
              inputProps={{ maxLength: MAX_LEN.texto_feedback }}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, texto_feedback: e.target.value }))}
              disabled={!canAct || loading || creating || saving}
              multiline
              minRows={4}
              fullWidth
              error={createAttempted && !normalizeText(createForm.texto_feedback)}
              helperText={
                <Box component="span" sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
                  <Box component="span">
                    {createAttempted && !normalizeText(createForm.texto_feedback)
                      ? "Informe a descrição do feedback."
                      : "\u00A0"}
                  </Box>
                  <Box component="span">{`${createForm.texto_feedback.length}/${MAX_LEN.texto_feedback} caracteres`}</Box>
                </Box>
              }
            />

            <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems="stretch">
              {isEditing && (
                <Button
                  variant="outlined"
                  disabled={!canAct || loading || isBusy}
                  onClick={cancelEdit}
                  sx={{ textTransform: "none" }}
                >
                  Cancelar
                </Button>
              )}
              <Button
                variant="contained"
                disabled={!canAct || loading || isBusy}
                onClick={async () => {
                  if (!token || !isValidEventoId) return;

                  setCreateAttempted(true);
                  setCreateError(null);

                  const nome = normalizeText(createForm.nome);
                  const descricao = normalizeText(createForm.descricao);
                  const premio = normalizeText(createForm.premio);
                  const titulo = normalizeText(createForm.titulo_feedback);
                  const texto = normalizeText(createForm.texto_feedback);

                  if (!nome || !descricao || !premio || !titulo || !texto) {
                    setCreateError("Preencha todos os campos obrigatórios.");
                    return;
                  }

                  if (editing) {
                    setSaving(true);
                    try {
                      const updated = await updateGamificacao(token, editing.id, {
                        nome,
                        descricao,
                        premio,
                        titulo_feedback: titulo,
                        texto_feedback: texto,
                      });
                      setGamificacoes((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
                      cancelEdit();
                      setSnackbar({
                        open: true,
                        message: "Gamificação atualizada com sucesso.",
                        severity: "success",
                      });
                    } catch (err: any) {
                      const message = getApiErrorMessage(err, "Erro ao atualizar gamificação.");
                      setCreateError(message);
                      setSnackbar({ open: true, message, severity: "error" });
                    } finally {
                      setSaving(false);
                    }
                    return;
                  }

                  setCreating(true);
                  try {
                    const created = await createEventoGamificacao(token, eventoId, {
                      nome,
                      descricao,
                      premio,
                      titulo_feedback: titulo,
                      texto_feedback: texto,
                    });
                    setGamificacoes((prev) => [...prev, created].sort((a, b) => a.id - b.id));
                    setCreateAttempted(false);
                    setCreateForm(EMPTY_FORM);
                    setSnackbar({
                      open: true,
                      message: "Gamificação adicionada com sucesso.",
                      severity: "success",
                    });
                  } catch (err: any) {
                    const code = getApiErrorCode(err);
                    if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
                    const message = getApiErrorMessage(err, "Erro ao criar gamificação.");
                    setCreateError(message);
                    setSnackbar({ open: true, message, severity: "error" });
                  } finally {
                    setCreating(false);
                  }
                }}
                sx={{ fontWeight: 800, textTransform: "none" }}
              >
                {saving || creating ? (
                  <CircularProgress size={22} color="inherit" />
                ) : isEditing ? (
                  "Atualizar gamificação"
                ) : (
                  "Adicionar gamificação"
                )}
              </Button>
            </Stack>
          </Stack>
        </Paper>

        <Paper elevation={2} sx={{ borderRadius: 1, overflow: "hidden", width: "100%", flex: 1 }}>
          <Box sx={{ px: 2.5, py: 2 }}>
            <Typography variant="h6" fontWeight={900}>
              Gamificações adicionadas
            </Typography>
          </Box>
          <Divider />

          {loading ? (
            <Box
              sx={{
                p: 4,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 1,
              }}
            >
              <CircularProgress size={22} />
              <Typography variant="body2" color="text.secondary">
                Carregando...
              </Typography>
            </Box>
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nome</TableCell>
                  <TableCell width={220}>Prêmio</TableCell>
                  <TableCell width={120} align="right">
                    Ações
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {gamificacoes.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.nome}</TableCell>
                    <TableCell>{item.premio}</TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <IconButton
                          aria-label="Editar"
                          size="small"
                          disabled={!canAct || isBusy}
                          onClick={() => startEdit(item)}
                        >
                          <EditOutlinedIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          aria-label="Excluir"
                          size="small"
                          color="error"
                          disabled={!canAct || isBusy}
                          onClick={() => openDelete(item)}
                        >
                          <DeleteOutlineOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}

                {!gamificacoes.length && (
                  <TableRow>
                    <TableCell colSpan={3}>
                      <Typography variant="body2" color="text.secondary">
                        Nenhuma gamificação adicionada.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </Paper>
      </Stack>

      <Dialog open={deleteOpen} onClose={() => (deleting ? null : setDeleteOpen(false))}>
        <DialogTitle>Excluir gamificação</DialogTitle>
        <DialogContent>
          {deleteError && (
            <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
              {deleteError}
            </Alert>
          )}
          <DialogContentText>
            {deletingTarget
              ? `Tem certeza que deseja excluir a gamificação "${deletingTarget.nome}"?`
              : "Tem certeza?"}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)} disabled={deleting}>
            Cancelar
          </Button>
          <Button
            color="error"
            variant="contained"
            disabled={!token || deleting || !deletingTarget}
            onClick={async () => {
              if (!token || !deletingTarget) return;
              setDeleting(true);
              setDeleteError(null);
              try {
                await deleteGamificacao(token, deletingTarget.id);
                setGamificacoes((prev) => prev.filter((g) => g.id !== deletingTarget.id));
                if (editing?.id === deletingTarget.id) cancelEdit();
                setDeleteOpen(false);
                setDeletingTarget(null);
                setSnackbar({
                  open: true,
                  message: "Gamificação excluída com sucesso.",
                  severity: "success",
                });
              } catch (err: any) {
                const message = getApiErrorMessage(err, "Erro ao excluir.");
                setDeleteError(message);
                setSnackbar({ open: true, message, severity: "error" });
              } finally {
                setDeleting(false);
              }
            }}
            sx={{ fontWeight: 800 }}
          >
            {deleting ? <CircularProgress size={22} color="inherit" /> : "Excluir"}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
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
