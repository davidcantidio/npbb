import { Box, createTheme } from "@mui/material";
import { alpha } from "@mui/material/styles";

import type { LandingPageData } from "../../services/landing_public";

const TEMPLATE_BACKGROUND_GRADIENTS: Record<string, string> = {
  corporativo: "linear-gradient(135deg, #1A237E 0%, #3333BD 60%, #465EFF 100%)",
  esporte_convencional: "linear-gradient(160deg, #3333BD 0%, #1A237E 50%, #3333BD 100%)",
  esporte_radical: "linear-gradient(145deg, #3333BD 0%, #FF6E91 55%, #FCFC30 100%)",
  evento_cultural: "linear-gradient(150deg, #BDB6FF 0%, #E8E4FF 50%, #83FFEA 100%)",
  show_musical: "linear-gradient(160deg, #0D0D1A 0%, #2D1B4E 50%, #4A1942 100%)",
  tecnologia: "linear-gradient(135deg, #0D1B2E 0%, #0A2440 40%, #0B3340 100%)",
  generico: "linear-gradient(150deg, #3333BD 0%, #465EFF 100%)",
};

const TEMPLATE_OVERLAY_OPACITY: Record<string, number> = {
  corporativo: 0.1,
  esporte_convencional: 0.1,
  esporte_radical: 0.15,
  evento_cultural: 0.12,
  show_musical: 0.2,
  tecnologia: 0.15,
  generico: 0.05,
};

const TEMPLATE_FOOTER_TEXT_COLORS: Record<string, string> = {
  corporativo: "rgba(255, 255, 255, 0.75)",
  esporte_convencional: "rgba(255, 255, 255, 0.75)",
  esporte_radical: "rgba(255, 255, 255, 0.85)",
  evento_cultural: "rgba(51, 51, 189, 0.75)",
  show_musical: "rgba(255, 255, 255, 0.65)",
  tecnologia: "rgba(255, 255, 255, 0.70)",
  generico: "rgba(255, 255, 255, 0.75)",
};

function normalizeTemplateCategory(data: LandingPageData): string {
  return String(data.template.categoria || "")
    .trim()
    .toLowerCase();
}

export function getTemplateBackgroundGradient(data: LandingPageData): string {
  const category = normalizeTemplateCategory(data);

  return TEMPLATE_BACKGROUND_GRADIENTS[category] || TEMPLATE_BACKGROUND_GRADIENTS.generico;
}

export function getTemplateOverlayOpacity(data: LandingPageData): number {
  const category = normalizeTemplateCategory(data);
  return TEMPLATE_OVERLAY_OPACITY[category] ?? TEMPLATE_OVERLAY_OPACITY.generico;
}

export function getTemplateFooterTextColor(data: LandingPageData): string {
  const category = normalizeTemplateCategory(data);
  return TEMPLATE_FOOTER_TEXT_COLORS[category] ?? TEMPLATE_FOOTER_TEXT_COLORS.generico;
}

export type LayoutVisualSpec = {
  heroBackground: string;
  heroTextColor: string;
  heroMinHeight: { xs: number | string; md: number | string };
  heroGridColumns: { xs: string; md: string };
  heroTextCardBackground: string;
  heroTextCardBorder: string;
  formCardBackground: string;
  formCardBorder: string;
  formCardShadow: string;
  footerTextColor: string;
  contentGridColumns: { xs: string; md: string };
  imageMinHeight: { xs: number; md: number };
  buttonVariant: "contained" | "outlined";
  buttonColor: "primary" | "secondary";
  buttonStyles?: Record<string, unknown>;
};

type FormCardVisualSpec = Pick<LayoutVisualSpec, "formCardBackground" | "formCardBorder" | "formCardShadow">;

