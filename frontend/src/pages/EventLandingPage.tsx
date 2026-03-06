import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Container,
  CssBaseline,
  Divider,
  FormControlLabel,
  Link,
  Paper,
  Stack,
  TextField,
  ThemeProvider,
  Typography,
  createTheme,
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import { useParams } from "react-router-dom";

import {
  getLandingByAtivacao,
  getLandingByEvento,
  submitLandingForm,
  type LandingField,
  type LandingPageData,
  type LandingSubmitResponse,
} from "../services/landing_public";
import { toApiErrorMessage } from "../services/http";

type FormState = Record<string, string>;

function formatDateRange(start?: string | null, end?: string | null) {
  const formatter = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
  if (!start && !end) return "Data a confirmar";
  const startLabel = start ? formatter.format(new Date(start)) : null;
  const endLabel = end ? formatter.format(new Date(end)) : null;
  if (startLabel && endLabel) return `${startLabel} - ${endLabel}`;
  return startLabel || endLabel || "Data a confirmar";
}

function buildLandingTheme(data: LandingPageData | null) {
  const primary = data?.template.color_primary || "#3333BD";
  const secondary = data?.template.color_secondary || "#FCFC30";
  const background = data?.template.color_background || "#F7F8FF";
  const text = data?.template.color_text || "#111827";
  const dark = [background, primary].some((color) => ["#07111F", "#140F2E"].includes(color.toUpperCase()));

  return createTheme({
    palette: {
      mode: dark ? "dark" : "light",
      primary: { main: primary },
      secondary: { main: secondary },
      background: {
        default: background,
        paper: dark ? alpha("#FFFFFF", 0.08) : "#FFFFFF",
      },
      text: {
        primary: text,
        secondary: dark ? alpha("#FFFFFF", 0.82) : alpha(text, 0.76),
      },
    },
    shape: { borderRadius: 20 },
    typography: {
      fontFamily: '"Roboto Flex Variable", "Roboto", "Inter", system-ui, sans-serif',
      h1: { fontSize: "3rem", fontWeight: 800, lineHeight: 1.05 },
      h2: { fontSize: "2rem", fontWeight: 800, lineHeight: 1.1 },
      h5: { fontWeight: 800 },
      button: { fontWeight: 800, textTransform: "none" },
    },
  });
}

function getFieldLabel(field: LandingField) {
  return field.required ? `${field.label} *` : field.label;
}

