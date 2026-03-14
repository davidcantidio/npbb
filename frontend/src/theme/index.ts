import { createTheme } from "@mui/material/styles";

import type { PaletteMode } from "./shared";
import {
  APP_FONT_FAMILY,
  APP_SHAPE_RADIUS,
  APP_THEME_MODE_STORAGE_KEY,
  LANDING_SHAPE_RADIUS,
  createAppPalette,
  createCommonComponents,
  createCommonThemeOptions,
  createCommonTypography,
  createToolbarMixins,
  getFocusVisibleStyles,
} from "./shared";

export function createAppTheme(mode: PaletteMode) {
  return createTheme(
    createCommonThemeOptions({
      palette: createAppPalette(mode),
      shapeRadius: APP_SHAPE_RADIUS,
      scale: "app",
    }),
  );
}

export {
  APP_FONT_FAMILY,
  APP_SHAPE_RADIUS,
  APP_THEME_MODE_STORAGE_KEY,
  LANDING_SHAPE_RADIUS,
  createAppPalette,
  createCommonComponents,
  createCommonThemeOptions,
  createCommonTypography,
  createToolbarMixins,
  getFocusVisibleStyles,
};
