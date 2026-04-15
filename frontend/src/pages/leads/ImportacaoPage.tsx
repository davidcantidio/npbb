import {
  Alert,
  Box,
  CircularProgress,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
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
import { createEventoAtivacao, listEventoAtivacoes } from "../../services/eventos/workflow";
import { ApiError, toApiErrorMessage } from "../../services/http";
import { useAuth } from "../../store/auth";
import BatchSummaryCard from "./importacao/BatchSummaryCard";
import ImportacaoUploadStep from "./importacao/ImportacaoUploadStep";
import MapeamentoPage from "./MapeamentoPage";
import PipelineStatusPage from "./PipelineStatusPage";

const BRONZE_WORKFLOW_STEPS = ["Upload", "Mapeamento", "Pipeline"];
const ETL_WORKFLOW_STEPS = ["Arquivo e evento", "Preview ETL", "Commit ETL"];
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
  const [bronzeEventoId, setBronzeEventoId] = useState("");
  const [bronzeOrigemLote, setBronzeOrigemLote] = useState<"proponente" | "ativacao">("proponente");
  const [bronzeTipoLeadProponente, setBronzeTipoLeadProponente] = useState<"bilheteria" | "entrada_evento">(
    "entrada_evento",
  );
  const [bronzeAtivacaoId, setBronzeAtivacaoId] = useState("");
  const [ativacoes, setAtivacoes] = useState<{ id: number; nome: string }[]>([]);
  const [loadingAtivacoes, setLoadingAtivacoes] = useState(false);
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
    const shouldLoadEventosCatalog = shellStep === "upload" || shellStep === "etl";
    if (!token || !shouldLoadEventosCatalog || (importFlow !== "etl" && importFlow !== "bronze")) return;
    setLoadingEventos(true);
    listReferenciaEventos(token)
      .then(setEventos)
      .catch(() => setEventos([]))
      .finally(() => setLoadingEventos(false));
  }, [importFlow, shellStep, token]);

  useEffect(() => {
    if (!token || importFlow !== "bronze" || !bronzeEventoId) {
      setAtivacoes([]);
      setBronzeAtivacaoId("");
      return;
    }
    setBronzeAtivacaoId("");
    setLoadingAtivacoes(true);
    listEventoAtivacoes(token, Number(bronzeEventoId))
      .then((rows) => setAtivacoes(rows.map((a) => ({ id: a.id, nome: a.nome }))))
      .catch(() => setAtivacoes([]))
      .finally(() => setLoadingAtivacoes(false));
  }, [bronzeEventoId, importFlow, token]);

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
    const bronzeOrigemOk =
      bronzeOrigemLote === "proponente" ||
      (bronzeOrigemLote === "ativacao" && Boolean(bronzeEventoId) && Boolean(bronzeAtivacaoId));
    return Boolean(
      quemEnviou.trim() &&
        plataformaOrigem &&
        dataEnvio &&
        file &&
        bronzeEventoId &&
        bronzeOrigemOk &&
        !loadingSubmit,
    );
  }, [
    bronzeAtivacaoId,
    bronzeEventoId,
    bronzeOrigemLote,
    dataEnvio,
    eventoId,
    file,
    importFlow,
    isEtlFile,
    loadingEtlPreview,
    loadingSubmit,
    plataformaOrigem,
    quemEnviou,
  ]);

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

  const resetEtlPreviewOnly = () => {
    setEtlPreview(null);
    setEtlCommitResult(null);
    setEtlWarningsPending(false);
    setEtlHeaderRow("");
    setEtlCpfColumnIndex("");
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
    setBronzeEventoId("");
    setBronzeOrigemLote("proponente");
    setBronzeTipoLeadProponente("entrada_evento");
    setBronzeAtivacaoId("");
    setAtivacoes([]);
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

  const handleCreateAtivacaoAdHoc = async (nome: string) => {
    if (!token || !bronzeEventoId) {
      setError("Sessao expirada ou evento nao selecionado.");
      throw new Error("invalid");
    }
    setError(null);
    try {
      const created = await createEventoAtivacao(token, Number(bronzeEventoId), { nome });
      const list = await listEventoAtivacoes(token, Number(bronzeEventoId));
      setAtivacoes(list.map((a) => ({ id: a.id, nome: a.nome })));
      setBronzeAtivacaoId(String(created.id));
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao criar ativacao."));
      throw err;
    }
  };

  const handleSelectFile = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] ?? null;
    setError(null);
    setFile(nextFile);
    resetBronzeFlow();
    resetEtlPreviewOnly();
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
    if (!bronzeEventoId) {
      setError("Selecione o evento de referencia desta importacao.");
      return;
    }
    if (bronzeOrigemLote === "ativacao" && !bronzeAtivacaoId) {
      setError("Selecione a ativacao desta importacao ou crie uma nova.");
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
        evento_id: Number(bronzeEventoId),
        file,
        origem_lote: bronzeOrigemLote,
        tipo_lead_proponente:
          bronzeOrigemLote === "proponente" ? bronzeTipoLeadProponente : undefined,
        ativacao_id:
          bronzeOrigemLote === "ativacao" ? Number(bronzeAtivacaoId) : undefined,
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
          loadingMappingBatch ? (
            <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}>
              <CircularProgress size={24} />
            </Box>
          ) : (
            <Stack spacing={2}>
              {mappingBatch ? <BatchSummaryCard batch={mappingBatch} /> : null}
              {mappingBatch?.evento_id != null ? (
                <Alert severity="info">
                  Campos do evento serao derivados automaticamente do cadastro do evento selecionado.
                </Alert>
              ) : null}
              <MapeamentoPage
                batchId={routeBatchId}
                fixedEventoId={mappingBatch?.evento_id ?? null}
                onCancel={() => {
                  resetBronzeFlow();
                  setCanonicalStep("upload");
                }}
                onMapped={(result) => {
                  setCanonicalStep("pipeline", result.batch_id);
                }}
              />
            </Stack>
          )
        ) : shellStep === "pipeline" ? (
          <PipelineStatusPage
            batchId={routeBatchId}
            onNewImport={() => {
              resetForNewImport("bronze");
            }}
          />
        ) : (
          <ImportacaoUploadStep
            activeStep={activeStep}
            ativacoes={ativacoes}
            batch={batch}
            bronzeAtivacaoId={bronzeAtivacaoId}
            bronzeEventoId={bronzeEventoId}
            bronzeOrigemLote={bronzeOrigemLote}
            bronzeTipoLeadProponente={bronzeTipoLeadProponente}
            canSubmit={canSubmit}
            committingEtl={committingEtl}
            dataEnvio={dataEnvio}
            etlCommitResult={etlCommitResult}
            etlCpfColumnIndex={etlCpfColumnIndex}
            etlHeaderRow={etlHeaderRow}
            etlPreview={etlPreview}
            etlWarningsPending={etlWarningsPending}
            eventoId={eventoId}
            eventos={eventos}
            file={file}
            importFlow={importFlow}
            isEtlFile={isEtlFile}
            loadingAtivacoes={loadingAtivacoes}
            loadingEtlPreview={loadingEtlPreview}
            loadingEventos={loadingEventos}
            loadingPreview={loadingPreview}
            loadingSubmit={loadingSubmit}
            plataformaOrigem={plataformaOrigem}
            preview={preview}
            quemEnviou={quemEnviou}
            onBack={handleBackToStep1}
            onCommitEtl={handleCommitEtl}
            onCpfColumnChange={setEtlCpfColumnIndex}
            onCpfColumnSubmit={handleSubmitCpfColumn}
            onBronzeAtivacaoIdChange={setBronzeAtivacaoId}
            onBronzeEventoIdChange={setBronzeEventoId}
            onBronzeOrigemLoteChange={(value) => {
              setBronzeOrigemLote(value);
              if (value === "proponente") {
                setBronzeAtivacaoId("");
              }
            }}
            onBronzeTipoLeadProponenteChange={setBronzeTipoLeadProponente}
            onCreateAtivacaoAdHoc={handleCreateAtivacaoAdHoc}
            onDataEnvioChange={setDataEnvio}
            onEventoIdChange={setEventoId}
            onFileChange={handleSelectFile}
            onGoToMapping={() => {
              if (batch) {
                setCanonicalStep("mapping", batch.id);
              }
            }}
            onHeaderRowChange={setEtlHeaderRow}
            onHeaderRowSubmit={handleSubmitHeaderRow}
            onImportFlowChange={resetForNewImport}
            onPlataformaOrigemChange={setPlataformaOrigem}
            onQuemEnviouChange={setQuemEnviou}
            onResetEtl={() => {
              resetForNewImport("etl");
            }}
            onSubmit={handleSubmitStep1}
          />
        )}
      </Paper>
    </Box>
  );
}
