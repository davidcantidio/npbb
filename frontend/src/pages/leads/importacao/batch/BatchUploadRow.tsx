import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  TableCell,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { Agencia } from "../../../../services/agencias";
import {
  DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON,
  ReferenciaEvento,
  getActivationImportBlockReason,
  supportsActivationImport,
} from "../../../../services/leads_import";
import { formatReferenciaEventoOptionLabel } from "../../../../utils/formatters";
import { LEADS_IMPORT_PLATFORMS, QUICK_CREATE_EVENTO_ID } from "../constants";
import {
  BronzeImportMode,
  getBronzeImportModeHelpText,
  getBronzeImportModeLabel,
  getBronzeImportModeSummary,
} from "../bronzeImportMode";
import InlineEventoAgencyEditor from "./InlineEventoAgencyEditor";
import { BatchUploadAtivacaoOption, BatchUploadRowDraft } from "./useBatchUploadDraft";

type Props = {
  row: BatchUploadRowDraft;
  eventos: ReferenciaEvento[];
  selectedEvento: ReferenciaEvento | null;
  ativacoes: BatchUploadAtivacaoOption[];
  ativacoesLoadError: string | null;
  loadingAtivacoes: boolean;
  agencias: Agencia[];
  loadingAgencias: boolean;
  agenciasLoadError: string | null;
  validationMessages: string[];
  onFieldChange: (localId: string, patch: Partial<BatchUploadRowDraft>) => void;
  onOpenQuickCreateEvento: (localId: string) => void;
  onCreateAtivacao: (localId: string, nome: string) => Promise<unknown>;
  onSaveAgency: (localId: string, agenciaId: number) => Promise<void>;
  onRemove: (localId: string) => void;
  onRetry: (localId: string) => Promise<void>;
  onOpenRowFlow: (row: BatchUploadRowDraft) => void;
};

function rowStatusLabel(status: BatchUploadRowDraft["status_ui"]) {
  if (status === "created") return "Criado";
  if (status === "submitting") return "Enviando";
  if (status === "error") return "Erro";
  return "Rascunho";
}

function rowStatusColor(status: BatchUploadRowDraft["status_ui"]) {
  if (status === "created") return "success";
  if (status === "submitting") return "info";
  if (status === "error") return "error";
  return "default";
}

function downstreamStatusLabel(row: BatchUploadRowDraft) {
  if (row.created_batch_id == null) return null;
  if (row.downstream_pipeline_status === "pass") return "Fluxo: Pipeline aprovado";
  if (row.downstream_pipeline_status === "pass_with_warnings") return "Fluxo: Pipeline com avisos";
  if (row.downstream_pipeline_status === "stalled") return "Fluxo: Pipeline interrompido (retomavel)";
  if (row.downstream_pipeline_status === "fail") return "Fluxo: Pipeline reprovado";
  if (row.downstream_stage === "gold") return "Fluxo: Gold gerado";
  if (row.downstream_stage === "silver") return "Fluxo: Pronto para pipeline";
  return "Fluxo: Aguardando mapeamento do batch";
}

function downstreamStatusColor(row: BatchUploadRowDraft) {
  if (row.downstream_pipeline_status === "pass" || row.downstream_stage === "gold") return "success";
  if (row.downstream_pipeline_status === "pass_with_warnings") return "warning";
  if (row.downstream_pipeline_status === "stalled") return "warning";
  if (row.downstream_pipeline_status === "fail") return "error";
  if (row.downstream_stage === "silver") return "info";
  return "default";
}

function rowFlowActionLabel(row: BatchUploadRowDraft) {
  if (row.created_batch_id == null) return null;
  return row.downstream_stage === "bronze" || row.downstream_stage == null
    ? "Abrir mapeamento do batch"
    : "Abrir pipeline";
}

