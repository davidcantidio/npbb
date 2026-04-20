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
import { useNavigate } from "react-router-dom";

import { toApiErrorCode, toApiErrorMessage } from "../../services/http";
import {
  BatchColumnGroup,
  ColumnConfidence,
  LeadBatch,
  MapearLotesBatchResult,
  getLeadBatchColunasBatch,
  mapearLeadBatches,
} from "../../services/leads_import";
import { reconcileLeadMappingTimeout } from "../../services/leads_mapping_recovery";
import { useAuth } from "../../store/auth";

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

function sanitizeMappedField(field: string | null | undefined) {
  if (!field) return "";
  if (isDerivedEventField(field)) {
    return "";
  }
  return field;
}

function sanitizeMappingRecord(mapping: Record<string, string>) {
  const sanitized: Record<string, string> = {};
  for (const [coluna, campo] of Object.entries(mapping)) {
    const nextValue = sanitizeMappedField(campo);
    if (nextValue) {
      sanitized[coluna] = nextValue;
    }
  }
  return sanitized;
}

function formatSamples(samples: string[]) {
  if (samples.length === 0) return "sem amostras";
  return samples.join(", ");
}

export type BatchMapeamentoPageProps = {
  batchIds: number[];
  primaryBatchId?: number | null;
  onCancel?: () => void;
  onMapped?: (result: MapearLotesBatchResult) => void;
  cancelLabel?: string;
};

function buildRecoveredBatchMappingResult(
  resolvedBatchIds: number[],
  recoveredBatches: LeadBatch[],
  primaryBatchId: number | null,
): MapearLotesBatchResult {
  const batchesById = new Map(recoveredBatches.map((batch) => [batch.id, batch]));
  const orderedBatches = resolvedBatchIds
    .map((batchId) => batchesById.get(batchId))
    .filter((batch): batch is LeadBatch => batch != null);
  const resolvedPrimaryBatchId = primaryBatchId ?? orderedBatches[0]?.id ?? resolvedBatchIds[0] ?? 0;

  return {
    batch_ids: orderedBatches.map((batch) => batch.id),
    primary_batch_id: resolvedPrimaryBatchId,
    total_silver_count: 0,
    results: orderedBatches.map((batch) => ({
      batch_id: batch.id,
      silver_count: 0,
      stage: batch.stage,
    })),
    stage: orderedBatches.every((batch) => batch.stage === "gold") ? "gold" : "silver",
  };
}

