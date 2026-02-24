import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useLocation, useNavigate, useParams } from "react-router-dom";

import EventWizardStepper from "../../components/eventos/EventWizardStepper";
import { getEvento, Tag, Territorio } from "../../services/eventos";
import { useAuth } from "../../store/auth";
import { EventWizardActions } from "./components/EventWizardActions";
import { EventWizardStepAgency } from "./components/EventWizardStepAgency";
import { EventWizardStepClassification } from "./components/EventWizardStepClassification";
import { EventWizardStepEventInfo } from "./components/EventWizardStepEventInfo";
import { useEventWizardDomainData } from "./hooks/useEventWizardDomainData";
import {
  EVENT_SUBSTEPS,
  EventWizardFormState,
  normalizeWizardText,
  useEventWizardForm,
} from "./hooks/useEventWizardForm";
import { useEventWizardFocus } from "./hooks/useEventWizardFocus";
import { resolveSubmitAndContinue, useEventWizardSubmit } from "./hooks/useEventWizardSubmit";
import { useEventWizardState } from "./hooks/useEventWizardState";
import { shouldPreventEnterSubmit } from "./hooks/useEventWizardValidation";

/**
 * Container page for create/edit event wizard flow.
 */
export default function EventWizardPage() {
  const navigate = useNavigate();
  const params = useParams();
  const location = useLocation();
  const eventoId = Number(params.id);
  const isEdit = Number.isFinite(eventoId);

  const { token, user } = useAuth();
  const isAgencia = String(user?.tipo_usuario || "").toLowerCase() === "agencia";
  const canPickAgencia = !isAgencia;

  const {
    eventSubStep,
    setEventSubStep,
    submitAttempted,
    setSubmitAttempted,
    submitAndContinueRequested,
    setSubmitAndContinueRequested,
  } = useEventWizardState(0);

  const {
    form,
    setForm,
    selectedTipoId,
    errors,
    canSubmit,
    eventStepFields,
    applyEventoData,
    ensureAgencia,
    handleChange,
    handleEstadoChange,
    handleTipoChange,
  } = useEventWizardForm({ defaultAgenciaId: user?.agencia_id });

  const {
    agencias,
    diretorias,
    divisoesDemandantes,
    tipos,
    subtipos,
    tags,
    territorios,
    cidades,
    loadingDomains,
    loadingCidades,
    loadingSubtipos,
    domainError,
    setDomainError,
  } = useEventWizardDomainData({
    token,
    canPickAgencia,
    selectedTipoId,
    estado: form.estado,
    userAgenciaId: user?.agencia_id,
    onApplyUserAgencia: ensureAgencia,
  });

  const [loadingEvento, setLoadingEvento] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const formRef = useRef<HTMLFormElement | null>(null);
  const submitAndContinueRef = useRef(false);

  const {
    missingFieldsSet,
    missingFieldsForList,
    getFieldLabel,
    handlePendingFieldClick,
    getFieldSx,
    setFieldRef,
  } = useEventWizardFocus({
    locationSearch: location.search,
    eventSubStep,
    setEventSubStep,
    loadingEvento,
    loadingDomains,
  });

  const { submitEventWizard } = useEventWizardSubmit();

  useEffect(() => {
    if (!isEdit || !token) return;

    let cancelled = false;
    setLoadingEvento(true);
    setError(null);

    getEvento(token, eventoId)
      .then((data) => {
        if (cancelled) return;
        applyEventoData(data);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "Erro ao carregar evento";
        setError(message);
      })
      .finally(() => {
        if (cancelled) return;
        setLoadingEvento(false);
      });

    return () => {
      cancelled = true;
    };
  }, [applyEventoData, eventoId, isEdit, token]);

  useEffect(() => {
    if (!domainError) return;
    setError(domainError);
    setDomainError(null);
  }, [domainError, setDomainError]);

  const selectedDivisaoDemandante = useMemo(() => {
    const id = Number(form.divisao_demandante_id);
    return Number.isFinite(id) && id > 0
      ? divisoesDemandantes.find((item) => item.id === id) ?? null
      : null;
  }, [divisoesDemandantes, form.divisao_demandante_id]);

  const selectedDiretoria = useMemo(() => {
    const id = Number(form.diretoria_id);
    return Number.isFinite(id) && id > 0 ? diretorias.find((item) => item.id === id) ?? null : null;
  }, [diretorias, form.diretoria_id]);

  const selectedTipo = useMemo(() => {
    const id = Number(form.tipo_id);
    return Number.isFinite(id) && id > 0 ? tipos.find((item) => item.id === id) ?? null : null;
  }, [form.tipo_id, tipos]);

  const selectedSubtipo = useMemo(() => {
    const id = Number(form.subtipo_id);
    return Number.isFinite(id) && id > 0 ? subtipos.find((item) => item.id === id) ?? null : null;
  }, [form.subtipo_id, subtipos]);

  const tagsById = useMemo(() => new Map(tags.map((tag) => [String(tag.id), tag])), [tags]);
  const tagsByLowerName = useMemo(() => new Map(tags.map((tag) => [tag.nome.toLowerCase(), tag])), [tags]);
  const territoriosById = useMemo(
    () => new Map(territorios.map((territorio) => [String(territorio.id), territorio])),
    [territorios],
  );

  const selectedTagValues = useMemo(() => {
    const values: Array<Tag | string> = [];
    for (const id of form.tag_ids) {
      const tag = tagsById.get(id);
      if (tag) values.push(tag);
    }
    for (const name of form.tag_names) values.push(name);
    return values;
  }, [form.tag_ids, form.tag_names, tagsById]);

  const selectedTerritorios = useMemo(() => {
    return form.territorio_ids
      .map((id) => territoriosById.get(id))
      .filter(Boolean) as Territorio[];
  }, [form.territorio_ids, territoriosById]);

  const getFieldHelperText = useCallback(
    (field: keyof EventWizardFormState, base?: string) => {
      const fieldError = errors[field];
      const isMissing = missingFieldsSet.has(field);
      if (isMissing) {
        if (fieldError) return `${fieldError} - Pendente`;
        if (base) return `${base} - Pendente`;
        return "Pendente";
      }
      return fieldError ?? base;
    },
    [errors, missingFieldsSet],
  );

  const currentStepHasErrors = useMemo(() => {
    const keys = eventStepFields[eventSubStep] ?? [];
    return keys.some((key) => Boolean(errors[key]));
  }, [errors, eventStepFields, eventSubStep]);

  const goToFirstErrorStep = useCallback(() => {
    for (let index = 0; index < eventStepFields.length; index += 1) {
      const keys = eventStepFields[index] ?? [];
      if (keys.some((key) => Boolean(errors[key]))) {
        setEventSubStep(index);
        return;
      }
    }
  }, [errors, eventStepFields, setEventSubStep]);

  const handleBackStep = useCallback(() => {
    setSubmitAttempted(false);
    setEventSubStep((prev) => Math.max(prev - 1, 0));
  }, [setEventSubStep, setSubmitAttempted]);

  const handleNextStep = useCallback(() => {
    setSubmitAttempted(true);
    const keys = eventStepFields[eventSubStep] ?? [];
    if (keys.some((key) => Boolean(errors[key]))) return;
    setSubmitAttempted(false);
    setEventSubStep((prev) => Math.min(prev + 1, EVENT_SUBSTEPS.length - 1));
  }, [errors, eventStepFields, eventSubStep, setEventSubStep, setSubmitAttempted]);

  const onTagsChange = useCallback(
    (values: Array<Tag | string>) => {
      const ids: string[] = [];
      const names: string[] = [];
      const seenIds = new Set<string>();
      const seenNames = new Set<string>();

      for (const value of values) {
        if (typeof value === "string") {
          const normalizedName = normalizeWizardText(value);
          if (!normalizedName) continue;
          const existing = tagsByLowerName.get(normalizedName.toLowerCase());
          if (existing) {
            const id = String(existing.id);
            if (!seenIds.has(id)) {
              seenIds.add(id);
              ids.push(id);
            }
            continue;
          }

          const key = normalizedName.toLowerCase();
          if (!seenNames.has(key)) {
            seenNames.add(key);
            names.push(normalizedName);
          }
          continue;
        }

        const id = String(value.id);
        if (!seenIds.has(id)) {
          seenIds.add(id);
          ids.push(id);
        }
      }

      setForm((prev) => ({ ...prev, tag_ids: ids, tag_names: names }));
    },
    [setForm, tagsByLowerName],
  );

  const preventEnterSubmitOnClassification = useCallback(
    (event: React.KeyboardEvent<HTMLElement>) => {
      const target = event.target as HTMLElement | null;
      const prevent = shouldPreventEnterSubmit({
        isClassificationStep: eventSubStep === EVENT_SUBSTEPS.length - 1,
        key: event.key,
        targetTagName: target?.tagName,
      });
      if (!prevent) return;
      event.preventDefault();
      event.stopPropagation();
    },
    [eventSubStep],
  );

  const handleSubmit = useCallback(
    async (event: React.FormEvent) => {
      event.preventDefault();

      if (eventSubStep < EVENT_SUBSTEPS.length - 1) {
        handleNextStep();
        return;
      }

      if (!token) return;

      const shouldContinue = resolveSubmitAndContinue({
        clickedContinue: submitAndContinueRef.current,
        requestedContinue: submitAndContinueRequested,
      });

      submitAndContinueRef.current = false;
      setSubmitAndContinueRequested(false);
      setSubmitAttempted(true);
      setError(null);
      setSaveSuccess(null);

      if (!canSubmit) {
        goToFirstErrorStep();
        return;
      }

      setSubmitting(true);
      try {
        await submitEventWizard({
          token,
          isEdit,
          eventoId,
          canPickAgencia,
          form,
          shouldContinue,
          navigate,
          onSaveSuccess: setSaveSuccess,
        });
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : isEdit ? "Erro ao salvar alteracoes" : "Erro ao criar evento";
        setError(message);
      } finally {
        setSubmitting(false);
      }
    },
    [
      canPickAgencia,
      canSubmit,
      eventSubStep,
      form,
      goToFirstErrorStep,
      handleNextStep,
      isEdit,
      navigate,
      setSubmitAndContinueRequested,
      setSubmitAttempted,
      submitAndContinueRequested,
      submitEventWizard,
      token,
      eventoId,
    ],
  );

  return (
    <Box sx={{ width: "100%", maxWidth: 1080, mx: "auto" }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            {isEdit ? "Editar Evento" : "Novo Evento"}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {isEdit ? `Editando o evento #${eventoId}.` : "Preencha os dados do evento."}
          </Typography>
        </Box>
        <Button
          component={RouterLink}
          to={isEdit ? `/eventos/${eventoId}` : "/eventos"}
          variant="outlined"
          sx={{ textTransform: "none" }}
        >
          Voltar
        </Button>
      </Box>

      {submitAttempted && currentStepHasErrors ? (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          Revise os campos destacados para continuar.
        </Alert>
      ) : null}

      {error ? (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}

      {saveSuccess ? (
        <Alert severity="success" variant="filled" sx={{ mb: 2 }} onClose={() => setSaveSuccess(null)}>
          {saveSuccess}
        </Alert>
      ) : null}

      <Paper elevation={2} sx={{ p: 3, borderRadius: 2, width: "100%", maxWidth: 680, mx: "auto" }}>
        {isEdit && loadingEvento ? (
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando evento...
            </Typography>
          </Stack>
        ) : null}

        <Box component="form" ref={formRef} onSubmit={handleSubmit} noValidate>
          <Stack spacing={3}>
            <EventWizardStepper activeStep={0} />

            <Stepper activeStep={eventSubStep}>
              {EVENT_SUBSTEPS.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {missingFieldsForList.length ? (
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  borderRadius: 2,
                  borderColor: "rgba(255, 167, 38, 0.6)",
                  bgcolor: "rgba(255, 243, 224, 0.6)",
                }}
              >
                <Stack spacing={1}>
                  <Typography variant="subtitle1" fontWeight={700}>
                    Campos pendentes ({missingFieldsForList.length})
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={1}>
                    {missingFieldsForList.map((fieldId) => (
                      <Button
                        key={fieldId}
                        size="small"
                        variant="outlined"
                        onClick={() => handlePendingFieldClick(fieldId)}
                        sx={{ textTransform: "none", borderRadius: 999, fontWeight: 600 }}
                      >
                        {getFieldLabel(fieldId)}
                      </Button>
                    ))}
                  </Stack>
                </Stack>
              </Paper>
            ) : null}

            <EventWizardStepAgency
              visible={eventSubStep === 0}
              canPickAgencia={canPickAgencia}
              agencias={agencias}
              agenciaId={form.agencia_id}
              concorrencia={Boolean(form.concorrencia)}
              loadingDomains={loadingDomains}
              setFieldRef={setFieldRef}
              getFieldSx={getFieldSx}
              onAgenciaChange={(agenciaId) => setForm((prev) => ({ ...prev, agencia_id: agenciaId }))}
              onConcorrenciaChange={(checked) => setForm((prev) => ({ ...prev, concorrencia: checked }))}
              getFieldHelperText={getFieldHelperText}
            />

            <EventWizardStepEventInfo
              visible={eventSubStep === 1}
              form={form}
              errors={errors}
              cidades={cidades}
              loadingDomains={loadingDomains}
              loadingCidades={loadingCidades}
              setFieldRef={setFieldRef}
              getFieldSx={getFieldSx}
              getFieldHelperText={getFieldHelperText}
              onChange={handleChange}
              onEstadoChange={handleEstadoChange}
            />

            <EventWizardStepClassification
              visible={eventSubStep === 2}
              form={form}
              errors={errors}
              diretorias={diretorias}
              divisoesDemandantes={divisoesDemandantes}
              tipos={tipos}
              subtipos={subtipos}
              tags={tags}
              territorios={territorios}
              selectedDiretoria={selectedDiretoria}
              selectedDivisaoDemandante={selectedDivisaoDemandante}
              selectedTipo={selectedTipo}
              selectedSubtipo={selectedSubtipo}
              selectedTerritorios={selectedTerritorios}
              selectedTagValues={selectedTagValues}
              selectedTipoId={selectedTipoId}
              loadingDomains={loadingDomains}
              loadingSubtipos={loadingSubtipos}
              setFieldRef={setFieldRef}
              getFieldSx={getFieldSx}
              getFieldHelperText={getFieldHelperText}
              preventEnterSubmitOnClassification={preventEnterSubmitOnClassification}
              onDiretoriaChange={(diretoriaId) => setForm((prev) => ({ ...prev, diretoria_id: diretoriaId }))}
              onDivisaoDemandanteChange={(divisaoId) =>
                setForm((prev) => ({ ...prev, divisao_demandante_id: divisaoId }))
              }
              onTipoChange={handleTipoChange}
              onSubtipoChange={(subtipoId) => setForm((prev) => ({ ...prev, subtipo_id: subtipoId }))}
              onTerritoriosChange={(territorioIds) =>
                setForm((prev) => ({ ...prev, territorio_ids: territorioIds }))
              }
              onTagsChange={onTagsChange}
            />

            <EventWizardActions
              leftActions={
                <Button
                  component={RouterLink}
                  to={isEdit ? `/eventos/${eventoId}` : "/eventos"}
                  variant="outlined"
                  sx={{ textTransform: "none", fontWeight: 700 }}
                >
                  Cancelar
                </Button>
              }
              rightActions={
                <>
                  <Button
                    variant="outlined"
                    onClick={handleBackStep}
                    disabled={eventSubStep === 0 || submitting}
                    sx={{ textTransform: "none", fontWeight: 700 }}
                  >
                    Voltar
                  </Button>

                  {eventSubStep === 0 && canPickAgencia ? (
                    <Button
                      variant="text"
                      onClick={() => {
                        setSubmitAttempted(false);
                        setEventSubStep(1);
                      }}
                      disabled={submitting || loadingDomains || (isEdit && loadingEvento)}
                      sx={{ textTransform: "none", fontWeight: 700 }}
                    >
                      Pular
                    </Button>
                  ) : null}

                  {eventSubStep < EVENT_SUBSTEPS.length - 1 ? (
                    <Button
                      variant="contained"
                      onClick={handleNextStep}
                      disabled={submitting || loadingDomains || (isEdit && loadingEvento)}
                      sx={{ textTransform: "none", fontWeight: 800 }}
                    >
                      Proximo
                    </Button>
                  ) : (
                    <>
                      <Button
                        type="submit"
                        variant="outlined"
                        disabled={submitting || loadingDomains || (isEdit && loadingEvento)}
                        sx={{ textTransform: "none", fontWeight: 800 }}
                      >
                        {submitting ? "Salvando..." : isEdit ? "Salvar alteracoes" : "Salvar"}
                      </Button>
                      <Button
                        variant="contained"
                        disabled={submitting || loadingDomains || (isEdit && loadingEvento)}
                        onClick={() => {
                          submitAndContinueRef.current = true;
                          setSubmitAndContinueRequested(true);
                          formRef.current?.requestSubmit();
                        }}
                        sx={{ textTransform: "none", fontWeight: 800 }}
                      >
                        {isEdit ? "Salvar e continuar" : "Criar e continuar"}
                      </Button>
                    </>
                  )}
                </>
              }
            />
          </Stack>
        </Box>
      </Paper>
    </Box>
  );
}
