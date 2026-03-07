import { Box, createTheme } from "@mui/material";
import { alpha } from "@mui/material/styles";

import type { LandingPageData } from "../../services/landing_public";

export type LayoutVisualSpec = {
  heroBackground: string;
  heroTextColor: string;
  heroMinHeight: { xs: number | string; md: number | string };
  heroGridColumns: { xs: string; md: string };
  heroTextCardBackground: string;
  heroTextCardBorder: string;
  contentGridColumns: { xs: string; md: string };
  imageMinHeight: { xs: number; md: number };
  buttonVariant: "contained" | "outlined";
  buttonColor: "primary" | "secondary";
  buttonStyles?: Record<string, unknown>;
};

export function isDarkColor(value?: string | null) {
  const token = String(value || "").trim().toUpperCase();
  return ["#07111F", "#140F2E", "#1E293B", "#0F172A"].includes(token);
}

export function buildLandingTheme(data: LandingPageData) {
  const primary = data.template.color_primary || "#3333BD";
  const secondary = data.template.color_secondary || "#FCFC30";
  const background = data.template.color_background || "#F7F8FF";
  const text = data.template.color_text || "#111827";
  const dark = isDarkColor(background) || isDarkColor(primary);

  return createTheme({
    palette: {
      mode: dark ? "dark" : "light",
      primary: { main: primary },
      secondary: { main: secondary },
      background: {
        default: background,
        paper: dark ? alpha("#FFFFFF", 0.08) : "#FFFFFF",
      },
      text: {
        primary: text,
        secondary: dark ? alpha("#FFFFFF", 0.82) : alpha(text, 0.76),
      },
    },
    shape: { borderRadius: 20 },
    typography: {
      fontFamily: '"Roboto Flex Variable", "Roboto", "Inter", system-ui, sans-serif',
      h1: { fontSize: "3rem", fontWeight: 800, lineHeight: 1.05 },
      h2: { fontSize: "2rem", fontWeight: 800, lineHeight: 1.1 },
      h5: { fontWeight: 800 },
      button: { fontWeight: 800, textTransform: "none" },
    },
  });
}

export function getLayoutVisualSpec(data: LandingPageData): LayoutVisualSpec {
  const { hero_layout: heroLayout, color_primary: primary, color_secondary: secondary, color_text: text } = data.template;
  const defaultTextColor = isDarkColor(primary) || isDarkColor(data.template.color_background) ? "#F8FAFC" : text;

  if (heroLayout === "editorial") {
    return {
      heroBackground: `linear-gradient(180deg, #FFFFFF 0%, ${alpha(primary, 0.08)} 55%, ${alpha(secondary, 0.16)} 100%)`,
      heroTextColor: "#111827",
      heroMinHeight: { xs: "100svh", md: "auto" },
      heroGridColumns: { xs: "1fr", md: "1.08fr 0.92fr" },
      heroTextCardBackground: alpha("#FFFFFF", 0.78),
      heroTextCardBorder: alpha(primary, 0.18),
      contentGridColumns: { xs: "1fr", md: "1.05fr 0.95fr" },
      imageMinHeight: { xs: 280, md: 520 },
      buttonVariant: "outlined",
      buttonColor: "primary",
      buttonStyles: {
        borderWidth: 2,
        "&:hover": { borderWidth: 2 },
      },
    };
  }

  if (heroLayout === "dark-overlay") {
    return {
      heroBackground: `linear-gradient(135deg, ${alpha("#07111F", 0.98)} 0%, ${alpha(primary, 0.6)} 55%, ${alpha(
        secondary,
        0.22,
      )} 100%)`,
      heroTextColor: "#F8FAFC",
      heroMinHeight: { xs: "100svh", md: "auto" },
      heroGridColumns: { xs: "1fr", md: "1.1fr 0.9fr" },
      heroTextCardBackground: alpha("#07111F", 0.46),
      heroTextCardBorder: alpha("#FFFFFF", 0.14),
      contentGridColumns: { xs: "1fr", md: "1fr 0.95fr" },
      imageMinHeight: { xs: 300, md: 500 },
      buttonVariant: "contained",
      buttonColor: "secondary",
      buttonStyles: {
        background: `linear-gradient(135deg, ${secondary} 0%, ${alpha("#FFFFFF", 0.88)} 180%)`,
        color: "#07111F",
      },
    };
  }

  if (heroLayout === "full-bleed") {
    return {
      heroBackground: `linear-gradient(180deg, ${alpha(primary, 0.12)} 0%, ${alpha(secondary, 0.08)} 45%, ${alpha(
        primary,
        0.18,
      )} 100%)`,
      heroTextColor: text || "#1F2937",
      heroMinHeight: { xs: "100svh", md: "auto" },
      heroGridColumns: { xs: "1fr", md: "1fr 1fr" },
      heroTextCardBackground: alpha("#FFFFFF", 0.92),
      heroTextCardBorder: alpha(primary, 0.2),
      contentGridColumns: { xs: "1fr", md: "0.95fr 1.05fr" },
      imageMinHeight: { xs: 320, md: 540 },
      buttonVariant: "contained",
      buttonColor: "secondary",
      buttonStyles: {
        background: `linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)`,
        color: "#FFFFFF",
      },
    };
  }

  return {
    heroBackground: `linear-gradient(135deg, ${primary} 0%, ${alpha(primary, 0.92)} 52%, ${alpha(secondary, 0.58)} 100%)`,
    heroTextColor: defaultTextColor,
    heroMinHeight: { xs: "100svh", md: "auto" },
    heroGridColumns: { xs: "1fr", md: "1.15fr 0.85fr" },
    heroTextCardBackground: alpha("#FFFFFF", 0.1),
    heroTextCardBorder: alpha("#FFFFFF", 0.18),
    contentGridColumns: { xs: "1fr", md: "0.98fr 1.02fr" },
    imageMinHeight: { xs: 260, md: 460 },
    buttonVariant: data.template.cta_variant === "outlined" ? "outlined" : "contained",
    buttonColor: data.template.cta_variant === "outlined" ? "primary" : "secondary",
  };
}

