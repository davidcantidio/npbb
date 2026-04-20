import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import LeadsListPage from "../leads/LeadsListPage";
import { useAuth } from "../../store/auth";
import { listLeads, type LeadListItem } from "../../services/leads_import";
import { triggerBlobDownload } from "../../services/leads_export";
import { exportLeadsListCsv } from "../../services/leads_list_export";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  listLeads: vi.fn(),
  LEADS_EXPORT_TIMEOUT_MS: 15 * 60_000,
}));
vi.mock("../../services/leads_export", () => ({
  triggerBlobDownload: vi.fn(),
}));
vi.mock("../../services/leads_list_export", () => ({
  exportLeadsListCsv: vi.fn(),
}));
vi.mock("../dashboard/useReferenciaEventos", () => ({
  useReferenciaEventos: () => ({
    eventOptions: [],
    isLoadingEvents: false,
    eventsError: null,
  }),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListLeads = vi.mocked(listLeads);
const mockedTriggerBlobDownload = vi.mocked(triggerBlobDownload);
const mockedExportLeadsListCsv = vi.mocked(exportLeadsListCsv);

function makeLead(id: number): LeadListItem {
  return {
    id,
    nome: `User ${id}`,
    sobrenome: null,
    email: `user${id}@example.com`,
    cpf: null,
    telefone: null,
    evento_nome: "Show X",
    cidade: "Sao Paulo",
    estado: "SP",
    data_compra: null,
    data_criacao: "2026-01-15T12:00:00.000Z",
    evento_convertido_id: 2,
    evento_convertido_nome: "Show X",
    tipo_conversao: null,
    data_conversao: null,
    rg: null,
    genero: null,
    is_cliente_bb: false,
    is_cliente_estilo: null,
    data_nascimento: "2000-06-20",
    data_evento: "2025-02-04 00:00:00",
    soma_de_ano_evento: 2025,
    tipo_evento: "Esporte/Volei de Praia",
    local_evento: "Navegantes-SC",
    faixa_etaria: "18-40",
    soma_de_idade: 25,
    logradouro: null,
    numero: null,
    complemento: null,
    bairro: null,
    cep: null,
  };
}

const defaultListResponse = {
  page: 1,
  page_size: 20,
  total: 1,
  items: [makeLead(1)],
};

function LocationProbe() {
  const { pathname } = useLocation();
  return <span data-testid="location">{pathname}</span>;
}

describe("LeadsListPage", () => {
  vi.setConfig({ testTimeout: 15_000 });

  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      token: "token-123",
      user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
      refresh: vi.fn(),
    });
    mockedListLeads.mockResolvedValue(defaultListResponse);
    mockedExportLeadsListCsv.mockResolvedValue({
      blob: new Blob(["nome,cpf"]),
      filename: "leads-2026-01-15.csv",
    } as never);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("lista leads e navega para importacao", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/leads"]}>
        <Routes>
          <Route path="/leads" element={<LeadsListPage />} />
          <Route
            path="/leads/importar"
            element={
              <>
                <LocationProbe />
                <span>Importacao</span>
              </>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(mockedListLeads).toHaveBeenCalled();
    });

    expect(await screen.findByRole("cell", { name: "User 1" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "user1@example.com" })).toBeInTheDocument();
    expect(screen.getByText("Sao Paulo / SP")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /importar leads/i }));
    expect(await screen.findByTestId("location")).toHaveTextContent("/leads/importar");
  });

  it("exportar CSV usa o backend dedicado e dispara download", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/leads"]}>
        <Routes>
          <Route path="/leads" element={<LeadsListPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(mockedListLeads).toHaveBeenCalled();
    });

    await user.click(screen.getByRole("button", { name: /exportar csv/i }));

    await waitFor(() => {
      expect(mockedExportLeadsListCsv).toHaveBeenCalledTimes(1);
      expect(mockedTriggerBlobDownload).toHaveBeenCalledTimes(1);
    });

    expect(mockedExportLeadsListCsv).toHaveBeenCalledWith("token-123", {
      data_inicio: "",
      data_fim: "",
      evento_id: null,
    });
    const [blob, filename] = mockedTriggerBlobDownload.mock.calls[0];
    expect(blob).toBeInstanceOf(Blob);
    expect(filename).toBe("leads-2026-01-15.csv");
  });

  it("exportar CSV repete os filtros aplicados na consulta do backend", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/leads"]}>
        <Routes>
          <Route path="/leads" element={<LeadsListPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(mockedListLeads).toHaveBeenCalled();
    });

    fireEvent.change(screen.getByLabelText(/data inicio/i), { target: { value: "2026-02-01" } });
    fireEvent.change(screen.getByLabelText(/data fim/i), { target: { value: "2026-02-28" } });
    await user.click(screen.getByRole("button", { name: /aplicar filtros/i }));

    await waitFor(() => {
      const withFilters = mockedListLeads.mock.calls.some(
        ([, p]) => p?.data_inicio === "2026-02-01" && p?.data_fim === "2026-02-28",
      );
      expect(withFilters).toBe(true);
    });

    mockedExportLeadsListCsv.mockResolvedValueOnce({
      blob: new Blob(["csv"]),
      filename: "leads-2026-01-15.csv",
    } as never);

    await user.click(screen.getByRole("button", { name: /exportar csv/i }));

    await waitFor(() => {
      expect(mockedExportLeadsListCsv).toHaveBeenCalledWith("token-123", {
        data_inicio: "2026-02-01",
        data_fim: "2026-02-28",
        evento_id: null,
      });
      expect(mockedTriggerBlobDownload).toHaveBeenCalledTimes(1);
    });
  });
});
