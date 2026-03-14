import { alpha } from "@mui/material/styles";
import type {
  PaletteMode,
  Shadows,
  Theme,
  ThemeOptions,
} from "@mui/material/styles";

export const APP_THEME_MODE_STORAGE_KEY = "npbb-theme-mode";

export const APP_FONT_FAMILY =
  '"Roboto Flex Variable", "Roboto", "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif';

export const APP_SHAPE_RADIUS = 16;
export const LANDING_SHAPE_RADIUS = 20;

const COMMON_SHADOWS: Shadows = [
  "none",
  "0 1px 2px rgba(15, 23, 42, 0.04)",
  "0 4px 12px rgba(15, 23, 42, 0.05)",
  "0 8px 20px rgba(15, 23, 42, 0.06)",
  "0 10px 24px rgba(15, 23, 42, 0.07)",
  "0 12px 28px rgba(15, 23, 42, 0.08)",
  "0 14px 32px rgba(15, 23, 42, 0.09)",
  "0 16px 36px rgba(15, 23, 42, 0.1)",
  "0 18px 40px rgba(15, 23, 42, 0.11)",
  "0 20px 44px rgba(15, 23, 42, 0.12)",
  "0 22px 48px rgba(15, 23, 42, 0.13)",
  "0 24px 52px rgba(15, 23, 42, 0.14)",
  "0 26px 56px rgba(15, 23, 42, 0.15)",
  "0 28px 60px rgba(15, 23, 42, 0.16)",
  "0 30px 64px rgba(15, 23, 42, 0.17)",
  "0 32px 68px rgba(15, 23, 42, 0.18)",
  "0 34px 72px rgba(15, 23, 42, 0.19)",
  "0 36px 76px rgba(15, 23, 42, 0.2)",
  "0 38px 80px rgba(15, 23, 42, 0.21)",
  "0 40px 84px rgba(15, 23, 42, 0.22)",
  "0 42px 88px rgba(15, 23, 42, 0.23)",
  "0 44px 92px rgba(15, 23, 42, 0.24)",
  "0 46px 96px rgba(15, 23, 42, 0.25)",
  "0 48px 100px rgba(15, 23, 42, 0.26)",
  "0 50px 104px rgba(15, 23, 42, 0.27)",
];

function createFocusRing(theme: Theme) {
  return {
    outline: `2px solid ${theme.palette.info.main}`,
    outlineOffset: 2,
  };
}

function createSelectionColor(theme: Theme) {
  return alpha(theme.palette.info.main, theme.palette.mode === "dark" ? 0.32 : 0.18);
}

export function getFocusVisibleStyles(theme: Theme) {
  return createFocusRing(theme);
}

export function createAppPalette(mode: PaletteMode): ThemeOptions["palette"] {
  if (mode === "dark") {
    return {
      mode,
      primary: {
        main: "#F5F5F5",
        light: "#FFFFFF",
        dark: "#E5E5E5",
        contrastText: "#0A0A0A",
      },
      secondary: {
        main: "#A1A1AA",
        light: "#D4D4D8",
        dark: "#71717A",
        contrastText: "#0A0A0A",
      },
      info: {
        main: "#60A5FA",
      },
      success: {
        main: "#34D399",
      },
      warning: {
        main: "#FBBF24",
      },
      error: {
        main: "#F87171",
      },
      background: {
        default: "#0A0A0A",
        paper: "#111111",
      },
      text: {
        primary: "#FAFAFA",
        secondary: "#A1A1AA",
      },
      divider: alpha("#FFFFFF", 0.12),
      action: {
        hover: alpha("#FFFFFF", 0.06),
        selected: alpha("#FFFFFF", 0.1),
        focus: alpha("#60A5FA", 0.22),
        disabled: alpha("#FFFFFF", 0.38),
        disabledBackground: alpha("#FFFFFF", 0.08),
      },
    };
  }

  return {
    mode,
    primary: {
      main: "#111827",
      light: "#1F2937",
      dark: "#030712",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#475569",
      light: "#64748B",
      dark: "#334155",
      contrastText: "#FFFFFF",
    },
    info: {
      main: "#2563EB",
    },
    success: {
      main: "#059669",
    },
    warning: {
      main: "#D97706",
    },
    error: {
      main: "#DC2626",
    },
    background: {
      default: "#FAFAFA",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#111827",
      secondary: "#475569",
    },
    divider: alpha("#0F172A", 0.12),
    action: {
      hover: alpha("#111827", 0.04),
      selected: alpha("#111827", 0.08),
      focus: alpha("#2563EB", 0.18),
      disabled: alpha("#111827", 0.36),
      disabledBackground: alpha("#111827", 0.08),
    },
  };
}

