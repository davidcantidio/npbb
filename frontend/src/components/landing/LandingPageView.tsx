import {
  Box,
  CssBaseline,
  Stack,
  ThemeProvider,
} from "@mui/material";

import type {
  LandingPageData,
  LandingSubmitResponse,
} from "../../services/landing_public";
import FormCard from "./FormCard";
import FullPageBackground from "./FullPageBackground";
import LandingPreviewBadge from "./LandingPreviewBadge";
import MinimalFooter from "./MinimalFooter";
import { FORM_ONLY_CONTENT_WIDTH_SX } from "./formOnlySurface";
import { resolveLandingContent } from "./landingContent";
import { LandingGamificacaoSection } from "./landingSections.gamificacao";
import type {
  LandingFormState,
  LandingGamificacaoConfig,
} from "./landingSections.types";
import {
  buildLandingTheme,
  getLayoutVisualSpec,
} from "./landingStyle";

export { buildLandingTheme } from "./landingStyle";
export { formatDateRange, getFieldLabel } from "./landingHelpers";

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
}: LandingPageViewProps) {
  const theme = buildLandingTheme(data);
  const layout = getLayoutVisualSpec(data);
  const isPreview = mode === "preview";
  const content = resolveLandingContent(data);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FullPageBackground data={data}>
        <Box
          sx={{
            position: "relative",
            minHeight: "100vh",
            px: { xs: 2, md: 3 },
            py: { xs: 3, md: 5 },
            color: "text.primary",
          }}
        >
          {isPreview ? <LandingPreviewBadge layout={layout} /> : null}

          <Box
            sx={{
              minHeight: "calc(100vh - 48px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Stack
              spacing={3}
              alignItems="center"
              sx={{
                width: "100%",
                py: { xs: 4, md: 6 },
              }}
            >
              <FormCard
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

              <LandingGamificacaoSection
                gamificacoes={data.gamificacoes}
                layout={layout}
                isPreview={isPreview}
                gamificacao={gamificacao}
              />

              <Box
                sx={{
                  ...FORM_ONLY_CONTENT_WIDTH_SX,
                  borderTop: `1px solid ${alpha(data.template.color_primary, 0.12)}`,
                  pt: 3,
                }}
              >
                <MinimalFooter
                  tagline={data.marca.tagline}
                  textColor={layout.footerTextColor}
                  privacyPolicyUrl={data.formulario.privacy_policy_url}
                />
              </Box>
            </Stack>
          </Box>
        </Box>
      </FullPageBackground>
    </ThemeProvider>
  );
}
