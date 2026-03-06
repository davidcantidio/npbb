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
  getEvento,
  getEventoFormConfig,
  getFormularioCamposPossiveis,
  listFormularioTemplates,
  updateEvento,
  updateEventoFormConfig,
  type EventoFormConfig,
  type FormularioTemplate,
} from "../services/eventos";
import EventWizardStepper from "../components/eventos/EventWizardStepper";
import { useAuth } from "../store/auth";
import LandingPageView, { type LandingPreviewChecklistItem } from "../components/landing/LandingPageView";
import { getLandingByEvento, type LandingPageData } from "../services/landing_public";

const TEMPLATE_OVERRIDE_OPTIONS = [
  "generico",
  "corporativo",
  "esporte_convencional",
  "esporte_radical",
  "show_musical",
  "evento_cultural",
  "tecnologia",
] as const;

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
    hero_image_url: string;
    cta_personalizado: string;
    descricao_curta: string;
  }>({
    template_override: "",
    hero_image_url: "",
    cta_personalizado: "",
    descricao_curta: "",
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<LandingPageData | null>(null);
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

  const loadPreview = useCallback(async () => {
    if (!Number.isFinite(eventoId)) return;
    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const response = await getLandingByEvento(eventoId);
      setPreviewData(response);
    } catch (err: any) {
      setPreviewError(err?.message || "Erro ao carregar preview da landing.");
    } finally {
      setPreviewLoading(false);
    }
  }, [eventoId]);

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
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
        hero_image_url: eventoRes.hero_image_url ?? "",
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
      setError(err?.message || "Erro ao carregar configuraÃ§Ã£o do formulÃ¡rio");
    } finally {
      setLoading(false);
    }
  }, [token, eventoId]);

  const handleSave = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;

    setSaving(true);
    try {
      const ordemByLower = new Map(camposPossiveisUniq.map((nome, index) => [nome.toLowerCase(), index]));
      const camposPayload = camposPossiveisUniq
        .map((nome, index) => {
          if (!camposAtivos.has(nome)) return null;
          return {
            nome_campo: nome,
            obrigatorio: camposObrigatorios[nome] ?? true,
            ordem: index,
          };
        })
        .filter(Boolean) as Array<{ nome_campo: string; obrigatorio: boolean; ordem: number }>;

      const extras = [...camposAtivos].filter((nome) => !ordemByLower.has(nome.toLowerCase()));
      extras.sort((a, b) => a.localeCompare(b));
      extras.forEach((nome, index) => {
        camposPayload.push({
          nome_campo: nome,
          obrigatorio: camposObrigatorios[nome] ?? true,
          ordem: camposPossiveisUniq.length + index,
        });
      });

      const updated = await updateEventoFormConfig(token, eventoId, {
        template_id: templateId ?? null,
        campos: camposPayload,
      });
      const updatedEvento = await updateEvento(token, eventoId, {
        template_override: landingMeta.template_override.trim() || null,
        hero_image_url: landingMeta.hero_image_url.trim() || null,
        cta_personalizado: landingMeta.cta_personalizado.trim() || null,
        descricao_curta: landingMeta.descricao_curta.trim() || null,
      });

      setConfig(updated);
      setTemplateId(updated.template_id ?? null);
      setLandingMeta({
        template_override: updatedEvento.template_override ?? "",
        hero_image_url: updatedEvento.hero_image_url ?? "",
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

      setSnackbar({ open: true, message: "ConfiguraÃ§Ã£o salva com sucesso.", severity: "success" });
      void loadPreview();
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: err?.message || "Erro ao salvar configuraÃ§Ã£o.",
        severity: "error",
      });
    } finally {
      setSaving(false);
    }
  }, [
    token,
    eventoId,
    templateId,
    camposPossiveis,
    camposPossiveisUniq,
    camposAtivos,
    camposObrigatorios,
    landingMeta,
    loadPreview,
  ]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    void loadPreview();
  }, [loadPreview]);

  const subtitle = Number.isFinite(eventoId)
    ? `Configure o tema e os campos do formulÃ¡rio do evento #${eventoId}.`
    : "Configure o tema e os campos do formulÃ¡rio do evento.";

  const previewChecklist = useMemo<LandingPreviewChecklistItem[]>(() => {
    if (!previewData) return [];
    const heroCustomizado = Boolean(landingMeta.hero_image_url.trim());
    const ctaDisponivel = Boolean(previewData.template.cta_text.trim());
    const taglineOk = previewData.marca.tagline.toLowerCase().includes("banco do brasil");
    const lgpdOk = Boolean(previewData.formulario.privacy_policy_url);

    return [
      {
        label: "Categoria resolvida",
        ok: Boolean(previewData.template.categoria),
        helper: `Categoria ativa: ${previewData.template.categoria || "fallback pendente"}.`,
      },
      {
        label: "Hero da campanha",
        ok: heroCustomizado,
        helper: heroCustomizado
          ? "O evento possui uma imagem de hero configurada manualmente."
          : "Sem URL dedicada. O preview esta usando a arte placeholder derivada do template.",
      },
      {
        label: "CTA principal",
        ok: ctaDisponivel,
        helper: ctaDisponivel
          ? `CTA publicado: "${previewData.template.cta_text}".`
          : "Defina um CTA personalizado ou valide o CTA padrao da categoria.",
      },
      {
        label: "Tagline BB",
        ok: taglineOk,
        helper: taglineOk ? "Assinatura BB presente no rodape e no bloco de marca." : "Tagline BB nao encontrada.",
      },
      {
        label: "Politica e LGPD",
        ok: lgpdOk,
        helper: lgpdOk
          ? "Link de privacidade carregado a partir do contrato real da landing."
          : "A landing esta sem link de politica de privacidade.",
      },
    ];
  }, [landingMeta.hero_image_url, previewData]);

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
            FormulÃ¡rio de Lead
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
              PrÃ³ximo
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
                Trocar tema altera a selecao local ate clicar em "Salvar".
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
                  Customizacao controlada: somente `template_override`, `hero_image_url`, `cta_personalizado` e
                  `descricao_curta` podem ser alterados sem sair do catalogo homologado da marca BB.
                </Alert>
                <TextField
                  label="Hero image URL"
                  value={landingMeta.hero_image_url}
                  onChange={(event) =>
                    setLandingMeta((prev) => ({ ...prev, hero_image_url: event.target.value }))
                  }
                  placeholder="https://..."
                  fullWidth
                />
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
                    O painel abaixo usa o mesmo contrato da landing publica para revisar hero, CTA, categoria e checklist minimo.
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button variant="outlined" onClick={() => void loadPreview()} disabled={previewLoading}>
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
                <Box sx={{ mt: 1, borderRadius: 4, overflow: "hidden", border: 1, borderColor: "divider" }}>
                  <LandingPageView data={previewData} mode="preview" checklist={previewChecklist} />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Nenhum preview disponivel no momento.
                </Typography>
              )}
            </Box>

            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Campos possÃ­veis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Marque os campos que estarao ativos no formulario e salve para persistir.
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
                            label="ObrigatÃ³rio"
                          />
                        </Stack>
                      </Stack>
                    </Box>
                  );
                })}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Nenhum campo disponÃ­vel.
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
