import type { GamificacaoPublic } from "../../services/landing_public";

const DEFAULT_BLOCKED_MESSAGE = "Preencha o cadastro acima para participar";

export function getBlockedReasonText({
  leadSubmitted,
  blockedReason,
}: {
  leadSubmitted: boolean;
  blockedReason?: string | null;
}) {
  if (leadSubmitted) return null;
  const normalized = String(blockedReason ?? "").trim();
  if (normalized.length > 0) return normalized;
  return DEFAULT_BLOCKED_MESSAGE;
}

export function getGamificacaoByPriority(gamificacoes: GamificacaoPublic[]): GamificacaoPublic | null {
  return gamificacoes[0] ?? null;
}
