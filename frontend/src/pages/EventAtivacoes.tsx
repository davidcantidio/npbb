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
  IconButton,
  Paper,
  Snackbar,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../components/eventos/EventWizardStepper";
import {
  deleteAtivacao,
  getEvento,
  listEventoAtivacoes,
  listEventoGamificacoes,
  type Ativacao,
  type EventoRead,
  type Gamificacao,
} from "../services/eventos";
import { useAuth } from "../store/auth";

function getApiErrorCode(err: unknown): string | null {
  const message = (err as any)?.message;
  if (typeof message !== "string" || !message) return null;
  try {
    const parsed = JSON.parse(message);
    if (parsed && typeof parsed.code === "string") return parsed.code;
  } catch {
    // ignore
  }
  if (message.includes("EVENTO_NOT_FOUND")) return "EVENTO_NOT_FOUND";
  if (message.includes("FORBIDDEN")) return "FORBIDDEN";
  return null;
}

function getApiErrorMessage(err: unknown, fallback: string): string {
  const code = getApiErrorCode(err);
  if (code === "EVENTO_NOT_FOUND") return "Evento nao encontrado ou voce nao tem permissao para acessa-lo.";
  if (code === "FORBIDDEN") return "Voce nao tem permissao para realizar esta acao.";

  const message = (err as any)?.message;
  if (typeof message !== "string" || !message.trim()) return fallback;
  if (message === "Failed to fetch") {
    return "Nao foi possivel conectar a API. Verifique se o backend esta rodando e se o CORS permite este endereco.";
  }

  try {
    const parsed = JSON.parse(message);
    if (parsed && typeof parsed.message === "string" && parsed.message.trim()) return parsed.message;
  } catch {
    // ignore
  }

  return message;
}

function getApiErrorExtra(err: unknown): any {
  const message = (err as any)?.message;
  if (typeof message !== "string" || !message) return null;
  try {
    const parsed = JSON.parse(message);
    return parsed?.extra ?? null;
  } catch {
    return null;
  }
}

