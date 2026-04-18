import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from "@mui/material";
import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import QuickCreateEventoModal from "../../components/QuickCreateEventoModal";
import {
  commitLeadImportEtl,
  createLeadBatch,
  DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON,
  getActivationImportBlockReason,
  getLeadBatch,
  getLeadBatchPreview,
  LeadBatch,
  LeadBatchPreview,
  LeadImportEtlPreview,
  LeadImportEtlResult,
  listReferenciaEventos,
  previewLeadImportEtl,
  ReferenciaEvento,
  supportsActivationImport,
} from "../../services/leads_import";
import type { EventoRead } from "../../services/eventos/core";
import { createEventoAtivacao, listEventoAtivacoes } from "../../services/eventos/workflow";
import { ApiError, toApiErrorMessage } from "../../services/http";
import { useAuth } from "../../store/auth";
import { getLocalDateInputValue } from "../../utils/date";
import BatchSummaryCard from "./importacao/BatchSummaryCard";
import ImportacaoUploadStep from "./importacao/ImportacaoUploadStep";
import { LEADS_IMPORT_ALLOWED_EXTENSIONS } from "./importacao/constants";
import {
  BronzeMode,
  useBatchUploadDraft,
} from "./importacao/batch/useBatchUploadDraft";
import MapeamentoPage from "./MapeamentoPage";
import PipelineStatusPage from "./PipelineStatusPage";

const BRONZE_WORKFLOW_STEPS = ["Upload", "Mapeamento", "Pipeline"];
const ETL_WORKFLOW_STEPS = ["Arquivo e evento", "Preview ETL", "Commit ETL"];

type ImportFlow = "bronze" | "etl";
type ShellStep = "upload" | "mapping" | "pipeline" | "etl";
type ShellContext = "batch" | null;
type QuickCreateTarget =
  | { kind: "bronze-single" }
  | { kind: "etl" }
  | { kind: "batch-row"; rowId: string }
  | null;

