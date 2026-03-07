import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../../../components/ProtectedRoute";
import DashboardLayout from "../../../components/dashboard/DashboardLayout";
import AppLayout from "../../../components/layout/AppLayout";
import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { listReferenciaEventos } from "../../../services/leads_import";
import type { AgeAnalysisResponse } from "../../../types/dashboard";
import DashboardHome from "../DashboardHome";
import LeadsAgeAnalysisPage from "../LeadsAgeAnalysisPage";
import { useAuth } from "../../../store/auth";

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

const ageAnalysisFixture: AgeAnalysisResponse = {
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
      base_leads: 4,
      clientes_bb_volume: 2,
      clientes_bb_pct: 50,
      cobertura_bb_pct: 100,
      faixa_dominante: "faixa_18_25",
      faixas: {
        faixa_18_25: { volume: 2, pct: 50 },
        faixa_26_40: { volume: 1, pct: 25 },
        fora_18_40: { volume: 1, pct: 25 },
        sem_info_volume: 0,
        sem_info_pct_da_base: 0,
      },
    },
  ],
  consolidado: {
    base_total: 4,
    clientes_bb_volume: 2,
    clientes_bb_pct: 50,
    cobertura_bb_pct: 100,
    faixas: {
      faixa_18_25: { volume: 2, pct: 50 },
      faixa_26_40: { volume: 1, pct: 25 },
      fora_18_40: { volume: 1, pct: 25 },
      sem_info_volume: 0,
      sem_info_pct_da_base: 0,
    },
    top_eventos: [
      {
        evento_id: 1,
        evento_nome: "Evento Alpha",
        base_leads: 4,
        faixa_dominante: "faixa_18_25",
      },
    ],
    media_por_evento: 4,
    mediana_por_evento: 4,
    concentracao_top3_pct: 100,
  },
};

function renderDashboardModule(initialEntry: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="leads" element={<Navigate to="analise-etaria" replace />} />
            <Route path="leads/analise-etaria" element={<LeadsAgeAnalysisPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("Dashboard module", () => {
  it("renders dashboard home with manifesto-driven cards and sidebar", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    mockedListReferenciaEventos.mockResolvedValue([]);
    mockedUseAuth.mockReturnValue({
      token: null,
      user: null,
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderDashboardModule("/dashboard");

    expect(await screen.findByText("Login page")).toBeInTheDocument();
  });

  it("redirects to login when the user is not authenticated", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: ageAnalysisFixture,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    mockedListReferenciaEventos.mockResolvedValue([
      { id: 1, nome: "Evento Alpha", data_inicio_prevista: "2026-01-05" },
    ]);
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

    renderDashboardModule("/dashboard");

    expect(
      await screen.findByText("Selecione uma trilha analitica para navegar pelos dashboards disponiveis."),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Analise etaria por evento").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Em breve").length).toBeGreaterThan(0);
  });

  it("renders the age analysis route with dashboard data", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: ageAnalysisFixture,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    mockedListReferenciaEventos.mockResolvedValue([
      { id: 1, nome: "Evento Alpha", data_inicio_prevista: "2026-01-05" },
    ]);
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

    renderDashboardModule("/dashboard/leads/analise-etaria");

    expect(await screen.findByText("Base total")).toBeInTheDocument();
    expect(screen.getByText("Distribuicao etaria por evento")).toBeInTheDocument();
    expect(screen.getAllByText("Evento Alpha").length).toBeGreaterThan(0);
  });

  it("redirects unknown dashboard routes back to the module home", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: ageAnalysisFixture,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    mockedListReferenciaEventos.mockResolvedValue([]);
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

    renderDashboardModule("/dashboard/rota-inexistente");

    expect(
      await screen.findByText("Selecione uma trilha analitica para navegar pelos dashboards disponiveis."),
    ).toBeInTheDocument();
  });
});