export default function BatchMapeamentoPage({
  batchIds,
  primaryBatchId = null,
  onCancel,
  onMapped,
  cancelLabel = "Voltar ao batch",
}: BatchMapeamentoPageProps) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const resolvedBatchIds = useMemo(() => {
    const uniqueIds: number[] = [];
    const seen = new Set<number>();
    const preferredIds = primaryBatchId != null ? [primaryBatchId, ...batchIds] : batchIds;

    preferredIds.forEach((rawBatchId) => {
      const batchId = Number(rawBatchId);
      if (!Number.isFinite(batchId) || batchId <= 0 || seen.has(batchId)) return;
      seen.add(batchId);
      uniqueIds.push(batchId);
    });

    return uniqueIds;
  }, [batchIds, primaryBatchId]);

  const [colunas, setColunas] = useState<BatchColumnGroup[]>([]);
  const [aggregationRule, setAggregationRule] = useState("");
  const [warnings, setWarnings] = useState<string[]>([]);
  const [blockers, setBlockers] = useState<string[]>([]);
  const [blockedBatchIds, setBlockedBatchIds] = useState<number[]>([]);
  const [mapeamento, setMapeamento] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MapearLotesBatchResult | null>(null);
  const [recoveryState, setRecoveryState] = useState<"idle" | "recovering" | "failed">("idle");
  const [recoveryMessage, setRecoveryMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token || resolvedBatchIds.length === 0) return;

    setLoading(true);
    setError(null);
    getLeadBatchColunasBatch(token, resolvedBatchIds)
      .then((data) => {
        setColunas(data.colunas);
        setAggregationRule(data.aggregation_rule);
        setWarnings(data.warnings);
        setBlockers(data.blockers);
        setBlockedBatchIds(data.blocked_batch_ids);
        const initial: Record<string, string> = {};
        data.colunas.forEach((coluna) => {
          initial[coluna.chave_agregada] = sanitizeMappedField(coluna.campo_sugerido);
        });
        setMapeamento(initial);
      })
      .catch((err) => {
        setError(toApiErrorMessage(err, "Falha ao carregar o mapeamento unificado do batch."));
      })
      .finally(() => setLoading(false));
  }, [resolvedBatchIds, token]);

  const availableCanonicalFields = useMemo(
    () => CANONICAL_FIELDS.filter((field) => !isDerivedEventField(field)),
    [],
  );
  const fallbackBatchId = blockedBatchIds[0] ?? primaryBatchId ?? resolvedBatchIds[0] ?? null;
  const sanitizedMapeamento = useMemo(() => sanitizeMappingRecord(mapeamento), [mapeamento]);
  const isRecovering = recoveryState === "recovering";
  const canConfirm = useMemo(() => {
    if (submitting || isRecovering || blockers.length > 0) return false;
    return Object.values(sanitizedMapeamento).some((value) => value !== "");
  }, [blockers.length, isRecovering, sanitizedMapeamento, submitting]);

  const completeRecoveredMapping = (recoveredBatches: LeadBatch[]) => {
    const response = buildRecoveredBatchMappingResult(resolvedBatchIds, recoveredBatches, primaryBatchId);
    if (onMapped) {
      onMapped(response);
      return;
    }
    navigate(`/leads/pipeline?batch_id=${response.primary_batch_id}`);
  };

  const runTimeoutRecovery = async () => {
    if (!token || resolvedBatchIds.length === 0) {
      return false;
    }

    setError(null);
    setRecoveryState("recovering");
    setRecoveryMessage(null);

    try {
      const recovery = await reconcileLeadMappingTimeout(token, resolvedBatchIds);
      if (recovery.status === "mapped") {
        setRecoveryState("idle");
        completeRecoveredMapping(recovery.batches);
        return true;
      }

      setRecoveryState("failed");
      setRecoveryMessage(
        "A confirmacao excedeu o tempo limite da requisicao, mas o backend ainda nao confirmou todos os lotes como mapeados. Reverifique o status antes de reenviar.",
      );
      return false;
    } catch (err) {
      setRecoveryState("idle");
      setError(toApiErrorMessage(err, "Falha ao reverificar o status do mapeamento batch."));
      return false;
    }
  };

  const handleConfirm = async () => {
    if (!token || resolvedBatchIds.length === 0) return;
    setSubmitting(true);
    setError(null);
    setRecoveryState("idle");
    setRecoveryMessage(null);
    try {
      const response = await mapearLeadBatches(token, {
        batch_ids: resolvedBatchIds,
        mapeamento: sanitizedMapeamento,
      });
      if (!Number.isFinite(response.primary_batch_id) || response.primary_batch_id <= 0) {
        throw new Error("Resposta de confirmacao nao retornou primary_batch_id.");
      }
      if (onMapped) {
        onMapped(response);
        return;
      }
      setResult(response);
      navigate(`/leads/pipeline?batch_id=${response.primary_batch_id}`);
    } catch (err) {
      if (toApiErrorCode(err) === "TIMEOUT") {
        await runTimeoutRecovery();
        return;
      }
      setError(toApiErrorMessage(err, "Falha ao confirmar o mapeamento unificado do batch."));
    } finally {
      setSubmitting(false);
    }
  };

  if (resolvedBatchIds.length === 0) {
    return <Alert severity="error">Nenhum lote elegivel foi informado para o mapeamento batch.</Alert>;
  }

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Mapeamento Unificado do Batch
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Aplique um unico mapeamento aos {resolvedBatchIds.length} lote(s) pendente(s) deste batch.
          </Typography>
        </Box>
      </Stack>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {isRecovering ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          A confirmacao excedeu o tempo limite da requisicao. Verificando automaticamente se o backend concluiu o
          mapeamento do batch.
        </Alert>
      ) : null}
      {recoveryState === "failed" && recoveryMessage ? (
        <Alert
          severity="warning"
          sx={{ mb: 2 }}
          action={
            <Button color="inherit" size="small" onClick={() => void runTimeoutRecovery()}>
              Reverificar status do batch
            </Button>
          }
        >
          {recoveryMessage}
        </Alert>
      ) : null}

      {result ? (
        <Paper elevation={1} sx={{ p: 3, borderRadius: 3 }}>
          <Stack spacing={2} alignItems="center" textAlign="center">
            <CheckCircleOutlineIcon color="success" sx={{ fontSize: 56 }} />
            <Typography variant="h6" fontWeight={700}>
              Mapeamento batch concluido!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {result.results.length} lote(s) atualizado(s), com {result.total_silver_count} linha(s) na camada Silver.
            </Typography>
            <Button variant="outlined" onClick={() => navigate("/leads/importar")}>
              Nova Importacao
            </Button>
          </Stack>
        </Paper>
      ) : (
        <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
          <Stack spacing={3}>
            <Alert severity="info">
              Campos do evento (`evento`, `tipo_evento`, `local`, `data_evento`) continuam sendo derivados do cadastro
              do evento em cada lote e nao entram no mapeamento manual do batch.
            </Alert>

            {aggregationRule ? (
              <Alert severity="info">
                Regra de agregacao de colunas: <strong>{aggregationRule}</strong>
              </Alert>
            ) : null}

            {warnings.map((warning) => (
              <Alert key={warning} severity="warning">
                {warning}
              </Alert>
            ))}

            {blockers.map((blocker) => (
              <Alert key={blocker} severity="error">
                {blocker}
              </Alert>
            ))}

            <Box>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Colunas agregadas do batch
              </Typography>
              {loading ? (
                <Box sx={{ py: 3, display: "flex", justifyContent: "center" }}>
                  <CircularProgress size={28} />
                </Box>
              ) : colunas.length === 0 ? (
                <Alert severity="warning">Nenhuma coluna detectada nos lotes selecionados.</Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700 }}>Coluna de origem</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Cobertura</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Sugestao automatica</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Campo canonico</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {colunas.map((coluna) => (
                        <TableRow key={coluna.chave_agregada} hover>
                          <TableCell sx={{ minWidth: 220, verticalAlign: "top" }}>
                            <Stack spacing={0.75}>
                              <Typography variant="body2" fontFamily="monospace">
                                {coluna.nome_exibicao}
                              </Typography>
                              {coluna.variantes.length > 1 ? (
                                <Typography variant="caption" color="text.secondary">
                                  Variantes: {coluna.variantes.join(", ")}
                                </Typography>
                              ) : null}
                            </Stack>
                          </TableCell>
                          <TableCell sx={{ minWidth: 320, verticalAlign: "top" }}>
                            <Stack spacing={0.75}>
                              <Typography variant="caption" color="text.secondary">
                                Presente em {coluna.aparece_em_arquivos} arquivo(s).
                              </Typography>
                              {coluna.ocorrencias.map((occurrence) => (
                                <Box key={`${coluna.chave_agregada}-${occurrence.batch_id}-${occurrence.coluna_original}`}>
                                  <Typography variant="caption" fontWeight={600}>
                                    {occurrence.file_name}
                                  </Typography>
                                  <Typography variant="caption" display="block" color="text.secondary">
                                    {occurrence.coluna_original !== coluna.nome_exibicao
                                      ? `Cabecalho neste arquivo: ${occurrence.coluna_original}. `
                                      : ""}
                                    Amostras: {formatSamples(occurrence.amostras)}.
                                  </Typography>
                                </Box>
                              ))}
                              {coluna.warnings.map((warning) => (
                                <Typography key={warning} variant="caption" color="warning.main">
                                  {warning}
                                </Typography>
                              ))}
                            </Stack>
                          </TableCell>
                          <TableCell sx={{ minWidth: 180, verticalAlign: "top" }}>
                            <Chip
                              label={CONFIDENCE_LABELS[coluna.confianca]}
                              color={CONFIDENCE_COLORS[coluna.confianca]}
                              size="small"
                              variant="outlined"
                            />
                            {coluna.campo_sugerido ? (
                              <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
                                -&gt; {coluna.campo_sugerido}
                              </Typography>
                            ) : null}
                          </TableCell>
                          <TableCell sx={{ minWidth: 200, verticalAlign: "top" }}>
                            <Select
                              value={sanitizeMappedField(mapeamento[coluna.chave_agregada])}
                              onChange={(event) =>
                                setMapeamento((prev) => ({
                                  ...prev,
                                  [coluna.chave_agregada]: event.target.value as string,
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
                disabled={submitting || isRecovering}
              >
                {cancelLabel}
              </Button>
              {blockers.length > 0 && fallbackBatchId != null ? (
                <Button
                  variant="text"
                  onClick={() =>
                    navigate(
                      `/leads/importar?step=mapping&batch_id=${fallbackBatchId}&context=batch&mapping_mode=single`,
                    )
                  }
                  disabled={submitting || isRecovering}
                >
                  {`Abrir lote #${fallbackBatchId} por arquivo`}
                </Button>
              ) : null}
              <Button variant="contained" disabled={!canConfirm} onClick={handleConfirm}>
                {submitting || isRecovering ? (
                  <CircularProgress size={18} color="inherit" />
                ) : (
                  "Concluir mapeamento do batch"
                )}
              </Button>
            </Stack>
          </Stack>
        </Paper>
      )}
    </Box>
  );
}
