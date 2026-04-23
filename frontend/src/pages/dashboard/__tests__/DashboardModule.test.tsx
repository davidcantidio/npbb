import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../../../components/ProtectedRoute";
import DashboardLayout from "../../../components/dashboard/DashboardLayout";
import AppLayout from "../../../components/layout/AppLayout";
import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { useReferenciaEventos } from "../../../features/leads/shared";
import DashboardHome from "../DashboardHome";
import { LeadsAgeAnalysisPage } from "../../../features/leads/dashboard";
import { useAuth } from "../../../store/auth";
import { useThemeMode } from "../../../theme/ThemeModeProvider";
import { buildAgeAnalysisFixture } from "./ageAnalysisFixtures";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../../theme/ThemeModeProvider", () => ({
  useThemeMode: vi.fn(),
}));

vi.mock("../../../hooks/useAgeAnalysis", () => ({
  useAgeAnalysis: vi.fn(),
}));

vi.mock("../../../features/leads/shared", () => ({
  useReferenciaEventos: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseThemeMode = vi.mocked(useThemeMode);
const mockedUseAgeAnalysis = vi.mocked(useAgeAnalysis);
const mockedUseReferenciaEventos = vi.mocked(useReferenciaEventos);

const ageAnalysisFixture = buildAgeAnalysisFixture({
  por_evento: [
    {
      evento_id: 1,
      evento_nome: "Evento Alpha",
      cidade: "Sao Paulo",
      estado: "SP",
      base_leads: 4,
      base_com_idade_volume: 4,
      base_bb_coberta_volume: 4,
      leads_proponente: 1,
      leads_ativacao: 3,
      leads_canal_desconhecido: 0,
      clientes_bb_volume: 2,
      clientes_bb_pct: 50,
      nao_clientes_bb_volume: 2,
      nao_clientes_bb_pct: 50,
      bb_indefinido_volume: 0,
      cobertura_bb_pct: 100,
      faixa_dominante: "faixa_18_25",
      faixa_dominante_status: "resolved",
      faixas: {
        faixa_18_25: { volume: 2, pct: 50 },
        faixa_26_40: { volume: 1, pct: 25 },
        faixa_18_40: { volume: 3, pct: 75 },
        fora_18_40: { volume: 1, pct: 25 },
        sem_info_volume: 0,
        sem_info_pct_da_base: 0,
      },
    },
  ],
  consolidado: {
    base_total: 4,
    base_com_idade_volume: 4,
    base_bb_coberta_volume: 4,
    leads_proponente: 1,
    leads_ativacao: 3,
    leads_canal_desconhecido: 0,
    clientes_bb_volume: 2,
    clientes_bb_pct: 50,
    nao_clientes_bb_volume: 2,
    nao_clientes_bb_pct: 50,
    bb_indefinido_volume: 0,
    cobertura_bb_pct: 100,
    faixas: {
      faixa_18_25: { volume: 2, pct: 50 },
      faixa_26_40: { volume: 1, pct: 25 },
      faixa_18_40: { volume: 3, pct: 75 },
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
    faixa_dominante_status: "resolved",
    clientes_bb_base_idade_volume: 2,
    clientes_bb_faixa_18_40_volume: 2,
    clientes_bb_faixa_18_40_pct: 100,
    clientes_bb_fora_18_40_volume: 0,
    clientes_bb_fora_18_40_pct: 0,
    nao_clientes_bb_base_idade_volume: 2,
    nao_clientes_bb_faixa_18_40_volume: 1,
    nao_clientes_bb_faixa_18_40_pct: 50,
    nao_clientes_bb_fora_18_40_volume: 1,
    nao_clientes_bb_fora_18_40_pct: 50,
  },
  qualidade_consolidado: {
    base_vinculos: 4,
    sem_cpf_volume: 0,
    sem_cpf_pct: 0,
    sem_data_nascimento_volume: 0,
    sem_data_nascimento_pct: 0,
    sem_nome_completo_volume: 0,
    sem_nome_completo_pct: 0,
  },
});

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

describe("Dashboard module", { timeout: 30000 }, () => {
  beforeEach(() => {
    mockedUseThemeMode.mockReturnValue({
      mode: "light",
      resolvedMode: "light",
      setMode: vi.fn(),
      toggleMode: vi.fn(),
    });
  });

  it("redirects to login when the user is not authenticated", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: null,
      isLoading: false,
      isRefreshing: false,
      error: null,
      lastSuccessfulAt: null,
      refetch: vi.fn(),
    });
    mockedUseReferenciaEventos.mockReturnValue({
      eventOptions: [],
      isLoadingEvents: false,
      eventsError: null,
    });
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

  it("renders dashboard home with manifesto-driven cards and sidebar", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: ageAnalysisFixture,
      isLoading: false,
      isRefreshing: false,
      error: null,
      lastSuccessfulAt: null,
      refetch: vi.fn(),
    });
    mockedUseReferenciaEventos.mockReturnValue({
      eventOptions: [{ id: 1, nome: "Evento Alpha", data_inicio_prevista: "2026-01-05" }],
      isLoadingEvents: false,
      eventsError: null,
    });
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
      isRefreshing: false,
      error: null,
      lastSuccessfulAt: null,
      refetch: vi.fn(),
    });
    mockedUseReferenciaEventos.mockReturnValue({
      eventOptions: [{ id: 1, nome: "Evento Alpha", data_inicio_prevista: "2026-01-05" }],
      isLoadingEvents: false,
      eventsError: null,
    });
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

    expect(await screen.findByText("Leads válidos")).toBeInTheDocument();
    expect(screen.getByText("Confianca e cobertura")).toBeInTheDocument();
    expect(screen.getByText("Distribuicao etaria por evento")).toBeInTheDocument();
    expect(screen.getAllByText("Evento Alpha").length).toBeGreaterThan(0);
  });

  it("redirects unknown dashboard routes back to the module home", async () => {
    mockedUseAgeAnalysis.mockReturnValue({
      data: ageAnalysisFixture,
      isLoading: false,
      isRefreshing: false,
      error: null,
      lastSuccessfulAt: null,
      refetch: vi.fn(),
    });
    mockedUseReferenciaEventos.mockReturnValue({
      eventOptions: [],
      isLoadingEvents: false,
      eventsError: null,
    });
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
