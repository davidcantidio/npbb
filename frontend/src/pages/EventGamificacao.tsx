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
  deleteGamificacao,
  getEvento,
  listEventoGamificacoes,
  updateGamificacao,
  type EventoRead,
  type Gamificacao,
  type UpdateGamificacaoPayload,
} from "../services/eventos";
import { useAuth } from "../store/auth";

type EditForm = Required<UpdateGamificacaoPayload>;

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

export default function EventGamificacao() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [gamificacoes, setGamificacoes] = useState<Gamificacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [editOpen, setEditOpen] = useState(false);
  const [editing, setEditing] = useState<Gamificacao | null>(null);
  const [editForm, setEditForm] = useState<EditForm>({
    nome: "",
    descricao: "",
    premio: "",
    titulo_feedback: "",
    texto_feedback: "",
  });
  const [saving, setSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletingTarget, setDeletingTarget] = useState<Gamificacao | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([getEvento(token, eventoId), listEventoGamificacoes(token, eventoId)])
      .then(([eventoRes, listRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setGamificacoes(listRes);
      })
      .catch((err: any) => {
        if (cancelled) return;
        setError(err?.message || "Erro ao carregar gamificações.");
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

  const openEdit = (item: Gamificacao) => {
    setEditing(item);
    setEditForm({
      nome: item.nome,
      descricao: item.descricao,
      premio: item.premio,
      titulo_feedback: item.titulo_feedback,
      texto_feedback: item.texto_feedback,
    });
    setEditError(null);
    setEditOpen(true);
  };

  const openDelete = (item: Gamificacao) => {
    setDeletingTarget(item);
    setDeleteError(null);
    setDeleteOpen(true);
  };

  const canAct = Boolean(token) && isValidEventoId;

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

      <Paper elevation={2} sx={{ borderRadius: 1, overflow: "hidden" }}>
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
                        disabled={!canAct}
                        onClick={() => openEdit(item)}
                      >
                        <EditOutlinedIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        aria-label="Excluir"
                        size="small"
                        color="error"
                        disabled={!canAct}
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

      <Dialog
        open={editOpen}
        onClose={() => (saving ? null : setEditOpen(false))}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Editar gamificação</DialogTitle>
        <DialogContent>
          {editError && (
            <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
              {editError}
            </Alert>
          )}

          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField
              label="Nome"
              required
              value={editForm.nome}
              inputProps={{ maxLength: MAX_LEN.nome }}
              onChange={(e) => setEditForm((prev) => ({ ...prev, nome: e.target.value }))}
              disabled={saving}
              fullWidth
            />
            <TextField
              label="Descrição"
              required
              value={editForm.descricao}
              inputProps={{ maxLength: MAX_LEN.descricao }}
              onChange={(e) => setEditForm((prev) => ({ ...prev, descricao: e.target.value }))}
              disabled={saving}
              multiline
              minRows={3}
              fullWidth
            />
            <TextField
              label="Prêmio"
              required
              value={editForm.premio}
              inputProps={{ maxLength: MAX_LEN.premio }}
              onChange={(e) => setEditForm((prev) => ({ ...prev, premio: e.target.value }))}
              disabled={saving}
              fullWidth
            />
            <TextField
              label="Título do feedback de sucesso"
              required
              value={editForm.titulo_feedback}
              inputProps={{ maxLength: MAX_LEN.titulo_feedback }}
              onChange={(e) => setEditForm((prev) => ({ ...prev, titulo_feedback: e.target.value }))}
              disabled={saving}
              fullWidth
            />
            <TextField
              label="Descrição do feedback de sucesso"
              required
              value={editForm.texto_feedback}
              inputProps={{ maxLength: MAX_LEN.texto_feedback }}
              onChange={(e) => setEditForm((prev) => ({ ...prev, texto_feedback: e.target.value }))}
              disabled={saving}
              multiline
              minRows={3}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)} disabled={saving}>
            Cancelar
          </Button>
          <Button
            variant="contained"
            disabled={!token || saving || !editing}
            onClick={async () => {
              if (!token || !editing) return;

              const nome = normalizeText(editForm.nome);
              const descricao = normalizeText(editForm.descricao);
              const premio = normalizeText(editForm.premio);
              const titulo = normalizeText(editForm.titulo_feedback);
              const texto = normalizeText(editForm.texto_feedback);

              if (!nome || !descricao || !premio || !titulo || !texto) {
                setEditError("Preencha todos os campos obrigatórios.");
                return;
              }

              setSaving(true);
              setEditError(null);
              try {
                const updated = await updateGamificacao(token, editing.id, {
                  nome,
                  descricao,
                  premio,
                  titulo_feedback: titulo,
                  texto_feedback: texto,
                });
                setGamificacoes((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
                setEditOpen(false);
                setEditing(null);
              } catch (err: any) {
                setEditError(err?.message || "Erro ao salvar.");
              } finally {
                setSaving(false);
              }
            }}
            sx={{ fontWeight: 800 }}
          >
            {saving ? <CircularProgress size={22} color="inherit" /> : "Salvar"}
          </Button>
        </DialogActions>
      </Dialog>

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
                setDeleteOpen(false);
                setDeletingTarget(null);
              } catch (err: any) {
                setDeleteError(err?.message || "Erro ao excluir.");
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
    </Box>
  );
}

