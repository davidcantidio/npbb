import type {
  GamificacaoPublic,
  LandingPageData,
  LandingSubmitResponse,
} from "../../services/landing_public";
import type { ResolvedLandingContent } from "./landingContent";
import type { LayoutVisualSpec } from "./landingStyle";

export type LandingFormState = Record<string, string>;

export type LandingPreviewChecklistItem = {
  label: string;
  ok: boolean;
  helper: string;
};

export type LandingGamificacaoConfig = {
  leadSubmitted: boolean;
  busy?: boolean;
  blockedReason?: string | null;
  resetVersion?: number;
  onComplete: (gamificacaoId: number) => Promise<void> | void;
  onReset: () => void;
};

export type HeroContextCardProps = {
  data: LandingPageData;
  layout: LayoutVisualSpec;
  isPreview: boolean;
};

export type HeroMediaCardProps = {
  data: LandingPageData;
  layout: LayoutVisualSpec;
  heroImageUrl: string | null;
  isPreview: boolean;
};

export type LandingFormCardProps = {
  data: LandingPageData;
  content: ResolvedLandingContent;
  layout: LayoutVisualSpec;
  isPreview: boolean;
  formState: LandingFormState;
  consentimento: boolean;
  submitError: string | null;
  saving: boolean;
  submitted: LandingSubmitResponse | null;
  onInputChange?: (key: string, value: string) => void;
  onConsentimentoChange?: (checked: boolean) => void;
  onSubmit?: () => void;
  onReset?: () => void;
  onResetDisabled?: boolean;
};

export type AboutEventCardProps = {
  data: LandingPageData;
  aboutDescription: string;
  pageTextColor: string;
};

export type BrandSummaryCardProps = {
  data: LandingPageData;
  isPreview: boolean;
};

export type LandingGamificacaoSectionProps = {
  gamificacoes: GamificacaoPublic[];
  isPreview: boolean;
  gamificacao?: LandingGamificacaoConfig;
};
