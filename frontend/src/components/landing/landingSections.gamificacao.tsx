import { Box, Paper } from "@mui/material";

import GamificacaoBlock from "./GamificacaoBlock";
import {
  FORM_ONLY_CONTENT_WIDTH_SX,
  getFormOnlySurfaceSx,
} from "./formOnlySurface";
import type { LandingGamificacaoSectionProps } from "./landingSections.types";

export function LandingGamificacaoSection({
  gamificacoes,
  layout,
  isPreview,
  gamificacao,
}: LandingGamificacaoSectionProps) {
  const resolvedGamificacoes = gamificacoes ?? [];
  if (!resolvedGamificacoes.length) return null;

  const effectiveLeadSubmitted = isPreview ? false : (gamificacao?.leadSubmitted ?? false);
  const effectiveBusy = isPreview ? false : (gamificacao?.busy ?? false);
  const effectiveBlockedReason = isPreview ? null : (gamificacao?.blockedReason ?? null);
  const effectiveResetVersion = isPreview ? 0 : (gamificacao?.resetVersion ?? 0);
  const onComplete = isPreview ? (() => undefined) : (gamificacao?.onComplete ?? (() => undefined));
  const onReset = isPreview ? (() => undefined) : (gamificacao?.onReset ?? (() => undefined));

  return (
    <Box
      data-testid="landing-gamificacao-section"
      sx={{
        ...FORM_ONLY_CONTENT_WIDTH_SX,
      }}
    >
      <Paper
        data-testid="landing-gamificacao-surface"
        elevation={0}
        sx={[
          { width: "100%" },
          getFormOnlySurfaceSx(layout, {
            preferTranslucentSolidBackground: true,
          }),
        ]}
      >
        <GamificacaoBlock
          gamificacoes={resolvedGamificacoes}
          leadSubmitted={effectiveLeadSubmitted}
          busy={effectiveBusy}
          blockedReason={effectiveBlockedReason}
          resetVersion={effectiveResetVersion}
          onComplete={onComplete}
          onReset={onReset}
        />
      </Paper>
    </Box>
  );
}
