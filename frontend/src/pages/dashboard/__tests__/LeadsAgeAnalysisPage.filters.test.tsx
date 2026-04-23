import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { useReferenciaEventos } from "../../../features/leads/shared";
import { useAuth } from "../../../store/auth";
import type { AgeAnalysisFiltersQuery } from "../../../types/dashboard";
import { LeadsAgeAnalysisPage } from "../../../features/leads/dashboard";
import { buildAgeAnalysisFixture } from "./ageAnalysisFixtures";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../../hooks/useAgeAnalysis", () => ({
  useAgeAnalysis: vi.fn(),
}));

vi.mock("../../../features/leads/shared", () => ({
  useReferenciaEventos: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseAgeAnalysis = vi.mocked(useAgeAnalysis);
const mockedUseReferenciaEventos = vi.mocked(useReferenciaEventos);

function buildHookState(overrides: Partial<ReturnType<typeof useAgeAnalysis>> = {}) {
  return {
    data: buildAgeAnalysisFixture(),
    isLoading: false,
    isRefreshing: false,
    error: null,
    lastSuccessfulAt: null,
    refetch: vi.fn(),
    ...overrides,
  };
}

const EVENT_OPTIONS = [
  { id: 1, nome: "Evento Alpha", data_inicio_prevista: "2026-01-05" },
  { id: 2, nome: "Evento Beta", data_inicio_prevista: "2026-02-10" },
];

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

describe("LeadsAgeAnalysisPage filters", { timeout: 30000 }, () => {
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
      ...buildHookState(),
    }));
    mockedUseReferenciaEventos.mockReturnValue({
      eventOptions: EVENT_OPTIONS,
      isLoadingEvents: false,
      eventsError: null,
    });
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
