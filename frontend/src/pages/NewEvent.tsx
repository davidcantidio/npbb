import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControlLabel,
  InputAdornment,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";

import { Agencia, listAgencias } from "../services/agencias";
import {
  createEvento,
  createTag,
  DivisaoDemandante,
  Diretoria,
  EventoCreate,
  getEvento,
  listDivisoesDemandantes,
  listDiretorias,
  listSubtiposEvento,
  listTags,
  listTerritorios,
  listTiposEvento,
  SubtipoEvento,
  Tag,
  Territorio,
  TipoEvento,
  updateEvento,
} from "../services/eventos";
import EventWizardStepper from "../components/eventos/EventWizardStepper";
import { useAuth } from "../store/auth";

type FormState = {
  agencia_id: string;
  concorrencia: boolean;
  nome: string;
  descricao: string;
  estado: string;
  cidade: string;
  data_inicio_prevista: string;
  data_fim_prevista: string;
  investimento: string;
  diretoria_id: string;
  divisao_demandante_id: string;
  tipo_id: string;
  subtipo_id: string;
  tag_ids: string[];
  tag_names: string[];
  territorio_ids: string[];
};

type FormErrors = Partial<Record<keyof FormState, string>>;

const UF_OPTIONS = [
  "AC",
  "AL",
  "AP",
  "AM",
  "BA",
  "CE",
  "DF",
  "ES",
  "GO",
  "MA",
  "MT",
  "MS",
  "MG",
  "PA",
  "PB",
  "PR",
  "PE",
  "PI",
  "RJ",
  "RN",
  "RS",
  "RO",
  "RR",
  "SC",
  "SP",
  "SE",
  "TO",
];

const EVENT_SUBSTEPS = ["Agência", "Informações do evento", "Classificação"];

type EstadosCidadesData = {
  estados: Array<{
    sigla: string;
    nome: string;
    cidades: string[];
  }>;
};

let cachedCidadesPorUf: Record<string, string[]> | null = null;

async function getCidadesPorUf(): Promise<Record<string, string[]>> {
  if (cachedCidadesPorUf) return cachedCidadesPorUf;
  const mod = await import("../data/estados-cidades.json");
  const data = ((mod as any).default ?? mod) as EstadosCidadesData;
  cachedCidadesPorUf = Object.fromEntries(
    data.estados.map((e) => [String(e.sigla).toUpperCase(), Array.isArray(e.cidades) ? e.cidades : []]),
  );
  return cachedCidadesPorUf;
}

function normalizeText(value: string) {
  return value.trim();
}

function parseId(value: string) {
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : null;
}

