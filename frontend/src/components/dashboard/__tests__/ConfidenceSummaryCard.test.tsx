import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { buildAgeAnalysisFixture } from "../../../pages/dashboard/__tests__/ageAnalysisFixtures";
import { buildAgeAnalysisViewModel } from "../../../utils/ageAnalysisViewModel";
import { ConfidenceSummaryCard } from "../ConfidenceSummaryCard";

describe("ConfidenceSummaryCard", () => {
  it("exibe metricas de sem conexao com evento e BB indefinido no consolidado", () => {
    const data = buildAgeAnalysisFixture();
    const viewModel = buildAgeAnalysisViewModel(data);

    render(<ConfidenceSummaryCard data={data} viewModel={viewModel} />);

    const section = screen.getByRole("region", { name: /confianca e cobertura/i });
    expect(within(section).getByText(/Sem conexao com evento:/)).toBeInTheDocument();
    expect(within(section).getByText(/Sem definicao de cliente BB:/)).toBeInTheDocument();
  });
});
