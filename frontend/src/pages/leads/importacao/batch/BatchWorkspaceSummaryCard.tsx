import { Button, Chip, Paper, Stack, Typography } from "@mui/material";

import { BatchUploadRowDraft } from "./useBatchUploadDraft";

type Props = {
  rows: BatchUploadRowDraft[];
  onOpenRowFlow: (row: BatchUploadRowDraft) => void;
};

function isTerminalRow(row: BatchUploadRowDraft) {
  return (
    row.downstream_stage === "gold" ||
    row.downstream_pipeline_status === "pass" ||
    row.downstream_pipeline_status === "pass_with_warnings" ||
    row.downstream_pipeline_status === "fail"
  );
}

function needsPipelineAction(row: BatchUploadRowDraft) {
  return (
    row.downstream_stage === "silver" &&
    (row.downstream_pipeline_status === "pending" || row.downstream_pipeline_status === "stalled")
  );
}

export default function BatchWorkspaceSummaryCard({ rows, onOpenRowFlow }: Props) {
  const createdRows = rows.filter((row) => row.created_batch_id != null);
  const mappingPendingRows = createdRows.filter(
    (row) => row.downstream_stage === "bronze" && row.import_mode === "event_linked",
  );
  const enrichmentMappingRows = createdRows.filter(
    (row) => row.downstream_stage === "bronze" && row.import_mode === "enrichment_only",
  );
  const pipelinePendingRows = createdRows.filter(needsPipelineAction);
  const terminalRows = createdRows.filter(isTerminalRow);
  const primaryRow = mappingPendingRows[0] ?? enrichmentMappingRows[0] ?? pipelinePendingRows[0] ?? null;

  if (createdRows.length === 0) {
    return null;
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
      <Stack spacing={1.5}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={1.5}
          justifyContent="space-between"
          alignItems={{ xs: "stretch", md: "center" }}
        >
          <Stack spacing={0.5}>
            <Typography variant="subtitle1" fontWeight={700}>
              Workspace do batch Bronze
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Continue o fluxo dos lotes criados sem sair da grade. O mapeamento unificado vale apenas para lotes
              vinculados a evento; linhas de enriquecimento sem evento seguem por arquivo.
            </Typography>
          </Stack>
          {primaryRow ? (
            <Button variant="contained" onClick={() => onOpenRowFlow(primaryRow)}>
              {primaryRow.downstream_stage === "bronze" && primaryRow.import_mode === "event_linked"
                ? "Abrir mapeamento unificado"
                : primaryRow.downstream_stage === "bronze"
                  ? "Abrir proximo mapeamento individual"
                : "Abrir proximo pipeline pendente"}
            </Button>
          ) : null}
        </Stack>

        <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
          <Chip label={`${createdRows.length} lote(s) criados`} color="success" size="small" />
          <Chip label={`${mappingPendingRows.length} aguardando mapeamento batch`} size="small" />
          <Chip label={`${enrichmentMappingRows.length} enriquecimento sem evento`} variant="outlined" size="small" />
          <Chip label={`${pipelinePendingRows.length} pronto(s) para pipeline/retomada`} color="info" size="small" />
          <Chip label={`${terminalRows.length} terminal(is)`} color="default" size="small" />
        </Stack>
      </Stack>
    </Paper>
  );
}
