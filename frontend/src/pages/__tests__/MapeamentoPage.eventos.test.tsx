import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import MapeamentoPage from "../leads/MapeamentoPage";
import { useAuth } from "../../store/auth";
import { getLeadBatchColunas, listReferenciaEventos, mapearLeadBatch } from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  getLeadBatchColunas: vi.fn(),
  listReferenciaEventos: vi.fn(),
  mapearLeadBatch: vi.fn(),
}));

const EVENTOS_LOAD_ERROR = "Não foi possível carregar os eventos. Tente recarregar a página.";

const mockedUseAuth = vi.mocked(useAuth);
const mockedGetLeadBatchColunas = vi.mocked(getLeadBatchColunas);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);
const mockedMapearLeadBatch = vi.mocked(mapearLeadBatch);

function renderMapeamentoPage() {
  return render(
    <MemoryRouter initialEntries={["/leads/mapeamento?batch_id=10"]}>
      <Routes>
        <Route path="/leads/mapeamento" element={<MapeamentoPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("MapeamentoPage reference events", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      token: "token-123",
      user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });
    mockedGetLeadBatchColunas.mockResolvedValue({
      batch_id: 10,
      colunas: [
        {
          coluna_original: "nome",
          campo_sugerido: "nome",
          confianca: "exact_match",
        },
      ],
    });
    mockedMapearLeadBatch.mockResolvedValue({
      batch_id: 10,
      silver_count: 1,
      stage: "silver",
    });
  });

  it("shows and dismisses an error alert when reference events fail to load", async () => {
    mockedListReferenciaEventos.mockRejectedValue(new Error("network error"));

    renderMapeamentoPage();

    expect(await screen.findByText(EVENTOS_LOAD_ERROR)).toBeInTheDocument();
    expect(mockedListReferenciaEventos).toHaveBeenCalledWith("token-123");

    const alert = screen.getByText(EVENTOS_LOAD_ERROR).closest('[role="alert"]');
    expect(alert).not.toBeNull();

    await userEvent.setup().click(within(alert as HTMLElement).getByRole("button"));

    await waitFor(() => {
      expect(screen.queryByText(EVENTOS_LOAD_ERROR)).not.toBeInTheDocument();
    });
  });
});
