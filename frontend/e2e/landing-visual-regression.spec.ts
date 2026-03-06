import { test, expect, type Page, type Route } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

/**
 * AFLPD-F4-01-001 — Regressão Visual Cross-Template (Playwright)
 *
 * Captura screenshots para 5 templates × 3 breakpoints × 2 hero states = 30 cenários.
 * Screenshots salvos em artifacts/phase-f4/screenshots/.
 *
 * Uso: npx playwright test e2e/landing-visual-regression.spec.ts --headed
 */

const SCREENSHOT_DIR = path.resolve(__dirname, "../../artifacts/phase-f4/screenshots");

const BREAKPOINTS = [
  { label: "mobile", width: 375, height: 812 },
  { label: "tablet", width: 768, height: 1024 },
  { label: "desktop", width: 1280, height: 900 },
] as const;

type TemplateKey = "esporte_convencional" | "esporte_radical" | "show_musical" | "evento_cultural" | "tecnologia";

interface MockLandingData {
  ativacao_id: number;
  ativacao: {
    id: number;
    nome: string;
    descricao: string;
    mensagem_qrcode: string;
  };
  gamificacoes: never[];
  evento: {
    id: number;
    nome: string;
    cta_personalizado: null;
    descricao: string;
    descricao_curta: string;
    data_inicio: string;
    data_fim: string;
    cidade: string;
    estado: string;
  };
  template: {
    categoria: string;
    tema: string;
    mood: string;
    cta_text: string;
    color_primary: string;
    color_secondary: string;
    color_background: string;
    color_text: string;
    hero_layout: string;
    cta_variant: string;
    graphics_style: string;
    tone_of_voice: string;
    cta_experiment_enabled: boolean;
    cta_variants: never[];
  };
  formulario: {
    event_id: number;
    ativacao_id: number;
    submit_url: string;
    campos: Array<{
      key: string;
      label: string;
      input_type: string;
      required: boolean;
      autocomplete: string;
      placeholder: string;
    }>;
    campos_obrigatorios: string[];
    campos_opcionais: string[];
    mensagem_sucesso: string;
    lgpd_texto: string;
    privacy_policy_url: string;
  };
  marca: {
    tagline: string;
    versao_logo: string;
    url_hero_image: string | null;
    hero_alt: string;
  };
  acesso: {
    landing_url: string;
    qr_code_url: string;
    url_promotor: string;
  };
}

