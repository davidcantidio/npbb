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
    base_com_idade_volume: 9,
    base_bb_coberta_volume: 9,
    leads_proponente: 3,
    leads_ativacao: 7,
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
  it("renders colunas: evento, base, proponente, ativacao, clientes, nao clientes, 18-40, fora da faixa, sem idade", () => {
    render(<EventsAgeTable events={[buildEvent({})]} />);
    const table = screen.getByRole("table", { name: /analise etaria/i });
    const [
      eventCell,
      baseCell,
      propCell,
      ativCell,
      clientesBbCell,
      naoClientesCell,
      faixa1840Cell,
      foraFaixaCell,
      semIdadeCell,
    ] = getRowCells(1);

    expect(within(table).getByRole("button", { name: "Evento" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Base" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Proponente" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Ativacao" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Clientes BB" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Nao clientes" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "18-40" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Fora da faixa" })).toBeInTheDocument();
    expect(within(table).getByRole("button", { name: "Sem idade" })).toBeInTheDocument();

    expect(eventCell).toHaveTextContent("Evento Alpha");
    expect(eventCell).toHaveTextContent("Sao Paulo - SP");
    expect(baseCell).toHaveTextContent("10");
    expect(propCell).toHaveTextContent("3");
    expect(ativCell).toHaveTextContent("7");
    expect(clientesBbCell).toHaveTextContent(/4\s*\/\s*40,0%/);
    expect(naoClientesCell).toHaveTextContent(/5\s*\/\s*50,0%/);
    expect(faixa1840Cell).toHaveTextContent(/8\s*\/\s*80,0%/);
    expect(foraFaixaCell).toHaveTextContent(/2\s*\/\s*20,0%/);
    expect(semIdadeCell).toHaveTextContent(/0\s*\/\s*0,0%/);
    expect(faixa1840Cell.querySelector("[data-share-18-40]")).toHaveAttribute("data-share-18-40", "major");
    expect(foraFaixaCell.querySelector("[data-share-fora-faixa]")).toHaveAttribute("data-share-fora-faixa", "minor");
  }, 20_000);

  it("marca fora da faixa como maioria quando o percentual e superior a 50%", () => {
    render(
      <EventsAgeTable
        events={[
          buildEvent({
            faixas: {
              faixa_18_25: { volume: 0, pct: 0 },
              faixa_26_40: { volume: 0, pct: 0 },
              faixa_18_40: { volume: 1, pct: 10 },
              fora_18_40: { volume: 9, pct: 90 },
              sem_info_volume: 0,
              sem_info_pct_da_base: 0,
            },
          }),
        ]}
      />,
    );
    const [, , , , , , , foraFaixaCell] = getRowCells(1);
    expect(foraFaixaCell).toHaveTextContent(/9\s*\/\s*90,0%/);
    expect(foraFaixaCell.querySelector("[data-share-fora-faixa]")).toHaveAttribute("data-share-fora-faixa", "major");
  });

  it("marca 18-40 como minoria quando a fatia nao e maioria de 50%", () => {
    render(
      <EventsAgeTable
        events={[
          buildEvent({
            faixas: {
              faixa_18_25: { volume: 0, pct: 0 },
              faixa_26_40: { volume: 0, pct: 0 },
              faixa_18_40: { volume: 2, pct: 25 },
              fora_18_40: { volume: 6, pct: 75 },
              sem_info_volume: 0,
              sem_info_pct_da_base: 0,
            },
          }),
        ]}
      />,
    );
    const [, , , , , , faixa1840Cell] = getRowCells(1);
    expect(faixa1840Cell).toHaveTextContent(/2\s*\/\s*25,0%/);
    expect(faixa1840Cell.querySelector("[data-share-18-40]")).toHaveAttribute("data-share-18-40", "minor");
  });

  it("renders partial-hint in Clientes BB when coverage is below threshold (sem coluna de cobertura na tabela)", () => {
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
    const [, , , , clientesBbCell] = getRowCells(4);
    expect(clientesBbCell).toHaveTextContent("dados parciais");
  });

  it('renders "—" for BB cells when backend returns null client metrics', () => {
    render(
      <EventsAgeTable
        events={[
          buildEvent({
            evento_id: 3,
            evento_nome: "Evento Null",
            clientes_bb_volume: null,
            clientes_bb_pct: null,
            nao_clientes_bb_volume: null,
            nao_clientes_bb_pct: null,
            cobertura_bb_pct: 15,
          }),
        ]}
      />,
    );
    const [, , , , clientesBbCell, naoClientesCell] = getRowCells(3);

    expect(clientesBbCell).toHaveTextContent(/—\s*\/\s*—/);
    expect(naoClientesCell).toHaveTextContent(/—\s*\/\s*—/);
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
            nao_clientes_bb_volume: null,
            nao_clientes_bb_pct: null,
            cobertura_bb_pct: 15,
          }),
        ]}
      />,
    );

    const table = screen.getByRole("table", { name: /analise etaria/i });

    expect(getRenderedRowIds()).toEqual([2, 1, 3]);
    expect(within(table).getByRole("button", { name: "Base" }).closest("th")).toHaveAttribute(
      "aria-sort",
      "descending",
    );

    await user.click(within(table).getByRole("button", { name: "Base" }));
    await waitFor(() => {
      expect(getRenderedRowIds()).toEqual([3, 1, 2]);
    });
    expect(within(table).getByRole("button", { name: "Base" }).closest("th")).toHaveAttribute(
      "aria-sort",
      "ascending",
    );

    await user.click(within(table).getByRole("button", { name: "Clientes BB" }));
    await waitFor(() => {
      expect(getRenderedRowIds()).toEqual([2, 1, 3]);
    });
    expect(within(table).getByRole("button", { name: "Clientes BB" }).closest("th")).toHaveAttribute(
      "aria-sort",
      "descending",
    );
  }, 20_000);

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
