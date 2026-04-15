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
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import QuickCreateEventoModal from "../../components/QuickCreateEventoModal";
import { toApiErrorMessage } from "../../services/http";
import {
  ColumnConfidence,
  ColumnSuggestion,
  MapearBatchResult,
  ReferenciaEvento,
  getLeadBatchColunas,
  listReferenciaEventos,
  mapearLeadBatch,
} from "../../services/leads_import";
import { formatEventoLabel } from "../../utils/formatters";
import { useAuth } from "../../store/auth";

const QUICK_CREATE_ID = -1;
const EVENTOS_LOAD_ERROR = "Nao foi possivel carregar os eventos. Tente recarregar a pagina.";
const DERIVED_EVENT_FIELDS = ["evento", "tipo_evento", "local", "data_evento"] as const;

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
  "id_salesforce",
  "sobrenome",
  "sessao",
  "data_compra",
  "data_compra_data",
  "data_compra_hora",
  "opt_in",
  "opt_in_id",
  "opt_in_flag",
  "metodo_entrega",
  "rg",
  "endereco_rua",
  "endereco_numero",
  "complemento",
  "bairro",
  "cep",
  "cidade",
  "estado",
  "genero",
  "codigo_promocional",
  "ingresso_tipo",
  "ingresso_qtd",
  "fonte_origem",
  "is_cliente_bb",
  "is_cliente_estilo",
];

const CONFIDENCE_LABELS: Record<ColumnConfidence, string> = {
  exact_match: "Exato",
  synonym_match: "Sinonimo",
  alias_match: "Alias salvo",
  none: "Sem sugestao",
};

const CONFIDENCE_COLORS: Record<ColumnConfidence, "success" | "info" | "warning" | "default"> = {
  exact_match: "success",
  synonym_match: "info",
  alias_match: "warning",
  none: "default",
};

function isDerivedEventField(field: string | null | undefined) {
  return Boolean(field && DERIVED_EVENT_FIELDS.includes(field as (typeof DERIVED_EVENT_FIELDS)[number]));
}

function sanitizeMappedField(field: string | null | undefined, usesFixedEvento: boolean) {
  if (!field) return "";
  if (usesFixedEvento && isDerivedEventField(field)) {
    return "";
  }
  return field;
}

function sanitizeMappingRecord(mapping: Record<string, string>, usesFixedEvento: boolean) {
  const sanitized: Record<string, string> = {};
  for (const [coluna, campo] of Object.entries(mapping)) {
    const nextValue = sanitizeMappedField(campo, usesFixedEvento);
    if (nextValue) {
      sanitized[coluna] = nextValue;
    }
  }
  return sanitized;
}

export type MapeamentoPageProps = {
  batchId?: number;
  initialEventoId?: number | null;
  fixedEventoId?: number | null;
  onCancel?: () => void;
  onMapped?: (result: MapearBatchResult) => void;
};

