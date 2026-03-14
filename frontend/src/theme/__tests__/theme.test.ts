import { describe, expect, it } from "vitest";

import { createAppTheme } from "../index";

function resolveStyleOverride(override: unknown, theme: ReturnType<typeof createAppTheme>) {
  if (typeof override === "function") {
    return (override as (props: { theme: ReturnType<typeof createAppTheme> }) => unknown)({ theme });
  }

  return override;
}

describe("createAppTheme", () => {
  it("gera temas light e dark com mixin responsivo de toolbar", () => {
    const lightTheme = createAppTheme("light");
    const darkTheme = createAppTheme("dark");

    expect(lightTheme.palette.mode).toBe("light");
    expect(darkTheme.palette.mode).toBe("dark");
    expect(lightTheme.mixins.toolbar).toMatchObject({
      minHeight: 56,
      "@media (min-width:900px)": { minHeight: 64 },
    });
  });

  it("padroniza foco de botao e neutraliza surfaces principais", () => {
    const theme = createAppTheme("light");

    const buttonRoot = resolveStyleOverride(
      theme.components?.MuiButton?.styleOverrides?.root,
      theme,
    ) as Record<string, Record<string, string | number>>;
    const paperRoot = resolveStyleOverride(
      theme.components?.MuiPaper?.styleOverrides?.root,
      theme,
    ) as Record<string, string>;
    const dialogPaper = resolveStyleOverride(
      theme.components?.MuiDialog?.styleOverrides?.paper,
      theme,
    ) as Record<string, string>;

    expect(theme.components?.MuiButton?.defaultProps).toMatchObject({
      disableElevation: true,
    });
    expect(buttonRoot["&:focus-visible"]).toMatchObject({
      outline: `2px solid ${theme.palette.info.main}`,
      outlineOffset: 2,
    });
    expect(paperRoot).toMatchObject({
      backgroundColor: theme.palette.background.paper,
      border: `1px solid ${theme.palette.divider}`,
    });
    expect(dialogPaper).toMatchObject({
      border: `1px solid ${theme.palette.divider}`,
      boxShadow: theme.shadows[8],
    });
  });

  it("configura tooltip, alert, chip e progress para a linguagem clean", () => {
    const theme = createAppTheme("dark");

    const tooltipStyle = resolveStyleOverride(
      theme.components?.MuiTooltip?.styleOverrides?.tooltip,
      theme,
    ) as Record<string, string | number>;
    const filledErrorAlert = resolveStyleOverride(
      theme.components?.MuiAlert?.styleOverrides?.filledError,
      theme,
    ) as Record<string, string>;
    const chipRoot = resolveStyleOverride(
      theme.components?.MuiChip?.styleOverrides?.root,
      theme,
    ) as Record<string, string | number>;
    const linearProgressRoot = resolveStyleOverride(
      theme.components?.MuiLinearProgress?.styleOverrides?.root,
      theme,
    ) as Record<string, string | number>;

    expect(tooltipStyle).toMatchObject({
      backgroundColor: theme.palette.background.paper,
      color: theme.palette.text.primary,
      border: `1px solid ${theme.palette.divider}`,
    });
    expect(filledErrorAlert.color).toBe(theme.palette.text.primary);
    expect(chipRoot.borderRadius).toBe(999);
    expect(linearProgressRoot).toMatchObject({
      height: 8,
      borderRadius: 999,
    });
  });
});
