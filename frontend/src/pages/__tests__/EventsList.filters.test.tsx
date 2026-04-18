import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import EventsList from "../EventsList";
import { useAuth } from "../../store/auth";
import {
  exportEventosCsv,
  importEventosCsv,
  listDiretorias,
  listEventos,
  listStatusEvento,
  updateEvento,
} from "../../services/eventos";
import { listAgencias } from "../../services/agencias";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/agencias", () => ({ listAgencias: vi.fn() }));
vi.mock("../../services/eventos", () => ({
  exportEventosCsv: vi.fn(),
  importEventosCsv: vi.fn(),
  listDiretorias: vi.fn(),
  listEventos: vi.fn(),
  listStatusEvento: vi.fn(),
  updateEvento: vi.fn(),
}));
vi.mock("../../components/eventos/EventoRow", () => ({
  EventoRow: ({ item }: { item: { nome: string } }) => (
    <tr>
      <td>{item.nome}</td>
    </tr>
  ),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListAgencias = vi.mocked(listAgencias);
const mockedExportEventosCsv = vi.mocked(exportEventosCsv);
const mockedImportEventosCsv = vi.mocked(importEventosCsv);
const mockedListDiretorias = vi.mocked(listDiretorias);
const mockedListEventos = vi.mocked(listEventos);
const mockedListStatusEvento = vi.mocked(listStatusEvento);
const mockedUpdateEvento = vi.mocked(updateEvento);

const currentPageEvento = {
  id: 93,
  nome: "Evento Atual",
  cidade: "Brasilia",
  estado: "DF",
  status_id: 1,
  agencia_id: null,
  diretoria_id: null,
  data_inicio_prevista: "2026-03-26",
  data_fim_prevista: "2026-03-27",
  data_inicio_realizada: null,
  data_fim_realizada: null,
  investimento: null,
  data_health: null,
  created_at: "2026-03-01T00:00:00Z",
  updated_at: "2026-03-01T00:00:00Z",
  qr_code_url: null,
};

const hiddenByPaginationEvento = {
  id: 5,
  nome: "Show Rural Coopavel",
  cidade: "Cascavel",
  estado: "PR",
  status_id: 1,
  agencia_id: 1,
  diretoria_id: 1,
  data_inicio_prevista: "2026-02-09",
  data_fim_prevista: "2026-02-10",
  data_inicio_realizada: null,
  data_fim_realizada: null,
  investimento: null,
  data_health: null,
  created_at: "2026-01-26T14:42:55.987226Z",
  updated_at: "2026-01-26T14:42:55.987226Z",
  qr_code_url: null,
};

describe("EventsList filters", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    const slot = document.createElement("div");
    slot.id = "events-filters-slot";
    document.body.appendChild(slot);

    mockedUseAuth.mockReturnValue({
      token: "token",
      user: { id: 1, email: "qa@npbb.com.br", tipo_usuario: "npbb", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });

    mockedListAgencias.mockResolvedValue([] as never);
    mockedListDiretorias.mockResolvedValue([] as never);
    mockedListStatusEvento.mockResolvedValue([{ id: 1, nome: "Previsto" }] as never);
    mockedExportEventosCsv.mockResolvedValue({ blob: new Blob(), filename: "eventos.csv" } as never);
    mockedImportEventosCsv.mockResolvedValue({
      total: 0,
      success: 0,
      failed: 0,
      errors: [],
    } as never);
    mockedUpdateEvento.mockResolvedValue(currentPageEvento as never);
    mockedListEventos.mockImplementation(async (_token, params) => {
      if (params?.search === hiddenByPaginationEvento.nome) {
        return {
          total: 1,
          items: [hiddenByPaginationEvento],
        } as never;
      }
      if (params?.limit === 200) {
        return {
          total: 89,
          items: [currentPageEvento, hiddenByPaginationEvento],
        } as never;
      }
      return {
        total: 89,
        items: [currentPageEvento],
      } as never;
    });
  });

  afterEach(() => {
    document.getElementById("events-filters-slot")?.remove();
  });

  it(
    "loads filter options from the full visible event catalog instead of only the current page",
    async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/eventos"]}>
        <Routes>
          <Route path="/eventos" element={<EventsList />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Evento Atual")).toBeInTheDocument();

    await waitFor(() =>
      expect(mockedListEventos).toHaveBeenCalledWith(
        "token",
        expect.objectContaining({ skip: 0, limit: 200 }),
      ),
    );

    const slot = document.getElementById("events-filters-slot");
    expect(slot).not.toBeNull();

    const eventoInput = await within(slot as HTMLElement).findByLabelText("Evento");
    await user.click(eventoInput);
    await user.type(eventoInput, "Show");

    const option = await screen.findByRole("option", { name: "Show Rural Coopavel" });
    expect(option).toBeInTheDocument();

    await user.clear(eventoInput);
    await user.type(eventoInput, hiddenByPaginationEvento.nome);
    await user.click(within(slot as HTMLElement).getByRole("button", { name: "Aplicar" }));

    await waitFor(() =>
      expect(mockedListEventos).toHaveBeenCalledWith(
        "token",
        expect.objectContaining({ search: "Show Rural Coopavel" }),
      ),
    );
    await waitFor(() => expect(screen.queryByText("Evento Atual")).not.toBeInTheDocument());
    expect(screen.getByText("Show Rural Coopavel")).toBeInTheDocument();
    },
    15000,
  );
});
