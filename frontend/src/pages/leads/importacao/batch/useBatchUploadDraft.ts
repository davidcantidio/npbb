import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";

import { Agencia, listAgencias } from "../../../../services/agencias";
import { toApiErrorMessage } from "../../../../services/http";
import {
  computeFileSha256Hex,
  DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON,
  LeadBatch,
  LeadImportMetadataHint,
  ReferenciaEvento,
  createLeadBatch,
  getActivationImportBlockReason,
  getLeadImportMetadataHint,
  normalizeLeadImportHintDateInput,
  supportsActivationImport,
  type OrigemLoteLeadBatch,
} from "../../../../services/leads_import";
import { EventoRead, updateEvento } from "../../../../services/eventos/core";
import { createEventoAtivacao, listEventoAtivacoes } from "../../../../services/eventos/workflow";
import { LEADS_IMPORT_ALLOWED_EXTENSIONS } from "../constants";

export type BronzeMode = "single" | "batch";

export type BatchUploadRowStatus = "draft" | "submitting" | "created" | "error";

export type BatchUploadAtivacaoOption = {
  id: number;
  nome: string;
};

export type BatchUploadHintEditableField =
  | "plataforma_origem"
  | "data_envio"
  | "evento_id"
  | "origem_lote"
  | "tipo_lead_proponente"
  | "ativacao_id";

export type BatchUploadRowDraft = {
  local_id: string;
  file: File;
  file_name: string;
  quem_enviou: string;
  plataforma_origem: string;
  data_envio: string;
  evento_id: string;
  origem_lote: OrigemLoteLeadBatch;
  tipo_lead_proponente: "bilheteria" | "entrada_evento";
  ativacao_id: string;
  status_ui: BatchUploadRowStatus;
  created_batch_id: number | null;
  error_message: string | null;
  downstream_stage: LeadBatch["stage"] | null;
  downstream_pipeline_status: LeadBatch["pipeline_status"] | null;
  last_synced_at: string | null;
  dirty_fields: Partial<Record<BatchUploadHintEditableField, boolean>>;
  metadata_hint_message: string | null;
  metadata_hint_source_batch_id: number | null;
  pending_hint_ativacao_id: string | null;
};

type UseBatchUploadDraftParams = {
  token: string | null;
  defaultQuemEnviou: string;
  defaultDataEnvio: string;
  eventos: ReferenciaEvento[];
  setEventos: Dispatch<SetStateAction<ReferenciaEvento[]>>;
};

