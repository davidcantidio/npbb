import { test, expect, request } from "@playwright/test";

const UI_BASE_URL = process.env.UI_BASE_URL || "http://localhost:5173";
const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";
const AUTH_USER = process.env.AUTH_USER || "agencia@agencia.com.br";
const AUTH_PASS = process.env.AUTH_PASS || "Senha123!";

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function login(page: any) {
  await page.goto(UI_BASE_URL);
  await page.getByLabel(/email/i).fill(AUTH_USER);
  await page.getByLabel(/senha/i).fill(AUTH_PASS);

  await Promise.all([
    page.waitForResponse(
      (resp: any) => resp.url().includes("/auth/login") && resp.request().method() === "POST" && resp.status() === 200,
    ),
    page.getByRole("button", { name: /entrar/i }).click(),
  ]);

  await page.waitForURL("**/success");
}

async function selectAutocomplete(page: any, label: string | RegExp, searchText: string, optionText: string) {
  const input = page.getByLabel(label);
  await input.click();
  await input.fill(searchText);
  await page.getByRole("option", { name: new RegExp(`^${escapeRegExp(optionText)}$`, "i") }).click();
}

test.describe("Eventos UI e2e", () => {
  test("login → cria evento → valida detalhe (e cleanup)", async ({ page }) => {
    await login(page);

    await page.goto(`${UI_BASE_URL}/eventos/novo`);
    await expect(page.getByRole("heading", { name: /novo evento/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /criar evento/i })).toBeEnabled();

    const nome = `E2E Evento ${Date.now()}`;
    const descricao = "Evento criado por teste e2e (Playwright)";
    const uf = "SE";
    const cidade = "Aracaju";
    const dataInicio = "2099-01-01";
    const dataFim = "2099-01-02";

    await page.getByLabel("Nome").fill(nome);
    await page.getByLabel(/descri/i).fill(descricao);

    await selectAutocomplete(page, "UF", uf, uf);
    await page.getByLabel("Cidade").fill(cidade);

    await page.getByLabel(/data de in/i).fill(dataInicio);
    await page.getByLabel(/data de fim/i).fill(dataFim);

    await selectAutocomplete(page, "Diretoria", "dimac", "dimac");
    await selectAutocomplete(page, "Tipo Evento", "Esporte", "Esporte");

    await Promise.all([
      page.waitForResponse(
        (resp: any) =>
          resp.url().includes("/evento/") && resp.request().method() === "POST" && resp.status() === 201,
      ),
      page.getByRole("button", { name: /criar evento/i }).click(),
    ]);

    await page.waitForURL(/\/eventos\/\d+$/);
    await page.waitForLoadState("networkidle");

    await expect(page.getByText(nome, { exact: true })).toBeVisible();
    await expect(page.getByText(descricao, { exact: true })).toBeVisible();
    await expect(page.getByText(cidade, { exact: true })).toBeVisible();
    await expect(page.getByText(uf, { exact: true })).toBeVisible();
    await expect(page.getByText("01/01/2099", { exact: true })).toBeVisible();
    await expect(page.getByText("02/01/2099", { exact: true })).toBeVisible();
    await expect(page.getByText(/previsto/i)).toBeVisible();

    const token = await page.evaluate(() => localStorage.getItem("access_token"));
    expect(token).toBeTruthy();

    const match = page.url().match(/\/eventos\/(\d+)$/);
    expect(match?.[1]).toBeTruthy();
    const eventoId = match ? Number(match[1]) : null;

    if (token && eventoId) {
      const api = await request.newContext({
        baseURL: API_BASE_URL,
        extraHTTPHeaders: { Authorization: `Bearer ${token}` },
      });
      const delRes = await api.delete(`/evento/${eventoId}`);
      expect(delRes.status()).toBe(204);
      await api.dispose();
    }
  });
});
