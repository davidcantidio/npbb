import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { AgeAnalysisResponse } from "../../../types/dashboard";
import { buildAgeAnalysisFixture } from "../../../pages/dashboard/__tests__/ageAnalysisFixtures";
import { AgeAnalysisKpiGrid } from "../AgeAnalysisKpiGrid";

function buildResponse(): AgeAnalysisResponse {
  const faixas = {
    faixa_18_25: { volume: 30, pct: 30 },
    faixa_26_40: { volume: 50, pct: 50 },
    faixa_18_40: { volume: 80, pct: 80 },
    fora_18_40: { volume: 20, pct: 20 },
    sem_info_volume: 0,
    sem_info_pct_da_base: 0,
  };
  return buildAgeAnalysisFixture({
    por_evento: [
      {
        evento_id: 1,
        evento_nome: "Evento Alpha",
        cidade: "Sao Paulo",
        estado: "SP",
        base_leads: 100,
        base_com_idade_volume: 100,
        base_bb_coberta_volume: 90,
        leads_proponente: 30,
        leads_ativacao: 70,
        leads_canal_desconhecido: 0,
        clientes_bb_volume: 40,
        clientes_bb_pct: 40,
        nao_clientes_bb_volume: 55,
        nao_clientes_bb_pct: 55,
        bb_indefinido_volume: 5,
        cobertura_bb_pct: 90,
        faixa_dominante: "faixa_26_40",
        faixa_dominante_status: "resolved",
        faixas,
      },
    ],
    consolidado: {
      base_total: 100,
      base_com_idade_volume: 100,
      base_bb_coberta_volume: 90,
      leads_proponente: 30,
      leads_ativacao: 70,
      leads_canal_desconhecido: 0,
      clientes_bb_volume: 40,
      clientes_bb_pct: 40,
      nao_clientes_bb_volume: 55,
      nao_clientes_bb_pct: 55,
      bb_indefinido_volume: 5,
      bb_indefinido_pct: 5,
      cobertura_bb_pct: 90,
      faixas,
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
      faixa_dominante_status: "resolved",
      clientes_bb_base_idade_volume: 40,
      clientes_bb_faixa_18_40_volume: 30,
      clientes_bb_faixa_18_40_pct: 75,
      clientes_bb_fora_18_40_volume: 10,
      clientes_bb_fora_18_40_pct: 25,
      nao_clientes_bb_base_idade_volume: 55,
      nao_clientes_bb_faixa_18_40_volume: 40,
      nao_clientes_bb_faixa_18_40_pct: 72.73,
      nao_clientes_bb_fora_18_40_volume: 15,
      nao_clientes_bb_fora_18_40_pct: 27.27,
    },
  });
}

describe("AgeAnalysisKpiGrid", () => {
  it("exibe o tooltip de Leads validos com o texto explicativo", async () => {
    const user = userEvent.setup();
    render(<AgeAnalysisKpiGrid data={buildResponse()} />);

    const leadsValidosTooltipButton = screen.getByRole("button", {
      name: "Saiba mais sobre Leads válidos",
    });
    expect(leadsValidosTooltipButton).toHaveTextContent("ℹ️");
    await user.hover(leadsValidosTooltipButton);
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Quantidade de vinculos com data de nascimento suficiente para calcular a idade.",
    );
  }, 20_000);
});
