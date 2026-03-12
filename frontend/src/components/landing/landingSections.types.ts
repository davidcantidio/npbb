import type {
  GamificacaoPublic,
  LandingPageData,
  LandingSubmitResponse,
} from "../../services/landing_public";
import type { ResolvedLandingContent } from "./landingContent";
import type { LayoutVisualSpec } from "./landingStyle";

export type LandingFormState = Record<string, string>;

export type LandingGamificacaoConfig = {
  leadSubmitted: boolean;
  busy?: boolean;
  blockedReason?: string | null;
  resetVersion?: number;
  onComplete: (gamificacaoId: number) => Promise<void> | void;
  onReset: () => void;
};

export type LandingFormCardProps = {
  data: LandingPageData;
  content: ResolvedLandingContent;
  layout: LayoutVisualSpec;
  isPreview: boolean;
  cpfFirstEnabled?: boolean;
  cpfFirstUnlocked?: boolean;
  formState: LandingFormState;
  consentimento: boolean;
  submitError: string | null;
  saving: boolean;
  submitted: LandingSubmitResponse | null;
  onInputChange?: (key: string, value: string) => void;
  onCpfFirstContinue?: () => void;
  onConsentimentoChange?: (checked: boolean) => void;
  onSubmit?: () => void;
  onReset?: () => void;
  onResetDisabled?: boolean;
};

export type LandingGamificacaoSectionProps = {
  gamificacoes: GamificacaoPublic[];
  layout: LayoutVisualSpec;
  isPreview: boolean;
  gamificacao?: LandingGamificacaoConfig;
};