export default function BatchUploadRow({
  row,
  eventos,
  selectedEvento,
  ativacoes,
  ativacoesLoadError,
  loadingAtivacoes,
  agencias,
  loadingAgencias,
  agenciasLoadError,
  validationMessages,
  onFieldChange,
  onOpenQuickCreateEvento,
  onCreateAtivacao,
  onSaveAgency,
  onRemove,
  onRetry,
  onOpenRowFlow,
}: Props) {
  const [ativacaoDialogOpen, setAtivacaoDialogOpen] = useState(false);
  const [ativacaoNome, setAtivacaoNome] = useState("");
  const [ativacaoSaving, setAtivacaoSaving] = useState(false);
  const [ativacaoDialogError, setAtivacaoDialogError] = useState<string | null>(null);

  const isReadonly = row.status_ui === "created" || row.status_ui === "submitting";
  const isEnrichmentOnly = row.import_mode === "enrichment_only";
  const activationImportBlocked =
    !isEnrichmentOnly &&
    row.origem_lote === "ativacao" &&
    selectedEvento != null &&
    !supportsActivationImport(selectedEvento);
  const activationBlockReason =
    getActivationImportBlockReason(selectedEvento) ??
    (activationImportBlocked ? DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON : null);
  const showAgencyEditor = Boolean(activationImportBlocked && selectedEvento);
  const pendingMessages = row.error_message ? [row.error_message] : validationMessages;
  const visiblePendingMessages =
    showAgencyEditor && activationBlockReason
      ? pendingMessages.filter((message) => message !== activationBlockReason && message !== ativacoesLoadError)
      : ativacoesLoadError
        ? pendingMessages.filter((message) => message !== ativacoesLoadError)
      : pendingMessages;
  const pendingMessagesColor = row.error_message || row.status_ui === "error" ? "error.main" : "warning.main";
  const flowStatusLabel = downstreamStatusLabel(row);
  const flowActionLabel = rowFlowActionLabel(row);

  return (
    <>
      <TableRow hover>
        <TableCell sx={{ minWidth: 180 }}>
          <Stack spacing={0.5}>
            <Typography variant="body2" fontWeight={600}>
              {row.file_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {Math.max(1, Math.round(row.file.size / 1024))} KB
            </Typography>
          </Stack>
        </TableCell>

        <TableCell sx={{ minWidth: 180 }}>
          <TextField
            label="Quem enviou"
            size="small"
            value={row.quem_enviou}
            onChange={(event) => onFieldChange(row.local_id, { quem_enviou: event.target.value })}
            disabled={isReadonly}
            fullWidth
          />
        </TableCell>

        <TableCell sx={{ minWidth: 150 }}>
          <TextField
            select
            label="Plataforma de origem"
            size="small"
            value={row.plataforma_origem}
            onChange={(event) => onFieldChange(row.local_id, { plataforma_origem: event.target.value })}
            disabled={isReadonly}
            fullWidth
          >
            {LEADS_IMPORT_PLATFORMS.map((plataforma) => (
              <MenuItem key={plataforma} value={plataforma}>
                {plataforma}
              </MenuItem>
            ))}
          </TextField>
        </TableCell>

        <TableCell sx={{ minWidth: 150 }}>
          <TextField
            label="Data de envio"
            type="date"
            size="small"
            value={row.data_envio}
            onChange={(event) => onFieldChange(row.local_id, { data_envio: event.target.value })}
            InputLabelProps={{ shrink: true }}
            disabled={isReadonly}
            fullWidth
          />
        </TableCell>

        <TableCell sx={{ minWidth: 260 }}>
          {isEnrichmentOnly ? (
            <Stack spacing={0.5}>
              <Typography variant="body2" fontWeight={600}>
                Sem evento
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Este envio segue apenas para enriquecimento.
              </Typography>
            </Stack>
          ) : (
            <Autocomplete<ReferenciaEvento, false, false, false>
              options={eventos}
              value={selectedEvento}
              disabled={isReadonly}
              getOptionLabel={(evento) => formatReferenciaEventoOptionLabel(evento)}
              filterOptions={(options, state) => {
                const filtered = options.filter((evento) =>
                  formatReferenciaEventoOptionLabel(evento).toLowerCase().includes(state.inputValue.toLowerCase()),
                );
                if (!filtered.some((evento) => evento.id === QUICK_CREATE_EVENTO_ID)) {
                  filtered.push({
                    id: QUICK_CREATE_EVENTO_ID,
                    nome: "+ Criar evento rapidamente",
                    data_inicio_prevista: null,
                  });
                }
                return filtered;
              }}
              onChange={(_, nextValue) => {
                if (!nextValue) {
                  onFieldChange(row.local_id, { evento_id: "", ativacao_id: "" });
                  return;
                }
                if (nextValue.id === QUICK_CREATE_EVENTO_ID) {
                  onOpenQuickCreateEvento(row.local_id);
                  return;
                }
                onFieldChange(row.local_id, {
                  import_mode: "event_linked",
                  evento_id: String(nextValue.id),
                  ativacao_id: "",
                });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Evento de referencia"
                  size="small"
                  fullWidth
                />
              )}
              renderOption={(props, option) => (
                <Box
                  component="li"
                  {...props}
                  key={option.id}
                  sx={option.id === QUICK_CREATE_EVENTO_ID ? { color: "primary.main", fontStyle: "italic" } : undefined}
                >
                  {formatReferenciaEventoOptionLabel(option)}
                </Box>
              )}
            />
          )}
        </TableCell>

        <TableCell sx={{ minWidth: 220 }}>
          <Stack spacing={1}>
            <TextField
              select
              label="Modo do fluxo"
              size="small"
              value={row.import_mode}
              onChange={(event) =>
                onFieldChange(row.local_id, {
                  import_mode: event.target.value as BronzeImportMode,
                })
              }
              disabled={isReadonly}
              fullWidth
            >
              <MenuItem value="event_linked">{getBronzeImportModeLabel("event_linked")}</MenuItem>
              <MenuItem value="enrichment_only">{getBronzeImportModeLabel("enrichment_only")}</MenuItem>
            </TextField>
            {isEnrichmentOnly ? (
              <Typography variant="caption" color="text.secondary">
                Classificação opcional: escolha “Não informar” quando esse contexto não for relevante.
              </Typography>
            ) : (
              <TextField
                select
                label="Origem"
                size="small"
                value={row.origem_lote}
                onChange={(event) =>
                  onFieldChange(row.local_id, {
                    origem_lote: event.target.value as BatchUploadRowDraft["origem_lote"],
                    ativacao_id: event.target.value === "proponente" ? "" : row.ativacao_id,
                  })
                }
                disabled={isReadonly}
                fullWidth
              >
                <MenuItem value="proponente">Proponente</MenuItem>
                <MenuItem value="ativacao">Ativacao</MenuItem>
              </TextField>
            )}
          </Stack>
        </TableCell>

        <TableCell sx={{ minWidth: 240 }}>
          {(isEnrichmentOnly || row.origem_lote === "proponente") ? (
            <Stack spacing={1}>
              <TextField
                select
                label={isEnrichmentOnly ? "Classificação do lead (opcional)" : "Classificação do lead"}
                size="small"
                value={row.tipo_lead_proponente}
                onChange={(event) =>
                  onFieldChange(row.local_id, {
                    tipo_lead_proponente: event.target.value as BatchUploadRowDraft["tipo_lead_proponente"],
                  })
                }
                disabled={isReadonly}
                fullWidth
              >
                <MenuItem value="">
                  <em>Não informar</em>
                </MenuItem>
                <MenuItem value="entrada_evento">Entrada no evento</MenuItem>
                <MenuItem value="bilheteria">Bilheteria</MenuItem>
              </TextField>
              {isEnrichmentOnly ? (
                <Typography variant="caption" color="text.secondary">
                  {getBronzeImportModeHelpText("enrichment_only")}
                </Typography>
              ) : null}
            </Stack>
          ) : !row.evento_id ? (
            <Typography variant="caption" color="text.secondary">
              Selecione o evento para listar as ativacoes.
            </Typography>
          ) : activationImportBlocked ? (
            <Typography variant="caption" color="warning.main">
              {activationBlockReason}
            </Typography>
          ) : (
            <Stack spacing={1}>
              <TextField
                select
                label="Ativacao"
                size="small"
                value={row.ativacao_id}
                onChange={(event) => onFieldChange(row.local_id, { ativacao_id: event.target.value })}
                disabled={isReadonly || loadingAtivacoes || (Boolean(ativacoesLoadError) && ativacoes.length === 0)}
                error={Boolean(ativacoesLoadError)}
                helperText={ativacoesLoadError ?? undefined}
                fullWidth
              >
                <MenuItem value="">
                  <em>Selecione a ativacao</em>
                </MenuItem>
                {ativacoes.map((ativacao) => (
                  <MenuItem key={ativacao.id} value={String(ativacao.id)}>
                    {ativacao.nome}
                  </MenuItem>
                ))}
              </TextField>

              {!loadingAtivacoes && !ativacoesLoadError && ativacoes.length === 0 ? (
                <Button
                  size="small"
                  variant="outlined"
                  disabled={isReadonly}
                  onClick={() => {
                    setAtivacaoDialogError(null);
                    setAtivacaoDialogOpen(true);
                  }}
                >
                  Criar ativacao
                </Button>
              ) : null}
            </Stack>
          )}
        </TableCell>

        <TableCell sx={{ minWidth: 260 }}>
          <Stack spacing={1}>
            {showAgencyEditor ? (
              <InlineEventoAgencyEditor
                agencias={agencias}
                currentAgenciaId={selectedEvento?.agencia_id ?? null}
                loading={loadingAgencias}
                loadError={agenciasLoadError}
                onSave={(agenciaId) => onSaveAgency(row.local_id, agenciaId)}
              />
            ) : null}

            {visiblePendingMessages.length > 0 ? (
              <Stack spacing={0.5}>
                {visiblePendingMessages.map((message) => (
                  <Typography
                    key={message}
                    variant="caption"
                    color={pendingMessagesColor}
                  >
                    {message}
                  </Typography>
                ))}
              </Stack>
            ) : (
              <Stack spacing={0.5}>
                {row.metadata_hint_message ? (
                  <Typography variant="caption" color="info.main">
                    {row.metadata_hint_message}
                  </Typography>
                ) : null}
                <Typography variant="caption" color="success.main">
                  {isEnrichmentOnly
                    ? "Linha pronta para envio ao enriquecimento sem evento."
                    : "Linha pronta para envio."}
                </Typography>
              </Stack>
            )}

            {visiblePendingMessages.length > 0 && row.metadata_hint_message ? (
              <Typography variant="caption" color="info.main">
                {row.metadata_hint_message}
              </Typography>
            ) : null}
          </Stack>
        </TableCell>

        <TableCell sx={{ minWidth: 150 }}>
          <Stack spacing={1}>
            <Chip
              label={`Upload: ${rowStatusLabel(row.status_ui)}`}
              color={rowStatusColor(row.status_ui)}
              size="small"
              sx={{ width: "fit-content" }}
            />
            {flowStatusLabel ? (
              <Chip
                label={flowStatusLabel}
                color={downstreamStatusColor(row)}
                size="small"
                variant="outlined"
                sx={{ width: "fit-content" }}
              />
            ) : null}
            <Chip
              label={getBronzeImportModeSummary(row.import_mode)}
              size="small"
              variant="outlined"
              sx={{ width: "fit-content" }}
            />
            {row.created_batch_id != null ? (
              <Typography variant="caption" color="text.secondary">
                batch_id: {row.created_batch_id}
              </Typography>
            ) : null}
          </Stack>
        </TableCell>

        <TableCell sx={{ minWidth: 190 }}>
          <Stack spacing={1}>
            {row.created_batch_id != null && flowActionLabel ? (
              <Button size="small" variant="contained" onClick={() => onOpenRowFlow(row)}>
                {flowActionLabel}
              </Button>
            ) : null}
            {row.status_ui === "error" ? (
              <Button size="small" variant="outlined" onClick={() => void onRetry(row.local_id)}>
                Reenviar linha
              </Button>
            ) : null}
            <Button
              size="small"
              color="inherit"
              onClick={() => onRemove(row.local_id)}
              disabled={row.status_ui === "submitting"}
            >
              Remover
            </Button>
          </Stack>
        </TableCell>
      </TableRow>

      <Dialog
        open={ativacaoDialogOpen}
        onClose={() => {
          if (ativacaoSaving) return;
          setAtivacaoDialogOpen(false);
          setAtivacaoDialogError(null);
        }}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Nova ativacao</DialogTitle>
        <DialogContent>
          {ativacaoDialogError ? <Alert severity="error" sx={{ mt: 1 }}>{ativacaoDialogError}</Alert> : null}
          <TextField
            autoFocus
            margin="dense"
            label="Nome da ativacao"
            value={ativacaoNome}
            onChange={(event) => {
              setAtivacaoNome(event.target.value);
              if (ativacaoDialogError) {
                setAtivacaoDialogError(null);
              }
            }}
            fullWidth
            disabled={ativacaoSaving}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setAtivacaoDialogOpen(false);
              setAtivacaoDialogError(null);
            }}
            disabled={ativacaoSaving}
          >
            Cancelar
          </Button>
          <Button
            variant="contained"
            disabled={!ativacaoNome.trim() || ativacaoSaving}
            onClick={async () => {
              setAtivacaoSaving(true);
              setAtivacaoDialogError(null);
              try {
                await onCreateAtivacao(row.local_id, ativacaoNome.trim());
                setAtivacaoDialogOpen(false);
                setAtivacaoNome("");
              } catch (error) {
                setAtivacaoDialogError(
                  error instanceof Error && error.message.trim()
                    ? error.message
                    : "Falha ao criar ativacao.",
                );
              } finally {
                setAtivacaoSaving(false);
              }
            }}
          >
            {ativacaoSaving ? <CircularProgress size={16} color="inherit" /> : "Criar"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
