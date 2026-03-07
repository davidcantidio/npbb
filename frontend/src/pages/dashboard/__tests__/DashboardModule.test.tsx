import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../../../components/ProtectedRoute";
import DashboardLayout from "../../../components/dashboard/DashboardLayout";
import AppLayout from "../../../components/layout/AppLayout";
import DashboardHome from "../DashboardHome";
import LeadsAgeAnalysisPlaceholder from "../LeadsAgeAnalysisPlaceholder";
import { useAuth } from "../../../store/auth";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

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
            <Route path="leads/analise-etaria" element={<LeadsAgeAnalysisPlaceholder />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("Dashboard module", () => {
  it("redirects to login when the user is not authenticated", async () => {
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

  it("renders the age analysis placeholder route", async () => {
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

    expect(await screen.findByText("Modulo reservado")).toBeInTheDocument();
    expect(screen.getByText(/camada de dados/i)).toBeInTheDocument();
  });

  it("redirects unknown dashboard routes back to the module home", async () => {
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
