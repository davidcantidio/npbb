import { alpha } from "@mui/material/styles";
import { describe, expect, it } from "vitest";

import {
  FORM_ONLY_CONTENT_WIDTH_SX,
  FORM_ONLY_SURFACE_BORDER_RADIUS,
  FORM_ONLY_SURFACE_PADDING_SX,
  getFormOnlySurfaceSx,
  resolveFormOnlySurfaceBackground,
} from "../formOnlySurface";

const FORM_LAYOUT_FIXTURE = {
  formCardBackground: "#FFFFFF",
  formCardBorder: "2px solid rgba(252, 252, 48, 0.6)",
  formCardShadow: "0 20px 44px rgba(0,0,0,0.24)",
};

describe("formOnlySurface", () => {
  it("define o contrato responsivo de largura compartilhado", () => {
    const responsiveWidth = FORM_ONLY_CONTENT_WIDTH_SX as unknown as Record<string, { width: string }>;

    expect(FORM_ONLY_CONTENT_WIDTH_SX.width).toBe("min(92vw, 440px)");
    expect(responsiveWidth["@media (min-width:768px)"].width).toBe("min(480px, 90vw)");
    expect(responsiveWidth["@media (min-width:1280px)"].width).toBe("min(520px, 90vw)");
  });

  it("define raio de 24px e padding responsivo para a surface", () => {
    const surfaceSx = getFormOnlySurfaceSx(FORM_LAYOUT_FIXTURE);
    const responsivePadding =
      FORM_ONLY_SURFACE_PADDING_SX as unknown as Record<string, { padding: string }>;
    const surfaceSxWithMedia: Record<string, unknown> = surfaceSx;

    expect(FORM_ONLY_SURFACE_BORDER_RADIUS).toBe("24px");
    expect(FORM_ONLY_SURFACE_PADDING_SX.padding).toBe("20px");
    expect(responsivePadding["@media (min-width:768px)"].padding).toBe("32px");
    expect(surfaceSx.borderRadius).toBe("24px");
    expect(surfaceSx.padding).toBe("20px");
    expect(surfaceSxWithMedia["@media (min-width:768px)"] as Record<string, unknown>).toMatchObject({
      padding: "32px",
    });
  });

  it("normaliza fundo sólido da gamificação para branco semitransparente", () => {
    const normalized = resolveFormOnlySurfaceBackground("#FFFFFF", {
      preferTranslucentSolidBackground: true,
    });
    const surfaceSx = getFormOnlySurfaceSx(FORM_LAYOUT_FIXTURE, {
      preferTranslucentSolidBackground: true,
    });

    expect(normalized).toBe(alpha("#FFFFFF", 0.92));
    expect(surfaceSx.bgcolor).toBe(alpha("#FFFFFF", 0.92));
  });

  it("preserva backgrounds que já são translúcidos", () => {
    const translucent = "rgba(255, 255, 255, 0.96)";

    expect(
      resolveFormOnlySurfaceBackground(translucent, {
        preferTranslucentSolidBackground: true,
      }),
    ).toBe(translucent);
  });
});
