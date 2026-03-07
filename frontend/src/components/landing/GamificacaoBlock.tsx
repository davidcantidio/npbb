import { useEffect, useState } from "react";

import type {
  GamificacaoBlockProps,
  GamificacaoState,
} from "../../services/landing_public";
import {
  getBlockedReasonText,
  getGamificacaoByPriority,
} from "./GamificacaoBlock.state";
import {
  GamificacaoActiveView,
  GamificacaoCompletedView,
  GamificacaoPresentingView,
} from "./GamificacaoBlock.views";

export default function GamificacaoBlock({
  gamificacoes,
  leadSubmitted,
  busy = false,
  blockedReason = null,
  resetVersion = 0,
  onComplete,
  onReset,
}: GamificacaoBlockProps) {
  const [state, setState] = useState<GamificacaoState>("presenting");
  const [error, setError] = useState<string | null>(null);
  const fallbackErrorMessage = "Nao foi possivel registrar a participacao. Tente novamente.";

  const gam = getGamificacaoByPriority(gamificacoes);
  const blockedReasonText = getBlockedReasonText({ leadSubmitted, blockedReason });

  useEffect(() => {
    setState("presenting");
    setError(null);
  }, [resetVersion]);

  if (!gam) return null;

  const handleParticipate = () => {
    if (!leadSubmitted || busy) return;
    setState("active");
    setError(null);
  };

  const handleComplete = async () => {
    if (busy) return;
    setError(null);
    try {
      await Promise.resolve(onComplete(gam.id));
      setState("completed");
    } catch (err) {
      if (err instanceof Error && err.message.trim()) {
        setError(err.message);
      } else {
        setError(fallbackErrorMessage);
      }
    }
  };

  const handleReset = () => {
    if (busy) return;
    setState("presenting");
    setError(null);
    onReset();
  };

  if (state === "completed") {
    return <GamificacaoCompletedView gam={gam} onReset={handleReset} disableReset={busy} />;
  }

  if (state === "active") {
    return <GamificacaoActiveView gam={gam} loading={busy} error={error} onComplete={handleComplete} />;
  }

  return (
    <GamificacaoPresentingView
      gam={gam}
      leadSubmitted={leadSubmitted}
      blockedReasonText={blockedReasonText}
      disabled={!leadSubmitted || busy}
      onParticipate={handleParticipate}
    />
  );
}
