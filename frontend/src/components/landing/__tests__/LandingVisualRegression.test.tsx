import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LandingPageView, { buildLandingTheme } from "../LandingPageView";
import {
  BREAKPOINTS,
  EXPECTED_TEMPLATE_OVERLAY_VARIANTS,
  HERO_LAYOUT_MAP,
  TEMPLATE_KEYS,
  createTemplateFixture,
} from "./landingFixtures";

function setViewportWidth(width: number) {
  Object.defineProperty(window, "innerWidth", { writable: true, configurable: true, value: width });
  window.dispatchEvent(new Event("resize"));
}

describe("ISSUE-F3-01-001 — Regressao visual de fundo tematico", () => {
  describe.each(TEMPLATE_KEYS)("Template: %s", (templateKey) => {
    describe.each(BREAKPOINTS)("Breakpoint: %dpx", (breakpoint) => {
      it("renderiza formulario sem blocos legados e preserva metadata do fundo", () => {
        setViewportWidth(breakpoint);
        const data = createTemplateFixture(templateKey);
        render(<LandingPageView data={data} mode="public" />);

        expect(screen.getByRole("button", { name: new RegExp(data.template.cta_text, "i") })).toBeInTheDocument();
        for (const field of data.formulario.campos) {
          expect(screen.getByLabelText(new RegExp(field.label, "i"))).toBeInTheDocument();
        }

        expect(screen.queryByTestId("landing-hero-image")).not.toBeInTheDocument();
        expect(screen.queryByTestId("landing-hero-fallback")).not.toBeInTheDocument();

        const backgroundLayer = screen.getByTestId("full-page-background-layer");
        expect(backgroundLayer).toHaveAttribute("data-template-category", templateKey);
        expect(backgroundLayer).toHaveAttribute("data-overlay-variant", EXPECTED_TEMPLATE_OVERLAY_VARIANTS[templateKey]);

        const overlayLayer = screen.getByTestId("full-page-overlay-layer");
        expect(overlayLayer).toHaveAttribute("data-template-category", templateKey);
        expect(overlayLayer).toHaveAttribute("data-overlay-variant", EXPECTED_TEMPLATE_OVERLAY_VARIANTS[templateKey]);
      });
    });

    it("oculta informacoes operacionais extras em modo publico", () => {
      const data = createTemplateFixture(templateKey);
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.queryByText(data.template.mood)).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Categoria: ${data.template.categoria}`))).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Template: ${data.template.tema}`))).not.toBeInTheDocument();
    });

    it("exibe apenas badge em modo preview", () => {
      const data = createTemplateFixture(templateKey);
      render(<LandingPageView data={data} mode="preview" />);

      expect(screen.getByTestId("landing-preview-badge")).toHaveTextContent("Preview");
      expect(screen.queryByText(data.template.mood)).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Categoria: ${data.template.categoria}`))).not.toBeInTheDocument();
    });

    it("integra o wrapper FullPageBackground na landing", () => {
      const data = createTemplateFixture(templateKey);
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

    it("mantem hero_layout do contrato de template", () => {
      const data = createTemplateFixture(templateKey);
      expect(data.template.hero_layout).toBe(HERO_LAYOUT_MAP[templateKey]);
    });

    it("gera tema MUI com borderRadius 20 e cores do template", () => {
      const data = createTemplateFixture(templateKey);
      const theme = buildLandingTheme(data);

      expect(theme.shape.borderRadius).toBe(20);
      expect(theme.palette.primary.main).toBe(data.template.color_primary);
      expect(theme.palette.secondary.main).toBe(data.template.color_secondary);
    });

    it("renderiza titulo da ativacao e oculta contexto legado de localizacao", () => {
      const data = createTemplateFixture(templateKey);
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByRole("heading", { name: data.ativacao!.nome })).toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`${data.evento.cidade}`))).not.toBeInTheDocument();
    });

    it("renderiza LGPD e link de privacidade", () => {
      const data = createTemplateFixture(templateKey);
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByText(/concorda com o tratamento/i)).toBeInTheDocument();
      const privacyLinks = screen.getAllByRole("link", { name: /privacidade/i });
      expect(privacyLinks.length).toBeGreaterThanOrEqual(1);
      expect(privacyLinks[0]).toHaveAttribute("href", data.formulario.privacy_policy_url);
    });

    it("renderiza footer minimo textual e link de privacidade em modo publico", () => {
      const data = createTemplateFixture(templateKey);
      const { container } = render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByTestId("minimal-footer-tagline")).toHaveTextContent(
        "Banco do Brasil. Pra tudo que voce imaginar.",
      );
      expect(container.querySelector("[data-testid='minimal-footer'] img")).toBeNull();
      expect(container.querySelector("[data-testid='minimal-footer'] svg")).toBeNull();
    });

    it("renderiza footer minimo tambem em modo preview", () => {
      const data = createTemplateFixture(templateKey);
      render(<LandingPageView data={data} mode="preview" />);

      const footerLinks = screen.getAllByRole("link", { name: /Politica de privacidade e LGPD/i });
      expect(footerLinks.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("usa cor de rodape do template corporativo", () => {
    const data = createTemplateFixture("corporativo");
    render(<LandingPageView data={data} mode="public" />);

    expect(screen.getByTestId("minimal-footer")).toHaveStyle({ color: "rgba(255, 255, 255, 0.75)" });
  });

  it("usa cor de rodape do template evento_cultural", () => {
    const data = createTemplateFixture("evento_cultural");
    render(<LandingPageView data={data} mode="public" />);

    expect(screen.getByTestId("minimal-footer")).toHaveStyle({ color: "rgba(51, 51, 189, 0.75)" });
  });
});
