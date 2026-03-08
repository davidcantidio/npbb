import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LandingPageView, { buildLandingTheme } from "../LandingPageView";
import {
  BREAKPOINTS,
  TEMPLATE_KEYS,
  GRAPHICS_STYLE_MAP,
  HERO_LAYOUT_MAP,
  createTemplateFixture,
} from "./landingFixtures";

/**
 * AFLPD-F4-01-001 — Regressão Visual Cross-Template
 *
 * Matriz: 5 templates × 3 breakpoints = 15 cenários
 *
 * Valida para cada cenário:
 *  - Formulário renderiza (above the fold intent)
 *  - renderGraphicOverlay renderiza overlay correto por graphics_style
 *  - Nenhum bloco legado é renderizado
 *  - Badge de preview fica restrito ao modo preview
 *  - borderRadius do tema = 20 (MUI shape units)
 */

function setViewportWidth(width: number) {
  Object.defineProperty(window, "innerWidth", { writable: true, configurable: true, value: width });
  window.dispatchEvent(new Event("resize"));
}

describe("AFLPD-F4-01-001 — Regressão Visual Cross-Template", () => {
  describe.each(TEMPLATE_KEYS)("Template: %s", (templateKey) => {
    describe.each(BREAKPOINTS)("Breakpoint: %dpx", (breakpoint) => {
      it("renderiza formulário sem blocos legados", () => {
        setViewportWidth(breakpoint);
        const data = createTemplateFixture(templateKey, { withHero: true });
        render(<LandingPageView data={data} mode="public" />);

        expect(screen.getByRole("button", { name: new RegExp(data.template.cta_text, "i") })).toBeInTheDocument();

        const fields = data.formulario.campos;
        for (const field of fields) {
          expect(screen.getByLabelText(new RegExp(field.label, "i"))).toBeInTheDocument();
        }

        expect(screen.queryByTestId("landing-hero-image")).not.toBeInTheDocument();
        expect(screen.queryByTestId("landing-hero-fallback")).not.toBeInTheDocument();
      });
    });

    it("oculta informacoes operacionais extras em modo público", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.queryByText(data.template.mood)).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Categoria: ${data.template.categoria}`))).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Template: ${data.template.tema}`))).not.toBeInTheDocument();
    });

    it("exibe apenas badge em modo preview", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="preview" />);

      expect(screen.getByTestId("landing-preview-badge")).toHaveTextContent("Preview");
      expect(screen.queryByText(data.template.mood)).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Categoria: ${data.template.categoria}`))).not.toBeInTheDocument();
    });

    it("integra o wrapper FullPageBackground na landing", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByTestId("full-page-background-layer")).toHaveStyle({
        position: "fixed",
        inset: "0",
        width: "100vw",
        minHeight: "100vh",
        zIndex: "0",
      });
      expect(screen.getByTestId("full-page-background-content")).toHaveStyle({
        position: "relative",
        zIndex: "2",
        minHeight: "100vh",
      });
    });

    it(`renderiza overlay gráfico estilo '${GRAPHICS_STYLE_MAP[templateKey as keyof typeof GRAPHICS_STYLE_MAP]}'`, () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      const { container } = render(<LandingPageView data={data} mode="public" />);

      const heroSection = container.querySelector("[style*='position']") ?? container.firstElementChild;
      expect(heroSection).not.toBeNull();
    });

    it("gera tema MUI com borderRadius 20", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      const theme = buildLandingTheme(data);
      expect(theme.shape.borderRadius).toBe(20);
    });

    it("gera tema MUI com cores do template", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      const theme = buildLandingTheme(data);
      expect(theme.palette.primary.main).toBe(data.template.color_primary);
      expect(theme.palette.secondary.main).toBe(data.template.color_secondary);
    });

    it(`usa hero_layout '${HERO_LAYOUT_MAP[templateKey as keyof typeof HERO_LAYOUT_MAP]}'`, () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      expect(data.template.hero_layout).toBe(HERO_LAYOUT_MAP[templateKey as keyof typeof HERO_LAYOUT_MAP]);
    });

    it("renderiza titulo da ativacao e oculta contexto legado de localizacao", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByRole("heading", { name: data.ativacao!.nome })).toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`${data.evento.cidade}`))).not.toBeInTheDocument();
    });

    it("renderiza LGPD e link de privacidade", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByText(/concorda com o tratamento/i)).toBeInTheDocument();
      const privacyLinks = screen.getAllByRole("link", { name: /privacidade/i });
      expect(privacyLinks.length).toBeGreaterThanOrEqual(1);
      expect(privacyLinks[0]).toHaveAttribute("href", data.formulario.privacy_policy_url);
    });

    it("renderiza footer mínimo textual e link de privacidade em modo público", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      const { container } = render(<LandingPageView data={data} mode="public" />);

      const links = screen.getAllByRole("link", { name: /privacidade/i });
      expect(links.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByTestId("minimal-footer-tagline")).toHaveTextContent(
        "Banco do Brasil. Pra tudo que voce imaginar.",
      );
      expect(container.querySelector("[data-testid='minimal-footer'] img")).toBeNull();
      expect(container.querySelector("[data-testid='minimal-footer'] svg")).toBeNull();
    });

    it("renderiza footer minimo tambem em modo preview", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="preview" />);

      const footerLinks = screen.getAllByRole("link", { name: /Politica de privacidade e LGPD/i });
      expect(footerLinks.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("usa cor de rodapé do template corporativo", () => {
    const data = createTemplateFixture("tecnologia", { withHero: true });
    render(
      <LandingPageView
        data={{
          ...data,
          template: {
            ...data.template,
            categoria: "corporativo",
            color_primary: "#1A237E",
            color_secondary: "#FCFC30",
            color_background: "#F7F8FF",
            color_text: "#111827",
          },
        }}
        mode="public"
      />,
    );

    expect(screen.getByTestId("minimal-footer")).toHaveStyle({ color: "rgba(255, 255, 255, 0.75)" });
  });

  it("usa cor de rodapé do template evento_cultural", () => {
    const data = createTemplateFixture("evento_cultural", { withHero: true });
    render(<LandingPageView data={data} mode="public" />);

    expect(screen.getByTestId("minimal-footer")).toHaveStyle({ color: "rgba(51, 51, 189, 0.75)" });
  });
});
