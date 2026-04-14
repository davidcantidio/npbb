import path from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

import { loginViaUi } from "./support/auth-helpers";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const xlsxFixturePath = path.resolve(
  __dirname,
  "..",
  "..",
  "backend",
  "tests",
  "fixtures",
  "lead_import_sample.xlsx",
);

test("uploads an XLSX lead file through the browser and opens mapping", async ({ page }) => {
  await loginViaUi(page);
  await page.goto("/leads/importar");

  await expect(page.getByRole("heading", { name: "Importacao de Leads", exact: true })).toBeVisible();

  await page.getByRole("combobox", { name: /plataforma de origem/i }).click();
  await page.getByRole("option", { name: "manual" }).click();

  await page.getByRole("combobox", { name: /evento de referencia/i }).click();
  await page.getByRole("option").filter({ hasNotText: /selecione o evento/i }).first().click();

  const fileInput = page.locator('input[type="file"]');
  await expect(fileInput).toHaveCount(1);
  // The MUI upload button hides the real input; Playwright 1.58 setInputFiles supports that directly.
  await fileInput.setInputFiles(xlsxFixturePath);
  await expect(page.getByText("lead_import_sample.xlsx")).toBeVisible();

  const [createBatchResponse, previewResponse] = await Promise.all([
    page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "POST" && pathname === "/leads/batches" && response.status() === 201;
    }),
    page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return (
        response.request().method() === "GET" &&
        /^\/leads\/batches\/\d+\/preview\/?$/.test(pathname) &&
        response.status() === 200
      );
    }),
    page.getByRole("button", { name: "Enviar para Bronze" }).click(),
  ]);

  expect(createBatchResponse.ok()).toBe(true);
  expect(previewResponse.ok()).toBe(true);
  await expect(page.getByText(/Preview do lote #\d+/)).toBeVisible();
  await expect(page.getByText(/Colunas detectadas:/)).toBeVisible();

  await Promise.all([
    page.waitForURL(/\/leads\/importar\?step=mapping&batch_id=\d+/),
    page.getByRole("button", { name: "Ir para Mapeamento" }).click(),
  ]);

  await expect(page.getByRole("heading", { name: "Mapeamento de Colunas", exact: true })).toBeVisible();
  await expect(page.getByPlaceholder("Selecione ou pesquise o evento...")).toHaveCount(0);
});
