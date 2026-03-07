import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

import type { GamificacaoPublic } from "../../services/landing_public";

type CommonViewProps = {
  gam: GamificacaoPublic;
};

type PresentingViewProps = CommonViewProps & {
  leadSubmitted: boolean;
  blockedReasonText: string | null;
  disabled: boolean;
  onParticipate: () => void;
};

type ActiveViewProps = CommonViewProps & {
  loading: boolean;
  error: string | null;
  onComplete: () => void;
};

type CompletedViewProps = CommonViewProps & {
  onReset: () => void;
  disableReset: boolean;
};

export function GamificacaoPresentingView({
  gam,
  leadSubmitted,
  blockedReasonText,
  disabled,
  onParticipate,
}: PresentingViewProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 3, md: 4 },
        borderRadius: 3,
        border: (t) => `1px solid ${alpha(t.palette.primary.main, 0.12)}`,
      }}
    >
      <Stack spacing={2.5}>
        <Typography variant="h5">{gam.nome}</Typography>

        <Typography variant="body1" color="text.secondary">
          {gam.descricao}
        </Typography>

        {gam.premio && (
          <Alert severity="info" icon={false}>
            <Typography variant="body2" fontWeight={700}>
              Premio: {gam.premio}
            </Typography>
          </Alert>
        )}

        {!leadSubmitted && blockedReasonText ? (
          <Typography
            variant="body2"
            color="text.secondary"
            role="status"
            sx={{ fontStyle: "italic" }}
          >
            {blockedReasonText}
          </Typography>
        ) : null}

        <Button
          size="large"
          variant="contained"
          onClick={onParticipate}
          disabled={disabled}
          aria-disabled={disabled}
          sx={{ minHeight: 48 }}
        >
          Quero participar
        </Button>
      </Stack>
    </Paper>
  );
}

export function GamificacaoActiveView({ gam, loading, error, onComplete }: ActiveViewProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 3, md: 4 },
        borderRadius: 3,
        border: (t) => `1px solid ${alpha(t.palette.primary.main, 0.12)}`,
      }}
    >
      <Stack spacing={2.5}>
        <Typography variant="h5">{gam.nome}</Typography>

        <Typography variant="body1" color="text.secondary">
          {gam.descricao}
        </Typography>

        {gam.premio && (
          <Alert severity="info" icon={false}>
            <Typography variant="body2" fontWeight={700}>
              Premio: {gam.premio}
            </Typography>
          </Alert>
        )}

        <Typography variant="body2" color="text.secondary">
          Participe da atividade e clique em &quot;Conclui&quot; ao finalizar.
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}

        <Button
          size="large"
          variant="contained"
          onClick={onComplete}
          disabled={loading}
          sx={{ minHeight: 48 }}
        >
          {loading ? <CircularProgress size={22} color="inherit" /> : "Conclui"}
        </Button>
      </Stack>
    </Paper>
  );
}

export function GamificacaoCompletedView({ gam, onReset, disableReset }: CompletedViewProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 3, md: 4 },
        borderRadius: 3,
        border: (t) => `1px solid ${alpha(t.palette.primary.main, 0.12)}`,
        textAlign: "center",
      }}
    >
      <Stack spacing={2.5} alignItems="center">
        <Box
          sx={{
            width: 56,
            height: 56,
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: (t) => alpha(t.palette.success.main, 0.12),
            color: "success.main",
            fontSize: 28,
          }}
        >
          &#10003;
        </Box>

        <Typography variant="h5">
          {gam.titulo_feedback || "Parabens!"}
        </Typography>

        <Typography variant="body1" color="text.secondary">
          {gam.texto_feedback || "Voce concluiu a gamificacao com sucesso."}
        </Typography>

        <Button variant="outlined" onClick={onReset} disabled={disableReset}>
          Nova pessoa
        </Button>
      </Stack>
    </Paper>
  );
}
