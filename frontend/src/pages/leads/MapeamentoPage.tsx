import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import {
  Alert,
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
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { toApiErrorMessage } from "../../services/http";
import {
  ColumnConfidence,
  ColumnSuggestion,
  getLeadBatchColunas,
  listReferenciaEventos,
  mapearLeadBatch,
} from "../../services/leads_import";
import { useAuth } from "../../store/auth";

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
  const [eventos, setEventos] = useState<Array<{ id: number; nome: string }>>([]);
  const [eventoId, setEventoId] = useState<number | "">("");

  const [loadingColunas, setLoadingColunas] = useState(false);
  const [loadingEventos, setLoadingEventos] = useState(false);
  const [submitting, setSubmitting] = useState(false);
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
    listReferenciaEventos(token)
      .then(setEventos)
      .catch(() => setEventos([]))
      .finally(() => setLoadingEventos(false));
  }, [token, batchId]);

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
      setResult({ silver_count: res.silver_count });
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
              {loadingEventos ? (
                <CircularProgress size={20} />
              ) : (
                <Select
                  value={eventoId}
                  onChange={(e) => setEventoId(e.target.value as number)}
                  displayEmpty
                  fullWidth
                  sx={{ maxWidth: 480 }}
                >
                  <MenuItem value="" disabled>
                    Selecione o evento...
                  </MenuItem>
                  {eventos.map((ev) => (
                    <MenuItem key={ev.id} value={ev.id}>
                      {ev.nome}
                    </MenuItem>
                  ))}
                </Select>
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
    </Box>
  );
}
