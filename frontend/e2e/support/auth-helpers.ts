import { expect, type APIRequestContext, type Page, request as playwrightRequest } from "@playwright/test";

import { API_URL } from "./test-urls";

export const SEEDED_USER = {
  email: "david.cantidio@npbb.com.br",
  password: "Senha123!",
} as const;

export const INVITE_TOKEN = "invite-secret";

export type AuthUser = {
  id: number;
  email: string;
  tipo_usuario: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}

export async function createApiContext(extraHTTPHeaders?: Record<string, string>): Promise<APIRequestContext> {
  return playwrightRequest.newContext({
    baseURL: API_URL,
    extraHTTPHeaders,
  });
}

export async function loginViaApi(
  api: APIRequestContext,
  credentials: { email: string; password: string } = SEEDED_USER,
): Promise<LoginResponse> {
  const response = await api.post("/auth/login", {
    data: credentials,
  });
  expect(response.ok()).toBeTruthy();
  return (await response.json()) as LoginResponse;
}

export async function loginViaUi(page: Page): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Email").fill(SEEDED_USER.email);
  await page.getByLabel("Senha").fill(SEEDED_USER.password);
  await Promise.all([
    page.waitForURL("**/success"),
    page.getByRole("button", { name: "Entrar" }).click(),
  ]);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
}

export function uniqueNpbbEmail(prefix = "playwright-e2e"): string {
  return `${prefix}.${Date.now()}@npbb.com.br`;
}
