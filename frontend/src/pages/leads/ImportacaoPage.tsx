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
  commitLeadImportEtlJob,
  createLeadBatchIntake,
  DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON,
  getActivationImportBlockReason,
  getLeadBatch,
  LeadBatch,
  LeadBatchPreview,
  LeadImportEtlPreview,
  LeadImportEtlResult,
  LeadImportMetadataHint,
  listReferenciaEventos,
  LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP,
  normalizeLeadImportHintDateInput,
  ReferenciaEvento,
  reprocessLeadImportEtlJobPreview,
  startLeadImportEtlJob,
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
import { useLeadImportEtlJobPolling } from "./importacao/useLeadImportEtlJobPolling";
import {
  BatchUploadRowDraft,
  BronzeMode,
  useBatchUploadDraft,
} from "./importacao/batch/useBatchUploadDraft";
import BatchMapeamentoPage from "./BatchMapeamentoPage";
import MapeamentoPage from "./MapeamentoPage";
import PipelineStatusPage from "./PipelineStatusPage";

const BRONZE_WORKFLOW_STEPS = ["Upload", "Mapeamento", "Pipeline"];
const ETL_WORKFLOW_STEPS = ["Arquivo e evento", "Preview ETL", "Commit ETL"];

type ImportFlow = "bronze" | "etl";
type ShellStep = "upload" | "mapping" | "pipeline" | "etl";
type ShellContext = "batch" | null;
type BatchMappingMode = "single" | null;
type QuickCreateTarget =
  | { kind: "bronze-single" }
  | { kind: "etl" }
  | { kind: "batch-row"; rowId: string }
  | null;
type BronzeHintEditableField =
  | "plataforma_origem"
  | "data_envio"
  | "evento_id"
  | "origem_lote"
  | "tipo_lead_proponente"
  | "ativacao_id";

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

function sanitizeBatchMappingMode(rawMode: string | null): BatchMappingMode {
  return rawMode === "single" ? "single" : null;
}

function isTerminalBatchWorkspaceRow(row: BatchUploadRowDraft) {
  return (
    row.downstream_stage === "gold" ||
    row.downstream_pipeline_status === "pass" ||
    row.downstream_pipeline_status === "pass_with_warnings" ||
    row.downstream_pipeline_status === "fail"
  );
}

