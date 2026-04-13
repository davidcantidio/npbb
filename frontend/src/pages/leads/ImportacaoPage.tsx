import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  MenuItem,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  commitLeadImportEtl,
  createLeadBatch,
  getLeadBatch,
  getLeadBatchPreview,
  LeadBatch,
  LeadBatchPreview,
  LeadImportEtlPreview,
  LeadImportEtlResult,
  listReferenciaEventos,
  previewLeadImportEtl,
  ReferenciaEvento,
} from "../../services/leads_import";
import { ApiError, toApiErrorMessage } from "../../services/http";
import { useAuth } from "../../store/auth";
import { formatEventoLabel } from "../../utils/formatters";
import MapeamentoPage from "./MapeamentoPage";
import PipelineStatusPage from "./PipelineStatusPage";

const BRONZE_WORKFLOW_STEPS = ["Upload", "Mapeamento", "Pipeline"];
const ETL_WORKFLOW_STEPS = ["Arquivo e evento", "Preview ETL", "Commit ETL"];
const PLATAFORMAS = ["email", "whatsapp", "drive", "manual", "outro"];
const ALLOWED_EXTENSIONS = [".csv", ".xlsx"];

type ImportFlow = "bronze" | "etl";
type ShellStep = "upload" | "mapping" | "pipeline" | "etl";

function hasAllowedExtension(file: File) {
  const name = file.name.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

function sanitizeShellStep(rawStep: string | null, batchId: number): ShellStep {
  if (rawStep === "mapping" || rawStep === "pipeline") {
    return batchId > 0 ? rawStep : "upload";
  }
  if (rawStep === "etl") {
    return "etl";
  }
  return "upload";
}

function pipelineStatusChipColor(
  status: LeadBatch["pipeline_status"],
): "default" | "info" | "success" | "warning" | "error" {
  if (status === "pass") return "success";
  if (status === "pass_with_warnings") return "warning";
  if (status === "fail") return "error";
  return "default";
}

function pipelineStatusLabel(status: LeadBatch["pipeline_status"]) {
  if (status === "pass") return "Pipeline aprovado";
  if (status === "pass_with_warnings") return "Pipeline com avisos";
  if (status === "fail") return "Pipeline reprovado";
  return "Pipeline pendente";
}

function stageChipColor(stage: LeadBatch["stage"]): "default" | "info" | "success" {
  if (stage === "silver") return "info";
  if (stage === "gold") return "success";
  return "default";
}

function formatDateOnly(value: string) {
  return value.slice(0, 10);
}

function BatchSummaryCard({ batch }: { batch: LeadBatch }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
      <Stack spacing={1.5}>
        <Typography variant="subtitle1" fontWeight={700}>
          Estado atual do lote #{batch.id}
        </Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} flexWrap="wrap">
          <Stack spacing={0.5}>
            <Typography variant="caption" color="text.secondary">
              Arquivo
            </Typography>
            <Typography variant="body2">{batch.nome_arquivo_original}</Typography>
          </Stack>
          <Stack spacing={0.5}>
            <Typography variant="caption" color="text.secondary">
              Plataforma
            </Typography>
            <Typography variant="body2">{batch.plataforma_origem}</Typography>
          </Stack>
          <Stack spacing={0.5}>
            <Typography variant="caption" color="text.secondary">
              Data de envio
            </Typography>
            <Typography variant="body2">{formatDateOnly(batch.data_envio)}</Typography>
          </Stack>
          <Stack spacing={0.5}>
            <Typography variant="caption" color="text.secondary">
              Stage
            </Typography>
            <Chip
              label={batch.stage.toUpperCase()}
              color={stageChipColor(batch.stage)}
              size="small"
              sx={{ width: "fit-content", fontWeight: 700 }}
            />
          </Stack>
          <Stack spacing={0.5}>
            <Typography variant="caption" color="text.secondary">
              Status pipeline
            </Typography>
            <Chip
              label={pipelineStatusLabel(batch.pipeline_status)}
              color={pipelineStatusChipColor(batch.pipeline_status)}
              size="small"
              sx={{ width: "fit-content", fontWeight: 700 }}
            />
          </Stack>
        </Stack>
        {batch.pipeline_report ? (
          <Typography variant="body2" color="text.secondary">
            Gate atual: {batch.pipeline_report.gate.status.replace(/_/g, " ")}
          </Typography>
        ) : null}
      </Stack>
    </Paper>
  );
}

