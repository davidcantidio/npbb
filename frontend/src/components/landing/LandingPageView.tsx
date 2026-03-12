import {
  Box,
  CssBaseline,
  Stack,
  ThemeProvider,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

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
  cpfFirstEnabled?: boolean;
  cpfFirstUnlocked?: boolean;
  formState?: LandingFormState;
  consentimento?: boolean;
  submitError?: string | null;
  saving?: boolean;
  submitted?: LandingSubmitResponse | null;
  onInputChange?: (key: string, value: string) => void;
  onCpfFirstContinue?: () => void;
  onConsentimentoChange?: (checked: boolean) => void;
  onSubmit?: () => void;
  onReset?: () => void;
  gamificacao?: LandingGamificacaoConfig;
};

export default function LandingPageView({
  data,
  mode = "public",
  cpfFirstEnabled = false,
  cpfFirstUnlocked = false,
  formState = {},
  consentimento = false,
  submitError = null,
  saving = false,
  submitted = null,
  onInputChange,
  onCpfFirstContinue,
  onConsentimentoChange,
  onSubmit,
  onReset,
  gamificacao,
}: LandingPageViewProps) {
  const theme = buildLandingTheme(data);
  const layout = getLayoutVisualSpec(data);
  const isPreview = mode === "preview";
  const backgroundLayerMode = isPreview ? "embedded" : "fixed";
  const sectionMinHeight = isPreview ? "auto" : "100vh";
  const contentMinHeight = isPreview ? "auto" : "calc(100vh - 48px)";
  const content = resolveLandingContent(data);

  return (
    <ThemeProvider theme={theme}>
      {!isPreview ? <CssBaseline /> : null}
      <FullPageBackground data={data} fullHeight={!isPreview} layerMode={backgroundLayerMode}>
        <Box
          sx={{
            position: "relative",
            minHeight: sectionMinHeight,
            px: { xs: 2, md: 3 },
            py: isPreview ? { xs: 2, md: 3 } : { xs: 3, md: 5 },
            color: "text.primary",
          }}
        >
          {isPreview ? <LandingPreviewBadge layout={layout} /> : null}

          <Box
            sx={{
              minHeight: contentMinHeight,
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
                py: isPreview ? { xs: 2, md: 3 } : { xs: 4, md: 6 },
              }}
            >
              <FormCard
                data={data}
                content={content}
                layout={layout}
                isPreview={isPreview}
                cpfFirstEnabled={cpfFirstEnabled}
                cpfFirstUnlocked={cpfFirstUnlocked}
                formState={formState}
                consentimento={consentimento}
                submitError={submitError}
                saving={saving}
                submitted={submitted}
                onInputChange={onInputChange}
                onCpfFirstContinue={onCpfFirstContinue}
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
