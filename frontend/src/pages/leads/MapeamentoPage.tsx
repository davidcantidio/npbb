import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Chip,
  CircularProgress,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import QuickCreateEventoModal from "../../components/QuickCreateEventoModal";
import { toApiErrorMessage } from "../../services/http";
import {
  ColumnConfidence,
  ColumnSuggestion,
  ReferenciaEvento,
  getLeadBatchColunas,
  listReferenciaEventos,
  mapearLeadBatch,
} from "../../services/leads_import";
import { formatEventoLabel } from "../../utils/formatters";
import { useAuth } from "../../store/auth";

/** Synthetic option id used to trigger the quick-create modal. */
const QUICK_CREATE_ID = -1;
const EVENTOS_LOAD_ERROR = "Não foi possível carregar os eventos. Tente recarregar a página.";

const CANONICAL_FIELDS = [
  "nome",
  "cpf",
  "data_nascimento",
  "email",
  "telefone",
  "evento",
  "tipo_evento",
  "local",
  "data_evento",
];

const CONFIDENCE_LABELS: Record<ColumnConfidence, string> = {
  exact_match: "Exato",
  synonym_match: "Sinônimo",
  alias_match: "Alias salvo",
  none: "Sem sugestão",
};

const CONFIDENCE_COLORS: Record<ColumnConfidence, "success" | "info" | "warning" | "default"> = {
  exact_match: "success",
  synonym_match: "info",
  alias_match: "warning",
  none: "default",
};

