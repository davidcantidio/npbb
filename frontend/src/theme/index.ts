import { createTheme } from "@mui/material/styles";
import { alpha } from "@mui/material/styles";

const cleanShadows = [
  "none",
  "0 1px 2px rgba(0,0,0,0.04)",
  "0 1px 3px rgba(0,0,0,0.06)",
  "0 2px 4px rgba(0,0,0,0.06)",
  "0 2px 6px rgba(0,0,0,0.07)",
  "0 3px 8px rgba(0,0,0,0.07)",
  "0 3px 10px rgba(0,0,0,0.08)",
  "0 4px 12px rgba(0,0,0,0.08)",
  "0 5px 14px rgba(0,0,0,0.09)",
  "0 5px 16px rgba(0,0,0,0.09)",
  "0 6px 18px rgba(0,0,0,0.10)",
  "0 6px 20px rgba(0,0,0,0.10)",
  "0 7px 22px rgba(0,0,0,0.11)",
  "0 7px 24px rgba(0,0,0,0.11)",
  "0 8px 26px rgba(0,0,0,0.12)",
  "0 8px 28px rgba(0,0,0,0.12)",
  "0 9px 30px rgba(0,0,0,0.12)",
  "0 9px 32px rgba(0,0,0,0.13)",
  "0 10px 34px rgba(0,0,0,0.13)",
  "0 10px 36px rgba(0,0,0,0.13)",
  "0 11px 38px rgba(0,0,0,0.14)",
  "0 11px 40px rgba(0,0,0,0.14)",
  "0 12px 42px rgba(0,0,0,0.14)",
  "0 12px 44px rgba(0,0,0,0.15)",
  "0 13px 46px rgba(0,0,0,0.15)",
] as const;

export const appTheme = createTheme({
  shadows: [...cleanShadows],
  spacing: 8,
  palette: {
    mode: "light",
    primary: {
      main: "#6750A4",
    },
    secondary: {
      main: "#625B71",
    },
    background: {
      default: "#f6f7fb",
      paper: "#ffffff",
    },
    divider: "rgba(0,0,0,0.08)",
  },
  shape: { borderRadius: 6 },
  typography: {
    fontFamily: '"Roboto Flex Variable", "Roboto", "Inter", system-ui, -apple-system, sans-serif',
    fontSize: 14,
    fontWeightRegular: 400,
    fontWeightMedium: 600,
    fontWeightBold: 700,
    h1: { fontSize: "1.75rem", fontWeight: 700, lineHeight: 1.2 },
    h2: { fontSize: "1.5rem", fontWeight: 700, lineHeight: 1.2 },
    h3: { fontSize: "1.25rem", fontWeight: 600, lineHeight: 1.3 },
    h4: { fontSize: "1.125rem", fontWeight: 600, lineHeight: 1.3 },
    h5: { fontSize: "1rem", fontWeight: 600, lineHeight: 1.4 },
    h6: { fontSize: "0.875rem", fontWeight: 600, lineHeight: 1.4 },
    body1: { fontSize: "0.875rem", lineHeight: 1.5 },
    body2: { fontSize: "0.8125rem", lineHeight: 1.5 },
    subtitle1: { fontSize: "0.875rem", lineHeight: 1.5 },
    subtitle2: { fontSize: "0.8125rem", lineHeight: 1.5 },
    caption: { fontSize: "0.75rem", lineHeight: 1.5 },
    button: { fontSize: "0.8125rem", lineHeight: 1.5 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableRipple: true },
      styleOverrides: {
        root: ({ theme }) => ({
          "&:focus-visible": {
            outline: "2px solid",
            outlineColor: theme.palette.primary.main,
            outlineOffset: 2,
          },
        }),
      },
    },
    MuiIconButton: {
      defaultProps: { disableRipple: true },
      styleOverrides: {
        root: ({ theme }) => ({
          "&:focus-visible": {
            outline: "2px solid",
            outlineColor: theme.palette.primary.main,
            outlineOffset: 2,
          },
        }),
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: ({ theme }) => ({
          "&:focus-visible": {
            outline: "2px solid",
            outlineColor: theme.palette.primary.main,
            outlineOffset: 2,
          },
        }),
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: ({ theme }) => ({
          boxShadow: "none",
          backgroundColor: alpha(theme.palette.background.default, 0.9),
          backdropFilter: "blur(8px)",
        }),
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: ({ theme }) => ({
          boxShadow: "none",
          backgroundColor: theme.palette.background.paper,
          border: "1px solid",
          borderColor: theme.palette.divider,
        }),
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: ({ theme }) => ({
          boxShadow: "none",
          backgroundColor: theme.palette.background.paper,
          border: "1px solid",
          borderColor: theme.palette.divider,
        }),
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: ({ theme }) => ({
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
          border: "1px solid",
          borderColor: theme.palette.divider,
        }),
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: "1px solid",
          borderColor: "divider",
        },
      },
    },
    MuiCardActionArea: { defaultProps: { disableRipple: true } },
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: "1px solid",
          borderColor: "divider",
        },
      },
    },
    MuiTextField: { defaultProps: { size: "small" } },
    MuiAutocomplete: { defaultProps: { size: "small" } },
    MuiSelect: { defaultProps: { size: "small" } },
    MuiFormControl: { defaultProps: { size: "small" } },
    MuiChip: { defaultProps: { size: "small" } },
  },
});
