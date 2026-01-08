import { useEffect, useMemo, useState } from "react";
import { Alert, Box, Button, CircularProgress, Divider, Paper, Stack, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import EventWizardStepper from "../components/eventos/EventWizardStepper";
import { getEvento, getEventoQuestionario, type EventoRead, type QuestionarioEstrutura } from "../services/eventos";
import { useAuth } from "../store/auth";

function getApiErrorCode(err: unknown): string | null {
  const message = (err as any)?.message;
  if (typeof message != "string" || !message) return null;
  try {
    const parsed = JSON.parse(message);
    if (parsed && typeof parsed.code == "string") return parsed.code;
  } catch {
    // ignore
  }
  if (message.includes("EVENTO_NOT_FOUND")) return "EVENTO_NOT_FOUND";
  if (message.includes("FORBIDDEN")) return "FORBIDDEN";
  return null;
}

function getApiErrorMessage(err: unknown, fallback: string): string {
  const code = getApiErrorCode(err);
  if (code == "EVENTO_NOT_FOUND") return "Evento nao encontrado ou voce nao tem permissao para acessa-lo.";
  if (code == "FORBIDDEN") return "Voce nao tem permissao para realizar esta acao.";

  const message = (err as any)?.message;
  if (typeof message != "string" || !message.trim()) return fallback;
  if (message == "Failed to fetch") {
    return "Nao foi possivel conectar a API. Verifique se o backend esta rodando e se o CORS permite este endereco.";
  }

  try {
    const parsed = JSON.parse(message);
    if (parsed && typeof parsed.message == "string" && parsed.message.trim()) return parsed.message;
  } catch {
    // ignore
  }

  return message;
}

export default function EventQuestionario() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [questionario, setQuestionario] = useState<QuestionarioEstrutura | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfScope, setOutOfScope] = useState(false);

  useEffect(() => {
    if (!token || !isValidEventoId) {
      setEvento(null);
      setQuestionario(null);
      setError(null);
      setOutOfScope(false);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setQuestionario(null);

    Promise.all([getEvento(token, eventoId), getEventoQuestionario(token, eventoId)])
      .then(([eventoRes, questionarioRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setQuestionario(questionarioRes);
      })
      .catch((err: any) => {
        if (cancelled) return;
        const code = getApiErrorCode(err);
        if (code == "EVENTO_NOT_FOUND") setOutOfScope(true);
        setError(getApiErrorMessage(err, "Erro ao carregar questionario."));
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
    if (!isValidEventoId) return "Configure o questionario do evento.";
    if (evento?.nome) return `Configure o questionario do evento "${evento.nome}".`;
    return `Configure o questionario do evento #${eventoId}.`;
  }, [evento?.nome, eventoId, isValidEventoId]);

  const paginas = questionario?.paginas ?? [];
  const totalPerguntas = paginas.reduce((total, pagina) => total + pagina.perguntas.length, 0);
  const totalOpcoes = paginas.reduce(
    (total, pagina) => total + pagina.perguntas.reduce((sum, pergunta) => sum + pergunta.opcoes.length, 0),
    0,
  );

  return (
    <Box sx={{ width: "100%" }}>
      <EventWizardStepper activeStep={4} sx={{ mb: 2 }} />

      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Questionario
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {isValidEventoId ? (
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}/ativacoes`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: "none" }}
            >
              Voltar
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}`}
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 800 }}
            >
              Finalizar
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
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Estrutura do questionario
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {evento?.nome ? `Evento: ${evento.nome}` : `Evento #${eventoId}`}
              </Typography>
            </Box>

            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Paginas
                </Typography>
                <Typography variant="h6" fontWeight={800}>
                  {paginas.length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Perguntas
                </Typography>
                <Typography variant="h6" fontWeight={800}>
                  {totalPerguntas}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Opcoes
                </Typography>
                <Typography variant="h6" fontWeight={800}>
                  {totalOpcoes}
                </Typography>
              </Box>
            </Stack>

            <Divider />

            {paginas.length ? (
              <Stack spacing={1}>
                {paginas.map((pagina) => (
                  <Box key={pagina.id ?? `ordem-${pagina.ordem}`}>
                    <Typography variant="subtitle2" fontWeight={700}>
                      {pagina.ordem}. {pagina.titulo}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {pagina.perguntas.length} pergunta(s)
                    </Typography>
                  </Box>
                ))}
              </Stack>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Nenhuma pagina cadastrada.
              </Typography>
            )}
          </Stack>
        )}
      </Paper>
    </Box>
  );
}
