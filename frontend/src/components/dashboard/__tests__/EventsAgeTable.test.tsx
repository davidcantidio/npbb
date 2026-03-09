import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { EventoAgeAnalysis } from "../../../types/dashboard";
import { EventsAgeTable } from "../EventsAgeTable";

function buildEvent(overrides: Partial<EventoAgeAnalysis>): EventoAgeAnalysis {
  return {
    evento_id: 1,
    evento_nome: "Evento Alpha",
    cidade: "Sao Paulo",
    estado: "SP",
    base_leads: 10,
    clientes_bb_volume: 4,
    clientes_bb_pct: 40,
    cobertura_bb_pct: 90,
    faixa_dominante: "faixa_18_25",
    faixas: {
      faixa_18_25: { volume: 5, pct: 50 },
      faixa_26_40: { volume: 3, pct: 30 },
      fora_18_40: { volume: 2, pct: 20 },
      sem_info_volume: 0,
      sem_info_pct_da_base: 0,
    },
    ...overrides,
  };
}

function getRenderedRowIds() {
  return screen
    .getAllByTestId(/events-age-table-row-/)
    .map((row) => Number(row.getAttribute("data-testid")?.replace("events-age-table-row-", "")));
}

function getRowCells(eventId: number) {
  const row = screen.getByTestId(`events-age-table-row-${eventId}`);
  return within(row).getAllByRole("cell");
}

describe("EventsAgeTable", () => {
  it("renders all required fields from PRD section 3.2 and keeps extra columns", () => {
    render(<EventsAgeTable events={[buildEvent({})]} />);
    const [eventCell, baseCell, clientesBbCell, naoClientesCell, , faixa18a25Cell, faixa26a40Cell, fora1840Cell, , faixaDominanteCell] =
      getRowCells(1);

    expect(screen.getByRole("button", { name: "Evento" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Base" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Clientes BB" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Nao clientes" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "18-25" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "26-40" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Fora 18-40" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Faixa dominante" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cobertura BB" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sem info" })).toBeInTheDocument();

    expect(eventCell).toHaveTextContent("Evento Alpha");
    expect(eventCell).toHaveTextContent("Sao Paulo - SP");
    expect(baseCell).toHaveTextContent("10");
    expect(clientesBbCell).toHaveTextContent(/4\s*\/\s*40,0%/);
    expect(naoClientesCell).toHaveTextContent(/6\s*\/\s*60,0%/);
    expect(faixa18a25Cell).toHaveTextContent(/5\s*\/\s*50,0%/);
    expect(faixa26a40Cell).toHaveTextContent(/3\s*\/\s*30,0%/);
    expect(fora1840Cell).toHaveTextContent(/2\s*\/\s*20,0%/);
    expect(faixaDominanteCell).toHaveTextContent("18–25");
  });

  it("renders compact warning banner text when coverage is partial", () => {
    render(
      <EventsAgeTable
        events={[
          buildEvent({
            evento_id: 4,
            evento_nome: "Evento Warning",
            clientes_bb_volume: null,
            clientes_bb_pct: null,
            cobertura_bb_pct: 65,
          }),
        ]}
      />,
    );

    expect(screen.getByTestId("coverage-banner-warning-compact")).toBeInTheDocument();
    expect(
      screen.getByText("Dados parcialmente disponiveis. Realize o cruzamento completo com a base do Banco."),
    ).toBeInTheDocument();
  });

  it('renders "—" for BB cells and the danger banner when backend returns null coverage values', () => {
    render(
      <EventsAgeTable
        events={[
          buildEvent({
            evento_id: 3,
            evento_nome: "Evento Null",
            clientes_bb_volume: null,
            clientes_bb_pct: null,
            cobertura_bb_pct: 15,
          }),
        ]}
      />,
    );
    const [, , clientesBbCell, naoClientesCell] = getRowCells(3);

    expect(clientesBbCell).toHaveTextContent(/—\s*\/\s*—/);
    expect(naoClientesCell).toHaveTextContent(/—\s*\/\s*—/);
    expect(screen.getByTestId("coverage-banner-danger-compact")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Dados de vinculo BB indisponiveis para este evento - realize o cruzamento com a base de dados do Banco.",
      ),
    ).toBeInTheDocument();
  });

  it("sorts by numeric columns through header click and updates visual direction", async () => {
    const user = userEvent.setup();
    render(
      <EventsAgeTable
        events={[
          buildEvent({ evento_id: 1, evento_nome: "Evento Alpha", base_leads: 10, clientes_bb_volume: 4 }),
          buildEvent({ evento_id: 2, evento_nome: "Evento Beta", base_leads: 20, clientes_bb_volume: 12 }),
          buildEvent({
            evento_id: 3,
            evento_nome: "Evento Gamma",
            base_leads: 5,
            clientes_bb_volume: null,
            clientes_bb_pct: null,
            cobertura_bb_pct: 15,
          }),
        ]}
      />,
    );

    expect(getRenderedRowIds()).toEqual([2, 1, 3]);
    expect(screen.getByRole("button", { name: "Base" }).closest("th")).toHaveAttribute(
      "aria-sort",
      "descending",
    );

    await user.click(screen.getByRole("button", { name: "Base" }));
    await waitFor(() => {
      expect(getRenderedRowIds()).toEqual([3, 1, 2]);
    });
    expect(screen.getByRole("button", { name: "Base" }).closest("th")).toHaveAttribute(
      "aria-sort",
      "ascending",
    );

    await user.click(screen.getByRole("button", { name: "Clientes BB" }));
    await waitFor(() => {
      expect(getRenderedRowIds()).toEqual([2, 1, 3]);
    });
    expect(screen.getByRole("button", { name: "Clientes BB" }).closest("th")).toHaveAttribute(
      "aria-sort",
      "descending",
    );
  });

  it("makes rows clickable and calls onSelectEvento with the event id", async () => {
    const user = userEvent.setup();
    const onSelectEvento = vi.fn();
    render(
      <EventsAgeTable
        events={[
          buildEvent({ evento_id: 1, evento_nome: "Evento Alpha" }),
          buildEvent({ evento_id: 2, evento_nome: "Evento Beta" }),
        ]}
        onSelectEvento={onSelectEvento}
      />,
    );

    await user.click(screen.getByTestId("events-age-table-row-2"));

    expect(onSelectEvento).toHaveBeenCalledTimes(1);
    expect(onSelectEvento).toHaveBeenCalledWith(2);
  });

  it("keeps an explicit horizontal scroll container for small screens", () => {
    render(<EventsAgeTable events={[buildEvent({})]} />);

    const scrollContainer = screen.getByTestId("events-age-table-scroll");
    expect(scrollContainer).toHaveAttribute("data-scroll-x", "enabled");
    expect(within(scrollContainer).getByTestId("events-age-table-grid")).toBeInTheDocument();
  });
});
