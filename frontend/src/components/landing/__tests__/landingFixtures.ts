import type { GamificacaoPublic, LandingPageData } from "../../../services/landing_public";

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
  conversao_unica: false,
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

const BASE_MARCA = {
  tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
};

const BASE_ACESSO = {
  landing_url: "https://npbb.example/landing/ativacoes/1",
  qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
  url_promotor: "https://npbb.example/landing/ativacoes/1",
};

export type TemplateKey =
  | "corporativo"
  | "esporte_convencional"
  | "esporte_radical"
  | "evento_cultural"
  | "show_musical"
  | "tecnologia"
  | "generico";

const TEMPLATE_CONFIGS: Record<TemplateKey, LandingPageData["template"]> = {
  corporativo: {
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
  generico: {
    categoria: "generico",
    tema: "Default",
    mood: "Neutro, confiavel e com identidade BB.",
    cta_text: "Quero me cadastrar",
    color_primary: "#3333BD",
    color_secondary: "#FCFC30",
    color_background: "#F7F8FF",
    color_text: "#111827",
    hero_layout: "split",
    cta_variant: "filled",
    graphics_style: "geometric",
    tone_of_voice: "warmth",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
};

export const TEMPLATE_KEYS = Object.keys(TEMPLATE_CONFIGS) as TemplateKey[];

export const BREAKPOINTS = [375, 768, 1280] as const;

export const EXPECTED_TEMPLATE_GRADIENTS: Record<TemplateKey, string> = {
  corporativo: "linear-gradient(135deg, #1A237E 0%, #3333BD 60%, #465EFF 100%)",
  esporte_convencional: "linear-gradient(160deg, #3333BD 0%, #1A237E 50%, #3333BD 100%)",
  esporte_radical: "linear-gradient(145deg, #3333BD 0%, #FF6E91 55%, #FCFC30 100%)",
  evento_cultural: "linear-gradient(150deg, #BDB6FF 0%, #E8E4FF 50%, #83FFEA 100%)",
  show_musical: "linear-gradient(160deg, #0D0D1A 0%, #2D1B4E 50%, #4A1942 100%)",
  tecnologia: "linear-gradient(135deg, #0D1B2E 0%, #0A2440 40%, #0B3340 100%)",
  generico: "linear-gradient(150deg, #3333BD 0%, #465EFF 100%)",
};

export const EXPECTED_TEMPLATE_OVERLAY_OPACITY: Record<TemplateKey, number> = {
  corporativo: 0.1,
  esporte_convencional: 0.1,
  esporte_radical: 0.15,
  evento_cultural: 0.12,
  show_musical: 0.2,
  tecnologia: 0.15,
  generico: 0.05,
};

export const EXPECTED_TEMPLATE_OVERLAY_VARIANTS: Record<TemplateKey, string> = {
  corporativo: "corporativo",
  esporte_convencional: "esporte_convencional",
  esporte_radical: "esporte_radical",
  evento_cultural: "evento_cultural",
  show_musical: "show_musical",
  tecnologia: "tecnologia",
  generico: "generico",
};

export const GRAPHICS_STYLE_MAP: Record<TemplateKey, string> = {
  corporativo: "grid",
  esporte_convencional: "geometric",
  esporte_radical: "dynamic",
  evento_cultural: "organic",
  show_musical: "dynamic",
  tecnologia: "grid",
  generico: "geometric",
};

export const HERO_LAYOUT_MAP: Record<TemplateKey, string> = {
  corporativo: "split",
  esporte_convencional: "split",
  esporte_radical: "full-bleed",
  evento_cultural: "editorial",
  show_musical: "dark-overlay",
  tecnologia: "dark-overlay",
  generico: "split",
};

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
  options: { withGamificacao?: boolean; withAtivacao?: boolean } = {},
): LandingPageData {
  const { withGamificacao = false, withAtivacao = true } = options;

  return {
    ativacao_id: withAtivacao ? 1 : null,
    ativacao: withAtivacao ? BASE_ATIVACAO : null,
    gamificacoes: withGamificacao ? [GAMIFICACAO_MOCK] : [],
    evento: BASE_EVENTO,
    template: TEMPLATE_CONFIGS[templateKey],
    formulario: BASE_FORMULARIO,
    marca: BASE_MARCA,
    acesso: BASE_ACESSO,
  };
}
