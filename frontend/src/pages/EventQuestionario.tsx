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

import EventWizardPageShell, {
  WIZARD_ACTION_BUTTON_SX,
} from "../components/eventos/EventWizardPageShell";
import EventWizardStepper from "../components/eventos/EventWizardStepper";
import WizardTwoColumnLayout from "../components/eventos/WizardTwoColumnLayout";
import {
  getEvento,
  getEventoQuestionario,
  updateEventoQuestionario,
  type EventoRead,
  type QuestionarioEstrutura,
} from "../services/eventos";
import { getEventApiErrorCode, getEventApiErrorMessage } from "../services/http_event_messages";
import { useAuth } from "../store/auth";

function getApiErrorCode(err: unknown): string | null {
  return getEventApiErrorCode(err);
}

function getApiErrorMessage(err: unknown, fallback: string): string {
  return getEventApiErrorMessage(err, fallback);
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

type PerguntaValidation = {
  texto?: string;
  opcoes?: string;
  opcaoTextos?: Record<EditorId, string>;
};

type PaginaValidation = {
  titulo?: string;
  perguntas: Record<EditorId, PerguntaValidation>;
};

type QuestionarioValidation = {
  hasErrors: boolean;
  paginas: Record<EditorId, PaginaValidation>;
};

const PERGUNTA_TIPO_OPTIONS = [
  { value: "aberta_texto_simples", label: "Aberta texto simples" },
  { value: "aberta_texto_area", label: "Aberta area de texto" },
  { value: "objetiva_unica", label: "Objetiva unica escolha" },
  { value: "objetiva_multipla", label: "Objetiva multipla escolha" },
  { value: "data", label: "Data" },
  { value: "avaliacao", label: "Avaliacao" },
  { value: "numerica", label: "Numerica" },
] as const;

const isPerguntaObjetiva = (tipo: string) => tipo === "objetiva_unica" || tipo === "objetiva_multipla";

const validateQuestionario = (paginas: EditorPagina[]): QuestionarioValidation => {
  let hasErrors = false;
  const paginasErrors: Record<EditorId, PaginaValidation> = {};

  paginas.forEach((pagina) => {
    const paginaErrors: PaginaValidation = { perguntas: {} };
    if (!pagina.titulo.trim()) {
      paginaErrors.titulo = "Titulo obrigatorio.";
      hasErrors = true;
    }

    pagina.perguntas.forEach((pergunta) => {
      const perguntaErrors: PerguntaValidation = {};
      if (!pergunta.texto.trim()) {
        perguntaErrors.texto = "Texto obrigatorio.";
        hasErrors = true;
      }
      if (isPerguntaObjetiva(pergunta.tipo)) {
        if (pergunta.opcoes.length === 0) {
          perguntaErrors.opcoes = "Adicione pelo menos uma opcao.";
          hasErrors = true;
        }
        const opcaoTextos: Record<EditorId, string> = {};
        pergunta.opcoes.forEach((opcao) => {
          if (!opcao.texto.trim()) {
            opcaoTextos[opcao.id] = "Opcao obrigatoria.";
            hasErrors = true;
          }
        });
        if (Object.keys(opcaoTextos).length) {
          perguntaErrors.opcaoTextos = opcaoTextos;
        }
      }
      if (Object.keys(perguntaErrors).length) {
        paginaErrors.perguntas[pergunta.id] = perguntaErrors;
      }
    });

    if (paginaErrors.titulo || Object.keys(paginaErrors.perguntas).length) {
      paginasErrors[pagina.id] = paginaErrors;
    }
  });

  return { hasErrors, paginas: paginasErrors };
};

export default function EventQuestionario() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [questionario, setQuestionario] = useState<QuestionarioEstrutura | null>(null);
  const [loading, setLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveFeedback, setSaveFeedback] = useState<{ severity: "success" | "error"; message: string } | null>(
    null,
  );
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
      setIsSaving(false);
      setSaveFeedback(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setQuestionario(null);
    setIsSaving(false);
    setSaveFeedback(null);

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
  const disableActions = isSaving;
  const validation = useMemo(() => validateQuestionario(editorPaginas), [editorPaginas]);
  const selectedPaginaErrors = selectedPagina ? validation.paginas[selectedPagina.id] : undefined;
  const selectedPerguntaErrors =
    selectedPagina && selectedPergunta ? selectedPaginaErrors?.perguntas[selectedPergunta.id] : undefined;
  const disableSave = disableActions || validation.hasErrors;

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
  const handleAddOpcao = (paginaId: EditorId, perguntaId: EditorId) => {
    const newId = nextTempId();
    setEditorPaginas((prev) =>
      prev.map((pagina) => {
        if (pagina.id !== paginaId) return pagina;
        return {
          ...pagina,
          perguntas: pagina.perguntas.map((pergunta) => {
            if (pergunta.id !== perguntaId) return pergunta;
            const maxOrdem = pergunta.opcoes.reduce((max, opcao) => Math.max(max, opcao.ordem || 0), 0);
            const ordem = maxOrdem + 1;
            return {
              ...pergunta,
              opcoes: [
                ...pergunta.opcoes,
                {
                  id: newId,
                  ordem,
                  texto: `Opcao ${ordem}`,
                },
              ],
            };
          }),
        };
      }),
    );
  };
  const handleOpcaoFieldChange = (paginaId: EditorId, perguntaId: EditorId, opcaoId: EditorId, value: string) => {
    setEditorPaginas((prev) =>
      prev.map((pagina) => {
        if (pagina.id !== paginaId) return pagina;
        return {
          ...pagina,
          perguntas: pagina.perguntas.map((pergunta) => {
            if (pergunta.id !== perguntaId) return pergunta;
            return {
              ...pergunta,
              opcoes: pergunta.opcoes.map((opcao) => (opcao.id === opcaoId ? { ...opcao, texto: value } : opcao)),
            };
          }),
        };
      }),
    );
  };
  const handleDeleteOpcao = (paginaId: EditorId, perguntaId: EditorId, opcaoId: EditorId) => {
    const pagina = editorPaginas.find((item) => item.id === paginaId);
    const pergunta = pagina?.perguntas.find((item) => item.id === perguntaId);
    const opcao = pergunta?.opcoes.find((item) => item.id === opcaoId);
    const label = opcao?.texto?.trim() ? ` "${opcao.texto.trim()}"` : "";
    if (!window.confirm(`Excluir opcao${label}?`)) return;

    setEditorPaginas((prev) =>
      prev.map((paginaItem) => {
        if (paginaItem.id !== paginaId) return paginaItem;
        return {
          ...paginaItem,
          perguntas: paginaItem.perguntas.map((perguntaItem) => {
            if (perguntaItem.id !== perguntaId) return perguntaItem;
            const remaining = perguntaItem.opcoes.filter((item) => item.id !== opcaoId);
            return {
              ...perguntaItem,
              opcoes: remaining.map((item, idx) => ({ ...item, ordem: idx + 1 })),
            };
          }),
        };
      }),
    );
  };
  const handleMoveOpcao = (paginaId: EditorId, perguntaId: EditorId, opcaoId: EditorId, direction: "up" | "down") => {
    setEditorPaginas((prev) =>
      prev.map((paginaItem) => {
        if (paginaItem.id !== paginaId) return paginaItem;
        return {
          ...paginaItem,
          perguntas: paginaItem.perguntas.map((perguntaItem) => {
            if (perguntaItem.id !== perguntaId) return perguntaItem;
            const index = perguntaItem.opcoes.findIndex((item) => item.id === opcaoId);
            if (index < 0) return perguntaItem;
            const targetIndex = direction === "up" ? index - 1 : index + 1;
            if (targetIndex < 0 || targetIndex >= perguntaItem.opcoes.length) return perguntaItem;
            const nextOpcoes = [...perguntaItem.opcoes];
            const [moved] = nextOpcoes.splice(index, 1);
            nextOpcoes.splice(targetIndex, 0, moved);
            return {
              ...perguntaItem,
              opcoes: nextOpcoes.map((item, idx) => ({ ...item, ordem: idx + 1 })),
            };
          }),
        };
      }),
    );
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
  const buildQuestionarioPayload = () => ({
    paginas: editorPaginas.map((pagina, paginaIndex) => ({
      ordem: paginaIndex + 1,
      titulo: pagina.titulo,
      descricao: pagina.descricao ?? null,
      perguntas: pagina.perguntas.map((pergunta, perguntaIndex) => ({
        ordem: perguntaIndex + 1,
        tipo: pergunta.tipo,
        texto: pergunta.texto,
        obrigatoria: pergunta.obrigatoria,
        opcoes: pergunta.opcoes.map((opcao, opcaoIndex) => ({
          ordem: opcaoIndex + 1,
          texto: opcao.texto,
        })),
      })),
    })),
  });
  const handleSave = async () => {
    if (!token || !isValidEventoId || isSaving) return;
    if (validation.hasErrors) {
      setSaveFeedback({
        severity: "error",
        message: "Existem campos obrigatorios pendentes. Revise os erros antes de salvar.",
      });
      return;
    }
    setIsSaving(true);
    setSaveFeedback(null);
    try {
      const payload = buildQuestionarioPayload();
      const saved = await updateEventoQuestionario(token, eventoId, payload);
      setQuestionario(saved);
      setSaveFeedback({ severity: "success", message: "Questionario salvo com sucesso." });
    } catch (err) {
      setSaveFeedback({ severity: "error", message: getApiErrorMessage(err, "Erro ao salvar questionario.") });
    } finally {
      setIsSaving(false);
    }
  };
  const getPerguntaTipoLabel = (tipo: string) => {
    switch (tipo) {
      case "aberta_texto_simples":
        return "Aberta texto simples";
      case "aberta_texto_area":
        return "Aberta area de texto";
      case "objetiva_unica":
        return "Objetiva unica escolha";
      case "objetiva_multipla":
        return "Objetiva multipla escolha";
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
    <EventWizardPageShell width="wide" testId="event-questionario-shell">
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
              to={`/eventos/${eventoId}/ativacoes`}
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              disabled={disableActions}
              size="small"
              sx={WIZARD_ACTION_BUTTON_SX}
            >
              Voltar
            </Button>
            <Button
              component={RouterLink}
              to={`/eventos/${eventoId}`}
              variant="contained"
              disabled={disableActions}
              size="small"
              sx={{ ...WIZARD_ACTION_BUTTON_SX, fontWeight: 800 }}
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
            <Stack
              direction={{ xs: "column", sm: "row" }}
              alignItems={{ xs: "flex-start", sm: "center" }}
              justifyContent="space-between"
              gap={2}
            >
              <Box>
                <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                  Estrutura do questionario
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {evento?.nome ? `Evento: ${evento.nome}` : `Evento #${eventoId}`}
                </Typography>
              </Box>
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={disableSave}
                size="small"
                sx={{ ...WIZARD_ACTION_BUTTON_SX, fontWeight: 800 }}
              >
                {isSaving ? "Salvando..." : "Salvar"}
              </Button>
            </Stack>

            {saveFeedback ? (
              <Alert
                severity={saveFeedback.severity}
                onClose={() => setSaveFeedback(null)}
                sx={{ mt: -1 }}
              >
                {saveFeedback.message}
              </Alert>
            ) : null}

            <Divider />

            <WizardTwoColumnLayout
              testId="event-questionario-layout"
              leftTestId="event-questionario-editor-column"
              rightTestId="event-questionario-structure-column"
              desktopColumns="minmax(0, 1fr) 260px"
              leftContent={(
                <Paper variant="outlined" sx={{ p: 2, width: "100%" }}>
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                  <Typography variant="subtitle2" fontWeight={800}>
                    {selectedPagina ? `Pagina ${selectedPagina.ordem}` : "Pagina"}
                  </Typography>
                  {selectedPagina ? (
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeletePagina(selectedPagina.id)}
                      disabled={disableActions}
                      aria-label="Excluir pagina"
                    >
                      <DeleteOutlineIcon fontSize="small" />
                    </IconButton>
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
                      error={Boolean(selectedPaginaErrors?.titulo)}
                      helperText={selectedPaginaErrors?.titulo ?? " "}
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
                    <Divider />
                    <Box>
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        spacing={1}
                        alignItems={{ xs: "stretch", sm: "center" }}
                        mb={2}
                      >
                        <TextField
                          select
                          label="Incluir pergunta"
                          value={novaPerguntaTipo}
                          onChange={(event) => setNovaPerguntaTipo(event.target.value)}
                          sx={{ flex: 1 }}
                        >
                          {PERGUNTA_TIPO_OPTIONS.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </TextField>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={handleAddPergunta}
                          disabled={disableActions}
                          aria-label="Adicionar pergunta"
                          sx={{ alignSelf: { xs: "flex-end", sm: "center" } }}
                        >
                          <AddIcon fontSize="small" />
                        </IconButton>
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
                                      disabled={disableActions || isFirst}
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
                                      disabled={disableActions || isLast}
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
                                  disabled={disableActions}
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
                                error={Boolean(selectedPerguntaErrors?.texto)}
                                helperText={selectedPerguntaErrors?.texto ?? " "}
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
                              {isPerguntaObjetiva(selectedPergunta.tipo) ? (
                                <Box>
                                  <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                                    <Typography variant="subtitle2" fontWeight={800}>
                                      Opcoes
                                    </Typography>
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      startIcon={<AddIcon />}
                                      onClick={() => handleAddOpcao(selectedPagina.id, selectedPergunta.id)}
                                      disabled={disableActions}
                                      sx={{ textTransform: "none", fontWeight: 700 }}
                                    >
                                      Adicionar opcao
                                    </Button>
                                  </Stack>
                                  {selectedPerguntaErrors?.opcoes ? (
                                    <Typography variant="caption" color="error" display="block" mb={1}>
                                      {selectedPerguntaErrors.opcoes}
                                    </Typography>
                                  ) : null}
                                  {selectedPergunta.opcoes.length ? (
                                    <Stack spacing={1}>
                                      {selectedPergunta.opcoes.map((opcao, index) => {
                                        const isFirst = index === 0;
                                        const isLast = index === selectedPergunta.opcoes.length - 1;
                                        return (
                                        <Stack
                                          key={opcao.id ?? `ordem-${opcao.ordem}`}
                                          direction={{ xs: "column", sm: "row" }}
                                          spacing={1}
                                          alignItems={{ xs: "stretch", sm: "center" }}
                                        >
                                          <TextField
                                            label={`Opcao ${opcao.ordem}`}
                                            value={opcao.texto}
                                            onChange={(event) =>
                                              handleOpcaoFieldChange(
                                                selectedPagina.id,
                                                selectedPergunta.id,
                                                opcao.id,
                                                event.target.value,
                                              )
                                            }
                                            error={Boolean(selectedPerguntaErrors?.opcaoTextos?.[opcao.id])}
                                            helperText={selectedPerguntaErrors?.opcaoTextos?.[opcao.id] ?? " "}
                                            fullWidth
                                          />
                                          <Stack direction="row" spacing={0.5}>
                                            <IconButton
                                              aria-label="Mover opcao para cima"
                                              onClick={() =>
                                                handleMoveOpcao(selectedPagina.id, selectedPergunta.id, opcao.id, "up")
                                              }
                                              disabled={disableActions || isFirst}
                                            >
                                              <ArrowUpwardIcon fontSize="inherit" />
                                            </IconButton>
                                            <IconButton
                                              aria-label="Mover opcao para baixo"
                                              onClick={() =>
                                                handleMoveOpcao(selectedPagina.id, selectedPergunta.id, opcao.id, "down")
                                              }
                                              disabled={disableActions || isLast}
                                            >
                                              <ArrowDownwardIcon fontSize="inherit" />
                                            </IconButton>
                                            <IconButton
                                              color="error"
                                              aria-label="Excluir opcao"
                                              onClick={() =>
                                                handleDeleteOpcao(selectedPagina.id, selectedPergunta.id, opcao.id)
                                              }
                                              disabled={disableActions}
                                            >
                                              <DeleteOutlineIcon />
                                            </IconButton>
                                          </Stack>
                                        </Stack>
                                      );
                                      })}
                                    </Stack>
                                  ) : (
                                    <Typography variant="body2" color="text.secondary">
                                      Nenhuma opcao cadastrada.
                                    </Typography>
                                  )}
                                </Box>
                              ) : null}
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
              )}
              rightContent={(
                <Paper variant="outlined" sx={{ p: 2, width: "100%" }}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                    <Typography variant="subtitle2" fontWeight={800}>
                      Estrutura
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={handleAddPagina}
                      disabled={disableActions}
                      aria-label="Adicionar pagina"
                    >
                      <AddIcon fontSize="small" />
                    </IconButton>
                  </Stack>

                  {paginas.length ? (
                    <Stack spacing={1}>
                      {paginas.map((pagina, index) => {
                        const isSelected = pagina.id === selectedPaginaId;
                        return (
                          <Stack key={pagina.id ?? `ordem-${pagina.ordem}`} direction="row" alignItems="center" spacing={1}>
                            <Button
                              variant="text"
                              color="inherit"
                              onClick={() => setSelectedPaginaId(pagina.id)}
                              disabled={disableActions}
                              sx={{
                                textTransform: "none",
                                justifyContent: "flex-start",
                                fontWeight: isSelected ? 800 : 500,
                                flex: 1,
                                backgroundColor: isSelected ? "action.selected" : "transparent",
                              }}
                            >
                              {pagina.ordem} - {pagina.titulo}
                            </Button>
                            <Stack direction="row" spacing={0.5}>
                              <IconButton
                                size="small"
                                onClick={() => handleMovePagina(pagina.id, "up")}
                                disabled={disableActions || index === 0}
                                aria-label="Mover pagina para cima"
                              >
                                <ArrowUpwardIcon fontSize="inherit" />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleMovePagina(pagina.id, "down")}
                                disabled={disableActions || index === paginas.length - 1}
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
              )}
            />
          </Stack>
        )}
      </Paper>
    </EventWizardPageShell>
  );
}
