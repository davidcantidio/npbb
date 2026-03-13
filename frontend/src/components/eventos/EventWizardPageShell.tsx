import { Box } from "@mui/material";
import type { ReactNode } from "react";

export const WIZARD_ACTION_BUTTON_SX = {
  textTransform: "none",
  whiteSpace: "nowrap",
} as const;

type EventWizardPageShellProps = {
  children: ReactNode;
  width?: "regular" | "wide";
  testId?: string;
};

const MAX_WIDTH_BY_VARIANT = {
  regular: 1080,
  wide: 1280,
} as const;

export default function EventWizardPageShell({
  children,
  width = "regular",
  testId,
}: EventWizardPageShellProps) {
  return (
    <Box
      data-testid={testId}
      sx={{
        width: "100%",
        maxWidth: MAX_WIDTH_BY_VARIANT[width],
        mx: "auto",
      }}
    >
      {children}
    </Box>
  );
}
