import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  FormControlLabel,
  Link,
  Paper,
  Stack,
  TextField,
  ThemeProvider,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

import { getFieldLabel } from "./landingHelpers";
import {
  FORM_ONLY_CONTENT_WIDTH_SX,
  getFormOnlySurfaceSx,
} from "./formOnlySurface";
import { buildFormCardTheme } from "./landingStyle";
import type { LandingFormCardProps } from "./landingSections.types";

export type FormCardProps = LandingFormCardProps;

export default function FormCard({
  data,
  content,
  layout,
  isPreview,
  formState,
  consentimento,
  submitError,
  saving,
  submitted,
  onInputChange,
  onConsentimentoChange,
  onSubmit,
  onReset,
  onResetDisabled = false,
}: FormCardProps) {
  const formCardTheme = buildFormCardTheme(data);

  return (
    <Box
      data-testid="form-card-container"
      sx={{
        width: "100%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Paper
        data-testid="form-card-paper"
        elevation={0}
        sx={[FORM_ONLY_CONTENT_WIDTH_SX, getFormOnlySurfaceSx(layout)]}
      >
        <ThemeProvider theme={formCardTheme}>
          {!submitted ? (
            <Stack spacing={2.5}>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {content.formTitle}
                </Typography>
                {content.formSubtitle ? (
                  <Typography variant="body2" color="text.secondary">
                    {content.formSubtitle}
                  </Typography>
                ) : null}
              </Box>

              {content.calloutMessage ? <Alert severity="info">{content.calloutMessage}</Alert> : null}

              {submitError ? <Alert severity="error">{submitError}</Alert> : null}

              <Box
                sx={{
                  display: "grid",
                  gap: 2,
                  gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
                }}
              >
                {data.formulario.campos.map((field) => (
                  <TextField
                    key={field.key}
                    fullWidth
                    required={field.required}
                    disabled={isPreview}
                    type={field.input_type}
                    label={getFieldLabel(field)}
                    value={formState[field.key] || ""}
                    onChange={(event) => onInputChange?.(field.key, event.target.value)}
                    autoComplete={field.autocomplete || undefined}
                    placeholder={field.placeholder || undefined}
                    multiline={field.key === "interesses"}
                    minRows={field.key === "interesses" ? 3 : undefined}
                    sx={{
                      gridColumn: field.key === "interesses" || field.key === "endereco" ? "1 / -1" : undefined,
                    }}
                  />
                ))}
              </Box>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={consentimento}
                    disabled={isPreview}
                    onChange={(_, checked) => onConsentimentoChange?.(checked)}
                  />
                }
                label={
                  <Typography variant="body2" color="text.secondary">
                    {data.formulario.lgpd_texto}{" "}
                    <Link href={data.formulario.privacy_policy_url} target="_blank" rel="noreferrer">
                      Politica de privacidade
                    </Link>
                    .
                  </Typography>
                }
              />

              <Button
                fullWidth
                size="large"
                variant={layout.buttonVariant}
                color={layout.buttonColor}
                onClick={isPreview ? undefined : onSubmit}
                disabled={isPreview || saving}
                sx={{
                  minHeight: 52,
                  ...(layout.buttonStyles || {}),
                }}
              >
                {saving ? <CircularProgress size={22} color="inherit" /> : content.ctaText}
              </Button>
            </Stack>
          ) : (
            <Stack spacing={2.5}>
              <Chip label="Cadastro concluido" sx={{ alignSelf: "flex-start", bgcolor: alpha(data.template.color_secondary, 0.9) }} />
              <Typography variant="h5">{submitted.mensagem_sucesso}</Typography>
              <Typography variant="body1" color="text.secondary">
                Seu cadastro foi registrado para {data.evento.nome}. Em breve o time do BB pode entrar em contato.
              </Typography>
              <Button variant="outlined" onClick={onReset} disabled={onResetDisabled} sx={{ alignSelf: "flex-start" }}>
                Cadastrar outro email
              </Button>
            </Stack>
          )}
        </ThemeProvider>
      </Paper>
    </Box>
  );
}
