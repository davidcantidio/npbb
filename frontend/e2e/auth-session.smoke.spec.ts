import { expect, test } from "@playwright/test";

import { loginViaUi, SEEDED_USER } from "./support/auth-helpers";
import { API_URL } from "./support/test-urls";

test("keeps UI session stable across protected routes", async ({ page }) => {
  await loginViaUi(page);
  const userMenuButton = page.getByRole("button", { name: new RegExp(SEEDED_USER.email, "i") });
  await expect(userMenuButton).toBeVisible();

  const meAfterLogin = await page.context().request.get(`${API_URL}/auth/me`, {
    failOnStatusCode: false,
  });
  expect(meAfterLogin.status()).toBe(200);
  const meAfterLoginBody = (await meAfterLogin.json()) as { email: string };
  expect(meAfterLoginBody.email).toBe(SEEDED_USER.email);

  await page.goto("/success");
  await page.reload();
  await expect(userMenuButton).toBeVisible();

  const meAfterReload = await page.context().request.get(`${API_URL}/auth/me`, {
    failOnStatusCode: false,
  });
  expect(meAfterReload.status()).toBe(200);

  await page.goto("/eventos");
  await expect(page.getByRole("link", { name: "Evento Playwright NPBB", exact: true })).toBeVisible();

  await page.goto("/leads");
  await expect(page).toHaveURL(/\/leads\/importar$/);
  await expect(page.getByRole("heading", { name: "Importacao de Leads", exact: true })).toBeVisible();

  const leadsResponse = await page.context().request.get(`${API_URL}/leads?page=1&page_size=20`, {
    failOnStatusCode: false,
  });
  expect(leadsResponse.status()).toBe(200);
  const leadsBody = (await leadsResponse.json()) as {
    total: number;
    items: Array<{ nome: string | null; evento_nome: string | null }>;
  };
  expect(leadsBody.total).toBe(1);
  expect(leadsBody.items).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        nome: "Lead Playwright",
        evento_nome: "Evento Playwright NPBB",
      }),
    ]),
  );

  await userMenuButton.click();
  await page.getByRole("menuitem", { name: "Sair" }).click();

  await expect(page).toHaveURL(/\/login$/);

  const meAfterLogout = await page.context().request.get(`${API_URL}/auth/me`, {
    failOnStatusCode: false,
  });
  expect(meAfterLogout.status()).toBe(401);
});