export default function EventLandingPage() {
  const { eventId, ativacaoId } = useParams();
  const resolvedEventId = eventId ? Number(eventId) : null;
  const resolvedAtivacaoId = ativacaoId ? Number(ativacaoId) : null;

  const [data, setData] = useState<LandingPageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>({});
  const [consentimento, setConsentimento] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [submitted, setSubmitted] = useState<LandingSubmitResponse | null>(null);
  const [lastSubmittedEmail, setLastSubmittedEmail] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    const load = async () => {
      try {
        if (resolvedAtivacaoId && Number.isFinite(resolvedAtivacaoId)) {
          const response = await getLandingByAtivacao(resolvedAtivacaoId);
          if (!active) return;
          setData(response);
          return;
        }
        if (resolvedEventId && Number.isFinite(resolvedEventId)) {
          const response = await getLandingByEvento(resolvedEventId);
          if (!active) return;
          setData(response);
          return;
        }
        setError("Landing invalida.");
      } catch (err) {
        if (!active) return;
        setError(toApiErrorMessage(err, "Nao foi possivel carregar esta landing."));
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();
    return () => {
      active = false;
    };
  }, [resolvedAtivacaoId, resolvedEventId]);

  const landingTheme = useMemo(() => buildLandingTheme(data), [data]);
  const isCorporativo = data?.template.categoria === "corporativo";
  const pageTextColor = data?.template.color_text || "#111827";

  const handleInputChange = (key: string, value: string) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
    setSubmitError(null);
  };

  const handleSubmit = async () => {
    if (!data) return;

    const missing = data.formulario.campos.filter((field) => field.required && !(formState[field.key] || "").trim());
    if (missing.length > 0) {
      setSubmitError(`Preencha os campos obrigatorios: ${missing.map((field) => field.label).join(", ")}.`);
      return;
    }
    if (!consentimento) {
      setSubmitError("Voce precisa aceitar o tratamento de dados para continuar.");
      return;
    }

    const email = (formState.email || "").trim().toLowerCase();
    if (submitted && email && lastSubmittedEmail === email) {
      return;
    }

    setSaving(true);
    try {
      const response = await submitLandingForm(data.formulario.submit_url, {
        nome: formState.nome || "",
        sobrenome: formState.sobrenome,
        email: formState.email || "",
        cpf: formState.cpf,
        telefone: formState.telefone,
        data_nascimento: formState.data_nascimento,
        estado: formState.estado,
        endereco: formState.endereco,
        interesses: formState.interesses,
        genero: formState.genero,
        area_de_atuacao: formState.area_de_atuacao,
        consentimento_lgpd: consentimento,
      });
      setSubmitted(response);
      setLastSubmittedEmail(email);
      setSubmitError(null);
    } catch (err) {
      setSubmitError(toApiErrorMessage(err, "Nao foi possivel enviar seus dados. Tente novamente."));
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setSubmitted(null);
    setSubmitError(null);
    setConsentimento(false);
    setFormState({});
  };

  return (
    <ThemeProvider theme={landingTheme}>
      <CssBaseline />
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default", color: "text.primary" }}>
        {loading ? (
          <Container maxWidth="sm" sx={{ py: 18 }}>
            <Stack spacing={2} alignItems="center">
              <CircularProgress />
              <Typography variant="body1" color="text.secondary">
                Preparando sua landing...
              </Typography>
            </Stack>
          </Container>
        ) : error || !data ? (
          <Container maxWidth="sm" sx={{ py: 12 }}>
            <Alert severity="error">{error || "Landing nao encontrada."}</Alert>
          </Container>
        ) : (
          <>
            <Box
              sx={{
                background: `linear-gradient(135deg, ${data.template.color_primary} 0%, ${alpha(
                  data.template.color_primary,
                  0.92,
                )} 52%, ${alpha(data.template.color_secondary, isCorporativo ? 0.35 : 0.6)} 100%)`,
                color:
                  data.template.color_text.toUpperCase() === "#F8FAFC" ? data.template.color_text : "#FFFFFF",
                pb: { xs: 6, md: 10 },
              }}
            >
              <Container maxWidth="lg" sx={{ pt: { xs: 4, md: 6 } }}>
                <Stack spacing={3}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: data.template.color_secondary,
                        color: "#1E293B",
                        display: "grid",
                        placeItems: "center",
                        fontWeight: 900,
                        letterSpacing: 1,
                        boxShadow: `0 12px 24px ${alpha("#000000", 0.18)}`,
                      }}
                    >
                      BB
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" sx={{ opacity: 0.82 }}>
                        Banco do Brasil
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.74 }}>
                        {data.template.tema}
                      </Typography>
                    </Box>
                  </Stack>

                  <Box
                    sx={{
                      display: "grid",
                      gap: 3,
                      alignItems: "stretch",
                      gridTemplateColumns: { xs: "1fr", md: isCorporativo ? "1.15fr 0.85fr" : "1fr" },
                    }}
                  >
                    <Paper
                      elevation={0}
                      sx={{
                        p: { xs: 3, md: 4 },
                        borderRadius: 6,
                        bgcolor: alpha("#FFFFFF", isCorporativo ? 0.08 : 0.1),
                        border: `1px solid ${alpha("#FFFFFF", 0.18)}`,
                        backdropFilter: "blur(10px)",
                      }}
                    >
                      <Stack spacing={2.5}>
                        <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems="flex-start">
                          <Chip
                            label={data.template.mood}
                            sx={{
                              bgcolor: alpha(data.template.color_secondary, 0.92),
                              color: "#0F172A",
                              fontWeight: 800,
                              maxWidth: "100%",
                            }}
                          />
                          <Chip
                            label={formatDateRange(data.evento.data_inicio, data.evento.data_fim)}
                            variant="outlined"
                            sx={{ color: "inherit", borderColor: alpha("#FFFFFF", 0.55) }}
                          />
                        </Stack>

                        <Typography variant="h1">{data.evento.nome}</Typography>

                        <Typography variant="h6" sx={{ maxWidth: 680, opacity: 0.92 }}>
                          {data.evento.descricao_curta || data.evento.descricao || "Cadastre-se para participar desta experiencia BB."}
                        </Typography>

                        <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} flexWrap="wrap">
                          <Chip
                            label={`${data.evento.cidade} - ${data.evento.estado}`}
                            variant="outlined"
                            sx={{ color: "inherit", borderColor: alpha("#FFFFFF", 0.55) }}
                          />
                          {data.ativacao_id ? (
                            <Chip
                              label={`Ativacao #${data.ativacao_id}`}
                              variant="outlined"
                              sx={{ color: "inherit", borderColor: alpha("#FFFFFF", 0.55) }}
                            />
                          ) : null}
                        </Stack>
                      </Stack>
                    </Paper>

                    <Box
                      sx={{
                        minHeight: { xs: 260, md: isCorporativo ? "100%" : 420 },
                        borderRadius: 6,
                        overflow: "hidden",
                        boxShadow: `0 24px 60px ${alpha("#000000", 0.18)}`,
                        border: `1px solid ${alpha("#FFFFFF", 0.2)}`,
                      }}
                    >
                      <Box
                        component="img"
                        src={data.marca.url_hero_image}
                        alt={data.marca.hero_alt}
                        loading="eager"
                        sx={{
                          width: "100%",
                          height: "100%",
                          minHeight: { xs: 260, md: isCorporativo ? 520 : 420 },
                          objectFit: "cover",
                          display: "block",
                        }}
                      />
                    </Box>
                  </Box>
                </Stack>
              </Container>
            </Box>

            <Container maxWidth="lg" sx={{ mt: { xs: -4, md: isCorporativo ? -18 : -8 }, pb: 8 }}>
              <Box
                sx={{
                  display: "grid",
                  gap: 3,
                  alignItems: "start",
                  gridTemplateColumns: { xs: "1fr", md: isCorporativo ? "0.95fr 1.05fr" : "1fr 0.95fr" },
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    p: { xs: 3, md: 4 },
                    borderRadius: 6,
                    border: `1px solid ${alpha(data.template.color_primary, 0.12)}`,
                    boxShadow: `0 24px 60px ${alpha(data.template.color_primary, 0.12)}`,
                  }}
                >
                  {!submitted ? (
                    <Stack spacing={2.5}>
                      <Box>
                        <Typography variant="h5" gutterBottom>
                          {data.template.cta_text}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Preencha os dados abaixo para receber novidades e ativar sua participacao.
                        </Typography>
                      </Box>

                      {submitError ? <Alert severity="error">{submitError}</Alert> : null}

                      <Box
                        sx={{
                          display: "grid",
                          gap: 2,
                          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
                        }}
                      >
                        {data.formulario.campos.map((field) => (
                          <TextField
                            key={field.key}
                            fullWidth
                            required={field.required}
                            type={field.input_type}
                            label={getFieldLabel(field)}
                            value={formState[field.key] || ""}
                            onChange={(event) => handleInputChange(field.key, event.target.value)}
                            autoComplete={field.autocomplete || undefined}
                            placeholder={field.placeholder || undefined}
                            multiline={field.key === "interesses"}
                            minRows={field.key === "interesses" ? 3 : undefined}
                            sx={{
                              gridColumn:
                                field.key === "interesses" || field.key === "endereco" ? "1 / -1" : undefined,
                            }}
                          />
                        ))}
                      </Box>

                      <FormControlLabel
                        control={
                          <Checkbox checked={consentimento} onChange={(_, checked) => setConsentimento(checked)} />
                        }
                        label={
                          <Typography variant="body2" color="text.secondary">
                            {data.formulario.lgpd_texto}{" "}
                            <Link href={data.formulario.privacy_policy_url} target="_blank" rel="noreferrer">
                              Politica de privacidade
                            </Link>
                            .
                          </Typography>
                        }
                      />

                      <Button
                        size="large"
                        variant={isCorporativo ? "outlined" : "contained"}
                        color={isCorporativo ? "primary" : "secondary"}
                        onClick={handleSubmit}
                        disabled={saving}
                        sx={{
                          minHeight: 52,
                          borderWidth: isCorporativo ? 2 : undefined,
                          "&:hover": { borderWidth: isCorporativo ? 2 : undefined },
                        }}
                      >
                        {saving ? <CircularProgress size={22} color="inherit" /> : data.template.cta_text}
                      </Button>
                    </Stack>
                  ) : (
                    <Stack spacing={2.5}>
                      <Chip
                        label="Cadastro concluido"
                        sx={{ alignSelf: "flex-start", bgcolor: alpha(data.template.color_secondary, 0.9) }}
                      />
                      <Typography variant="h5">{submitted.mensagem_sucesso}</Typography>
                      <Typography variant="body1" color="text.secondary">
                        Seu cadastro foi registrado para {data.evento.nome}. Em breve o time do BB pode entrar em contato.
                      </Typography>
                      <Button variant="outlined" onClick={handleReset} sx={{ alignSelf: "flex-start" }}>
                        Cadastrar outro email
                      </Button>
                    </Stack>
                  )}
                </Paper>

                <Stack spacing={3}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: { xs: 3, md: 4 },
                      borderRadius: 6,
                      border: `1px solid ${alpha(data.template.color_primary, 0.12)}`,
                    }}
                  >
                    <Stack spacing={2}>
                      <Typography variant="h5">Sobre o evento</Typography>
                      <Typography variant="body1" color="text.secondary">
                        {data.evento.descricao_curta || data.evento.descricao || "Acompanhe esta ativacao especial do Banco do Brasil."}
                      </Typography>
                      <Divider />
                      <Stack spacing={1}>
                        <Typography variant="body2" color="text.secondary">
                          <strong style={{ color: pageTextColor }}>Quando:</strong>{" "}
                          {formatDateRange(data.evento.data_inicio, data.evento.data_fim)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong style={{ color: pageTextColor }}>Onde:</strong> {data.evento.cidade} - {data.evento.estado}
                        </Typography>
                        {data.acesso.url_promotor ? (
                          <Typography variant="body2" color="text.secondary">
                            <strong style={{ color: pageTextColor }}>Link do promotor:</strong> {data.acesso.url_promotor}
                          </Typography>
                        ) : null}
                      </Stack>
                    </Stack>
                  </Paper>

                  <Paper
                    elevation={0}
                    sx={{
                      p: { xs: 3, md: 4 },
                      borderRadius: 6,
                      border: `1px solid ${alpha(data.template.color_primary, 0.12)}`,
                    }}
                  >
                    <Stack spacing={2}>
                      <Typography variant="h6">Marca BB</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {data.marca.tagline}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Template: {data.template.tema} · Tom: {data.template.tone_of_voice}
                      </Typography>
                    </Stack>
                  </Paper>
                </Stack>
              </Box>
            </Container>

            <Box sx={{ borderTop: `1px solid ${alpha(data.template.color_primary, 0.12)}`, py: 4 }}>
              <Container maxWidth="lg">
                <Stack
                  direction={{ xs: "column", md: "row" }}
                  spacing={2}
                  justifyContent="space-between"
                  alignItems={{ xs: "flex-start", md: "center" }}
                >
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: 2,
                        bgcolor: data.template.color_secondary,
                        color: "#1E293B",
                        display: "grid",
                        placeItems: "center",
                        fontWeight: 900,
                      }}
                    >
                      BB
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {data.marca.tagline}
                    </Typography>
                  </Stack>
                  <Link href={data.formulario.privacy_policy_url} target="_blank" rel="noreferrer" underline="hover">
                    Politica de privacidade e LGPD
                  </Link>
                </Stack>
              </Container>
            </Box>
          </>
        )}
      </Box>
    </ThemeProvider>
  );
}
