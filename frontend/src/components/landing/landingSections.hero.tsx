import { Box, Chip, Paper, Stack, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";

import { formatDateRange } from "./landingHelpers";
import { isDarkColor } from "./landingStyle";
import type { HeroContextCardProps, HeroMediaCardProps } from "./landingSections.types";

export function LandingHeader({
  data,
  isPreview,
}: {
  data: HeroContextCardProps["data"];
  isPreview: boolean;
}) {
  return (
    <Stack direction="row" spacing={1.5} alignItems="center">
      <Box
        component="img"
        src="/logo-bb.svg"
        alt="Banco do Brasil"
        sx={{
          width: 48,
          height: 48,
          borderRadius: 2,
          boxShadow: `0 12px 24px ${alpha("#000000", 0.18)}`,
        }}
      />
      <Box>
        <Typography variant="subtitle2" sx={{ opacity: 0.82 }}>
          Banco do Brasil
        </Typography>
        {isPreview ? (
          <Typography variant="caption" sx={{ opacity: 0.78 }}>
            {data.template.tema}
          </Typography>
        ) : null}
      </Box>
    </Stack>
  );
}

export function HeroContextCard({ data, layout, isPreview }: HeroContextCardProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        position: "relative",
        overflow: "hidden",
        p: { xs: 3, md: 4 },
        borderRadius: 3,
        bgcolor: layout.heroTextCardBackground,
        border: `1px solid ${layout.heroTextCardBorder}`,
        backdropFilter: "blur(10px)",
        zIndex: 1,
      }}
    >
      <Stack spacing={2.5}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems="flex-start" flexWrap="wrap">
          {isPreview && data.template.categoria === "esporte_radical" ? (
            <Chip
              label="Radical"
              size="small"
              sx={{
                bgcolor: alpha(data.template.color_primary, 0.9),
                color: "#FFFFFF",
                fontWeight: 800,
              }}
            />
          ) : null}
          {isPreview ? (
            <Chip
              label={data.template.mood}
              sx={{
                bgcolor: alpha(data.template.color_secondary, 0.92),
                color: "#0F172A",
                fontWeight: 800,
                maxWidth: "100%",
              }}
            />
          ) : null}
          <Chip
            label={formatDateRange(data.evento.data_inicio, data.evento.data_fim)}
            variant="outlined"
            sx={{
              color: "inherit",
              borderColor: alpha(layout.heroTextColor, 0.28),
              bgcolor: alpha("#FFFFFF", isDarkColor(layout.heroTextColor) ? 0.04 : 0.4),
            }}
          />
          {isPreview ? (
            <Chip
              label={`Categoria: ${data.template.categoria}`}
              variant="outlined"
              sx={{ color: "inherit", borderColor: alpha(layout.heroTextColor, 0.24) }}
            />
          ) : null}
        </Stack>

        <Typography
          variant="h1"
          sx={{
            fontSize: {
              xs:
                data.template.hero_layout === "editorial" || data.template.hero_layout === "full-bleed"
                  ? "2.35rem"
                  : "2.5rem",
              md:
                data.template.hero_layout === "editorial" || data.template.hero_layout === "full-bleed"
                  ? "4rem"
                  : "3.7rem",
            },
            maxWidth: 760,
          }}
        >
          {data.evento.nome}
        </Typography>

        <Typography
          variant="h6"
          sx={{
            maxWidth: data.template.hero_layout === "editorial" ? 740 : 680,
            opacity: 0.92,
            fontSize: data.template.hero_layout === "editorial" ? { xs: "1rem", md: "1.15rem" } : undefined,
          }}
        >
          {data.evento.descricao_curta || data.evento.descricao || "Cadastre-se para participar desta experiencia BB."}
        </Typography>

        <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} flexWrap="wrap">
          <Chip
            label={`${data.evento.cidade} - ${data.evento.estado}`}
            variant="outlined"
            sx={{ color: "inherit", borderColor: alpha(layout.heroTextColor, 0.28) }}
          />
          {isPreview && data.ativacao_id ? (
            <Chip
              label={`Ativacao #${data.ativacao_id}`}
              variant="outlined"
              sx={{ color: "inherit", borderColor: alpha(layout.heroTextColor, 0.28) }}
            />
          ) : null}
        </Stack>
      </Stack>
    </Paper>
  );
}

export function HeroMediaCard({ data, layout, heroImageUrl, isPreview }: HeroMediaCardProps) {
  if (heroImageUrl) {
    return (
      <Box
        sx={{
          position: "relative",
          minHeight: layout.imageMinHeight,
          borderRadius: 3,
          overflow: "hidden",
          boxShadow: `0 24px 60px ${alpha("#000000", 0.18)}`,
          border: `1px solid ${alpha("#FFFFFF", 0.2)}`,
        }}
      >
        <Box
          component="img"
          data-testid="landing-hero-image"
          src={heroImageUrl}
          alt={data.marca.hero_alt}
          loading={isPreview ? "lazy" : "eager"}
          sx={{
            width: "100%",
            height: "100%",
            minHeight: layout.imageMinHeight,
            objectFit: "cover",
            display: "block",
          }}
        />
        <Box
          sx={{
            position: "absolute",
            inset: 0,
            background:
              data.template.hero_layout === "dark-overlay"
                ? `linear-gradient(180deg, ${alpha("#07111F", 0.18)} 0%, ${alpha("#07111F", 0.68)} 100%)`
                : `linear-gradient(180deg, transparent 25%, ${alpha("#000000", 0.26)} 100%)`,
          }}
        />
      </Box>
    );
  }

  return (
    <Box
      data-testid="landing-hero-fallback"
      sx={{
        minHeight: layout.imageMinHeight,
        borderRadius: 3,
        background: layout.heroBackground,
        border: `1px solid ${alpha("#FFFFFF", 0.2)}`,
      }}
    />
  );
}
