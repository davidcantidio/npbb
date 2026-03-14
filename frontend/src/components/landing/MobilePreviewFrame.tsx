import { Box } from "@mui/material";
import type { ReactNode } from "react";

type MobilePreviewFrameProps = {
  children: ReactNode;
  testId?: string;
};

const PREVIEW_MOBILE_WIDTH = "390px";
const PREVIEW_MOBILE_BASE_HEIGHT = "700px";

export default function MobilePreviewFrame({
  children,
  testId = "event-lead-preview-host",
}: MobilePreviewFrameProps) {
  return (
    <Box
      data-testid={testId}
      sx={{
        "--preview-mobile-width": PREVIEW_MOBILE_WIDTH,
        "--preview-mobile-base-height": PREVIEW_MOBILE_BASE_HEIGHT,
        mt: 1,
        position: "relative",
        isolation: "isolate",
        width: "var(--preview-mobile-width)",
        maxWidth: "100%",
        height: "min(var(--preview-mobile-base-height), calc(100vh - 200px))",
        minHeight: "540px",
        overflowX: "hidden",
        overflowY: "auto",
        overscrollBehavior: "contain",
        borderRadius: "36px",
        border: "1px solid",
        borderColor: "divider",
        bgcolor: "common.white",
        boxShadow: "0 28px 80px rgba(15, 23, 42, 0.22)",
      }}
    >
      <Box
        aria-hidden="true"
        sx={{
          position: "sticky",
          top: 12,
          zIndex: 3,
          mx: "auto",
          mb: -2,
          width: 120,
          height: 18,
          borderRadius: 999,
          bgcolor: "rgba(15, 23, 42, 0.9)",
        }}
      />
      <Box
        sx={{
          minHeight: "100%",
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
