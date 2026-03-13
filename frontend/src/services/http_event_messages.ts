import { ApiError, toApiErrorCode, toApiErrorMessage } from "./http";

const EVENT_API_ERROR_MESSAGES: Record<string, string> = {
  EVENTO_NOT_FOUND: "Evento nao encontrado ou voce nao tem permissao para acessa-lo.",
  GAMIFICACAO_NOT_FOUND: "Gamificacao nao encontrada ou voce nao tem permissao para acessa-la.",
  FORBIDDEN: "Voce nao tem permissao para realizar esta acao.",
  NETWORK_ERROR:
    "Nao foi possivel conectar a API. Verifique se o backend esta rodando e se o CORS permite este endereco.",
  TIMEOUT:
    "Nao foi possivel conectar a API. Verifique se o backend esta rodando e se o CORS permite este endereco.",
};

/**
 * Reads normalized API error code from an unknown thrown value.
 * @param err Unknown error instance thrown by services.
 * @returns API error code when available.
 */
export function getEventApiErrorCode(err: unknown): string | null {
  return toApiErrorCode(err);
}

/**
 * Resolves user-facing error message from typed API errors.
 * @param err Unknown error instance thrown by services.
 * @param fallback Fallback message when no typed code is available.
 * @returns Human readable message for event workflow screens.
 */
export function getEventApiErrorMessage(err: unknown, fallback: string): string {
  const code = getEventApiErrorCode(err);
  if (code && EVENT_API_ERROR_MESSAGES[code]) {
    return EVENT_API_ERROR_MESSAGES[code];
  }
  return toApiErrorMessage(err, fallback);
}

/**
 * Extracts extra payload from API error body (e.g. dependencies for ATIVACAO_DELETE_BLOCKED).
 * @param err Unknown error instance thrown by services.
 * @returns extra object when available, null otherwise.
 */
export function getEventApiErrorExtra(err: unknown): Record<string, unknown> | null {
  if (!(err instanceof ApiError)) return null;
  if (!err.body || typeof err.body !== "object") return null;
  const extra = (err.body as { extra?: unknown })?.extra;
  return extra && typeof extra === "object" && !Array.isArray(extra) ? (extra as Record<string, unknown>) : null;
}
