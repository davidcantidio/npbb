import { Chip } from "@mui/material";
import { alpha } from "@mui/material/styles";

import type { LayoutVisualSpec } from "./landingStyle";
import { isDarkColor } from "./landingStyle";

type LandingPreviewBadgeProps = {
  layout: LayoutVisualSpec;
};

export default function LandingPreviewBadge({ layout }: LandingPreviewBadgeProps) {
  return (
    <Chip
      data-testid="landing-preview-badge"
      label="Preview"
      sx={{
        position: "fixed",
        top: { xs: 16, md: 24 },
        right: { xs: 16, md: 24 },
        zIndex: 3,
        fontWeight: 800,
        bgcolor: alpha("#FFFFFF", isDarkColor(layout.pageTextColor) ? 0.16 : 0.84),
        color: layout.pageTextColor,
        border: `1px solid ${alpha("#FFFFFF", 0.18)}`,
        backdropFilter: "blur(10px)",
      }}
    />
  );
}
