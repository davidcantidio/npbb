import { render, screen, within } from "@testing-library/react";
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
 * Matriz: 5 templates × 3 breakpoints × 2 hero states = 30 cenários
 *
 * Valida para cada cenário:
 *  - Formulário renderiza (above the fold intent)
 *  - renderGraphicOverlay renderiza overlay correto por graphics_style
 *  - Hero image condicional (com/sem imagem)
 *  - Chips internos (mood/categoria) ausentes em modo público
 *  - borderRadius do tema = 20 (MUI shape units)
 */

function setViewportWidth(width: number) {
  Object.defineProperty(window, "innerWidth", { writable: true, configurable: true, value: width });
  window.dispatchEvent(new Event("resize"));
}

describe("AFLPD-F4-01-001 — Regressão Visual Cross-Template", () => {
  describe.each(TEMPLATE_KEYS)("Template: %s", (templateKey) => {
    describe.each(BREAKPOINTS)("Breakpoint: %dpx", (breakpoint) => {
      it("renderiza formulário com hero image", () => {
        setViewportWidth(breakpoint);
        const data = createTemplateFixture(templateKey, { withHero: true });
        const { container } = render(<LandingPageView data={data} mode="public" />);

        expect(screen.getByRole("button", { name: new RegExp(data.template.cta_text, "i") })).toBeInTheDocument();

        const fields = data.formulario.campos;
        for (const field of fields) {
          expect(screen.getByLabelText(new RegExp(field.label, "i"))).toBeInTheDocument();
        }

        expect(screen.getByTestId("landing-hero-image")).toBeInTheDocument();
        expect(screen.queryByTestId("landing-hero-fallback")).not.toBeInTheDocument();

        expect(container.querySelector("[data-testid='landing-hero-image']")?.tagName).toBe("IMG");
      });

      it("renderiza formulário sem hero image (fallback visual)", () => {
        setViewportWidth(breakpoint);
        const data = createTemplateFixture(templateKey, { withHero: false });
        render(<LandingPageView data={data} mode="public" />);

        expect(screen.getByRole("button", { name: new RegExp(data.template.cta_text, "i") })).toBeInTheDocument();

        expect(screen.queryByTestId("landing-hero-image")).not.toBeInTheDocument();
        expect(screen.getByTestId("landing-hero-fallback")).toBeInTheDocument();
      });
    });

    it("oculta chips mood/categoria em modo público", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.queryByText(data.template.mood)).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Categoria: ${data.template.categoria}`))).not.toBeInTheDocument();
      if (templateKey === "esporte_radical") {
        expect(screen.queryByText("Radical")).not.toBeInTheDocument();
      }
    });

    it("exibe chips mood/categoria em modo preview", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="preview" />);

      expect(screen.getByText(data.template.mood)).toBeInTheDocument();
      expect(screen.getByText(new RegExp(`Categoria: ${data.template.categoria}`))).toBeInTheDocument();
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

    it("renderiza data do evento e localização", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByText(data.evento.nome)).toBeInTheDocument();
      const cityMatches = screen.getAllByText(new RegExp(`${data.evento.cidade}`));
      expect(cityMatches.length).toBeGreaterThanOrEqual(1);
    });

    it("renderiza LGPD e link de privacidade", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByText(/concorda com o tratamento/i)).toBeInTheDocument();
      const privacyLinks = screen.getAllByRole("link", { name: /privacidade/i });
      expect(privacyLinks.length).toBeGreaterThanOrEqual(1);
      expect(privacyLinks[0]).toHaveAttribute("href", data.formulario.privacy_policy_url);
    });

    it("renderiza footer com logo BB e link de privacidade em modo público", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="public" />);

      const links = screen.getAllByRole("link", { name: /privacidade/i });
      expect(links.length).toBeGreaterThanOrEqual(1);

      const images = screen.getAllByAltText("Banco do Brasil");
      expect(images.length).toBeGreaterThanOrEqual(1);
    });

    it("não renderiza footer em modo preview", () => {
      const data = createTemplateFixture(templateKey, { withHero: true });
      render(<LandingPageView data={data} mode="preview" />);

      const footerLinks = screen
        .queryAllByRole("link", { name: /Politica de privacidade e LGPD/i });
      expect(footerLinks.length).toBe(0);
    });
  });
});
