import { expect, test, type Page, type Route } from "@playwright/test";

import { loginViaUi } from "./support/auth-helpers";

const EVENTO_ID = 321;

type AtivacaoFixture = {
  id: number;
  nome: string;
  descricao: string | null;
  mensagem_qrcode: string | null;
  landing_url: string;
  qr_code_url: string | null;
  url_promotor: string;
  checkin_unico: boolean;
};

async function fulfillJson(route: Route, body: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function installAtivacoesPageRoutes(page: Page, ativacoes: AtivacaoFixture[]) {
  await page.route(`**/evento/${EVENTO_ID}`, async (route) => {
    await fulfillJson(route, {
      id: EVENTO_ID,
      nome: "Evento QR Operador",
    });
  });

  await page.route(`**/evento/${EVENTO_ID}/gamificacoes`, async (route) => {
    await fulfillJson(route, []);
  });

  await page.route(`**/evento/${EVENTO_ID}/ativacoes`, async (route) => {
    await fulfillJson(
      route,
      ativacoes.map((ativacao) => ({
        ...ativacao,
        evento_id: EVENTO_ID,
        gamificacao_id: null,
        redireciona_pesquisa: false,
        termo_uso: false,
        gera_cupom: false,
        created_at: "2026-03-01T10:00:00Z",
        updated_at: "2026-03-02T10:00:00Z",
      })),
    );
  });
}

test("operador visualiza o qr e baixa o arquivo com extensao coerente", async ({ page }) => {
  await loginViaUi(page);

  await page.route("**/qr/ativacao-101.svg", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "image/svg+xml",
      body: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10" fill="black" /></svg>`,
    });
  });

  await installAtivacoesPageRoutes(page, [
    {
      id: 101,
      nome: "Stand Principal",
      descricao: "QR pronto para impressao.",
      mensagem_qrcode: "Escaneie para participar.",
      landing_url: "https://npbb.example/landing/ativacoes/101",
      qr_code_url: "qr/ativacao-101.svg",
      url_promotor: "https://npbb.example/promotor/101",
      checkin_unico: false,
    },
  ]);

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes`);

  await expect(page.getByRole("heading", { name: "Ativações", exact: true })).toBeVisible();
  const row = page.getByRole("row", { name: /stand principal/i });
  await row.getByRole("button", { name: /visualizar/i }).click();

  await expect(page.getByTestId("ativacao-qr-image")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /baixar qr/i }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toBe("ativacao-101-qr.svg");
});

test("operador ve placeholder quando a ativacao ainda nao tem qr_code_url", async ({ page }) => {
  await loginViaUi(page);

  await installAtivacoesPageRoutes(page, [
    {
      id: 202,
      nome: "Stand Secundario",
      descricao: "Ainda aguardando o gerador de QR.",
      mensagem_qrcode: null,
      landing_url: "https://npbb.example/landing/ativacoes/202",
      qr_code_url: null,
      url_promotor: "https://npbb.example/promotor/202",
      checkin_unico: true,
    },
  ]);

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes`);

  const row = page.getByRole("row", { name: /stand secundario/i });
  await row.getByRole("button", { name: /visualizar/i }).click();

  await expect(page.getByTestId("ativacao-qr-placeholder")).toContainText(
    "QR ainda nao disponivel para esta ativacao.",
  );
  await expect(page.getByRole("button", { name: /baixar qr/i })).toBeDisabled();
});
