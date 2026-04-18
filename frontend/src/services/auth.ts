import { fetchWithAuth, handleApiResponse } from "./http";

/** Login/sessao: alinhar ao proxy Vite (120s) para cold start / DB lenta sem abort prematuro. */
const AUTH_REQUEST_TIMEOUT_MS = 120_000;

/**
 * Credentials payload used to authenticate a user.
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Authenticated user returned by backend auth endpoints.
 */
export interface LoginUser {
  id: number;
  email: string;
  matricula?: string | null;
  diretoria_id?: number | null;
  status_aprovacao?: string | null;
  tipo_usuario: string;
  funcionario_id?: number | null;
  agencia_id?: number | null;
}

/**
 * Authentication response with access token and user profile.
 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: LoginUser;
}

export interface SessionStatusResponse {
  authenticated: boolean;
  user: LoginUser | null;
}

/**
 * Authenticates a user and returns access token plus profile payload.
 * @param payload Login credentials.
 * @returns Token and user profile from backend.
 * @throws Error When backend rejects credentials or network request fails.
 */
export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const res = await fetchWithAuth("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    retries: 0,
    timeoutMs: AUTH_REQUEST_TIMEOUT_MS,
  });
  return handleApiResponse<LoginResponse>(res);
}

/**
 * Loads authenticated user profile from current access token.
 * @param token Bearer token used for authorization.
 * @returns Current authenticated user data.
 * @throws Error When token is invalid/expired or request fails.
 */
export async function getMe(token?: string | null): Promise<LoginUser> {
  const res = await fetchWithAuth("/auth/me", {
    token: token || undefined,
    retries: 0,
    timeoutMs: AUTH_REQUEST_TIMEOUT_MS,
  });
  return handleApiResponse<LoginUser>(res);
}

export async function logout(): Promise<void> {
  await fetchWithAuth("/auth/logout", {
    method: "POST",
    retries: 0,
    timeoutMs: AUTH_REQUEST_TIMEOUT_MS,
  });
}

export async function refreshSession(token?: string | null): Promise<LoginResponse> {
  const res = await fetchWithAuth("/auth/refresh", {
    method: "POST",
    token: token || undefined,
    retries: 0,
    timeoutMs: AUTH_REQUEST_TIMEOUT_MS,
  });
  return handleApiResponse<LoginResponse>(res);
}

/**
 * Returns session status without failing when no authenticated session exists.
 * @param token Optional bearer token fallback.
 * @returns Session status and user payload when authenticated.
 */
export async function getSessionStatus(token?: string | null): Promise<SessionStatusResponse> {
  const res = await fetchWithAuth("/auth/session", {
    token: token || undefined,
    retries: 0,
    timeoutMs: AUTH_REQUEST_TIMEOUT_MS,
  });
  return handleApiResponse<SessionStatusResponse>(res);
}
