import { useState } from "react";
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

import type {
  GamificacaoBlockProps,
  GamificacaoState,
} from "../../services/landing_public";

export default function GamificacaoBlock({
  gamificacoes,
  leadSubmitted,
  onComplete,
  onReset,
}: GamificacaoBlockProps) {
  const [state, setState] = useState<GamificacaoState>("presenting");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fallbackErrorMessage = "Nao foi possivel registrar a participacao. Tente novamente.";

  const gam = gamificacoes[0];
  if (!gam) return null;

  const handleParticipate = () => {
    if (!leadSubmitted) return;
    setState("active");
    setError(null);
  };

  const handleComplete = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.resolve(onComplete(gam.id));
      setState("completed");
    } catch (err) {
      if (err instanceof Error && err.message.trim()) {
        setError(err.message);
      } else {
        setError(fallbackErrorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setState("presenting");
    setError(null);
    onReset();
  };

  if (state === "completed") {
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

          <Button variant="outlined" onClick={handleReset}>
            Nova pessoa
          </Button>
        </Stack>
      </Paper>
    );
  }

  if (state === "active") {
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
            onClick={handleComplete}
            disabled={loading}
            sx={{ minHeight: 48 }}
          >
            {loading ? <CircularProgress size={22} color="inherit" /> : "Conclui"}
          </Button>
        </Stack>
      </Paper>
    );
  }

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

        {!leadSubmitted && (
          <Typography
            variant="body2"
            color="text.secondary"
            role="status"
            sx={{ fontStyle: "italic" }}
          >
            Preencha o cadastro acima para participar
          </Typography>
        )}

        <Button
          size="large"
          variant="contained"
          onClick={handleParticipate}
          disabled={!leadSubmitted}
          aria-disabled={!leadSubmitted}
          sx={{ minHeight: 48 }}
        >
          Quero participar
        </Button>
      </Stack>
    </Paper>
  );
}
