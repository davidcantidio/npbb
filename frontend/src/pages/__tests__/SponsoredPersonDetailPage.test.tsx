import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import SponsoredPersonDetailPage from "../../features/patrocinados/SponsoredPersonDetailPage";
import { useAuth } from "../../store/auth";
import {
  getSponsoredPerson,
  listPersonGroups,
  listSocialProfiles,
} from "../../services/sponsorship";

vi.mock("../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../services/sponsorship", () => ({
  getSponsoredPerson: vi.fn(),
  listPersonGroups: vi.fn(),
  listSocialProfiles: vi.fn(),
  updateSponsoredPerson: vi.fn(),
  createSocialProfile: vi.fn(),
  deleteSocialProfile: vi.fn(),
  createPersonGroup: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedGetSponsoredPerson = vi.mocked(getSponsoredPerson);
const mockedListPersonGroups = vi.mocked(listPersonGroups);
const mockedListSocialProfiles = vi.mocked(listSocialProfiles);

describe("SponsoredPersonDetailPage", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_SPONSORSHIP_USE_API", "true");
    mockedUseAuth.mockReturnValue({
      user: null,
      token: "token-test",
      loading: false,
      refreshing: false,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
      refresh: vi.fn(),
    });
    mockedGetSponsoredPerson.mockResolvedValue({
      id: 7,
      full_name: "Atleta Teste",
      cpf: null,
      email: "atleta@example.com",
      phone: null,
      role: "atleta",
      notes: null,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: null,
      groups_count: 0,
      contracts_count: 0,
      social_profiles_count: 0,
    });
    mockedListSocialProfiles.mockResolvedValue([]);
    mockedListPersonGroups.mockResolvedValue([]);
  });

  it("orienta o fluxo owner-first para operar contratos e contrapartidas via grupo", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/patrocinados/pessoas/7"]}>
        <Routes>
          <Route path="/patrocinados/pessoas/:id" element={<SponsoredPersonDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", { name: "Atleta Teste" }),
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(mockedGetSponsoredPerson).toHaveBeenCalledWith("token-test", 7);
      expect(mockedListSocialProfiles).toHaveBeenCalledWith("token-test", "person", 7);
      expect(mockedListPersonGroups).toHaveBeenCalledWith("token-test", 7);
    });

    await user.click(screen.getByRole("tab", { name: /Grupos vinculados \(0\)/i }));

    expect(
      screen.getByText(/Contratos e contrapartidas sao operados dentro de grupos/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Criar grupo e abrir operacao/i }),
    ).toBeInTheDocument();
  });
});
