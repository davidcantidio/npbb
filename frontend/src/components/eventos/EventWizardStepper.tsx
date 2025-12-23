import { Step, StepLabel, Stepper, Typography } from "@mui/material";

export const EVENT_WIZARD_STEPS = [
  "Evento",
  "Formulário de Lead",
  "Gamificação",
  "Ativações",
  "Questionário",
] as const;

type Props = {
  activeStep: number;
  showComingSoonFrom?: number;
  sx?: any;
};

export default function EventWizardStepper({ activeStep, showComingSoonFrom = 2, sx }: Props) {
  return (
    <Stepper activeStep={activeStep} alternativeLabel sx={{ pt: 0.5, ...(sx || {}) }}>
      {EVENT_WIZARD_STEPS.map((label, index) => (
        <Step key={label} completed={index < activeStep}>
          <StepLabel
            optional={
              index >= showComingSoonFrom ? (
                <Typography variant="caption" color="text.secondary">
                  Em breve
                </Typography>
              ) : undefined
            }
          >
            {label}
          </StepLabel>
        </Step>
      ))}
    </Stepper>
  );
}

