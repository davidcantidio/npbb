import { fetchWithAuth, handleApiResponse } from "./http";

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
  });
  return handleApiResponse<LoginResponse>(res);
}

/**
 * Loads authenticated user profile from current access token.
 * @param token Bearer token used for authorization.
 * @returns Current authenticated user data.
 * @throws Error When token is invalid/expired or request fails.
 */
export async function getMe(token: string): Promise<LoginUser> {
  const res = await fetchWithAuth("/auth/me", {
    token,
    retries: 0,
  });
  return handleApiResponse<LoginUser>(res);
}
