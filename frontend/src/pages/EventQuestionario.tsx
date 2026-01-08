import { useEffect, useMemo, useRef, useState } from "react";
import { Alert, Box, Button, CircularProgress, Divider, Paper, Stack, Typography } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
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

type EditorId = string;

type EditorOpcao = {
  id: EditorId;
  ordem: number;
  texto: string;
};

type EditorPergunta = {
  id: EditorId;
  ordem: number;
  tipo: string;
  texto: string;
  obrigatoria: boolean;
  opcoes: EditorOpcao[];
};

type EditorPagina = {
  id: EditorId;
  ordem: number;
  titulo: string;
  descricao?: string | null;
  perguntas: EditorPergunta[];
};

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
  const [editorPaginas, setEditorPaginas] = useState<EditorPagina[]>([]);
  const [selectedPaginaId, setSelectedPaginaId] = useState<EditorId | null>(null);
  const [selectedPerguntaId, setSelectedPerguntaId] = useState<EditorId | null>(null);

  const tempIdRef = useRef(0);
  const nextTempId = () => {
    tempIdRef.current += 1;
    return `tmp-${tempIdRef.current}`;
  };

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

  useEffect(() => {
    if (!questionario) {
      setEditorPaginas([]);
      setSelectedPaginaId(null);
      setSelectedPerguntaId(null);
      return;
    }

    const mappedPaginas = questionario.paginas.map((pagina) => {
      const paginaId = typeof pagina.id == "number" ? String(pagina.id) : nextTempId();
      const perguntas = pagina.perguntas.map((pergunta) => {
        const perguntaId = typeof pergunta.id == "number" ? String(pergunta.id) : nextTempId();
        const opcoes = pergunta.opcoes.map((opcao) => ({
          id: typeof opcao.id == "number" ? String(opcao.id) : nextTempId(),
          ordem: opcao.ordem,
          texto: opcao.texto,
        }));
        return {
          id: perguntaId,
          ordem: pergunta.ordem,
          tipo: pergunta.tipo,
          texto: pergunta.texto,
          obrigatoria: pergunta.obrigatoria,
          opcoes,
        };
      });
      return {
        id: paginaId,
        ordem: pagina.ordem,
        titulo: pagina.titulo,
        descricao: pagina.descricao ?? null,
        perguntas,
      };
    });

    setEditorPaginas(mappedPaginas);
    setSelectedPaginaId(mappedPaginas[0]?.id ?? null);
    setSelectedPerguntaId(mappedPaginas[0]?.perguntas[0]?.id ?? null);
  }, [questionario]);

  const subtitle = useMemo(() => {
    if (!isValidEventoId) return "Configure o questionario do evento.";
    if (evento?.nome) return `Configure o questionario do evento "${evento.nome}".`;
    return `Configure o questionario do evento #${eventoId}.`;
  }, [evento?.nome, eventoId, isValidEventoId]);

  const paginas = editorPaginas;
  const selectedPagina = paginas.find((pagina) => pagina.id === selectedPaginaId) ?? null;
  const handleAddPagina = () => {
    const newId = nextTempId();
    setEditorPaginas((prev) => {
      const maxOrdem = prev.reduce((max, pagina) => Math.max(max, pagina.ordem || 0), 0);
      const ordem = maxOrdem + 1;
      return [
        ...prev,
        {
          id: newId,
          ordem,
          titulo: `Pagina ${ordem}`,
          descricao: null,
          perguntas: [],
        },
      ];
    });
    setSelectedPaginaId(newId);
    setSelectedPerguntaId(null);
  };

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

            <Divider />

            <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="stretch">
              <Paper
                variant="outlined"
                sx={{ p: 2, width: { xs: "100%", md: 260 }, flexShrink: 0 }}
              >
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                  <Typography variant="subtitle2" fontWeight={800}>
                    Estrutura
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={handleAddPagina}
                    sx={{ textTransform: "none", fontWeight: 700 }}
                  >
                    Nova pagina
                  </Button>
                </Stack>

                {paginas.length ? (
                  <Stack spacing={1}>
                    {paginas.map((pagina) => {
                      const isSelected = pagina.id === selectedPaginaId;
                      return (
                        <Button
                          key={pagina.id ?? `ordem-${pagina.ordem}`}
                          variant={isSelected ? "contained" : "text"}
                          color={isSelected ? "primary" : "inherit"}
                          onClick={() => setSelectedPaginaId(pagina.id)}
                          sx={{
                            textTransform: "none",
                            justifyContent: "flex-start",
                            fontWeight: isSelected ? 800 : 500,
                          }}
                        >
                          {pagina.ordem}. {pagina.titulo}
                        </Button>
                      );
                    })}
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Nenhuma pagina cadastrada.
                  </Typography>
                )}
              </Paper>

              <Paper variant="outlined" sx={{ p: 2, flex: 1 }}>
                <Typography variant="subtitle2" fontWeight={800} gutterBottom>
                  Pagina selecionada
                </Typography>

                {selectedPagina ? (
                  <Stack spacing={1}>
                    <Typography variant="body1" fontWeight={700}>
                      {selectedPagina.ordem}. {selectedPagina.titulo}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedPagina.descricao || "Sem descricao"}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedPagina.perguntas.length} pergunta(s)
                    </Typography>
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Selecione uma pagina para editar.
                  </Typography>
                )}
              </Paper>
            </Stack>
          </Stack>
        )}
      </Paper>
    </Box>
  );
}
