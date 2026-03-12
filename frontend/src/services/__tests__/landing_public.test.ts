import { afterEach, describe, expect, it, vi } from "vitest";

import {
  getLandingByAtivacao,
  getLandingByEvento,
  getLandingByEventoAtivacao,
  previewEventoLanding,
} from "../landing_public";
import { fetchWithAuth, handleApiResponse } from "../http";

vi.mock("../http", () => ({
  fetchWithAuth: vi.fn(),
  handleApiResponse: vi.fn(),
}));

const mockedFetchWithAuth = vi.mocked(fetchWithAuth);
const mockedHandleApiResponse = vi.mocked(handleApiResponse);

const landingBasePayload = {
  ativacao_id: 1,
  ativacao: {
    id: 1,
    nome: "Stand Principal",
    descricao: "Descricao",
    mensagem_qrcode: "Mensagem",
  },
  evento: {
    id: 10,
    nome: "BB Summit 2026",
    cta_personalizado: null,
    descricao: "Descricao completa",
    descricao_curta: "Descricao curta",
    data_inicio: "2026-04-10",
    data_fim: "2026-04-12",
    cidade: "Brasilia",
    estado: "DF",
  },
  template: {
    categoria: "corporativo",
    tema: "Tema",
    mood: "Mood",
    cta_text: "CTA",
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
    campos: [],
    campos_obrigatorios: [],
    campos_opcionais: [],
    mensagem_sucesso: "Sucesso",
    lgpd_texto: "LGPD",
    privacy_policy_url: "https://example.com/privacy",
  },
  marca: {
    tagline: "Banco do Brasil",
  },
  acesso: {
    landing_url: "https://npbb.example/landing/ativacoes/1",
    qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
    url_promotor: "https://npbb.example/landing/ativacoes/1",
  },
};

afterEach(() => {
  vi.clearAllMocks();
});

describe("landing_public service", () => {
  it("normaliza gamificacoes ausente para lista vazia no endpoint por evento", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce(landingBasePayload);

    const payload = await getLandingByEvento(10);

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/eventos/10/landing", { retries: 0 });
    expect(payload.gamificacoes).toEqual([]);
  });

  it("serializa template_override valido no endpoint por evento", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce(landingBasePayload);

    await getLandingByEvento(10, { templateOverride: " show_musical " });

    expect(mockedFetchWithAuth).toHaveBeenCalledWith(
      "/eventos/10/landing?template_override=show_musical",
      { retries: 0 },
    );
  });

  it("omite template_override vazio no endpoint por evento", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce(landingBasePayload);

    await getLandingByEvento(10, { templateOverride: "   " });

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/eventos/10/landing", { retries: 0 });
  });

  it("carrega landing pelo endpoint canonico de evento e ativacao sem token", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce({
      ...landingBasePayload,
      gamificacoes: null,
    });

    const payload = await getLandingByEventoAtivacao(10, 1);

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/eventos/10/ativacoes/1/landing", { retries: 0 });
    expect(payload.gamificacoes).toEqual([]);
  });

  it("serializa token no endpoint canonico de evento e ativacao", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce({
      ...landingBasePayload,
      gamificacoes: null,
    });

    const payload = await getLandingByEventoAtivacao(10, 1, { token: " abc123 " });

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/eventos/10/ativacoes/1/landing?token=abc123", {
      retries: 0,
    });
    expect(payload.gamificacoes).toEqual([]);
  });

  it("envia payload autenticado para o preview transiente por evento", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce({
      ...landingBasePayload,
      gamificacoes: null,
    });
    const signal = {} as AbortSignal;

    const payload = await previewEventoLanding(
      "token-preview",
      10,
      {
        template_id: 4,
        template_override: "show_musical",
        cta_personalizado: "Quero ir",
        descricao_curta: "Descricao curta",
        campos: [{ nome_campo: "Nome", obrigatorio: true, ordem: 0 }],
      },
      { signal },
    );

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/evento/10/landing-preview", {
      token: "token-preview",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        template_id: 4,
        template_override: "show_musical",
        cta_personalizado: "Quero ir",
        descricao_curta: "Descricao curta",
        campos: [{ nome_campo: "Nome", obrigatorio: true, ordem: 0 }],
      }),
      retries: 0,
      signal,
    });
    expect(payload.gamificacoes).toEqual([]);
  });

  it("normaliza gamificacoes nula para lista vazia no endpoint por ativacao", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce({
      ...landingBasePayload,
      gamificacoes: null,
    });

    const payload = await getLandingByAtivacao(1);

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/ativacoes/1/landing", { retries: 0 });
    expect(payload.gamificacoes).toEqual([]);
  });
});
