import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import LandingPageView, { formatDateRange } from "../LandingPageView";
import type { LandingPageData } from "../../../services/landing_public";

function expectLegacyBlocksToBeAbsent() {
  expect(screen.queryByTestId("landing-hero-image")).not.toBeInTheDocument();
  expect(screen.queryByTestId("landing-hero-fallback")).not.toBeInTheDocument();
  expect(screen.queryByAltText(/banco do brasil/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/Sobre o evento/i)).not.toBeInTheDocument();
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function getEmotionCssText() {
  return Array.from(document.querySelectorAll("style[data-emotion]"))
    .map((node) => node.textContent ?? "")
    .join("")
    .replace(/\s+/g, "");
}

function expectSharedWidthContract(element: HTMLElement) {
  const emotionClass = Array.from(element.classList).find((className) => className.startsWith("css-"));
  expect(emotionClass).toBeTruthy();

  const css = getEmotionCssText();
  const selector = `\\.${escapeRegExp(emotionClass!)}`;

  expect(css).toMatch(new RegExp(`${selector}\\{[^}]*width:min\\(92vw,440px\\)`));
  expect(css).toMatch(new RegExp(`@media\\(min-width:768px\\)\\{${selector}\\{[^}]*width:min\\(480px,90vw\\)`));
  expect(css).toMatch(new RegExp(`@media\\(min-width:1280px\\)\\{${selector}\\{[^}]*width:min\\(520px,90vw\\)`));
}

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
    },
    acesso: {
      landing_url: "https://npbb.example/landing/ativacoes/1",
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: "https://npbb.example/landing/ativacoes/1",
    },
    gamificacoes: [],
    ...overrides,
  };
}

describe("LandingPageView", () => {
  it("renderiza o FormCard dedicado no layout", () => {
    render(<LandingPageView data={createLandingFixture()} mode="public" />);

    expect(screen.getByTestId("form-card-container")).toBeInTheDocument();
    expect(screen.getByTestId("form-card-paper")).toBeInTheDocument();
  });

  it("oculta campos internos de template no modo publico", () => {
    render(<LandingPageView data={createLandingFixture()} mode="public" />);

    expect(screen.queryByText("Tema Interno")).not.toBeInTheDocument();
    expect(screen.queryByText(/tom-interno/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/mood-interno/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Categoria: categoria-interna/i)).not.toBeInTheDocument();
  });

  it("exibe apenas badge discreto no modo preview", () => {
    render(<LandingPageView data={createLandingFixture()} mode="preview" />);

    expect(screen.getByTestId("landing-preview-badge")).toHaveTextContent("Preview");
    expect(screen.queryByText("Tema Interno")).not.toBeInTheDocument();
    expect(screen.queryByText(/Template: Tema Interno/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/mood-interno/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Categoria: categoria-interna/i)).not.toBeInTheDocument();
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

  it("nao renderiza hero, header nem blocos legados na view publica", () => {
    render(<LandingPageView data={createLandingFixture()} mode="public" />);

    expectLegacyBlocksToBeAbsent();
  });

  it("nao renderiza hero, header nem blocos legados no preview", () => {
    render(<LandingPageView data={createLandingFixture()} mode="preview" />);

    expect(screen.getByTestId("landing-preview-badge")).toHaveTextContent("Preview");
    expectLegacyBlocksToBeAbsent();
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

  it("renderiza gamificacao abaixo do FormCard com largura e surface compartilhadas", () => {
    render(
      <LandingPageView
        data={createLandingFixture({
          template: {
            ...createLandingFixture().template,
            categoria: "corporativo",
          },
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
        mode="public"
      />,
    );

    const formCardContainer = screen.getByTestId("form-card-container");
    const formCardPaper = screen.getByTestId("form-card-paper");
    const gamificacaoSection = screen.getByTestId("landing-gamificacao-section");
    const gamificacaoSurface = screen.getByTestId("landing-gamificacao-surface");

    expect(
      formCardContainer.compareDocumentPosition(gamificacaoSection) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBe(Node.DOCUMENT_POSITION_FOLLOWING);

    expectSharedWidthContract(formCardPaper);
    expectSharedWidthContract(gamificacaoSection);

    const formCardStyles = window.getComputedStyle(formCardPaper);
    const gamificacaoStyles = window.getComputedStyle(gamificacaoSurface);

    expect(gamificacaoStyles.borderRadius).toBe(formCardStyles.borderRadius);
    expect(gamificacaoStyles.boxShadow).toBe(formCardStyles.boxShadow);
    expect(gamificacaoStyles.borderTopWidth).toBe(formCardStyles.borderTopWidth);
    expect(gamificacaoStyles.borderTopStyle).toBe(formCardStyles.borderTopStyle);
    expect(gamificacaoStyles.borderTopColor).toBe(formCardStyles.borderTopColor);
    expect(gamificacaoStyles.backgroundColor).toBe("rgba(255, 255, 255, 0.92)");
  });

  it("mantem overlay decorativo sem bloquear clique no CTA", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<LandingPageView data={createLandingFixture()} mode="public" onSubmit={onSubmit} />);

    const overlayLayer = screen.getByTestId("full-page-overlay-layer");
    expect(overlayLayer).toHaveStyle({ pointerEvents: "none" });

    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(onSubmit).toHaveBeenCalledTimes(1);
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

  it("renderiza footer minimo tambem no preview", () => {
    render(<LandingPageView data={createLandingFixture()} mode="preview" />);

    expect(screen.getByTestId("minimal-footer")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /politica de privacidade e lgpd/i })).toHaveAttribute(
      "href",
      "https://www.bb.com.br/site/privacidade-e-lgpd/",
    );
  });

  it("formatDateRange preserva o dia para datas YYYY-MM-DD", () => {
    const label = formatDateRange("2026-04-10", "2026-04-12");
    expect(label).toMatch(/^10 de .* 2026 - 12 de .* 2026$/);
    expect(label).not.toContain("09 de");
  });
});