export default function MapeamentoPage({
  batchId: batchIdProp,
  initialEventoId = null,
  fixedEventoId = null,
  onCancel,
  onMapped,
}: MapeamentoPageProps = {}) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const batchId = batchIdProp ?? Number(searchParams.get("batch_id") ?? "0");

  const fixedEvento = fixedEventoId != null && Number.isFinite(fixedEventoId) ? Number(fixedEventoId) : null;
  const usesFixedEvento = fixedEvento != null;

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
  const eventoPrefillAppliedForBatchRef = useRef<number | null>(null);

  useEffect(() => {
    eventoPrefillAppliedForBatchRef.current = null;
    if (usesFixedEvento) {
      setEventoId(fixedEvento);
      setEventoInputValue("");
      return;
    }
    setEventoId("");
    setEventoInputValue("");
  }, [batchId, fixedEvento, usesFixedEvento]);

  useEffect(() => {
    if (usesFixedEvento || !batchId || initialEventoId == null || !Number.isFinite(initialEventoId)) return;
    if (eventoPrefillAppliedForBatchRef.current === batchId) return;
    const evento = eventos.find((item) => item.id === initialEventoId);
    if (!evento) return;
    setEventoId(initialEventoId);
    setEventoInputValue(formatEventoLabel(evento.nome, evento.data_inicio_prevista));
    eventoPrefillAppliedForBatchRef.current = batchId;
  }, [batchId, eventos, initialEventoId, usesFixedEvento]);

  useEffect(() => {
    if (!token || !batchId) return;

    setLoadingColunas(true);
    getLeadBatchColunas(token, batchId)
      .then((data) => {
        setColunas(data.colunas);
        const initial: Record<string, string> = {};
        for (const col of data.colunas) {
          initial[col.coluna_original] = sanitizeMappedField(col.campo_sugerido, usesFixedEvento);
        }
        setMapeamento(initial);
      })
      .catch((err) => setError(toApiErrorMessage(err, "Falha ao carregar colunas do lote.")))
      .finally(() => setLoadingColunas(false));

    if (usesFixedEvento) {
      setEventos([]);
      setEventosError(null);
      setLoadingEventos(false);
      return;
    }

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
  }, [batchId, token, usesFixedEvento]);

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

  const resolvedEventoId = usesFixedEvento ? fixedEvento : typeof eventoId === "number" ? eventoId : null;
  const availableCanonicalFields = useMemo(
    () => CANONICAL_FIELDS.filter((field) => !(usesFixedEvento && isDerivedEventField(field))),
    [usesFixedEvento],
  );
  const sanitizedMapeamento = useMemo(
    () => sanitizeMappingRecord(mapeamento, usesFixedEvento),
    [mapeamento, usesFixedEvento],
  );

  const canConfirm = useMemo(() => {
    if (!resolvedEventoId || submitting) return false;
    return Object.values(sanitizedMapeamento).some((value) => value !== "");
  }, [resolvedEventoId, sanitizedMapeamento, submitting]);

  const handleConfirm = async () => {
    if (!token || !resolvedEventoId) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await mapearLeadBatch(token, batchId, {
        evento_id: resolvedEventoId,
        mapeamento: sanitizedMapeamento,
      });
      if (!Number.isFinite(res.batch_id) || res.batch_id <= 0) {
        throw new Error("Resposta de confirmacao nao retornou batch_id.");
      }
      if (onMapped) {
        onMapped(res);
      } else {
        setResult({ silver_count: res.silver_count });
        navigate(`/leads/pipeline?batch_id=${res.batch_id}`);
      }
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao confirmar mapeamento."));
    } finally {
      setSubmitting(false);
    }
  };

  if (!batchId) {
    return <Alert severity="error">batch_id ausente. Acesse esta pagina a partir do fluxo de importacao.</Alert>;
  }

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Mapeamento de Colunas
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Lote #{batchId} - confirme o mapeamento das colunas para os campos canonicos.
          </Typography>
        </Box>
      </Stack>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      {result ? (
        <Paper elevation={1} sx={{ p: 3, borderRadius: 3 }}>
          <Stack spacing={2} alignItems="center" textAlign="center">
            <CheckCircleOutlineIcon color="success" sx={{ fontSize: 56 }} />
            <Typography variant="h6" fontWeight={700}>
              Mapeamento concluido!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {result.silver_count} linha{result.silver_count !== 1 ? "s" : ""} persistida
              {result.silver_count !== 1 ? "s" : ""} na camada Silver.
            </Typography>
            <Stack direction="row" spacing={2} justifyContent="center">
              <Button variant="outlined" onClick={() => navigate("/leads/importar")}>
                Nova Importacao
              </Button>
            </Stack>
          </Stack>
        </Paper>
      ) : (
        <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
          <Stack spacing={3}>
            {!usesFixedEvento ? (
              <Box>
                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Evento de referencia
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
                    getOptionLabel={(evento) => formatEventoLabel(evento.nome, evento.data_inicio_prevista)}
                    filterOptions={(options, state) => {
                      const filtered = options.filter((evento) =>
                        formatEventoLabel(evento.nome, evento.data_inicio_prevista)
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
                    value={eventoId ? (eventos.find((evento) => evento.id === eventoId) ?? null) : null}
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
                    renderInput={(params) => <TextField {...params} placeholder="Selecione ou pesquise o evento..." />}
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
            ) : null}

            <Box>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Mapeamento de colunas
              </Typography>
              {usesFixedEvento ? (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Com evento fixo, evento, tipo_evento, local e data_evento serao derivados automaticamente do
                  cadastro do evento selecionado. Nao e necessario mapea-los no arquivo.
                </Alert>
              ) : null}
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
                        <TableCell sx={{ fontWeight: 700 }}>Sugestao automatica</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Campo canonico</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {colunas.map((coluna) => (
                        <TableRow key={coluna.coluna_original} hover>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {coluna.coluna_original}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={CONFIDENCE_LABELS[coluna.confianca]}
                              color={CONFIDENCE_COLORS[coluna.confianca]}
                              size="small"
                              variant="outlined"
                            />
                            {coluna.campo_sugerido ? (
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                -&gt;{" "}
                                {usesFixedEvento && isDerivedEventField(coluna.campo_sugerido)
                                  ? "Derivado do evento"
                                  : coluna.campo_sugerido}
                              </Typography>
                            ) : null}
                          </TableCell>
                          <TableCell>
                            <Select
                              value={sanitizeMappedField(mapeamento[coluna.coluna_original], usesFixedEvento)}
                              onChange={(event) =>
                                setMapeamento((prev) => ({
                                  ...prev,
                                  [coluna.coluna_original]: event.target.value as string,
                                }))
                              }
                              displayEmpty
                              size="small"
                              sx={{ minWidth: 180 }}
                            >
                              <MenuItem value="">
                                <em>Ignorar coluna</em>
                              </MenuItem>
                              {availableCanonicalFields.map((field) => (
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

            <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
              <Button
                variant="outlined"
                onClick={() => {
                  if (onCancel) {
                    onCancel();
                  } else {
                    navigate("/leads/importar");
                  }
                }}
                disabled={submitting}
              >
                Cancelar
              </Button>
              <Button variant="contained" disabled={!canConfirm} onClick={handleConfirm}>
                {submitting ? <CircularProgress size={18} color="inherit" /> : "Confirmar Mapeamento"}
              </Button>
            </Stack>
          </Stack>
        </Paper>
      )}

      {!usesFixedEvento ? (
        <QuickCreateEventoModal
          open={isQuickCreateOpen}
          onClose={() => setIsQuickCreateOpen(false)}
          onCreated={handleEventoCreated}
        />
      ) : null}
    </Box>
  );
}
