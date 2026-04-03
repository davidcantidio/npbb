import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ConsolidadoAgeAnalysis } from "../../../types/dashboard";
import { ConsolidatedPanel } from "../ConsolidatedPanel";

function buildConsolidated(overrides: Partial<ConsolidadoAgeAnalysis> = {}): ConsolidadoAgeAnalysis {
  return {
    base_total: 250,
    clientes_bb_volume: 120,
    clientes_bb_pct: 48,
    cobertura_bb_pct: 90,
    faixas: {
      faixa_18_25: { volume: 100, pct: 40 },
      faixa_26_40: { volume: 120, pct: 48 },
      fora_18_40: { volume: 20, pct: 8 },
      sem_info_volume: 10,
      sem_info_pct_da_base: 4,
    },
    top_eventos: [
      {
        evento_id: 1,
        evento_nome: "Evento Alpha",
        base_leads: 100,
        faixa_dominante: "faixa_26_40",
      },
      {
        evento_id: 2,
        evento_nome: "Evento Beta",
        base_leads: 60,
        faixa_dominante: "faixa_18_25",
      },
      {
        evento_id: 3,
        evento_nome: "Evento Gama",
        base_leads: 40,
        faixa_dominante: "faixa_18_25",
      },
    ],
    media_por_evento: 83.333,
    mediana_por_evento: 60.49,
    concentracao_top3_pct: 80,
    ...overrides,
  };
}

describe("ConsolidatedPanel", () => {
  it("exibe ranking Top 3 com nome, volume e percentual da base", () => {
    render(<ConsolidatedPanel data={buildConsolidated()} />);

    expect(screen.getByText("1º Evento Alpha")).toBeInTheDocument();
    expect(screen.getByText("2º Evento Beta")).toBeInTheDocument();
    expect(screen.getByText("3º Evento Gama")).toBeInTheDocument();

    expect(screen.getAllByText(/^100$/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/^60$/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/^40$/).length).toBeGreaterThan(0);
    expect(screen.getByText("40,0%")).toBeInTheDocument();
    expect(screen.getByText("24,0%")).toBeInTheDocument();
    expect(screen.getByText("16,0%")).toBeInTheDocument();
  });

  it("exibe media com 1 casa decimal, mediana inteira arredondada e concentracao em percentual", () => {
    render(
      <ConsolidatedPanel
        data={buildConsolidated({
          media_por_evento: 1234.56,
          mediana_por_evento: 77.6,
          concentracao_top3_pct: 66.7,
        })}
      />,
    );

    const mediaBlock = screen.getByText("Media por evento").closest("div")?.parentElement;
    if (!mediaBlock) throw new Error("Media block not found");
    expect(within(mediaBlock).getByText("1.234,6")).toBeInTheDocument();

    const medianaBlock = screen.getByText("Mediana por evento").closest("div")?.parentElement;
    if (!medianaBlock) throw new Error("Mediana block not found");
    expect(within(medianaBlock).getByText(/^78$/)).toBeInTheDocument();
    expect(within(medianaBlock).queryByText("77,6")).not.toBeInTheDocument();

    const concentracaoBlock = screen.getByText("Concentracao Top 3").closest("div")?.parentElement;
    if (!concentracaoBlock) throw new Error("Concentracao block not found");
    expect(within(concentracaoBlock).getByText("66,7%")).toBeInTheDocument();
  });

  it("exibe tooltip interpretativo de media por evento", async () => {
    render(<ConsolidatedPanel data={buildConsolidated()} />);

    fireEvent.mouseOver(screen.getByRole("button", { name: "Saiba mais sobre Media por evento" }));
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Soma dos volumes dividida pela quantidade de eventos",
    );
  });

  it("exibe tooltip interpretativo de mediana por evento", async () => {
    render(<ConsolidatedPanel data={buildConsolidated()} />);

    fireEvent.mouseOver(screen.getByRole("button", { name: "Saiba mais sobre Mediana por evento" }));
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Volume central quando os eventos são ordenados por tamanho. Quando poucos eventos são muito grandes, a mediana é mais representativa do tamanho típico.",
    );
  });

  it("exibe tooltip interpretativo de concentracao top 3", async () => {
    render(<ConsolidatedPanel data={buildConsolidated()} />);

    fireEvent.mouseOver(screen.getByRole("button", { name: "Saiba mais sobre Concentracao Top 3" }));
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Percentual da base total representada pelos 3 maiores eventos",
    );
  });

  it("exibe tooltip interpretativo de faixa dominante", async () => {
    render(<ConsolidatedPanel data={buildConsolidated()} />);

    const faixaDominanteButtons = screen.getAllByRole("button", { name: "Saiba mais sobre Faixa dominante" });
    fireEvent.mouseOver(faixaDominanteButtons[0]);
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Faixa etária com maior volume de leads neste evento",
    );
  });
});
