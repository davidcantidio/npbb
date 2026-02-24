import { Dispatch, SetStateAction, useCallback, useEffect, useMemo, useRef, useState } from "react";

type FocusFieldId =
  | "agencia_id"
  | "nome"
  | "descricao"
  | "estado"
  | "cidade"
  | "data_inicio_prevista"
  | "data_fim_prevista"
  | "investimento"
  | "diretoria_id"
  | "divisao_demandante_id"
  | "tipo_id"
  | "subtipo_id"
  | "territorio_ids"
  | "tag_ids";

const FIELD_STEP_MAP: Record<FocusFieldId, number> = {
  agencia_id: 0,
  nome: 1,
  descricao: 1,
  estado: 1,
  cidade: 1,
  data_inicio_prevista: 1,
  data_fim_prevista: 1,
  investimento: 1,
  diretoria_id: 2,
  divisao_demandante_id: 2,
  tipo_id: 2,
  subtipo_id: 2,
  territorio_ids: 2,
  tag_ids: 2,
};

const FIELD_LABEL_MAP: Record<FocusFieldId, string> = {
  agencia_id: "Agencia",
  nome: "Nome",
  descricao: "Descricao",
  estado: "UF",
  cidade: "Cidade",
  data_inicio_prevista: "Data de inicio",
  data_fim_prevista: "Data de fim",
  investimento: "Investimento",
  diretoria_id: "Diretoria",
  divisao_demandante_id: "Divisao demandante",
  tipo_id: "Tipo de evento",
  subtipo_id: "Subtipo",
  territorio_ids: "Territorios",
  tag_ids: "Tags",
};

function normalizeText(value: string): string {
  return String(value || "").trim();
}

/**
 * Handles query-driven missing-field focus, highlighting and navigation helpers.
 * @param params Query/search and loading context needed to drive assisted field focus.
 * @returns Focus helpers, highlighting metadata and pending-field navigation handlers.
 */
export function useEventWizardFocus(params: {
  locationSearch: string;
  eventSubStep: number;
  setEventSubStep: Dispatch<SetStateAction<number>>;
  loadingEvento: boolean;
  loadingDomains: boolean;
}) {
  const { locationSearch, eventSubStep, setEventSubStep, loadingEvento, loadingDomains } = params;

  const searchParams = useMemo(() => new URLSearchParams(locationSearch), [locationSearch]);
  const missingFieldsFromQuery = useMemo(() => {
    const raw = searchParams.get("missing") ?? "";
    const fields = raw
      .split(",")
      .map((value) => normalizeText(value))
      .filter(Boolean);
    return Array.from(new Set(fields));
  }, [searchParams]);
  const focusFieldParam = useMemo(() => normalizeText(searchParams.get("focus") ?? ""), [searchParams]);

  const [manualFocusField, setManualFocusField] = useState("");
  const fieldRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const lastFocusedFieldRef = useRef<string | null>(null);

  const missingFieldsSet = useMemo(() => new Set(missingFieldsFromQuery), [missingFieldsFromQuery]);

  const focusFieldIdFromQuery = useMemo(() => {
    if (focusFieldParam && FIELD_STEP_MAP[focusFieldParam as FocusFieldId] !== undefined) {
      return focusFieldParam;
    }
    const fallback = missingFieldsFromQuery.find(
      (fieldId) => FIELD_STEP_MAP[fieldId as FocusFieldId] !== undefined,
    );
    return fallback ?? "";
  }, [focusFieldParam, missingFieldsFromQuery]);

  const activeFocusField = manualFocusField || focusFieldIdFromQuery;
  const focusFieldStep = activeFocusField
    ? FIELD_STEP_MAP[activeFocusField as FocusFieldId] ?? null
    : null;

  const missingFieldHighlightSx = useMemo(
    () => ({
      borderRadius: 2,
      boxShadow: "0 0 0 2px rgba(255, 167, 38, 0.7)",
      "& .MuiOutlinedInput-root": {
        backgroundColor: "rgba(255, 167, 38, 0.08)",
      },
    }),
    [],
  );

  const setFieldRef = useCallback(
    (fieldId: string) => (node: HTMLDivElement | null) => {
      fieldRefs.current[fieldId] = node;
    },
    [],
  );

  const getFieldSx = useCallback(
    (fieldId: string, base?: unknown) => {
      const highlight = missingFieldsSet.has(fieldId) ? missingFieldHighlightSx : undefined;
      if (highlight && base) return [highlight, base];
      return highlight ?? base;
    },
    [missingFieldHighlightSx, missingFieldsSet],
  );

  const focusFieldInView = useCallback((fieldId: string): boolean => {
    const node = fieldRefs.current[fieldId];
    if (!node) return false;
    if (typeof node.scrollIntoView === "function") {
      node.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    const input = node.querySelector("input, textarea") as HTMLInputElement | HTMLTextAreaElement | null;
    if (input) input.focus();
    return true;
  }, []);

  const handlePendingFieldClick = useCallback(
    (fieldId: string) => {
      if (!fieldId) return;
      const step = FIELD_STEP_MAP[fieldId as FocusFieldId];
      if (step === undefined) return;

      lastFocusedFieldRef.current = null;
      setManualFocusField(fieldId);
      if (eventSubStep !== step) {
        setEventSubStep(step);
        return;
      }
      focusFieldInView(fieldId);
    },
    [eventSubStep, focusFieldInView, setEventSubStep],
  );

  const missingFieldsForList = useMemo(
    () => missingFieldsFromQuery.filter((fieldId) => FIELD_STEP_MAP[fieldId as FocusFieldId] !== undefined),
    [missingFieldsFromQuery],
  );

  const getFieldLabel = useCallback((fieldId: string) => {
    return FIELD_LABEL_MAP[fieldId as FocusFieldId] ?? fieldId;
  }, []);

  useEffect(() => {
    if (!activeFocusField || focusFieldStep == null) return;
    if (lastFocusedFieldRef.current === activeFocusField) return;
    if (eventSubStep !== focusFieldStep) {
      setEventSubStep(focusFieldStep);
    }
  }, [activeFocusField, eventSubStep, focusFieldStep, setEventSubStep]);

  useEffect(() => {
    if (!activeFocusField || focusFieldStep == null) return;
    if (eventSubStep !== focusFieldStep) return;
    if (loadingEvento || loadingDomains) return;
    if (lastFocusedFieldRef.current === activeFocusField) return;

    if (focusFieldInView(activeFocusField)) {
      lastFocusedFieldRef.current = activeFocusField;
    }
  }, [activeFocusField, eventSubStep, focusFieldInView, focusFieldStep, loadingDomains, loadingEvento]);

  return {
    missingFieldsSet,
    missingFieldsForList,
    getFieldLabel,
    handlePendingFieldClick,
    getFieldSx,
    setFieldRef,
  };
}
