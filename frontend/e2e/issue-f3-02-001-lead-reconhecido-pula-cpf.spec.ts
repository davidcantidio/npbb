import { expect, test, type Page, type Route } from "@playwright/test";

const EVENTO_ID = 10;
const ATIVACAO_MULTIPLA_ID = 1;
const ATIVACAO_UNICA_ID = 2;

function buildLandingPayload(params: {
  ativacaoId: number;
  nome: string;
  conversaoUnica: boolean;
  leadReconhecido?: boolean;
}) {
  const { ativacaoId, nome, conversaoUnica, leadReconhecido = false } = params;
  return {
    ativacao_id: ativacaoId,
    ativacao: {
      id: ativacaoId,
      nome,
      conversao_unica: conversaoUnica,
      descricao: "Venha conhecer as novidades do BB.",
      mensagem_qrcode: "Escaneie o QR code no totem para se cadastrar.",
    },
    evento: {
      id: EVENTO_ID,
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
      event_id: EVENTO_ID,
      ativacao_id: ativacaoId,
      submit_url: `/landing/ativacoes/${ativacaoId}/submit`,
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
      landing_url: `https://npbb.example/landing/ativacoes/${ativacaoId}`,
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: `https://npbb.example/landing/ativacoes/${ativacaoId}`,
    },
    lead_reconhecido: leadReconhecido,
    token: null,
    gamificacoes: [],
  } as const;
}

async function fulfillJson(route: Route, body: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function installAnalyticsMock(page: Page) {
  await page.route("**/landing/analytics", async (route) => {
    await route.fulfill({ status: 204, body: "" });
  });
}

async function installLandingRoute(page: Page) {
  await page.route(/\/eventos\/10\/ativacoes\/\d+\/landing(?:\?.*)?$/, async (route, request) => {
    const match = request.url().match(/ativacoes\/(\d+)\/landing/);
    const ativacaoId = Number(match?.[1] || 0);

    await fulfillJson(
      route,
      buildLandingPayload({
        ativacaoId,
        nome: ativacaoId === ATIVACAO_UNICA_ID ? "Stand Unico" : "Stand Multiplo",
        conversaoUnica: ativacaoId === ATIVACAO_UNICA_ID,
        leadReconhecido: true,
      }),
    );
  });
}

test("lead reconhecido em ativacao multipla abre formulario direto", async ({ page }) => {
  await installAnalyticsMock(page);
  await installLandingRoute(page);

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_MULTIPLA_ID}`);

  await expect(page.getByText("Stand Multiplo")).toBeVisible();
  await expect(page.getByRole("textbox", { name: /nome/i })).toBeVisible();
  await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
  await expect(page.getByTestId("cpf-first-input")).toHaveCount(0);
  await expect(page.getByRole("textbox", { name: /^cpf/i })).toHaveCount(0);
});

test("ativacao multipla reconhecida registra conversao sem reenviar CPF", async ({ page }) => {
  await installAnalyticsMock(page);
  await installLandingRoute(page);

  await page.route(`**/landing/ativacoes/${ATIVACAO_MULTIPLA_ID}/submit`, async (route, request) => {
    expect(request.postDataJSON()).toMatchObject({
      nome: "Maria",
      email: "maria@example.com",
      consentimento_lgpd: true,
    });
    expect(request.postDataJSON()).not.toHaveProperty("cpf", "52998224725");

    await fulfillJson(route, {
      lead_id: 99,
      event_id: EVENTO_ID,
      ativacao_id: ATIVACAO_MULTIPLA_ID,
      ativacao_lead_id: 444,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    }, 201);
  });

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_MULTIPLA_ID}`);
  await page.getByRole("textbox", { name: /nome/i }).fill("Maria");
  await page.getByRole("textbox", { name: /email/i }).fill("maria@example.com");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: /confirmar presenca/i }).click();

  await expect(page.getByText("Cadastro realizado com sucesso.")).toBeVisible();
});

test("lead reconhecido em ativacao unica nao usa o fluxo direto desta issue", async ({ page }) => {
  await installAnalyticsMock(page);
  await installLandingRoute(page);

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_UNICA_ID}`);

  await expect(page.getByText("Stand Unico")).toBeVisible();
  await expect(page.getByTestId("cpf-first-input")).toBeVisible();
  await expect(page.getByRole("button", { name: /continuar/i })).toBeVisible();
  await expect(page.getByRole("textbox", { name: /nome/i })).toHaveCount(0);
});
