import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import PatrocinadosPage from "../../features/patrocinados/PatrocinadosPage";
import LegacySponsorshipGroupRedirect from "../../features/patrocinados/LegacySponsorshipGroupRedirect";
import { useAuth } from "../../store/auth";

vi.mock("../../store/auth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("Patrocinados pages", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.clearAllMocks();
  });

  it("bloqueia o modulo quando a API nao esta habilitada", () => {
    vi.stubEnv("VITE_SPONSORSHIP_USE_API", "false");
    mockedUseAuth.mockReturnValue({
      user: null,
      token: null,
      loading: false,
      refreshing: false,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
      refresh: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={["/patrocinados"]}>
        <Routes>
          <Route path="/patrocinados" element={<PatrocinadosPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: /patrocinados/i })).toBeInTheDocument();
    expect(screen.getByText(/VITE_SPONSORSHIP_USE_API=true/i)).toBeInTheDocument();
    expect(screen.queryByText(/novo patrocinador/i)).not.toBeInTheDocument();
  });

  it("redireciona a rota legada para a rota explicita de grupo", () => {
    render(
      <MemoryRouter initialEntries={["/patrocinados/42"]}>
        <Routes>
          <Route path="/patrocinados/:id" element={<LegacySponsorshipGroupRedirect />} />
          <Route path="/patrocinados/grupos/:id" element={<div>Grupo explicito</div>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Grupo explicito")).toBeInTheDocument();
  });

  it("falha explicitamente para ids string do legado local", () => {
    render(
      <MemoryRouter initialEntries={["/patrocinados/550e8400-e29b-41d4-a716-446655440000"]}>
        <Routes>
          <Route path="/patrocinados/:id" element={<LegacySponsorshipGroupRedirect />} />
          <Route path="/patrocinados/grupos/:id" element={<div>Grupo explicito</div>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.queryByText("Grupo explicito")).not.toBeInTheDocument();
    expect(
      screen.getByText(/Compatibilidade limitada: a rota legada \/patrocinados\/:id agora so aceita IDs numericos de grupo/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /voltar para patrocinados/i }),
    ).toHaveAttribute("href", "/patrocinados");
  });
});
