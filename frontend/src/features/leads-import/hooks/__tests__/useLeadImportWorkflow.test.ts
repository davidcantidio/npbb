import { describe, expect, it } from "vitest";
import type { LeadImportPreview } from "../../../../services/leads_import";
import { useLeadImportWorkflow } from "../useLeadImportWorkflow";

describe("useLeadImportWorkflow", () => {
  it("updates mapping immutably", () => {
    const { updateSuggestionAt } = useLeadImportWorkflow();
    const preview: LeadImportPreview = {
      filename: "sample.csv",
      headers: ["Email", "CPF"],
      rows: [["a@a.com", "123"]],
      delimiter: ";",
      start_index: 0,
      suggestions: [
        { coluna: "Email", campo: "email", confianca: 0.9 },
        { coluna: "CPF", campo: "cpf", confianca: 0.8 },
      ],
      samples_by_column: [["a@a.com"], ["123"]],
    };

    const next = updateSuggestionAt(preview, 1, "nome");

    expect(next).not.toBe(preview);
    expect(next?.suggestions).not.toBe(preview.suggestions);
    expect(next?.suggestions[0]).toBe(preview.suggestions[0]);
    expect(next?.suggestions[1]).toEqual({ coluna: "CPF", campo: "nome", confianca: 0.8 });
  });
});
