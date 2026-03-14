import { Autocomplete, Box, Stack, TextField, Typography } from "@mui/material";
import { TEMPLATE_OVERRIDE_OPTIONS } from "../constants";
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
      <Stack spacing={1.5} sx={{ maxWidth: { xs: "100%", md: 480 } }}>
        <Box sx={{ width: "100%" }}>
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
                label="Template"
                placeholder="Selecione..."
              />
            )}
          />
        </Box>
        <Box sx={{ width: "100%" }}>
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