export function createCommonTypography(scale: "app" | "landing" = "app"): ThemeOptions["typography"] {
  if (scale === "landing") {
    return {
      fontFamily: APP_FONT_FAMILY,
      fontSize: 14,
      fontWeightRegular: 400,
      fontWeightMedium: 600,
      fontWeightBold: 800,
      h1: { fontSize: "2rem", fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.04em" },
      h2: { fontSize: "1.5rem", fontWeight: 800, lineHeight: 1.12, letterSpacing: "-0.03em" },
      h3: { fontSize: "1.25rem", fontWeight: 700, lineHeight: 1.2, letterSpacing: "-0.025em" },
      h4: { fontSize: "1.125rem", fontWeight: 700, lineHeight: 1.25, letterSpacing: "-0.02em" },
      h5: { fontSize: "1.25rem", fontWeight: 800, lineHeight: 1.2, letterSpacing: "-0.025em" },
      h6: { fontSize: "1rem", fontWeight: 700, lineHeight: 1.3, letterSpacing: "-0.015em" },
      body1: { fontSize: "0.9375rem", lineHeight: 1.6 },
      body2: { fontSize: "0.875rem", lineHeight: 1.6 },
      subtitle1: { fontSize: "1rem", lineHeight: 1.55, fontWeight: 600 },
      subtitle2: { fontSize: "0.875rem", lineHeight: 1.5, fontWeight: 600 },
      button: { fontSize: "0.875rem", lineHeight: 1.4, fontWeight: 700, textTransform: "none" },
      caption: { fontSize: "0.75rem", lineHeight: 1.5 },
      overline: {
        fontSize: "0.75rem",
        lineHeight: 1.4,
        fontWeight: 700,
        letterSpacing: "0.08em",
        textTransform: "uppercase",
      },
    };
  }

  return {
    fontFamily: APP_FONT_FAMILY,
    fontSize: 14,
    fontWeightRegular: 400,
    fontWeightMedium: 600,
    fontWeightBold: 700,
    h1: { fontSize: "2.5rem", fontWeight: 750, lineHeight: 1.02, letterSpacing: "-0.05em" },
    h2: { fontSize: "2rem", fontWeight: 750, lineHeight: 1.05, letterSpacing: "-0.04em" },
    h3: { fontSize: "1.5rem", fontWeight: 700, lineHeight: 1.12, letterSpacing: "-0.03em" },
    h4: { fontSize: "1.25rem", fontWeight: 700, lineHeight: 1.2, letterSpacing: "-0.025em" },
    h5: { fontSize: "1.0625rem", fontWeight: 700, lineHeight: 1.3, letterSpacing: "-0.02em" },
    h6: { fontSize: "0.9375rem", fontWeight: 700, lineHeight: 1.35, letterSpacing: "-0.015em" },
    subtitle1: { fontSize: "1rem", fontWeight: 600, lineHeight: 1.5 },
    subtitle2: { fontSize: "0.875rem", fontWeight: 600, lineHeight: 1.45 },
    body1: { fontSize: "0.9375rem", lineHeight: 1.6 },
    body2: { fontSize: "0.875rem", lineHeight: 1.6 },
    button: { fontSize: "0.875rem", lineHeight: 1.3, fontWeight: 700, textTransform: "none" },
    caption: { fontSize: "0.75rem", lineHeight: 1.5 },
    overline: {
      fontSize: "0.75rem",
      lineHeight: 1.4,
      fontWeight: 700,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
    },
  };
}

export function createToolbarMixins(): ThemeOptions["mixins"] {
  return {
    toolbar: {
      minHeight: 56,
      "@media (min-width:0px)": {
        minHeight: 56,
      },
      "@media (min-width:900px)": {
        minHeight: 64,
      },
    },
  };
}

export function createCommonComponents(): ThemeOptions["components"] {
  return {
    MuiCssBaseline: {
      styleOverrides: (theme) => ({
        ":root": {
          colorScheme: theme.palette.mode,
        },
        "*, *::before, *::after": {
          boxSizing: "border-box",
        },
        html: {
          WebkitFontSmoothing: "antialiased",
          MozOsxFontSmoothing: "grayscale",
          textRendering: "optimizeLegibility",
        },
        body: {
          margin: 0,
          backgroundColor: theme.palette.background.default,
          color: theme.palette.text.primary,
        },
        "::selection": {
          backgroundColor: createSelectionColor(theme),
        },
        "h1, h2, h3, h4, h5, h6, p": {
          margin: 0,
        },
        "a, button, [role='button'], input, textarea, select": {
          transition:
            "border-color 160ms ease, background-color 160ms ease, box-shadow 160ms ease, color 160ms ease",
        },
        "a:focus-visible, button:focus-visible, [role='button']:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible":
          createFocusRing(theme),
      }),
    },
    MuiButtonBase: {
      defaultProps: {
        disableRipple: true,
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: ({ theme }) => ({
          minHeight: 36,
          borderRadius: 12,
          fontWeight: 700,
          paddingInline: theme.spacing(1.5),
          "&:focus-visible": createFocusRing(theme),
        }),
        contained: ({ theme }) => ({
          boxShadow: "none",
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
          "&:hover": {
            boxShadow: "none",
            backgroundColor: theme.palette.primary.dark,
          },
        }),
        outlined: ({ theme }) => ({
          borderColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.22 : 0.16),
          "&:hover": {
            borderColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.4 : 0.28),
            backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.08 : 0.03),
          },
        }),
        text: ({ theme }) => ({
          color: theme.palette.text.primary,
          "&:hover": {
            backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.08 : 0.04),
          },
        }),
        sizeLarge: {
          minHeight: 44,
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 12,
          color: theme.palette.text.secondary,
          "&:hover": {
            backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.08 : 0.04),
          },
          "&:focus-visible": createFocusRing(theme),
        }),
      },
    },
    MuiAppBar: {
      defaultProps: {
        color: "transparent",
        elevation: 0,
      },
      styleOverrides: {
        root: ({ theme }) => ({
          boxShadow: "none",
          backgroundColor: alpha(theme.palette.background.default, theme.palette.mode === "dark" ? 0.9 : 0.82),
          borderBottom: `1px solid ${theme.palette.divider}`,
          backdropFilter: "blur(18px)",
        }),
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: ({ theme }) => ({
          backgroundImage: "none",
          backgroundColor: theme.palette.background.paper,
          borderColor: theme.palette.divider,
        }),
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundImage: "none",
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
        }),
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundImage: "none",
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
        }),
      },
    },
    MuiCardActionArea: {
      defaultProps: {
        disableRipple: true,
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: ({ theme }) => ({
          backgroundImage: "none",
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.shadows[8],
        }),
      },
    },
    MuiPopover: {
      styleOverrides: {
        paper: ({ theme }) => ({
          backgroundImage: "none",
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.shadows[6],
        }),
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: ({ theme }) => ({
          backgroundImage: "none",
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.shadows[6],
          marginTop: theme.spacing(0.5),
        }),
        list: {
          padding: 6,
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: ({ theme }) => ({
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.shadows[4],
          padding: theme.spacing(1, 1.25),
          fontSize: theme.typography.pxToRem(12),
          lineHeight: 1.5,
        }),
        arrow: ({ theme }) => ({
          color: theme.palette.background.paper,
          "&::before": {
            border: `1px solid ${theme.palette.divider}`,
            boxSizing: "border-box",
          },
        }),
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 14,
          border: `1px solid ${alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.14 : 0.08)}`,
          alignItems: "flex-start",
        }),
        standardInfo: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.info.main, theme.palette.mode === "dark" ? 0.18 : 0.1),
          color: theme.palette.text.primary,
        }),
        standardSuccess: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.success.main, theme.palette.mode === "dark" ? 0.18 : 0.1),
          color: theme.palette.text.primary,
        }),
        standardWarning: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.warning.main, theme.palette.mode === "dark" ? 0.2 : 0.11),
          color: theme.palette.text.primary,
        }),
        standardError: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.error.main, theme.palette.mode === "dark" ? 0.18 : 0.1),
          color: theme.palette.text.primary,
        }),
        filledInfo: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.info.main, theme.palette.mode === "dark" ? 0.22 : 0.14),
          color: theme.palette.text.primary,
        }),
        filledSuccess: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.success.main, theme.palette.mode === "dark" ? 0.22 : 0.14),
          color: theme.palette.text.primary,
        }),
        filledWarning: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.warning.main, theme.palette.mode === "dark" ? 0.24 : 0.16),
          color: theme.palette.text.primary,
        }),
        filledError: ({ theme }) => ({
          backgroundColor: alpha(theme.palette.error.main, theme.palette.mode === "dark" ? 0.22 : 0.14),
          color: theme.palette.text.primary,
        }),
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: ({ theme }) => ({
          minHeight: 40,
          borderRadius: 10,
          marginBlock: 2,
          "&.Mui-selected": {
            backgroundColor: theme.palette.action.selected,
          },
          "&.Mui-selected:hover, &:hover": {
            backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.08 : 0.04),
          },
          "&:focus-visible": createFocusRing(theme),
        }),
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 12,
          "&.Mui-selected": {
            backgroundColor: theme.palette.action.selected,
          },
          "&.Mui-selected:hover, &:hover": {
            backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.08 : 0.04),
          },
          "&:focus-visible": createFocusRing(theme),
        }),
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 12,
          backgroundColor:
            theme.palette.mode === "dark"
              ? alpha(theme.palette.common.white, 0.03)
              : theme.palette.background.paper,
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.18 : 0.14),
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.32 : 0.24),
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: theme.palette.info.main,
            borderWidth: 1,
          },
        }),
        input: ({ theme }) => ({
          paddingBlock: theme.spacing(1.25),
        }),
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: ({ theme }) => ({
          fontWeight: 500,
          color: theme.palette.text.secondary,
          "&.Mui-focused": {
            color: theme.palette.info.main,
          },
        }),
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: ({ theme }) => ({
          height: 8,
          borderRadius: 999,
          backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.16 : 0.08),
        }),
        bar: {
          borderRadius: 999,
        },
      },
    },
    MuiChip: {
      defaultProps: {
        size: "small",
      },
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 999,
          fontWeight: 700,
          borderColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.18 : 0.12),
        }),
      },
    },
    MuiTextField: {
      defaultProps: {
        size: "small",
      },
    },
    MuiAutocomplete: {
      defaultProps: {
        size: "small",
      },
    },
    MuiSelect: {
      defaultProps: {
        size: "small",
      },
    },
    MuiFormControl: {
      defaultProps: {
        size: "small",
      },
    },
    MuiToolbar: {
      styleOverrides: {
        regular: {
          minHeight: 56,
          "@media (min-width:900px)": {
            minHeight: 64,
          },
        },
      },
    },
  };
}

export function createCommonThemeOptions({
  palette,
  shapeRadius,
  scale = "app",
}: {
  palette: ThemeOptions["palette"];
  shapeRadius: number;
  scale?: "app" | "landing";
}): ThemeOptions {
  return {
    spacing: 8,
    shadows: COMMON_SHADOWS,
    mixins: createToolbarMixins(),
    palette,
    shape: { borderRadius: shapeRadius },
    typography: createCommonTypography(scale),
    components: createCommonComponents(),
  };
}
