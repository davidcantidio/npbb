import type { OrigemLoteLeadBatch } from "../../../services/leads_import";

export type BronzeImportMode = "event_linked" | "enrichment_only";
export type BronzeTipoLeadProponente = "bilheteria" | "entrada_evento";
export type BronzeTipoLeadProponenteSelection = BronzeTipoLeadProponente | "";

export type BronzeMetadataFormValues = {
  importMode: BronzeImportMode;
  eventoId: string;
  origemLote: OrigemLoteLeadBatch | null;
  tipoLeadProponente: BronzeTipoLeadProponenteSelection;
  ativacaoId: string;
};

type BronzeMetadataValidationOptions = {
  activationImportSupported?: boolean;
  activationImportBlockReason?: string | null;
  ativacoesLoadError?: string | null;
  validAtivacaoIds?: number[];
};

type BronzeMetadataPayload = {
  evento_id?: number;
  origem_lote?: OrigemLoteLeadBatch;
  enrichment_only: boolean;
  tipo_lead_proponente?: BronzeTipoLeadProponente;
  ativacao_id?: number;
};

export function normalizeBronzeTipoLeadProponenteSelection(
  value: string | null | undefined,
  fallback: BronzeTipoLeadProponenteSelection = "",
): BronzeTipoLeadProponenteSelection {
  return value === "bilheteria" || value === "entrada_evento" ? value : fallback;
}

export function parsePositiveInt(value: string | number | null | undefined) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export function bronzeImportModeFromFlag(
  enrichmentOnly: boolean | null | undefined,
): BronzeImportMode {
  return enrichmentOnly ? "enrichment_only" : "event_linked";
}

export function getBronzeImportModeLabel(mode: BronzeImportMode) {
  return mode === "enrichment_only"
    ? "Enviar para enriquecimento sem evento"
    : "Importar para evento";
}

export function getBronzeImportModeHelpText(mode: BronzeImportMode) {
  return mode === "enrichment_only"
    ? "Use este modo para enriquecer dados de leads sem vinculá-los a um evento. O lote segue sem evento e sem ativação vinculada."
    : "Use este modo quando os leads precisarem ficar vinculados a um evento de referência.";
}

export function getBronzeImportModeSummary(mode: BronzeImportMode) {
  return mode === "enrichment_only"
    ? "Enriquecimento sem evento"
    : "Importação vinculada a evento";
}

export function sanitizeBronzeMetadataFormValues(
  values: BronzeMetadataFormValues,
): BronzeMetadataFormValues {
  if (values.importMode === "enrichment_only") {
    return {
      ...values,
      eventoId: "",
      ativacaoId: "",
    };
  }

  if (values.origemLote === "proponente") {
    return {
      ...values,
      ativacaoId: "",
    };
  }

  return values;
}

export function buildBronzeMetadataPayload(
  values: BronzeMetadataFormValues,
): BronzeMetadataPayload {
  const sanitizedValues = sanitizeBronzeMetadataFormValues(values);
  const eventoId = parsePositiveInt(sanitizedValues.eventoId);
  const ativacaoId = parsePositiveInt(sanitizedValues.ativacaoId);

  if (sanitizedValues.importMode === "enrichment_only") {
    return {
      enrichment_only: true,
      ...(sanitizedValues.tipoLeadProponente
        ? { tipo_lead_proponente: sanitizedValues.tipoLeadProponente }
        : {}),
    };
  }

  if (sanitizedValues.origemLote === "ativacao") {
    return {
      evento_id: eventoId ?? undefined,
      origem_lote: "ativacao",
      enrichment_only: false,
      ativacao_id: ativacaoId ?? undefined,
    };
  }

  return {
    evento_id: eventoId ?? undefined,
    origem_lote: "proponente",
    enrichment_only: false,
    ...(sanitizedValues.tipoLeadProponente
      ? { tipo_lead_proponente: sanitizedValues.tipoLeadProponente }
      : {}),
  };
}

export function validateBronzeMetadataFormValues(
  values: BronzeMetadataFormValues,
  options: BronzeMetadataValidationOptions = {},
) {
  const sanitizedValues = sanitizeBronzeMetadataFormValues(values);
  const eventoId = parsePositiveInt(values.eventoId);
  const ativacaoId = parsePositiveInt(values.ativacaoId);
  const errors: string[] = [];

  if (sanitizedValues.importMode === "enrichment_only") {
    if (eventoId != null) {
      errors.push("O modo de enriquecimento sem evento não permite evento de referência.");
    }
    if (ativacaoId != null) {
      errors.push("O modo de enriquecimento sem evento não permite ativação vinculada.");
    }
    return [...new Set(errors)];
  }

  if (eventoId == null) {
    errors.push("Selecione o evento de referência desta importação.");
  }

  if (sanitizedValues.origemLote === "proponente" && !sanitizedValues.tipoLeadProponente) {
    errors.push("Selecione a classificação do lead proponente.");
  }

  if (sanitizedValues.origemLote === "ativacao") {
    if (options.activationImportBlockReason) {
      errors.push(options.activationImportBlockReason);
    } else if (options.ativacoesLoadError) {
      errors.push(options.ativacoesLoadError);
    }

    if (ativacaoId == null) {
      errors.push("Selecione a ativação desta importação.");
    } else if (
      options.validAtivacaoIds &&
      options.validAtivacaoIds.length > 0 &&
      !options.validAtivacaoIds.includes(ativacaoId)
    ) {
      errors.push("Selecione uma ativação válida para o evento.");
    }
  }

  return [...new Set(errors)];
}
