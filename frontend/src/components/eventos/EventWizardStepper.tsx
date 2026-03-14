import { Step, StepButton, StepLabel, Stepper, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export const EVENT_WIZARD_STEPS = [
  "Evento",
  "Landing Page",
  "Gamificação",
  "Ativações",
  "Questionário",
] as const;

export const EVENT_STEP_PATHS = [
  "editar",
  "formulario-lead",
  "gamificacao",
  "ativacoes",
  "questionario",
] as const;

type Props = {
  activeStep: number;
  eventoId?: number;
  showComingSoonFrom?: number;
  sx?: any;
};

export default function EventWizardStepper({ activeStep, eventoId, showComingSoonFrom, sx }: Props) {
  const isValidEventoId = Number.isFinite(eventoId);

  return (
    <Stepper activeStep={activeStep} alternativeLabel sx={{ pt: 0.5, ...(sx || {}) }}>
      {EVENT_WIZARD_STEPS.map((label, index) => {
        const isComingSoon =
          typeof showComingSoonFrom === "number" && index >= showComingSoonFrom;
        const isClickable = isValidEventoId && !isComingSoon;
        const path = EVENT_STEP_PATHS[index];

        const stepLabel = (
          <StepLabel
            optional={
              isComingSoon ? (
                <Typography variant="caption" color="text.secondary">
                  Em breve
                </Typography>
              ) : undefined
            }
          >
            {label}
          </StepLabel>
        );

        return (
          <Step key={label} completed={index < activeStep}>
            {isClickable ? (
              <StepButton
                component={RouterLink}
                to={`/eventos/${eventoId}/${path}`}
                sx={{ textDecoration: "none", color: "inherit" }}
              >
                {stepLabel}
              </StepButton>
            ) : (
              stepLabel
            )}
          </Step>
        );
      })}
    </Stepper>
  );
}
