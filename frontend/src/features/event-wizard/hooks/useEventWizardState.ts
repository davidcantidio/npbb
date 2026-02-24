import { useState } from "react";

export type EventWizardProgressState = {
  eventSubStep: number;
  submitAttempted: boolean;
  submitAndContinueRequested: boolean;
};

/**
 * Controls lightweight wizard progress flags used across event creation substeps.
 * @param initialSubStep Initial wizard substep index.
 * @returns Local state and setters for substep and submit intent flags.
 */
export function useEventWizardState(initialSubStep = 0) {
  const [eventSubStep, setEventSubStep] = useState(initialSubStep);
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [submitAndContinueRequested, setSubmitAndContinueRequested] = useState(false);

  return {
    eventSubStep,
    setEventSubStep,
    submitAttempted,
    setSubmitAttempted,
    submitAndContinueRequested,
    setSubmitAndContinueRequested,
  };
}
