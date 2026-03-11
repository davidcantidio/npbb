import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  getEvento,
  getEventoFormConfig,
  getFormularioCamposPossiveis,
  getLandingAnalytics,
  getLandingCustomizationAudit,
  listFormularioTemplates,
  updateEvento,
  updateEventoFormConfig,
  type EventoFormConfig,
  type FormularioTemplate,
  type LandingAnalyticsSummary,
  type LandingCustomizationAuditItem,
} from "../services/eventos";
import { toApiErrorMessage } from "../services/http";
import EventWizardStepper from "../components/eventos/EventWizardStepper";
import { useAuth } from "../store/auth";
import LandingPageView from "../components/landing/LandingPageView";
import {
  previewEventoLanding,
  type LandingPageData,
  type PreviewEventoLandingPayload,
} from "../services/landing_public";

const TEMPLATE_OVERRIDE_OPTIONS = [
  "generico",
  "corporativo",
  "esporte_convencional",
  "esporte_radical",
  "show_musical",
  "evento_cultural",
  "tecnologia",
] as const;

const LANDING_CUSTOMIZATION_MESSAGE =
  "Customizacao controlada: somente template_override, cta_personalizado e descricao_curta podem ser alterados sem sair do catalogo homologado da marca BB. O visual do fundo e determinado pelo template selecionado.";

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
  const [landingMeta, setLandingMeta] = useState<{
    template_override: string;
    cta_personalizado: string;
    descricao_curta: string;
  }>({
    template_override: "",
    cta_personalizado: "",
    descricao_curta: "",
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<LandingPageData | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<LandingAnalyticsSummary[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditItems, setAuditItems] = useState<LandingCustomizationAuditItem[]>([]);
  const hasLoadedInitialPreviewRef = useRef(false);
  const previewAbortControllerRef = useRef<AbortController | null>(null);
  const previewRequestVersionRef = useRef(0);
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

  const camposPayload = useMemo(() => {
    const ordemByLower = new Map(camposPossiveisUniq.map((nome, index) => [nome.toLowerCase(), index]));
    const payload = camposPossiveisUniq
      .map((nome, index) => {
        if (!camposAtivos.has(nome)) return null;
        return {
          nome_campo: nome,
          obrigatorio: camposObrigatorios[nome] ?? true,
          ordem: index,
        };
      })
      .filter(Boolean) as PreviewEventoLandingPayload["campos"];

    const extras = [...camposAtivos].filter((nome) => !ordemByLower.has(nome.toLowerCase()));
    extras.sort((a, b) => a.localeCompare(b));
    extras.forEach((nome, index) => {
      payload.push({
        nome_campo: nome,
        obrigatorio: camposObrigatorios[nome] ?? true,
        ordem: camposPossiveisUniq.length + index,
      });
    });

    return payload;
  }, [camposAtivos, camposObrigatorios, camposPossiveisUniq]);

  const previewPayload = useMemo<PreviewEventoLandingPayload>(
    () => ({
      template_id: templateId,
      template_override: landingMeta.template_override.trim() || null,
      cta_personalizado: landingMeta.cta_personalizado.trim() || null,
      descricao_curta: landingMeta.descricao_curta.trim() || null,
      campos: camposPayload,
    }),
    [camposPayload, landingMeta.cta_personalizado, landingMeta.descricao_curta, landingMeta.template_override, templateId],
  );

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

  const loadPreview = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;

    previewAbortControllerRef.current?.abort();
    const controller = new AbortController();
    previewAbortControllerRef.current = controller;
    const requestVersion = previewRequestVersionRef.current + 1;
    previewRequestVersionRef.current = requestVersion;

    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const response = await previewEventoLanding(token, eventoId, previewPayload, {
        signal: controller.signal,
      });
      if (controller.signal.aborted || requestVersion !== previewRequestVersionRef.current) return;
      setPreviewData(response);
      hasLoadedInitialPreviewRef.current = true;
    } catch (err) {
      if (controller.signal.aborted || requestVersion !== previewRequestVersionRef.current) return;
      setPreviewError(toApiErrorMessage(err, "Erro ao carregar preview da landing."));
    } finally {
      if (!controller.signal.aborted && requestVersion === previewRequestVersionRef.current) {
        setPreviewLoading(false);
      }
    }
  }, [eventoId, previewPayload, token]);

  const refreshPreview = useCallback(async () => {
    await loadPreview();
  }, [loadPreview]);

  const loadGovernanceData = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setAnalyticsLoading(true);
    setAuditLoading(true);
    try {
      const [analyticsRes, auditRes] = await Promise.all([
        getLandingAnalytics(token, eventoId).catch(() => []),
        getLandingCustomizationAudit(token, eventoId).catch(() => []),
      ]);
      setAnalyticsData(analyticsRes);
      setAuditItems(auditRes);
    } finally {
      setAnalyticsLoading(false);
      setAuditLoading(false);
    }
  }, [token, eventoId]);

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
    hasLoadedInitialPreviewRef.current = false;
    try {
      const [configRes, templatesRes, camposRes, eventoRes] = await Promise.all([
        getEventoFormConfig(token, eventoId),
        listFormularioTemplates(token).catch(() => []),
        getFormularioCamposPossiveis(token),
        getEvento(token, eventoId),
      ]);
      setConfig(configRes);
      setTemplates(templatesRes);
      setCamposPossiveis(camposRes);
      setTemplateId(configRes.template_id ?? null);
      setLandingMeta({
        template_override: eventoRes.template_override ?? "",
        cta_personalizado: eventoRes.cta_personalizado ?? "",
        descricao_curta: eventoRes.descricao_curta ?? "",
      });

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

  const handleSave = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;

    setSaving(true);
    try {
      const updated = await updateEventoFormConfig(token, eventoId, {
        template_id: templateId ?? null,
        campos: camposPayload,
      });
      const updatedEvento = await updateEvento(token, eventoId, {
        template_override: landingMeta.template_override.trim() || null,
        cta_personalizado: landingMeta.cta_personalizado.trim() || null,
        descricao_curta: landingMeta.descricao_curta.trim() || null,
      });

      setConfig(updated);
      setTemplateId(updated.template_id ?? null);
      setLandingMeta({
        template_override: updatedEvento.template_override ?? "",
        cta_personalizado: updatedEvento.cta_personalizado ?? "",
        descricao_curta: updatedEvento.descricao_curta ?? "",
      });

      const catalogByLower = new Map(camposPossiveis.map((nome) => [nome.trim().toLowerCase(), nome.trim()]));
      const nextAtivos = new Set<string>();
      const nextObrigatorios: Record<string, boolean> = {};
      for (const campo of updated.campos || []) {
        const normalized = String(campo?.nome_campo || "").trim();
        if (!normalized) continue;
        const canonical = catalogByLower.get(normalized.toLowerCase()) ?? normalized;
        nextAtivos.add(canonical);
        nextObrigatorios[canonical] = Boolean(campo?.obrigatorio);
      }
      setCamposAtivos(nextAtivos);
      setCamposObrigatorios(nextObrigatorios);

      setSnackbar({ open: true, message: "Configuração salva com sucesso.", severity: "success" });
      void loadGovernanceData();
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: err?.message || "Erro ao salvar configuração.",
        severity: "error",
      });
    } finally {
      setSaving(false);
    }
  }, [
    camposPayload,
    camposPossiveis,
    eventoId,
    landingMeta,
    loadGovernanceData,
    templateId,
    token,
  ]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    void loadGovernanceData();
  }, [loadGovernanceData]);

  useEffect(() => {
    if (loading || !config || !token || !Number.isFinite(eventoId)) return;

    const delayMs = hasLoadedInitialPreviewRef.current ? 250 : 0;
    const timer = window.setTimeout(() => {
      void loadPreview();
    }, delayMs);

    return () => window.clearTimeout(timer);
  }, [config, eventoId, loadPreview, loading, token]);

  useEffect(() => {
    return () => {
      previewAbortControllerRef.current?.abort();
    };
  }, []);

  const subtitle = Number.isFinite(eventoId)
    ? `Configure o tema e os campos do formulário do evento #${eventoId}.`
    : "Configure o tema e os campos do formulário do evento.";

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={1} sx={{ mb: 2 }} />

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
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/editar`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: "none" }}
            >
              Voltar (Evento)
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/gamificacao`}
              variant="outlined"
              disabled={!config || loading || saving}
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Próximo
            </Button>
            <Button
              variant="contained"
              disabled={!config || loading || saving}
              onClick={handleSave}
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              {saving ? <CircularProgress size={22} color="inherit" /> : "Salvar"}
            </Button>
          </Stack>
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
                O preview atualiza em tempo real; clique em "Salvar" apenas para persistir.
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Contexto da landing
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                Personalize o comportamento inicial da landing publica e valide o template resolvido antes de usar a URL em campo.
              </Typography>
              <Stack spacing={2}>
                <Autocomplete
                  freeSolo
                  options={[...TEMPLATE_OVERRIDE_OPTIONS]}
                  value={landingMeta.template_override}
                  onChange={(_, value) =>
                    setLandingMeta((prev) => ({ ...prev, template_override: value ?? "" }))
                  }
                  onInputChange={(_, value) =>
                    setLandingMeta((prev) => ({ ...prev, template_override: value }))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Template override"
                      placeholder="Deixe em branco para usar a resolucao automatica"
                    />
                  )}
                />
                <Alert severity="info" variant="outlined">
                  {LANDING_CUSTOMIZATION_MESSAGE}
                </Alert>
                <TextField
                  label="CTA personalizado"
                  value={landingMeta.cta_personalizado}
                  onChange={(event) =>
                    setLandingMeta((prev) => ({ ...prev, cta_personalizado: event.target.value }))
                  }
                  fullWidth
                />
                <TextField
                  label="Descricao curta"
                  value={landingMeta.descricao_curta}
                  onChange={(event) =>
                    setLandingMeta((prev) => ({ ...prev, descricao_curta: event.target.value }))
                  }
                  multiline
                  minRows={3}
                  fullWidth
                />
              </Stack>
            </Box>

            <Box>
              <Stack
                direction={{ xs: "column", md: "row" }}
                justifyContent="space-between"
                alignItems={{ xs: "flex-start", md: "center" }}
                gap={1.5}
                mb={1.5}
              >
                <Box>
                  <Typography variant="subtitle1" fontWeight={900}>
                    Preview da landing
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    O painel abaixo renderiza a mesma landing form-only publicada, com interacoes desabilitadas por estar em preview interno.
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button variant="outlined" onClick={() => void refreshPreview()} disabled={previewLoading}>
                    {previewLoading ? <CircularProgress size={18} color="inherit" /> : "Atualizar preview"}
                  </Button>
                  {previewData?.acesso.landing_url ? (
                    <Button
                      component="a"
                      href={previewData.acesso.landing_url}
                      target="_blank"
                      rel="noreferrer"
                      variant="contained"
                    >
                      Abrir landing publica
                    </Button>
                  ) : null}
                </Stack>
              </Stack>

              {previewError ? (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  {previewError}
                </Alert>
              ) : null}

              {previewLoading && !previewData ? (
                <Stack direction="row" spacing={1} alignItems="center">
                  <CircularProgress size={22} />
                  <Typography variant="body2" color="text.secondary">
                    Carregando preview...
                  </Typography>
                </Stack>
              ) : previewData ? (
                <Box
                  data-testid="event-lead-preview-host"
                  sx={{
                    mt: 1,
                    position: "relative",
                    isolation: "isolate",
                    borderRadius: 4,
                    overflow: "hidden",
                    border: 1,
                    borderColor: "divider",
                  }}
                >
                  <LandingPageView data={previewData} mode="preview" />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Nenhum preview disponivel no momento.
                </Typography>
              )}
            </Box>

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
                        <Box key={`${item.categoria}-${item.tema}`} sx={{ p: 1.5, borderRadius: 2, bgcolor: "action.hover" }}>
                          <Typography variant="body2" fontWeight={800}>
                            {item.tema} · {item.categoria}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Views: {item.page_views} · Inicios: {item.form_starts} · Envios: {item.submit_successes} · Conversao:{" "}
                            {(item.conversion_rate * 100).toFixed(1)}%
                          </Typography>
                          {item.variants.length ? (
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
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

            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Campos possíveis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Marque os campos que estarao ativos no formulario. O preview responde imediatamente; "Salvar" persiste a configuracao.
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
                      data-testid={`lead-field-card-${nome.toLowerCase().replace(/\s+/g, "-")}`}
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
                  label="Check-in sem QR"
                  value={config.urls.url_checkin_sem_qr}
                  fullWidth
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="Copiar URL do check-in sem QR"
                          size="small"
                          onClick={() =>
                            copyToClipboard(config.urls.url_checkin_sem_qr, "Check-in sem QR")
                          }
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
