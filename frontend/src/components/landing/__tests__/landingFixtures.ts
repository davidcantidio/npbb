import type { LandingPageData, GamificacaoPublic } from "../../../services/landing_public";

const BASE_EVENTO = {
  id: 10,
  nome: "BB Summit 2026",
  cta_personalizado: null,
  descricao: "O Banco do Brasil apresenta a maior experiencia de inovacao.",
  descricao_curta: "Cadastre-se e participe do maior evento BB.",
  data_inicio: "2026-04-10",
  data_fim: "2026-04-12",
  cidade: "Brasilia",
  estado: "DF",
};

const BASE_ATIVACAO = {
  id: 1,
  nome: "Stand Principal",
  descricao: "Venha conhecer as novidades do BB.",
  mensagem_qrcode: "Escaneie o QR code no totem para se cadastrar.",
};

const BASE_FORMULARIO = {
  event_id: 10,
  ativacao_id: 1,
  submit_url: "/landing/ativacoes/1/submit",
  campos: [
    { key: "nome", label: "Nome", input_type: "text", required: true, autocomplete: "name", placeholder: "Seu nome" },
    { key: "email", label: "Email", input_type: "email", required: true, autocomplete: "email", placeholder: "voce@exemplo.com" },
    { key: "telefone", label: "Telefone", input_type: "tel", required: false, autocomplete: "tel", placeholder: "(00) 00000-0000" },
  ],
  campos_obrigatorios: ["nome", "email"],
  campos_opcionais: ["telefone"],
  mensagem_sucesso: "Cadastro realizado com sucesso.",
  lgpd_texto: "Ao enviar seus dados, voce concorda com o tratamento das informacoes.",
  privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
};

const BASE_MARCA_WITH_HERO = {
  tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
  versao_logo: "positivo",
  url_hero_image: "https://example.com/hero.webp",
  hero_alt: "Imagem do evento BB Summit 2026",
};

const BASE_MARCA_NO_HERO = {
  ...BASE_MARCA_WITH_HERO,
  url_hero_image: null,
};

const BASE_ACESSO = {
  landing_url: "https://npbb.example/landing/ativacoes/1",
  qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
  url_promotor: "https://npbb.example/landing/ativacoes/1",
};

type TemplateKey = "esporte_convencional" | "esporte_radical" | "show_musical" | "evento_cultural" | "tecnologia";

const TEMPLATE_CONFIGS: Record<TemplateKey, LandingPageData["template"]> = {
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

export const TEMPLATE_KEYS = Object.keys(TEMPLATE_CONFIGS) as TemplateKey[];

export const BREAKPOINTS = [375, 768, 1280] as const;

export const GAMIFICACAO_MOCK: GamificacaoPublic = {
  id: 1,
  nome: "Roleta da Sorte BB",
  descricao: "Gire a roleta e concorra a premios exclusivos.",
  premio: "Camiseta oficial BB",
  titulo_feedback: "Parabens!",
  texto_feedback: "Voce concluiu a gamificacao com sucesso.",
};

export function createTemplateFixture(
  templateKey: TemplateKey,
  options: { withHero?: boolean; withGamificacao?: boolean; withAtivacao?: boolean } = {},
): LandingPageData {
  const { withHero = true, withGamificacao = false, withAtivacao = true } = options;
  return {
    ativacao_id: withAtivacao ? 1 : null,
    ativacao: withAtivacao ? BASE_ATIVACAO : null,
    gamificacoes: withGamificacao ? [GAMIFICACAO_MOCK] : [],
    evento: BASE_EVENTO,
    template: TEMPLATE_CONFIGS[templateKey],
    formulario: BASE_FORMULARIO,
    marca: withHero ? BASE_MARCA_WITH_HERO : BASE_MARCA_NO_HERO,
    acesso: BASE_ACESSO,
  };
}

export const GRAPHICS_STYLE_MAP: Record<TemplateKey, string> = {
  esporte_convencional: "geometric",
  esporte_radical: "dynamic",
  show_musical: "dynamic",
  evento_cultural: "organic",
  tecnologia: "grid",
};

export const HERO_LAYOUT_MAP: Record<TemplateKey, string> = {
  esporte_convencional: "split",
  esporte_radical: "full-bleed",
  show_musical: "dark-overlay",
  evento_cultural: "editorial",
  tecnologia: "dark-overlay",
};
