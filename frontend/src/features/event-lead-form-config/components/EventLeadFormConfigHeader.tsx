import { Box, Button, CircularProgress, Stack, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink } from "react-router-dom";

import { WIZARD_ACTION_BUTTON_SX } from "../../../components/eventos/EventWizardPageShell";

type EventLeadFormConfigHeaderProps = {
  eventoId: number;
  config: unknown;
  loading: boolean;
  saving: boolean;
  onSave: () => void;
};

export function EventLeadFormConfigHeader({
  eventoId,
  config,
  loading,
  saving,
  onSave,
}: EventLeadFormConfigHeaderProps) {
  const isValidEventoId = Number.isFinite(eventoId);

  const subtitle = isValidEventoId
    ? `Configure o tema e os campos do formulário do evento #${eventoId}.`
    : "Configure o tema e os campos do formulário do evento.";

  return (
    <Stack
      direction={{ xs: "column", md: "row" }}
      justifyContent="space-between"
      alignItems={{ xs: "flex-start", md: "center" }}
      mb={2}
      gap={2}
    >
      <Box>
        <Typography variant="h4" fontWeight={800}>
          Landing Page
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </Box>

      {isValidEventoId ? (
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          useFlexGap
          flexWrap="wrap"
          justifyContent="flex-end"
        >
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}/editar`}
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            size="small"
            sx={WIZARD_ACTION_BUTTON_SX}
          >
            Voltar (Evento)
          </Button>
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}/gamificacao`}
            variant="outlined"
            disabled={!config || loading || saving}
            size="small"
            sx={{ ...WIZARD_ACTION_BUTTON_SX, fontWeight: 800 }}
          >
            Próximo
          </Button>
          <Button
            variant="contained"
            disabled={!config || loading || saving}
            onClick={onSave}
            size="small"
            sx={{ ...WIZARD_ACTION_BUTTON_SX, fontWeight: 800 }}
          >
            {saving ? <CircularProgress size={22} color="inherit" /> : "Salvar"}
          </Button>
        </Stack>
      ) : null}
    </Stack>
  );
}
