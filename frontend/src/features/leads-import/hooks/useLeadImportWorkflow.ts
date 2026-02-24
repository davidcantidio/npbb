import type { LeadImportPreview, LeadImportSuggestion } from "../../../services/leads_import";

/**
 * Immutable helpers for lead import mapping updates.
 * @returns Mapping helper functions that preserve immutable preview state updates.
 */
export function useLeadImportWorkflow() {
  const updateSuggestionAt = (
    preview: LeadImportPreview | null,
    index: number,
    campo: string | null,
  ): LeadImportPreview | null => {
    if (!preview) return preview;
    const nextSuggestions: LeadImportSuggestion[] = preview.suggestions.map((suggestion, suggestionIndex) => {
      if (suggestionIndex !== index) return suggestion;
      const fallbackHeader = preview.headers[suggestionIndex] || `Coluna ${suggestionIndex + 1}`;
      const current = suggestion ?? { coluna: fallbackHeader, campo: null, confianca: null };
      return { ...current, campo };
    });
    return { ...preview, suggestions: nextSuggestions };
  };

  return { updateSuggestionAt };
}
