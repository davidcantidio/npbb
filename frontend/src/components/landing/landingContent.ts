import type { LandingPageData } from "../../services/landing_public";

export type ResolvedLandingContent = {
  formTitle: string;
  formSubtitle: string | null;
  calloutMessage: string | null;
  ctaText: string;
};

function normalizeOptionalText(value?: string | null): string | null {
  const normalized = String(value ?? "").trim();
  return normalized.length ? normalized : null;
}

export function resolveLandingContent(data: LandingPageData): ResolvedLandingContent {
  const ativacaoNome = normalizeOptionalText(data.ativacao?.nome);
  const ativacaoDescricao = normalizeOptionalText(data.ativacao?.descricao);
  const eventoDescricaoCurta = normalizeOptionalText(data.evento.descricao_curta);
  const calloutMessage = normalizeOptionalText(data.ativacao?.mensagem_qrcode);
  const ctaCustomizado = normalizeOptionalText(data.evento.cta_personalizado);
  const ctaTemplate = normalizeOptionalText(data.template.cta_text);

  return {
    formTitle: ativacaoNome ?? data.evento.nome,
    formSubtitle: ativacaoDescricao ?? eventoDescricaoCurta,
    calloutMessage,
    ctaText: ctaCustomizado ?? ctaTemplate ?? "Confirmar presenca",
  };
}
