import { useCallback, useMemo, useState } from "react";
import { TipoEvento } from "../../../services/eventos";

export type EventWizardFormState = {
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

export type EventWizardFormErrors = Partial<Record<keyof EventWizardFormState, string>>;

export const EVENT_SUBSTEPS = ["Agencia", "Informacoes do evento", "Classificacao"] as const;

export const UF_OPTIONS = [
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
] as const;

/**
 * Normalizes free-text values used across wizard payload fields.
 * @param value Raw text value.
 * @returns Trimmed string representation.
 */
export function normalizeWizardText(value: string): string {
  return String(value || "").trim();
}

/**
 * Parses positive numeric ids from form string values.
 * @param value Raw id value stored in form state.
 * @returns Positive numeric id or `null` when invalid.
 */
export function parseWizardId(value: string): number | null {
  const id = Number(value);
  return Number.isFinite(id) && id > 0 ? id : null;
}

/**
 * Stores event wizard form values and centralizes validation logic.
 * @param params Initial defaults used to bootstrap form state.
 * @returns Form state, validation metadata and field handlers used by wizard UI.
 */
export function useEventWizardForm(params: { defaultAgenciaId?: number | null }) {
  const { defaultAgenciaId } = params;

  const [form, setForm] = useState<EventWizardFormState>({
    agencia_id: defaultAgenciaId ? String(defaultAgenciaId) : "",
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

  const selectedTipoId = useMemo(() => parseWizardId(form.tipo_id), [form.tipo_id]);

  const errors: EventWizardFormErrors = useMemo(() => {
    const next: EventWizardFormErrors = {};

    const nome = normalizeWizardText(form.nome);
    if (!nome) next.nome = "Informe o nome do evento";

    const descricao = normalizeWizardText(form.descricao);
    if (descricao && descricao.length > 240) next.descricao = "Maximo 240 caracteres";

    const cidade = normalizeWizardText(form.cidade);
    if (!cidade) next.cidade = "Informe a cidade";
    else if (cidade.length > 40) next.cidade = "Maximo 40 caracteres";

    const estado = normalizeWizardText(form.estado).toUpperCase();
    if (!estado) next.estado = "Selecione a UF";
    else if (!UF_OPTIONS.includes(estado as (typeof UF_OPTIONS)[number])) next.estado = "UF invalida";

    if (form.subtipo_id && !parseWizardId(form.subtipo_id)) {
      next.subtipo_id = "Subtipo invalido";
    }

    const inicioPrev = form.data_inicio_prevista || "";
    const fimPrev = form.data_fim_prevista || "";
    if (!inicioPrev) next.data_inicio_prevista = "Informe a data do evento";
    if (inicioPrev && fimPrev && fimPrev < inicioPrev) {
      next.data_fim_prevista = "Fim previsto deve ser maior/igual ao inicio previsto";
    }

    const investimento = normalizeWizardText(form.investimento);
    if (investimento) {
      const numeric = Number(investimento.replace(",", "."));
      if (!Number.isFinite(numeric) || numeric < 0) {
        next.investimento = "Informe um investimento valido";
      }
    }

    if (form.divisao_demandante_id && !parseWizardId(form.divisao_demandante_id)) {
      next.divisao_demandante_id = "Selecione uma divisao valida";
    }

    return next;
  }, [form]);

  const canSubmit = useMemo(() => Object.keys(errors).length === 0, [errors]);

  const eventStepFields = useMemo<Array<Array<keyof EventWizardFormState>>>(
    () => [
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
    ],
    [],
  );

  const applyEventoData = useCallback((data: {
    agencia_id?: number | null;
    concorrencia: boolean;
    nome?: string | null;
    descricao?: string | null;
    estado?: string | null;
    cidade?: string | null;
    data_inicio_prevista?: string | null;
    data_fim_prevista?: string | null;
    investimento?: string | number | null;
    diretoria_id?: number | null;
    divisao_demandante_id?: number | null;
    tipo_id?: number | null;
    subtipo_id?: number | null;
    tag_ids?: number[];
    territorio_ids?: number[];
  }) => {
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
      divisao_demandante_id: data.divisao_demandante_id != null ? String(data.divisao_demandante_id) : "",
      tipo_id: data.tipo_id != null ? String(data.tipo_id) : "",
      subtipo_id: data.subtipo_id != null ? String(data.subtipo_id) : "",
      tag_ids: Array.isArray(data.tag_ids) ? data.tag_ids.map((id) => String(id)) : [],
      tag_names: [],
      territorio_ids: Array.isArray(data.territorio_ids)
        ? data.territorio_ids.map((id) => String(id))
        : [],
    });
  }, []);

  const ensureAgencia = useCallback((agenciaId: string) => {
    setForm((prev) => (prev.agencia_id ? prev : { ...prev, agencia_id: agenciaId }));
  }, []);

  const handleChange = useCallback(
    (field: keyof EventWizardFormState) =>
      (event: { target?: { value?: unknown } }) => {
        const value = event?.target?.value;
        setForm((prev) => ({ ...prev, [field]: String(value ?? "") }));
      },
    [],
  );

  const handleEstadoChange = useCallback((_: unknown, value: string | null) => {
    const next = String(value || "");
    setForm((prev) => ({
      ...prev,
      estado: next,
      cidade: prev.estado === next ? prev.cidade : "",
    }));
  }, []);

  const handleTipoChange = useCallback((_: unknown, value: TipoEvento | null) => {
    setForm((prev) => ({
      ...prev,
      tipo_id: value ? String(value.id) : "",
      subtipo_id: "",
    }));
  }, []);

  return {
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
  };
}