export default function NewEvent() {
  const navigate = useNavigate();
  const params = useParams();
  const eventoId = Number(params.id);
  const isEdit = Number.isFinite(eventoId);
  const { token, user } = useAuth();
  const isAgencia = String(user?.tipo_usuario || "").toLowerCase() === "agencia";
  const canPickAgencia = !isAgencia;

  const [form, setForm] = useState<FormState>({
    agencia_id: user?.agencia_id ? String(user.agencia_id) : "",
    concorrencia: false,
    nome: "",
    descricao: "",
    estado: "",
    cidade: "",
    data_inicio_prevista: "",
    data_fim_prevista: "",
    investimento: "",
    diretoria_id: "",
    divisao_demandante_id: "",
    tipo_id: "",
    subtipo_id: "",
    tag_ids: [],
    tag_names: [],
    territorio_ids: [],
  });

  const [eventSubStep, setEventSubStep] = useState(0);

  const [agencias, setAgencias] = useState<Agencia[]>([]);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [divisoesDemandantes, setDivisoesDemandantes] = useState<DivisaoDemandante[]>([]);
  const [tipos, setTipos] = useState<TipoEvento[]>([]);
  const [subtipos, setSubtipos] = useState<SubtipoEvento[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [territorios, setTerritorios] = useState<Territorio[]>([]);
  const [cidades, setCidades] = useState<string[]>([]);

  const [loadingDomains, setLoadingDomains] = useState(false);
  const [loadingEvento, setLoadingEvento] = useState(false);
  const [loadingCidades, setLoadingCidades] = useState(false);
  const [loadingSubtipos, setLoadingSubtipos] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedTipoId = useMemo(() => parseId(form.tipo_id), [form.tipo_id]);

  useEffect(() => {
    if (!isEdit || !token) return;

    let cancelled = false;
    setLoadingEvento(true);
    setError(null);

    getEvento(token, eventoId)
      .then((data) => {
        if (cancelled) return;
        setForm({
          agencia_id: data.agencia_id ? String(data.agencia_id) : "",
          concorrencia: Boolean(data.concorrencia),
          nome: data.nome || "",
          descricao: data.descricao || "",
          estado: data.estado ? String(data.estado).toUpperCase() : "",
          cidade: data.cidade || "",
          data_inicio_prevista: data.data_inicio_prevista || "",
          data_fim_prevista: data.data_fim_prevista || "",
          investimento: data.investimento != null ? String(data.investimento) : "",
          diretoria_id: data.diretoria_id != null ? String(data.diretoria_id) : "",
          divisao_demandante_id:
            data.divisao_demandante_id != null ? String(data.divisao_demandante_id) : "",
          tipo_id: data.tipo_id ? String(data.tipo_id) : "",
          subtipo_id: data.subtipo_id != null ? String(data.subtipo_id) : "",
          tag_ids: Array.isArray(data.tag_ids) ? data.tag_ids.map((n) => String(n)) : [],
          tag_names: [],
          territorio_ids: Array.isArray(data.territorio_ids)
            ? data.territorio_ids.map((n) => String(n))
            : [],
        });
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || "Erro ao carregar evento");
      })
      .finally(() => {
        if (!cancelled) setLoadingEvento(false);
      });

    return () => {
      cancelled = true;
    };
  }, [eventoId, isEdit, token]);

  const selectedDivisaoDemandante = useMemo(() => {
    const id = parseId(form.divisao_demandante_id);
    return id ? divisoesDemandantes.find((d) => d.id === id) ?? null : null;
  }, [divisoesDemandantes, form.divisao_demandante_id]);

  const selectedDiretoria = useMemo(() => {
    const id = parseId(form.diretoria_id);
    return id ? diretorias.find((d) => d.id === id) ?? null : null;
  }, [diretorias, form.diretoria_id]);

  const selectedTipo = useMemo(() => {
    const id = parseId(form.tipo_id);
    return id ? tipos.find((t) => t.id === id) ?? null : null;
  }, [tipos, form.tipo_id]);

  const selectedSubtipo = useMemo(() => {
    const id = parseId(form.subtipo_id);
    return id ? subtipos.find((s) => s.id === id) ?? null : null;
  }, [subtipos, form.subtipo_id]);

  const tagsById = useMemo(() => new Map(tags.map((t) => [String(t.id), t])), [tags]);
  const tagsByLowerName = useMemo(
    () => new Map(tags.map((t) => [t.nome.toLowerCase(), t])),
    [tags],
  );
  const territoriosById = useMemo(
    () => new Map(territorios.map((t) => [String(t.id), t])),
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
    return form.territorio_ids.map((id) => territoriosById.get(id)).filter(Boolean) as Territorio[];
  }, [form.territorio_ids, territoriosById]);

  const errors: FormErrors = useMemo(() => {
    const next: FormErrors = {};

    const nome = normalizeText(form.nome);
    if (!nome) next.nome = "Informe o nome do evento";

    const descricao = normalizeText(form.descricao);
    if (descricao && descricao.length > 240) next.descricao = "Maximo 240 caracteres";

    const cidade = normalizeText(form.cidade);
    if (!cidade) next.cidade = "Informe a cidade";
    else if (cidade.length > 40) next.cidade = "Maximo 40 caracteres";

    const estado = normalizeText(form.estado).toUpperCase();
    if (!estado) next.estado = "Selecione a UF";
    else if (!UF_OPTIONS.includes(estado)) next.estado = "UF invalida";

    if (form.subtipo_id) {
      const subtipoId = parseId(form.subtipo_id);
      if (!subtipoId) next.subtipo_id = "Subtipo invalido";
      else if (!subtipos.some((s) => s.id === subtipoId)) next.subtipo_id = "Subtipo nao pertence ao tipo";
    }

    const inicioPrev = form.data_inicio_prevista || "";
    const fimPrev = form.data_fim_prevista || "";
    if (!inicioPrev) next.data_inicio_prevista = "Informe a data do evento";
    if (inicioPrev && fimPrev && fimPrev < inicioPrev) {
      next.data_fim_prevista = "Fim previsto deve ser maior/igual ao inicio previsto";
    }

    const investimento = normalizeText(form.investimento);
    if (investimento) {
      const numeric = Number(investimento.replace(",", "."));
      if (!Number.isFinite(numeric) || numeric < 0) next.investimento = "Informe um investimento valido";
    }

    if (form.divisao_demandante_id && !parseId(form.divisao_demandante_id)) {
      next.divisao_demandante_id = "Selecione uma divisao valida";
    }

    return next;
  }, [form, subtipos]);

  const canSubmit = useMemo(() => Object.keys(errors).length === 0, [errors]);

  const eventStepFields = useMemo(() => {
    const steps: Array<Array<keyof FormState>> = [
      [],
      [
        "nome",
        "descricao",
        "estado",
        "cidade",
        "data_inicio_prevista",
        "data_fim_prevista",
        "investimento",
      ],
      ["divisao_demandante_id", "subtipo_id"],
    ];

    return steps;
  }, []);

  const currentStepHasErrors = useMemo(() => {
    const keys = eventStepFields[eventSubStep] ?? [];
    return keys.some((key) => Boolean(errors[key]));
  }, [errors, eventStepFields, eventSubStep]);

  const goToFirstErrorStep = useCallback(() => {
    for (let i = 0; i < eventStepFields.length; i += 1) {
      const keys = eventStepFields[i] ?? [];
      if (keys.some((key) => Boolean(errors[key]))) {
        setEventSubStep(i);
        return;
      }
    }
  }, [errors, eventStepFields]);

  const handleBackStep = () => {
    setSubmitAttempted(false);
    setEventSubStep((prev) => Math.max(prev - 1, 0));
  };

  const handleNextStep = () => {
    setSubmitAttempted(true);
    const keys = eventStepFields[eventSubStep] ?? [];
    if (keys.some((key) => Boolean(errors[key]))) return;
    setSubmitAttempted(false);
    setEventSubStep((prev) => Math.min(prev + 1, EVENT_SUBSTEPS.length - 1));
  };

  const loadDomains = useCallback(async () => {
    if (!token) return;
    setLoadingDomains(true);
    setError(null);
    try {
      const [
        agenciasResult,
        diretoriasResult,
        divisoesResult,
        tiposResult,
        tagsResult,
        territoriosResult,
      ] = await Promise.all([
        canPickAgencia ? listAgencias({ limit: 200 }) : Promise.resolve([] as Agencia[]),
        listDiretorias(token),
        listDivisoesDemandantes(token),
        listTiposEvento(token),
        listTags(token),
        listTerritorios(token),
      ]);

      setAgencias(canPickAgencia ? agenciasResult : []);
      setDiretorias(diretoriasResult);
      setDivisoesDemandantes(divisoesResult);
      setTipos(tiposResult);
      setTags(tagsResult);
      setTerritorios(territoriosResult);

      if (user?.agencia_id) {
        setForm((prev) => (prev.agencia_id ? prev : { ...prev, agencia_id: String(user.agencia_id) }));
      }
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar dominios");
    } finally {
      setLoadingDomains(false);
    }
  }, [token, canPickAgencia, user?.agencia_id]);

  useEffect(() => {
    loadDomains();
  }, [loadDomains]);

  useEffect(() => {
    const uf = normalizeText(form.estado).toUpperCase();
    if (!uf) {
      setCidades([]);
      return;
    }

    let cancelled = false;
    setLoadingCidades(true);
    getCidadesPorUf()
      .then((map) => {
        if (cancelled) return;
        setCidades(map[uf] ?? []);
      })
      .catch(() => {
        if (cancelled) return;
        setCidades([]);
      })
      .finally(() => {
        if (cancelled) return;
        setLoadingCidades(false);
      });

    return () => {
      cancelled = true;
    };
  }, [form.estado]);

  const loadSubtipos = useCallback(async () => {
    if (!token) return;
    if (!selectedTipoId) {
      setSubtipos([]);
      return;
    }
    setLoadingSubtipos(true);
    try {
      const items = await listSubtiposEvento(token, { tipo_id: selectedTipoId });
      setSubtipos(items);
    } catch {
      setSubtipos([]);
    } finally {
      setLoadingSubtipos(false);
    }
  }, [token, selectedTipoId]);

  useEffect(() => {
    loadSubtipos();
  }, [loadSubtipos]);

  const handleChange = (field: keyof FormState) => (e: any) => {
    const value = e?.target?.value;
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleEstadoChange = (_: unknown, value: string | null) => {
    const next = String(value || "");
    setForm((prev) => ({
      ...prev,
      estado: next,
      cidade: prev.estado === next ? prev.cidade : "",
    }));
  };

  const handleTipoChange = (_: unknown, value: TipoEvento | null) => {
    setForm((prev) => ({
      ...prev,
      tipo_id: value ? String(value.id) : "",
      subtipo_id: "",
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (eventSubStep < EVENT_SUBSTEPS.length - 1) {
      handleNextStep();
      return;
    }
    if (!token) return;
    setSubmitAttempted(true);
    setError(null);
    if (!canSubmit) {
      goToFirstErrorStep();
      return;
    }

    setSubmitting(true);
    try {
      let tagIds = form.tag_ids.map((id) => Number(id)).filter((n) => Number.isFinite(n) && n > 0);
      if (form.tag_names.length) {
        const createdTags = await Promise.all(form.tag_names.map((name) => createTag(token, name)));
        const createdIds = createdTags.map((t) => t.id).filter((id) => Number.isFinite(id) && id > 0);
        tagIds = Array.from(new Set([...tagIds, ...createdIds]));
      }

      const descricao = normalizeText(form.descricao);
      const payload: EventoCreate = {
        nome: normalizeText(form.nome),
        investimento: normalizeText(form.investimento) || undefined,
        concorrencia: Boolean(form.concorrencia),
        cidade: normalizeText(form.cidade),
        estado: normalizeText(form.estado).toUpperCase(),
        divisao_demandante_id: parseId(form.divisao_demandante_id) || undefined,
        data_inicio_prevista: form.data_inicio_prevista,
        data_fim_prevista: form.data_fim_prevista || undefined,
        tag_ids: tagIds,
        territorio_ids: form.territorio_ids.map((id) => Number(id)).filter((n) => Number.isFinite(n) && n > 0),
      };

      if (descricao) payload.descricao = descricao;

      const tipoId = parseId(form.tipo_id);
      if (tipoId) payload.tipo_id = tipoId;

      const diretoriaId = parseId(form.diretoria_id);
      if (diretoriaId) payload.diretoria_id = diretoriaId;

      const subtipoId = parseId(form.subtipo_id);
      if (subtipoId) payload.subtipo_id = subtipoId;

      if (canPickAgencia) {
        const agenciaId = parseId(form.agencia_id);
        if (agenciaId) payload.agencia_id = agenciaId;
      }

      if (isEdit) {
        const updated = await updateEvento(token, eventoId, payload);
        navigate(`/eventos/${updated.id}/formulario-lead`, { replace: true });
      } else {
        const created = await createEvento(token, payload);
        navigate(`/eventos/${created.id}/formulario-lead`, { replace: true });
      }
    } catch (err: any) {
      setError(err?.message || (isEdit ? "Erro ao salvar alterações" : "Erro ao criar evento"));
    } finally {
      setSubmitting(false);
    }
  };

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

      {submitAttempted && currentStepHasErrors && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          Revise os campos destacados para continuar.
        </Alert>
      )}

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 3, borderRadius: 2, width: "100%", maxWidth: 680, mx: "auto" }}>
        {isEdit && loadingEvento ? (
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando evento...
            </Typography>
          </Stack>
        ) : null}
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Stack spacing={3}>
            <EventWizardStepper activeStep={0} />

            <Stepper activeStep={eventSubStep}>
              {EVENT_SUBSTEPS.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {eventSubStep === 0 ? (
              <Box>
                <Typography variant="h6" fontWeight={800}>
                  Agência e concorrência
                </Typography>

                <Stack spacing={2} sx={{ pt: 1 }}>
                  {canPickAgencia ? (
                    <Autocomplete
                      options={agencias}
                      value={agencias.find((a) => a.id === parseId(form.agencia_id)) ?? null}
                      onChange={(_, value) =>
                        setForm((prev) => ({ ...prev, agencia_id: value ? String(value.id) : "" }))
                      }
                      getOptionLabel={(option) => option.nome}
                      isOptionEqualToValue={(option, value) => option.id === value.id}
                      disabled={loadingDomains}
                      sx={{ width: "100%" }}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Agência"
                          fullWidth
                          helperText="Opcional"
                        />
                      )}
                    />
                  ) : (
                    <TextField
                      label="Agência"
                      value={form.agencia_id ? `#${form.agencia_id}` : ""}
                      disabled
                      fullWidth
                      helperText="Agência definida pelo seu usuário"
                    />
                  )}

                  <Box display="flex" justifyContent={{ xs: "flex-start", sm: "flex-end" }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={Boolean(form.concorrencia)}
                          onChange={(_, checked) => setForm((prev) => ({ ...prev, concorrencia: checked }))}
                        />
                      }
                      label="Concorrência"
                    />
                  </Box>
                </Stack>
              </Box>
            ) : null}

            {eventSubStep === 1 ? (
              <Box>
                <Typography variant="h6" fontWeight={800}>
                  Informações do evento
              </Typography>

              <Stack spacing={2} sx={{ pt: 1 }}>
                <TextField
                  label="Nome"
                  value={form.nome}
                  onChange={handleChange("nome")}
                  required
                  fullWidth
                  error={Boolean(errors.nome)}
                  helperText={errors.nome}
                />

                <TextField
                  label="Descrição"
                  value={form.descricao}
                  onChange={handleChange("descricao")}
                  fullWidth
                  multiline
                  minRows={3}
                  error={Boolean(errors.descricao)}
                  helperText={errors.descricao ?? "Opcional (máximo 240 caracteres)"}
                />

                <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                  <Autocomplete
                    options={UF_OPTIONS}
                    value={form.estado ? form.estado : null}
                    onChange={handleEstadoChange}
                    disabled={loadingDomains}
                    sx={{ width: { xs: "100%", sm: 120 }, flex: { sm: "0 0 120px" } }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="UF"
                        required
                        error={Boolean(errors.estado)}
                        helperText={errors.estado}
                      />
                    )}
                  />

                  <Autocomplete
                    freeSolo
                    options={cidades}
                    sx={{ flex: 1, width: "100%" }}
                    inputValue={form.cidade}
                    onInputChange={(_, value) => setForm((prev) => ({ ...prev, cidade: value }))}
                    onChange={(_, value) =>
                      setForm((prev) => ({ ...prev, cidade: typeof value === "string" ? value : "" }))
                    }
                    loading={loadingCidades}
                    disabled={!normalizeText(form.estado) || loadingDomains}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Cidade"
                        required
                        fullWidth
                        error={Boolean(errors.cidade)}
                        helperText={errors.cidade}
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {loadingCidades ? <CircularProgress color="inherit" size={18} /> : null}
                              {params.InputProps.endAdornment}
                            </>
                          ),
                        }}
                      />
                    )}
                  />
                </Stack>

                <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                  <TextField
                    label="Data de início"
                    type="date"
                    value={form.data_inicio_prevista}
                    onChange={handleChange("data_inicio_prevista")}
                    required
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={Boolean(errors.data_inicio_prevista)}
                    helperText={errors.data_inicio_prevista}
                  />
                  <TextField
                    label="Data de fim"
                    type="date"
                    value={form.data_fim_prevista}
                    onChange={handleChange("data_fim_prevista")}
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={Boolean(errors.data_fim_prevista)}
                    helperText={errors.data_fim_prevista ?? "Opcional"}
                  />
                  <TextField
                    label="Investimento"
                    value={form.investimento}
                    onChange={handleChange("investimento")}
                    fullWidth
                    type="number"
                    inputMode="decimal"
                    inputProps={{ step: "0.01", min: 0 }}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">R$</InputAdornment>,
                    }}
                    error={Boolean(errors.investimento)}
                    helperText={errors.investimento ?? "Opcional"}
                  />
                </Stack>
              </Stack>
            </Box>
            ) : null}

            {eventSubStep === 2 ? (
              <Box>
                <Typography variant="h6" fontWeight={800}>
                  Classificação
                </Typography>

              <Stack spacing={2} sx={{ pt: 1 }}>
                <Autocomplete
                  options={diretorias}
                  value={selectedDiretoria}
                  onChange={(_, value) =>
                    setForm((prev) => ({ ...prev, diretoria_id: value ? String(value.id) : "" }))
                  }
                  getOptionLabel={(option) => option.nome}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  disabled={loadingDomains}
                  fullWidth
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Diretoria"
                      fullWidth
                      helperText="Opcional"
                    />
                  )}
                />

                <Autocomplete
                  options={divisoesDemandantes}
                  value={selectedDivisaoDemandante}
                  onChange={(_, value) =>
                    setForm((prev) => ({
                      ...prev,
                      divisao_demandante_id: value ? String(value.id) : "",
                    }))
                  }
                  getOptionLabel={(option) => option.nome}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  disabled={loadingDomains}
                  fullWidth
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Divisão demandante"
                      placeholder="Selecione uma Divisão demandante"
                      fullWidth
                      error={Boolean(errors.divisao_demandante_id)}
                      helperText={errors.divisao_demandante_id}
                    />
                  )}
                />

                <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                  <Autocomplete
                    options={tipos}
                    value={selectedTipo}
                    onChange={handleTipoChange}
                    getOptionLabel={(option) => option.nome}
                    isOptionEqualToValue={(option, value) => option.id === value.id}
                    disabled={loadingDomains}
                    sx={{ flex: 1 }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Tipo de evento"
                        placeholder="Selecione um Tipo de Evento"
                        fullWidth
                        helperText="Opcional"
                      />
                    )}
                  />

                  <Autocomplete
                    options={subtipos}
                    value={selectedSubtipo}
                    onChange={(_, value) =>
                      setForm((prev) => ({ ...prev, subtipo_id: value ? String(value.id) : "" }))
                    }
                    getOptionLabel={(option) => option.nome}
                    isOptionEqualToValue={(option, value) => option.id === value.id}
                    disabled={!selectedTipoId || loadingSubtipos || loadingDomains}
                    loading={loadingSubtipos}
                    sx={{ flex: 1 }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Subtipo"
                        placeholder="Selecione um Subtipo"
                        fullWidth
                        error={Boolean(errors.subtipo_id)}
                        helperText={errors.subtipo_id}
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {loadingSubtipos ? <CircularProgress color="inherit" size={18} /> : null}
                              {params.InputProps.endAdornment}
                            </>
                          ),
                        }}
                      />
                    )}
                  />
                </Stack>

                <Autocomplete
                  multiple
                  options={territorios}
                  value={selectedTerritorios}
                  onChange={(_, values) =>
                    setForm((prev) => ({
                      ...prev,
                      territorio_ids: values.map((v) => String(v.id)),
                    }))
                  }
                  disableCloseOnSelect
                  getOptionLabel={(option) => option.nome}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  disabled={loadingDomains}
                  fullWidth
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip {...getTagProps({ index })} key={option.id} label={option.nome} size="small" />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Territórios"
                      placeholder={selectedTerritorios.length ? "" : "Selecione os territórios"}
                      fullWidth
                    />
                  )}
                />

                <Autocomplete<Tag, true, false, true>
                  multiple
                  freeSolo
                  options={tags}
                  value={selectedTagValues}
                  onChange={(_, values) => {
                    const ids: string[] = [];
                    const names: string[] = [];
                    const seenIds = new Set<string>();
                    const seenNames = new Set<string>();

                    for (const value of values) {
                      if (typeof value === "string") {
                        const name = normalizeText(value);
                        if (!name) continue;
                        const existing = tagsByLowerName.get(name.toLowerCase());
                        if (existing) {
                          const id = String(existing.id);
                          if (!seenIds.has(id)) {
                            seenIds.add(id);
                            ids.push(id);
                          }
                          continue;
                        }
                        const key = name.toLowerCase();
                        if (!seenNames.has(key)) {
                          seenNames.add(key);
                          names.push(name);
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
                  }}
                  disableCloseOnSelect
                  getOptionLabel={(option) => (typeof option === "string" ? option : option.nome)}
                  isOptionEqualToValue={(option, value) => typeof value !== "string" && option.id === value.id}
                  disabled={loadingDomains}
                  fullWidth
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => {
                      const label = typeof option === "string" ? option : option.nome;
                      const key = typeof option === "string" ? option : String(option.id);
                      return <Chip {...getTagProps({ index })} key={key} label={label} size="small" />;
                    })
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Tags"
                      fullWidth
                      placeholder={selectedTagValues.length ? "" : "Selecione ou digite uma nova tag"}
                    />
                  )}
                />
              </Stack>
            </Box>
            ) : null}

            <Box display="flex" justifyContent="space-between" gap={2} pt={1}>
              <Button
                component={RouterLink}
                to={isEdit ? `/eventos/${eventoId}` : "/eventos"}
                variant="outlined"
                sx={{ textTransform: "none", fontWeight: 700 }}
              >
                Cancelar
              </Button>
              <Stack direction="row" spacing={2}>
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
                    Próximo
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={submitting || loadingDomains || (isEdit && loadingEvento)}
                    sx={{ textTransform: "none", fontWeight: 800 }}
                  >
                    {submitting
                      ? isEdit
                        ? "Salvando..."
                        : "Criando..."
                      : isEdit
                        ? "Salvar alterações"
                        : "Criar evento"}
                  </Button>
                )}
              </Stack>
            </Box>
          </Stack>
        </Box>
      </Paper>
    </Box>
  );
}
