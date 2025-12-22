import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  Divider,
  FormControlLabel,
  IconButton,
  InputAdornment,
  Paper,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Link as RouterLink, useParams } from "react-router-dom";

import {
  getEventoFormConfig,
  getFormularioCamposPossiveis,
  listFormularioTemplates,
  type EventoFormConfig,
  type FormularioTemplate,
} from "../services/eventos";
import { useAuth } from "../store/auth";

export default function EventLeadFormConfig() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const [config, setConfig] = useState<EventoFormConfig | null>(null);
  const [camposPossiveis, setCamposPossiveis] = useState<string[]>([]);
  const [camposAtivos, setCamposAtivos] = useState<Set<string>>(() => new Set());
  const [camposObrigatorios, setCamposObrigatorios] = useState<Record<string, boolean>>({});
  const [templates, setTemplates] = useState<FormularioTemplate[]>([]);
  const [templateId, setTemplateId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error" | "info";
  }>({ open: false, message: "", severity: "success" });

  const selectedTemplate = useMemo(() => {
    if (templateId == null) return null;
    return templates.find((t) => t.id === templateId) ?? null;
  }, [templates, templateId]);

  const camposPossiveisUniq = useMemo(() => {
    const seen = new Set<string>();
    const items: string[] = [];
    for (const nome of camposPossiveis) {
      const normalized = String(nome || "").trim();
      if (!normalized) continue;
      if (seen.has(normalized.toLowerCase())) continue;
      seen.add(normalized.toLowerCase());
      items.push(normalized);
    }
    return items;
  }, [camposPossiveis]);

  const toggleCampo = useCallback((nome: string) => {
    setCamposAtivos((prev) => {
      const next = new Set(prev);
      const wasActive = next.has(nome);
      if (wasActive) next.delete(nome);
      else next.add(nome);

      if (!wasActive) {
        setCamposObrigatorios((prevObrigatorios) => {
          if (Object.prototype.hasOwnProperty.call(prevObrigatorios, nome)) return prevObrigatorios;
          return { ...prevObrigatorios, [nome]: true };
        });
      }

      return next;
    });
  }, []);

  const setCampoObrigatorio = useCallback((nome: string, obrigatorio: boolean) => {
    setCamposObrigatorios((prev) => ({ ...prev, [nome]: obrigatorio }));
  }, []);

  const copyToClipboard = useCallback(async (text: string, label: string) => {
    const value = (text || "").trim();
    if (!value) {
      setSnackbar({ open: true, message: `Sem URL para copiar (${label}).`, severity: "info" });
      return;
    }

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        setSnackbar({ open: true, message: `Copiado: ${label}`, severity: "success" });
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
        message: ok ? `Copiado: ${label}` : `N\u00e3o foi poss\u00edvel copiar (${label}).`,
        severity: ok ? "success" : "error",
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: err?.message || `N\u00e3o foi poss\u00edvel copiar (${label}).`,
        severity: "error",
      });
    }
  }, []);

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
    try {
      const [configRes, templatesRes, camposRes] = await Promise.all([
        getEventoFormConfig(token, eventoId),
        listFormularioTemplates(token).catch(() => []),
        getFormularioCamposPossiveis(token),
      ]);
      setConfig(configRes);
      setTemplates(templatesRes);
      setCamposPossiveis(camposRes);
      setTemplateId(configRes.template_id ?? null);

      const catalogByLower = new Map(camposRes.map((nome) => [nome.trim().toLowerCase(), nome.trim()]));
      const initialAtivos = new Set<string>();
      const initialObrigatorios: Record<string, boolean> = {};
      for (const campo of configRes.campos || []) {
        const normalized = String(campo?.nome_campo || "").trim();
        if (!normalized) continue;
        const canonical = catalogByLower.get(normalized.toLowerCase()) ?? normalized;
        initialAtivos.add(canonical);
        initialObrigatorios[canonical] = Boolean(campo?.obrigatorio);
      }
      setCamposAtivos(initialAtivos);
      setCamposObrigatorios(initialObrigatorios);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar configuração do formulário");
    } finally {
      setLoading(false);
    }
  }, [token, eventoId]);

  useEffect(() => {
    load();
  }, [load]);

  const subtitle = Number.isFinite(eventoId)
    ? `Configure o tema e os campos do formulário do evento #${eventoId}.`
    : "Configure o tema e os campos do formulário do evento.";

  return (
    <Box sx={{ width: "100%" }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Formulário de Lead
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {Number.isFinite(eventoId) ? (
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}`}
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            sx={{ textTransform: "none" }}
          >
            Voltar ao evento
          </Button>
        ) : null}
      </Stack>

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Stack>
        ) : config ? (
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Tema
              </Typography>
              <Autocomplete
                options={templates}
                value={selectedTemplate}
                onChange={(_, value) => setTemplateId(value ? value.id : null)}
                getOptionLabel={(option) => option.nome}
                isOptionEqualToValue={(option, value) => option.id === value.id}
                sx={{ width: "100%" }}
                renderInput={(params) => <TextField {...params} label="Tema" placeholder="Selecione..." />}
              />
              <Typography variant="caption" color="text.secondary" display="block" sx={{ pt: 0.5 }}>
                Trocar tema altera apenas o estado local (ainda não salva).
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Campos possíveis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Marque os campos que estarão ativos no formulário. (Placeholder: ainda não salva)
              </Typography>
            </Box>

            {camposPossiveisUniq.length ? (
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                  columnGap: 3,
                  rowGap: 1,
                }}
              >
                {camposPossiveisUniq.map((nome, index) => {
                  const ativo = camposAtivos.has(nome);
                  const obrigatorio = ativo ? (camposObrigatorios[nome] ?? true) : false;

                  return (
                    <Box
                      key={nome}
                      sx={{
                        px: 1.5,
                        py: 0.75,
                        borderRadius: 2,
                        border: 1,
                        borderColor: "divider",
                        backgroundColor: ativo ? "rgba(103, 80, 164, 0.05)" : "transparent",
                      }}
                    >
                      <Stack
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                        gap={1}
                        flexWrap="wrap"
                      >
                        <Box>
                          <Typography variant="body2" fontWeight={800} lineHeight={1.2}>
                            {nome}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ordem {index}
                          </Typography>
                        </Box>

                        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                          <FormControlLabel
                            sx={{ m: 0 }}
                            control={<Checkbox size="small" checked={ativo} onChange={() => toggleCampo(nome)} />}
                            label="Ativo"
                          />
                          <FormControlLabel
                            sx={{ m: 0 }}
                            control={
                              <Checkbox
                                size="small"
                                checked={obrigatorio}
                                disabled={!ativo}
                                onChange={(_, checked) => setCampoObrigatorio(nome, checked)}
                              />
                            }
                            label="Obrigatório"
                          />
                        </Stack>
                      </Stack>
                    </Box>
                  );
                })}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Nenhum campo disponível.
              </Typography>
            )}
            <Divider />

            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                URLs geradas
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Links p\u00fablicos gerados pela API (somente leitura).
              </Typography>

              <Stack spacing={1}>
                <TextField
                  label="Landing"
                  value={config.urls.url_landing}
                  fullWidth
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="Copiar URL da landing"
                          size="small"
                          onClick={() => copyToClipboard(config.urls.url_landing, "Landing")}
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  label="Promotor"
                  value={config.urls.url_promotor}
                  fullWidth
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="Copiar URL do promotor"
                          size="small"
                          onClick={() => copyToClipboard(config.urls.url_promotor, "Promotor")}
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  label="Question\u00e1rio"
                  value={config.urls.url_questionario}
                  fullWidth
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="Copiar URL do questionario"
                          size="small"
                          onClick={() => copyToClipboard(config.urls.url_questionario, "Question\u00e1rio")}
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  label="API"
                  value={config.urls.url_api}
                  fullWidth
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="Copiar URL da API"
                          size="small"
                          onClick={() => copyToClipboard(config.urls.url_api, "API")}
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Stack>
            </Box>
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
        onClose={(_, reason) => {
          if (reason === "clickaway") return;
          setSnackbar((prev) => ({ ...prev, open: false }));
        }}
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
