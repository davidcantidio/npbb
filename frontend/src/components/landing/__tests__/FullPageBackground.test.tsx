import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
  getTemplateBackgroundGradient,
  getTemplateOverlayOpacity,
  getTemplateOverlayVariant,
} from "../landingStyle";
import FullPageBackground from "../FullPageBackground";
import {
  EXPECTED_TEMPLATE_GRADIENTS,
  EXPECTED_TEMPLATE_OVERLAY_OPACITY,
  EXPECTED_TEMPLATE_OVERLAY_VARIANTS,
  TEMPLATE_KEYS,
  createTemplateFixture,
} from "./landingFixtures";

describe("FullPageBackground", () => {
  it.each(TEMPLATE_KEYS)("resolve o gradiente correto para template %s", (templateKey) => {
    expect(getTemplateBackgroundGradient(createTemplateFixture(templateKey))).toBe(EXPECTED_TEMPLATE_GRADIENTS[templateKey]);
  });

  it.each(TEMPLATE_KEYS)("resolve opacidade de overlay para template %s", (templateKey) => {
    expect(getTemplateOverlayOpacity(createTemplateFixture(templateKey))).toBe(EXPECTED_TEMPLATE_OVERLAY_OPACITY[templateKey]);
  });

  it.each(TEMPLATE_KEYS)("resolve variante explicita de overlay para template %s", (templateKey) => {
    expect(getTemplateOverlayVariant(createTemplateFixture(templateKey))).toBe(EXPECTED_TEMPLATE_OVERLAY_VARIANTS[templateKey]);
  });

  it("usa fallback generico de gradiente e opacidade para categoria desconhecida", () => {
    const fixture = createTemplateFixture("generico");
    fixture.template = {
      ...fixture.template,
      categoria: "desconhecida",
      graphics_style: "unexpected",
    };

    expect(getTemplateBackgroundGradient(fixture)).toBe(EXPECTED_TEMPLATE_GRADIENTS.generico);
    expect(getTemplateOverlayOpacity(fixture)).toBe(EXPECTED_TEMPLATE_OVERLAY_OPACITY.generico);
    expect(getTemplateOverlayVariant(fixture)).toBe("generico");
  });

  it("renderiza camada fixa cobrindo viewport por padrao, metadata de QA e slot de children", () => {
    const { container } = render(
      <FullPageBackground data={createTemplateFixture("corporativo")}>
        <div data-testid="background-child">conteudo</div>
      </FullPageBackground>,
    );

    expect(screen.getByTestId("background-child")).toBeInTheDocument();
    expect(screen.getByTestId("full-page-background-root")).toHaveAttribute("data-layer-mode", "fixed");

    const backgroundLayer = screen.getByTestId("full-page-background-layer");
    expect(backgroundLayer).toHaveStyle({
      position: "fixed",
      inset: "0",
      width: "100vw",
      minHeight: "100vh",
      zIndex: "0",
    });
    expect(backgroundLayer).toHaveAttribute("data-template-category", "corporativo");
    expect(backgroundLayer).toHaveAttribute("data-overlay-variant", "corporativo");
    expect(backgroundLayer).toHaveAttribute("data-layer-mode", "fixed");

    const overlayLayer = screen.getByTestId("full-page-overlay-layer");
    expect(overlayLayer).toHaveStyle({
      position: "fixed",
      inset: "0",
      width: "100vw",
      minHeight: "100vh",
      pointerEvents: "none",
      zIndex: "1",
    });
    expect(overlayLayer).toHaveAttribute("data-template-category", "corporativo");
    expect(overlayLayer).toHaveAttribute("data-overlay-variant", "corporativo");
    expect(overlayLayer).toHaveAttribute("data-layer-mode", "fixed");

    const contentLayer = screen.getByTestId("full-page-background-content");
    expect(contentLayer).toHaveStyle({
      position: "relative",
      zIndex: "2",
      minHeight: "100vh",
    });

    expect(container.querySelectorAll("img")).toHaveLength(0);
  });

  it("renderiza camada embutida em modo embedded sem ocupar viewport inteira", () => {
    render(
      <FullPageBackground data={createTemplateFixture("show_musical")} fullHeight={false} layerMode="embedded">
        <div data-testid="background-child">conteudo</div>
      </FullPageBackground>,
    );

    const root = screen.getByTestId("full-page-background-root");
    expect(root).toHaveAttribute("data-layer-mode", "embedded");
    expect(root).toHaveStyle({
      position: "relative",
      minHeight: "auto",
      overflow: "hidden",
    });

    const backgroundLayer = screen.getByTestId("full-page-background-layer");
    expect(backgroundLayer).toHaveStyle({
      position: "absolute",
      inset: "0",
      width: "100%",
      minHeight: "100%",
      zIndex: "0",
    });
    expect(backgroundLayer).toHaveAttribute("data-layer-mode", "embedded");

    const overlayLayer = screen.getByTestId("full-page-overlay-layer");
    expect(overlayLayer).toHaveStyle({
      position: "absolute",
      inset: "0",
      width: "100%",
      minHeight: "100%",
      pointerEvents: "none",
      zIndex: "1",
    });
    expect(overlayLayer).toHaveAttribute("data-layer-mode", "embedded");

    const contentLayer = screen.getByTestId("full-page-background-content");
    expect(contentLayer).toHaveStyle({
      position: "relative",
      zIndex: "2",
      minHeight: "auto",
    });
  });
});
