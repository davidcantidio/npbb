import { CssBaseline, ThemeProvider } from "@mui/material";
import { useMemo } from "react";
import { Outlet } from "react-router-dom";

import { createAppTheme } from "./index";
import { useThemeMode } from "./ThemeModeProvider";

export default function AppThemeShell() {
  const { resolvedMode } = useThemeMode();
  const theme = useMemo(() => createAppTheme(resolvedMode), [resolvedMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Outlet />
    </ThemeProvider>
  );
}
