import { act, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import type { EventoAgeAnalysis } from "../../../types/dashboard";
import {
  AgeDistributionChart,
  CustomTooltip,
  buildChartData,
  getResponsiveChartHeight,
} from "../AgeDistributionChart";

function buildEvent(eventoId: number, eventoNome: string): EventoAgeAnalysis {
  return {
    evento_id: eventoId,
    evento_nome: eventoNome,
    cidade: "Sao Paulo",
    estado: "SP",
    base_leads: 10,
    base_com_idade_volume: 9,
    base_bb_coberta_volume: 9,
    leads_proponente: 2,
    leads_ativacao: 8,
    leads_canal_desconhecido: 0,
    clientes_bb_volume: 4,
    clientes_bb_pct: 40,
    nao_clientes_bb_volume: 5,
    nao_clientes_bb_pct: 50,
    bb_indefinido_volume: 1,
    cobertura_bb_pct: 90,
    faixa_dominante: "faixa_18_25",
    faixa_dominante_status: "resolved",
    faixas: {
      faixa_18_25: { volume: 5, pct: 50 },
      faixa_26_40: { volume: 3, pct: 30 },
      faixa_18_40: { volume: 8, pct: 80 },
      fora_18_40: { volume: 1, pct: 10 },
      sem_info_volume: 1,
      sem_info_pct_da_base: 10,
    },
  };
}

function setViewportSize(width: number, height: number) {
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    writable: true,
    value: width,
  });
  Object.defineProperty(window, "innerHeight", {
    configurable: true,
    writable: true,
    value: height,
  });
}

describe("AgeDistributionChart", () => {
  const originalInnerWidth = window.innerWidth;
  const originalInnerHeight = window.innerHeight;

  beforeEach(() => {
    setViewportSize(1280, 900);
  });

  afterEach(() => {
    setViewportSize(originalInnerWidth, originalInnerHeight);
  });

  it("trunca o nome do evento no eixo X quando ele e longo", () => {
    const rows = buildChartData([
      buildEvent(1, "Evento muito longo para testar truncamento no eixo horizontal"),
    ]);

    expect(rows[0].eventoNomeCurto).toContain("…");
    expect(rows[0].eventoNomeCurto.length).toBeLessThanOrEqual(18);
  });

  it("mostra tooltip com volume e percentual por faixa etaria", () => {
    const rows = buildChartData([buildEvent(1, "Evento Tooltip")]);

    render(
      <CustomTooltip
        active
        label={rows[0].eventoNomeCurto}
        payload={[
          {
            payload: rows[0],
          },
        ]}
      />,
    );

    expect(screen.getAllByText("Evento Tooltip")).toHaveLength(2);
    expect(screen.getByText("18–25")).toBeInTheDocument();
    expect(screen.getByText("50,0% • 5")).toBeInTheDocument();
    expect(screen.getByText("26–40")).toBeInTheDocument();
    expect(screen.getByText("30,0% • 3")).toBeInTheDocument();
    expect(screen.getByText("Fora de 18–40")).toBeInTheDocument();
    expect(screen.getAllByText("10,0% • 1")).toHaveLength(2);
    expect(screen.getByText("Sem informacao")).toBeInTheDocument();
  });

  it("renderiza as quatro faixas com as cores definidas", () => {
    const { container } = render(<AgeDistributionChart events={[buildEvent(1, "Evento Alpha")]} />);

    expect(container.querySelector('[fill="#1976d2"]')).toBeTruthy();
    expect(container.querySelector('[fill="#2e7d32"]')).toBeTruthy();
    expect(container.querySelector('[fill="#ed6c02"]')).toBeTruthy();
    expect(container.querySelector('[fill="#9e9e9e"]')).toBeTruthy();
  });

  it("habilita scroll horizontal apenas quando ha mais de 10 eventos", () => {
    const tenEvents = Array.from({ length: 10 }, (_, index) =>
      buildEvent(index + 1, `Evento ${index + 1}`),
    );
    const elevenEvents = Array.from({ length: 11 }, (_, index) =>
      buildEvent(index + 1, `Evento ${index + 1}`),
    );

    const { rerender } = render(<AgeDistributionChart events={tenEvents} />);
    expect(screen.getByTestId("age-distribution-chart-scroll")).toHaveAttribute(
      "data-scroll-enabled",
      "false",
    );

    rerender(<AgeDistributionChart events={elevenEvents} />);
    expect(screen.getByTestId("age-distribution-chart-scroll")).toHaveAttribute(
      "data-scroll-enabled",
      "true",
    );
  });

  it("ajusta a altura do grafico ao viewport", async () => {
    setViewportSize(1280, 1000);
    render(<AgeDistributionChart events={[buildEvent(1, "Evento Responsivo")]} />);

    expect(screen.getByTestId("age-distribution-chart-canvas")).toHaveAttribute(
      "data-chart-height",
      String(getResponsiveChartHeight(1000)),
    );

    setViewportSize(1280, 640);
    act(() => {
      window.dispatchEvent(new Event("resize"));
    });

    await waitFor(() => {
      expect(screen.getByTestId("age-distribution-chart-canvas")).toHaveAttribute(
        "data-chart-height",
        String(getResponsiveChartHeight(640)),
      );
    });
  });
});
