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
  type BirthDateControlIssue,
  type LeadBatch,
  type PipelineReport,
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

type SourceRowRef = {
  source_file: string;
  source_sheet: string;
  source_row: number;
};

type QualityMetricKey = keyof PipelineReport["quality_metrics"];

const MOTIVO_CPF = "CPF_INVALIDO";
const MOTIVO_TELEFONE = "TELEFONE_INVALIDO";
const MOTIVO_DATA_EVENTO = "DATA_EVENTO_INVALIDA";
const MOTIVO_DUPLICIDADE = "DUPLICIDADE_CPF_EVENTO";

function splitMotivos(motivo: string): string[] {
  return (motivo || "")
    .split(";")
    .map((part) => part.trim())
    .filter(Boolean);
}

function sourceRowKey(r: SourceRowRef): string {
  return `${r.source_file}\u0000${r.source_sheet}\u0000${r.source_row}`;
}

function uniqueSortedRefs(refs: SourceRowRef[]): SourceRowRef[] {
  const seen = new Map<string, SourceRowRef>();
  for (const r of refs) {
    const key = sourceRowKey(r);
    if (!seen.has(key)) {
      seen.set(key, r);
    }
  }
  return [...seen.values()].sort((a, b) => {
    const fa = [a.source_file, a.source_sheet || "", String(a.source_row).padStart(8, "0")].join("\t");
    const fb = [b.source_file, b.source_sheet || "", String(b.source_row).padStart(8, "0")].join("\t");
    return fa.localeCompare(fb);
  });
}

function formatSourceRowRef(r: SourceRowRef): string {
  const sheet = (r.source_sheet || "").trim();
  if (sheet) {
    return `${sheet} · linha ${r.source_row}`;
  }
  return `Linha ${r.source_row}`;
}

function refsFromInvalidRecords(
  report: PipelineReport,
  motivoTest: (motivos: string[]) => boolean,
): SourceRowRef[] {
  const inv = report.invalid_records;
  if (!inv?.length) return [];
  const acc: SourceRowRef[] = [];
  for (const rec of inv) {
    const motivos = splitMotivos(rec.motivo_rejeicao);
    if (!motivoTest(motivos)) continue;
    acc.push({
      source_file: String(rec.source_file ?? ""),
      source_sheet: String(rec.source_sheet ?? ""),
      source_row: Number(rec.source_row) || 0,
    });
  }
  return uniqueSortedRefs(acc);
}

function refsFromBirthControle(report: PipelineReport, issues: BirthDateControlIssue[]): SourceRowRef[] {
  const ctrl = report.data_nascimento_controle;
  if (!ctrl?.length) return [];
  const want = new Set(issues);
  const acc = ctrl
    .filter((entry) => want.has(entry.issue))
    .map((entry) => ({
      source_file: String(entry.source_file ?? ""),
      source_sheet: String(entry.source_sheet ?? ""),
      source_row: Number(entry.source_row) || 0,
    }));
  return uniqueSortedRefs(acc);
}

function refsFromLocalidade(report: PipelineReport, issueTest: (issue: string) => boolean): SourceRowRef[] {
  const ctrl = report.localidade_controle;
  if (!ctrl?.length) return [];
  const acc = ctrl
    .filter((entry) => issueTest(entry.issue))
    .map((entry) => ({
      source_file: String(entry.source_file ?? ""),
      source_sheet: String(entry.source_sheet ?? ""),
      source_row: Number(entry.source_row) || 0,
    }));
  return uniqueSortedRefs(acc);
}

function refsCidadeForaMapeamento(report: PipelineReport): SourceRowRef[] {
  const ctrl = report.cidade_fora_mapeamento_controle;
  if (!ctrl?.length) return [];
  return uniqueSortedRefs(
    ctrl.map((entry) => ({
      source_file: String(entry.source_file ?? ""),
      source_sheet: String(entry.source_sheet ?? ""),
      source_row: Number(entry.source_row) || 0,
    })),
  );
}

function buildQualityMetricRowIndex(report: PipelineReport): Record<QualityMetricKey, SourceRowRef[]> {
  return {
    cpf_invalid_discarded: refsFromInvalidRecords(report, (motivos) => motivos.includes(MOTIVO_CPF)),
    telefone_invalid: refsFromInvalidRecords(report, (motivos) => motivos.includes(MOTIVO_TELEFONE)),
    data_evento_invalid: refsFromInvalidRecords(report, (motivos) => motivos.includes(MOTIVO_DATA_EVENTO)),
    data_nascimento_invalid: refsFromBirthControle(report, ["unparseable", "future", "before_min"]),
    data_nascimento_missing: refsFromBirthControle(report, ["missing"]),
    duplicidades_cpf_evento: refsFromInvalidRecords(report, (motivos) => motivos.includes(MOTIVO_DUPLICIDADE)),
    cidade_fora_mapeamento: refsCidadeForaMapeamento(report),
    localidade_invalida: refsFromLocalidade(report, () => true),
    localidade_nao_resolvida: refsFromLocalidade(
      report,
      (issue) => issue !== "non_br" && issue !== "cidade_uf_mismatch",
    ),
    localidade_fora_brasil: refsFromLocalidade(report, (issue) => issue === "non_br"),
    localidade_cidade_uf_inconsistente: refsFromLocalidade(report, (issue) => issue === "cidade_uf_mismatch"),
  };
}

