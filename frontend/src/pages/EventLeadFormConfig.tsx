import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import { getEventoFormConfig, type EventoFormConfig } from "../services/eventos";
import { useAuth } from "../store/auth";

export default function EventLeadFormConfig() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const [config, setConfig] = useState<EventoFormConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getEventoFormConfig(token, eventoId);
      setConfig(data);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar configuração do formulário");
    } finally {
      setLoading(false);
    }
  }, [token, eventoId]);

  useEffect(() => {
    load();
  }, [load]);

  const subtitle = Number.isFinite(eventoId)
    ? `Configure o tema e os campos do formulário do evento #${eventoId}.`
    : "Configure o tema e os campos do formulário do evento.";

  return (
    <Box sx={{ width: "100%" }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Formulário de Lead
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {Number.isFinite(eventoId) ? (
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}`}
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            sx={{ textTransform: "none" }}
          >
            Voltar ao evento
          </Button>
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
        ) : config ? (
          <Stack spacing={1}>
            <Typography variant="subtitle1" fontWeight={900}>
              Placeholder
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Em breve: seleção de tema, campos e URLs geradas.
            </Typography>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Nenhum dado para exibir.
          </Typography>
        )}
      </Paper>
    </Box>
  );
}