function parseOptionalId(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function hasAllowedExtension(file: File) {
  const normalizedName = file.name.toLowerCase();
  return LEADS_IMPORT_ALLOWED_EXTENSIONS.some((extension) => normalizedName.endsWith(extension));
}

function mapAtivacoesToOptions(items: Array<{ id: number; nome: string }>): BatchUploadAtivacaoOption[] {
  return items.map((item) => ({ id: item.id, nome: item.nome }));
}

function upsertAtivacaoOption(
  prev: BatchUploadAtivacaoOption[] | undefined,
  next: BatchUploadAtivacaoOption,
) {
  if (!prev || prev.length === 0) {
    return [next];
  }
  if (prev.some((item) => item.id === next.id)) {
    return prev.map((item) => (item.id === next.id ? next : item));
  }
  return [...prev, next];
}

function buildReferenciaEventoFromEvento(evento: Pick<EventoRead, "id" | "nome" | "data_inicio_prevista" | "agencia_id">) {
  const supportsActivation = evento.agencia_id != null;
  return {
    id: evento.id,
    nome: evento.nome,
    data_inicio_prevista: evento.data_inicio_prevista ?? null,
    agencia_id: evento.agencia_id ?? null,
    supports_activation_import: supportsActivation,
    activation_import_block_reason: supportsActivation ? null : DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON,
    leads_count: 0,
  } satisfies ReferenciaEvento;
}

function upsertReferenciaEvento(prev: ReferenciaEvento[], next: ReferenciaEvento) {
  const current = prev.find((item) => item.id === next.id);
  if (!current) {
    return [next, ...prev];
  }
  return prev.map((item) =>
    item.id === next.id
      ? {
          ...item,
          ...next,
          leads_count: item.leads_count ?? next.leads_count ?? 0,
        }
      : item,
  );
}

function nextEditableStatus(status: BatchUploadRowStatus) {
  return status === "error" ? "draft" : status;
}

function nowIsoString() {
  return new Date().toISOString();
}

function buildBatchMetadataHintMessage(sourceBatchId: number) {
  return `Metadados recuperados de uma importacao anterior (lote #${sourceBatchId}).`;
}

function createDraftRow(params: {
  localId: string;
  file: File;
  defaultQuemEnviou: string;
  defaultDataEnvio: string;
}): BatchUploadRowDraft {
  return {
    local_id: params.localId,
    file: params.file,
    file_name: params.file.name,
    quem_enviou: params.defaultQuemEnviou,
    plataforma_origem: "",
    data_envio: params.defaultDataEnvio,
    evento_id: "",
    origem_lote: "proponente",
    tipo_lead_proponente: "entrada_evento",
    ativacao_id: "",
    status_ui: "draft",
    created_batch_id: null,
    error_message: null,
    downstream_stage: null,
    downstream_pipeline_status: null,
    last_synced_at: null,
    dirty_fields: {},
    metadata_hint_message: null,
    metadata_hint_source_batch_id: null,
    pending_hint_ativacao_id: null,
  };
}

const BATCH_HINT_EDITABLE_FIELDS: BatchUploadHintEditableField[] = [
  "plataforma_origem",
  "data_envio",
  "evento_id",
  "origem_lote",
  "tipo_lead_proponente",
  "ativacao_id",
];

function markDirtyFields(
  row: BatchUploadRowDraft,
  patch: Partial<BatchUploadRowDraft>,
) {
  const nextDirtyFields = { ...row.dirty_fields };

  BATCH_HINT_EDITABLE_FIELDS.forEach((field) => {
    if (!Object.prototype.hasOwnProperty.call(patch, field)) return;
    if (patch[field] === row[field]) return;
    nextDirtyFields[field] = true;
  });

  return nextDirtyFields;
}

async function runWithConcurrency<T>(
  items: T[],
  limit: number,
  worker: (item: T) => Promise<void>,
) {
  const concurrency = Math.max(1, Math.min(limit, items.length));
  let cursor = 0;

  await Promise.all(
    Array.from({ length: concurrency }, async () => {
      while (cursor < items.length) {
        const item = items[cursor];
        cursor += 1;
        await worker(item);
      }
    }),
  );
}

export function getBatchRowSelectedEvento(
  eventos: ReferenciaEvento[],
  eventoId: string,
) {
  const parsedId = parseOptionalId(eventoId);
  if (parsedId == null) return null;
  return eventos.find((evento) => evento.id === parsedId) ?? null;
}

export function getBatchRowValidationErrors(params: {
  row: BatchUploadRowDraft;
  selectedEvento: ReferenciaEvento | null;
  ativacoes?: BatchUploadAtivacaoOption[];
  ativacoesLoadError?: string | null;
}) {
  const { row, selectedEvento, ativacoes, ativacoesLoadError } = params;
  const errors: string[] = [];

  if (!hasAllowedExtension(row.file)) {
    errors.push("Formato de arquivo invalido. Use CSV ou XLSX.");
  }
  if (!row.quem_enviou.trim()) {
    errors.push("Preencha quem enviou.");
  }
  if (!row.plataforma_origem.trim()) {
    errors.push("Selecione a plataforma de origem.");
  }
  if (!row.data_envio) {
    errors.push("Preencha a data de envio.");
  }
  if (!parseOptionalId(row.evento_id)) {
    errors.push("Selecione o evento de referencia.");
  }

  if (row.origem_lote === "ativacao") {
    const blockReason =
      getActivationImportBlockReason(selectedEvento) ??
      (selectedEvento && !supportsActivationImport(selectedEvento)
        ? DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON
        : null);

    if (blockReason) {
      errors.push(blockReason);
    } else if (ativacoesLoadError) {
      errors.push(ativacoesLoadError);
    } else if (!parseOptionalId(row.ativacao_id)) {
      errors.push("Selecione a ativacao desta importacao.");
    } else if (ativacoes && ativacoes.length > 0) {
      const ativacaoId = parseOptionalId(row.ativacao_id);
      if (!ativacoes.some((ativacao) => ativacao.id === ativacaoId)) {
        errors.push("Selecione uma ativacao valida para o evento.");
      }
    }
  } else if (!["entrada_evento", "bilheteria"].includes(row.tipo_lead_proponente)) {
    errors.push("Selecione um tipo de lead do proponente.");
  }

  return [...new Set(errors)];
}

export function useBatchUploadDraft({
  token,
  defaultQuemEnviou,
  defaultDataEnvio,
  eventos,
  setEventos,
}: UseBatchUploadDraftParams) {
  const nextRowIdRef = useRef(0);
  const agenciasRequestIdRef = useRef(0);
  const mountedRef = useRef(true);
  const [rows, setRows] = useState<BatchUploadRowDraft[]>([]);
  const [ativacoesByEventoId, setAtivacoesByEventoId] = useState<Record<number, BatchUploadAtivacaoOption[]>>({});
  const [ativacoesLoadErrorByEventoId, setAtivacoesLoadErrorByEventoId] = useState<Record<number, string | null>>({});
  const [loadingAtivacoesByEventoId, setLoadingAtivacoesByEventoId] = useState<Record<number, boolean>>({});
  const [agencias, setAgencias] = useState<Agencia[]>([]);
  const [loadingAgencias, setLoadingAgencias] = useState(false);
  const [agenciasLoadError, setAgenciasLoadError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (loadingAgencias || agencias.length > 0) return;

    const needsAgencyEditor = rows.some((row) => {
      if (row.origem_lote !== "ativacao") return false;
      const selectedEvento = getBatchRowSelectedEvento(eventos, row.evento_id);
      return Boolean(selectedEvento && !supportsActivationImport(selectedEvento));
    });

    if (!needsAgencyEditor) return;

    const requestId = agenciasRequestIdRef.current + 1;
    agenciasRequestIdRef.current = requestId;
    setLoadingAgencias(true);
    setAgenciasLoadError(null);

    listAgencias({ limit: 200 })
      .then((items) => {
        if (!mountedRef.current || agenciasRequestIdRef.current !== requestId) return;
        setAgencias(items);
      })
      .catch((error) => {
        if (!mountedRef.current || agenciasRequestIdRef.current !== requestId) return;
        setAgencias([]);
        setAgenciasLoadError(toApiErrorMessage(error, "Nao foi possivel carregar as agencias."));
      })
      .finally(() => {
        if (!mountedRef.current || agenciasRequestIdRef.current !== requestId) return;
        setLoadingAgencias(false);
      });
  }, [agencias.length, eventos, rows]);

  useEffect(() => {
    if (!token) return;

    const eventIdsToLoad = new Set<number>();

    rows.forEach((row) => {
      if (row.origem_lote !== "ativacao") return;
      const eventId = parseOptionalId(row.evento_id);
      if (eventId == null) return;
      const selectedEvento = getBatchRowSelectedEvento(eventos, row.evento_id);
      if (!selectedEvento || !supportsActivationImport(selectedEvento)) return;
      if (Object.prototype.hasOwnProperty.call(ativacoesByEventoId, eventId) || loadingAtivacoesByEventoId[eventId]) {
        return;
      }
      eventIdsToLoad.add(eventId);
    });

    eventIdsToLoad.forEach((eventId) => {
      setLoadingAtivacoesByEventoId((prev) => ({ ...prev, [eventId]: true }));
      setAtivacoesLoadErrorByEventoId((prev) => ({ ...prev, [eventId]: null }));
      listEventoAtivacoes(token, eventId)
        .then((items) => {
          setAtivacoesByEventoId((prev) => ({
            ...prev,
            [eventId]: mapAtivacoesToOptions(items),
          }));
          setAtivacoesLoadErrorByEventoId((prev) => ({ ...prev, [eventId]: null }));
        })
        .catch((error) => {
          setAtivacoesByEventoId((prev) => ({ ...prev, [eventId]: prev[eventId] ?? [] }));
          setAtivacoesLoadErrorByEventoId((prev) => ({
            ...prev,
            [eventId]: toApiErrorMessage(error, "Nao foi possivel carregar as ativacoes deste evento."),
          }));
        })
        .finally(() => {
          setLoadingAtivacoesByEventoId((prev) => ({ ...prev, [eventId]: false }));
        });
    });
  }, [ativacoesByEventoId, eventos, loadingAtivacoesByEventoId, rows, token]);

  useEffect(() => {
    setRows((prev) => {
      let changed = false;

      const nextRows = prev.map((row) => {
        if (!row.pending_hint_ativacao_id || row.origem_lote !== "ativacao") {
          return row;
        }

        const eventId = parseOptionalId(row.evento_id);
        if (eventId == null || row.dirty_fields.ativacao_id) {
          changed = true;
          return {
            ...row,
            pending_hint_ativacao_id: null,
          };
        }

        if (loadingAtivacoesByEventoId[eventId]) {
          return row;
        }

        const ativacoes = ativacoesByEventoId[eventId] ?? [];
        if (ativacoes.some((ativacao) => String(ativacao.id) === row.pending_hint_ativacao_id)) {
          changed = true;
          return {
            ...row,
            ativacao_id: row.pending_hint_ativacao_id,
            pending_hint_ativacao_id: null,
          };
        }

        if (
          ativacoesLoadErrorByEventoId[eventId] ||
          Object.prototype.hasOwnProperty.call(ativacoesByEventoId, eventId)
        ) {
          changed = true;
          return {
            ...row,
            pending_hint_ativacao_id: null,
          };
        }

        return row;
      });

      return changed ? nextRows : prev;
    });
  }, [ativacoesByEventoId, ativacoesLoadErrorByEventoId, loadingAtivacoesByEventoId]);

  function updateRowInternal(
    localId: string,
    patch: Partial<BatchUploadRowDraft>,
    options?: { markDirty?: boolean },
  ) {
    setRows((prev) =>
      prev.map((row) => {
        if (row.local_id !== localId || row.status_ui === "created" || row.status_ui === "submitting") {
          return row;
        }

        const nextRow: BatchUploadRowDraft = {
          ...row,
          ...patch,
          status_ui: nextEditableStatus(row.status_ui),
          error_message: null,
          dirty_fields: options?.markDirty ? markDirtyFields(row, patch) : row.dirty_fields,
        };

        if (patch.evento_id !== undefined && patch.evento_id !== row.evento_id) {
          nextRow.ativacao_id = "";
          if (patch.pending_hint_ativacao_id === undefined) {
            nextRow.pending_hint_ativacao_id = null;
          }
        }
        if (patch.origem_lote === "proponente") {
          nextRow.ativacao_id = "";
          if (patch.pending_hint_ativacao_id === undefined) {
            nextRow.pending_hint_ativacao_id = null;
          }
        }
        if (options?.markDirty && patch.ativacao_id !== undefined && patch.ativacao_id !== row.ativacao_id) {
          nextRow.pending_hint_ativacao_id = null;
        }

        return nextRow;
      }),
    );
  }

  function updateRow(localId: string, patch: Partial<BatchUploadRowDraft>) {
    updateRowInternal(localId, patch, { markDirty: true });
  }

  function applyMetadataHint(localId: string, hint: LeadImportMetadataHint) {
    setRows((prev) =>
      prev.map((row) => {
        if (row.local_id !== localId || row.status_ui === "created" || row.status_ui === "submitting") {
          return row;
        }

        const nextRow: BatchUploadRowDraft = {
          ...row,
          status_ui: nextEditableStatus(row.status_ui),
          error_message: null,
          metadata_hint_message: buildBatchMetadataHintMessage(hint.source_batch_id),
          metadata_hint_source_batch_id: hint.source_batch_id,
        };

        if (!row.dirty_fields.plataforma_origem) {
          nextRow.plataforma_origem = hint.plataforma_origem;
        }

        if (!row.dirty_fields.data_envio) {
          const normalizedDate = normalizeLeadImportHintDateInput(hint.data_envio);
          if (normalizedDate) {
            nextRow.data_envio = normalizedDate;
          }
        }

        const nextEventoId = hint.evento_id != null ? String(hint.evento_id) : "";
        const shouldApplyEvento = !row.dirty_fields.evento_id;
        if (shouldApplyEvento) {
          if (nextEventoId !== row.evento_id) {
            nextRow.evento_id = nextEventoId;
            nextRow.ativacao_id = "";
          }
        }

        const canApplyLinkedMetadata = !row.dirty_fields.evento_id || row.evento_id === nextEventoId;
        const shouldApplyOrigem = canApplyLinkedMetadata && !row.dirty_fields.origem_lote;
        if (shouldApplyOrigem) {
          nextRow.origem_lote = hint.origem_lote;
          if (hint.origem_lote === "proponente") {
            nextRow.ativacao_id = "";
          }
        }

        const effectiveOrigem = shouldApplyOrigem ? hint.origem_lote : nextRow.origem_lote;
        if (canApplyLinkedMetadata && effectiveOrigem === "proponente") {
          if (!row.dirty_fields.tipo_lead_proponente && hint.tipo_lead_proponente) {
            nextRow.tipo_lead_proponente = hint.tipo_lead_proponente;
          }
          if (!row.dirty_fields.ativacao_id) {
            nextRow.ativacao_id = "";
            nextRow.pending_hint_ativacao_id = null;
          }
        } else if (canApplyLinkedMetadata && !row.dirty_fields.ativacao_id) {
          nextRow.ativacao_id = "";
          nextRow.pending_hint_ativacao_id =
            hint.ativacao_id != null ? String(hint.ativacao_id) : null;
        }

        return nextRow;
      }),
    );
  }

  function reset() {
    setRows([]);
    setAtivacoesByEventoId({});
    setAtivacoesLoadErrorByEventoId({});
    setLoadingAtivacoesByEventoId({});
  }

  function addFiles(nextFiles: FileList | File[]) {
    const fileList = Array.from(nextFiles);
    if (fileList.length === 0) return;

    const nextRows = fileList.map((file) => {
      nextRowIdRef.current += 1;
      return createDraftRow({
        localId: `batch-upload-row-${nextRowIdRef.current}`,
        file,
        defaultQuemEnviou,
        defaultDataEnvio,
      });
    });

    setRows((prev) => [...prev, ...nextRows]);

    if (!token) return;

    void runWithConcurrency(nextRows, 3, async (row) => {
      try {
        const arquivoSha256 = await computeFileSha256Hex(row.file);
        const hint = await getLeadImportMetadataHint(token, arquivoSha256);
        if (!hint) return;
        applyMetadataHint(row.local_id, hint);
      } catch {
        // Hint e hash sao best-effort: falhas nao devem bloquear o envio manual.
      }
    });
  }

  function removeRow(localId: string) {
    setRows((prev) => prev.filter((row) => row.local_id !== localId));
  }

  function setRowError(localId: string, message: string) {
    setRows((prev) =>
      prev.map((row) => {
        if (row.local_id !== localId || row.status_ui === "created" || row.status_ui === "submitting") {
          return row;
        }
        return {
          ...row,
          status_ui: nextEditableStatus(row.status_ui),
          error_message: message,
        };
      }),
    );
  }

  function attachCreatedEvento(localId: string, evento: EventoRead) {
    updateRowInternal(localId, {
      evento_id: String(evento.id),
      ativacao_id: "",
      pending_hint_ativacao_id: null,
    }, { markDirty: true });
  }

  function markRowsMapped(batchIds: number[]) {
    const targetBatchIds = new Set(batchIds);
    if (targetBatchIds.size === 0) return;
    const syncedAt = nowIsoString();
    setRows((prev) =>
      prev.map((row) =>
        row.created_batch_id != null && targetBatchIds.has(row.created_batch_id)
          ? {
              ...row,
              downstream_stage: "silver",
              downstream_pipeline_status: "pending",
              last_synced_at: syncedAt,
            }
          : row,
      ),
    );
  }

  function markRowMapped(batchId: number) {
    markRowsMapped([batchId]);
  }

  function syncCreatedBatch(batch: LeadBatch | null | undefined) {
    if (!batch || !Number.isFinite(batch.id)) {
      return;
    }
    const syncedAt = nowIsoString();
    setRows((prev) =>
      prev.map((row) =>
        row.created_batch_id === batch.id
          ? {
              ...row,
              downstream_stage: batch.stage,
              downstream_pipeline_status: batch.pipeline_status,
              last_synced_at: syncedAt,
            }
          : row,
      ),
    );
  }

  async function createAdHocAtivacao(localId: string, nome: string) {
    try {
      if (!token) {
        throw new Error("Sessao expirada. Faca login novamente.");
      }

      const row = rows.find((item) => item.local_id === localId);
      const eventId = parseOptionalId(row?.evento_id ?? "");
      if (!row || eventId == null) {
        throw new Error("Selecione o evento da linha antes de criar a ativacao.");
      }

      const created = await createEventoAtivacao(token, eventId, { nome });
      const createdOption = { id: created.id, nome: created.nome };

      setAtivacoesByEventoId((prev) => ({
        ...prev,
        [eventId]: upsertAtivacaoOption(prev[eventId], createdOption),
      }));
      setAtivacoesLoadErrorByEventoId((prev) => ({ ...prev, [eventId]: null }));
      updateRowInternal(
        localId,
        {
          ativacao_id: String(created.id),
          pending_hint_ativacao_id: null,
        },
        { markDirty: true },
      );

      void listEventoAtivacoes(token, eventId)
        .then((items) => {
          setAtivacoesByEventoId((prev) => ({
            ...prev,
            [eventId]: mapAtivacoesToOptions(items),
          }));
          setAtivacoesLoadErrorByEventoId((prev) => ({ ...prev, [eventId]: null }));
        })
        .catch(() => {
          // Preserve the optimistic option when the refresh fails after a successful creation.
        });

      return created;
    } catch (error) {
      setRowError(localId, toApiErrorMessage(error, "Falha ao criar ativacao."));
      throw error;
    }
  }

  async function saveEventoAgency(localId: string, agenciaId: number) {
    try {
      if (!token) {
        throw new Error("Sessao expirada. Faca login novamente.");
      }

      const row = rows.find((item) => item.local_id === localId);
      const eventId = parseOptionalId(row?.evento_id ?? "");
      if (!row || eventId == null) {
        throw new Error("Selecione o evento da linha antes de atualizar a agencia.");
      }

      const updated = await updateEvento(token, eventId, { agencia_id: agenciaId });
      const referenciaAtualizada = buildReferenciaEventoFromEvento(updated);

      setEventos((prev) => upsertReferenciaEvento(prev, referenciaAtualizada));
      updateRowInternal(localId, { evento_id: String(updated.id) }, { markDirty: true });
    } catch (error) {
      setRowError(localId, toApiErrorMessage(error, "Falha ao salvar a agencia do evento."));
      throw error;
    }
  }

  async function submitRows(localIds?: string[]) {
    const targetRows = rows.filter((row) => {
      if (row.status_ui === "created" || row.status_ui === "submitting") return false;
      return !localIds || localIds.includes(row.local_id);
    });

    if (!token) {
      if (targetRows.length === 0) return;
      const targetLocalIds = new Set(targetRows.map((row) => row.local_id));
      setRows((prev) =>
        prev.map((row) =>
          targetLocalIds.has(row.local_id)
            ? {
                ...row,
                status_ui: "error",
                error_message: "Sessao expirada. Faca login novamente.",
              }
            : row,
        ),
      );
      return;
    }

    if (targetRows.length === 0) return;

    const validationMap = new Map(
      targetRows.map((row) => {
        const selectedEvento = getBatchRowSelectedEvento(eventos, row.evento_id);
        const eventId = parseOptionalId(row.evento_id);
        const ativacoes = eventId != null ? ativacoesByEventoId[eventId] : undefined;
        const ativacoesLoadError = eventId != null ? ativacoesLoadErrorByEventoId[eventId] : null;
        const errors = getBatchRowValidationErrors({ row, selectedEvento, ativacoes, ativacoesLoadError });
        return [row.local_id, errors] as const;
      }),
    );

    setRows((prev) =>
      prev.map((row) => {
        const errors = validationMap.get(row.local_id);
        if (!errors) return row;
        if (errors.length === 0) {
          return {
            ...row,
            status_ui: nextEditableStatus(row.status_ui),
            error_message: null,
          };
        }
        return {
          ...row,
          status_ui: "error",
          error_message: errors.join(" "),
        };
      }),
    );

    const validRows = targetRows.filter((row) => (validationMap.get(row.local_id) ?? []).length === 0);
    if (validRows.length === 0) return;

    await runWithConcurrency(validRows, 3, async (row) => {
      setRows((prev) =>
        prev.map((current) =>
          current.local_id === row.local_id
            ? {
                ...current,
                status_ui: "submitting",
                error_message: null,
              }
            : current,
        ),
      );

      try {
        const createdBatch = await createLeadBatch(token, {
          quem_enviou: row.quem_enviou.trim(),
          plataforma_origem: row.plataforma_origem,
          data_envio: row.data_envio,
          evento_id: Number(row.evento_id),
          file: row.file,
          origem_lote: row.origem_lote,
          tipo_lead_proponente:
            row.origem_lote === "proponente" ? row.tipo_lead_proponente : undefined,
          ativacao_id:
            row.origem_lote === "ativacao" ? Number(row.ativacao_id) : undefined,
        });

        setRows((prev) =>
          prev.map((current) =>
            current.local_id === row.local_id
              ? {
                  ...current,
                  status_ui: "created",
                  created_batch_id: createdBatch.id,
                  error_message: null,
                  downstream_stage: createdBatch.stage,
                  downstream_pipeline_status: createdBatch.pipeline_status,
                  last_synced_at: nowIsoString(),
                }
              : current,
          ),
        );
      } catch (error) {
        setRows((prev) =>
          prev.map((current) =>
            current.local_id === row.local_id
              ? {
                  ...current,
                  status_ui: "error",
                  error_message: toApiErrorMessage(error, "Falha ao enviar a linha para o Bronze."),
                }
              : current,
          ),
        );
      }
    });
  }

  function retryRow(localId: string) {
    return submitRows([localId]);
  }

  return {
    rows,
    ativacoesByEventoId,
    ativacoesLoadErrorByEventoId,
    loadingAtivacoesByEventoId,
    agencias,
    loadingAgencias,
    agenciasLoadError,
    reset,
    addFiles,
    removeRow,
    updateRow,
    attachCreatedEvento,
    markRowMapped,
    markRowsMapped,
    syncCreatedBatch,
    createAdHocAtivacao,
    saveEventoAgency,
    submitRows,
    retryRow,
  };
}