function resolveFormCardVisualSpec(data: LandingPageData): FormCardVisualSpec {
  const category = normalizeTemplateCategory(data);

  if (category === "corporativo") {
    return {
      formCardBackground: "#FFFFFF",
      formCardBorder: "2px solid rgba(252, 252, 48, 0.6)",
      formCardShadow: "0 20px 44px rgba(0,0,0,0.24)",
    };
  }

  if (category === "esporte_convencional") {
    return {
      formCardBackground: "rgba(255, 255, 255, 0.96)",
      formCardBorder: "none",
      formCardShadow: "0 8px 32px rgba(0,0,0,0.35)",
    };
  }

  if (category === "esporte_radical") {
    return {
      formCardBackground: "rgba(255, 255, 255, 0.95)",
      formCardBorder: "3px solid #FF6E91",
      formCardShadow: "0 20px 44px rgba(0,0,0,0.24)",
    };
  }

  if (category === "evento_cultural") {
    return {
      formCardBackground: "#FFFFFF",
      formCardBorder: "none",
      formCardShadow: "0 4px 24px rgba(115, 92, 198, 0.25)",
    };
  }

  if (category === "show_musical") {
    return {
      formCardBackground: "rgba(255, 255, 255, 0.97)",
      formCardBorder: "2px solid rgba(255, 110, 145, 0.5)",
      formCardShadow: "0 20px 44px rgba(0,0,0,0.24)",
    };
  }

  if (category === "tecnologia") {
    return {
      formCardBackground: "rgba(255, 255, 255, 0.97)",
      formCardBorder: "2px solid rgba(84, 220, 252, 0.5)",
      formCardShadow: "0 20px 44px rgba(0,0,0,0.24)",
    };
  }

  return {
    formCardBackground: "#FFFFFF",
    formCardBorder: "none",
    formCardShadow: "0px 2px 8px rgba(0,0,0,0.2)",
  };
}

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
  const formCardSpec = resolveFormCardVisualSpec(data);
  const footerTextColor = getTemplateFooterTextColor(data);

  if (heroLayout === "editorial") {
    return {
      heroBackground: `linear-gradient(180deg, #FFFFFF 0%, ${alpha(primary, 0.08)} 55%, ${alpha(secondary, 0.16)} 100%)`,
      heroTextColor: "#111827",
      heroMinHeight: { xs: "100svh", md: "auto" },
      heroGridColumns: { xs: "1fr", md: "1.08fr 0.92fr" },
      heroTextCardBackground: alpha("#FFFFFF", 0.78),
      heroTextCardBorder: alpha(primary, 0.18),
      ...formCardSpec,
      footerTextColor,
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
      ...formCardSpec,
      footerTextColor,
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
      ...formCardSpec,
      footerTextColor,
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
    ...formCardSpec,
    footerTextColor,
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

type OverlayPalette = {
  primary: string;
  secondary: string;
  neutral: string;
};

function resolveOverlayPalette(data: LandingPageData): OverlayPalette {
  const category = normalizeTemplateCategory(data);

  if (category === "evento_cultural") {
    return {
      primary: "#735CC6",
      secondary: data.template.color_secondary || "#BDB6FF",
      neutral: "#FFFFFF",
    };
  }

  if (category === "show_musical") {
    return {
      primary: "#FF6E91",
      secondary: "#FCFC30",
      neutral: "#FFFFFF",
    };
  }

  if (category === "tecnologia") {
    return {
      primary: data.template.color_primary || "#54DCFC",
      secondary: "#54DCFC",
      neutral: "#D5F5FF",
    };
  }

  return {
    primary: data.template.color_primary || "#3333BD",
    secondary: data.template.color_secondary || "#FCFC30",
    neutral: "#FFFFFF",
  };
}

function renderOrganicOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          inset: "auto auto -90px -48px",
          width: 240,
          height: 240,
          borderRadius: "46% 54% 62% 38% / 43% 36% 64% 57%",
          bgcolor: alpha(palette.secondary, 0.85),
          filter: "blur(8px)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: "-54px -26px auto auto",
          width: 190,
          height: 190,
          borderRadius: "61% 39% 42% 58% / 47% 59% 41% 53%",
          bgcolor: alpha(palette.primary, 0.72),
        }}
      />
    </>
  );
}

function renderGridOverlay(palette: OverlayPalette) {
  return (
    <Box
      sx={{
        position: "absolute",
        inset: 0,
        backgroundImage: `linear-gradient(${alpha(palette.neutral, 0.85)} 1px, transparent 1px), linear-gradient(90deg, ${alpha(
          palette.neutral,
          0.85,
        )} 1px, transparent 1px)`,
        backgroundSize: "32px 32px",
        maskImage: "linear-gradient(180deg, rgba(0,0,0,0.92), transparent 78%)",
      }}
    />
  );
}

function renderDynamicOverlay(palette: OverlayPalette) {
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
          bgcolor: alpha(palette.secondary, 0.85),
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
          bgcolor: alpha(palette.primary, 0.82),
        }}
      />
      <Box
        sx={{
          position: "absolute",
          top: 72,
          right: 120,
          width: 8,
          height: 8,
          borderRadius: "50%",
          bgcolor: alpha(palette.neutral, 0.95),
          boxShadow: `0 0 18px ${alpha(palette.neutral, 0.95)}`,
        }}
      />
    </>
  );
}

function renderGeometricOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: -32,
          right: -8,
          width: 150,
          height: 150,
          borderRadius: 6,
          border: `1px solid ${alpha(palette.neutral, 0.82)}`,
          transform: "rotate(18deg)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: -20,
          left: 40,
          width: 170,
          height: 170,
          borderRadius: "50%",
          bgcolor: alpha(palette.secondary, 0.78),
        }}
      />
    </>
  );
}

function renderOverlayByStyle(graphicsStyle: string, palette: OverlayPalette) {
  if (graphicsStyle === "organic") {
    return renderOrganicOverlay(palette);
  }

  if (graphicsStyle === "grid") {
    return renderGridOverlay(palette);
  }

  if (graphicsStyle === "dynamic") {
    return renderDynamicOverlay(palette);
  }

  return renderGeometricOverlay(palette);
}

export function renderGraphicOverlay(data: LandingPageData) {
  const overlayOpacity = getTemplateOverlayOpacity(data);
  const palette = resolveOverlayPalette(data);

  return (
    <Box
      data-testid="landing-graphic-overlay"
      aria-hidden="true"
      sx={{
        position: "absolute",
        inset: 0,
        opacity: overlayOpacity,
        pointerEvents: "none",
      }}
    >
      {renderOverlayByStyle(data.template.graphics_style, palette)}
    </Box>
  );
}