export default function MapeamentoPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const batchId = Number(searchParams.get("batch_id") ?? "0");

  const [colunas, setColunas] = useState<ColumnSuggestion[]>([]);
  const [mapeamento, setMapeamento] = useState<Record<string, string>>({});
  const [eventos, setEventos] = useState<ReferenciaEvento[]>([]);
  const [eventoId, setEventoId] = useState<number | "">("");
  const [eventoInputValue, setEventoInputValue] = useState("");
  const [isQuickCreateOpen, setIsQuickCreateOpen] = useState(false);

  const [loadingColunas, setLoadingColunas] = useState(false);
  const [loadingEventos, setLoadingEventos] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [eventosError, setEventosError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ silver_count: number } | null>(null);

  useEffect(() => {
    if (!token || !batchId) return;

    setLoadingColunas(true);
    getLeadBatchColunas(token, batchId)
      .then((data) => {
        setColunas(data.colunas);
        const initial: Record<string, string> = {};
        for (const col of data.colunas) {
          initial[col.coluna_original] = col.campo_sugerido ?? "";
        }
        setMapeamento(initial);
      })
      .catch((err) => setError(toApiErrorMessage(err, "Falha ao carregar colunas do lote.")))
      .finally(() => setLoadingColunas(false));

    setLoadingEventos(true);
    setEventosError(null);
    listReferenciaEventos(token)
      .then((data) => {
        setEventos(data);
        setEventosError(null);
      })
      .catch(() => {
        setEventos([]);
        setEventosError(EVENTOS_LOAD_ERROR);
      })
      .finally(() => setLoadingEventos(false));
  }, [token, batchId]);

  const handleEventoCreated = useCallback(
    (created: { id: number; nome: string; data_inicio_prevista?: string | null }) => {
      const newRef: ReferenciaEvento = {
        id: created.id,
        nome: created.nome,
        data_inicio_prevista: created.data_inicio_prevista ?? null,
      };
      setEventos((prev) => [newRef, ...prev]);
      setEventoId(created.id);
      setEventoInputValue(formatEventoLabel(created.nome, created.data_inicio_prevista ?? null));
      setIsQuickCreateOpen(false);
    },
    [],
  );

  const canConfirm = useMemo(() => {
    if (!eventoId || submitting) return false;
    const hasMapped = Object.values(mapeamento).some((v) => v !== "");
    return hasMapped;
  }, [eventoId, mapeamento, submitting]);

  const handleConfirm = async () => {
    if (!token || !eventoId) return;
    setSubmitting(true);
    setError(null);
    try {
      const activeMapeamento: Record<string, string> = {};
      for (const [col, campo] of Object.entries(mapeamento)) {
        if (campo) activeMapeamento[col] = campo;
      }
      const res = await mapearLeadBatch(token, batchId, {
        evento_id: Number(eventoId),
        mapeamento: activeMapeamento,
      });
      if (!Number.isFinite(res.batch_id) || res.batch_id <= 0) {
        throw new Error("Resposta de confirmação não retornou batch_id.");
      }
      setResult({ silver_count: res.silver_count });
      navigate(`/leads/pipeline?batch_id=${res.batch_id}`);
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao confirmar mapeamento."));
    } finally {
      setSubmitting(false);
    }
  };

  if (!batchId) {
    return (
      <Alert severity="error">
        batch_id ausente. Acesse esta página a partir do fluxo de importação.
      </Alert>
    );
  }

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Mapeamento de Colunas
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Lote #{batchId} — confirme o mapeamento das colunas para os campos canônicos.
          </Typography>
        </Box>
      </Stack>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      {result ? (
        <Paper elevation={1} sx={{ p: 3, borderRadius: 3 }}>
          <Stack spacing={2} alignItems="center" textAlign="center">
            <CheckCircleOutlineIcon color="success" sx={{ fontSize: 56 }} />
            <Typography variant="h6" fontWeight={700}>
              Mapeamento concluído!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {result.silver_count} linha{result.silver_count !== 1 ? "s" : ""} persistida
              {result.silver_count !== 1 ? "s" : ""} na camada Silver.
            </Typography>
            <Stack direction="row" spacing={2} justifyContent="center">
              <Button variant="outlined" onClick={() => navigate("/leads/importar")}>
                Nova Importação
              </Button>
            </Stack>
          </Stack>
        </Paper>
      ) : (
        <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
          <Stack spacing={3}>
            {/* Seleção de Evento */}
            <Box>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Evento de referência
              </Typography>
              {eventosError ? (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setEventosError(null)}>
                  {eventosError}
                </Alert>
              ) : null}
              {loadingEventos ? (
                <CircularProgress size={20} />
              ) : (
                <Autocomplete<ReferenciaEvento, false, false, false>
                  options={eventos}
                  getOptionLabel={(ev) => formatEventoLabel(ev.nome, ev.data_inicio_prevista)}
                  filterOptions={(options, state) => {
                    const filtered = options.filter((o) =>
                      formatEventoLabel(o.nome, o.data_inicio_prevista)
                        .toLowerCase()
                        .includes(state.inputValue.toLowerCase()),
                    );
                    if (filtered.length === 0 || state.inputValue.trim()) {
                      filtered.push({
                        id: QUICK_CREATE_ID,
                        nome: "+ Criar evento rapidamente",
                        data_inicio_prevista: null,
                      });
                    }
                    return filtered;
                  }}
                  value={eventoId ? (eventos.find((e) => e.id === eventoId) ?? null) : null}
                  inputValue={eventoInputValue}
                  onInputChange={(_, value) => setEventoInputValue(value)}
                  onChange={(_, selected) => {
                    if (!selected) {
                      setEventoId("");
                      return;
                    }
                    if (selected.id === QUICK_CREATE_ID) {
                      setIsQuickCreateOpen(true);
                      return;
                    }
                    setEventoId(selected.id);
                  }}
                  sx={{ maxWidth: 480 }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      placeholder="Selecione ou pesquise o evento..."
                    />
                  )}
                  renderOption={(props, option) => (
                    <MenuItem
                      {...props}
                      key={option.id}
                      sx={option.id === QUICK_CREATE_ID ? { color: "primary.main", fontStyle: "italic" } : undefined}
                    >
                      {option.id === QUICK_CREATE_ID
                        ? option.nome
                        : formatEventoLabel(option.nome, option.data_inicio_prevista)}
                    </MenuItem>
                  )}
                />
              )}
            </Box>

            {/* Tabela de Mapeamento */}
            <Box>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Mapeamento de colunas
              </Typography>
              {loadingColunas ? (
                <Box sx={{ py: 3, display: "flex", justifyContent: "center" }}>
                  <CircularProgress size={28} />
                </Box>
              ) : colunas.length === 0 ? (
                <Alert severity="warning">Nenhuma coluna detectada no lote.</Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700 }}>Coluna original</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Sugestão automática</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Campo canônico</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {colunas.map((col) => (
                        <TableRow key={col.coluna_original} hover>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {col.coluna_original}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={CONFIDENCE_LABELS[col.confianca]}
                              color={CONFIDENCE_COLORS[col.confianca]}
                              size="small"
                              variant="outlined"
                            />
                            {col.campo_sugerido ? (
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ ml: 1 }}
                              >
                                → {col.campo_sugerido}
                              </Typography>
                            ) : null}
                          </TableCell>
                          <TableCell>
                            <Select
                              value={mapeamento[col.coluna_original] ?? ""}
                              onChange={(e) =>
                                setMapeamento((prev) => ({
                                  ...prev,
                                  [col.coluna_original]: e.target.value as string,
                                }))
                              }
                              displayEmpty
                              size="small"
                              sx={{ minWidth: 180 }}
                            >
                              <MenuItem value="">
                                <em>Ignorar coluna</em>
                              </MenuItem>
                              {CANONICAL_FIELDS.map((field) => (
                                <MenuItem key={field} value={field}>
                                  {field}
                                </MenuItem>
                              ))}
                            </Select>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>

            {/* Ações */}
            <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
              <Button
                variant="outlined"
                onClick={() => navigate(`/leads/importar`)}
                disabled={submitting}
              >
                Cancelar
              </Button>
              <Button
                variant="contained"
                disabled={!canConfirm}
                onClick={handleConfirm}
              >
                {submitting ? (
                  <CircularProgress size={18} color="inherit" />
                ) : (
                  "Confirmar Mapeamento"
                )}
              </Button>
            </Stack>
          </Stack>
        </Paper>
      )}

      <QuickCreateEventoModal
        open={isQuickCreateOpen}
        onClose={() => setIsQuickCreateOpen(false)}
        onCreated={handleEventoCreated}
      />
    </Box>
  );
}