export default function ImportacaoPage() {
  const { token, user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const routeBatchId = Number(searchParams.get("batch_id") ?? "0");
  const shellStep = sanitizeShellStep(searchParams.get("step"), routeBatchId);

  const [activeStep, setActiveStep] = useState(0);
  const [quemEnviou, setQuemEnviou] = useState(user?.email ?? "");
  const [plataformaOrigem, setPlataformaOrigem] = useState("");
  const [dataEnvio, setDataEnvio] = useState(() => new Date().toISOString().slice(0, 10));
  const [file, setFile] = useState<File | null>(null);
  const [importFlow, setImportFlow] = useState<ImportFlow>(() => (shellStep === "etl" ? "etl" : "bronze"));
  const [eventos, setEventos] = useState<ReferenciaEvento[]>([]);
  const [eventoId, setEventoId] = useState("");
  const [loadingEventos, setLoadingEventos] = useState(false);
  const [batch, setBatch] = useState<LeadBatch | null>(null);
  const [mappingBatch, setMappingBatch] = useState<LeadBatch | null>(null);
  const [loadingMappingBatch, setLoadingMappingBatch] = useState(false);
  const [preview, setPreview] = useState<LeadBatchPreview | null>(null);
  const [etlPreview, setEtlPreview] = useState<LeadImportEtlPreview | null>(null);
  const [etlCommitResult, setEtlCommitResult] = useState<LeadImportEtlResult | null>(null);
  const [etlHeaderRow, setEtlHeaderRow] = useState("");
  const [etlCpfColumnIndex, setEtlCpfColumnIndex] = useState("");
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingEtlPreview, setLoadingEtlPreview] = useState(false);
  const [committingEtl, setCommittingEtl] = useState(false);
  const [etlWarningsPending, setEtlWarningsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (shellStep === "etl") {
      setImportFlow("etl");
      return;
    }
    if (shellStep === "mapping" || shellStep === "pipeline") {
      setImportFlow("bronze");
    }
  }, [shellStep]);

  useEffect(() => {
    if (!token || importFlow !== "etl") return;
    setLoadingEventos(true);
    listReferenciaEventos(token)
      .then(setEventos)
      .catch(() => setEventos([]))
      .finally(() => setLoadingEventos(false));
  }, [importFlow, token]);

  useEffect(() => {
    if (!token || shellStep !== "mapping" || routeBatchId <= 0) {
      setMappingBatch(null);
      setLoadingMappingBatch(false);
      return;
    }
    setLoadingMappingBatch(true);
    getLeadBatch(token, routeBatchId)
      .then(setMappingBatch)
      .catch(() => setMappingBatch(null))
      .finally(() => setLoadingMappingBatch(false));
  }, [routeBatchId, shellStep, token]);

  const isEtlFile = Boolean(file && hasAllowedExtension(file));

  const canSubmit = useMemo(() => {
    if (importFlow === "etl") {
      return Boolean(quemEnviou.trim() && file && isEtlFile && eventoId && !loadingSubmit && !loadingEtlPreview);
    }
    return Boolean(quemEnviou.trim() && plataformaOrigem && dataEnvio && file && !loadingSubmit);
  }, [dataEnvio, eventoId, file, importFlow, isEtlFile, loadingEtlPreview, loadingSubmit, plataformaOrigem, quemEnviou]);

  const workflowSteps = importFlow === "etl" ? ETL_WORKFLOW_STEPS : BRONZE_WORKFLOW_STEPS;
  const workflowIndex = useMemo(() => {
    if (importFlow === "etl") {
      if (etlCommitResult) return 2;
      if (etlPreview) return 1;
      return 0;
    }
    if (shellStep === "mapping") return 1;
    if (shellStep === "pipeline") return 2;
    return 0;
  }, [etlCommitResult, etlPreview, importFlow, shellStep]);

  const resetBronzeFlow = () => {
    setActiveStep(0);
    setBatch(null);
    setMappingBatch(null);
    setPreview(null);
  };

  const resetEtlFlow = () => {
    setEtlPreview(null);
    setEtlCommitResult(null);
    setEtlWarningsPending(false);
    setEtlHeaderRow("");
    setEtlCpfColumnIndex("");
    setEventoId("");
  };

  const resetErrorState = () => {
    setError(null);
    setLoadingPreview(false);
    setLoadingSubmit(false);
    setLoadingEtlPreview(false);
    setCommittingEtl(false);
  };

  const resetForNewImport = (nextFlow: ImportFlow) => {
    setImportFlow(nextFlow);
    setPlataformaOrigem("");
    setFile(null);
    resetBronzeFlow();
    resetEtlFlow();
    resetErrorState();
    const nextParams = new URLSearchParams();
    nextParams.set("step", nextFlow === "etl" ? "etl" : "upload");
    setSearchParams(nextParams);
  };

  const setCanonicalStep = (nextStep: ShellStep, batchId?: number | null) => {
    const nextParams = new URLSearchParams();
    nextParams.set("step", nextStep);
    if (batchId && (nextStep === "mapping" || nextStep === "pipeline")) {
      nextParams.set("batch_id", String(batchId));
    }
    setSearchParams(nextParams);
  };

  const handleSelectFile = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] ?? null;
    setError(null);
    setFile(nextFile);
    resetBronzeFlow();
    resetEtlFlow();
  };

  const requestEtlPreview = async (
    options?: {
      headerRow?: number;
      fieldAliases?: Record<string, { column_index?: number; source_value?: string | null }>;
    },
  ) => {
    if (!token || !file || !eventoId) return;
    setLoadingEtlPreview(true);
    setError(null);
    setEtlCommitResult(null);
    try {
      const result = await previewLeadImportEtl(token, file, Number(eventoId), false, options);
      setEtlPreview(result);
      setActiveStep(1);
      if (result.status === "cpf_column_required") {
        setEtlCpfColumnIndex("");
      }
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao gerar preview ETL."));
    } finally {
      setLoadingEtlPreview(false);
    }
  };

  const handleSubmitStep1 = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      setError("Sessao expirada. Faca login novamente.");
      return;
    }
    if (!file) {
      setError("Selecione um arquivo CSV ou XLSX.");
      return;
    }
    if (!hasAllowedExtension(file)) {
      setError("Formato de arquivo invalido. Use CSV ou XLSX.");
      return;
    }

    if (importFlow === "etl") {
      if (!eventoId) {
        setError("Selecione o evento de referencia para o preview ETL.");
        return;
      }
      setLoadingSubmit(true);
      resetBronzeFlow();
      try {
        await requestEtlPreview();
      } finally {
        setLoadingSubmit(false);
      }
      return;
    }

    if (!quemEnviou.trim() || !plataformaOrigem || !dataEnvio) {
      setError("Preencha todos os campos obrigatorios.");
      return;
    }

    setLoadingSubmit(true);
    setError(null);
    setPreview(null);
    try {
      const createdBatch = await createLeadBatch(token, {
        quem_enviou: quemEnviou.trim(),
        plataforma_origem: plataformaOrigem,
        data_envio: dataEnvio,
        file,
      });
      setBatch(createdBatch);

      setLoadingPreview(true);
      const batchPreview = await getLeadBatchPreview(token, createdBatch.id);
      setPreview(batchPreview);
      setActiveStep(1);
      setCanonicalStep("upload");
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao enviar arquivo para camada Bronze."));
    } finally {
      setLoadingSubmit(false);
      setLoadingPreview(false);
    }
  };

  const handleBackToStep1 = () => {
    setActiveStep(0);
    setPreview(null);
    setEtlPreview(null);
    setEtlCommitResult(null);
    setEtlWarningsPending(false);
    setError(null);
  };

  const handleSubmitHeaderRow = async () => {
    const parsed = Number(etlHeaderRow);
    if (!Number.isInteger(parsed) || parsed < 1) {
      setError("Informe uma linha de cabecalho valida.");
      return;
    }
    await requestEtlPreview({ headerRow: parsed });
  };

  const handleSubmitCpfColumn = async () => {
    if (!etlPreview || etlPreview.status !== "cpf_column_required") return;
    const parsedColumn = Number(etlCpfColumnIndex);
    const selectedColumn = etlPreview.columns.find((column) => column.column_index === parsedColumn);
    if (!selectedColumn) {
      setError("Selecione a coluna correspondente ao CPF.");
      return;
    }
    await requestEtlPreview({
      headerRow: etlPreview.header_row,
      fieldAliases: {
        cpf: {
          column_index: selectedColumn.column_index,
          source_value: selectedColumn.source_value,
        },
      },
    });
  };

  const handleCommitEtl = async (forceWarnings = false) => {
    if (!token || !eventoId || !etlPreview || etlPreview.status !== "previewed") return;
    setCommittingEtl(true);
    setError(null);
    try {
      const result = await commitLeadImportEtl(token, etlPreview.session_token, Number(eventoId), forceWarnings);
      setEtlCommitResult(result);
      setEtlWarningsPending(false);
    } catch (err: unknown) {
      if (!forceWarnings && err instanceof ApiError && err.code === "ETL_COMMIT_BLOCKED") {
        setEtlWarningsPending(true);
        setError(null);
      } else {
        setEtlWarningsPending(false);
        setError(toApiErrorMessage(err, "Falha ao importar leads do preview ETL."));
      }
    } finally {
      setCommittingEtl(false);
    }
  };

  const renderUploadStep = () => (
    <>
      {activeStep === 0 ? (
        <Box component="form" onSubmit={handleSubmitStep1}>
          <Stack spacing={2}>
            <TextField
              select
              label="Fluxo de processamento"
              value={importFlow}
              onChange={(event) => {
                const nextFlow = event.target.value as ImportFlow;
                resetForNewImport(nextFlow);
              }}
              fullWidth
            >
              <MenuItem value="bronze">Bronze + mapeamento</MenuItem>
              <MenuItem value="etl">ETL CSV/XLSX</MenuItem>
            </TextField>

            <TextField
              label="Quem enviou"
              value={quemEnviou}
              onChange={(event) => setQuemEnviou(event.target.value)}
              required
              fullWidth
            />

            {importFlow === "bronze" ? (
              <>
                <TextField
                  select
                  label="Plataforma de origem"
                  value={plataformaOrigem}
                  onChange={(event) => setPlataformaOrigem(event.target.value)}
                  required
                  fullWidth
                >
                  {PLATAFORMAS.map((plataforma) => (
                    <MenuItem key={plataforma} value={plataforma}>
                      {plataforma}
                    </MenuItem>
                  ))}
                </TextField>

                <TextField
                  label="Data de envio"
                  type="date"
                  value={dataEnvio}
                  onChange={(event) => setDataEnvio(event.target.value)}
                  InputLabelProps={{ shrink: true }}
                  required
                  fullWidth
                />
              </>
            ) : null}

            {importFlow === "etl" ? (
              <TextField
                select
                label="Evento de referencia"
                value={eventoId}
                onChange={(event) => setEventoId(event.target.value)}
                required
                fullWidth
                disabled={loadingEventos}
                helperText={isEtlFile || !file ? "Obrigatorio para o preview ETL." : "Use CSV ou XLSX no preview ETL."}
              >
                <MenuItem value="">
                  <em>Selecione o evento</em>
                </MenuItem>
                {eventos.map((evento) => (
                  <MenuItem key={evento.id} value={String(evento.id)}>
                    {formatEventoLabel(evento.nome, evento.data_inicio_prevista)}
                  </MenuItem>
                ))}
                {eventos.length === 0 ? (
                  <MenuItem value="" disabled>
                    {loadingEventos ? "Carregando eventos..." : "Nenhum evento disponivel"}
                  </MenuItem>
                ) : null}
              </TextField>
            ) : null}

            <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ xs: "stretch", md: "center" }}>
              <Button variant="outlined" component="label" startIcon={<CloudUploadRoundedIcon />} sx={{ textTransform: "none" }}>
                Selecionar CSV/XLSX
                <input hidden type="file" accept=".csv,.xlsx" onChange={handleSelectFile} />
              </Button>
              <Typography variant="body2" color={file ? "text.primary" : "text.secondary"}>
                {file ? file.name : "Nenhum arquivo selecionado"}
              </Typography>
            </Stack>

            {importFlow === "etl" ? (
              <Alert severity="info">
                O fluxo ETL fecha preview e commit no mesmo shell. O contrato atual nao expoe batch_id para consulta de lote.
              </Alert>
            ) : null}

            <Box>
              <Button type="submit" variant="contained" disabled={!canSubmit}>
                {loadingSubmit || loadingEtlPreview ? (
                  <CircularProgress size={18} color="inherit" />
                ) : importFlow === "etl" ? (
                  "Gerar preview ETL"
                ) : (
                  "Enviar para Bronze"
                )}
              </Button>
            </Box>
          </Stack>
        </Box>
      ) : importFlow === "etl" ? (
        <Stack spacing={2}>
          <Typography variant="subtitle1" fontWeight={700}>
            Preview ETL
          </Typography>

          {loadingEtlPreview ? (
            <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}>
              <CircularProgress size={24} />
            </Box>
          ) : null}

          {!etlPreview ? (
            <Alert severity="warning">Nao foi possivel carregar o preview ETL.</Alert>
          ) : null}

          {etlPreview?.status === "header_required" ? (
            <Stack spacing={2}>
              <Alert severity="warning">{etlPreview.message}</Alert>
              <TextField
                label="Linha do cabecalho"
                type="number"
                value={etlHeaderRow}
                onChange={(event) => setEtlHeaderRow(event.target.value)}
                inputProps={{ min: 1, max: etlPreview.max_row }}
                helperText={`Informe uma linha entre 1 e ${etlPreview.max_row}.`}
                fullWidth
              />
              <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
                <Button variant="outlined" onClick={handleBackToStep1}>
                  Cancelar
                </Button>
                <Button variant="contained" onClick={handleSubmitHeaderRow} disabled={loadingEtlPreview}>
                  {loadingEtlPreview ? <CircularProgress size={18} color="inherit" /> : "Reprocessar cabecalho"}
                </Button>
              </Stack>
            </Stack>
          ) : null}

          {etlPreview?.status === "cpf_column_required" ? (
            <Stack spacing={2}>
              <Alert severity="warning">{etlPreview.message}</Alert>
              <TextField
                select
                label="Coluna de CPF"
                value={etlCpfColumnIndex}
                onChange={(event) => setEtlCpfColumnIndex(event.target.value)}
                helperText={`Linha ${etlPreview.header_row}: selecione o cabecalho que representa CPF.`}
                fullWidth
              >
                {etlPreview.columns.map((column) => (
                  <MenuItem key={column.column_index} value={String(column.column_index)}>
                    {column.column_letter} - {column.source_value}
                  </MenuItem>
                ))}
              </TextField>
              <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
                <Button variant="outlined" onClick={handleBackToStep1}>
                  Cancelar
                </Button>
                <Button variant="contained" onClick={handleSubmitCpfColumn} disabled={!etlCpfColumnIndex || loadingEtlPreview}>
                  {loadingEtlPreview ? <CircularProgress size={18} color="inherit" /> : "Salvar alias CPF"}
                </Button>
              </Stack>
            </Stack>
          ) : null}

          {etlPreview?.status === "previewed" ? (
            <Stack spacing={2}>
              {etlCommitResult ? (
                <Alert severity="success">
                  Importacao concluida: {etlCommitResult.created} criado(s), {etlCommitResult.updated} atualizado(s), {etlCommitResult.skipped} ignorado(s), {etlCommitResult.errors} erro(s).
                </Alert>
              ) : null}
              <Typography variant="body2" color="text.secondary">
                Linhas: {etlPreview.total_rows} | Validas: {etlPreview.valid_rows} | Invalidas: {etlPreview.invalid_rows}
              </Typography>
              <Stack spacing={1}>
                {etlPreview.dq_report.map((item) => (
                  <Alert
                    key={item.check_id ?? item.check_name}
                    severity={item.severity === "error" ? "error" : item.severity === "warning" ? "warning" : "info"}
                  >
                    {item.message ?? item.check_name} ({item.affected_rows})
                  </Alert>
                ))}
              </Stack>
              {etlWarningsPending ? (
                <Alert severity="warning">
                  O preview possui avisos (warnings). Confirme que deseja prosseguir mesmo assim.
                </Alert>
              ) : null}
              <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
                <Button
                  variant="outlined"
                  onClick={() => {
                    resetForNewImport("etl");
                  }}
                  disabled={committingEtl}
                >
                  Nova importacao
                </Button>
                {etlWarningsPending ? (
                  <Button
                    variant="contained"
                    color="warning"
                    onClick={() => handleCommitEtl(true)}
                    disabled={committingEtl || Boolean(etlCommitResult)}
                  >
                    {committingEtl ? <CircularProgress size={18} color="inherit" /> : "Confirmar mesmo com avisos"}
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    onClick={() => handleCommitEtl(false)}
                    disabled={committingEtl || Boolean(etlCommitResult)}
                  >
                    {committingEtl ? <CircularProgress size={18} color="inherit" /> : "Confirmar importacao ETL"}
                  </Button>
                )}
              </Stack>
            </Stack>
          ) : null}
        </Stack>
      ) : (
        <Stack spacing={2}>
          {batch ? <BatchSummaryCard batch={batch} /> : null}
          <Typography variant="subtitle1" fontWeight={700}>
            Preview do lote #{batch?.id}
          </Typography>
          {loadingPreview ? (
            <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}>
              <CircularProgress size={24} />
            </Box>
          ) : null}
          {preview ? (
            <>
              <Typography variant="body2" color="text.secondary">
                Colunas detectadas: {preview.headers.length} | Linhas de amostra: {preview.rows.length} de {preview.total_rows}
              </Typography>
              <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {preview.headers.map((header) => (
                        <TableCell key={header}>{header || "-"}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {preview.rows.map((row, rowIndex) => (
                      <TableRow key={`row-${rowIndex}`}>
                        {preview.headers.map((_, columnIndex) => (
                          <TableCell key={`cell-${rowIndex}-${columnIndex}`}>
                            {row[columnIndex] ?? ""}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          ) : (
            <Alert severity="warning">Nao foi possivel carregar o preview.</Alert>
          )}

          <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
            <Button variant="outlined" onClick={handleBackToStep1}>
              Cancelar
            </Button>
            <Button
              variant="contained"
              disabled={!batch}
              onClick={() => {
                if (batch) {
                  setCanonicalStep("mapping", batch.id);
                }
              }}
            >
              Ir para Mapeamento
            </Button>
          </Stack>
        </Stack>
      )}
    </>
  );

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Importacao de Leads
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Shell canonico para upload, mapeamento, pipeline e ETL.
          </Typography>
        </Box>
      </Stack>

      <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
        <Stepper activeStep={workflowIndex} sx={{ mb: 3 }}>
          {workflowSteps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

        {shellStep === "mapping" ? (
          <Stack spacing={2}>
            {loadingMappingBatch ? (
              <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}>
                <CircularProgress size={24} />
              </Box>
            ) : mappingBatch ? (
              <BatchSummaryCard batch={mappingBatch} />
            ) : null}
            <MapeamentoPage
              batchId={routeBatchId}
              onCancel={() => {
                resetBronzeFlow();
                setCanonicalStep("upload");
              }}
              onMapped={(result) => {
                setCanonicalStep("pipeline", result.batch_id);
              }}
            />
          </Stack>
        ) : shellStep === "pipeline" ? (
          <PipelineStatusPage
            batchId={routeBatchId}
            onNewImport={() => {
              resetForNewImport("bronze");
            }}
          />
        ) : (
          renderUploadStep()
        )}
      </Paper>
    </Box>
  );
}
