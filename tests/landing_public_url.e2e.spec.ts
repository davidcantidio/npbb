import { test, expect, request } from "@playwright/test";

const UI_BASE_URL = (process.env.UI_BASE_URL || "http://localhost:5173").replace(/\/+$/, "");
const API_BASE_URL = (process.env.API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");
const AUTH_USER = process.env.AUTH_USER || "agencia@agencia.com.br";
const AUTH_PASS = process.env.AUTH_PASS || "Senha123!";

type LoginResult = {
  accessToken: string | null;
};

async function login(page: any): Promise<LoginResult> {
  await page.goto(UI_BASE_URL);
  await page.getByLabel(/email/i).fill(AUTH_USER);
  await page.getByLabel(/senha/i).fill(AUTH_PASS);

  const [loginResponse] = await Promise.all([
    page.waitForResponse(
      (resp: any) =>
        resp.url().includes("/auth/login") &&
        resp.request().method() === "POST" &&
        resp.status() === 200,
    ),
    page.getByRole("button", { name: /entrar/i }).click(),
  ]);

  await page.waitForURL("**/success");
  const loginPayload = (await loginResponse.json()) as { access_token?: string };
  return {
    accessToken: loginPayload.access_token || null,
  };
}

type ApiContextResult = {
  api: Awaited<ReturnType<typeof request.newContext>>;
  tipos: { id: number; nome: string }[];
};

async function createApiContext(token: string): Promise<ApiContextResult> {
  const candidates = Array.from(
    new Set(
      [API_BASE_URL, `${API_BASE_URL}/api`, `${UI_BASE_URL}/api`, UI_BASE_URL].map((value) =>
        value.replace(/\/+$/, ""),
      ),
    ),
  );

  for (const baseURL of candidates) {
    const api = await request.newContext({
      baseURL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const tiposRes = await api.get("/evento/all/tipos-evento");
    const contentType = tiposRes.headers()["content-type"] || "";
    if (tiposRes.status() === 200 && contentType.includes("application/json")) {
      const tipos = (await tiposRes.json()) as { id: number; nome: string }[];
      if (Array.isArray(tipos) && tipos.length > 0) {
        return { api, tipos };
      }
    }
    await api.dispose();
  }

  throw new Error("Nao foi possivel resolver uma base de API valida para os endpoints de evento.");
}

test.describe("Landing publica URL", () => {
  test("botao de preview abre landing publica no host do frontend", async ({ page }) => {
    const { accessToken: token } = await login(page);
    expect(token).toBeTruthy();
    const { api, tipos } = await createApiContext(token as string);

    let eventoId: number | null = null;
    try {
      const createRes = await api.post("/evento", {
        data: {
          nome: `E2E Landing URL ${Date.now()}`,
          descricao: "Evento para validar URL publica da landing no preview",
          cidade: "Aracaju",
          estado: "SE",
          tipo_id: tipos[0]!.id,
          data_inicio_prevista: "2099-01-01",
          data_fim_prevista: "2099-01-02",
        },
      });
      expect(createRes.status()).toBe(201);
      const created = (await createRes.json()) as { id: number };
      eventoId = created.id;
      expect(typeof eventoId === "number" && eventoId > 0).toBeTruthy();

      await page.goto(`${UI_BASE_URL}/eventos/${eventoId}/formulario-lead`);
      await expect(page.getByText(/contexto da landing/i)).toBeVisible();

      const openLandingButton = page.getByRole("link", { name: /abrir landing p[uú]blica/i });
      await expect(openLandingButton).toBeVisible({ timeout: 20_000 });

      const href = await openLandingButton.getAttribute("href");
      expect(href).toBe(`${UI_BASE_URL}/landing/eventos/${eventoId}`);
      expect(href?.startsWith(`${API_BASE_URL}/landing/`)).toBeFalsy();

      const popupPromise = page.waitForEvent("popup");
      await openLandingButton.click();
      const popup = await popupPromise;
      await popup.waitForLoadState("domcontentloaded");
      await expect(popup).toHaveURL(`${UI_BASE_URL}/landing/eventos/${eventoId}`);
    } finally {
      if (eventoId) {
        const delRes = await api.delete(`/evento/${eventoId}`);
        expect([204, 404]).toContain(delRes.status());
      }
      await api.dispose();
    }
  });
});
