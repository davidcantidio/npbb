import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  LinearProgress,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { toApiErrorMessage } from "../../services/http";
import {
  LeadBatch,
  PipelineReport,
  executarPipeline,
  getLeadBatch,
} from "../../services/leads_import";
import { useAuth } from "../../store/auth";

const POLL_INTERVAL_MS = 1500;

type GateStatus = "PASS" | "PASS_WITH_WARNINGS" | "FAIL";

function GateIcon({ status }: { status: GateStatus }) {
  if (status === "PASS") {
    return <CheckCircleIcon color="success" sx={{ fontSize: 28 }} />;
  }
  if (status === "PASS_WITH_WARNINGS") {
    return <WarningAmberIcon color="warning" sx={{ fontSize: 28 }} />;
  }
  return <ErrorIcon color="error" sx={{ fontSize: 28 }} />;
}

function StageChip({ stage }: { stage: string }) {
  const colorMap: Record<string, "default" | "info" | "success"> = {
    bronze: "default",
    silver: "info",
    gold: "success",
  };
  return (
    <Chip
      label={stage.toUpperCase()}
      color={colorMap[stage] ?? "default"}
      size="small"
      sx={{ fontWeight: 700, letterSpacing: 0.5 }}
    />
  );
}

function PipelineStatusChip({ pipelineStatus }: { pipelineStatus: string }) {
  const colorMap: Record<string, "default" | "success" | "warning" | "error"> = {
    pending: "default",
    pass: "success",
    pass_with_warnings: "warning",
    fail: "error",
  };
  const labelMap: Record<string, string> = {
    pending: "Pendente",
    pass: "Aprovado",
    pass_with_warnings: "Aprovado c/ avisos",
    fail: "Reprovado",
  };
  return (
    <Chip
      label={labelMap[pipelineStatus] ?? pipelineStatus}
      color={colorMap[pipelineStatus] ?? "default"}
      size="small"
      sx={{ fontWeight: 700, letterSpacing: 0.5 }}
    />
  );
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, textAlign: "center", minWidth: 120 }}>
      <Typography variant="h5" fontWeight={700}>
        {value}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Paper>
  );
}

