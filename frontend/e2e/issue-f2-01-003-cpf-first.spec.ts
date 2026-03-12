import { expect, test, type Page, type Route } from "@playwright/test";

const CANONICAL_URL = "/eventos/10/ativacoes/1";
const LANDING_API_PATTERN = "**/eventos/10/ativacoes/1/landing*";
const SUBMIT_API_PATTERN = "**/landing/ativacoes/1/submit";
const ANALYTICS_API_PATTERN = "**/landing/analytics";

const landingPayload = {
  ativacao_id: 1,
  ativacao: {
    id: 1,
    nome: "Stand Principal",
    conversao_unica: false,
    descricao: "Venha conhecer as novidades do BB.",
    mensagem_qrcode: "Escaneie o QR code no totem para se cadastrar.",
  },
  evento: {
    id: 10,
    nome: "BB Summit 2026",
    descricao: "Descricao completa do evento.",
    descricao_curta: "Resumo curto do evento.",
    data_inicio: "2026-04-10",
    data_fim: "2026-04-12",
    cidade: "Brasilia",
    estado: "DF",
  },
  template: {
    categoria: "corporativo",
    tema: "Corp",
    mood: "Profissional, confiavel e estrategico.",
    cta_text: "Confirmar presenca",
    color_primary: "#1E3A8A",
    color_secondary: "#FCFC30",
    color_background: "#F5F7FB",
    color_text: "#111827",
    hero_layout: "split",
    cta_variant: "outlined",
    graphics_style: "grid",
    tone_of_voice: "attention",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
  formulario: {
    event_id: 10,
    ativacao_id: 1,
    submit_url: "/landing/ativacoes/1/submit",
    campos: [
      {
        key: "nome",
        label: "Nome",
        input_type: "text",
        required: true,
        autocomplete: "name",
        placeholder: "Como voce gostaria de ser chamado?",
      },
      {
        key: "email",
        label: "Email",
        input_type: "email",
        required: true,
        autocomplete: "email",
        placeholder: "voce@exemplo.com",
      },
      {
        key: "cpf",
        label: "CPF",
        input_type: "text",
        required: false,
        autocomplete: "off",
        placeholder: "00000000000",
      },
    ],
    campos_obrigatorios: ["nome", "email"],
    campos_opcionais: ["cpf"],
    mensagem_sucesso: "Cadastro realizado com sucesso.",
    lgpd_texto: "Ao enviar seus dados, voce concorda com o tratamento das informacoes.",
    privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
  },
  marca: {
    tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
  },
  acesso: {
    landing_url: "https://npbb.example/landing/ativacoes/1",
    qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
    url_promotor: "https://npbb.example/landing/ativacoes/1",
  },
  gamificacoes: [],
} as const;

async function fulfillJson(route: Route, body: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function installCpfFirstMocks(page: Page) {
  await page.route(LANDING_API_PATTERN, async (route) => {
    await fulfillJson(route, landingPayload);
  });

  await page.route(ANALYTICS_API_PATTERN, async (route) => {
    await route.fulfill({ status: 204, body: "" });
  });

  await page.route(SUBMIT_API_PATTERN, async (route) => {
    await fulfillJson(route, {
      lead_id: 99,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: null,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
    });
  });
}

async function openLanding(page: Page) {
  await installCpfFirstMocks(page);
  await page.goto(CANONICAL_URL);
  await expect(page.getByText("Stand Principal")).toBeVisible();
  await expect(page.getByTestId("form-card-paper")).toBeVisible();
}

async function unlockCpfFirst(page: Page, cpf = "529.982.247-25") {
  await page.getByTestId("cpf-first-input").fill(cpf);
  await page.getByRole("button", { name: /continuar/i }).click();
}

test("mostra apenas o campo CPF no primeiro acesso", async ({ page }) => {
  await openLanding(page);

  await expect(page.getByTestId("cpf-first-input")).toBeVisible();
  await expect(page.getByRole("textbox", { name: /nome/i })).toHaveCount(0);
  await expect(page.getByRole("textbox", { name: /email/i })).toHaveCount(0);
  await expect(page.getByRole("checkbox")).toHaveCount(0);
});

test("exibe erro para CPF invalido", async ({ page }) => {
  await openLanding(page);
  await unlockCpfFirst(page, "52998224726");

  await expect(page.getByText("Informe um CPF valido.")).toBeVisible();
  await expect(page.getByRole("textbox", { name: /nome/i })).toHaveCount(0);
  await expect(page.getByRole("textbox", { name: /email/i })).toHaveCount(0);
});

test("libera o formulario completo para CPF valido", async ({ page }) => {
  await openLanding(page);
  await unlockCpfFirst(page);

  await expect(page.getByRole("textbox", { name: /nome/i })).toBeVisible();
  await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
  await expect(page.getByRole("checkbox")).toBeVisible();
  await expect(page.locator('input[value="52998224725"]')).toBeDisabled();
});

test("submete o formulario com sucesso apos validar CPF", async ({ page }) => {
  await openLanding(page);
  await unlockCpfFirst(page);

  const submitRequestPromise = page.waitForRequest((request) => {
    return request.method() === "POST" && /\/landing\/ativacoes\/1\/submit$/.test(request.url());
  });

  await page.getByRole("textbox", { name: /nome/i }).fill("Maria");
  await page.getByRole("textbox", { name: /email/i }).fill("maria@example.com");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: /confirmar presenca/i }).click();

  const submitRequest = await submitRequestPromise;
  expect(submitRequest.postDataJSON()).toMatchObject({
    nome: "Maria",
    email: "maria@example.com",
    cpf: "52998224725",
    consentimento_lgpd: true,
  });

  await expect(page.getByText("Cadastro concluido")).toBeVisible();
  await expect(page.getByText("Cadastro realizado com sucesso.")).toBeVisible();
});
