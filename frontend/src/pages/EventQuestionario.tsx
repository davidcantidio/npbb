import { useEffect, useMemo, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  FormControlLabel,
  IconButton,
  MenuItem,
  Paper,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
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

const PERGUNTA_TIPO_OPTIONS = [
  { value: "aberta_texto_simples", label: "Texto curto" },
  { value: "aberta_texto_area", label: "Texto longo" },
  { value: "objetiva_unica", label: "Unica escolha" },
  { value: "objetiva_multipla", label: "Multipla escolha" },
  { value: "data", label: "Data" },
  { value: "avaliacao", label: "Avaliacao" },
  { value: "numerica", label: "Numerica" },
] as const;

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
  const [novaPerguntaTipo, setNovaPerguntaTipo] = useState<string>(PERGUNTA_TIPO_OPTIONS[0].value);

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
  const selectedPergunta =
    selectedPagina?.perguntas.find((pergunta) => pergunta.id === selectedPerguntaId) ?? null;

  useEffect(() => {
    if (!selectedPaginaId) {
      if (selectedPerguntaId !== null) setSelectedPerguntaId(null);
      return;
    }
    const pagina = editorPaginas.find((item) => item.id === selectedPaginaId);
    if (!pagina || pagina.perguntas.length === 0) {
      if (selectedPerguntaId !== null) setSelectedPerguntaId(null);
      return;
    }
    const exists = pagina.perguntas.some((pergunta) => pergunta.id === selectedPerguntaId);
    if (!exists) setSelectedPerguntaId(pagina.perguntas[0].id);
  }, [editorPaginas, selectedPaginaId, selectedPerguntaId]);
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
  const handlePaginaFieldChange = (paginaId: EditorId, field: "titulo" | "descricao", value: string) => {
    setEditorPaginas((prev) =>
      prev.map((pagina) => (pagina.id === paginaId ? { ...pagina, [field]: value } : pagina)),
    );
  };
  const handleDeletePagina = (paginaId: EditorId) => {
    const pagina = editorPaginas.find((item) => item.id === paginaId);
    const label = pagina?.titulo?.trim() ? ` "${pagina.titulo.trim()}"` : "";
    if (!window.confirm(`Excluir pagina${label}? Esta acao remove suas perguntas.`)) return;

    const index = editorPaginas.findIndex((item) => item.id === paginaId);
    const nextPaginas = editorPaginas.filter((item) => item.id !== paginaId);
    setEditorPaginas(nextPaginas);

    if (paginaId !== selectedPaginaId) {
      return;
    }

    const fallback = nextPaginas[index] ?? nextPaginas[index - 1] ?? null;
    setSelectedPaginaId(fallback?.id ?? null);
    setSelectedPerguntaId(fallback?.perguntas[0]?.id ?? null);
  };
  const handleMovePagina = (paginaId: EditorId, direction: "up" | "down") => {
    setEditorPaginas((prev) => {
      const index = prev.findIndex((item) => item.id === paginaId);
      if (index < 0) return prev;
      const targetIndex = direction === "up" ? index - 1 : index + 1;
      if (targetIndex < 0 || targetIndex >= prev.length) return prev;

      const next = [...prev];
      const [moved] = next.splice(index, 1);
      next.splice(targetIndex, 0, moved);
      return next.map((pagina, idx) => ({ ...pagina, ordem: idx + 1 }));
    });
  };
  const handleAddPergunta = () => {
    if (!selectedPaginaId) return;
    const newId = nextTempId();
    setEditorPaginas((prev) =>
      prev.map((pagina) => {
        if (pagina.id !== selectedPaginaId) return pagina;
        const maxOrdem = pagina.perguntas.reduce((max, pergunta) => Math.max(max, pergunta.ordem || 0), 0);
        const ordem = maxOrdem + 1;
        return {
          ...pagina,
          perguntas: [
            ...pagina.perguntas,
            {
              id: newId,
              ordem,
              tipo: novaPerguntaTipo,
              texto: `Pergunta ${ordem}`,
              obrigatoria: false,
              opcoes: [],
            },
          ],
        };
      }),
    );
    setSelectedPerguntaId(newId);
  };
  const handlePerguntaFieldChange = <K extends keyof EditorPergunta>(
    paginaId: EditorId,
    perguntaId: EditorId,
    field: K,
    value: EditorPergunta[K],
  ) => {
    setEditorPaginas((prev) =>
      prev.map((pagina) => {
        if (pagina.id !== paginaId) return pagina;
        return {
          ...pagina,
          perguntas: pagina.perguntas.map((pergunta) =>
            pergunta.id === perguntaId ? { ...pergunta, [field]: value } : pergunta,
          ),
        };
      }),
    );
  };
  const handleDeletePergunta = (paginaId: EditorId, perguntaId: EditorId) => {
    const pagina = editorPaginas.find((item) => item.id === paginaId);
    const pergunta = pagina?.perguntas.find((item) => item.id === perguntaId);
    const label = pergunta?.texto?.trim() ? ` "${pergunta.texto.trim()}"` : "";
    if (!window.confirm(`Excluir pergunta${label}? Esta acao remove suas opcoes.`)) return;

    const index = pagina?.perguntas.findIndex((item) => item.id === perguntaId) ?? -1;
    const nextPaginas = editorPaginas.map((item) => {
      if (item.id !== paginaId) return item;
      return {
        ...item,
        perguntas: item.perguntas.filter((perg) => perg.id !== perguntaId),
      };
    });
    setEditorPaginas(nextPaginas);

    if (selectedPerguntaId !== perguntaId) return;
    const updatedPagina = nextPaginas.find((item) => item.id === paginaId);
    if (!updatedPagina || updatedPagina.perguntas.length === 0) {
      setSelectedPerguntaId(null);
      return;
    }
    const fallback =
      updatedPagina.perguntas[index] ?? updatedPagina.perguntas[index - 1] ?? updatedPagina.perguntas[0];
    setSelectedPerguntaId(fallback.id);
  };
  const handleMovePergunta = (paginaId: EditorId, perguntaId: EditorId, direction: "up" | "down") => {
    setEditorPaginas((prev) =>
      prev.map((pagina) => {
        if (pagina.id !== paginaId) return pagina;
        const index = pagina.perguntas.findIndex((item) => item.id === perguntaId);
        if (index < 0) return pagina;
        const targetIndex = direction === "up" ? index - 1 : index + 1;
        if (targetIndex < 0 || targetIndex >= pagina.perguntas.length) return pagina;

        const nextPerguntas = [...pagina.perguntas];
        const [moved] = nextPerguntas.splice(index, 1);
        nextPerguntas.splice(targetIndex, 0, moved);

        return {
          ...pagina,
          perguntas: nextPerguntas.map((pergunta, idx) => ({ ...pergunta, ordem: idx + 1 })),
        };
      }),
    );
  };
  const getPerguntaTipoLabel = (tipo: string) => {
    switch (tipo) {
      case "aberta_texto_simples":
        return "Texto curto";
      case "aberta_texto_area":
        return "Texto longo";
      case "objetiva_unica":
        return "Unica escolha";
      case "objetiva_multipla":
        return "Multipla escolha";
      case "data":
        return "Data";
      case "avaliacao":
        return "Avaliacao";
      case "numerica":
        return "Numerica";
      default:
        return tipo;
    }
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
                    {paginas.map((pagina, index) => {
                      const isSelected = pagina.id === selectedPaginaId;
                      return (
                        <Stack key={pagina.id ?? `ordem-${pagina.ordem}`} direction="row" alignItems="center" spacing={1}>
                          <Button
                            variant={isSelected ? "contained" : "text"}
                            color={isSelected ? "primary" : "inherit"}
                            onClick={() => setSelectedPaginaId(pagina.id)}
                            sx={{
                              textTransform: "none",
                              justifyContent: "flex-start",
                              fontWeight: isSelected ? 800 : 500,
                              flex: 1,
                            }}
                          >
                            {pagina.ordem}. {pagina.titulo}
                          </Button>
                          <Stack direction="row" spacing={0.5}>
                            <IconButton
                              size="small"
                              onClick={() => handleMovePagina(pagina.id, "up")}
                              disabled={index === 0}
                              aria-label="Mover pagina para cima"
                            >
                              <ArrowUpwardIcon fontSize="inherit" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleMovePagina(pagina.id, "down")}
                              disabled={index === paginas.length - 1}
                              aria-label="Mover pagina para baixo"
                            >
                              <ArrowDownwardIcon fontSize="inherit" />
                            </IconButton>
                          </Stack>
                        </Stack>
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
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                  <Typography variant="subtitle2" fontWeight={800}>
                    Pagina selecionada
                  </Typography>
                  {selectedPagina ? (
                    <Button
                      size="small"
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteOutlineIcon />}
                      onClick={() => handleDeletePagina(selectedPagina.id)}
                      sx={{ textTransform: "none", fontWeight: 700 }}
                    >
                      Excluir pagina
                    </Button>
                  ) : null}
                </Stack>

                {selectedPagina ? (
                  <Stack spacing={2}>
                    <TextField
                      label="Titulo da pagina"
                      required
                      value={selectedPagina.titulo}
                      onChange={(event) =>
                        handlePaginaFieldChange(selectedPagina.id, "titulo", event.target.value)
                      }
                      error={!selectedPagina.titulo.trim()}
                      helperText={!selectedPagina.titulo.trim() ? "Titulo obrigatorio." : " "}
                    />
                    <TextField
                      label="Descricao da pagina"
                      value={selectedPagina.descricao ?? ""}
                      onChange={(event) =>
                        handlePaginaFieldChange(selectedPagina.id, "descricao", event.target.value)
                      }
                      multiline
                      minRows={2}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Ordem: {selectedPagina.ordem} - Perguntas: {selectedPagina.perguntas.length}
                    </Typography>
                    <Divider />
                    <Box>
                      <Typography variant="subtitle2" fontWeight={800} gutterBottom>
                        Perguntas
                      </Typography>
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        spacing={1}
                        alignItems={{ xs: "stretch", sm: "center" }}
                        mb={2}
                      >
                        <TextField
                          select
                          label="Tipo da pergunta"
                          value={novaPerguntaTipo}
                          onChange={(event) => setNovaPerguntaTipo(event.target.value)}
                          sx={{ minWidth: 220 }}
                        >
                          {PERGUNTA_TIPO_OPTIONS.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </TextField>
                        <Button
                          variant="contained"
                          startIcon={<AddIcon />}
                          onClick={handleAddPergunta}
                          sx={{ textTransform: "none", fontWeight: 700 }}
                        >
                          Adicionar pergunta
                        </Button>
                      </Stack>
                      {selectedPagina.perguntas.length ? (
                        <Stack spacing={1}>
                          {selectedPagina.perguntas.map((pergunta, index) => {
                            const isSelected = pergunta.id === selectedPerguntaId;
                            const isFirst = index === 0;
                            const isLast = index === selectedPagina.perguntas.length - 1;
                            return (
                              <Box
                                key={pergunta.id ?? `ordem-${pergunta.ordem}`}
                                onClick={() => setSelectedPerguntaId(pergunta.id)}
                                sx={{
                                  border: "1px solid",
                                  borderColor: isSelected ? "primary.main" : "divider",
                                  borderRadius: 2,
                                  p: 1.5,
                                  cursor: "pointer",
                                  backgroundColor: isSelected ? "action.selected" : "transparent",
                                }}
                              >
                                <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
                                  <Box>
                                    <Typography variant="body2" fontWeight={700}>
                                      {pergunta.ordem}. {pergunta.texto || "Sem texto"}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      Tipo: {getPerguntaTipoLabel(pergunta.tipo)} -{" "}
                                      {pergunta.obrigatoria ? "Obrigatoria" : "Opcional"}
                                    </Typography>
                                  </Box>
                                  <Stack direction="row" spacing={0.5}>
                                    <IconButton
                                      size="small"
                                      onClick={(event) => {
                                        event.stopPropagation();
                                        handleMovePergunta(selectedPagina.id, pergunta.id, "up");
                                      }}
                                      disabled={isFirst}
                                      aria-label="Mover pergunta para cima"
                                    >
                                      <ArrowUpwardIcon fontSize="inherit" />
                                    </IconButton>
                                    <IconButton
                                      size="small"
                                      onClick={(event) => {
                                        event.stopPropagation();
                                        handleMovePergunta(selectedPagina.id, pergunta.id, "down");
                                      }}
                                      disabled={isLast}
                                      aria-label="Mover pergunta para baixo"
                                    >
                                      <ArrowDownwardIcon fontSize="inherit" />
                                    </IconButton>
                                  </Stack>
                                </Stack>
                              </Box>
                            );
                          })}
                        </Stack>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Nenhuma pergunta cadastrada.
                        </Typography>
                      )}
                      {selectedPagina.perguntas.length ? (
                        <>
                          <Divider sx={{ my: 2 }} />
                          {selectedPergunta ? (
                            <Stack spacing={2}>
                              <Stack direction="row" alignItems="center" justifyContent="space-between">
                                <Typography variant="subtitle2" fontWeight={800}>
                                  Editar pergunta
                                </Typography>
                                <Button
                                  size="small"
                                  variant="outlined"
                                  color="error"
                                  startIcon={<DeleteIcon />}
                                  onClick={() => handleDeletePergunta(selectedPagina.id, selectedPergunta.id)}
                                  sx={{ textTransform: "none", fontWeight: 700 }}
                                >
                                  Excluir pergunta
                                </Button>
                              </Stack>
                              <TextField
                                label="Texto da pergunta"
                                required
                                value={selectedPergunta.texto}
                                onChange={(event) =>
                                  handlePerguntaFieldChange(
                                    selectedPagina.id,
                                    selectedPergunta.id,
                                    "texto",
                                    event.target.value,
                                  )
                                }
                              />
                              <TextField
                                select
                                label="Tipo da pergunta"
                                value={selectedPergunta.tipo}
                                onChange={(event) =>
                                  handlePerguntaFieldChange(
                                    selectedPagina.id,
                                    selectedPergunta.id,
                                    "tipo",
                                    event.target.value,
                                  )
                                }
                              >
                                {PERGUNTA_TIPO_OPTIONS.map((option) => (
                                  <MenuItem key={option.value} value={option.value}>
                                    {option.label}
                                  </MenuItem>
                                ))}
                              </TextField>
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={selectedPergunta.obrigatoria}
                                    onChange={(event) =>
                                      handlePerguntaFieldChange(
                                        selectedPagina.id,
                                        selectedPergunta.id,
                                        "obrigatoria",
                                        event.target.checked,
                                      )
                                    }
                                  />
                                }
                                label="Obrigatoria"
                              />
                            </Stack>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              Selecione uma pergunta para editar.
                            </Typography>
                          )}
                        </>
                      ) : null}
                    </Box>
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
