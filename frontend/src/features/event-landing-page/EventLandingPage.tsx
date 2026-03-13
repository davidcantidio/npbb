import { useMemo } from "react";
import { Alert, CircularProgress, Container, Stack, Typography } from "@mui/material";
import { useLocation, useParams } from "react-router-dom";

import LandingPageView from "../../components/landing/LandingPageView";
import { useEventLandingPageData } from "./hooks";
import { REGISTER_ANOTHER_CPF_MESSAGE } from "./constants";

export default function EventLandingPage() {
  const { eventId, ativacaoId, evento_id, ativacao_id } = useParams();
  const location = useLocation();

  const resolvedEventId = useMemo(
    () => (evento_id ? Number(evento_id) : eventId ? Number(eventId) : null),
    [evento_id, eventId],
  );
  const resolvedAtivacaoId = useMemo(
    () => (ativacao_id ? Number(ativacao_id) : ativacaoId ? Number(ativacaoId) : null),
    [ativacao_id, ativacaoId],
  );
  const landingToken = useMemo(() => {
    const token = new URLSearchParams(location.search).get("token");
    const normalizedToken = token?.trim();
    return normalizedToken ? normalizedToken : null;
  }, [location.search]);

  const data = useEventLandingPageData({
    resolvedEventId,
    resolvedAtivacaoId,
    landingToken,
  });

  return (
    <>
      {data.loading ? (
        <Container maxWidth="sm" sx={{ py: 18 }}>
          <Stack spacing={2} alignItems="center">
            <CircularProgress />
            <Typography variant="body1" color="text.secondary">
              Preparando sua landing...
            </Typography>
          </Stack>
        </Container>
      ) : data.error || !data.effectiveData ? (
        <Container maxWidth="sm" sx={{ py: 12 }}>
          <Alert severity="error">{data.error || "Landing nao encontrada."}</Alert>
        </Container>
      ) : (
        <LandingPageView
          data={data.effectiveData}
          mode="public"
          cpfFirstEnabled={data.cpfFirstEnabled}
          cpfFirstUnlocked={data.cpfFirstUnlocked}
          showRegistrarOutroCpfPrompt={data.showRegistrarOutroCpfPrompt}
          registrarOutroCpfMessage={REGISTER_ANOTHER_CPF_MESSAGE}
          formState={data.formState}
          consentimento={data.consentimento}
          submitError={data.submitError}
          saving={data.saving}
          submitted={data.submitted}
          onInputChange={data.handleInputChange}
          onCpfFirstContinue={data.handleCpfFirstContinue}
          onRegistrarOutroCpf={data.handleRegistrarOutroCpf}
          onConsentimentoChange={data.setConsentimento}
          onSubmit={data.handleSubmit}
          onReset={data.handleReset}
          gamificacao={{
            leadSubmitted: data.leadSubmitted,
            busy: data.gamificacaoBusy,
            blockedReason: data.gamificacaoBlockedReason,
            resetVersion: data.gamificacaoResetVersion,
            onComplete: data.handleGamificacaoComplete,
            onReset: data.handleReset,
          }}
        />
      )}
    </>
  );
}
