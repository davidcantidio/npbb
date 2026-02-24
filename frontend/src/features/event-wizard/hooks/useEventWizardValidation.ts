/**
 * Returns true when the current substep can be safely submitted.
 * @param params Validation context for current wizard substep.
 * @returns `true` when final step can be submitted.
 */
export function canSubmitEventWizardStep(params: {
  isLastSubStep: boolean;
  hasRequiredFields: boolean;
}): boolean {
  if (!params.isLastSubStep) return false;
  return params.hasRequiredFields;
}

/**
 * Blocks Enter-key submit on the classification step to avoid unintended auto-advance.
 * @param params Keyboard context from form interactions.
 * @returns `true` when Enter submit must be prevented.
 */
export function shouldPreventEnterSubmit(params: {
  isClassificationStep: boolean;
  key: string;
  targetTagName?: string | null;
}): boolean {
  if (!params.isClassificationStep) return false;
  if (params.key !== "Enter") return false;
  return String(params.targetTagName || "").toUpperCase() !== "TEXTAREA";
}
