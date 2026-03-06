import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControlLabel,
  IconButton,
  InputAdornment,
  MenuItem,
  Paper,
  Snackbar,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../components/eventos/EventWizardStepper";
import {
  createEventoAtivacao,
  deleteAtivacao,
  getEvento,
  listEventoAtivacoes,
  listEventoGamificacoes,
  type CreateEventoAtivacaoPayload,
  type Ativacao,
  type EventoRead,
  type Gamificacao,
} from "../services/eventos";
import { ApiError } from "../services/http";
import { getEventApiErrorCode, getEventApiErrorMessage } from "../services/http_event_messages";
import { useAuth } from "../store/auth";

function getApiErrorCode(err: unknown): string | null {
  return getEventApiErrorCode(err);
}

function getApiErrorMessage(err: unknown, fallback: string): string {
  return getEventApiErrorMessage(err, fallback);
}

function getApiErrorExtra(err: unknown): any {
  if (!(err instanceof ApiError)) return null;
  if (!err.body || typeof err.body !== "object") return null;
  return (err.body as any)?.extra ?? null;
}

type CreateForm = {
  nome: string;
  mensagem_qrcode: string;
  descricao: string;
  gamificacao_id: number | null;
  redireciona_pesquisa: boolean;
  checkin_unico: boolean;
  termo_uso: boolean;
  gera_cupom: boolean;
};

const EMPTY_CREATE_FORM: CreateForm = {
  nome: "",
  mensagem_qrcode: "",
  descricao: "",
  gamificacao_id: null,
  redireciona_pesquisa: false,
  checkin_unico: false,
  termo_uso: false,
  gera_cupom: false,
};

const MAX_LEN = {
  nome: 100,
  mensagem_qrcode: 240,
  descricao: 240,
} as const;

function normalizeText(value: string) {
  return String(value || "").trim();
}

