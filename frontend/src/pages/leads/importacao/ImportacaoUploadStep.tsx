import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormLabel,
  MenuItem,
  Paper,
  Radio,
  RadioGroup,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { ChangeEvent, FormEvent, useState } from "react";

import { Agencia } from "../../../services/agencias";
import {
  LeadBatch,
  LeadBatchPreview,
  LeadImportEtlPreview,
  LeadImportEtlResult,
  LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP,
  ReferenciaEvento,
} from "../../../services/leads_import";
import { formatReferenciaEventoOptionLabel } from "../../../utils/formatters";
import BatchSummaryCard from "./BatchSummaryCard";
import BatchUploadTable from "./batch/BatchUploadTable";
import {
  BatchUploadAtivacaoOption,
  BatchUploadRowDraft,
  BronzeMode,
} from "./batch/useBatchUploadDraft";
import { LEADS_IMPORT_PLATFORMS, QUICK_CREATE_EVENTO_ID } from "./constants";

type ImportFlow = "bronze" | "etl";

type AtivacaoOption = { id: number; nome: string };

type Props = {
  activeStep: number;
  ativacoes: AtivacaoOption[];
  ativacoesLoadError: string | null;
  batch: LeadBatch | null;
  batchAgencias: Agencia[];
  batchAgenciasLoadError: string | null;
  batchAtivacoesByEventoId: Record<number, BatchUploadAtivacaoOption[]>;
  batchAtivacoesLoadErrorByEventoId: Record<number, string | null>;
  batchLoadingAgencias: boolean;
  batchLoadingAtivacoesByEventoId: Record<number, boolean>;
  batchRows: BatchUploadRowDraft[];
  bronzeAtivacaoId: string;
  bronzeActivationImportBlockReason: string | null;
  bronzeEventoId: string;
  bronzeEventoSupportsActivationImport: boolean;
  bronzeMode: BronzeMode;
  bronzeOrigemLote: "proponente" | "ativacao";
  bronzeTipoLeadProponente: "bilheteria" | "entrada_evento";
  canSubmit: boolean;
  committingEtl: boolean;
  dataEnvio: string;
  etlCommitResult: LeadImportEtlResult | null;
  etlCpfColumnIndex: string;
  etlHeaderRow: string;
  etlMaxScanRows: string;
  etlPreview: LeadImportEtlPreview | null;
  etlSheetName: string;
  etlWarningsPending: boolean;
  eventoId: string;
  eventos: ReferenciaEvento[];
  file: File | null;
  importFlow: ImportFlow;
  isEtlFile: boolean;
  loadingAtivacoes: boolean;
  loadingEtlPreview: boolean;
  loadingEventos: boolean;
  loadingPreview: boolean;
  loadingSubmit: boolean;
  plataformaOrigem: string;
  preview: LeadBatchPreview | null;
  quemEnviou: string;
  onBack: () => void;
  onBatchAddFiles: (files: FileList | File[]) => void;
  onBatchCreateAtivacao: (localId: string, nome: string) => Promise<unknown>;
  onBatchFieldChange: (localId: string, patch: Partial<BatchUploadRowDraft>) => void;
  onBatchOpenRowFlow: (row: BatchUploadRowDraft) => void;
  onBatchOpenQuickCreateEvento: (localId: string) => void;
  onBatchRemoveRow: (localId: string) => void;
  onBatchRetryRow: (localId: string) => Promise<void>;
  onBatchSaveAgency: (localId: string, agenciaId: number) => Promise<void>;
  onBatchSubmit: () => Promise<void>;
  onBronzeAtivacaoIdChange: (value: string) => void;
  onBronzeEventoIdChange: (value: string) => void;
  onBronzeModeChange: (value: BronzeMode) => void;
  onBronzeOrigemLoteChange: (value: "proponente" | "ativacao") => void;
  onBronzeTipoLeadProponenteChange: (value: "bilheteria" | "entrada_evento") => void;
  onCommitEtl: (forceWarnings: boolean) => void;
  onCpfColumnChange: (value: string) => void;
  onCpfColumnSubmit: () => void;
  onCreateAtivacaoAdHoc: (nome: string) => Promise<void>;
  onDataEnvioChange: (value: string) => void;
  onEventoIdChange: (value: string) => void;
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onGoToMapping: () => void;
  onEtlMaxScanRowsChange: (value: string) => void;
  onEtlSheetNameChange: (value: string) => void;
  onHeaderRowChange: (value: string) => void;
  onHeaderRowSubmit: () => void;
  onImportFlowChange: (nextFlow: ImportFlow) => void;
  onOpenQuickCreateEvento: () => void;
  onPlataformaOrigemChange: (value: string) => void;
  onQuemEnviouChange: (value: string) => void;
  onResetEtl: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function UploadStep({
  ativacoes,
  ativacoesLoadError,
  batchAgencias,
  batchAgenciasLoadError,
  batchAtivacoesByEventoId,
  batchAtivacoesLoadErrorByEventoId,
  batchLoadingAgencias,
  batchLoadingAtivacoesByEventoId,
  batchRows,
  bronzeAtivacaoId,
  bronzeActivationImportBlockReason,
  bronzeEventoId,
  bronzeEventoSupportsActivationImport,
  bronzeMode,
  bronzeOrigemLote,
  bronzeTipoLeadProponente,
  canSubmit,
  dataEnvio,
  etlMaxScanRows,
  etlSheetName,
  eventoId,
  eventos,
  file,
  importFlow,
  loadingAtivacoes,
  loadingEtlPreview,
  loadingEventos,
  loadingSubmit,
  plataformaOrigem,
  quemEnviou,
  onBatchAddFiles,
  onBatchCreateAtivacao,
  onBatchFieldChange,
  onBatchOpenRowFlow,
  onBatchOpenQuickCreateEvento,
  onBatchRemoveRow,
  onBatchRetryRow,
  onBatchSaveAgency,
  onBatchSubmit,
  onBronzeAtivacaoIdChange,
  onBronzeEventoIdChange,
  onBronzeModeChange,
  onBronzeOrigemLoteChange,
  onBronzeTipoLeadProponenteChange,
  onCreateAtivacaoAdHoc,
  onDataEnvioChange,
  onEtlMaxScanRowsChange,
  onEtlSheetNameChange,
  onEventoIdChange,
  onFileChange,
  onImportFlowChange,
  onOpenQuickCreateEvento,
  onPlataformaOrigemChange,
  onQuemEnviouChange,
  onSubmit,
}: Pick<
  Props,
  | "ativacoes"
  | "ativacoesLoadError"
  | "batchAgencias"
  | "batchAgenciasLoadError"
  | "batchAtivacoesByEventoId"
  | "batchAtivacoesLoadErrorByEventoId"
  | "batchLoadingAgencias"
  | "batchLoadingAtivacoesByEventoId"
  | "batchRows"
  | "bronzeAtivacaoId"
  | "bronzeActivationImportBlockReason"
  | "bronzeEventoId"
  | "bronzeEventoSupportsActivationImport"
  | "bronzeMode"
  | "bronzeOrigemLote"
  | "bronzeTipoLeadProponente"
  | "canSubmit"
  | "dataEnvio"
  | "etlMaxScanRows"
  | "etlSheetName"
  | "eventoId"
  | "eventos"
  | "file"
  | "importFlow"
  | "loadingAtivacoes"
  | "loadingEtlPreview"
  | "loadingEventos"
  | "loadingSubmit"
  | "plataformaOrigem"
  | "quemEnviou"
  | "onBatchAddFiles"
  | "onBatchCreateAtivacao"
  | "onBatchFieldChange"
  | "onBatchOpenRowFlow"
  | "onBatchOpenQuickCreateEvento"
  | "onBatchRemoveRow"
  | "onBatchRetryRow"
  | "onBatchSaveAgency"
  | "onBatchSubmit"
  | "onBronzeAtivacaoIdChange"
  | "onBronzeEventoIdChange"
  | "onBronzeModeChange"
  | "onBronzeOrigemLoteChange"
  | "onBronzeTipoLeadProponenteChange"
  | "onCreateAtivacaoAdHoc"
  | "onDataEnvioChange"
  | "onEtlMaxScanRowsChange"
  | "onEtlSheetNameChange"
  | "onEventoIdChange"
  | "onFileChange"
  | "onImportFlowChange"
  | "onOpenQuickCreateEvento"
  | "onPlataformaOrigemChange"
  | "onQuemEnviouChange"
  | "onSubmit"
>) {
  const [ativDialogOpen, setAtivDialogOpen] = useState(false);
  const [ativDialogNome, setAtivDialogNome] = useState("");
  const [ativSaving, setAtivSaving] = useState(false);

  const activationImportBlocked = Boolean(bronzeEventoId) && !bronzeEventoSupportsActivationImport;
  const activationSelectionMissing =
    bronzeOrigemLote === "ativacao" &&
    Boolean(bronzeEventoId) &&
    bronzeEventoSupportsActivationImport &&
    !loadingAtivacoes &&
    !bronzeAtivacaoId;
  const selectedEtlEvento =
    eventoId && Number.isFinite(Number(eventoId))
      ? eventos.find((evento) => evento.id === Number(eventoId)) ?? null
      : null;
  const selectedBronzeEvento =
    bronzeEventoId && Number.isFinite(Number(bronzeEventoId))
      ? eventos.find((evento) => evento.id === Number(bronzeEventoId)) ?? null
      : null;

  const filterEventoOptions = (options: ReferenciaEvento[], inputValue: string) => {
    const filtered = options.filter((evento) =>
      formatReferenciaEventoOptionLabel(evento).toLowerCase().includes(inputValue.toLowerCase()),
    );
    if (!filtered.some((evento) => evento.id === QUICK_CREATE_EVENTO_ID)) {
      filtered.push({
        id: QUICK_CREATE_EVENTO_ID,
        nome: "+ Criar evento rapidamente",
        data_inicio_prevista: null,
      });
    }
    return filtered;
  };

  const handleConfirmNovaAtivacao = async () => {
    const nome = ativDialogNome.trim();
    if (!nome) return;
    setAtivSaving(true);
    try {
      await onCreateAtivacaoAdHoc(nome);
      setAtivDialogOpen(false);
      setAtivDialogNome("");
    } catch {
      /* erro exibido no ImportacaoPage */
    } finally {
      setAtivSaving(false);
    }
  };

  return (
    <Stack spacing={2}>
      <TextField
        select
        label="Fluxo de processamento"
        value={importFlow}
        onChange={(event) => onImportFlowChange(event.target.value as ImportFlow)}
        fullWidth
      >
        <MenuItem value="bronze">Bronze + mapeamento</MenuItem>
        <MenuItem value="etl">ETL CSV/XLSX</MenuItem>
      </TextField>

      {importFlow === "bronze" ? (
        <TextField
          select
          label="Modo de upload Bronze"
          value={bronzeMode}
          onChange={(event) => onBronzeModeChange(event.target.value as BronzeMode)}
          fullWidth
        >
          <MenuItem value="single">Upload simples</MenuItem>
          <MenuItem value="batch">Upload batch</MenuItem>
        </TextField>
      ) : null}

      {importFlow === "bronze" && bronzeMode === "batch" ? (
        <BatchUploadTable
          rows={batchRows}
          eventos={eventos}
          ativacoesByEventoId={batchAtivacoesByEventoId}
          ativacoesLoadErrorByEventoId={batchAtivacoesLoadErrorByEventoId}
          loadingAtivacoesByEventoId={batchLoadingAtivacoesByEventoId}
          agencias={batchAgencias}
          loadingAgencias={batchLoadingAgencias}
          agenciasLoadError={batchAgenciasLoadError}
          onAddFiles={onBatchAddFiles}
          onFieldChange={onBatchFieldChange}
          onOpenQuickCreateEvento={onBatchOpenQuickCreateEvento}
            onCreateAtivacao={onBatchCreateAtivacao}
            onSaveAgency={onBatchSaveAgency}
            onRemoveRow={onBatchRemoveRow}
            onRetryRow={onBatchRetryRow}
            onSubmitRows={onBatchSubmit}
            onOpenRowFlow={onBatchOpenRowFlow}
          />
      ) : (
        <>
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              {importFlow === "etl" ? (
                <Autocomplete<ReferenciaEvento, false, false, false>
                  options={eventos}
                  value={selectedEtlEvento}
                  disabled={loadingEventos}
                  getOptionLabel={(evento) => formatReferenciaEventoOptionLabel(evento)}
                  filterOptions={(options, state) => filterEventoOptions(options, state.inputValue)}
                  onChange={(_, selected) => {
                    if (!selected) {
                      onEventoIdChange("");
                      return;
                    }
                    if (selected.id === QUICK_CREATE_EVENTO_ID) {
                      onOpenQuickCreateEvento();
                      return;
                    }
                    onEventoIdChange(String(selected.id));
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Evento de referencia"
                      required
                      fullWidth
                      helperText="Obrigatorio para o preview ETL. Pode ser escolhido antes ou depois de selecionar o arquivo."
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
              ) : null}

              <TextField
                label="Quem enviou"
                value={quemEnviou}
                onChange={(event) => onQuemEnviouChange(event.target.value)}
                required
                fullWidth
              />

              {importFlow === "bronze" ? (
                <>
                  <TextField
                    select
                    label="Plataforma de origem"
                    value={plataformaOrigem}
                    onChange={(event) => onPlataformaOrigemChange(event.target.value)}
                    required
                    fullWidth
                  >
                    {LEADS_IMPORT_PLATFORMS.map((plataforma) => (
                      <MenuItem key={plataforma} value={plataforma}>
                        {plataforma}
                      </MenuItem>
                    ))}
                  </TextField>

                  <TextField
                    label="Data de envio"
                    type="date"
                    value={dataEnvio}
                    onChange={(event) => onDataEnvioChange(event.target.value)}
                    InputLabelProps={{ shrink: true }}
                    required
                    fullWidth
                  />

                  <Autocomplete<ReferenciaEvento, false, false, false>
                    options={eventos}
                    value={selectedBronzeEvento}
                    disabled={loadingEventos}
                    getOptionLabel={(evento) => formatReferenciaEventoOptionLabel(evento)}
                    filterOptions={(options, state) => filterEventoOptions(options, state.inputValue)}
                    onChange={(_, selected) => {
                      if (!selected) {
                        onBronzeEventoIdChange("");
                        return;
                      }
                      if (selected.id === QUICK_CREATE_EVENTO_ID) {
                        onOpenQuickCreateEvento();
                        return;
                      }
                      onBronzeEventoIdChange(String(selected.id));
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Evento de referencia"
                        required
                        fullWidth
                        helperText="Evento associado a esta importacao Bronze."
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

                  <FormControl component="fieldset" variant="standard" sx={{ width: "100%" }}>
                    <FormLabel component="legend">Origem dos leads</FormLabel>
                    <RadioGroup
                      row
                      value={bronzeOrigemLote}
                      onChange={(event) =>
                        onBronzeOrigemLoteChange(event.target.value as "proponente" | "ativacao")
                      }
                    >
                      <FormControlLabel value="proponente" control={<Radio />} label="Proponente" />
                      <FormControlLabel
                        value="ativacao"
                        control={<Radio />}
                        label="Ativacao (importacao)"
                        disabled={activationImportBlocked}
                      />
                    </RadioGroup>
                  </FormControl>

                  {activationImportBlocked && bronzeOrigemLote !== "ativacao" ? (
                    <Alert severity="warning">
                      {bronzeActivationImportBlockReason ??
                        "Vincule uma agencia ao evento antes de importar leads de ativacao."}
                    </Alert>
                  ) : null}

                  {bronzeOrigemLote === "proponente" ? (
                    <TextField
                      select
                      label="Tipo (proponente)"
                      value={bronzeTipoLeadProponente}
                      onChange={(event) =>
                        onBronzeTipoLeadProponenteChange(
                          event.target.value as "bilheteria" | "entrada_evento",
                        )
                      }
                      fullWidth
                    >
                      <MenuItem value="entrada_evento">Entrada no evento</MenuItem>
                      <MenuItem value="bilheteria">Bilheteria</MenuItem>
                    </TextField>
                  ) : null}

                  {bronzeOrigemLote === "ativacao" ? (
                    <Stack spacing={1}>
                      {activationImportBlocked ? (
                        <Alert severity="warning">
                          {bronzeActivationImportBlockReason ??
                            "Vincule uma agencia ao evento antes de importar leads de ativacao."}
                        </Alert>
                      ) : !bronzeEventoId ? (
                        <Alert severity="info">Selecione o evento acima para listar as ativacoes.</Alert>
                      ) : (
                        <>
                          <TextField
                            select
                            label="Ativacao vinculada"
                            value={bronzeAtivacaoId}
                            onChange={(event) => onBronzeAtivacaoIdChange(event.target.value)}
                            required
                            fullWidth
                            error={Boolean(ativacoesLoadError) || activationSelectionMissing}
                            disabled={loadingAtivacoes || (Boolean(ativacoesLoadError) && ativacoes.length === 0)}
                            helperText={
                              activationSelectionMissing
                                ? "Selecione a ativacao desta importacao para continuar."
                                : "Obrigatorio: selecione a ativacao vinculada a estes leads."
                            }
                          >
                            <MenuItem value="">
                              <em>Selecione a ativacao</em>
                            </MenuItem>
                            {ativacoes.map((ativacao) => (
                              <MenuItem key={ativacao.id} value={String(ativacao.id)}>
                                {ativacao.nome}
                              </MenuItem>
                            ))}
                            {ativacoes.length === 0 && !loadingAtivacoes ? (
                              <MenuItem value="" disabled>
                                Nenhuma ativacao cadastrada
                              </MenuItem>
                            ) : null}
                          </TextField>
                          {!loadingAtivacoes && ativacoesLoadError ? (
                            <Alert severity="error">{ativacoesLoadError}</Alert>
                          ) : null}
                          {!loadingAtivacoes && !ativacoesLoadError && ativacoes.length === 0 ? (
                            <Alert
                              severity="warning"
                              action={
                                <Button color="inherit" size="small" onClick={() => setAtivDialogOpen(true)}>
                                  Criar ativacao
                                </Button>
                              }
                            >
                              Este evento ainda nao possui ativacoes. Crie uma para importar como ativacao.
                            </Alert>
                          ) : null}
                        </>
                      )}
                    </Stack>
                  ) : null}
                </>
              ) : null}

              <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ xs: "stretch", md: "center" }}>
                <Button variant="outlined" component="label" startIcon={<CloudUploadRoundedIcon />} sx={{ textTransform: "none" }}>
                  Selecionar CSV/XLSX
                  <input hidden type="file" accept=".csv,.xlsx" onChange={onFileChange} />
                </Button>
                <Typography variant="body2" color={file ? "text.primary" : "text.secondary"}>
                  {file ? file.name : "Nenhum arquivo selecionado"}
                </Typography>
              </Stack>

              {importFlow === "etl" ? (
                <Stack spacing={1.5}>
                  <Alert severity="info">
                    O fluxo ETL fecha preview e commit no mesmo shell. O contrato atual nao expoe batch_id para consulta de lote.
                  </Alert>
                  {file?.name.toLowerCase().endsWith(".xlsx") ? (
                    <TextField
                      label="Aba (XLSX)"
                      value={etlSheetName}
                      onChange={(event) => onEtlSheetNameChange(event.target.value)}
                      fullWidth
                      helperText="Opcional: titulo exato da folha. Se vazio, usa a primeira aba."
                    />
                  ) : null}
                  <TextField
                    label="Linhas para buscar cabecalho"
                    type="number"
                    value={etlMaxScanRows}
                    onChange={(event) => onEtlMaxScanRowsChange(event.target.value)}
                    fullWidth
                    inputProps={{ min: 1, max: LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP }}
                    helperText={`Opcional. Padrao 40, maximo ${LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP} (planilhas com cabecalho tardio).`}
                  />
                </Stack>
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

          <Dialog open={ativDialogOpen} onClose={() => !ativSaving && setAtivDialogOpen(false)} fullWidth maxWidth="xs">
            <DialogTitle>Nova ativacao no evento</DialogTitle>
            <DialogContent>
              <TextField
                autoFocus
                margin="dense"
                label="Nome da ativacao"
                fullWidth
                value={ativDialogNome}
                onChange={(event) => setAtivDialogNome(event.target.value)}
                disabled={ativSaving}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setAtivDialogOpen(false)} disabled={ativSaving}>
                Cancelar
              </Button>
              <Button
                onClick={() => void handleConfirmNovaAtivacao()}
                disabled={!ativDialogNome.trim() || ativSaving}
                variant="contained"
              >
                {ativSaving ? <CircularProgress size={18} color="inherit" /> : "Criar"}
              </Button>
            </DialogActions>
          </Dialog>
        </>
      )}
    </Stack>
  );
}

function EtlPreviewStep({
  committingEtl,
  etlCommitResult,
  etlCpfColumnIndex,
  etlHeaderRow,
  etlMaxScanRows,
  etlPreview,
  etlSheetName,
  etlWarningsPending,
  loadingEtlPreview,
  file,
  onBack,
  onCommitEtl,
  onCpfColumnChange,
  onCpfColumnSubmit,
  onEtlMaxScanRowsChange,
  onEtlSheetNameChange,
  onHeaderRowChange,
  onHeaderRowSubmit,
  onResetEtl,
}: Pick<
  Props,
  | "committingEtl"
  | "etlCommitResult"
  | "etlCpfColumnIndex"
  | "etlHeaderRow"
  | "etlMaxScanRows"
  | "etlPreview"
  | "etlSheetName"
  | "etlWarningsPending"
  | "file"
  | "loadingEtlPreview"
  | "onBack"
  | "onCommitEtl"
  | "onCpfColumnChange"
  | "onCpfColumnSubmit"
  | "onEtlMaxScanRowsChange"
  | "onEtlSheetNameChange"
  | "onHeaderRowChange"
  | "onHeaderRowSubmit"
  | "onResetEtl"
>) {
  const isPartialFailure = etlCommitResult?.status === "partial_failure";
  const isCommitted = etlCommitResult?.status === "committed";
  const isCommitClosed = isCommitted;
  const commitActionLabel = etlWarningsPending
    ? isPartialFailure
      ? "Retentar mesmo com avisos"
      : "Confirmar mesmo com avisos"
    : isPartialFailure
      ? "Retentar importacao ETL"
      : "Confirmar importacao ETL";

  return (
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
          {etlPreview.active_sheet ? (
            <Typography variant="body2" color="text.secondary">
              Folha ativa na ultima tentativa: {etlPreview.active_sheet}
            </Typography>
          ) : null}
          {etlPreview.available_sheets && etlPreview.available_sheets.length > 1 ? (
            <TextField
              select
              label="Aba do ficheiro"
              value={etlSheetName}
              onChange={(event) => onEtlSheetNameChange(event.target.value)}
              fullWidth
              helperText="Escolha a folha com os dados (titulo exato)."
            >
              <MenuItem value="">
                <em>Primeira aba (padrao)</em>
              </MenuItem>
              {etlPreview.available_sheets.map((name) => (
                <MenuItem key={name} value={name}>
                  {name}
                </MenuItem>
              ))}
            </TextField>
          ) : file?.name.toLowerCase().endsWith(".xlsx") ? (
            <TextField
              label="Aba (titulo exato)"
              value={etlSheetName}
              onChange={(event) => onEtlSheetNameChange(event.target.value)}
              fullWidth
              helperText="Opcional se a folha correta ja for a primeira."
            />
          ) : null}
          <TextField
            label="Linhas para buscar cabecalho"
            type="number"
            value={etlMaxScanRows}
            onChange={(event) => onEtlMaxScanRowsChange(event.target.value)}
            fullWidth
            inputProps={{ min: 1, max: LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP }}
            helperText={`Opcional. Padrao 40, maximo ${LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP}.`}
          />
          <TextField
            label="Linha do cabecalho"
            type="number"
            value={etlHeaderRow}
            onChange={(event) => onHeaderRowChange(event.target.value)}
            inputProps={{ min: 1, max: etlPreview.max_row }}
            helperText={`Informe uma linha entre 1 e ${etlPreview.max_row}.`}
            fullWidth
          />
          <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
            <Button variant="outlined" onClick={onBack}>
              Cancelar
            </Button>
            <Button variant="contained" onClick={onHeaderRowSubmit} disabled={loadingEtlPreview}>
              {loadingEtlPreview ? <CircularProgress size={18} color="inherit" /> : "Reprocessar cabecalho"}
            </Button>
          </Stack>
        </Stack>
      ) : null}

      {etlPreview?.status === "cpf_column_required" ? (
        <Stack spacing={2}>
          <Alert severity="warning">{etlPreview.message}</Alert>
          {etlPreview.active_sheet ? (
            <Typography variant="body2" color="text.secondary">
              Folha ativa na ultima tentativa: {etlPreview.active_sheet}
            </Typography>
          ) : null}
          {etlPreview.available_sheets && etlPreview.available_sheets.length > 1 ? (
            <TextField
              select
              label="Aba do ficheiro"
              value={etlSheetName}
              onChange={(event) => onEtlSheetNameChange(event.target.value)}
              fullWidth
            >
              <MenuItem value="">
                <em>Primeira aba (padrao)</em>
              </MenuItem>
              {etlPreview.available_sheets.map((name) => (
                <MenuItem key={name} value={name}>
                  {name}
                </MenuItem>
              ))}
            </TextField>
          ) : null}
          <TextField
            select
            label="Coluna de CPF"
            value={etlCpfColumnIndex}
            onChange={(event) => onCpfColumnChange(event.target.value)}
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
            <Button variant="outlined" onClick={onBack}>
              Cancelar
            </Button>
            <Button variant="contained" onClick={onCpfColumnSubmit} disabled={!etlCpfColumnIndex || loadingEtlPreview}>
              {loadingEtlPreview ? <CircularProgress size={18} color="inherit" /> : "Salvar alias CPF"}
            </Button>
          </Stack>
        </Stack>
      ) : null}

      {etlPreview?.status === "previewed" ? (
        <Stack spacing={2}>
          {etlPreview.sheet_name ? (
            <Typography variant="body2" color="text.secondary">
              Folha usada: {etlPreview.sheet_name}
              {etlPreview.available_sheets?.length ? ` (${etlPreview.available_sheets.length} abas no ficheiro)` : null}
            </Typography>
          ) : null}
          {isCommitted ? (
            <Alert severity="success">
              Importacao concluida: {etlCommitResult.created} criado(s), {etlCommitResult.updated} atualizado(s), {etlCommitResult.skipped} ignorado(s), {etlCommitResult.errors} erro(s).
            </Alert>
          ) : null}
          {isPartialFailure ? (
            <Alert severity="warning">
              <Stack spacing={1}>
                <Typography variant="body2">
                  Importacao parcialmente concluida: {etlCommitResult.created} criado(s), {etlCommitResult.updated} atualizado(s), {etlCommitResult.skipped} ignorado(s), {etlCommitResult.errors} erro(s). Corrija o problema e repita o commit com o mesmo preview.
                </Typography>
                {etlCommitResult.persistence_failures.length ? (
                  <Box component="ul" sx={{ mb: 0, mt: 0, pl: 3 }}>
                    {etlCommitResult.persistence_failures.map((failure) => (
                      <Box component="li" key={`${failure.row_number}-${failure.reason}`}>
                        <Typography variant="body2">
                          Linha {failure.row_number}: {failure.reason}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                ) : null}
              </Stack>
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
            <Button variant="outlined" onClick={onResetEtl} disabled={committingEtl}>
              Nova importacao
            </Button>
            {etlWarningsPending ? (
              <Button
                variant="contained"
                color="warning"
                onClick={() => onCommitEtl(true)}
                disabled={committingEtl || isCommitClosed}
              >
                {committingEtl ? <CircularProgress size={18} color="inherit" /> : commitActionLabel}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={() => onCommitEtl(false)}
                disabled={committingEtl || isCommitClosed}
              >
                {committingEtl ? <CircularProgress size={18} color="inherit" /> : commitActionLabel}
              </Button>
            )}
          </Stack>
        </Stack>
      ) : null}
    </Stack>
  );
}

function BronzePreviewStep({
  batch,
  loadingPreview,
  onBack,
  onGoToMapping,
  preview,
}: Pick<Props, "batch" | "loadingPreview" | "onBack" | "onGoToMapping" | "preview">) {
  return (
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
                      <TableCell key={`cell-${rowIndex}-${columnIndex}`}>{row[columnIndex] ?? ""}</TableCell>
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
        <Button variant="outlined" onClick={onBack}>
          Cancelar
        </Button>
        <Button variant="contained" disabled={!batch} onClick={onGoToMapping}>
          Ir para Mapeamento
        </Button>
      </Stack>
    </Stack>
  );
}

export default function ImportacaoUploadStep(props: Props) {
  if (props.activeStep === 0) {
    return <UploadStep {...props} />;
  }

  if (props.importFlow === "etl") {
    return <EtlPreviewStep {...props} />;
  }

  return <BronzePreviewStep {...props} />;
}
