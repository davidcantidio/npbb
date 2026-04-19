import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import {
  Alert,
  Button,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { ChangeEvent } from "react";

import { Agencia } from "../../../../services/agencias";
import { ReferenciaEvento } from "../../../../services/leads_import";
import BatchUploadRow from "./BatchUploadRow";
import BatchWorkspaceSummaryCard from "./BatchWorkspaceSummaryCard";
import {
  BatchUploadAtivacaoOption,
  BatchUploadRowDraft,
  getBatchRowSelectedEvento,
  getBatchRowValidationErrors,
} from "./useBatchUploadDraft";

type Props = {
  rows: BatchUploadRowDraft[];
  eventos: ReferenciaEvento[];
  ativacoesByEventoId: Record<number, BatchUploadAtivacaoOption[]>;
  ativacoesLoadErrorByEventoId: Record<number, string | null>;
  loadingAtivacoesByEventoId: Record<number, boolean>;
  agencias: Agencia[];
  loadingAgencias: boolean;
  agenciasLoadError: string | null;
  onAddFiles: (files: FileList | File[]) => void;
  onFieldChange: (localId: string, patch: Partial<BatchUploadRowDraft>) => void;
  onOpenQuickCreateEvento: (localId: string) => void;
  onCreateAtivacao: (localId: string, nome: string) => Promise<unknown>;
  onSaveAgency: (localId: string, agenciaId: number) => Promise<void>;
  onRemoveRow: (localId: string) => void;
  onRetryRow: (localId: string) => Promise<void>;
  onSubmitRows: () => Promise<void>;
  onOpenRowFlow: (row: BatchUploadRowDraft) => void;
};

export default function BatchUploadTable({
  rows,
  eventos,
  ativacoesByEventoId,
  ativacoesLoadErrorByEventoId,
  loadingAtivacoesByEventoId,
  agencias,
  loadingAgencias,
  agenciasLoadError,
  onAddFiles,
  onFieldChange,
  onOpenQuickCreateEvento,
  onCreateAtivacao,
  onSaveAgency,
  onRemoveRow,
  onRetryRow,
  onSubmitRows,
  onOpenRowFlow,
}: Props) {
  const draftCount = rows.filter((row) => row.status_ui === "draft").length;
  const errorCount = rows.filter((row) => row.status_ui === "error").length;
  const createdCount = rows.filter((row) => row.status_ui === "created").length;
  const submittingCount = rows.filter((row) => row.status_ui === "submitting").length;
  const canSubmit = rows.some((row) => row.status_ui !== "created" && row.status_ui !== "submitting");

  return (
    <Stack spacing={2}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1.5}
        justifyContent="space-between"
        alignItems={{ xs: "stretch", md: "center" }}
      >
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Chip label={`${rows.length} arquivo(s)`} size="small" />
          <Chip label={`${draftCount} rascunho`} size="small" color="default" />
          <Chip label={`${createdCount} criado(s)`} size="small" color="success" />
          <Chip label={`${errorCount} com erro`} size="small" color="error" />
          {submittingCount > 0 ? <Chip label={`${submittingCount} enviando`} size="small" color="info" /> : null}
        </Stack>

        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUploadRoundedIcon />}
            sx={{ textTransform: "none" }}
          >
            Selecionar multiplos arquivos
            <input
              hidden
              multiple
              type="file"
              accept=".csv,.xlsx"
              onChange={(event: ChangeEvent<HTMLInputElement>) => {
                if (!event.target.files || event.target.files.length === 0) return;
                onAddFiles(event.target.files);
                event.target.value = "";
              }}
            />
          </Button>
          <Button
            variant="contained"
            onClick={() => void onSubmitRows()}
            disabled={!canSubmit || submittingCount > 0}
          >
            {submittingCount > 0 ? <CircularProgress size={18} color="inherit" /> : "Enviar linhas validas para Bronze"}
          </Button>
        </Stack>
      </Stack>

      <Alert severity="info">
        Cada linha gera um <code>LeadBatch</code> independente. O mapeamento e aplicado uma unica vez para todos os
        lotes pendentes do workspace, e o pipeline continua por <code>batch_id</code>.
      </Alert>

      <BatchWorkspaceSummaryCard rows={rows} onOpenRowFlow={onOpenRowFlow} />

      {rows.length === 0 ? (
        <Paper variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Selecione varias planilhas CSV/XLSX para montar a grade de upload Bronze.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Arquivo</TableCell>
                <TableCell>Quem enviou</TableCell>
                <TableCell>Plataforma</TableCell>
                <TableCell>Data envio</TableCell>
                <TableCell>Evento</TableCell>
                <TableCell>Origem</TableCell>
                <TableCell>Tipo / Ativacao</TableCell>
                <TableCell>Pendencias</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Acoes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => {
                const selectedEvento = getBatchRowSelectedEvento(eventos, row.evento_id);
                const eventId = selectedEvento?.id ?? null;
                const ativacoes = eventId != null ? ativacoesByEventoId[eventId] ?? [] : [];
                const ativacoesLoadError = eventId != null ? ativacoesLoadErrorByEventoId[eventId] ?? null : null;
                const loadingAtivacoes = eventId != null ? Boolean(loadingAtivacoesByEventoId[eventId]) : false;
                const validationMessages = getBatchRowValidationErrors({
                  row,
                  selectedEvento,
                  ativacoes,
                  ativacoesLoadError,
                });

                return (
                  <BatchUploadRow
                    key={row.local_id}
                    row={row}
                    eventos={eventos}
                    selectedEvento={selectedEvento}
                    ativacoes={ativacoes}
                    ativacoesLoadError={ativacoesLoadError}
                    loadingAtivacoes={loadingAtivacoes}
                    agencias={agencias}
                    loadingAgencias={loadingAgencias}
                    agenciasLoadError={agenciasLoadError}
                    validationMessages={validationMessages}
                    onFieldChange={onFieldChange}
                    onOpenQuickCreateEvento={onOpenQuickCreateEvento}
                    onCreateAtivacao={onCreateAtivacao}
                    onSaveAgency={onSaveAgency}
                    onRemove={onRemoveRow}
                    onRetry={onRetryRow}
                    onOpenRowFlow={onOpenRowFlow}
                  />
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Stack>
  );
}