function normalizeOptionalText(value: string) {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
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

  const [createAttempted, setCreateAttempted] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>(EMPTY_CREATE_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

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

  const canAct = Boolean(token) && isValidEventoId && !outOfScope;
  const isBusy = creating || deleting;
  const formDisabled = !canAct || isBusy;

  const nomeNormalized = normalizeText(createForm.nome);
  const nomeRequiredError = createAttempted && !nomeNormalized;

  const copyToClipboard = async (text: string | null | undefined, label: string) => {
    const value = String(text || "").trim();
    if (!value) {
      setSnackbar({ open: true, message: `Sem ${label.toLowerCase()} para copiar.`, severity: "info" });
      return;
    }

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        setSnackbar({ open: true, message: `${label} copiado.`, severity: "success" });
        return;
      }
    } catch {
      // fallback abaixo
    }

    try {
      const textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.style.position = "fixed";
      textarea.style.top = "0";
      textarea.style.left = "0";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(textarea);
      setSnackbar({
        open: true,
        message: ok ? `${label} copiado.` : `Nao foi possivel copiar ${label.toLowerCase()}.`,
        severity: ok ? "success" : "error",
      });
    } catch {
      setSnackbar({
        open: true,
        message: `Nao foi possivel copiar ${label.toLowerCase()}.`,
        severity: "error",
      });
    }
  };

  const handleCreate = async () => {
    if (!token || !isValidEventoId) return;

    setCreateAttempted(true);
    setCreateError(null);
    if (!canAct) return;

    const nome = normalizeText(createForm.nome);
    if (!nome) {
      setCreateError("Informe o nome da ativacao.");
      return;
    }

    setCreating(true);

    try {
      const payload: CreateEventoAtivacaoPayload = {
        nome,
        descricao: normalizeOptionalText(createForm.descricao),
        mensagem_qrcode: normalizeOptionalText(createForm.mensagem_qrcode),
        gamificacao_id: createForm.gamificacao_id,
        redireciona_pesquisa: createForm.redireciona_pesquisa,
        checkin_unico: createForm.checkin_unico,
        termo_uso: createForm.termo_uso,
        gera_cupom: createForm.gera_cupom,
      };

      const created = await createEventoAtivacao(token, eventoId, payload);
      setAtivacoes((prev) => [...prev, created].sort((a, b) => a.id - b.id));
      setCreateForm(EMPTY_CREATE_FORM);
      setCreateAttempted(false);
      setSnackbar({ open: true, message: "Ativacao adicionada com sucesso.", severity: "success" });
    } catch (err: any) {
      const code = getApiErrorCode(err);
      if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
      const message = getApiErrorMessage(err, "Erro ao adicionar ativacao.");
        setCreateError(message);
        setSnackbar({ open: true, message, severity: "error" });
      } finally {
        setCreating(false);
      }
    };

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setAtivacoes([]);
    setGamificacoes([]);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm(EMPTY_CREATE_FORM);

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
          <Stack spacing={3}>
            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Nova ativacao
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {evento?.nome ? `Evento: ${evento.nome}` : `Evento #${eventoId}`}
              </Typography>
            </Box>

            {createError && <Alert severity="error">{createError}</Alert>}

            <Stack spacing={2}>
              <TextField
                label="Nome da ativação"
                value={createForm.nome}
                onChange={(e) => {
                  setCreateForm((prev) => ({ ...prev, nome: e.target.value }));
                  setCreateError(null);
                }}
                disabled={formDisabled}
                required
                error={Boolean(nomeRequiredError)}
                helperText={
                  nomeRequiredError ? "Nome obrigatorio." : `${createForm.nome.length}/${MAX_LEN.nome}`
                }
                fullWidth
                inputProps={{ maxLength: MAX_LEN.nome }}
              />

              <TextField
                label="Mensagem do QR Code"
                value={createForm.mensagem_qrcode}
                onChange={(e) => {
                  setCreateForm((prev) => ({ ...prev, mensagem_qrcode: e.target.value }));
                  setCreateError(null);
                }}
                disabled={formDisabled}
                multiline
                minRows={2}
                helperText={`${createForm.mensagem_qrcode.length}/${MAX_LEN.mensagem_qrcode} caracteres`}
                fullWidth
                inputProps={{ maxLength: MAX_LEN.mensagem_qrcode }}
              />

              <TextField
                label="Mensagem"
                value={createForm.descricao}
                onChange={(e) => {
                  setCreateForm((prev) => ({ ...prev, descricao: e.target.value }));
                  setCreateError(null);
                }}
                disabled={formDisabled}
                multiline
                minRows={2}
                helperText={`${createForm.descricao.length}/${MAX_LEN.descricao} caracteres`}
                fullWidth
                inputProps={{ maxLength: MAX_LEN.descricao }}
              />

              <TextField
                select
                label="Tipo de gamificação"
                value={createForm.gamificacao_id ?? ""}
                onChange={(e) => {
                  const raw = e.target.value;
                  const parsed = raw === "" ? null : Number(raw);
                  setCreateForm((prev) => ({
                    ...prev,
                    gamificacao_id: parsed != null && Number.isFinite(parsed) ? parsed : null,
                  }));
                  setCreateError(null);
                }}
                disabled={formDisabled}
                fullWidth
              >
                <MenuItem value="">Nenhuma</MenuItem>
                {gamificacoes.map((g) => (
                  <MenuItem key={g.id} value={g.id}>
                    {g.nome}
                  </MenuItem>
                ))}
              </TextField>

              <Stack direction="row" flexWrap="wrap" columnGap={3} rowGap={1}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={createForm.redireciona_pesquisa}
                      disabled={formDisabled}
                      onChange={(_, checked) => {
                        setCreateError(null);
                        setCreateForm((prev) => ({ ...prev, redireciona_pesquisa: checked }));
                      }}
                    />
                  }
                  label="Redirecionamento para tela de pesquisa"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={createForm.checkin_unico}
                      disabled={formDisabled}
                      onChange={(_, checked) => {
                        setCreateError(null);
                        setCreateForm((prev) => ({ ...prev, checkin_unico: checked }));
                      }}
                    />
                  }
                  label="Check-in único por ativação"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={createForm.termo_uso}
                      disabled={formDisabled}
                      onChange={(_, checked) => {
                        setCreateError(null);
                        setCreateForm((prev) => ({ ...prev, termo_uso: checked }));
                      }}
                    />
                  }
                  label="Termo de uso"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={createForm.gera_cupom}
                      disabled={formDisabled}
                      onChange={(_, checked) => {
                        setCreateError(null);
                        setCreateForm((prev) => ({ ...prev, gera_cupom: checked }));
                      }}
                    />
                  }
                  label="Gerar Cupom"
                />
              </Stack>

              <Stack direction="row" justifyContent="flex-end">
                <Button
                  variant="contained"
                  onClick={handleCreate}
                  disabled={!canAct || isBusy}
                  sx={{ textTransform: "none", fontWeight: 800 }}
                >
                  {creating ? <CircularProgress size={22} color="inherit" /> : "Adicionar ativação"}
                </Button>
              </Stack>
            </Stack>

            <Divider />

            <Typography variant="subtitle1" fontWeight={900}>
              Ativações adicionadas
            </Typography>

            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nome</TableCell>
                  <TableCell width={120}>Único</TableCell>
                  <TableCell width={220}>Gamificação</TableCell>
                  <TableCell width={140} align="right">
                    Ações
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
                          <IconButton
                            aria-label="Visualizar"
                            size="small"
                            color="primary"
                            disabled={!canAct || isBusy}
                            onClick={() => setViewing(item)}
                          >
                            <VisibilityOutlinedIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            aria-label="Excluir"
                            size="small"
                            color="error"
                            disabled={!canAct || isBusy}
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
                        Nenhuma ativação adicionada.
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
              <Alert severity="info" variant="outlined">
                Para quem nao consegue ler QR Code, o promotor pode digitar ou compartilhar a URL abaixo.
              </Alert>
              <TextField
                label="Landing publica"
                value={viewing.landing_url || ""}
                fullWidth
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        edge="end"
                        aria-label="Copiar landing publica"
                        onClick={() => copyToClipboard(viewing.landing_url, "Landing publica")}
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <TextField
                label="URL alternativa do promotor"
                value={viewing.url_promotor || ""}
                fullWidth
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        edge="end"
                        aria-label="Copiar URL alternativa do promotor"
                        onClick={() => copyToClipboard(viewing.url_promotor, "URL alternativa do promotor")}
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              {viewing.qr_code_url ? (
                <Box>
                  <Typography variant="body2" sx={{ mb: 1, fontWeight: 700 }}>
                    QR Code da ativacao
                  </Typography>
                  <Box
                    component="img"
                    src={viewing.qr_code_url}
                    alt={`QR Code da ativacao ${viewing.nome}`}
                    sx={{
                      width: 180,
                      height: 180,
                      borderRadius: 2,
                      border: "1px solid",
                      borderColor: "divider",
                      bgcolor: "common.white",
                      p: 1,
                    }}
                  />
                </Box>
              ) : null}
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