function needsPipelineWorkspaceAction(row: BatchUploadRowDraft) {
  return (
    row.downstream_stage === "silver" &&
    (row.downstream_pipeline_status === "pending" || row.downstream_pipeline_status === "stalled")
  );
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
  const batchMappingMode = sanitizeBatchMappingMode(searchParams.get("mapping_mode"));
  const today = useMemo(() => getLocalDateInputValue(), []);
  const bronzeAtivacoesRequestIdRef = useRef(0);
  const bronzeEventoIdRef = useRef("");
  const bronzeDirtyFieldsRef = useRef<Set<BronzeHintEditableField>>(new Set());

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
  const [bronzeImportHint, setBronzeImportHint] = useState<LeadImportMetadataHint | null>(null);
  const [bronzePendingHintAtivacaoId, setBronzePendingHintAtivacaoId] = useState<string | null>(null);
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
  const [etlSheetName, setEtlSheetName] = useState("");
  const [etlMaxScanRows, setEtlMaxScanRows] = useState("");
  const [quickCreateTarget, setQuickCreateTarget] = useState<QuickCreateTarget>(null);
  const [error, setError] = useState<string | null>(null);
  const etlJobPolling = useLeadImportEtlJobPolling({ token });

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
  const batchMappingEligibleRows = useMemo(() => {
    if (!hasBatchWorkspaceContext) return [];

    const eligibleRows = batchUpload.rows.filter(
      (row) => row.created_batch_id != null && (row.downstream_stage === "bronze" || row.downstream_stage == null),
    );
    const primaryRow = eligibleRows.find((row) => row.created_batch_id === routeBatchId) ?? null;
    if (!primaryRow) {
      return eligibleRows;
    }
    return [primaryRow, ...eligibleRows.filter((row) => row.local_id !== primaryRow.local_id)];
  }, [batchUpload.rows, hasBatchWorkspaceContext, routeBatchId]);
  const batchMappingBatchIds = useMemo(
    () =>
      batchMappingEligibleRows
        .map((row) => row.created_batch_id)
        .filter((batchId): batchId is number => batchId != null),
    [batchMappingEligibleRows],
  );
  const shouldUseBatchMappingShell =
    hasBatchWorkspaceContext && batchMappingBatchIds.length > 0 && batchMappingMode !== "single";
  const currentBatchIsTerminal = useMemo(() => {
    if (!hasBatchWorkspaceContext || !batchContextRow) return false;
    return isTerminalBatchWorkspaceRow(batchContextRow);
  }, [batchContextRow, hasBatchWorkspaceContext]);
  const nextBatchWorkspaceRow = useMemo(() => {
    if (!hasBatchWorkspaceContext) return null;

    const candidateRows = batchUpload.rows.filter((row) => row.created_batch_id != null && row.created_batch_id !== routeBatchId);
    const nextMappingRow =
      candidateRows.find((row) => row.downstream_stage === "bronze" || row.downstream_stage == null) ?? null;
    if (nextMappingRow) {
      return nextMappingRow;
    }

    return candidateRows.find(needsPipelineWorkspaceAction) ?? null;
  }, [batchUpload.rows, hasBatchWorkspaceContext, routeBatchId]);
  const nextBatchWorkspaceLabel =
    nextBatchWorkspaceRow == null
      ? null
      : nextBatchWorkspaceRow.downstream_stage === "bronze" || nextBatchWorkspaceRow.downstream_stage == null
        ? "Abrir mapeamento unificado"
        : "Abrir proximo pipeline pendente";

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
    bronzeEventoIdRef.current = bronzeEventoId;
  }, [bronzeEventoId]);

  const markBronzeFieldDirty = (field: BronzeHintEditableField) => {
    bronzeDirtyFieldsRef.current.add(field);
  };

  const resetBronzeImportHintState = () => {
    bronzeDirtyFieldsRef.current = new Set();
    setBronzeImportHint(null);
    setBronzePendingHintAtivacaoId(null);
  };

  const applyBronzeImportHint = (hint: LeadImportMetadataHint) => {
    const dirtyFields = bronzeDirtyFieldsRef.current;
    const nextEventoId = hint.evento_id != null ? String(hint.evento_id) : "";
    const canApplyLinkedMetadata =
      !dirtyFields.has("evento_id") || bronzeEventoIdRef.current === nextEventoId;

    setBronzeImportHint(hint);

    if (!dirtyFields.has("plataforma_origem")) {
      setPlataformaOrigem(hint.plataforma_origem);
    }

    if (!dirtyFields.has("data_envio")) {
      const normalizedDate = normalizeLeadImportHintDateInput(hint.data_envio);
      if (normalizedDate) {
        setDataEnvio(normalizedDate);
      }
    }

    if (!dirtyFields.has("evento_id")) {
      bronzeEventoIdRef.current = nextEventoId;
      setBronzeEventoId(nextEventoId);
    }

    if (!canApplyLinkedMetadata) {
      return;
    }

    if (!dirtyFields.has("origem_lote")) {
      setBronzeOrigemLote(hint.origem_lote);
    }

    if (hint.origem_lote === "proponente") {
      if (!dirtyFields.has("tipo_lead_proponente") && hint.tipo_lead_proponente) {
        setBronzeTipoLeadProponente(hint.tipo_lead_proponente);
      }
      if (!dirtyFields.has("ativacao_id")) {
        setBronzeAtivacaoId("");
        setBronzePendingHintAtivacaoId(null);
      }
      return;
    }

    if (!dirtyFields.has("ativacao_id")) {
      setBronzeAtivacaoId("");
      setBronzePendingHintAtivacaoId(
        hint.ativacao_id != null ? String(hint.ativacao_id) : null,
      );
    }
  };

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
      setBronzePendingHintAtivacaoId(null);
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
      importFlow !== "bronze" ||
      bronzeOrigemLote !== "ativacao" ||
      !bronzePendingHintAtivacaoId ||
      !bronzeEventoId
    ) {
      return;
    }
    if (bronzeDirtyFieldsRef.current.has("ativacao_id") || loadingAtivacoes) {
      return;
    }

    if (ativacoes.some((ativacao) => String(ativacao.id) === bronzePendingHintAtivacaoId)) {
      setBronzeAtivacaoId(bronzePendingHintAtivacaoId);
      setBronzePendingHintAtivacaoId(null);
      return;
    }

    if (ativacoesLoadError || ativacoes.length === 0) {
      setBronzePendingHintAtivacaoId(null);
    }
  }, [
    ativacoes,
    ativacoesLoadError,
    bronzeEventoId,
    bronzeOrigemLote,
    bronzePendingHintAtivacaoId,
    importFlow,
    loadingAtivacoes,
  ]);

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

  useEffect(() => {
    const job = etlJobPolling.job;
    if (!job) return;

    const previewPolling = job.status === "queued" || job.status === "running";
    const commitPolling = job.status === "commit_queued" || job.status === "committing";
    setLoadingEtlPreview(previewPolling);
    setCommittingEtl(commitPolling);

    if (job.preview_result) {
      setEtlPreview(job.preview_result);
      setActiveStep(1);
      if (job.preview_result.status === "cpf_column_required") {
        setEtlCpfColumnIndex("");
      }
    }

    if (job.commit_result) {
      const previewHasWarnings =
        etlPreview?.status === "previewed" &&
        etlPreview.dq_report.some((item) => item.severity === "warning");
      setEtlCommitResult(job.commit_result);
      setEtlWarningsPending(job.commit_result.status === "partial_failure" && previewHasWarnings);
    }

    if (!etlJobPolling.isPolling && job.error_message) {
      if (job.error_code === "ETL_COMMIT_BLOCKED") {
        setEtlWarningsPending(true);
        setError(null);
        return;
      }
      setError(job.error_message);
    }
  }, [etlJobPolling.isPolling, etlJobPolling.job, etlPreview]);

  useEffect(() => {
    if (!etlJobPolling.pollError) return;
    setLoadingEtlPreview(false);
    setCommittingEtl(false);
    setError(etlJobPolling.pollError);
  }, [etlJobPolling.pollError]);

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
    setBronzeImportHint(null);
    setBronzePendingHintAtivacaoId(null);
  };

  const resetEtlFlow = () => {
    etlJobPolling.clearJob();
    setEtlPreview(null);
    setEtlCommitResult(null);
    setEtlWarningsPending(false);
    setEtlHeaderRow("");
    setEtlCpfColumnIndex("");
    setEtlSheetName("");
    setEtlMaxScanRows("");
    setEventoId("");
  };

  const resetEtlPreviewOnly = () => {
    etlJobPolling.clearJob();
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
    bronzeEventoIdRef.current = "";
    setBronzeEventoId("");
    setBronzeOrigemLote("proponente");
    setBronzeTipoLeadProponente("entrada_evento");
    setBronzeAtivacaoId("");
    setAtivacoes([]);
    setAtivacoesLoadError(null);
    setQuickCreateTarget(null);
    resetBronzeImportHintState();
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

  const handleBronzePlataformaOrigemChange = (value: string) => {
    markBronzeFieldDirty("plataforma_origem");
    setPlataformaOrigem(value);
  };

  const handleBronzeDataEnvioChange = (value: string) => {
    markBronzeFieldDirty("data_envio");
    setDataEnvio(value);
  };

  const handleBronzeEventoIdChange = (value: string) => {
    markBronzeFieldDirty("evento_id");
    setBronzePendingHintAtivacaoId(null);
    bronzeEventoIdRef.current = value;
    setBronzeEventoId(value);
  };

  const handleBronzeOrigemLoteChange = (value: "proponente" | "ativacao") => {
    markBronzeFieldDirty("origem_lote");
    if (
      value === "ativacao" &&
      bronzeEventoId &&
      !bronzeEventoSupportsActivationImport
    ) {
      setBronzeOrigemLote("proponente");
      setBronzeAtivacaoId("");
      setBronzePendingHintAtivacaoId(null);
      return;
    }

    setBronzeOrigemLote(value);
    if (value === "proponente") {
      setBronzeAtivacaoId("");
      setBronzePendingHintAtivacaoId(null);
    }
  };

  const handleBronzeTipoLeadProponenteChange = (value: "bilheteria" | "entrada_evento") => {
    markBronzeFieldDirty("tipo_lead_proponente");
    setBronzeTipoLeadProponente(value);
  };

  const handleBronzeAtivacaoIdChange = (value: string) => {
    markBronzeFieldDirty("ativacao_id");
    setBronzePendingHintAtivacaoId(null);
    setBronzeAtivacaoId(value);
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
      handleBronzeAtivacaoIdChange(String(created.id));

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
      handleBronzeEventoIdChange(String(created.id));
      setBronzeAtivacaoId("");
      setAtivacoes([]);
    }

    setQuickCreateTarget(null);
  };

  const handleSelectFile = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] ?? null;
    event.target.value = "";
    setError(null);
    setFile(nextFile);
    resetBronzeImportHintState();
    resetBronzeFlow();
    resetEtlPreviewOnly();
    setEtlSheetName("");
    setEtlMaxScanRows("");
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
      const maxParsed =
        etlMaxScanRows.trim() === "" ? undefined : Math.floor(Number(etlMaxScanRows));
      const merged = {
        ...(etlSheetName.trim() ? { sheetName: etlSheetName.trim() } : {}),
        ...(maxParsed != null && Number.isFinite(maxParsed) ? { maxScanRows: maxParsed } : {}),
        ...options,
      };
      const queued = etlJobPolling.jobId
        ? await reprocessLeadImportEtlJobPreview(token, etlJobPolling.jobId, merged)
        : await startLeadImportEtlJob(token, file, Number(eventoId), false, merged);
      etlJobPolling.beginPolling(queued.job_id);
      setEtlPreview(null);
      setActiveStep(1);
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao gerar preview ETL."));
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
      const result = await createLeadBatchIntake(token, {
        items: [
          {
            client_row_id: "single-upload",
            plataforma_origem: plataformaOrigem,
            data_envio: dataEnvio,
            evento_id: Number(bronzeEventoId),
            file,
            origem_lote: bronzeOrigemLote,
            tipo_lead_proponente:
              bronzeOrigemLote === "proponente" ? bronzeTipoLeadProponente : undefined,
            ativacao_id:
              bronzeOrigemLote === "ativacao" ? Number(bronzeAtivacaoId) : undefined,
          },
        ],
      });
      const created = result.items[0];
      setBatch(created.batch);
      setPreview(created.preview);
      if (created.hint_applied) {
        applyBronzeImportHint(created.hint_applied);
      } else {
        setBronzeImportHint(null);
      }
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
    if (!token || !etlJobPolling.jobId || !etlPreview || etlPreview.status !== "previewed") return;
    setCommittingEtl(true);
    setError(null);
    try {
      const queued = await commitLeadImportEtlJob(token, etlJobPolling.jobId, forceWarnings);
      etlJobPolling.beginPolling(queued.job_id);
    } catch (err: unknown) {
      if (!forceWarnings && err instanceof ApiError && err.code === "ETL_COMMIT_BLOCKED") {
        setEtlWarningsPending(true);
        setError(null);
      } else {
        setEtlWarningsPending(false);
        setError(toApiErrorMessage(err, "Falha ao importar leads do preview ETL."));
      }
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
          shouldUseBatchMappingShell ? (
            <BatchMapeamentoPage
              batchIds={batchMappingBatchIds}
              primaryBatchId={routeBatchId}
              cancelLabel="Voltar ao batch"
              onCancel={() => {
                setCanonicalStep("upload");
              }}
              onMapped={(result) => {
                batchUpload.markRowsMapped(result.batch_ids);
                setCanonicalStep("pipeline", result.primary_batch_id, "batch");
              }}
            />
          ) : loadingMappingBatch ? (
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
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                <Button variant="outlined" onClick={() => void handleReturnToBatchWorkspace()}>
                  Voltar ao batch
                </Button>
                {currentBatchIsTerminal && nextBatchWorkspaceRow && nextBatchWorkspaceLabel ? (
                  <Button variant="contained" onClick={() => handleOpenBatchRowFlow(nextBatchWorkspaceRow)}>
                    {nextBatchWorkspaceLabel}
                  </Button>
                ) : null}
              </Box>
            ) : null}
            <PipelineStatusPage
              batchId={routeBatchId}
              onBatchLoaded={hasBatchWorkspaceContext ? (loadedBatch) => batchUpload.syncCreatedBatch(loadedBatch) : undefined}
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
            bronzeMetadataHintMessage={
              bronzeImportHint
                ? "Metadados recuperados de uma importacao anterior (mesmo ficheiro)."
                : null
            }
            bronzeMetadataHintSourceBatchId={bronzeImportHint?.source_batch_id ?? null}
            bronzeMode={bronzeMode}
            bronzeOrigemLote={bronzeOrigemLote}
            bronzeTipoLeadProponente={bronzeTipoLeadProponente}
            canSubmit={canSubmit}
            committingEtl={committingEtl}
            dataEnvio={dataEnvio}
            etlCommitResult={etlCommitResult}
            etlCpfColumnIndex={etlCpfColumnIndex}
            etlHeaderRow={etlHeaderRow}
            etlMaxScanRows={etlMaxScanRows}
            etlPreview={etlPreview}
            etlSheetName={etlSheetName}
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
            onBronzeAtivacaoIdChange={handleBronzeAtivacaoIdChange}
            onBronzeEventoIdChange={handleBronzeEventoIdChange}
            onBronzeModeChange={(nextMode) => {
              setBronzeMode(nextMode);
              resetBronzeImportHintState();
              resetBronzeFlow();
              setError(null);
            }}
            onBronzeOrigemLoteChange={handleBronzeOrigemLoteChange}
            onBronzeTipoLeadProponenteChange={handleBronzeTipoLeadProponenteChange}
            onCommitEtl={handleCommitEtl}
            onCpfColumnChange={setEtlCpfColumnIndex}
            onCpfColumnSubmit={handleSubmitCpfColumn}
            onCreateAtivacaoAdHoc={handleCreateAtivacaoAdHoc}
            onDataEnvioChange={handleBronzeDataEnvioChange}
            onEventoIdChange={setEventoId}
            onFileChange={handleSelectFile}
            onGoToMapping={() => {
              if (batch) {
                setCanonicalStep("mapping", batch.id);
              }
            }}
            onEtlMaxScanRowsChange={setEtlMaxScanRows}
            onEtlSheetNameChange={setEtlSheetName}
            onHeaderRowChange={setEtlHeaderRow}
            onHeaderRowSubmit={handleSubmitHeaderRow}
            onImportFlowChange={resetForNewImport}
            onOpenQuickCreateEvento={handleOpenQuickCreateEvento}
            onPlataformaOrigemChange={handleBronzePlataformaOrigemChange}
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
