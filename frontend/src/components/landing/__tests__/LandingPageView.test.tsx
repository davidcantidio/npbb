import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LandingPageView, { formatDateRange } from "../LandingPageView";
import type { LandingPageData } from "../../../services/landing_public";

function createLandingFixture(overrides: Partial<LandingPageData> = {}): LandingPageData {
  return {
    ativacao_id: 1,
    ativacao: {
      id: 1,
      nome: "Stand Principal",
      descricao: "Venha conhecer as novidades do BB.",
      mensagem_qrcode: "Escaneie o QR code no totem para se cadastrar.",
    },
    evento: {
      id: 10,
      nome: "BB Summit 2026",
      cta_personalizado: null,
      descricao: "Descricao completa do evento.",
      descricao_curta: "Resumo curto do evento.",
      data_inicio: "2026-04-10",
      data_fim: "2026-04-12",
      cidade: "Brasilia",
      estado: "DF",
    },
    template: {
      categoria: "categoria-interna",
      tema: "Tema Interno",
      mood: "mood-interno",
      cta_text: "Confirmar presenca",
      color_primary: "#1E3A8A",
      color_secondary: "#FCFC30",
      color_background: "#F5F7FB",
      color_text: "#111827",
      hero_layout: "split",
      cta_variant: "outlined",
      graphics_style: "grid",
      tone_of_voice: "tom-interno",
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
      ],
      campos_obrigatorios: ["nome", "email"],
      campos_opcionais: [],
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lgpd_texto: "Ao enviar seus dados, voce concorda com o tratamento das informacoes.",
      privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
    },
    marca: {
      tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
      versao_logo: "positivo",
      url_hero_image: "https://example.com/hero-image.webp",
      hero_alt: "Imagem de destaque do evento BB Summit 2026",
    },
    acesso: {
      landing_url: "https://npbb.example/landing/ativacoes/1",
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: "https://npbb.example/landing/ativacoes/1",
    },
    ...overrides,
  };
}

describe("LandingPageView", () => {
  it("oculta campos internos de template no modo publico", () => {
    render(<LandingPageView data={createLandingFixture()} mode="public" />);

    expect(screen.queryByText("Tema Interno")).not.toBeInTheDocument();
    expect(screen.queryByText(/tom-interno/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/mood-interno/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Categoria: categoria-interna/i)).not.toBeInTheDocument();
  });

  it("exibe campos internos de template no modo preview", () => {
    render(<LandingPageView data={createLandingFixture()} mode="preview" />);

    expect(screen.getByText("Tema Interno")).toBeInTheDocument();
    expect(screen.getByText(/Template: Tema Interno/i)).toBeInTheDocument();
    expect(screen.getByText(/mood-interno/i)).toBeInTheDocument();
    expect(screen.getByText(/Categoria: categoria-interna/i)).toBeInTheDocument();
  });

  it("prioriza cta_personalizado do evento sobre o CTA do template", () => {
    const fixture = createLandingFixture({
      evento: {
        ...createLandingFixture().evento,
        cta_personalizado: "Cadastre-se agora",
      },
    });

    render(<LandingPageView data={fixture} mode="public" />);

    expect(screen.getByRole("button", { name: /cadastre-se agora/i })).toBeInTheDocument();
  });

  it("renderiza fallback visual quando hero image estiver vazia", () => {
    const fixture = createLandingFixture({
      marca: {
        ...createLandingFixture().marca,
        url_hero_image: "   ",
      },
    });

    render(<LandingPageView data={fixture} mode="public" />);

    expect(screen.getByTestId("landing-hero-fallback")).toBeInTheDocument();
    expect(screen.queryByTestId("landing-hero-image")).not.toBeInTheDocument();
  });

  it("renderiza hero image quando URL valida estiver presente", () => {
    render(<LandingPageView data={createLandingFixture()} mode="public" />);

    expect(screen.getByTestId("landing-hero-image")).toBeInTheDocument();
    expect(screen.queryByTestId("landing-hero-fallback")).not.toBeInTheDocument();
  });

  it("usa fallback com ativacao nula e nao mostra callout", () => {
    const fixture = createLandingFixture({
      ativacao_id: null,
      ativacao: null,
      evento: {
        ...createLandingFixture().evento,
        nome: "Evento sem ativacao",
      },
    });

    render(<LandingPageView data={fixture} mode="public" />);

    expect(screen.getAllByText("Evento sem ativacao").length).toBeGreaterThan(0);
    expect(screen.queryByText(/Escaneie o QR code no totem para se cadastrar/i)).not.toBeInTheDocument();
  });

  it("nao renderiza bloco de gamificacao quando lista estiver vazia", () => {
    render(<LandingPageView data={createLandingFixture({ gamificacoes: [] })} mode="public" />);

    expect(screen.queryByRole("button", { name: /quero participar/i })).not.toBeInTheDocument();
  });

  it("mantem gamificacao em modo somente leitura no preview", () => {
    render(
      <LandingPageView
        data={createLandingFixture({
          gamificacoes: [
            {
              id: 12,
              nome: "Quiz BB",
              descricao: "Responda ao quiz interativo.",
              premio: "Kit promocional",
              titulo_feedback: "Boa!",
              texto_feedback: "Participacao registrada.",
            },
          ],
        })}
        mode="preview"
        gamificacao={{
          leadSubmitted: true,
          onComplete: () => undefined,
          onReset: () => undefined,
        }}
      />,
    );

    expect(screen.getByRole("button", { name: /quero participar/i })).toBeDisabled();
  });

  it("formatDateRange preserva o dia para datas YYYY-MM-DD", () => {
    const label = formatDateRange("2026-04-10", "2026-04-12");
    expect(label).toMatch(/^10 de .* 2026 - 12 de .* 2026$/);
    expect(label).not.toContain("09 de");
  });
});
