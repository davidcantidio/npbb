import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EventoRow } from "../EventoRow";
import type { Agencia } from "../../../services/agencias";
import type { EventoListItem, EventoUpdate } from "../../../services/eventos";

type InlineUpdateFn = (id: number, patch: EventoUpdate) => Promise<unknown>;

const AGENCIAS: Agencia[] = [
  { id: 10, nome: "Agencia 10", dominio: "ag10.com.br" },
  { id: 20, nome: "Agencia 20", dominio: "ag20.com.br" },
];

const BASE_ITEM: EventoListItem = {
  id: 1,
  nome: "Evento QA",
  cidade: "Brasilia",
  estado: "DF",
  agencia_id: null,
  diretoria_id: null,
  status_id: 1,
  investimento: null,
  data_inicio_prevista: "2026-03-01",
  data_fim_prevista: "2026-03-02",
  data_inicio_realizada: null,
  data_fim_realizada: null,
  qr_code_url: null,
  data_health: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderRow({
  item,
  onInlineUpdate,
}: {
  item: EventoListItem;
  onInlineUpdate: InlineUpdateFn;
}) {
  return render(
    <MemoryRouter>
      <table>
        <tbody>
          <EventoRow item={item} agencias={AGENCIAS} onInlineUpdate={onInlineUpdate} />
        </tbody>
      </table>
    </MemoryRouter>,
  );
}

async function selectAgenciaByName(name: string) {
  const user = userEvent.setup();
  await user.click(screen.getByRole("combobox"));
  await user.click(await screen.findByRole("option", { name }));
}

describe("EventoRow agencia inline", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders current agencia on first render when event already has agencia", () => {
    const onInlineUpdate = vi.fn<InlineUpdateFn>().mockResolvedValue({});
    renderRow({ item: { ...BASE_ITEM, agencia_id: 10 }, onInlineUpdate });

    expect(screen.getByRole("combobox")).toHaveTextContent("Agencia 10");
    expect(screen.getByRole("combobox")).not.toHaveTextContent("Indefinida");
  });

  it("keeps select editable and updates agencia more than once", async () => {
    const onInlineUpdate = vi.fn<InlineUpdateFn>().mockResolvedValue({});
    renderRow({ item: { ...BASE_ITEM, agencia_id: null }, onInlineUpdate });

    await selectAgenciaByName("Agencia 10");
    await waitFor(() =>
      expect(onInlineUpdate).toHaveBeenNthCalledWith(1, BASE_ITEM.id, { agencia_id: 10 }),
    );

    await selectAgenciaByName("Agencia 20");
    await waitFor(() =>
      expect(onInlineUpdate).toHaveBeenNthCalledWith(2, BASE_ITEM.id, { agencia_id: 20 }),
    );

    expect(screen.getByRole("combobox")).toBeEnabled();
  });

  it("sends agencia_id null when selecting Indefinida", async () => {
    const onInlineUpdate = vi.fn<InlineUpdateFn>().mockResolvedValue({});
    renderRow({ item: { ...BASE_ITEM, agencia_id: 10 }, onInlineUpdate });

    await selectAgenciaByName("Indefinida");

    await waitFor(() =>
      expect(onInlineUpdate).toHaveBeenCalledWith(BASE_ITEM.id, { agencia_id: null }),
    );
  });

  it("rolls back UI value on update error", async () => {
    const onInlineUpdate = vi.fn<InlineUpdateFn>().mockRejectedValue(new Error("FORBIDDEN"));
    renderRow({ item: { ...BASE_ITEM, agencia_id: 10 }, onInlineUpdate });

    await selectAgenciaByName("Agencia 20");
    await waitFor(() => expect(onInlineUpdate).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole("combobox")).toHaveTextContent("Agencia 10"));
  });

  it("does not trigger update when selecting the same agencia", async () => {
    const onInlineUpdate = vi.fn<InlineUpdateFn>().mockResolvedValue({});
    renderRow({ item: { ...BASE_ITEM, agencia_id: 10 }, onInlineUpdate });

    await selectAgenciaByName("Agencia 10");

    expect(onInlineUpdate).not.toHaveBeenCalled();
  });
});
