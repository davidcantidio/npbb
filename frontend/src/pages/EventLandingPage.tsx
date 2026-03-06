import { useEffect, useState } from "react";
import { Alert, CircularProgress, Container, Stack, Typography } from "@mui/material";
import { useParams } from "react-router-dom";

import {
  getLandingByAtivacao,
  getLandingByEvento,
  type LandingPageData,
  type LandingSubmitResponse,
  submitLandingForm,
} from "../services/landing_public";
import { toApiErrorMessage } from "../services/http";
import LandingPageView from "../components/landing/LandingPageView";

type FormState = Record<string, string>;

export default function EventLandingPage() {
  const { eventId, ativacaoId } = useParams();
  const resolvedEventId = eventId ? Number(eventId) : null;
  const resolvedAtivacaoId = ativacaoId ? Number(ativacaoId) : null;

  const [data, setData] = useState<LandingPageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>({});
  const [consentimento, setConsentimento] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [submitted, setSubmitted] = useState<LandingSubmitResponse | null>(null);
  const [lastSubmittedEmail, setLastSubmittedEmail] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    const load = async () => {
      try {
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
        setError(toApiErrorMessage(err, "Nao foi possivel carregar esta landing."));
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();
    return () => {
      active = false;
    };
  }, [resolvedAtivacaoId, resolvedEventId]);

  const handleInputChange = (key: string, value: string) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
    setSubmitError(null);
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
        consentimento_lgpd: consentimento,
      });
      setSubmitted(response);
      setLastSubmittedEmail(email);
      setSubmitError(null);
    } catch (err) {
      setSubmitError(toApiErrorMessage(err, "Nao foi possivel enviar seus dados. Tente novamente."));
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setSubmitted(null);
    setSubmitError(null);
    setConsentimento(false);
    setFormState({});
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
      ) : error || !data ? (
        <Container maxWidth="sm" sx={{ py: 12 }}>
          <Alert severity="error">{error || "Landing nao encontrada."}</Alert>
        </Container>
      ) : (
        <LandingPageView
          data={data}
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
        />
      )}
    </>
  );
}
