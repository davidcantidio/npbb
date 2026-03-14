import {
  Alert,
  Box,
  Button,
  CircularProgress,
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
    <Stack spacing={2.5}>
      <Typography component="h2" variant="h5">
        {gam.nome}
      </Typography>

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
  );
}

export function GamificacaoActiveView({ gam, loading, error, onComplete }: ActiveViewProps) {
  return (
    <Stack spacing={2.5}>
      <Typography component="h2" variant="h5">
        {gam.nome}
      </Typography>

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
  );
}

export function GamificacaoCompletedView({ gam, onReset, disableReset }: CompletedViewProps) {
  return (
    <Stack spacing={2.5} alignItems="center" sx={{ textAlign: "center" }}>
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

      <Typography component="h2" variant="h5">
        {gam.titulo_feedback || "Parabens!"}
      </Typography>

      <Typography variant="body1" color="text.secondary">
        {gam.texto_feedback || "Voce concluiu a gamificacao com sucesso."}
      </Typography>

      <Button variant="outlined" onClick={onReset} disabled={disableReset}>
        Nova pessoa
      </Button>
    </Stack>
  );
}
