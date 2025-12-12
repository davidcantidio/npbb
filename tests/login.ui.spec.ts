import { test, expect } from "@playwright/test";

const UI_BASE_URL = process.env.UI_BASE_URL || "http://localhost:5173";
const AUTH_USER = process.env.AUTH_USER || "admin@example.com";
const AUTH_PASS = process.env.AUTH_PASS || "senha-forte";

test.describe("Login UI", () => {
  test("faz login, redireciona e grava token no localStorage", async ({ page }) => {
    await page.goto(UI_BASE_URL);

    await page.getByLabel(/email/i).fill(AUTH_USER);
    await page.getByLabel(/senha/i).fill(AUTH_PASS);

    const [loginResponse] = await Promise.all([
      page.waitForResponse(
        (resp) => resp.url().includes("/auth/login") && resp.status() === 200,
      ),
      page.getByRole("button", { name: /entrar/i }).click(),
    ]);

    expect(loginResponse.ok()).toBeTruthy();

    await page.waitForURL("**/success");
    await page.waitForLoadState("networkidle");
    const token = await page.evaluate(() => localStorage.getItem("access_token"));
    expect(token).toBeTruthy();
    await expect(page.getByText(/dados do usuario/i)).toBeVisible();
  });

  test("mostra erro com senha errada", async ({ page }) => {
    await page.goto(UI_BASE_URL);
    await page.getByLabel(/email/i).fill(AUTH_USER);
    await page.getByLabel(/senha/i).fill("senha-incorreta");
    await page.getByRole("button", { name: /entrar/i }).click();

    const alert = page.getByRole("alert");
    await expect(alert).toContainText(/credenciais/i);
    await expect(page).toHaveURL(UI_BASE_URL + "/");
  });

  test("rota protegida sem login redireciona para login", async ({ page }) => {
    await page.goto(UI_BASE_URL);
    await page.evaluate(() => localStorage.clear());
    await page.goto(UI_BASE_URL + "/success");
    await expect(page).toHaveURL(/\/login|\/$/);
    await expect(page.getByRole("button", { name: /entrar/i })).toBeVisible();
  });
});
