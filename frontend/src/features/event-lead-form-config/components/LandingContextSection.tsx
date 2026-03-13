import { Alert, Autocomplete, Box, Stack, TextField, Typography } from "@mui/material";
import { LANDING_CUSTOMIZATION_MESSAGE, TEMPLATE_OVERRIDE_OPTIONS } from "../constants";
import type { LandingMeta } from "../hooks/useEventLeadFormConfigData";

type LandingContextSectionProps = {
  landingMeta: LandingMeta;
  onLandingMetaChange: (updates: Partial<LandingMeta>) => void;
};

export function LandingContextSection({
  landingMeta,
  onLandingMetaChange,
}: LandingContextSectionProps) {
  return (
    <Box>
      <Typography variant="subtitle1" fontWeight={900} gutterBottom>
        Contexto da landing
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        Personalize o comportamento inicial da landing publica e valide o template resolvido antes
        de usar a URL em campo.
      </Typography>
      <Stack spacing={1.5}>
        <Box sx={{ width: "100%", maxWidth: { xs: "100%", md: 520 } }}>
          <Autocomplete
            freeSolo
            options={[...TEMPLATE_OVERRIDE_OPTIONS]}
            value={landingMeta.template_override}
            onChange={(_, value) =>
              onLandingMetaChange({ template_override: value ?? "" })
            }
            onInputChange={(_, value) =>
              onLandingMetaChange({ template_override: value })
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label="Template override"
                placeholder="Deixe em branco para usar a resolucao automatica"
              />
            )}
          />
        </Box>
        <Alert severity="info" variant="outlined">
          {LANDING_CUSTOMIZATION_MESSAGE}
        </Alert>
        <Box sx={{ width: "100%", maxWidth: { xs: "100%", md: 460 } }}>
          <TextField
            label="CTA personalizado"
            value={landingMeta.cta_personalizado}
            onChange={(event) =>
              onLandingMetaChange({ cta_personalizado: event.target.value })
            }
            fullWidth
          />
        </Box>
        <TextField
          label="Descricao curta"
          value={landingMeta.descricao_curta}
          onChange={(event) =>
            onLandingMetaChange({ descricao_curta: event.target.value })
          }
          multiline
          minRows={2}
          fullWidth
        />
      </Stack>
    </Box>
  );
}
