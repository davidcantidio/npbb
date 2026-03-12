import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { AgeAnalysisResponse } from "../../../types/dashboard";
import { AgeAnalysisKpiGrid } from "../AgeAnalysisKpiGrid";

function buildResponse(): AgeAnalysisResponse {
  return {
    version: 1,
    generated_at: "2026-03-08T12:00:00Z",
    filters: {
      data_inicio: null,
      data_fim: null,
      evento_id: null,
    },
    por_evento: [
      {
        evento_id: 1,
        evento_nome: "Evento Alpha",
        cidade: "Sao Paulo",
        estado: "SP",
        base_leads: 100,
        clientes_bb_volume: 40,
        clientes_bb_pct: 40,
        cobertura_bb_pct: 90,
        faixa_dominante: "faixa_26_40",
        faixas: {
          faixa_18_25: { volume: 30, pct: 30 },
          faixa_26_40: { volume: 50, pct: 50 },
          fora_18_40: { volume: 20, pct: 20 },
          sem_info_volume: 0,
          sem_info_pct_da_base: 0,
        },
      },
    ],
    consolidado: {
      base_total: 100,
      clientes_bb_volume: 40,
      clientes_bb_pct: 40,
      cobertura_bb_pct: 90,
      faixas: {
        faixa_18_25: { volume: 30, pct: 30 },
        faixa_26_40: { volume: 50, pct: 50 },
        fora_18_40: { volume: 20, pct: 20 },
        sem_info_volume: 0,
        sem_info_pct_da_base: 0,
      },
      top_eventos: [
        {
          evento_id: 1,
          evento_nome: "Evento Alpha",
          base_leads: 100,
          faixa_dominante: "faixa_26_40",
        },
      ],
      media_por_evento: 100,
      mediana_por_evento: 100,
      concentracao_top3_pct: 100,
    },
  };
}

describe("AgeAnalysisKpiGrid", () => {
  it("exibe tooltips para cobertura BB e faixa dominante com os textos da issue", async () => {
    const user = userEvent.setup();

    render(
      <AgeAnalysisKpiGrid
        data={buildResponse()}
        eventosTotal={1}
        appliedFilters={{
          evento_id: null,
          data_inicio: "",
          data_fim: "",
        }}
      />,
    );

    const faixaTooltipButton = screen.getByRole("button", {
      name: "Saiba mais sobre Faixa Dominante",
    });
    expect(faixaTooltipButton).toHaveTextContent("ℹ️");
    await user.hover(faixaTooltipButton);
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Faixa etária com maior volume de leads neste evento",
    );

    await user.unhover(faixaTooltipButton);

    const coberturaTooltipButton = screen.getByRole("button", {
      name: "Saiba mais sobre Cobertura BB",
    });
    expect(coberturaTooltipButton).toHaveTextContent("ℹ️");
    await user.hover(coberturaTooltipButton);
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Percentual de leads com informação de vínculo BB disponível",
    );
  });
});
