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

import type {
  LandingField,
  LandingPageData,
  LandingSubmitResponse,
} from "../../services/landing_public";

type FormState = Record<string, string>;

export type LandingPreviewChecklistItem = {
  label: string;
  ok: boolean;
  helper: string;
};

type LandingPageViewProps = {
  data: LandingPageData;
  mode?: "public" | "preview";
  formState?: FormState;
  consentimento?: boolean;
  submitError?: string | null;
  saving?: boolean;
  submitted?: LandingSubmitResponse | null;
  onInputChange?: (key: string, value: string) => void;
  onConsentimentoChange?: (checked: boolean) => void;
  onSubmit?: () => void;
  onReset?: () => void;
  checklist?: LandingPreviewChecklistItem[];
};

type LayoutVisualSpec = {
  heroBackground: string;
  heroTextColor: string;
  heroGridColumns: { xs: string; md: string };
  heroTextCardBackground: string;
  heroTextCardBorder: string;
  contentGridColumns: { xs: string; md: string };
  imageMinHeight: { xs: number; md: number };
  buttonVariant: "contained" | "outlined";
  buttonColor: "primary" | "secondary";
  buttonStyles?: Record<string, unknown>;
};

function isDarkColor(value?: string | null) {
  const token = String(value || "").trim().toUpperCase();
  return ["#07111F", "#140F2E", "#1E293B", "#0F172A"].includes(token);
}

export function formatDateRange(start?: string | null, end?: string | null) {
  const formatter = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
  if (!start && !end) return "Data a confirmar";
  const startLabel = start ? formatter.format(new Date(start)) : null;
  const endLabel = end ? formatter.format(new Date(end)) : null;
  if (startLabel && endLabel) return `${startLabel} - ${endLabel}`;
  return startLabel || endLabel || "Data a confirmar";
}

export function getFieldLabel(field: LandingField) {
  return field.required ? `${field.label} *` : field.label;
}

