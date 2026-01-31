import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  LinearProgress,
  Paper,
  Radio,
  RadioGroup,
  Skeleton,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import {
  criarSolicitacaoIngresso,
  listIngressosAtivos,
  type IngressoAtivoListItem,
} from "../services/ingressos";
import { useAuth } from "../store/auth";
import { listDiretoriasPublic, setDiretoriaForUser, type Diretoria } from "../services/usuarios";

function formatPeriodo(inicio?: string | null, fim?: string | null) {
  if (!inicio && !fim) return "Periodo nao informado";
  if (inicio && fim && inicio !== fim) return `${inicio} a ${fim}`;
  return inicio || fim;
}

function getFriendlyErrorMessage(err: unknown, fallback: string) {
  const raw = typeof err === "object" && err ? (err as any).message : "";
  if (typeof raw === "string" && raw.trim()) {
    const trimmed = raw.trim();
    if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
      try {
        const parsed = JSON.parse(trimmed);
        const parsedMessage =
          typeof parsed?.message === "string"
            ? parsed.message
            : typeof parsed?.detail === "string"
              ? parsed.detail
              : "";
        if (parsedMessage) return parsedMessage;
      } catch {
        return fallback;
      }
    }
    return trimmed;
  }
  return fallback;
}

function parseErrorDetail(err: unknown): { code?: string; message?: string } {
  const raw = typeof err === "object" && err ? (err as any).message : "";
  if (typeof raw !== "string") return {};
  const trimmed = raw.trim();
  if (!trimmed) return {};
  if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
    try {
      const parsed = JSON.parse(trimmed);
      return {
        code: typeof parsed?.code === "string" ? parsed.code : undefined,
        message: typeof parsed?.message === "string" ? parsed.message : undefined,
      };
    } catch {
      return {};
    }
  }
  return {};
}

