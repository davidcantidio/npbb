import { useEffect, useMemo, useState } from "react";
import { Alert, Box, Button, CircularProgress, Paper, Stack, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../components/eventos/EventWizardStepper";
import { getEvento, type EventoRead } from "../services/eventos";
import { useAuth } from "../store/auth";

export default function EventGamificacao() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;
  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    getEvento(token, eventoId)
      .then((data) => {
        if (cancelled) return;
        setEvento(data);
      })
      .catch((err: any) => {
        if (cancelled) return;
        setError(err?.message || "Erro ao carregar evento.");
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, eventoId, isValidEventoId]);

  const subtitle = useMemo(() => {
    if (!isValidEventoId) return "Evento inválido.";
    if (evento?.nome) return `Configure as gamificações do evento "${evento.nome}" (#${eventoId}).`;
    return `Configure as gamificações do evento #${eventoId}.`;
  }, [evento?.nome, eventoId, isValidEventoId]);

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={2} sx={{ mb: 2 }} />

      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Gamificação
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {isValidEventoId ? (
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/formulario-lead`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: "none" }}
            >
              Voltar
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/ativacoes`}
              variant="contained"
              disabled={loading}
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Próximo
            </Button>
          </Stack>
        ) : null}
      </Stack>

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Em breve.
          </Typography>
        )}
      </Paper>
    </Box>
  );
}

