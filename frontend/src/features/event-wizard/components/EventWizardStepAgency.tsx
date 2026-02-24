import { Autocomplete, Box, FormControlLabel, Stack, Switch, TextField, Typography } from "@mui/material";
import { Agencia } from "../../../services/agencias";
import { EventWizardFormState } from "../hooks/useEventWizardForm";

type EventWizardStepAgencyProps = {
  visible: boolean;
  canPickAgencia: boolean;
  agencias: Agencia[];
  agenciaId: string;
  concorrencia: boolean;
  loadingDomains: boolean;
  setFieldRef: (fieldId: string) => (node: HTMLDivElement | null) => void;
  getFieldSx: (fieldId: string, base?: unknown) => unknown;
  onAgenciaChange: (agenciaId: string) => void;
  onConcorrenciaChange: (checked: boolean) => void;
  getFieldHelperText: (field: keyof EventWizardFormState, base?: string) => string | undefined;
};

/**
 * Renders agencia and concorrencia controls for the first wizard substep.
 */
export function EventWizardStepAgency({
  visible,
  canPickAgencia,
  agencias,
  agenciaId,
  concorrencia,
  loadingDomains,
  setFieldRef,
  getFieldSx,
  onAgenciaChange,
  onConcorrenciaChange,
  getFieldHelperText,
}: EventWizardStepAgencyProps) {
  if (!visible) return null;

  return (
    <Box>
      <Typography variant="h6" fontWeight={800}>
        Agencia e concorrencia
      </Typography>

      <Stack spacing={2} sx={{ pt: 1 }}>
        {canPickAgencia ? (
          <Box ref={setFieldRef("agencia_id")} sx={getFieldSx("agencia_id") as object}>
            <Autocomplete
              options={agencias}
              value={agencias.find((agencia) => agencia.id === Number(agenciaId)) ?? null}
              onChange={(_, value) => onAgenciaChange(value ? String(value.id) : "")}
              getOptionLabel={(option) => option.nome}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              disabled={loadingDomains}
              sx={{ width: "100%" }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Agencia"
                  fullWidth
                  helperText={getFieldHelperText("agencia_id", "Opcional")}
                />
              )}
            />
          </Box>
        ) : (
          <Box ref={setFieldRef("agencia_id")} sx={getFieldSx("agencia_id") as object}>
            <TextField
              label="Agencia"
              value={agenciaId ? `#${agenciaId}` : ""}
              disabled
              fullWidth
              helperText={getFieldHelperText("agencia_id", "Agencia definida pelo seu usuario")}
            />
          </Box>
        )}

        <Box display="flex" justifyContent={{ xs: "flex-start", sm: "flex-end" }}>
          <FormControlLabel
            control={<Switch checked={concorrencia} onChange={(_, checked) => onConcorrenciaChange(checked)} />}
            label="Concorrencia"
          />
        </Box>
      </Stack>
    </Box>
  );
}
