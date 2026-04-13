import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  MenuItem,
  Paper,
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
import { ChangeEvent, FormEvent } from "react";

import {
  LeadBatch,
  LeadBatchPreview,
  LeadImportEtlPreview,
  LeadImportEtlResult,
  ReferenciaEvento,
} from "../../../services/leads_import";
import { formatEventoLabel } from "../../../utils/formatters";
import BatchSummaryCard from "./BatchSummaryCard";

const PLATAFORMAS = ["email", "whatsapp", "drive", "manual", "outro"];

type ImportFlow = "bronze" | "etl";

type Props = {
  activeStep: number;
  batch: LeadBatch | null;
  canSubmit: boolean;
  committingEtl: boolean;
  dataEnvio: string;
  etlCommitResult: LeadImportEtlResult | null;
  etlCpfColumnIndex: string;
  etlHeaderRow: string;
  etlPreview: LeadImportEtlPreview | null;
  etlWarningsPending: boolean;
  eventoId: string;
  eventos: ReferenciaEvento[];
  file: File | null;
  importFlow: ImportFlow;
  isEtlFile: boolean;
  loadingEtlPreview: boolean;
  loadingEventos: boolean;
  loadingPreview: boolean;
  loadingSubmit: boolean;
  plataformaOrigem: string;
  preview: LeadBatchPreview | null;
  quemEnviou: string;
  onBack: () => void;
  onCommitEtl: (forceWarnings: boolean) => void;
  onCpfColumnChange: (value: string) => void;
  onCpfColumnSubmit: () => void;
  onDataEnvioChange: (value: string) => void;
  onEventoIdChange: (value: string) => void;
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onGoToMapping: () => void;
  onHeaderRowChange: (value: string) => void;
  onHeaderRowSubmit: () => void;
  onImportFlowChange: (nextFlow: ImportFlow) => void;
  onPlataformaOrigemChange: (value: string) => void;
  onQuemEnviouChange: (value: string) => void;
  onResetEtl: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function BronzeUploadForm({
  canSubmit,
  dataEnvio,
  eventoId,
  eventos,
  file,
  importFlow,
  isEtlFile,
  loadingEtlPreview,
  loadingEventos,
  loadingSubmit,
  plataformaOrigem,
  quemEnviou,
  onDataEnvioChange,
  onEventoIdChange,
  onFileChange,
  onImportFlowChange,
  onPlataformaOrigemChange,
  onQuemEnviouChange,
  onSubmit,
}: Omit<
  Props,
  | "activeStep"
  | "batch"
  | "committingEtl"
  | "etlCommitResult"
  | "etlCpfColumnIndex"
  | "etlHeaderRow"
  | "etlPreview"
  | "etlWarningsPending"
  | "loadingPreview"
  | "preview"
  | "onBack"
  | "onCommitEtl"
  | "onCpfColumnChange"
  | "onCpfColumnSubmit"
  | "onGoToMapping"
  | "onHeaderRowChange"
  | "onHeaderRowSubmit"
  | "onResetEtl"
>) {
  return (
    <Box component="form" onSubmit={onSubmit}>
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
              onChange={(event) => onDataEnvioChange(event.target.value)}
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
            onChange={(event) => onEventoIdChange(event.target.value)}
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
            <input hidden type="file" accept=".csv,.xlsx" onChange={onFileChange} />
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
  );
}

function EtlPreviewStep({
  committingEtl,
  etlCommitResult,
  etlCpfColumnIndex,
  etlHeaderRow,
  etlPreview,
  etlWarningsPending,
  loadingEtlPreview,
  onBack,
  onCommitEtl,
  onCpfColumnChange,
  onCpfColumnSubmit,
  onHeaderRowChange,
  onHeaderRowSubmit,
  onResetEtl,
}: Pick<
  Props,
  | "committingEtl"
  | "etlCommitResult"
  | "etlCpfColumnIndex"
  | "etlHeaderRow"
  | "etlPreview"
  | "etlWarningsPending"
  | "loadingEtlPreview"
  | "onBack"
  | "onCommitEtl"
  | "onCpfColumnChange"
  | "onCpfColumnSubmit"
  | "onHeaderRowChange"
  | "onHeaderRowSubmit"
  | "onResetEtl"
>) {
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
            <Button variant="outlined" onClick={onResetEtl} disabled={committingEtl}>
              Nova importacao
            </Button>
            {etlWarningsPending ? (
              <Button
                variant="contained"
                color="warning"
                onClick={() => onCommitEtl(true)}
                disabled={committingEtl || Boolean(etlCommitResult)}
              >
                {committingEtl ? <CircularProgress size={18} color="inherit" /> : "Confirmar mesmo com avisos"}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={() => onCommitEtl(false)}
                disabled={committingEtl || Boolean(etlCommitResult)}
              >
                {committingEtl ? <CircularProgress size={18} color="inherit" /> : "Confirmar importacao ETL"}
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
    return <BronzeUploadForm {...props} />;
  }

  if (props.importFlow === "etl") {
    return <EtlPreviewStep {...props} />;
  }

  return <BronzePreviewStep {...props} />;
}
