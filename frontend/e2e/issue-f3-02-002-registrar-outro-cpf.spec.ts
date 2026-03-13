import { expect, test, type Page, type Route } from "@playwright/test";

const EVENTO_ID = 10;
const ATIVACAO_UNICA_ID = 2;

function buildLandingPayload() {
  return {
    ativacao_id: ATIVACAO_UNICA_ID,
    ativacao: {
      id: ATIVACAO_UNICA_ID,
      nome: "Stand Unico",
      conversao_unica: true,
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
      ativacao_id: ATIVACAO_UNICA_ID,
      submit_url: "/leads",
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
      landing_url: `https://npbb.example/landing/ativacoes/${ATIVACAO_UNICA_ID}`,
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: `https://npbb.example/landing/ativacoes/${ATIVACAO_UNICA_ID}`,
    },
    lead_reconhecido: true,
    lead_ja_converteu_nesta_ativacao: true,
    token: "abc123",
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

test('ativacao unica reconhecida mostra CTA "Registrar outro CPF" e conclui novo cadastro', async ({ page }) => {
  await installAnalyticsMock(page);

  await page.route(
    `**/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_UNICA_ID}/landing**`,
    async (route) => {
      await fulfillJson(route, buildLandingPayload());
    },
  );

  await page.route("**/leads", async (route, request) => {
    expect(request.postDataJSON()).toMatchObject({
      nome: "Maria",
      email: "maria@example.com",
      event_id: EVENTO_ID,
      ativacao_id: ATIVACAO_UNICA_ID,
      cpf: "11144477735",
      consentimento_lgpd: true,
    });

    await fulfillJson(
      route,
      {
        lead_id: 99,
        event_id: EVENTO_ID,
        ativacao_id: ATIVACAO_UNICA_ID,
        ativacao_lead_id: 444,
        mensagem_sucesso: "Cadastro realizado com sucesso.",
        lead_reconhecido: true,
        conversao_registrada: true,
        bloqueado_cpf_duplicado: false,
      },
      201,
    );
  });

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_UNICA_ID}?token=abc123`);

  await expect(page.getByText("Stand Unico")).toBeVisible();
  await expect(page.getByText("Você já se cadastrou nesta ativação.")).toBeVisible();
  await expect(page.getByRole("button", { name: /registrar outro cpf/i })).toBeVisible();
  await expect(page.getByTestId("cpf-first-input")).toHaveCount(0);
  await expect(page.getByRole("textbox", { name: /nome/i })).toHaveCount(0);

  await page.getByRole("button", { name: /registrar outro cpf/i }).click();

  await expect(page.getByTestId("cpf-first-input")).toBeVisible();
  await expect(page.getByText("Você já se cadastrou nesta ativação.")).toHaveCount(0);

  await page.getByTestId("cpf-first-input").fill("111.444.777-35");
  await page.getByRole("button", { name: /continuar/i }).click();
  await page.getByRole("textbox", { name: /nome/i }).fill("Maria");
  await page.getByRole("textbox", { name: /email/i }).fill("maria@example.com");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: /confirmar presenca/i }).click();

  await expect(page.getByText("Cadastro realizado com sucesso.")).toBeVisible();
});
