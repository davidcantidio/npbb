import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { listReferenciaEventos } from "../../../services/leads_import";
import { useAuth } from "../../../store/auth";
import type { AgeAnalysisResponse } from "../../../types/dashboard";
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

function renderPage(initialEntry = "/dashboard/leads/analise-etaria") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/dashboard/leads/analise-etaria" element={<LeadsAgeAnalysisPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("LeadsAgeAnalysisPage states", () => {
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
    mockedListReferenciaEventos.mockResolvedValue([{ id: 1, nome: "Evento Alpha", data_inicio_prevista: null }]);
  });

  it("renders skeleton loaders while loading", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: vi.fn(),
    });

    renderPage();

    expect(await screen.findAllByTestId("kpi-card-skeleton")).toHaveLength(4);
    expect(screen.getByTestId("chart-skeleton")).toBeInTheDocument();
    expect(screen.getByTestId("table-skeleton")).toBeInTheDocument();
  });

  it("renders centered empty state", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: buildFixture({
        por_evento: [],
        consolidado: {
          ...buildFixture().consolidado,
          base_total: 0,
          top_eventos: [],
        },
      }),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderPage();

    expect(await screen.findByText("Nenhum lead encontrado para os filtros aplicados")).toBeInTheDocument();
  });

  it("renders the four KPI cards with required consolidated metrics", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: buildFixture(),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderPage();

    const baseCard = (await screen.findByText("Base Total")).closest(".MuiCard-root");
    if (!baseCard) {
      throw new Error("Base Total card not found");
    }
    expect(within(baseCard).getByText("10")).toBeInTheDocument();

    const clientesCard = screen.getByText("Percentual da base: 40,0%").closest(".MuiCard-root");
    if (!clientesCard) {
      throw new Error("Clientes BB card not found");
    }
    expect(within(clientesCard).getByText("Clientes BB")).toBeInTheDocument();
    expect(within(clientesCard).getByText("4")).toBeInTheDocument();
    expect(within(clientesCard).getByText("Percentual da base: 40,0%")).toBeInTheDocument();
    expect(within(clientesCard).getByText("Cobertura BB")).toBeInTheDocument();
    expect(within(clientesCard).getByText("90.0%")).toBeInTheDocument();

    const faixaCard = screen.getByText("Faixa Dominante").closest(".MuiCard-root");
    if (!faixaCard) {
      throw new Error("Faixa Dominante card not found");
    }
    expect(within(faixaCard).getByText("18–25")).toBeInTheDocument();

    const eventosCard = screen.getByText("Eventos").closest(".MuiCard-root");
    if (!eventosCard) {
      throw new Error("Eventos card not found");
    }
    expect(within(eventosCard).getByText("1")).toBeInTheDocument();
  });

  it("shows error toast with retry action", async () => {
    const refetch = vi.fn();
    const user = userEvent.setup();
    mockedUseAgeAnalysis.mockReturnValue({
      data: null,
      isLoading: false,
      error: "Nao foi possivel carregar a analise etaria.",
      refetch,
    });

    renderPage();

    expect(await screen.findByText("Nao foi possivel carregar a analise etaria.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /tentar novamente/i }));
    expect(refetch).toHaveBeenCalledTimes(1);
  });

  it("shows and restores warning coverage banner after filters change", async () => {
    const user = userEvent.setup();
    const fixture = buildFixture({
      por_evento: [
        {
          ...buildFixture().por_evento[0],
          clientes_bb_volume: null,
          clientes_bb_pct: null,
          cobertura_bb_pct: 65,
        },
      ],
      consolidado: {
        ...buildFixture().consolidado,
        clientes_bb_volume: null,
        clientes_bb_pct: null,
        cobertura_bb_pct: 65,
      },
    });

    mockedUseAgeAnalysis.mockReturnValue({
      data: fixture,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderPage();

    expect(await screen.findByTestId("coverage-banner-warning-default")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /close/i }));
    expect(screen.queryByTestId("coverage-banner-warning-default")).not.toBeInTheDocument();

    const table = screen.getByRole("table");
    await user.click(within(table).getByText("Evento Alpha"));

    expect(await screen.findByTestId("coverage-banner-warning-default")).toBeInTheDocument();
  });

  it("renders danger coverage state and partial-data hints", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: buildFixture({
        por_evento: [
          {
            ...buildFixture().por_evento[0],
            clientes_bb_volume: null,
            clientes_bb_pct: null,
            cobertura_bb_pct: 12,
          },
        ],
        consolidado: {
          ...buildFixture().consolidado,
          clientes_bb_volume: null,
          clientes_bb_pct: null,
          cobertura_bb_pct: 12,
        },
      }),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderPage();

    expect(await screen.findByTestId("coverage-banner-danger-default")).toBeInTheDocument();
    expect(await screen.findByTestId("coverage-banner-danger-compact")).toBeInTheDocument();
    expect(screen.getAllByText("(dados parciais)").length).toBeGreaterThan(0);
  });
});
