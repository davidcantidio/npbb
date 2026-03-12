import { fetchWithAuth, handleApiResponse } from "./http";

export type LandingTemplateConfig = {
  categoria: string;
  tema: string;
  mood: string;
  cta_text: string;
  color_primary: string;
  color_secondary: string;
  color_background: string;
  color_text: string;
  hero_layout: string;
  cta_variant: string;
  graphics_style: string;
  tone_of_voice: string;
  cta_experiment_enabled: boolean;
  cta_variants: LandingCtaVariant[];
};

export type LandingCtaVariant = {
  id: string;
  label: string;
  text: string;
};

export type LandingField = {
  key: string;
  label: string;
  input_type: string;
  required: boolean;
  autocomplete?: string | null;
  placeholder?: string | null;
};

export type LandingForm = {
  event_id: number;
  ativacao_id?: number | null;
  submit_url: string;
  campos: LandingField[];
  campos_obrigatorios: string[];
  campos_opcionais: string[];
  mensagem_sucesso: string;
  lgpd_texto: string;
  privacy_policy_url: string;
};

export type LandingBrand = {
  tagline: string;
};

export type LandingEvent = {
  id: number;
  nome: string;
  cta_personalizado?: string | null;
  descricao?: string | null;
  descricao_curta?: string | null;
  data_inicio?: string | null;
  data_fim?: string | null;
  cidade: string;
  estado: string;
};

export type LandingAccess = {
  landing_url?: string | null;
  qr_code_url?: string | null;
  url_promotor?: string | null;
};

export type LandingAtivacaoInfo = {
  id: number;
  nome: string;
  conversao_unica: boolean;
  descricao?: string | null;
  mensagem_qrcode?: string | null;
};

export type GamificacaoPublic = {
  id: number;
  nome: string;
  descricao: string;
  premio: string;
  titulo_feedback: string;
  texto_feedback: string;
};

export type LandingPageData = {
  ativacao_id?: number | null;
  ativacao?: LandingAtivacaoInfo | null;
  gamificacoes: GamificacaoPublic[];
  evento: LandingEvent;
  template: LandingTemplateConfig;
  formulario: LandingForm;
  marca: LandingBrand;
  acesso: LandingAccess;
  lead_reconhecido: boolean;
  lead_ja_converteu_nesta_ativacao: boolean;
  token?: string | null;
};

export type LandingSubmitPayload = {
  nome: string;
  sobrenome?: string;
  email: string;
  cpf?: string;
  telefone?: string;
  data_nascimento?: string;
  estado?: string;
  endereco?: string;
  interesses?: string;
  genero?: string;
  area_de_atuacao?: string;
  cta_variant_id?: string;
  landing_session_id?: string;
  consentimento_lgpd: boolean;
};

export type LandingSubmitResponse = {
  lead_id: number;
  event_id: number;
  ativacao_id?: number | null;
  ativacao_lead_id?: number | null;
  mensagem_sucesso: string;
  conversao_registrada: boolean;
  bloqueado_cpf_duplicado: boolean;
  token_reconhecimento?: string | null;
};

export type GamificacaoState = "presenting" | "active" | "completed";

export type GamificacaoBlockProps = {
  gamificacoes: GamificacaoPublic[];
  leadSubmitted: boolean;
  busy?: boolean;
  blockedReason?: string | null;
  resetVersion?: number;
  onComplete: (gamificacaoId: number) => Promise<void> | void;
  onReset: () => void;
};

export type GamificacaoCompletePayload = {
  gamificacao_id: number;
  gamificacao_completed: boolean;
};

export type GamificacaoCompleteResponse = {
  ativacao_lead_id: number;
  gamificacao_id: number;
  gamificacao_completed: boolean;
  gamificacao_completed_at?: string | null;
};

export type LandingAnalyticsTrackPayload = {
  event_id: number;
  ativacao_id?: number | null;
  categoria: string;
  tema: string;
  event_name: string;
  cta_variant_id?: string | null;
  landing_session_id?: string | null;
};

export type LandingPageDataRaw = Omit<LandingPageData, "gamificacoes"> & {
  ativacao?:
    | (Omit<LandingAtivacaoInfo, "conversao_unica"> & {
        conversao_unica?: boolean | null;
      })
    | null;
  gamificacoes?: GamificacaoPublic[] | null;
  lead_reconhecido?: boolean | null;
  lead_ja_converteu_nesta_ativacao?: boolean | null;
  token?: string | null;
};

export type GetLandingByEventoOptions = {
  templateOverride?: string | null;
};

