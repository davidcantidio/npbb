import { useEffect, useMemo, useRef, useState } from "react";
import { Alert, CircularProgress, Container, Stack, Typography } from "@mui/material";
import { useLocation, useParams } from "react-router-dom";

import {
  completeGamificacao,
  getLandingByAtivacao,
  getLandingByEventoAtivacao,
  getLandingByEvento,
  trackLandingAnalytics,
  type LandingPageData,
  type LandingSubmitResponse,
  submitLandingForm,
} from "../services/landing_public";
import { getLandingSessionId, selectLandingCtaVariant } from "../services/landing_experiments";
import { ApiError, toApiErrorMessage } from "../services/http";
import LandingPageView from "../components/landing/LandingPageView";

type FormState = Record<string, string>;

export default function EventLandingPage() {
  const { eventId, ativacaoId, evento_id, ativacao_id } = useParams();
  const location = useLocation();
  const resolvedEventId = evento_id ? Number(evento_id) : eventId ? Number(eventId) : null;
  const resolvedAtivacaoId = ativacao_id ? Number(ativacao_id) : ativacaoId ? Number(ativacaoId) : null;
  const landingToken = useMemo(() => {
    const token = new URLSearchParams(location.search).get("token");
    const normalizedToken = token?.trim();
    return normalizedToken ? normalizedToken : null;
  }, [location.search]);

  const [data, setData] = useState<LandingPageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>({});
  const [consentimento, setConsentimento] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [submitted, setSubmitted] = useState<LandingSubmitResponse | null>(null);
  const [leadSubmitted, setLeadSubmitted] = useState(false);
  const [ativacaoLeadId, setAtivacaoLeadId] = useState<number | null>(null);
  const [gamificacaoBusy, setGamificacaoBusy] = useState(false);
  const [gamificacaoBlockedReason, setGamificacaoBlockedReason] = useState<string | null>(null);
  const [gamificacaoResetVersion, setGamificacaoResetVersion] = useState(0);
  const [lastSubmittedEmail, setLastSubmittedEmail] = useState<string | null>(null);
  const formStartTracked = useRef(false);
  const ctaExposureTracked = useRef(false);

  const sessionId = useMemo(() => getLandingSessionId(), []);
  const selectedVariant = useMemo(() => {
    if (!data) return null;
    return selectLandingCtaVariant(data, sessionId);
  }, [data, sessionId]);

  const effectiveData = useMemo<LandingPageData | null>(() => {
    if (!data) return null;
    if (!selectedVariant) return data;
    return {
      ...data,
      template: {
        ...data.template,
        cta_text: selectedVariant.text,
      },
    };
  }, [data, selectedVariant]);

  useEffect(() => {
    let active = true;
    setFormState({});
    setConsentimento(false);
    setSubmitError(null);
    setSaving(false);
    setSubmitted(null);
    setLeadSubmitted(false);
    setAtivacaoLeadId(null);
    setGamificacaoBusy(false);
    setGamificacaoBlockedReason(null);
    setGamificacaoResetVersion((prev) => prev + 1);
    setLastSubmittedEmail(null);
    formStartTracked.current = false;
    ctaExposureTracked.current = false;
    setLoading(true);
    setError(null);

    const load = async () => {
      try {
        if (
          resolvedEventId &&
          Number.isFinite(resolvedEventId) &&
          resolvedAtivacaoId &&
          Number.isFinite(resolvedAtivacaoId)
        ) {
          const response = await getLandingByEventoAtivacao(resolvedEventId, resolvedAtivacaoId, {
            token: landingToken,
          });
          if (!active) return;
          setData(response);
          return;
        }
        if (resolvedAtivacaoId && Number.isFinite(resolvedAtivacaoId)) {
          const response = await getLandingByAtivacao(resolvedAtivacaoId);
          if (!active) return;
          setData(response);
          return;
        }
        if (resolvedEventId && Number.isFinite(resolvedEventId)) {
          const response = await getLandingByEvento(resolvedEventId);
          if (!active) return;
          setData(response);
          return;
        }
        setError("Landing invalida.");
      } catch (err) {
        if (!active) return;
        if (err instanceof ApiError && err.status === 404) {
          setError("Evento ou ativacao nao encontrados.");
          return;
        }
        setError(toApiErrorMessage(err, "Nao foi possivel carregar esta landing."));
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();
    return () => {
      active = false;
    };
  }, [landingToken, resolvedAtivacaoId, resolvedEventId]);

  useEffect(() => {
    if (!effectiveData) return;
    trackLandingAnalytics({
      event_id: effectiveData.evento.id,
      ativacao_id: effectiveData.ativacao_id ?? undefined,
      categoria: effectiveData.template.categoria,
      tema: effectiveData.template.tema,
      event_name: "page_view",
      cta_variant_id: selectedVariant?.id ?? null,
      landing_session_id: sessionId,
    }).catch(() => {});
  }, [effectiveData, selectedVariant?.id, sessionId]);

  useEffect(() => {
    if (!effectiveData || ctaExposureTracked.current) return;
    ctaExposureTracked.current = true;
    trackLandingAnalytics({
      event_id: effectiveData.evento.id,
      ativacao_id: effectiveData.ativacao_id ?? undefined,
      categoria: effectiveData.template.categoria,
      tema: effectiveData.template.tema,
      event_name: "cta_exposure",
      cta_variant_id: selectedVariant?.id ?? null,
      landing_session_id: sessionId,
    }).catch(() => {});
  }, [effectiveData, selectedVariant?.id, sessionId]);

  const handleInputChange = (key: string, value: string) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
    setSubmitError(null);
    if (!formStartTracked.current && data) {
      formStartTracked.current = true;
      trackLandingAnalytics({
        event_id: data.evento.id,
        ativacao_id: data.ativacao_id ?? undefined,
        categoria: data.template.categoria,
        tema: data.template.tema,
        event_name: "form_start",
        cta_variant_id: selectedVariant?.id ?? null,
        landing_session_id: sessionId,
      }).catch(() => {});
    }
  };

  const handleSubmit = async () => {
    if (!data) return;

    const missing = data.formulario.campos.filter((field) => field.required && !(formState[field.key] || "").trim());
    if (missing.length > 0) {
      setSubmitError(`Preencha os campos obrigatorios: ${missing.map((field) => field.label).join(", ")}.`);
      return;
    }
    if (!consentimento) {
      setSubmitError("Voce precisa aceitar o tratamento de dados para continuar.");
      return;
    }

    const email = (formState.email || "").trim().toLowerCase();
    if (submitted && email && lastSubmittedEmail === email) {
      return;
    }

    trackLandingAnalytics({
      event_id: data.evento.id,
      ativacao_id: data.ativacao_id ?? undefined,
      categoria: data.template.categoria,
      tema: data.template.tema,
      event_name: "submit_attempt",
      cta_variant_id: selectedVariant?.id ?? null,
      landing_session_id: sessionId,
    }).catch(() => {});

    setSaving(true);
    try {
      const response = await submitLandingForm(data.formulario.submit_url, {
        nome: formState.nome || "",
        sobrenome: formState.sobrenome,
        email: formState.email || "",
        cpf: formState.cpf,
        telefone: formState.telefone,
        data_nascimento: formState.data_nascimento,
        estado: formState.estado,
        endereco: formState.endereco,
        interesses: formState.interesses,
        genero: formState.genero,
        area_de_atuacao: formState.area_de_atuacao,
        cta_variant_id: selectedVariant?.id,
        landing_session_id: sessionId,
        consentimento_lgpd: consentimento,
      });
      const nextAtivacaoLeadId = response.ativacao_lead_id ?? null;
      const hasGamificacao = data.gamificacoes.length > 0;
      setSubmitted(response);
      setLeadSubmitted(Boolean(nextAtivacaoLeadId));
      setAtivacaoLeadId(nextAtivacaoLeadId);
      setGamificacaoBlockedReason(
        !nextAtivacaoLeadId && hasGamificacao
          ? "Seu cadastro foi concluido, mas a gamificacao esta indisponivel para este envio. Clique em \"Cadastrar outro email\" e tente novamente."
          : null,
      );
      setLastSubmittedEmail(email);
      setSubmitError(null);
      trackLandingAnalytics({
        event_id: data.evento.id,
        ativacao_id: data.ativacao_id ?? undefined,
        categoria: data.template.categoria,
        tema: data.template.tema,
        event_name: "submit_success",
        cta_variant_id: selectedVariant?.id ?? null,
        landing_session_id: sessionId,
      }).catch(() => {});
    } catch (err) {
      setSubmitError(toApiErrorMessage(err, "Nao foi possivel enviar seus dados. Tente novamente."));
    } finally {
      setSaving(false);
    }
  };

  const handleGamificacaoComplete = async (gamificacaoId: number) => {
    if (!ativacaoLeadId) {
      throw new Error("Nao foi possivel identificar seu cadastro para concluir a gamificacao.");
    }
    setGamificacaoBusy(true);
    try {
      await completeGamificacao(ativacaoLeadId, {
        gamificacao_id: gamificacaoId,
        gamificacao_completed: true,
      });
    } catch (err) {
      throw new Error(toApiErrorMessage(err, "Nao foi possivel registrar sua participacao na gamificacao."));
    } finally {
      setGamificacaoBusy(false);
    }
  };

  const handleReset = () => {
    if (gamificacaoBusy) return;
    setSubmitted(null);
    setSubmitError(null);
    setConsentimento(false);
    setFormState({});
    setLeadSubmitted(false);
    setAtivacaoLeadId(null);
    setGamificacaoBlockedReason(null);
    setGamificacaoResetVersion((prev) => prev + 1);
    setLastSubmittedEmail(null);
    formStartTracked.current = false;
  };

  return (
    <>
      {loading ? (
        <Container maxWidth="sm" sx={{ py: 18 }}>
          <Stack spacing={2} alignItems="center">
            <CircularProgress />
            <Typography variant="body1" color="text.secondary">
              Preparando sua landing...
            </Typography>
          </Stack>
        </Container>
      ) : error || !effectiveData ? (
        <Container maxWidth="sm" sx={{ py: 12 }}>
          <Alert severity="error">{error || "Landing nao encontrada."}</Alert>
        </Container>
      ) : (
        <LandingPageView
          data={effectiveData}
          mode="public"
          formState={formState}
          consentimento={consentimento}
          submitError={submitError}
          saving={saving}
          submitted={submitted}
          onInputChange={handleInputChange}
          onConsentimentoChange={setConsentimento}
          onSubmit={handleSubmit}
          onReset={handleReset}
          gamificacao={{
            leadSubmitted,
            busy: gamificacaoBusy,
            blockedReason: gamificacaoBlockedReason,
            resetVersion: gamificacaoResetVersion,
            onComplete: handleGamificacaoComplete,
            onReset: handleReset,
          }}
        />
      )}
    </>
  );
}
