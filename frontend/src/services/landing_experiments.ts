import type { LandingCtaVariant, LandingPageData } from "./landing_public";

const LANDING_SESSION_KEY = "npbb.landing.session-id";

function hashString(input: string) {
  let hash = 0;
  for (let index = 0; index < input.length; index += 1) {
    hash = (hash << 5) - hash + input.charCodeAt(index);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function getLandingSessionId() {
  if (typeof window === "undefined") return "server-session";
  const existing = window.localStorage.getItem(LANDING_SESSION_KEY);
  if (existing) return existing;
  const created = `landing-${Math.random().toString(36).slice(2, 10)}-${Date.now().toString(36)}`;
  window.localStorage.setItem(LANDING_SESSION_KEY, created);
  return created;
}

export function selectLandingCtaVariant(
  data: LandingPageData,
  sessionId: string,
): LandingCtaVariant | null {
  const variants = data.template.cta_variants || [];
  if (!data.template.cta_experiment_enabled || variants.length === 0) return null;
  const source = `${data.evento.id}:${data.ativacao_id ?? "evento"}:${data.template.categoria}:${sessionId}`;
  const index = hashString(source) % variants.length;
  return variants[index] || null;
}
