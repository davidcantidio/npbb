import {
  Alert,
  Box,
  Container,
  CssBaseline,
  Link,
  Stack,
  ThemeProvider,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

import type {
  LandingPageData,
  LandingSubmitResponse,
} from "../../services/landing_public";
import { resolveLandingContent } from "./landingContent";
import {
  AboutEventCard,
  BrandSummaryCard,
  HeroContextCard,
  HeroMediaCard,
  LandingFormCard,
  LandingGamificacaoSection,
  LandingHeader,
  type LandingFormState,
  type LandingGamificacaoConfig,
  type LandingPreviewChecklistItem,
  PreviewChecklistCard,
} from "./landingSections";
import {
  buildLandingTheme,
  getLayoutVisualSpec,
  isDarkColor,
  renderGraphicOverlay,
} from "./landingStyle";

export { buildLandingTheme } from "./landingStyle";
export { formatDateRange, getFieldLabel } from "./landingHelpers";

export type { LandingPreviewChecklistItem };

type LandingPageViewProps = {
  data: LandingPageData;
  mode?: "public" | "preview";
  formState?: LandingFormState;
  consentimento?: boolean;
  submitError?: string | null;
  saving?: boolean;
  submitted?: LandingSubmitResponse | null;
  onInputChange?: (key: string, value: string) => void;
  onConsentimentoChange?: (checked: boolean) => void;
  onSubmit?: () => void;
  onReset?: () => void;
  gamificacao?: LandingGamificacaoConfig;
  checklist?: LandingPreviewChecklistItem[];
};

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
  gamificacao,
  checklist = [],
}: LandingPageViewProps) {
  const theme = buildLandingTheme(data);
  const layout = getLayoutVisualSpec(data);
  const pageTextColor = data.template.color_text || "#111827";
  const isPreview = mode === "preview";
  const content = resolveLandingContent(data, isPreview);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: isPreview ? "auto" : "100vh", bgcolor: "background.default", color: "text.primary" }}>
        <Box
          sx={{
            position: "relative",
            overflow: "hidden",
            minHeight: isPreview ? "auto" : layout.heroMinHeight,
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

              <LandingHeader data={data} isPreview={isPreview} />

              <Box
                sx={{
                  display: "grid",
                  gap: 3,
                  alignItems: "start",
                  gridTemplateColumns: layout.heroGridColumns,
                }}
              >
                <Stack spacing={3}>
                  <HeroContextCard data={data} layout={layout} isPreview={isPreview} />
                  <HeroMediaCard data={data} layout={layout} heroImageUrl={content.heroImageUrl} isPreview={isPreview} />
                </Stack>

                <LandingFormCard
                  data={data}
                  content={content}
                  layout={layout}
                  isPreview={isPreview}
                  formState={formState}
                  consentimento={consentimento}
                  submitError={submitError}
                  saving={saving}
                  submitted={submitted}
                  onInputChange={onInputChange}
                  onConsentimentoChange={onConsentimentoChange}
                  onSubmit={onSubmit}
                  onReset={onReset}
                  onResetDisabled={Boolean(gamificacao?.busy)}
                />
              </Box>
            </Stack>
          </Container>
        </Box>

        <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
          <Box
            sx={{
              display: "grid",
              gap: 3,
              alignItems: "start",
              gridTemplateColumns: layout.contentGridColumns,
            }}
          >
            {content.aboutDescription ? (
              <AboutEventCard data={data} aboutDescription={content.aboutDescription} pageTextColor={pageTextColor} />
            ) : null}

            <Stack spacing={3}>
              <BrandSummaryCard data={data} isPreview={isPreview} />
              <PreviewChecklistCard checklist={checklist} primaryColor={data.template.color_primary} />
            </Stack>
          </Box>
        </Container>

        <LandingGamificacaoSection
          gamificacoes={data.gamificacoes}
          isPreview={isPreview}
          gamificacao={gamificacao}
        />

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
                    component="img"
                    src="/logo-bb.svg"
                    alt="Banco do Brasil"
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                    }}
                  />
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
