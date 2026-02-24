import { describe, expect, it } from "vitest";
import { canSubmitEventWizardStep, shouldPreventEnterSubmit } from "../useEventWizardValidation";

describe("useEventWizardValidation", () => {
  it("blocks Enter submit on classification step", () => {
    expect(
      shouldPreventEnterSubmit({
        isClassificationStep: true,
        key: "Enter",
        targetTagName: "INPUT",
      }),
    ).toBe(true);
  });

  it("allows Enter inside textarea", () => {
    expect(
      shouldPreventEnterSubmit({
        isClassificationStep: true,
        key: "Enter",
        targetTagName: "TEXTAREA",
      }),
    ).toBe(false);
  });

  it("requires last step and required fields before submit", () => {
    expect(canSubmitEventWizardStep({ isLastSubStep: false, hasRequiredFields: true })).toBe(false);
    expect(canSubmitEventWizardStep({ isLastSubStep: true, hasRequiredFields: false })).toBe(false);
    expect(canSubmitEventWizardStep({ isLastSubStep: true, hasRequiredFields: true })).toBe(true);
  });
});
