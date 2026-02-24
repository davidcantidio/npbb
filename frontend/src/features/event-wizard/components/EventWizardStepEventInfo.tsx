import { Autocomplete, Box, CircularProgress, InputAdornment, Stack, TextField, Typography } from "@mui/material";
import {
  EventWizardFormErrors,
  EventWizardFormState,
  UF_OPTIONS,
} from "../hooks/useEventWizardForm";

type EventWizardStepEventInfoProps = {
  visible: boolean;
  form: EventWizardFormState;
  errors: EventWizardFormErrors;
  cidades: string[];
  loadingDomains: boolean;
  loadingCidades: boolean;
  setFieldRef: (fieldId: string) => (node: HTMLDivElement | null) => void;
  getFieldSx: (fieldId: string, base?: unknown) => unknown;
  getFieldHelperText: (field: keyof EventWizardFormState, base?: string) => string | undefined;
  onChange: (field: keyof EventWizardFormState) => (event: { target?: { value?: unknown } }) => void;
  onEstadoChange: (_: unknown, value: string | null) => void;
};

/**
 * Renders basic event information fields.
 */
export function EventWizardStepEventInfo({
  visible,
  form,
  errors,
  cidades,
  loadingDomains,
  loadingCidades,
  setFieldRef,
  getFieldSx,
  getFieldHelperText,
  onChange,
  onEstadoChange,
}: EventWizardStepEventInfoProps) {
  if (!visible) return null;

  return (
    <Box>
      <Typography variant="h6" fontWeight={800}>
        Informacoes do evento
      </Typography>

      <Stack spacing={2} sx={{ pt: 1 }}>
        <Box ref={setFieldRef("nome")} sx={getFieldSx("nome") as object}>
          <TextField
            label="Nome"
            value={form.nome}
            onChange={onChange("nome")}
            required
            fullWidth
            error={Boolean(errors.nome)}
            helperText={getFieldHelperText("nome")}
          />
        </Box>

        <Box ref={setFieldRef("descricao")} sx={getFieldSx("descricao") as object}>
          <TextField
            label="Descricao"
            value={form.descricao}
            onChange={onChange("descricao")}
            fullWidth
            multiline
            minRows={3}
            error={Boolean(errors.descricao)}
            helperText={getFieldHelperText("descricao", "Opcional (maximo 240 caracteres)")}
          />
        </Box>

        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <Box
            ref={setFieldRef("estado")}
            sx={getFieldSx("estado", { width: { xs: "100%", sm: 120 }, flex: { sm: "0 0 120px" } }) as object}
          >
            <Autocomplete
              options={[...UF_OPTIONS]}
              value={form.estado ? form.estado : null}
              onChange={onEstadoChange}
              disabled={loadingDomains}
              sx={{ width: "100%" }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="UF"
                  required
                  error={Boolean(errors.estado)}
                  helperText={getFieldHelperText("estado")}
                />
              )}
            />
          </Box>

          <Box ref={setFieldRef("cidade")} sx={getFieldSx("cidade", { flex: 1, width: "100%" }) as object}>
            <Autocomplete
              freeSolo
              options={cidades}
              sx={{ flex: 1, width: "100%" }}
              inputValue={form.cidade}
              onInputChange={(_, value) => onChange("cidade")({ target: { value } })}
              onChange={(_, value) => onChange("cidade")({ target: { value: typeof value === "string" ? value : "" } })}
              loading={loadingCidades}
              disabled={!String(form.estado || "").trim() || loadingDomains}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Cidade"
                  required
                  fullWidth
                  error={Boolean(errors.cidade)}
                  helperText={getFieldHelperText("cidade")}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {loadingCidades ? <CircularProgress color="inherit" size={18} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Box>
        </Stack>

        <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
          <Box ref={setFieldRef("data_inicio_prevista")} sx={getFieldSx("data_inicio_prevista", { flex: 1, width: "100%" }) as object}>
            <TextField
              label="Data de inicio"
              type="date"
              value={form.data_inicio_prevista}
              onChange={onChange("data_inicio_prevista")}
              required
              fullWidth
              InputLabelProps={{ shrink: true }}
              error={Boolean(errors.data_inicio_prevista)}
              helperText={getFieldHelperText("data_inicio_prevista")}
            />
          </Box>
          <Box ref={setFieldRef("data_fim_prevista")} sx={getFieldSx("data_fim_prevista", { flex: 1, width: "100%" }) as object}>
            <TextField
              label="Data de fim"
              type="date"
              value={form.data_fim_prevista}
              onChange={onChange("data_fim_prevista")}
              fullWidth
              InputLabelProps={{ shrink: true }}
              error={Boolean(errors.data_fim_prevista)}
              helperText={getFieldHelperText("data_fim_prevista", "Opcional")}
            />
          </Box>
          <Box ref={setFieldRef("investimento")} sx={getFieldSx("investimento", { flex: 1, width: "100%" }) as object}>
            <TextField
              label="Investimento"
              value={form.investimento}
              onChange={onChange("investimento")}
              fullWidth
              type="number"
              inputMode="decimal"
              inputProps={{ step: "0.01", min: 0 }}
              InputProps={{ startAdornment: <InputAdornment position="start">R$</InputAdornment> }}
              error={Boolean(errors.investimento)}
              helperText={getFieldHelperText("investimento", "Opcional")}
            />
          </Box>
        </Stack>
      </Stack>
    </Box>
  );
}
