import { useEffect, useMemo, useState } from "react";
import { Alert, Box, Button, CircularProgress, Paper, Stack, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../components/eventos/EventWizardStepper";
import {
  getEvento,
  listEventoAtivacoes,
  listEventoGamificacoes,
  type Ativacao,
  type EventoRead,
  type Gamificacao,
} from "../services/eventos";
import { useAuth } from "../store/auth";

function getApiErrorCode(err: unknown): string | null {
  const message = (err as any)?.message;
  if (typeof message !== "string" || !message) return null;
  try {
    const parsed = JSON.parse(message);
    if (parsed && typeof parsed.code === "string") return parsed.code;
  } catch {
    // ignore
  }
  if (message.includes("EVENTO_NOT_FOUND")) return "EVENTO_NOT_FOUND";
  if (message.includes("FORBIDDEN")) return "FORBIDDEN";
  return null;
}

function getApiErrorMessage(err: unknown, fallback: string): string {
  const code = getApiErrorCode(err);
  if (code === "EVENTO_NOT_FOUND") return "Evento nao encontrado ou voce nao tem permissao para acessa-lo.";
  if (code === "FORBIDDEN") return "Voce nao tem permissao para realizar esta acao.";

  const message = (err as any)?.message;
  if (typeof message !== "string" || !message.trim()) return fallback;
  if (message === "Failed to fetch") {
    return "Nao foi possivel conectar a API. Verifique se o backend esta rodando e se o CORS permite este endereco.";
  }

  try {
    const parsed = JSON.parse(message);
    if (parsed && typeof parsed.message === "string" && parsed.message.trim()) return parsed.message;
  } catch {
    // ignore
  }

  return message;
}

export default function EventAtivacoes() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [ativacoes, setAtivacoes] = useState<Ativacao[]>([]);
  const [gamificacoes, setGamificacoes] = useState<Gamificacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfScope, setOutOfScope] = useState(false);

  const subtitle = useMemo(() => {
    if (!isValidEventoId) return "Configure as ativacoes do evento.";
    if (evento?.nome) return `Configure as ativacoes do evento "${evento.nome}".`;
    return `Configure as ativacoes do evento #${eventoId}.`;
  }, [evento?.nome, eventoId, isValidEventoId]);

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setAtivacoes([]);
    setGamificacoes([]);

    Promise.all([
      getEvento(token, eventoId),
      listEventoAtivacoes(token, eventoId),
      listEventoGamificacoes(token, eventoId),
    ])
      .then(([eventoRes, ativacoesRes, gamificacoesRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setAtivacoes(ativacoesRes);
        setGamificacoes(gamificacoesRes);
      })
      .catch((err: any) => {
        if (cancelled) return;
        const code = getApiErrorCode(err);
        if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
        setError(getApiErrorMessage(err, "Erro ao carregar ativacoes."));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, eventoId, isValidEventoId]);

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={3} sx={{ mb: 2 }} />

      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Ativações
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {isValidEventoId ? (
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/gamificacao`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: "none" }}
            >
              Voltar
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/questionario`}
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Próximo
            </Button>
          </Stack>
        ) : null}
      </Stack>

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {!token ? (
          <Alert severity="warning">Voce precisa estar autenticado para acessar esta pagina.</Alert>
        ) : !isValidEventoId ? (
          <Alert severity="warning">Evento invalido.</Alert>
        ) : outOfScope ? (
          <Alert severity="warning">Evento nao encontrado ou fora do seu escopo.</Alert>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : loading ? (
          <Box sx={{ py: 2, display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Box>
        ) : (
          <Stack spacing={1}>
            <Typography variant="subtitle1" fontWeight={900}>
              Dados carregados
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Evento: {evento?.nome ?? `#${eventoId}`}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ativacoes: {ativacoes.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Gamificacoes: {gamificacoes.length}
            </Typography>
          </Stack>
        )}
      </Paper>
    </Box>
  );
}
