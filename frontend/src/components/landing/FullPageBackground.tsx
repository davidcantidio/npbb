import { Box } from "@mui/material";
import type { ReactNode } from "react";

import type { LandingPageData } from "../../services/landing_public";
import {
  getTemplateBackgroundGradient,
  getTemplateOverlayVariant,
  renderGraphicOverlay,
} from "./landingStyle";

type FullPageBackgroundProps = {
  data: LandingPageData;
  children: ReactNode;
  fullHeight?: boolean;
  layerMode?: "fixed" | "embedded";
};

export default function FullPageBackground({
  data,
  children,
  fullHeight = true,
  layerMode = "fixed",
}: FullPageBackgroundProps) {
  const backgroundGradient = getTemplateBackgroundGradient(data);
  const templateCategory = String(data.template.categoria || "generico").trim().toLowerCase() || "generico";
  const overlayVariant = getTemplateOverlayVariant(data);
  const contentMinHeight = fullHeight ? "100vh" : "auto";
  const layerPosition = layerMode === "embedded" ? "absolute" : "fixed";
  const layerWidth = layerMode === "embedded" ? "100%" : "100vw";
  const layerMinHeight = layerMode === "embedded" ? "100%" : "100vh";
  const containerOverflow = layerMode === "embedded" ? "hidden" : undefined;

  return (
    <Box
      data-testid="full-page-background-root"
      data-layer-mode={layerMode}
      sx={{ position: "relative", minHeight: contentMinHeight, overflow: containerOverflow }}
    >
      <Box
        data-testid="full-page-background-layer"
        data-template-category={templateCategory}
        data-overlay-variant={overlayVariant}
        data-layer-mode={layerMode}
        aria-hidden="true"
        sx={{
          position: layerPosition,
          inset: 0,
          width: layerWidth,
          minHeight: layerMinHeight,
          background: backgroundGradient,
          zIndex: 0,
        }}
      />
      <Box
        data-testid="full-page-overlay-layer"
        data-template-category={templateCategory}
        data-overlay-variant={overlayVariant}
        data-layer-mode={layerMode}
        aria-hidden="true"
        sx={{
          position: layerPosition,
          inset: 0,
          width: layerWidth,
          minHeight: layerMinHeight,
          overflow: "hidden",
          pointerEvents: "none",
          zIndex: 1,
        }}
      >
        {renderGraphicOverlay(data)}
      </Box>
      <Box
        data-testid="full-page-background-content"
        sx={{
          position: "relative",
          zIndex: 2,
          minHeight: contentMinHeight,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
