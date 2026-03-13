import { alpha } from "@mui/material/styles";

import type { LayoutVisualSpec } from "./landingStyle";

type FormOnlySurfaceLayout = Pick<
  LayoutVisualSpec,
  "formCardBackground" | "formCardBorder" | "formCardShadow"
>;

type FormOnlySurfaceOptions = {
  preferTranslucentSolidBackground?: boolean;
  previewMobileMode?: boolean;
};

export const FORM_ONLY_CONTENT_WIDTH_SX = {
  width: "min(92vw, 440px)",
  "@media (min-width:768px)": {
    width: "min(480px, 90vw)",
  },
  "@media (min-width:1280px)": {
    width: "min(520px, 90vw)",
  },
} as const;

export const PREVIEW_FORM_ONLY_CONTENT_WIDTH_SX = {
  width: "100%",
  maxWidth: "100%",
} as const;

export const FORM_ONLY_SURFACE_BORDER_RADIUS = "24px";

export const FORM_ONLY_SURFACE_PADDING_SX = {
  padding: "20px",
  "@media (min-width:768px)": {
    padding: "32px",
  },
} as const;

export const PREVIEW_FORM_ONLY_SURFACE_PADDING_SX = {
  padding: "20px",
} as const;

export function resolveFormOnlySurfaceBackground(
  formCardBackground: string,
  options: FormOnlySurfaceOptions = {},
) {
  const background = String(formCardBackground || "").trim();
  if (!background || !options.preferTranslucentSolidBackground) {
    return background;
  }

  if (
    /^(rgba|hsla)\(/i.test(background) ||
    /^(linear-gradient|radial-gradient|conic-gradient)\(/i.test(background) ||
    background.toLowerCase() === "transparent"
  ) {
    return background;
  }

  try {
    return alpha(background, 0.92);
  } catch {
    return background;
  }
}

export function getFormOnlySurfaceSx(
  layout: FormOnlySurfaceLayout,
  options: FormOnlySurfaceOptions = {},
) {
  return {
    ...(options.previewMobileMode
      ? PREVIEW_FORM_ONLY_SURFACE_PADDING_SX
      : FORM_ONLY_SURFACE_PADDING_SX),
    borderRadius: FORM_ONLY_SURFACE_BORDER_RADIUS,
    bgcolor: resolveFormOnlySurfaceBackground(layout.formCardBackground, options),
    border: layout.formCardBorder,
    boxShadow: layout.formCardShadow,
  };
}
