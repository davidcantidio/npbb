import type { AgeAnalysisResponse } from "../types/dashboard";
import { formatInteger, formatPercent } from "./ageAnalysis";

export type AgeAnalysisViewModel = {
  ageReferenceLabel: string;
  generatedAtLabel: string;
  lineageSummary: string;
  confidenceNotes: string[];
  executiveHighlights: string[];
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("pt-BR");
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("pt-BR");
}

export function buildAgeAnalysisViewModel(data: AgeAnalysisResponse): AgeAnalysisViewModel {
  const confidence = data.confianca_consolidado;
  const lineageSummary =
    confidence.lineage_mix.length > 0
      ? confidence.lineage_mix
          .map((row) => `${row.label}: ${formatInteger(row.volume)} (${formatPercent(row.pct)})`)
          .join(" | ")
      : "Sem lineage disponivel para o filtro.";

  const confidenceNotes: string[] = [];
  if (!confidence.evento_nome_backfill_habilitado) {
    confidenceNotes.push("Fallback por nome do evento desabilitado.");
  }
  if (confidence.ambiguous_event_name_volume > 0) {
    confidenceNotes.push(
      `${formatInteger(confidence.ambiguous_event_name_volume)} lead(s) foram descartados por ambiguidade de nome.`,
    );
  }
  if (confidence.dedupe_suppressed_volume > 0) {
    confidenceNotes.push(
      `${formatInteger(confidence.dedupe_suppressed_volume)} candidato(s) foram suprimidos por deduplicacao.`,
    );
  }
  if (confidence.event_name_missing_volume > 0) {
    confidenceNotes.push(
      `${formatInteger(confidence.event_name_missing_volume)} lead(s) ficaram sem correspondencia valida por nome.`,
    );
  }
  if (confidenceNotes.length === 0) {
    confidenceNotes.push("Sem alertas estruturais de merge neste filtro.");
  }

  return {
    ageReferenceLabel: formatDate(data.age_reference_date),
    generatedAtLabel: formatDateTime(data.generated_at),
    lineageSummary,
    confidenceNotes,
    executiveHighlights: [
      `Base utilizavel: ${formatInteger(data.consolidado.base_com_idade_volume)} com idade e ${formatInteger(
        data.consolidado.base_bb_coberta_volume,
      )} com cobertura BB.`,
      `Lineage consolidada: ${lineageSummary}`,
    ],
  };
}