export default function IngressosPortal() {
  const { token } = useAuth();
  const location = useLocation();
  const [items, setItems] = useState<IngressoAtivoListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<IngressoAtivoListItem | null>(null);
  const [tipo, setTipo] = useState<"SELF" | "TERCEIRO">("SELF");
  const [emailTerceiro, setEmailTerceiro] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("Solicitacao registrada com sucesso.");
  const [needsDiretoria, setNeedsDiretoria] = useState(false);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [diretoriasLoading, setDiretoriasLoading] = useState(false);
  const [diretoriasError, setDiretoriasError] = useState<string | null>(null);
  const [diretoriaId, setDiretoriaId] = useState<string>("");
  const [diretoriaSaving, setDiretoriaSaving] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    setNeedsDiretoria(false);
    try {
      const data = await listIngressosAtivos(token);
      setItems(data);
    } catch (err: any) {
      const detail = parseErrorDetail(err);
      if (detail.code === "MISSING_DIRETORIA") {
        setNeedsDiretoria(true);
        setError(null);
        return;
      }
      const message = typeof err?.message === "string" ? err.message : "";
      setError(message || "Nao foi possivel carregar os ingressos.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    load();
  }, [token, load]);

  const loadDiretorias = useCallback(async () => {
    setDiretoriasLoading(true);
    setDiretoriasError(null);
    try {
      const data = await listDiretoriasPublic();
      setDiretorias(data);
    } catch (err: any) {
      setDiretoriasError(err?.message || "Erro ao carregar diretorias");
    } finally {
      setDiretoriasLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!needsDiretoria) return;
    loadDiretorias();
  }, [needsDiretoria, loadDiretorias]);

  const showSkeletons = loading && items.length === 0;
  const isValidEmail = (value: string) => /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(value);
  const isTerceiro = tipo === "TERCEIRO";
  const isEmailValid =
    !isTerceiro || (emailTerceiro.trim() !== "" && isValidEmail(emailTerceiro.trim()));
  const canSubmit = Boolean(selected) && !saving && (!isTerceiro || isEmailValid);
  const filteredItems = useMemo(() => {
    const params = new URLSearchParams(location.search);
    const cotaIdParam = params.get("cota_id");
    const cotaId = cotaIdParam ? Number(cotaIdParam) : null;
    if (!cotaId || !Number.isFinite(cotaId)) {
      return items;
    }
    return items.filter((item) => item.cota_id === cotaId);
  }, [items, location.search]);
  const cards = useMemo(
    () =>
      filteredItems.map((item) => {
        const percentual = item.total > 0 ? item.usados / item.total : 0;
        const percentualLabel = `${Math.round(percentual * 100)}%`;
        const usageColor = percentual >= 0.8 ? "error" : percentual >= 0.5 ? "warning" : "success";

        return (
          <Paper
            key={item.cota_id}
            elevation={2}
            sx={{ p: 2.5, borderRadius: 2, display: "flex", flexDirection: "column", gap: 2 }}
          >
            <Box>
              <Typography variant="subtitle1" fontWeight={800}>
                {item.evento_nome}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                Diretoria: {item.diretoria_nome}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                Periodo: {formatPeriodo(item.data_inicio, item.data_fim)}
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" fontWeight={700}>
                {item.usados} usados de {item.total}
              </Typography>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography
                  variant="caption"
                  fontWeight={700}
                  color={item.disponiveis > 0 ? "success.main" : "text.secondary"}
                >
                  {item.disponiveis} disponiveis
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {percentualLabel}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(percentual * 100, 100)}
                color={usageColor}
                sx={{ mt: 1, height: 8, borderRadius: 999 }}
              />
            </Box>

            <Button
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 700 }}
              disabled={item.disponiveis <= 0}
              onClick={() => {
                setSelected(item);
                setTipo("SELF");
                setEmailTerceiro("");
                setEmailError(null);
                setModalError(null);
              }}
            >
              Solicitar ingresso
            </Button>
          </Paper>
        );
      }),
    [filteredItems],
  );

  const handleCloseModal = () => {
    if (saving) return;
    setSelected(null);
    setEmailTerceiro("");
    setTipo("SELF");
    setEmailError(null);
    setModalError(null);
  };

  const helperText =
    !isTerceiro
      ? ""
      : emailTerceiro.trim() === ""
        ? "Informe o email do indicado."
        : isValidEmail(emailTerceiro.trim())
          ? ""
          : "Email invalido.";

  const handleSubmit = async () => {
    if (!token || !selected || !canSubmit) return;
    setSaving(true);
    setModalError(null);

    const rollbackItems = items;
    const optimistic = items.map((item) => {
      if (item.cota_id !== selected.cota_id) return item;
      const nextUsados = item.usados + 1;
      const nextDisponiveis = Math.max(item.disponiveis - 1, 0);
      return {
        ...item,
        usados: nextUsados,
        disponiveis: nextDisponiveis,
      };
    });
    setItems(optimistic);

    try {
      await criarSolicitacaoIngresso(token, {
        cota_id: selected.cota_id,
        tipo,
        indicado_email: isTerceiro ? emailTerceiro.trim() : null,
      });
      setSnackbarMessage("Solicitacao registrada com sucesso.");
      setSnackbarOpen(true);
      handleCloseModal();
    } catch (err: any) {
      setItems(rollbackItems);
      setModalError(getFriendlyErrorMessage(err, "Nao foi possivel registrar a solicitacao."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ width: "100%" }}>
      <Box mb={2}>
        <Typography variant="h4" fontWeight={800}>
          Ingressos
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Solicite ingressos disponiveis para a sua diretoria
        </Typography>
      </Box>

      {loading && items.length > 0 ? <LinearProgress sx={{ mb: 2 }} /> : null}
      {needsDiretoria ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Complete seu cadastro
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Para acessar os ingressos, informe a diretoria a qual voce pertence.
          </Typography>
          <Stack spacing={1.5} mt={2}>
            <Autocomplete
              options={diretorias}
              loading={diretoriasLoading}
              value={
                diretorias.find((d) => d.id === (diretoriaId ? Number(diretoriaId) : -1)) ?? null
              }
              onChange={(_, value) => {
                setDiretoriaId(value ? String(value.id) : "");
                setDiretoriasError(null);
              }}
              getOptionLabel={(option) => option.nome}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Diretoria"
                  placeholder="Selecione sua diretoria"
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {diretoriasLoading ? <CircularProgress color="inherit" size={18} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
            {diretoriasError ? (
              <Typography variant="caption" color="error">
                {diretoriasError}
              </Typography>
            ) : null}
            <Button
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 700, alignSelf: "flex-start" }}
              disabled={!diretoriaId || diretoriaSaving}
              onClick={async () => {
                if (!token || !diretoriaId) return;
                setDiretoriaSaving(true);
                try {
                  await setDiretoriaForUser(token, Number(diretoriaId));
                  setSnackbarMessage("Diretoria atualizada com sucesso.");
                  setSnackbarOpen(true);
                  setNeedsDiretoria(false);
                  await load();
                } catch (err: any) {
                  setDiretoriasError(
                    getFriendlyErrorMessage(err, "Nao foi possivel atualizar a diretoria."),
                  );
                } finally {
                  setDiretoriaSaving(false);
                }
              }}
            >
              {diretoriaSaving ? "Salvando..." : "Salvar diretoria"}
            </Button>
          </Stack>
        </Paper>
      ) : error ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Nao foi possivel carregar os ingressos
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {error}
          </Typography>
          <Button variant="contained" sx={{ textTransform: "none", fontWeight: 700 }} onClick={load}>
            Tentar novamente
          </Button>
        </Paper>
      ) : showSkeletons ? (
        <Box
          sx={{
            display: "grid",
            gap: { xs: 1.5, sm: 2 },
            gridTemplateColumns: {
              xs: "1fr",
              sm: "repeat(2, minmax(0, 1fr))",
              lg: "repeat(3, minmax(0, 1fr))",
              xl: "repeat(4, minmax(0, 1fr))",
            },
          }}
        >
          {Array.from({ length: 4 }).map((_, index) => (
            <Paper
              key={`skeleton-${index}`}
              elevation={2}
              sx={{ p: 2.5, borderRadius: 2, display: "flex", flexDirection: "column", gap: 2 }}
            >
              <Box>
                <Skeleton variant="text" width="70%" height={24} />
                <Skeleton variant="text" width="50%" height={16} />
                <Skeleton variant="text" width="60%" height={16} />
              </Box>
              <Box>
                <Skeleton variant="text" width="60%" height={18} />
                <Skeleton variant="text" width="40%" height={14} />
                <Skeleton variant="rectangular" height={8} sx={{ mt: 1, borderRadius: 999 }} />
              </Box>
              <Skeleton variant="rectangular" height={36} sx={{ borderRadius: 2 }} />
            </Paper>
          ))}
        </Box>
      ) : !loading && filteredItems.length === 0 ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Nenhum ingresso disponivel
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Sua diretoria nao possui cotas abertas no momento.
          </Typography>
          <Button variant="outlined" sx={{ textTransform: "none", fontWeight: 700 }} onClick={load}>
            Atualizar
          </Button>
        </Paper>
      ) : (
        <Stack spacing={2}>
          <Box
            sx={{
              display: "grid",
              gap: { xs: 1.5, sm: 2 },
              gridTemplateColumns: {
                xs: "1fr",
                sm: "repeat(2, minmax(0, 1fr))",
                lg: "repeat(3, minmax(0, 1fr))",
                xl: "repeat(4, minmax(0, 1fr))",
              },
            }}
          >
            {cards}
          </Box>
        </Stack>
      )}

      <Dialog open={Boolean(selected)} onClose={handleCloseModal} fullWidth maxWidth="sm">
        <DialogTitle>Solicitar ingresso</DialogTitle>
        <DialogContent sx={{ pt: 1, display: "flex", flexDirection: "column", gap: 2 }}>
          <Box>
            <Typography variant="subtitle1" fontWeight={800}>
              {selected?.evento_nome || "-"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Diretoria: {selected?.diretoria_nome || "-"}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Disponiveis: {selected?.disponiveis ?? "-"}
          </Typography>
          <RadioGroup
            row
            value={tipo}
            onChange={(event) => {
              const next = event.target.value as "SELF" | "TERCEIRO";
              setTipo(next);
              if (next === "SELF") {
                setEmailTerceiro("");
                setEmailError(null);
              }
            }}
          >
            <FormControlLabel value="SELF" control={<Radio />} label="Para mim" />
            <FormControlLabel value="TERCEIRO" control={<Radio />} label="Para terceiro" />
          </RadioGroup>
          {tipo === "TERCEIRO" ? (
            <TextField
              label="Email do indicado"
              placeholder="nome@exemplo.com"
              value={emailTerceiro}
              onChange={(event) => {
                setEmailTerceiro(event.target.value);
                setEmailError(null);
                setModalError(null);
              }}
              onBlur={() => {
                if (!isValidEmail(emailTerceiro.trim())) {
                  setEmailError("Email invalido.");
                }
              }}
              error={Boolean(emailError) || !isEmailValid}
              helperText={emailError || helperText}
              fullWidth
            />
          ) : null}
          {modalError ? (
            <Alert severity="error" variant="outlined">
              {modalError}
            </Alert>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button variant="outlined" onClick={handleCloseModal} sx={{ textTransform: "none" }}>
            Cancelar
          </Button>
          <Button
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 700 }}
            disabled={!canSubmit}
            onClick={handleSubmit}
          >
            {saving ? "Enviando..." : "Confirmar solicitacao"}
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert onClose={() => setSnackbarOpen(false)} severity="success" variant="filled">
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}
