import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { listReferenciaEventos } from "../../../services/leads_import";
import { useAuth } from "../../../store/auth";
import type { AgeAnalysisFiltersQuery, AgeAnalysisResponse } from "../../../types/dashboard";
import LeadsAgeAnalysisPage from "../LeadsAgeAnalysisPage";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../../hooks/useAgeAnalysis", () => ({
  useAgeAnalysis: vi.fn(),
}));

vi.mock("../../../services/leads_import", () => ({
  listReferenciaEventos: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseAgeAnalysis = vi.mocked(useAgeAnalysis);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);

const EVENT_OPTIONS = [
  { id: 1, nome: "Evento Alpha", data_inicio_prevista: "2026-01-05" },
  { id: 2, nome: "Evento Beta", data_inicio_prevista: "2026-02-10" },
];

function buildFixture(overrides?: Partial<AgeAnalysisResponse>): AgeAnalysisResponse {
  return {
    version: 1,
    generated_at: "2026-03-07T12:00:00Z",
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
      },
    ],
    consolidado: {
      base_total: 10,
      clientes_bb_volume: 4,
      clientes_bb_pct: 40,
      cobertura_bb_pct: 90,
      faixas: {
        faixa_18_25: { volume: 5, pct: 50 },
        faixa_26_40: { volume: 3, pct: 30 },
        fora_18_40: { volume: 2, pct: 20 },
        sem_info_volume: 0,
        sem_info_pct_da_base: 0,
      },
      top_eventos: [
        {
          evento_id: 1,
          evento_nome: "Evento Alpha",
          base_leads: 10,
          faixa_dominante: "faixa_18_25",
        },
      ],
      media_por_evento: 10,
      mediana_por_evento: 10,
      concentracao_top3_pct: 100,
    },
    ...overrides,
  };
}

function SearchParamsObserver() {
  const location = useLocation();

  return <output data-testid="location-search">{location.search}</output>;
}

function renderPage(initialEntry = "/dashboard/leads/analise-etaria") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route
          path="/dashboard/leads/analise-etaria"
          element={
            <>
              <LeadsAgeAnalysisPage />
              <SearchParamsObserver />
            </>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

function expectLastHookFilters(filters: AgeAnalysisFiltersQuery) {
  expect(mockedUseAgeAnalysis).toHaveBeenLastCalledWith(filters);
}

describe("LeadsAgeAnalysisPage filters", () => {
  beforeEach(() => {
    mockedUseAuth.mockReturnValue({
      token: "token",
      user: { id: 1, email: "qa@npbb.com.br", tipo_usuario: "admin" },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });
    mockedUseAgeAnalysis.mockImplementation(() => ({
      data: buildFixture(),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    }));
    mockedListReferenciaEventos.mockResolvedValue(EVENT_OPTIONS);
  });

  it("hydrates filters from the URL and forwards them to the hook", async () => {
    renderPage("/dashboard/leads/analise-etaria?evento_id=1&data_inicio=2026-01-10&data_fim=2026-01-31");

    expect(await screen.findByDisplayValue("Evento Alpha • 2026-01-05")).toBeInTheDocument();
    expect(screen.getByLabelText("Data inicio")).toHaveValue("2026-01-10");
    expect(screen.getByLabelText("Data fim")).toHaveValue("2026-01-31");
    expect(screen.getByTestId("location-search")).toHaveTextContent(
      "?evento_id=1&data_inicio=2026-01-10&data_fim=2026-01-31",
    );
    expectLastHookFilters({
      evento_id: 1,
      data_inicio: "2026-01-10",
      data_fim: "2026-01-31",
    });
  });

  it("auto-applies event and date changes to the URL and hook filters", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole("combobox", { name: "Evento" }));
    await user.click(await screen.findByText("Evento Beta • 2026-02-10"));

    await waitFor(() => {
      expect(screen.getByTestId("location-search")).toHaveTextContent("?evento_id=2");
      expectLastHookFilters({ evento_id: 2 });
    });

    fireEvent.change(screen.getByLabelText("Data inicio"), {
      target: { value: "2026-01-10" },
    });

    await waitFor(() => {
      expect(screen.getByTestId("location-search")).toHaveTextContent("?evento_id=2&data_inicio=2026-01-10");
      expectLastHookFilters({
        evento_id: 2,
        data_inicio: "2026-01-10",
      });
    });

    fireEvent.change(screen.getByLabelText("Data fim"), {
      target: { value: "2026-01-31" },
    });

    await waitFor(() => {
      expect(screen.getByTestId("location-search")).toHaveTextContent(
        "?evento_id=2&data_inicio=2026-01-10&data_fim=2026-01-31",
      );
      expectLastHookFilters({
        evento_id: 2,
        data_inicio: "2026-01-10",
        data_fim: "2026-01-31",
      });
    });
  });

  it("keeps the last valid applied filters when the draft range becomes invalid", async () => {
    renderPage("/dashboard/leads/analise-etaria?data_inicio=2026-01-10&data_fim=2026-01-20");

    fireEvent.change(screen.getByLabelText("Data fim"), {
      target: { value: "2026-01-05" },
    });

    expect(screen.getByLabelText("Data fim")).toHaveValue("2026-01-05");
    expect(await screen.findByText("A data fim deve ser maior ou igual a data inicio.")).toBeInTheDocument();
    expect(screen.getByTestId("location-search")).toHaveTextContent(
      "?data_inicio=2026-01-10&data_fim=2026-01-20",
    );
    expectLastHookFilters({
      data_inicio: "2026-01-10",
      data_fim: "2026-01-20",
    });
  });

  it("clears event and period filters back to the default state", async () => {
    const user = userEvent.setup();
    renderPage("/dashboard/leads/analise-etaria?evento_id=2&data_inicio=2026-01-10&data_fim=2026-01-31");

    expect(await screen.findByDisplayValue("Evento Beta • 2026-02-10")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Limpar filtros" }));

    await waitFor(() => {
      expect(screen.getByTestId("location-search")).toHaveTextContent(/^$/);
      expectLastHookFilters({});
    });

    expect(screen.getByLabelText("Data inicio")).toHaveValue("");
    expect(screen.getByLabelText("Data fim")).toHaveValue("");
    expect(screen.getByDisplayValue("Todos os eventos")).toBeInTheDocument();
  });
});