function QualityMetricsSection({ report }: { report: PipelineReport }) {
  const { totals, quality_metrics: qm } = report;
  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1" fontWeight={600}>
        Totais
      </Typography>
      <Stack direction="row" spacing={2} flexWrap="wrap">
        <MetricCard label="Linhas brutas" value={totals.raw_rows} />
        <MetricCard label="Linhas válidas" value={totals.valid_rows} />
        <MetricCard label="Descartadas" value={totals.discarded_rows} />
      </Stack>

      <Typography variant="subtitle1" fontWeight={600} sx={{ mt: 1 }}>
        Métricas de Qualidade
      </Typography>
      <Grid container spacing={1}>
        {[
          { label: "CPFs inválidos descartados", value: qm.cpf_invalid_discarded },
          { label: "Telefones inválidos", value: qm.telefone_invalid },
          { label: "Datas de evento inválidas", value: qm.data_evento_invalid },
          { label: "Datas de nascimento inválidas", value: qm.data_nascimento_invalid },
          { label: "Datas de nascimento ausentes", value: qm.data_nascimento_missing },
          { label: "Duplicidades CPF+evento", value: qm.duplicidades_cpf_evento },
          { label: "Cidade fora do mapeamento", value: qm.cidade_fora_mapeamento },
          { label: "Localidades inválidas", value: qm.localidade_invalida },
          { label: "Localidades não resolvidas", value: qm.localidade_nao_resolvida },
          { label: "Localidades fora do Brasil", value: qm.localidade_fora_brasil },
          {
            label: "Cidade/UF inconsistentes",
            value: qm.localidade_cidade_uf_inconsistente,
          },
        ].map(({ label, value }) => (
          <Grid item xs={6} sm={4} key={label}>
            <Tooltip title={label}>
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  textAlign: "center",
                  borderColor: value > 0 ? "warning.main" : "divider",
                }}
              >
                <Typography
                  variant="h6"
                  fontWeight={700}
                  color={value > 0 ? "warning.main" : "text.primary"}
                >
                  {value}
                </Typography>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {label}
                </Typography>
              </Paper>
            </Tooltip>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}

export type PipelineStatusPageProps = {
  batchId?: number;
  onNewImport?: () => void;
};

export default function PipelineStatusPage({
  batchId: batchIdProp,
  onNewImport,
}: PipelineStatusPageProps = {}) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const batchId = batchIdProp ?? Number(searchParams.get("batch_id"));

  const [batch, setBatch] = useState<LeadBatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const fetchBatch = async () => {
    if (!token || !batchId) return;
    try {
      const data = await getLeadBatch(token, batchId);
      setBatch(data);
      if (!(data.pipeline_status === "pending" && data.pipeline_progress !== null)) {
        stopPolling();
      }
    } catch (err) {
      setError(toApiErrorMessage(err, "Erro ao carregar o status do lote."));
      stopPolling();
    }
  };

  useEffect(() => {
    if (!batchId) {
      setError("batch_id ausente na URL.");
      setLoading(false);
      return;
    }
    fetchBatch().finally(() => setLoading(false));
    return () => stopPolling();
  }, [batchId, token]);

  useEffect(() => {
    if (!batch) return;
    const hasActiveProgress =
      batch.pipeline_status === "pending" && batch.pipeline_progress !== null;
    if (!hasActiveProgress) {
      stopPolling();
      return;
    }
    if (!pollRef.current) {
      pollRef.current = setInterval(fetchBatch, POLL_INTERVAL_MS);
    }
  }, [batch?.pipeline_status, batch?.pipeline_progress?.updated_at]);

  const handleExecutar = async () => {
    if (!token || !batchId) return;
    setRunning(true);
    setError(null);
    try {
      await executarPipeline(token, batchId);
      await fetchBatch();
    } catch (err) {
      setError(toApiErrorMessage(err, "Erro ao executar o pipeline."));
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ py: 8, display: "flex", justifyContent: "center" }}>
        <CircularProgress size={32} />
      </Box>
    );
  }

  if (error && !batch) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!batch) return null;

  const report = batch.pipeline_report;
  const gateStatus: GateStatus | null = report?.gate?.status ?? null;
  const pipelineProgress = batch.pipeline_progress;
  const hasActiveProgress =
    batch.pipeline_status === "pending" && pipelineProgress !== null;
  const progressValue = pipelineProgress?.pct ?? null;

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, maxWidth: 900, mx: "auto" }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" fontWeight={700}>
          Pipeline Gold — Lote #{batch.id}
        </Typography>
        <Button
          variant="text"
          size="small"
          onClick={() => {
            if (onNewImport) {
              onNewImport();
            } else {
              navigate("/leads/importar");
            }
          }}
        >
          Nova importação
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={3} alignItems="flex-start">
          <Stack spacing={1}>
            <Typography variant="caption" color="text.secondary">
              Arquivo
            </Typography>
            <Typography variant="body2" fontWeight={500}>
              {batch.nome_arquivo_original}
            </Typography>
          </Stack>

          <Stack spacing={1}>
            <Typography variant="caption" color="text.secondary">
              Plataforma
            </Typography>
            <Typography variant="body2">{batch.plataforma_origem}</Typography>
          </Stack>

          <Stack spacing={1}>
            <Typography variant="caption" color="text.secondary">
              Stage
            </Typography>
            <StageChip stage={batch.stage} />
          </Stack>

          <Stack spacing={1}>
            <Typography variant="caption" color="text.secondary">
              Status Pipeline
            </Typography>
            <Stack direction="row" alignItems="center" spacing={1}>
              <PipelineStatusChip pipelineStatus={batch.pipeline_status} />
              {hasActiveProgress && <CircularProgress size={14} />}
            </Stack>
          </Stack>
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
          {batch.stage === "silver" && !hasActiveProgress && (
            <Button
              variant="contained"
              onClick={handleExecutar}
              disabled={running}
              startIcon={running ? <CircularProgress size={16} /> : undefined}
            >
              {running ? "Executando..." : "Executar Pipeline"}
            </Button>
          )}
          {hasActiveProgress && (
            <Stack spacing={1} sx={{ flex: 1, minWidth: { xs: "100%", sm: 320 } }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2}>
                <Typography variant="body2" color="text.secondary">
                  {pipelineProgress?.label ?? "Processando pipeline..."}
                </Typography>
                {typeof progressValue === "number" && (
                  <Typography variant="caption" color="text.secondary">
                    {progressValue}%
                  </Typography>
                )}
              </Stack>
              <LinearProgress
                aria-label="Progresso da pipeline"
                variant={typeof progressValue === "number" ? "determinate" : "indeterminate"}
                value={typeof progressValue === "number" ? progressValue : undefined}
              />
              <Typography variant="caption" color="text.secondary">
                Atualizando automaticamente...
              </Typography>
            </Stack>
          )}
          {batch.stage === "gold" && (
            <Alert severity="success" sx={{ py: 0.5 }} icon={<CheckCircleIcon />}>
              {report?.totals?.valid_rows ?? "?"} leads promovidos para Gold
            </Alert>
          )}
        </Stack>
      </Paper>

      {report && gateStatus && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1.5} mb={2}>
            <GateIcon status={gateStatus} />
            <Typography variant="h6" fontWeight={700}>
              Gate:{" "}
              <span style={{ textTransform: "uppercase" }}>
                {gateStatus.replace(/_/g, " ")}
              </span>
            </Typography>
          </Stack>

          {gateStatus === "FAIL" && report.gate.fail_reasons.length > 0 && (
            <Stack spacing={1} mb={2}>
              <Typography variant="subtitle2" fontWeight={600} color="error">
                Motivos de reprovação:
              </Typography>
              {report.gate.fail_reasons.map((reason) => (
                <Alert key={reason} severity="error" sx={{ py: 0.5 }}>
                  {reason}
                </Alert>
              ))}
            </Stack>
          )}

          {report.gate.warnings.length > 0 && (
            <Stack spacing={1} mb={2}>
              <Typography variant="subtitle2" fontWeight={600} color="warning.dark">
                Avisos:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {report.gate.warnings.map((warning) => (
                  <Chip key={warning} label={warning} color="warning" size="small" />
                ))}
              </Stack>
            </Stack>
          )}

          <Divider sx={{ my: 2 }} />
          <QualityMetricsSection report={report} />
        </Paper>
      )}
    </Box>
  );
}