export default function EventAtivacoes() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [ativacoes, setAtivacoes] = useState<Ativacao[]>([]);
  const [gamificacoes, setGamificacoes] = useState<Gamificacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfScope, setOutOfScope] = useState(false);

  const [viewing, setViewing] = useState<Ativacao | null>(null);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletingTarget, setDeletingTarget] = useState<Ativacao | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error" | "info";
  }>({ open: false, message: "", severity: "success" });

  const gamificacaoNameById = useMemo(() => {
    const map = new Map<number, string>();
    for (const item of gamificacoes) {
      map.set(item.id, item.nome);
    }
    return map;
  }, [gamificacoes]);

  const subtitle = useMemo(() => {
    if (!isValidEventoId) return "Configure as ativacoes do evento.";
    if (evento?.nome) return `Configure as ativacoes do evento "${evento.nome}".`;
    return `Configure as ativacoes do evento #${eventoId}.`;
  }, [evento?.nome, eventoId, isValidEventoId]);

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setAtivacoes([]);
    setGamificacoes([]);

    Promise.all([
      getEvento(token, eventoId),
      listEventoAtivacoes(token, eventoId),
      listEventoGamificacoes(token, eventoId),
    ])
      .then(([eventoRes, ativacoesRes, gamificacoesRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setAtivacoes(ativacoesRes);
        setGamificacoes(gamificacoesRes);
      })
      .catch((err: any) => {
        if (cancelled) return;
        const code = getApiErrorCode(err);
        if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
        setError(getApiErrorMessage(err, "Erro ao carregar ativacoes."));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, eventoId, isValidEventoId]);

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

        {isValidEventoId ? (
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
        ) : !isValidEventoId ? (
          <Alert severity="warning">Evento invalido.</Alert>
        ) : outOfScope ? (
          <Alert severity="warning">Evento nao encontrado ou fora do seu escopo.</Alert>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : loading ? (
          <Box sx={{ py: 2, display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Box>
        ) : (
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Ativacoes adicionadas
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {evento?.nome ? `Evento: ${evento.nome}` : `Evento #${eventoId}`}
              </Typography>
            </Box>

            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nome</TableCell>
                  <TableCell width={140}>Check-in unico</TableCell>
                  <TableCell width={220}>Gamificacao</TableCell>
                  <TableCell width={140} align="right">
                    Acoes
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ativacoes.map((item) => {
                  const gamificacaoLabel = item.gamificacao_id
                    ? gamificacaoNameById.get(item.gamificacao_id) ?? `#${item.gamificacao_id}`
                    : "Nenhuma";
                  return (
                    <TableRow key={item.id}>
                      <TableCell>{item.nome}</TableCell>
                      <TableCell>{item.checkin_unico ? "Sim" : "Nao"}</TableCell>
                      <TableCell>{gamificacaoLabel}</TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                          <IconButton aria-label="Visualizar" size="small" onClick={() => setViewing(item)}>
                            <VisibilityOutlinedIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            aria-label="Editar"
                            size="small"
                            onClick={() =>
                              setSnackbar({
                                open: true,
                                message: "Edicao sera implementada no proximo ticket.",
                                severity: "info",
                              })
                            }
                          >
                            <EditOutlinedIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            aria-label="Excluir"
                            size="small"
                            color="error"
                            onClick={() => {
                              setDeleteError(null);
                              setDeletingTarget(item);
                              setDeleteOpen(true);
                            }}
                          >
                            <DeleteOutlineOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  );
                })}

                {!ativacoes.length && (
                  <TableRow>
                    <TableCell colSpan={4}>
                      <Typography variant="body2" color="text.secondary">
                        Nenhuma ativacao adicionada.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Stack>
        )}
      </Paper>

      <Dialog open={Boolean(viewing)} onClose={() => setViewing(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Visualizar ativacao</DialogTitle>
        <DialogContent>
          {viewing ? (
            <Stack spacing={1}>
              <Typography variant="body2">
                <strong>Nome:</strong> {viewing.nome}
              </Typography>
              <Typography variant="body2">
                <strong>Mensagem (descricao):</strong> {viewing.descricao || "-"}
              </Typography>
              <Typography variant="body2">
                <strong>Mensagem QR Code:</strong> {viewing.mensagem_qrcode || "-"}
              </Typography>
              <Typography variant="body2">
                <strong>Gamificacao:</strong>{" "}
                {viewing.gamificacao_id
                  ? gamificacaoNameById.get(viewing.gamificacao_id) ?? `#${viewing.gamificacao_id}`
                  : "Nenhuma"}
              </Typography>
              <Typography variant="body2">
                <strong>Check-in unico:</strong> {viewing.checkin_unico ? "Sim" : "Nao"}
              </Typography>
              <Typography variant="body2">
                <strong>Redireciona pesquisa:</strong> {viewing.redireciona_pesquisa ? "Sim" : "Nao"}
              </Typography>
              <Typography variant="body2">
                <strong>Termo de uso:</strong> {viewing.termo_uso ? "Sim" : "Nao"}
              </Typography>
              <Typography variant="body2">
                <strong>Gera cupom:</strong> {viewing.gera_cupom ? "Sim" : "Nao"}
              </Typography>
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewing(null)}>Fechar</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteOpen} onClose={() => (deleting ? null : setDeleteOpen(false))}>
        <DialogTitle>Excluir ativacao</DialogTitle>
        <DialogContent>
          {deleteError && (
            <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
              {deleteError}
            </Alert>
          )}
          <DialogContentText>
            {deletingTarget
              ? `Tem certeza que deseja excluir a ativacao "${deletingTarget.nome}"?`
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
                await deleteAtivacao(token, deletingTarget.id);
                setAtivacoes((prev) => prev.filter((a) => a.id !== deletingTarget.id));
                if (viewing?.id === deletingTarget.id) setViewing(null);
                setDeleteOpen(false);
                setDeletingTarget(null);
                setSnackbar({ open: true, message: "Ativacao excluida com sucesso.", severity: "success" });
              } catch (err: any) {
                const code = getApiErrorCode(err);
                if (code === "ATIVACAO_DELETE_BLOCKED") {
                  const deps = getApiErrorExtra(err)?.dependencies;
                  if (deps && typeof deps === "object") {
                    const items = Object.entries(deps)
                      .filter(([, v]) => typeof v === "number" && v > 0)
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(", ");
                    const message = items
                      ? `Nao e possivel excluir: existem vinculos (${items}).`
                      : "Nao e possivel excluir: existem vinculos.";
                    setDeleteError(message);
                    setSnackbar({ open: true, message, severity: "error" });
                    return;
                  }
                }

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
