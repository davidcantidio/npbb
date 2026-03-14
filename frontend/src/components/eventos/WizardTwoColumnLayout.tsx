import { Box, useMediaQuery, useTheme } from "@mui/material";
import type { ReactNode } from "react";

type WizardTwoColumnLayoutProps = {
  leftContent: ReactNode;
  rightContent: ReactNode;
  desktopColumns: string;
  rightSticky?: boolean;
  stickyTop?: number | string;
  testId?: string;
  leftTestId?: string;
  rightTestId?: string;
};

function resolveStickyTop(stickyTop: number | string, spacing: (value: number) => string) {
  return typeof stickyTop === "number" ? spacing(stickyTop) : stickyTop;
}

export default function WizardTwoColumnLayout({
  leftContent,
  rightContent,
  desktopColumns,
  rightSticky = true,
  stickyTop = 3,
  testId,
  leftTestId,
  rightTestId,
}: WizardTwoColumnLayoutProps) {
  const theme = useTheme();
  const isDesktopLayout = useMediaQuery(theme.breakpoints.up("md"));

  return (
    <Box
      data-testid={testId}
      data-layout-mode={isDesktopLayout ? "side-by-side" : "stacked"}
      sx={{
        display: "grid",
        gap: { xs: 3, xl: 4 },
        alignItems: "start",
        gridTemplateColumns: isDesktopLayout ? desktopColumns : "minmax(0, 1fr)",
      }}
    >
      <Box data-testid={leftTestId} sx={{ minWidth: 0, width: "100%" }}>
        {leftContent}
      </Box>

      <Box
        data-testid={rightTestId}
        sx={{
          minWidth: 0,
          width: "100%",
          alignSelf: "start",
          position: isDesktopLayout && rightSticky ? "sticky" : "static",
          top: isDesktopLayout && rightSticky ? resolveStickyTop(stickyTop, theme.spacing) : "auto",
        }}
      >
        {rightContent}
      </Box>
    </Box>
  );
}
