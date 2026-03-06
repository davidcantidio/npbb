import type { LandingPageData } from "../../services/landing_public";

export type ResolvedLandingContent = {
  formTitle: string;
  formSubtitle: string;
  aboutDescription: string | null;
  calloutMessage: string | null;
  ctaText: string;
  heroImageUrl: string | null;
};

function normalizeOptionalText(value?: string | null): string | null {
  const normalized = String(value ?? "").trim();
  return normalized.length ? normalized : null;
}

function getDefaultFormSubtitle(isPreview: boolean): string {
  return isPreview
    ? "Preview do formulario publicado para este evento."
    : "Preencha os dados abaixo para receber novidades e ativar sua participacao.";
}

export function resolveLandingContent(data: LandingPageData, isPreview: boolean): ResolvedLandingContent {
  const ativacaoNome = normalizeOptionalText(data.ativacao?.nome);
  const ativacaoDescricao = normalizeOptionalText(data.ativacao?.descricao);
  const eventoDescricaoCurta = normalizeOptionalText(data.evento.descricao_curta);
  const eventoDescricao = normalizeOptionalText(data.evento.descricao);
  const calloutMessage = normalizeOptionalText(data.ativacao?.mensagem_qrcode);
  const ctaCustomizado = normalizeOptionalText(data.evento.cta_personalizado);
  const ctaTemplate = normalizeOptionalText(data.template.cta_text);

  return {
    formTitle: ativacaoNome ?? data.evento.nome,
    formSubtitle: ativacaoDescricao ?? eventoDescricaoCurta ?? eventoDescricao ?? getDefaultFormSubtitle(isPreview),
    aboutDescription: ativacaoDescricao ?? eventoDescricaoCurta ?? eventoDescricao,
    calloutMessage,
    ctaText: ctaCustomizado ?? ctaTemplate ?? "Confirmar presenca",
    heroImageUrl: normalizeOptionalText(data.marca.url_hero_image),
  };
}
