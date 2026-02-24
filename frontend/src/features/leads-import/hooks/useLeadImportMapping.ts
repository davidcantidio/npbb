import { Dispatch, SetStateAction, useCallback, useEffect, useState } from "react";
import {
  createLeadAlias,
  LeadImportPreview,
  LeadImportSuggestion,
  validateLeadMapping,
} from "../../../services/leads_import";
import { toApiErrorMessage } from "../../../services/http";
import { useLeadImportWorkflow } from "./useLeadImportWorkflow";

type ReferenceOptions = Record<string, Array<{ value: string; label: string }>>;

/**
 * Handles assisted mapping state, alias persistence and mapping validation.
 * @param token Auth token used by validate/import alias APIs.
 * @param preview Current preview payload from uploaded file.
 * @param setPreview Preview state setter used for immutable mapping updates.
 * @param referenceOptions Canonical options used to auto-select alias candidates.
 * @returns Mapping UI state and handlers for selection, validation and alias persistence.
 * @throws Error Re-throws validation errors after mapping message state is updated.
 */
export function useLeadImportMapping(
  token: string | null,
  preview: LeadImportPreview | null,
  setPreview: Dispatch<SetStateAction<LeadImportPreview | null>>,
  referenceOptions: ReferenceOptions,
) {
  const { updateSuggestionAt } = useLeadImportWorkflow();

  const [mappingError, setMappingError] = useState<string | null>(null);
  const [aliasWarning, setAliasWarning] = useState<string | null>(null);
  const [secondarySelections, setSecondarySelections] = useState<Record<number, string>>({});
  const [activeRowIndex, setActiveRowIndex] = useState<number | null>(null);

  const applyAliasSelections = useCallback((nextPreview: LeadImportPreview | null) => {
    if (!nextPreview) {
      setSecondarySelections({});
      return;
    }

    const initial: Record<number, string> = {};
    nextPreview.headers.forEach((_, idx) => {
      const hit = nextPreview.alias_hits?.[idx];
      if (hit?.evento_id) initial[idx] = String(hit.evento_id);
      if (hit?.canonical_value) initial[idx] = hit.canonical_value;
    });
    setSecondarySelections(initial);
  }, []);

  useEffect(() => {
    applyAliasSelections(preview);
  }, [applyAliasSelections, preview]);

  useEffect(() => {
    if (!preview) return;

    const normalize = (value: string) =>
      value
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();

    setSecondarySelections((prev) => {
      const next = { ...prev };
      preview.headers.forEach((_, idx) => {
        const campo = preview.suggestions[idx]?.campo;
        if (!campo || !["evento_nome", "cidade", "estado", "genero"].includes(campo)) return;
        if (next[idx]) return;
        const sample = preview.samples_by_column[idx]?.[0];
        if (!sample) return;
        const options = referenceOptions[campo] || [];
        const match = options.find((option) => normalize(option.label) === normalize(sample));
        if (match) next[idx] = match.value;
      });
      return next;
    });
  }, [preview, referenceOptions]);

  const onSuggestionFieldChange = useCallback((index: number, campo: string | null) => {
    setPreview((prev) => updateSuggestionAt(prev, index, campo));
  }, [setPreview, updateSuggestionAt]);

  const confirmMapping = useCallback(async (suggestions: LeadImportSuggestion[], headers: string[], samples: string[][]) => {
    if (!token) return;

    setMappingError(null);
    setAliasWarning(null);

    try {
      await validateLeadMapping(token, suggestions);
      const aliasRequests: Array<Promise<unknown>> = [];
      headers.forEach((_, idx) => {
        const campo = suggestions[idx]?.campo;
        if (!campo || !["evento_nome", "cidade", "estado", "genero"].includes(campo)) return;
        const sample = samples[idx]?.[0];
        const selected = secondarySelections[idx];
        if (!sample || !selected) return;

        const tipoMap: Record<string, string> = {
          evento_nome: "EVENTO",
          cidade: "CIDADE",
          estado: "ESTADO",
          genero: "GENERO",
        };

        const payload =
          campo === "evento_nome"
            ? { tipo: tipoMap[campo], valor_origem: sample, evento_id: Number(selected) }
            : { tipo: tipoMap[campo], valor_origem: sample, canonical_value: selected };

        aliasRequests.push(createLeadAlias(token, payload));
      });

      if (aliasRequests.length) {
        const aliasResults = await Promise.allSettled(aliasRequests);
        const failures = aliasResults.filter((result) => result.status === "rejected").length;
        if (failures > 0) {
          setAliasWarning(
            `${failures} correspondencia(s) de alias nao foram salvas. O import continua, mas revise as referencias.`,
          );
        }
      }
    } catch (err) {
      const message = toApiErrorMessage(err, "Erro ao validar mapeamento.");
      setMappingError(message);
      throw err;
    }
  }, [secondarySelections, token]);

  return {
    mappingError,
    setMappingError,
    aliasWarning,
    setAliasWarning,
    secondarySelections,
    setSecondarySelections,
    activeRowIndex,
    setActiveRowIndex,
    onSuggestionFieldChange,
    confirmMapping,
  };
}

