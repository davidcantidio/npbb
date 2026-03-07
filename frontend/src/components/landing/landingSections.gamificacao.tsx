import { Container } from "@mui/material";

import GamificacaoBlock from "./GamificacaoBlock";
import type { LandingGamificacaoSectionProps } from "./landingSections.types";

export function LandingGamificacaoSection({ gamificacoes, isPreview, gamificacao }: LandingGamificacaoSectionProps) {
  if (!gamificacoes.length) return null;

  const effectiveLeadSubmitted = isPreview ? false : (gamificacao?.leadSubmitted ?? false);
  const effectiveBusy = isPreview ? false : (gamificacao?.busy ?? false);
  const effectiveBlockedReason = isPreview ? null : (gamificacao?.blockedReason ?? null);
  const effectiveResetVersion = isPreview ? 0 : (gamificacao?.resetVersion ?? 0);
  const onComplete = isPreview ? (() => undefined) : (gamificacao?.onComplete ?? (() => undefined));
  const onReset = isPreview ? (() => undefined) : (gamificacao?.onReset ?? (() => undefined));

  return (
    <Container maxWidth="lg" sx={{ pb: { xs: 4, md: 6 } }}>
      <GamificacaoBlock
        gamificacoes={gamificacoes}
        leadSubmitted={effectiveLeadSubmitted}
        busy={effectiveBusy}
        blockedReason={effectiveBlockedReason}
        resetVersion={effectiveResetVersion}
        onComplete={onComplete}
        onReset={onReset}
      />
    </Container>
  );
}
