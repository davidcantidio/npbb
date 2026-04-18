import { Chip, Paper, Stack, Typography } from "@mui/material";

import { LeadBatch } from "../../../services/leads_import";

function pipelineStatusChipColor(
  status: LeadBatch["pipeline_status"],
): "default" | "info" | "success" | "warning" | "error" {
  if (status === "pass") return "success";
  if (status === "pass_with_warnings") return "warning";
  if (status === "stalled") return "warning";
  if (status === "fail") return "error";
  return "default";
}

function pipelineStatusLabel(status: LeadBatch["pipeline_status"]) {
  if (status === "pass") return "Pipeline aprovado";
  if (status === "pass_with_warnings") return "Pipeline com avisos";
  if (status === "stalled") return "Pipeline interrompido (retomavel)";
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

export default function BatchSummaryCard({ batch }: { batch: LeadBatch }) {
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
          {batch.evento_id != null ? (
            <Stack spacing={0.5}>
              <Typography variant="caption" color="text.secondary">
                Evento (id)
              </Typography>
              <Typography variant="body2">{batch.evento_id}</Typography>
            </Stack>
          ) : null}
          <Stack spacing={0.5}>
            <Typography variant="caption" color="text.secondary">
              Origem do lote
            </Typography>
            <Typography variant="body2">
              {(batch.origem_lote ?? "proponente") === "ativacao" ? "Ativacao" : "Proponente"}
              {(batch.origem_lote ?? "proponente") === "ativacao" && batch.ativacao_id != null
                ? ` (ativacao #${batch.ativacao_id})`
                : null}
              {(batch.origem_lote ?? "proponente") === "proponente" && batch.tipo_lead_proponente
                ? ` — ${batch.tipo_lead_proponente}`
                : null}
            </Typography>
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