export function getCardPaperSx(primaryColor: string, withShadow = false) {
  return {
    p: { xs: 3, md: 4 },
    borderRadius: 3,
    border: `1px solid ${alpha(primaryColor, 0.12)}`,
    ...(withShadow ? { boxShadow: `0 24px 60px ${alpha(primaryColor, 0.12)}` } : {}),
  };
}

export function renderGraphicOverlay(data: LandingPageData) {
  const primary = data.template.color_primary;
  const secondary = data.template.color_secondary;

  if (data.template.graphics_style === "organic") {
    return (
      <>
        <Box
          sx={{
            position: "absolute",
            inset: "auto auto -80px -40px",
            width: 220,
            height: 220,
            borderRadius: "46% 54% 62% 38% / 43% 36% 64% 57%",
            bgcolor: alpha(secondary, 0.24),
            filter: "blur(6px)",
          }}
        />
        <Box
          sx={{
            position: "absolute",
            inset: "-48px -24px auto auto",
            width: 180,
            height: 180,
            borderRadius: "61% 39% 42% 58% / 47% 59% 41% 53%",
            bgcolor: alpha(primary, 0.18),
          }}
        />
      </>
    );
  }

  if (data.template.graphics_style === "grid") {
    return (
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(${alpha("#FFFFFF", 0.08)} 1px, transparent 1px), linear-gradient(90deg, ${alpha(
            "#FFFFFF",
            0.08,
          )} 1px, transparent 1px)`,
          backgroundSize: "32px 32px",
          maskImage: "linear-gradient(180deg, rgba(0,0,0,0.9), transparent 75%)",
          pointerEvents: "none",
        }}
      />
    );
  }

  if (data.template.graphics_style === "dynamic") {
    return (
      <>
        <Box
          sx={{
            position: "absolute",
            top: -20,
            right: 40,
            width: 180,
            height: 180,
            transform: "rotate(18deg)",
            borderRadius: 8,
            bgcolor: alpha(secondary, 0.18),
          }}
        />
        <Box
          sx={{
            position: "absolute",
            bottom: -36,
            left: 32,
            width: 220,
            height: 72,
            transform: "rotate(-12deg)",
            borderRadius: 999,
            bgcolor: alpha(primary, 0.16),
          }}
        />
      </>
    );
  }

  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: -30,
          right: -10,
          width: 140,
          height: 140,
          borderRadius: 6,
          border: `1px solid ${alpha("#FFFFFF", 0.14)}`,
          transform: "rotate(18deg)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: -20,
          left: 40,
          width: 160,
          height: 160,
          borderRadius: "50%",
          bgcolor: alpha(data.template.color_secondary, 0.12),
        }}
      />
    </>
  );
}
