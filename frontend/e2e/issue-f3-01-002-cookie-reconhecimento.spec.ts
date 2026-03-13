import { expect, test, type Page, type Route } from "@playwright/test";

const EVENTO_ID = 10;
const ATIVACAO_INICIAL_ID = 1;
const ATIVACAO_RETORNO_ID = 2;
const COOKIE_TOKEN = "cookie-token-123";
const URL_TOKEN = "url-token-456";

function buildLandingPayload(params: {
  ativacaoId: number;
  nome: string;
  conversaoUnica?: boolean;
  leadReconhecido?: boolean;
  token?: string | null;
}) {
  const { ativacaoId, nome, conversaoUnica = true, leadReconhecido = false, token = null } = params;
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
      landing_url: `https://npbb.example/landing/ativacoes/${ativacaoId}`,
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: `https://npbb.example/landing/ativacoes/${ativacaoId}`,
    },
    lead_reconhecido: leadReconhecido,
    token,
    gamificacoes: [],
  } as const;
}

async function fulfillJson(
  route: Route,
  body: unknown,
  status = 200,
  headers: Record<string, string> = {},
) {
  await route.fulfill({
    status,
    contentType: "application/json",
    headers,
    body: JSON.stringify(body),
  });
}

async function installAnalyticsMock(page: Page) {
  await page.route("**/landing/analytics", async (route) => {
    await route.fulfill({ status: 204, body: "" });
  });
}

async function unlockCpfFirst(page: Page, cpf = "529.982.247-25") {
  await page.getByTestId("cpf-first-input").fill(cpf);
  await page.getByRole("button", { name: /continuar/i }).click();
}

test("reconhece a segunda landing via cookie emitido no submit", async ({ page }) => {
  let secondLandingCookieHeader = "";
  let secondLandingWasRecognized = false;

  await installAnalyticsMock(page);

  await page.route(/\/eventos\/10\/ativacoes\/\d+\/landing(?:\?.*)?$/, async (route, request) => {
    const match = request.url().match(/ativacoes\/(\d+)\/landing/);
    const ativacaoId = Number(match?.[1] || 0);
    const isReturnLanding = ativacaoId === ATIVACAO_RETORNO_ID;
    const cookieHeader = request.headers()["cookie"] || "";

    if (isReturnLanding) {
      secondLandingCookieHeader = cookieHeader;
    }

    await fulfillJson(
      route,
      buildLandingPayload({
        ativacaoId,
        nome: ativacaoId === ATIVACAO_RETORNO_ID ? "Stand Secundario" : "Stand Principal",
        leadReconhecido: isReturnLanding && cookieHeader.includes(`lp_lead_token=${COOKIE_TOKEN}`),
      }),
    );
    if (isReturnLanding) {
      secondLandingWasRecognized = cookieHeader.includes(`lp_lead_token=${COOKIE_TOKEN}`);
    }
  });

  await page.route("**/leads", async (route) => {
    await fulfillJson(
      route,
      {
        lead_id: 99,
        event_id: EVENTO_ID,
        ativacao_id: ATIVACAO_INICIAL_ID,
        ativacao_lead_id: 444,
        mensagem_sucesso: "Cadastro realizado com sucesso.",
        lead_reconhecido: true,
        conversao_registrada: true,
        bloqueado_cpf_duplicado: false,
        token_reconhecimento: COOKIE_TOKEN,
      },
      201,
      {
        "Set-Cookie": `lp_lead_token=${COOKIE_TOKEN}; Path=/; Max-Age=604800; SameSite=Lax`,
      },
    );
  });

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_INICIAL_ID}`);
  await expect(page.getByText("Stand Principal")).toBeVisible();
  await expect(page.getByTestId("cpf-first-input")).toBeVisible();

  await unlockCpfFirst(page);
  await page.getByRole("textbox", { name: /nome/i }).fill("Maria");
  await page.getByRole("textbox", { name: /email/i }).fill("maria@example.com");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: /confirmar presenca/i }).click();

  await expect(page.getByText("Cadastro realizado com sucesso.")).toBeVisible();

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_RETORNO_ID}`);
  await expect(page.getByText("Stand Secundario")).toBeVisible();
  expect(secondLandingCookieHeader).toContain(`lp_lead_token=${COOKIE_TOKEN}`);
  expect(secondLandingWasRecognized).toBe(true);
  await expect(page.getByTestId("cpf-first-input")).toBeVisible();
  await expect(page.getByRole("button", { name: /continuar/i })).toBeVisible();
});

test("repassa token na URL para o GET canonico e entra reconhecido", async ({ page }) => {
  let requestedToken = "";
  let landingWasRecognized = false;

  await installAnalyticsMock(page);

  await page.route(/\/eventos\/10\/ativacoes\/1\/landing(?:\?.*)?$/, async (route, request) => {
    requestedToken = new URL(request.url()).searchParams.get("token") || "";
    await fulfillJson(
      route,
      buildLandingPayload({
        ativacaoId: ATIVACAO_INICIAL_ID,
        nome: "Stand Principal",
        leadReconhecido: requestedToken === URL_TOKEN,
        token: requestedToken,
      }),
    );
    landingWasRecognized = requestedToken === URL_TOKEN;
  });

  await page.goto(`/eventos/${EVENTO_ID}/ativacoes/${ATIVACAO_INICIAL_ID}?token=${URL_TOKEN}`);
  await expect(page.getByText("Stand Principal")).toBeVisible();
  expect(requestedToken).toBe(URL_TOKEN);
  expect(landingWasRecognized).toBe(true);
  await expect(page.getByTestId("cpf-first-input")).toBeVisible();
  await expect(page.getByRole("button", { name: /continuar/i })).toBeVisible();
});