const TEMPLATES: Record<TemplateKey, MockLandingData["template"]> = {
  esporte_convencional: {
    categoria: "esporte_convencional",
    tema: "Sport",
    mood: "Orgulho, conquista e energia alta.",
    cta_text: "Garanta sua vaga",
    color_primary: "#3333BD",
    color_secondary: "#FCFC30",
    color_background: "#F3F7FF",
    color_text: "#111827",
    hero_layout: "split",
    cta_variant: "filled",
    graphics_style: "geometric",
    tone_of_voice: "enthusiasm",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
  esporte_radical: {
    categoria: "esporte_radical",
    tema: "Radical",
    mood: "Alta energia, autenticidade e movimento.",
    cta_text: "Quero fazer parte",
    color_primary: "#FF6E91",
    color_secondary: "#FCFC30",
    color_background: "#FFF7FB",
    color_text: "#1F2937",
    hero_layout: "full-bleed",
    cta_variant: "gradient",
    graphics_style: "dynamic",
    tone_of_voice: "enthusiasm",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
  show_musical: {
    categoria: "show_musical",
    tema: "Show",
    mood: "Vibrante, noturno e memoravel.",
    cta_text: "Quero ir",
    color_primary: "#735CC6",
    color_secondary: "#FF6E91",
    color_background: "#140F2E",
    color_text: "#F8FAFC",
    hero_layout: "dark-overlay",
    cta_variant: "gradient",
    graphics_style: "dynamic",
    tone_of_voice: "enthusiasm",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
  evento_cultural: {
    categoria: "evento_cultural",
    tema: "Cultural",
    mood: "Sofisticado, acessivel e inspirador.",
    cta_text: "Quero conhecer",
    color_primary: "#00EBD0",
    color_secondary: "#BDB6FF",
    color_background: "#F7FBFB",
    color_text: "#111827",
    hero_layout: "editorial",
    cta_variant: "outlined",
    graphics_style: "organic",
    tone_of_voice: "attention",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
  tecnologia: {
    categoria: "tecnologia",
    tema: "Tech",
    mood: "Futuro, comunidade e inovacao.",
    cta_text: "Quero participar",
    color_primary: "#54DCFC",
    color_secondary: "#83FFEA",
    color_background: "#07111F",
    color_text: "#F8FAFC",
    hero_layout: "dark-overlay",
    cta_variant: "gradient",
    graphics_style: "grid",
    tone_of_voice: "enthusiasm",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
};

function buildMockData(template: TemplateKey, withHero: boolean): MockLandingData {
  return {
    ativacao_id: 1,
    ativacao: {
      id: 1,
      nome: "Stand Principal",
      descricao: "Venha conhecer as novidades do BB.",
      mensagem_qrcode: "Escaneie o QR code no totem.",
    },
    gamificacoes: [],
    evento: {
      id: 10,
      nome: "BB Summit 2026",
      cta_personalizado: null,
      descricao: "O maior evento do Banco do Brasil.",
      descricao_curta: "Cadastre-se e participe.",
      data_inicio: "2026-04-10",
      data_fim: "2026-04-12",
      cidade: "Brasilia",
      estado: "DF",
    },
    template: TEMPLATES[template],
    formulario: {
      event_id: 10,
      ativacao_id: 1,
      submit_url: "/landing/ativacoes/1/submit",
      campos: [
        { key: "nome", label: "Nome", input_type: "text", required: true, autocomplete: "name", placeholder: "Seu nome" },
        { key: "email", label: "Email", input_type: "email", required: true, autocomplete: "email", placeholder: "voce@exemplo.com" },
      ],
      campos_obrigatorios: ["nome", "email"],
      campos_opcionais: [],
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lgpd_texto: "Ao enviar seus dados, voce concorda com o tratamento.",
      privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
    },
    marca: {
      tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
      versao_logo: "positivo",
      url_hero_image: withHero ? "https://picsum.photos/800/600" : null,
      hero_alt: "Imagem de destaque do evento BB Summit 2026",
    },
    acesso: {
      landing_url: "https://npbb.example/landing/ativacoes/1",
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: "https://npbb.example/landing/ativacoes/1",
    },
  };
}

async function interceptLandingApi(page: Page, mockData: MockLandingData) {
  await page.route("**/ativacoes/*/landing", (route: Route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mockData) }),
  );
  await page.route("**/landing/analytics", (route: Route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) }),
  );
}

test.beforeAll(() => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
});

const templateKeys = Object.keys(TEMPLATES) as TemplateKey[];

for (const template of templateKeys) {
  for (const bp of BREAKPOINTS) {
    for (const heroState of ["hero", "nohero"] as const) {
      const testName = `${template}_${bp.label}_${heroState}`;

      test(testName, async ({ page }) => {
        const withHero = heroState === "hero";
        const mockData = buildMockData(template, withHero);

        await page.setViewportSize({ width: bp.width, height: bp.height });
        await interceptLandingApi(page, mockData);
        await page.goto("/landing/ativacoes/1");

        await page.waitForSelector("button", { timeout: 10_000 });

        await page.screenshot({
          path: path.join(SCREENSHOT_DIR, `${testName}.png`),
          fullPage: true,
        });

        const formButton = page.getByRole("button", { name: new RegExp(mockData.template.cta_text, "i") });
        await expect(formButton).toBeVisible();

        if (withHero) {
          await expect(page.getByTestId("landing-hero-image")).toBeVisible();
        } else {
          await expect(page.getByTestId("landing-hero-fallback")).toBeVisible();
        }

        const moodChip = page.getByText(mockData.template.mood, { exact: true });
        await expect(moodChip).not.toBeVisible();
      });
    }
  }
}
