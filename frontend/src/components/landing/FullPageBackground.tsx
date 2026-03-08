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
};

export default function FullPageBackground({
  data,
  children,
  fullHeight = true,
}: FullPageBackgroundProps) {
  const backgroundGradient = getTemplateBackgroundGradient(data);
  const templateCategory = String(data.template.categoria || "generico").trim().toLowerCase() || "generico";
  const overlayVariant = getTemplateOverlayVariant(data);
  const contentMinHeight = fullHeight ? "100vh" : "auto";

  return (
    <Box sx={{ position: "relative", minHeight: contentMinHeight }}>
      <Box
        data-testid="full-page-background-layer"
        data-template-category={templateCategory}
        data-overlay-variant={overlayVariant}
        aria-hidden="true"
        sx={{
          position: "fixed",
          inset: 0,
          width: "100vw",
          minHeight: "100vh",
          background: backgroundGradient,
          zIndex: 0,
        }}
      />
      <Box
        data-testid="full-page-overlay-layer"
        data-template-category={templateCategory}
        data-overlay-variant={overlayVariant}
        aria-hidden="true"
        sx={{
          position: "fixed",
          inset: 0,
          width: "100vw",
          minHeight: "100vh",
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
