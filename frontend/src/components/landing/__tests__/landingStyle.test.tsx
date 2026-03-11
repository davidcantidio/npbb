import { describe, expect, it } from "vitest";

import {
  getTemplateBackgroundGradient,
  getTemplateFooterTextColor,
  getTemplateOverlayOpacity,
  getTemplateOverlayVariant,
} from "../landingStyle";
import {
  EXPECTED_TEMPLATE_GRADIENTS,
  EXPECTED_TEMPLATE_OVERLAY_OPACITY,
  EXPECTED_TEMPLATE_OVERLAY_VARIANTS,
  TEMPLATE_KEYS,
  createTemplateFixture,
} from "./landingFixtures";

const EXPECTED_FOOTER_TEXT_COLORS = {
  corporativo: "rgba(248, 250, 252, 0.82)",
  esporte_convencional: "rgba(248, 250, 252, 0.82)",
  esporte_radical: "rgba(17, 24, 39, 0.82)",
  evento_cultural: "rgba(17, 24, 39, 0.82)",
  show_musical: "rgba(248, 250, 252, 0.82)",
  tecnologia: "rgba(248, 250, 252, 0.82)",
  generico: "rgba(248, 250, 252, 0.82)",
} as const;

describe("landingStyle contract", () => {
  it.each(TEMPLATE_KEYS)("mantem gradiente, opacidade e variante de overlay para %s", (templateKey) => {
    const fixture = createTemplateFixture(templateKey);

    expect(getTemplateBackgroundGradient(fixture)).toBe(EXPECTED_TEMPLATE_GRADIENTS[templateKey]);
    expect(getTemplateOverlayOpacity(fixture)).toBe(EXPECTED_TEMPLATE_OVERLAY_OPACITY[templateKey]);
    expect(getTemplateOverlayVariant(fixture)).toBe(EXPECTED_TEMPLATE_OVERLAY_VARIANTS[templateKey]);
  });

  it.each(TEMPLATE_KEYS)("mantem cor de rodape esperada para %s", (templateKey) => {
    const fixture = createTemplateFixture(templateKey);

    expect(getTemplateFooterTextColor(fixture)).toBe(EXPECTED_FOOTER_TEXT_COLORS[templateKey]);
  });

  it("faz fallback da variante de overlay pelo graphics_style para categorias internas desconhecidas", () => {
    const fixture = createTemplateFixture("generico");
    fixture.template = {
      ...fixture.template,
      categoria: "categoria-interna",
      graphics_style: "organic",
    };

    expect(getTemplateOverlayVariant(fixture)).toBe("evento_cultural");
  });
});