export type GetLandingByEventoAtivacaoOptions = {
  token?: string | null;
};

export type LandingPreviewFieldInput = {
  nome_campo: string;
  obrigatorio: boolean;
  ordem: number;
};

export type PreviewEventoLandingPayload = {
  template_id?: number | null;
  template_override?: string | null;
  cta_personalizado?: string | null;
  descricao_curta?: string | null;
  campos?: LandingPreviewFieldInput[];
};

export type PreviewEventoLandingOptions = {
  signal?: AbortSignal;
};

export function normalizeLandingPageData(payload: LandingPageDataRaw): LandingPageData {
  return {
    ...payload,
    ativacao: payload.ativacao
      ? {
          ...payload.ativacao,
          // Preserve CPF-first as the safe fallback if older payloads omit the conversion rule.
          conversao_unica:
            typeof payload.ativacao.conversao_unica === "boolean"
              ? payload.ativacao.conversao_unica
              : true,
        }
      : null,
    gamificacoes: Array.isArray(payload.gamificacoes) ? payload.gamificacoes : [],
    lead_reconhecido: Boolean(payload.lead_reconhecido),
    lead_ja_converteu_nesta_ativacao: Boolean(payload.lead_ja_converteu_nesta_ativacao),
    token: typeof payload.token === "string" && payload.token.trim() ? payload.token.trim() : null,
  };
}

function buildEventoLandingPath(eventoId: number, options?: GetLandingByEventoOptions): string {
  const templateOverride = String(options?.templateOverride || "").trim();
  if (!templateOverride) {
    return `/eventos/${eventoId}/landing`;
  }

  const params = new URLSearchParams({ template_override: templateOverride });
  return `/eventos/${eventoId}/landing?${params.toString()}`;
}

function buildEventoAtivacaoLandingPath(
  eventoId: number,
  ativacaoId: number,
  options?: GetLandingByEventoAtivacaoOptions,
): string {
  const token = String(options?.token || "").trim();
  const basePath = `/eventos/${eventoId}/ativacoes/${ativacaoId}/landing`;
  if (!token) {
    return basePath;
  }

  const params = new URLSearchParams({ token });
  return `${basePath}?${params.toString()}`;
}

export async function getLandingByEvento(
  eventoId: number,
  options?: GetLandingByEventoOptions,
): Promise<LandingPageData> {
  const res = await fetchWithAuth(buildEventoLandingPath(eventoId, options), { retries: 0 });
  const payload = await handleApiResponse<LandingPageDataRaw>(res);
  return normalizeLandingPageData(payload);
}

export async function getLandingByEventoAtivacao(
  eventoId: number,
  ativacaoId: number,
  options?: GetLandingByEventoAtivacaoOptions,
): Promise<LandingPageData> {
  const res = await fetchWithAuth(buildEventoAtivacaoLandingPath(eventoId, ativacaoId, options), { retries: 0 });
  const payload = await handleApiResponse<LandingPageDataRaw>(res);
  return normalizeLandingPageData(payload);
}

export async function previewEventoLanding(
  token: string,
  eventoId: number,
  payload: PreviewEventoLandingPayload,
  options?: PreviewEventoLandingOptions,
): Promise<LandingPageData> {
  const res = await fetchWithAuth(`/evento/${eventoId}/landing-preview`, {
    token,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
    signal: options?.signal,
  });
  const data = await handleApiResponse<LandingPageDataRaw>(res);
  return normalizeLandingPageData(data);
}

export async function getLandingByAtivacao(ativacaoId: number): Promise<LandingPageData> {
  const res = await fetchWithAuth(`/ativacoes/${ativacaoId}/landing`, { retries: 0 });
  const payload = await handleApiResponse<LandingPageDataRaw>(res);
  return normalizeLandingPageData(payload);
}

export async function submitLandingForm(
  submitUrl: string,
  payload: LandingSubmitPayload,
): Promise<LandingSubmitResponse> {
  const res = await fetchWithAuth(submitUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
  });
  return handleApiResponse<LandingSubmitResponse>(res);
}

export async function trackLandingAnalytics(payload: LandingAnalyticsTrackPayload): Promise<void> {
  const res = await fetchWithAuth("/landing/analytics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
  });
  await handleApiResponse(res);
}

export async function completeGamificacao(
  ativacaoLeadId: number,
  payload: GamificacaoCompletePayload,
): Promise<GamificacaoCompleteResponse> {
  const res = await fetchWithAuth(`/ativacao-leads/${ativacaoLeadId}/gamificacao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
  });
  return handleApiResponse<GamificacaoCompleteResponse>(res);
}
