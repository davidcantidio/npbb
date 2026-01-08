import { test, expect, request } from "@playwright/test";

const UI_BASE_URL = process.env.UI_BASE_URL || "http://localhost:5173";
const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";
const AUTH_USER = process.env.AUTH_USER || "agencia@agencia.com.br";
const AUTH_PASS = process.env.AUTH_PASS || "Senha123!";

async function login(page: any) {
  await page.goto(UI_BASE_URL);
  await page.getByLabel(/email/i).fill(AUTH_USER);
  await page.getByLabel(/senha/i).fill(AUTH_PASS);

  await Promise.all([
    page.waitForResponse(
      (resp: any) =>
        resp.url().includes("/auth/login") &&
        resp.request().method() === "POST" &&
        resp.status() === 200,
    ),
    page.getByRole("button", { name: /entrar/i }).click(),
  ]);

  await page.waitForURL("**/success");
}

test.describe("Ativacoes UI", () => {
  test("login -> abre aba de ativacoes do evento", async ({ page }) => {
    await login(page);

    const token = await page.evaluate(() => localStorage.getItem("access_token"));
    expect(token).toBeTruthy();

    const api = await request.newContext({
      baseURL: API_BASE_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    let eventoId: number | null = null;
    try {
      const tiposRes = await api.get("/evento/all/tipos");
      expect(tiposRes.status()).toBe(200);
      const tipos = (await tiposRes.json()) as { id: number; nome: string }[];
      expect(Array.isArray(tipos) && tipos.length > 0).toBeTruthy();
      const tipoId = tipos[0]?.id;
      expect(typeof tipoId === "number" && tipoId > 0).toBeTruthy();

      const createRes = await api.post("/evento", {
        data: {
          nome: `E2E Evento Ativacoes ${Date.now()}`,
          descricao: "Evento criado por teste e2e (Playwright) - Ativacoes",
          cidade: "Aracaju",
          estado: "SE",
          tipo_id: tipoId,
        },
      });
      expect(createRes.status()).toBe(201);
      const created = (await createRes.json()) as { id: number };
      eventoId = created.id;
      expect(typeof eventoId === "number" && eventoId > 0).toBeTruthy();

      await page.goto(`${UI_BASE_URL}/eventos/${eventoId}/ativacoes`);
      await expect(page.getByRole("heading", { name: /Ativaç/i })).toBeVisible();
      await expect(page.getByText(/Nova ativacao/i)).toBeVisible();
      await expect(page.getByText(/Ativacoes adicionadas/i)).toBeVisible();
      await expect(page.getByText(/Nenhuma ativacao adicionada/i)).toBeVisible();
    } finally {
      if (eventoId) {
        const delRes = await api.delete(`/evento/${eventoId}`);
        expect([204, 404]).toContain(delRes.status());
      }
      await api.dispose();
    }
  });
});