export function buildLandingTheme(data: LandingPageData) {
  const primary = data.template.color_primary || "#3333BD";
  const secondary = data.template.color_secondary || "#FCFC30";
  const background = data.template.color_background || "#F7F8FF";
  const text = data.template.color_text || "#111827";
  const dark = isDarkColor(background) || isDarkColor(primary);

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

function getLayoutVisualSpec(data: LandingPageData): LayoutVisualSpec {
  const { hero_layout: heroLayout, color_primary: primary, color_secondary: secondary, color_text: text } = data.template;
  const defaultTextColor = isDarkColor(primary) || isDarkColor(data.template.color_background) ? "#F8FAFC" : text;

  if (heroLayout === "editorial") {
    return {
      heroBackground: `linear-gradient(180deg, #FFFFFF 0%, ${alpha(primary, 0.08)} 55%, ${alpha(secondary, 0.16)} 100%)`,
      heroTextColor: "#111827",
      heroGridColumns: { xs: "1fr", md: "1.08fr 0.92fr" },
      heroTextCardBackground: alpha("#FFFFFF", 0.78),
      heroTextCardBorder: alpha(primary, 0.18),
      contentGridColumns: { xs: "1fr", md: "1.05fr 0.95fr" },
      imageMinHeight: { xs: 280, md: 520 },
      buttonVariant: "outlined",
      buttonColor: "primary",
      buttonStyles: {
        borderWidth: 2,
        "&:hover": { borderWidth: 2 },
      },
    };
  }

  if (heroLayout === "dark-overlay") {
    return {
      heroBackground: `linear-gradient(135deg, ${alpha("#07111F", 0.98)} 0%, ${alpha(primary, 0.6)} 55%, ${alpha(
        secondary,
        0.22,
      )} 100%)`,
      heroTextColor: "#F8FAFC",
      heroGridColumns: { xs: "1fr", md: "1.1fr 0.9fr" },
      heroTextCardBackground: alpha("#07111F", 0.46),
      heroTextCardBorder: alpha("#FFFFFF", 0.14),
      contentGridColumns: { xs: "1fr", md: "1fr 0.95fr" },
      imageMinHeight: { xs: 300, md: 500 },
      buttonVariant: "contained",
      buttonColor: "secondary",
      buttonStyles: {
        background: `linear-gradient(135deg, ${secondary} 0%, ${alpha("#FFFFFF", 0.88)} 180%)`,
        color: "#07111F",
      },
    };
  }

  if (heroLayout === "full-bleed") {
    return {
      heroBackground: `linear-gradient(180deg, ${alpha(primary, 0.12)} 0%, ${alpha(secondary, 0.08)} 45%, ${alpha(
        primary,
        0.18,
      )} 100%)`,
      heroTextColor: text || "#1F2937",
      heroGridColumns: { xs: "1fr", md: "1fr 1fr" },
      heroTextCardBackground: alpha("#FFFFFF", 0.92),
      heroTextCardBorder: alpha(primary, 0.2),
      contentGridColumns: { xs: "1fr", md: "0.95fr 1.05fr" },
      imageMinHeight: { xs: 320, md: 540 },
      buttonVariant: "contained",
      buttonColor: "secondary",
      buttonStyles: {
        background: `linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)`,
        color: "#FFFFFF",
      },
    };
  }

  return {
    heroBackground: `linear-gradient(135deg, ${primary} 0%, ${alpha(primary, 0.92)} 52%, ${alpha(secondary, 0.58)} 100%)`,
    heroTextColor: defaultTextColor,
    heroGridColumns: { xs: "1fr", md: "1.15fr 0.85fr" },
    heroTextCardBackground: alpha("#FFFFFF", 0.1),
    heroTextCardBorder: alpha("#FFFFFF", 0.18),
    contentGridColumns: { xs: "1fr", md: "0.98fr 1.02fr" },
    imageMinHeight: { xs: 260, md: 460 },
    buttonVariant: data.template.cta_variant === "outlined" ? "outlined" : "contained",
    buttonColor: data.template.cta_variant === "outlined" ? "primary" : "secondary",
  };
}

function renderGraphicOverlay(data: LandingPageData) {
  const primary = data.template.color_primary;
  const secondary = data.template.color_secondary;

  if (data.template.graphics_style === "organic") {
    return (
      <>
        <Box
          sx={{
            position: "absolute",
            inset: "auto auto -80px -40px",
            width: 220,
            height: 220,
            borderRadius: "46% 54% 62% 38% / 43% 36% 64% 57%",
            bgcolor: alpha(secondary, 0.24),
            filter: "blur(6px)",
          }}
        />
        <Box
          sx={{
            position: "absolute",
            inset: "-48px -24px auto auto",
            width: 180,
            height: 180,
            borderRadius: "61% 39% 42% 58% / 47% 59% 41% 53%",
            bgcolor: alpha(primary, 0.18),
          }}
        />
      </>
    );
  }

  if (data.template.graphics_style === "grid") {
    return (
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(${alpha("#FFFFFF", 0.08)} 1px, transparent 1px), linear-gradient(90deg, ${alpha(
            "#FFFFFF",
            0.08,
          )} 1px, transparent 1px)`,
          backgroundSize: "32px 32px",
          maskImage: "linear-gradient(180deg, rgba(0,0,0,0.9), transparent 75%)",
          pointerEvents: "none",
        }}
      />
    );
  }

  if (data.template.graphics_style === "dynamic") {
    return (
      <>
        <Box
          sx={{
            position: "absolute",
            top: -20,
            right: 40,
            width: 180,
            height: 180,
            transform: "rotate(18deg)",
            borderRadius: 8,
            bgcolor: alpha(secondary, 0.18),
          }}
        />
        <Box
          sx={{
            position: "absolute",
            bottom: -36,
            left: 32,
            width: 220,
            height: 72,
            transform: "rotate(-12deg)",
            borderRadius: 999,
            bgcolor: alpha(primary, 0.16),
          }}
        />
      </>
    );
  }

  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: -30,
          right: -10,
          width: 140,
          height: 140,
          borderRadius: 6,
          border: `1px solid ${alpha("#FFFFFF", 0.14)}`,
          transform: "rotate(18deg)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: -20,
          left: 40,
          width: 160,
          height: 160,
          borderRadius: "50%",
          bgcolor: alpha(data.template.color_secondary, 0.12),
        }}
      />
    </>
  );
}

export default function LandingPageView({
  data,
  mode = "public",
  formState = {},
  consentimento = false,
  submitError = null,
  saving = false,
  submitted = null,
  onInputChange,
  onConsentimentoChange,
  onSubmit,
  onReset,
  checklist = [],
}: LandingPageViewProps) {
  const theme = buildLandingTheme(data);
  const layout = getLayoutVisualSpec(data);
  const pageTextColor = data.template.color_text || "#111827";
  const isPreview = mode === "preview";

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: isPreview ? "auto" : "100vh", bgcolor: "background.default", color: "text.primary" }}>
        <Box
          sx={{
            position: "relative",
            overflow: "hidden",
            background: layout.heroBackground,
            color: layout.heroTextColor,
            pb: { xs: 6, md: 10 },
          }}
        >
          {renderGraphicOverlay(data)}

          <Container maxWidth="lg" sx={{ position: "relative", pt: { xs: 4, md: 6 } }}>
            <Stack spacing={3}>
              {isPreview ? (
                <Alert
                  severity="info"
                  sx={{
                    alignSelf: "flex-start",
                    bgcolor: alpha("#FFFFFF", isDarkColor(layout.heroTextColor) ? 0.08 : 0.78),
                    color: layout.heroTextColor,
                    border: `1px solid ${alpha("#FFFFFF", 0.14)}`,
                    "& .MuiAlert-icon": { color: layout.heroTextColor },
                  }}
                >
                  Preview fiel ao contrato real da landing. Hero, CTA, paleta e categoria usam os mesmos dados da rota publica.
                </Alert>
              ) : null}

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
                  <Typography variant="caption" sx={{ opacity: 0.78 }}>
                    {data.template.tema}
                  </Typography>
                </Box>
              </Stack>

              <Box
                sx={{
                  display: "grid",
                  gap: 3,
                  alignItems: "stretch",
                  gridTemplateColumns: layout.heroGridColumns,
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    position: "relative",
                    overflow: "hidden",
                    p: { xs: 3, md: 4 },
                    borderRadius: 6,
                    bgcolor: layout.heroTextCardBackground,
                    border: `1px solid ${layout.heroTextCardBorder}`,
                    backdropFilter: "blur(10px)",
                    zIndex: 1,
                  }}
                >
                  <Stack spacing={2.5}>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems="flex-start" flexWrap="wrap">
                      {data.template.categoria === "esporte_radical" ? (
                        <Chip
                          label="Radical"
                          size="small"
                          sx={{
                            bgcolor: alpha(data.template.color_primary, 0.9),
                            color: "#FFFFFF",
                            fontWeight: 800,
                          }}
                        />
                      ) : null}
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
                        sx={{
                          color: "inherit",
                          borderColor: alpha(layout.heroTextColor, 0.28),
                          bgcolor: alpha("#FFFFFF", isDarkColor(layout.heroTextColor) ? 0.04 : 0.4),
                        }}
                      />
                      {isPreview ? (
                        <Chip
                          label={`Categoria: ${data.template.categoria}`}
                          variant="outlined"
                          sx={{ color: "inherit", borderColor: alpha(layout.heroTextColor, 0.24) }}
                        />
                      ) : null}
                    </Stack>

                    <Typography
                      variant="h1"
                      sx={{
                        fontSize: {
                          xs:
                            data.template.hero_layout === "editorial" || data.template.hero_layout === "full-bleed"
                              ? "2.35rem"
                              : "2.5rem",
                          md:
                            data.template.hero_layout === "editorial" || data.template.hero_layout === "full-bleed"
                              ? "4rem"
                              : "3.7rem",
                        },
                        maxWidth: 760,
                      }}
                    >
                      {data.evento.nome}
                    </Typography>

                    <Typography
                      variant="h6"
                      sx={{
                        maxWidth: data.template.hero_layout === "editorial" ? 740 : 680,
                        opacity: 0.92,
                        fontSize: data.template.hero_layout === "editorial" ? { xs: "1rem", md: "1.15rem" } : undefined,
                      }}
                    >
                      {data.evento.descricao_curta || data.evento.descricao || "Cadastre-se para participar desta experiencia BB."}
                    </Typography>

                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} flexWrap="wrap">
                      <Chip
                        label={`${data.evento.cidade} - ${data.evento.estado}`}
                        variant="outlined"
                        sx={{ color: "inherit", borderColor: alpha(layout.heroTextColor, 0.28) }}
                      />
                      {data.ativacao_id ? (
                        <Chip
                          label={`Ativacao #${data.ativacao_id}`}
                          variant="outlined"
                          sx={{ color: "inherit", borderColor: alpha(layout.heroTextColor, 0.28) }}
                        />
                      ) : null}
                    </Stack>
                  </Stack>
                </Paper>

                <Box
                  sx={{
                    position: "relative",
                    minHeight: layout.imageMinHeight,
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
                    loading={isPreview ? "lazy" : "eager"}
                    sx={{
                      width: "100%",
                      height: "100%",
                      minHeight: layout.imageMinHeight,
                      objectFit: "cover",
                      display: "block",
                    }}
                  />
                  <Box
                    sx={{
                      position: "absolute",
                      inset: 0,
                      background:
                        data.template.hero_layout === "dark-overlay"
                          ? `linear-gradient(180deg, ${alpha("#07111F", 0.18)} 0%, ${alpha("#07111F", 0.68)} 100%)`
                          : `linear-gradient(180deg, transparent 25%, ${alpha("#000000", 0.26)} 100%)`,
                    }}
                  />
                </Box>
              </Box>
            </Stack>
          </Container>
        </Box>

        <Container maxWidth="lg" sx={{ mt: { xs: -4, md: -8 }, pb: isPreview ? 0 : 8 }}>
          <Box
            sx={{
              display: "grid",
              gap: 3,
              alignItems: "start",
              gridTemplateColumns: layout.contentGridColumns,
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
                      {isPreview
                        ? "Preview do formulario publicado para este evento."
                        : "Preencha os dados abaixo para receber novidades e ativar sua participacao."}
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
                        disabled={isPreview}
                        type={field.input_type}
                        label={getFieldLabel(field)}
                        value={formState[field.key] || ""}
                        onChange={(event) => onInputChange?.(field.key, event.target.value)}
                        autoComplete={field.autocomplete || undefined}
                        placeholder={field.placeholder || undefined}
                        multiline={field.key === "interesses"}
                        minRows={field.key === "interesses" ? 3 : undefined}
                        sx={{
                          gridColumn: field.key === "interesses" || field.key === "endereco" ? "1 / -1" : undefined,
                        }}
                      />
                    ))}
                  </Box>

                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={consentimento}
                        disabled={isPreview}
                        onChange={(_, checked) => onConsentimentoChange?.(checked)}
                      />
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
                    variant={layout.buttonVariant}
                    color={layout.buttonColor}
                    onClick={isPreview ? undefined : onSubmit}
                    disabled={isPreview || saving}
                    sx={{
                      minHeight: 52,
                      ...(layout.buttonStyles || {}),
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
                  <Button variant="outlined" onClick={onReset} sx={{ alignSelf: "flex-start" }}>
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
                  <Typography variant="h5">
                    {data.template.hero_layout === "editorial" ? "Programacao e contexto" : "Sobre o evento"}
                  </Typography>
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

              {checklist.length ? (
                <Paper
                  elevation={0}
                  sx={{
                    p: { xs: 3, md: 4 },
                    borderRadius: 6,
                    border: `1px solid ${alpha(data.template.color_primary, 0.12)}`,
                  }}
                >
                  <Stack spacing={2}>
                    <Typography variant="h6">Checklist minimo da ativacao</Typography>
                    {checklist.map((item) => (
                      <Box
                        key={item.label}
                        sx={{
                          p: 1.5,
                          borderRadius: 3,
                          border: `1px solid ${item.ok ? alpha("#16A34A", 0.28) : alpha("#F59E0B", 0.35)}`,
                          bgcolor: item.ok ? alpha("#16A34A", 0.06) : alpha("#F59E0B", 0.08),
                        }}
                      >
                        <Typography variant="body2" fontWeight={800}>
                          {item.ok ? "OK" : "Pendente"} · {item.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.helper}
                        </Typography>
                      </Box>
                    ))}
                  </Stack>
                </Paper>
              ) : null}
            </Stack>
          </Box>
        </Container>

        {!isPreview ? (
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
        ) : null}
      </Box>
    </ThemeProvider>
  );
}
