import { Box, createTheme } from "@mui/material";
import { alpha } from "@mui/material/styles";

import type { LandingPageData } from "../../services/landing_public";

export const TEMPLATE_CATEGORIES = [
  "corporativo",
  "esporte_convencional",
  "esporte_radical",
  "evento_cultural",
  "show_musical",
  "tecnologia",
  "generico",
] as const;

export type TemplateCategory = (typeof TEMPLATE_CATEGORIES)[number];
export type TemplateOverlayVariant = TemplateCategory;

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

const TEMPLATE_OVERLAY_VARIANTS: Record<TemplateCategory, TemplateOverlayVariant> = {
  corporativo: "corporativo",
  esporte_convencional: "esporte_convencional",
  esporte_radical: "esporte_radical",
  evento_cultural: "evento_cultural",
  show_musical: "show_musical",
  tecnologia: "tecnologia",
  generico: "generico",
};

function normalizeTemplateCategory(data: LandingPageData): string {
  return String(data.template.categoria || "")
    .trim()
    .toLowerCase();
}

function isKnownTemplateCategory(category: string): category is TemplateCategory {
  return (TEMPLATE_CATEGORIES as readonly string[]).includes(category);
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

function resolveOverlayVariantFromGraphicsStyle(graphicsStyle: string): TemplateOverlayVariant {
  if (graphicsStyle === "organic") {
    return "evento_cultural";
  }

  if (graphicsStyle === "grid") {
    return "tecnologia";
  }

  if (graphicsStyle === "dynamic") {
    return "esporte_radical";
  }

  if (graphicsStyle === "geometric") {
    return "esporte_convencional";
  }

  return "generico";
}

export function getTemplateOverlayVariant(data: LandingPageData): TemplateOverlayVariant {
  const category = normalizeTemplateCategory(data);

  if (isKnownTemplateCategory(category)) {
    return TEMPLATE_OVERLAY_VARIANTS[category];
  }

  return resolveOverlayVariantFromGraphicsStyle(data.template.graphics_style);
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

export function buildFormCardTheme(data: LandingPageData) {
  const primary = data.template.color_primary || "#3333BD";
  const secondary = data.template.color_secondary || "#FCFC30";
  const surfaceText = "#07111F";

  return createTheme({
    palette: {
      mode: "light",
      primary: {
        main: primary,
        contrastText: "#FFFFFF",
      },
      secondary: {
        main: secondary,
        contrastText: surfaceText,
      },
      background: {
        default: "#FFFFFF",
        paper: "#FFFFFF",
      },
      text: {
        primary: surfaceText,
        secondary: alpha(surfaceText, 0.76),
      },
    },
    shape: { borderRadius: 20 },
    typography: {
      fontFamily: '"Roboto Flex Variable", "Roboto", "Inter", system-ui, sans-serif',
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
        borderColor: "#3333BD",
        color: "#3333BD",
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
        color: "#07111F",
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

  if (category === "corporativo") {
    return {
      primary: "#1A237E",
      secondary: "#FCFC30",
      neutral: "#FFFFFF",
    };
  }

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

function renderCorporateOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(${alpha(palette.neutral, 0.82)} 1px, transparent 1px), linear-gradient(90deg, ${alpha(
            palette.neutral,
            0.82,
          )} 1px, transparent 1px)`,
          backgroundSize: "72px 72px",
          maskImage: "linear-gradient(180deg, rgba(0,0,0,0.9), transparent 82%)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: "8% 12% auto auto",
          width: 220,
          height: 220,
          borderRadius: 3,
          border: `1px solid ${alpha(palette.secondary, 0.48)}`,
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: "auto auto 12% 10%",
          width: 260,
          height: 96,
          borderTop: `1px solid ${alpha(palette.neutral, 0.72)}`,
          borderBottom: `1px solid ${alpha(palette.neutral, 0.48)}`,
        }}
      />
    </>
  );
}

function renderSportOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: -24,
          right: 48,
          width: 180,
          height: 180,
          transform: "rotate(18deg)",
          borderRadius: 6,
          bgcolor: alpha(palette.secondary, 0.88),
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: 40,
          left: -18,
          width: 168,
          height: 168,
          clipPath: "polygon(12% 12%, 88% 12%, 88% 88%, 12% 88%)",
          bgcolor: alpha(palette.neutral, 0.74),
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: -24,
          left: 96,
          width: 220,
          height: 72,
          transform: "rotate(-12deg)",
          borderRadius: 999,
          bgcolor: alpha(palette.primary, 0.78),
        }}
      />
    </>
  );
}

function renderRadicalOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: -48,
          right: 24,
          width: 240,
          height: 200,
          clipPath: "polygon(12% 0%, 100% 0%, 72% 100%, 0% 84%)",
          bgcolor: alpha(palette.secondary, 0.9),
          transform: "rotate(6deg)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: -40,
          left: -12,
          width: 280,
          height: 180,
          clipPath: "polygon(0% 30%, 58% 0%, 100% 52%, 36% 100%)",
          bgcolor: alpha(palette.primary, 0.86),
          transform: "rotate(-8deg)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          top: 96,
          right: 128,
          width: 10,
          height: 10,
          borderRadius: "50%",
          bgcolor: alpha(palette.neutral, 0.95),
          boxShadow: `0 0 18px ${alpha(palette.neutral, 0.95)}`,
        }}
      />
    </>
  );
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

function renderMusicalOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: 48,
          right: 120,
          width: 18,
          height: 18,
          borderRadius: "50%",
          bgcolor: alpha(palette.secondary, 0.92),
          boxShadow: `0 0 22px ${alpha(palette.secondary, 0.88)}`,
        }}
      />
      <Box
        sx={{
          position: "absolute",
          top: 112,
          right: 60,
          width: 10,
          height: 10,
          borderRadius: "50%",
          bgcolor: alpha(palette.neutral, 0.92),
          boxShadow: `0 0 18px ${alpha(palette.neutral, 0.85)}`,
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: 72,
          left: 48,
          width: 16,
          height: 16,
          borderRadius: "50%",
          bgcolor: alpha(palette.primary, 0.94),
          boxShadow: `0 0 24px ${alpha(palette.primary, 0.78)}`,
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: 120,
          left: 120,
          width: 8,
          height: 8,
          borderRadius: "50%",
          bgcolor: alpha(palette.secondary, 0.86),
          boxShadow: `0 0 14px ${alpha(palette.secondary, 0.78)}`,
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: "auto 8% 12% auto",
          width: 220,
          height: 220,
          background: `radial-gradient(circle, ${alpha(palette.primary, 0.34)} 0%, ${alpha(palette.primary, 0.08)} 45%, transparent 72%)`,
          filter: "blur(6px)",
        }}
      />
    </>
  );
}

function renderTechnologyOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          backgroundImage: `radial-gradient(circle, ${alpha(palette.secondary, 0.92)} 1.2px, transparent 1.3px)`,
          backgroundSize: "22px 22px",
          maskImage: "linear-gradient(180deg, rgba(0,0,0,0.95), transparent 84%)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          top: 48,
          right: 72,
          width: 190,
          height: 168,
          border: `1px solid ${alpha(palette.secondary, 0.78)}`,
          clipPath: "polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%)",
        }}
      />
      <Box
        sx={{
          position: "absolute",
          bottom: 56,
          left: 40,
          width: 140,
          height: 124,
          border: `1px solid ${alpha(palette.neutral, 0.7)}`,
          clipPath: "polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%)",
        }}
      />
    </>
  );
}

function renderGenericOverlay(palette: OverlayPalette) {
  return (
    <>
      <Box
        sx={{
          position: "absolute",
          inset: "auto 6% 8% auto",
          fontSize: { xs: 160, md: 240 },
          fontWeight: 900,
          letterSpacing: "-0.12em",
          lineHeight: 0.8,
          color: alpha(palette.neutral, 0.86),
          transform: "rotate(-12deg)",
          userSelect: "none",
        }}
      >
        BB
      </Box>
      <Box
        sx={{
          position: "absolute",
          top: 72,
          left: 48,
          width: 180,
          height: 180,
          borderRadius: "50%",
          border: `1px solid ${alpha(palette.secondary, 0.42)}`,
        }}
      />
    </>
  );
}

function renderOverlayByVariant(overlayVariant: TemplateOverlayVariant, palette: OverlayPalette) {
  if (overlayVariant === "corporativo") {
    return renderCorporateOverlay(palette);
  }

  if (overlayVariant === "esporte_convencional") {
    return renderSportOverlay(palette);
  }

  if (overlayVariant === "esporte_radical") {
    return renderRadicalOverlay(palette);
  }

  if (overlayVariant === "evento_cultural") {
    return renderOrganicOverlay(palette);
  }

  if (overlayVariant === "show_musical") {
    return renderMusicalOverlay(palette);
  }

  if (overlayVariant === "tecnologia") {
    return renderTechnologyOverlay(palette);
  }

  return renderGenericOverlay(palette);
}

export function renderGraphicOverlay(data: LandingPageData) {
  const overlayOpacity = getTemplateOverlayOpacity(data);
  const palette = resolveOverlayPalette(data);
  const overlayVariant = getTemplateOverlayVariant(data);
  const templateCategory = normalizeTemplateCategory(data) || "generico";

  return (
    <Box
      data-testid="landing-graphic-overlay"
      data-template-category={templateCategory}
      data-overlay-variant={overlayVariant}
      aria-hidden="true"
      sx={{
        position: "absolute",
        inset: 0,
        opacity: overlayOpacity,
        pointerEvents: "none",
      }}
    >
      {renderOverlayByVariant(overlayVariant, palette)}
    </Box>
  );
}
