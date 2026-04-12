/** Quando true, o módulo Patrocinados usa a API `/sponsorship` em vez do localStorage. */
export function useSponsorshipApiMode(): boolean {
  return String(import.meta.env.VITE_SPONSORSHIP_USE_API || "").toLowerCase() === "true";
}
