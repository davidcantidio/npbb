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
  versao_logo: string;
  url_hero_image: string;
  hero_alt: string;
};

export type LandingEvent = {
  id: number;
  nome: string;
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

export type LandingPageData = {
  ativacao_id?: number | null;
  evento: LandingEvent;
  template: LandingTemplateConfig;
  formulario: LandingForm;
  marca: LandingBrand;
  acesso: LandingAccess;
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
  mensagem_sucesso: string;
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

export async function getLandingByEvento(eventoId: number): Promise<LandingPageData> {
  const res = await fetchWithAuth(`/eventos/${eventoId}/landing`, { retries: 0 });
  return handleApiResponse<LandingPageData>(res);
}

export async function getLandingByAtivacao(ativacaoId: number): Promise<LandingPageData> {
  const res = await fetchWithAuth(`/ativacoes/${ativacaoId}/landing`, { retries: 0 });
  return handleApiResponse<LandingPageData>(res);
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