function hasAllowedExtension(file: File) {
  const name = file.name.toLowerCase();
  return LEADS_IMPORT_ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
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

function sanitizeShellContext(rawContext: string | null): ShellContext {
  return rawContext === "batch" ? "batch" : null;
}

function mapAtivacaoOptions(items: Array<{ id: number; nome: string }>) {
  return items.map((item) => ({ id: item.id, nome: item.nome }));
}

function upsertAtivacaoOption(prev: Array<{ id: number; nome: string }>, next: { id: number; nome: string }) {
  if (prev.some((item) => item.id === next.id)) {
    return prev.map((item) => (item.id === next.id ? next : item));
  }
  return [...prev, next];
}

export default function ImportacaoPage() {
  const { token, user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const routeBatchId = Number(searchParams.get("batch_id") ?? "0");
  const shellStep = sanitizeShellStep(searchParams.get("step"), routeBatchId);
  const shellContext = sanitizeShellContext(searchParams.get("context"));
  const today = useMemo(() => getLocalDateInputValue(), []);
  const bronzeAtivacoesRequestIdRef = useRef(0);

  const [activeStep, setActiveStep] = useState(0);
  const [quemEnviou, setQuemEnviou] = useState(user?.email ?? "");
  const [plataformaOrigem, setPlataformaOrigem] = useState("");
  const [dataEnvio, setDataEnvio] = useState(today);
  const [file, setFile] = useState<File | null>(null);
  const [importFlow, setImportFlow] = useState<ImportFlow>(() => (shellStep === "etl" ? "etl" : "bronze"));
  const [bronzeMode, setBronzeMode] = useState<BronzeMode>("single");
  const [eventos, setEventos] = useState<ReferenciaEvento[]>([]);
  const [eventoId, setEventoId] = useState("");
  const [bronzeEventoId, setBronzeEventoId] = useState("");
  const [bronzeOrigemLote, setBronzeOrigemLote] = useState<"proponente" | "ativacao">("proponente");
  const [bronzeTipoLeadProponente, setBronzeTipoLeadProponente] = useState<"bilheteria" | "entrada_evento">(
    "entrada_evento",
  );
  const [bronzeAtivacaoId, setBronzeAtivacaoId] = useState("");
  const [ativacoes, setAtivacoes] = useState<{ id: number; nome: string }[]>([]);
  const [ativacoesLoadError, setAtivacoesLoadError] = useState<string | null>(null);
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
  const [quickCreateTarget, setQuickCreateTarget] = useState<QuickCreateTarget>(null);
  const [error, setError] = useState<string | null>(null);

  const batchUpload = useBatchUploadDraft({
    token,
    defaultQuemEnviou: user?.email ?? "",
    defaultDataEnvio: today,
    eventos,
    setEventos,
  });
  const batchContextRow = useMemo(() => {
    if (shellContext !== "batch" || routeBatchId <= 0) return null;
    return batchUpload.rows.find((row) => row.created_batch_id === routeBatchId) ?? null;
  }, [batchUpload.rows, routeBatchId, shellContext]);
  const hasBatchWorkspaceContext = shellContext === "batch" && batchContextRow != null;

  const selectedBronzeEvento = useMemo(() => {
    if (!bronzeEventoId || !Number.isFinite(Number(bronzeEventoId))) return null;
    return eventos.find((evento) => evento.id === Number(bronzeEventoId)) ?? null;
  }, [bronzeEventoId, eventos]);
  const bronzeEventoSupportsActivationImport = supportsActivationImport(selectedBronzeEvento);
  const bronzeActivationImportBlockReason =
    getActivationImportBlockReason(selectedBronzeEvento) ??
    (selectedBronzeEvento && !bronzeEventoSupportsActivationImport
      ? DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON
      : null);

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
    if (!token || importFlow !== "bronze" || !bronzeEventoId || !bronzeEventoSupportsActivationImport) {
      bronzeAtivacoesRequestIdRef.current += 1;
      setAtivacoes([]);
      setAtivacoesLoadError(null);
      setLoadingAtivacoes(false);
      setBronzeAtivacaoId("");
      return;
    }

    const requestId = bronzeAtivacoesRequestIdRef.current + 1;
    bronzeAtivacoesRequestIdRef.current = requestId;

    setBronzeAtivacaoId("");
    setAtivacoes([]);
    setAtivacoesLoadError(null);
    setLoadingAtivacoes(true);
    listEventoAtivacoes(token, Number(bronzeEventoId))
      .then((rows) => {
        if (bronzeAtivacoesRequestIdRef.current !== requestId) return;
        setAtivacoes(mapAtivacaoOptions(rows));
        setAtivacoesLoadError(null);
      })
      .catch((error) => {
        if (bronzeAtivacoesRequestIdRef.current !== requestId) return;
        setAtivacoes([]);
        setAtivacoesLoadError(toApiErrorMessage(error, "Nao foi possivel carregar as ativacoes deste evento."));
      })
      .finally(() => {
        if (bronzeAtivacoesRequestIdRef.current !== requestId) return;
        setLoadingAtivacoes(false);
      });
  }, [bronzeEventoId, bronzeEventoSupportsActivationImport, importFlow, token]);

  useEffect(() => {
    if (
      importFlow === "bronze" &&
      bronzeOrigemLote === "ativacao" &&
      bronzeEventoId &&
      !bronzeEventoSupportsActivationImport
    ) {
      setBronzeOrigemLote("proponente");
      setBronzeAtivacaoId("");
    }
  }, [bronzeEventoId, bronzeEventoSupportsActivationImport, bronzeOrigemLote, importFlow]);

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
      (bronzeOrigemLote === "ativacao" &&
        bronzeEventoSupportsActivationImport &&
        Boolean(bronzeEventoId) &&
        Boolean(bronzeAtivacaoId));
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
    bronzeEventoSupportsActivationImport,
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
    setBronzeMode("single");
    setPlataformaOrigem("");
    setFile(null);
    setBronzeEventoId("");
    setBronzeOrigemLote("proponente");
    setBronzeTipoLeadProponente("entrada_evento");
    setBronzeAtivacaoId("");
    setAtivacoes([]);
    setAtivacoesLoadError(null);
    setQuickCreateTarget(null);
    batchUpload.reset();
    resetBronzeFlow();
    resetEtlFlow();
    resetErrorState();
    const nextParams = new URLSearchParams();
    nextParams.set("step", nextFlow === "etl" ? "etl" : "upload");
    setSearchParams(nextParams);
  };

  const setCanonicalStep = (nextStep: ShellStep, batchId?: number | null, context?: ShellContext) => {
    const nextParams = new URLSearchParams();
    nextParams.set("step", nextStep);
    if (batchId && (nextStep === "mapping" || nextStep === "pipeline")) {
      nextParams.set("batch_id", String(batchId));
    }
    if (context === "batch" && (nextStep === "mapping" || nextStep === "pipeline")) {
      nextParams.set("context", context);
    }
    setSearchParams(nextParams);
  };

  const handleOpenBatchRowFlow = (row: (typeof batchUpload.rows)[number]) => {
    if (row.created_batch_id == null) return;
    const nextStep =
      row.downstream_stage === "bronze" || row.downstream_stage == null ? "mapping" : "pipeline";
    setError(null);
    setCanonicalStep(nextStep, row.created_batch_id, "batch");
  };

  const handleReturnToBatchWorkspace = async () => {
    if (!hasBatchWorkspaceContext) {
      setCanonicalStep("upload");
      return;
    }

    if (!token) {
      setError("Sessao expirada. Faca login novamente.");
      setCanonicalStep("upload");
      return;
    }

    try {
      const latestBatch = await getLeadBatch(token, routeBatchId);
      batchUpload.syncCreatedBatch(latestBatch);
      setError(null);
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao sincronizar o lote ao voltar para o batch."));
    } finally {
      setCanonicalStep("upload");
    }
  };

  const handleOpenQuickCreateEvento = () => {
    if (importFlow === "etl") {
      setQuickCreateTarget({ kind: "etl" });
      return;
    }
    setQuickCreateTarget({ kind: "bronze-single" });
  };

  const handleCreateAtivacaoAdHoc = async (nome: string) => {
    if (!token || !bronzeEventoId) {
      setError("Sessao expirada ou evento nao selecionado.");
      throw new Error("invalid");
    }
    if (!bronzeEventoSupportsActivationImport) {
      setError(bronzeActivationImportBlockReason ?? DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON);
      throw new Error("invalid");
    }
    setError(null);
    try {
      const eventId = Number(bronzeEventoId);
      const created = await createEventoAtivacao(token, eventId, { nome });
      const createdOption = { id: created.id, nome: created.nome };

      setAtivacoes((prev) => upsertAtivacaoOption(prev, createdOption));
      setAtivacoesLoadError(null);
      setBronzeAtivacaoId(String(created.id));

      void listEventoAtivacoes(token, eventId)
        .then((rows) => {
          setAtivacoes(mapAtivacaoOptions(rows));
          setAtivacoesLoadError(null);
        })
        .catch(() => {
          // Keep the optimistic activation selected when the post-create refresh fails.
        });
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao criar ativacao."));
      throw err;
    }
  };

  const handleEventoCreated = (created: EventoRead) => {
    const supportsCreatedEventoActivationImport = created.agencia_id != null;
    const referencia: ReferenciaEvento = {
      id: created.id,
      nome: created.nome,
      data_inicio_prevista: created.data_inicio_prevista ?? null,
      agencia_id: created.agencia_id ?? null,
      supports_activation_import: supportsCreatedEventoActivationImport,
      activation_import_block_reason: supportsCreatedEventoActivationImport
        ? null
        : DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON,
      leads_count: 0,
    };
    setEventos((prev) => [referencia, ...prev.filter((item) => item.id !== referencia.id)]);

    if (quickCreateTarget?.kind === "etl") {
      setEventoId(String(created.id));
    } else if (quickCreateTarget?.kind === "batch-row") {
      batchUpload.attachCreatedEvento(quickCreateTarget.rowId, created);
    } else {
      setBronzeEventoId(String(created.id));
      setBronzeAtivacaoId("");
      setAtivacoes([]);
    }

    setQuickCreateTarget(null);
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
    if (bronzeOrigemLote === "ativacao" && !bronzeEventoSupportsActivationImport) {
      setError(bronzeActivationImportBlockReason ?? DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON);
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
                cancelLabel={hasBatchWorkspaceContext ? "Voltar ao batch" : undefined}
                onCancel={() => {
                  if (hasBatchWorkspaceContext) {
                    setCanonicalStep("upload");
                    return;
                  }
                  resetBronzeFlow();
                  setCanonicalStep("upload");
                }}
                onMapped={(result) => {
                  if (hasBatchWorkspaceContext) {
                    batchUpload.markRowMapped(result.batch_id);
                    setCanonicalStep("upload");
                    return;
                  }
                  setCanonicalStep("pipeline", result.batch_id);
                }}
              />
            </Stack>
          )
        ) : shellStep === "pipeline" ? (
          <Stack spacing={2}>
            {hasBatchWorkspaceContext ? (
              <Box>
                <Button variant="outlined" onClick={() => void handleReturnToBatchWorkspace()}>
                  Voltar ao batch
                </Button>
              </Box>
            ) : null}
            <PipelineStatusPage
              batchId={routeBatchId}
              onNewImport={
                hasBatchWorkspaceContext
                  ? undefined
                  : () => {
                      resetForNewImport("bronze");
                    }
              }
            />
          </Stack>
        ) : (
          <ImportacaoUploadStep
            activeStep={activeStep}
            ativacoes={ativacoes}
            ativacoesLoadError={ativacoesLoadError}
            batch={batch}
            batchAgencias={batchUpload.agencias}
            batchAgenciasLoadError={batchUpload.agenciasLoadError}
            batchAtivacoesByEventoId={batchUpload.ativacoesByEventoId}
            batchAtivacoesLoadErrorByEventoId={batchUpload.ativacoesLoadErrorByEventoId}
            batchLoadingAgencias={batchUpload.loadingAgencias}
            batchLoadingAtivacoesByEventoId={batchUpload.loadingAtivacoesByEventoId}
            batchRows={batchUpload.rows}
            bronzeAtivacaoId={bronzeAtivacaoId}
            bronzeActivationImportBlockReason={bronzeActivationImportBlockReason}
            bronzeEventoId={bronzeEventoId}
            bronzeEventoSupportsActivationImport={bronzeEventoSupportsActivationImport}
            bronzeMode={bronzeMode}
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
            onBatchAddFiles={batchUpload.addFiles}
            onBatchCreateAtivacao={batchUpload.createAdHocAtivacao}
            onBatchFieldChange={batchUpload.updateRow}
            onBatchOpenRowFlow={handleOpenBatchRowFlow}
            onBatchOpenQuickCreateEvento={(rowId) => setQuickCreateTarget({ kind: "batch-row", rowId })}
            onBatchRemoveRow={batchUpload.removeRow}
            onBatchRetryRow={batchUpload.retryRow}
            onBatchSaveAgency={batchUpload.saveEventoAgency}
            onBatchSubmit={() => batchUpload.submitRows()}
            onBronzeAtivacaoIdChange={setBronzeAtivacaoId}
            onBronzeEventoIdChange={setBronzeEventoId}
            onBronzeModeChange={(nextMode) => {
              setBronzeMode(nextMode);
              resetBronzeFlow();
              setError(null);
            }}
            onBronzeOrigemLoteChange={(value) => {
              if (
                value === "ativacao" &&
                bronzeEventoId &&
                !bronzeEventoSupportsActivationImport
              ) {
                setBronzeOrigemLote("proponente");
                setBronzeAtivacaoId("");
                return;
              }
              setBronzeOrigemLote(value);
              if (value === "proponente") {
                setBronzeAtivacaoId("");
              }
            }}
            onBronzeTipoLeadProponenteChange={setBronzeTipoLeadProponente}
            onCommitEtl={handleCommitEtl}
            onCpfColumnChange={setEtlCpfColumnIndex}
            onCpfColumnSubmit={handleSubmitCpfColumn}
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
            onOpenQuickCreateEvento={handleOpenQuickCreateEvento}
            onPlataformaOrigemChange={setPlataformaOrigem}
            onQuemEnviouChange={setQuemEnviou}
            onResetEtl={() => {
              resetForNewImport("etl");
            }}
            onSubmit={handleSubmitStep1}
          />
        )}
      </Paper>

      <QuickCreateEventoModal
        open={quickCreateTarget != null}
        onClose={() => setQuickCreateTarget(null)}
        onCreated={handleEventoCreated}
      />
    </Box>
  );
}
