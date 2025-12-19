import { test, expect, request } from "@playwright/test";

const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";
const API_USER = process.env.API_USER || "agencia@agencia.com.br";
const API_PASS = process.env.API_PASS || "Senha123!";

test.describe("Auth API e2e", () => {
  test("login sucesso e /auth/me com token válido", async () => {
    const api = await request.newContext({ baseURL: API_BASE_URL });

    const loginRes = await api.post("/auth/login", {
      data: { email: API_USER, password: API_PASS },
    });
    expect(loginRes.status()).toBe(200);
    const loginJson = await loginRes.json();
    expect(loginJson.access_token).toBeTruthy();
    expect(loginJson.user.email).toBe(API_USER);

    const token = loginJson.access_token as string;
    const meRes = await api.get("/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(meRes.status()).toBe(200);
    const meJson = await meRes.json();
    expect(meJson.email).toBe(API_USER);
  });

  test("login falha com credenciais inválidas", async () => {
    const api = await request.newContext({ baseURL: API_BASE_URL });
    const res = await api.post("/auth/login", {
      data: { email: API_USER, password: "errada" },
    });
    expect(res.status()).toBe(401);
  });
});