function QualityMetricCardWithRows({
  label,
  value,
  rowRefs,
}: {
  label: string;
  value: number;
  rowRefs: SourceRowRef[];
}) {
  const formattedRows = rowRefs.map(formatSourceRowRef);
  const maxInline = 6;
  const shownInline = formattedRows.slice(0, maxInline);
  const hiddenCount = formattedRows.length - shownInline.length;
  const inlineSummary =
    formattedRows.length === 0
      ? ""
      : hiddenCount > 0
        ? `${shownInline.join(", ")} (+${hiddenCount})`
        : shownInline.join(", ");

  const tooltipBody =
    formattedRows.length > 0 ? (
      <Box sx={{ maxHeight: 280, overflow: "auto", py: 0.5 }}>
        {formattedRows.map((line, idx) => (
          <Typography key={`${line}-${idx}`} component="div" variant="caption" sx={{ display: "block", py: 0.25 }}>
            {line}
          </Typography>
        ))}
      </Box>
    ) : (
      label
    );

  const paper = (
    <Paper
      variant="outlined"
      sx={{
        p: 1.5,
        textAlign: "center",
        borderColor: value > 0 ? "warning.main" : "divider",
      }}
    >
      <Typography variant="h6" fontWeight={700} color={value > 0 ? "warning.main" : "text.primary"}>
        {value}
      </Typography>
      <Typography variant="caption" color="text.secondary" noWrap title={label}>
        {label}
      </Typography>
      {rowRefs.length > 0 && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            display: "block",
            mt: 0.75,
            lineHeight: 1.35,
            textAlign: "left",
            whiteSpace: "normal",
          }}
        >
          <Box component="span" fontWeight={600}>
            Linhas:{" "}
          </Box>
          {inlineSummary}
        </Typography>
      )}
    </Paper>
  );

  return (
    <Tooltip title={tooltipBody} describeChild>
      <Box sx={{ cursor: rowRefs.length > 0 ? "help" : "default" }}>{paper}</Box>
    </Tooltip>
  );
}

function QualityMetricsSection({
  report,
  anchoredOnEventoId = false,
}: {
  report: PipelineReport;
  anchoredOnEventoId?: boolean;
}) {
  const { totals, quality_metrics: qm } = report;
  const rowIndex = buildQualityMetricRowIndex(report);

  const items = [
    { key: "cpf_invalid_discarded", label: "CPFs inválidos descartados" },
    { key: "telefone_invalid", label: "Telefones inválidos" },
    { key: "data_evento_invalid", label: "Datas de evento inválidas" },
    { key: "data_nascimento_invalid", label: "Datas de nascimento inválidas" },
    { key: "data_nascimento_missing", label: "Datas de nascimento ausentes" },
    { key: "duplicidades_cpf_evento", label: "Duplicidades CPF+evento" },
    {
      key: "cidade_fora_mapeamento",
      label: "Cidade fora do mapeamento",
    },
    {
      key: "localidade_invalida",
      label: anchoredOnEventoId ? "Cidade/UF do lead inválidos" : "Localidades inválidas",
    },
    {
      key: "localidade_nao_resolvida",
      label: anchoredOnEventoId ? "Cidade/UF do lead não resolvidos" : "Localidades não resolvidas",
    },
    {
      key: "localidade_fora_brasil",
      label: anchoredOnEventoId ? "Cidade/UF do lead fora do Brasil" : "Localidades fora do Brasil",
    },
    {
      key: "localidade_cidade_uf_inconsistente",
      label: anchoredOnEventoId ? "Cidade/UF do lead inconsistentes" : "Cidade/UF inconsistentes",
    },
  ] satisfies Array<{ key: QualityMetricKey; label: string }>;

  const visibleItems = items.filter(({ key }) => {
    if (anchoredOnEventoId && key === "data_evento_invalid") return false;
    if (anchoredOnEventoId && key === "cidade_fora_mapeamento") return false;
    return true;
  });

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
        {visibleItems.map(({ key, label }) => (
          <Grid item xs={6} sm={4} key={key}>
            <QualityMetricCardWithRows label={label} value={qm[key]} rowRefs={rowIndex[key]} />
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
  const failureContextMessage = report?.failure_context?.message?.trim() || null;
  const visibleFailReasons = report?.gate?.fail_reasons.filter((reason) => reason !== failureContextMessage) ?? [];
  const pipelineProgress = batch.pipeline_progress;
  const hasActiveProgress =
    batch.pipeline_status === "pending" && pipelineProgress !== null;
  const progressValue = pipelineProgress?.pct ?? null;
  const anchoredOnEventoId = batch.evento_id != null;

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

      {batch.pipeline_status === "fail" && !report && (
        <Alert severity="error" sx={{ mb: 3 }}>
          O pipeline falhou antes de gerar o relatorio desta execucao. Isso indica erro interno na promocao do lote
          para Gold, nao uma reprovacao explicada pelo quadro de qualidade.
        </Alert>
      )}

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

          {gateStatus === "FAIL" && visibleFailReasons.length > 0 && (
            <Stack spacing={1} mb={2}>
              <Typography variant="subtitle2" fontWeight={600} color="error">
                Motivos de reprovação:
              </Typography>
              {visibleFailReasons.map((reason) => (
                <Alert key={reason} severity="error" sx={{ py: 0.5 }}>
                  {reason}
                </Alert>
              ))}
            </Stack>
          )}

          {gateStatus === "FAIL" && failureContextMessage && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {failureContextMessage}
            </Alert>
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
          <QualityMetricsSection
            report={report}
            anchoredOnEventoId={anchoredOnEventoId}
          />
        </Paper>
      )}
    </Box>
  );
}
