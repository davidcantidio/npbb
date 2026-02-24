import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../ProtectedRoute";
import { useAuth } from "../../store/auth";

vi.mock("../../store/auth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("ProtectedRoute", () => {
  it("redirects to login when token is missing", async () => {
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

    render(
      <MemoryRouter initialEntries={["/eventos"]}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route
            path="/eventos"
            element={
              <ProtectedRoute>
                <div>Private content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Login page")).toBeInTheDocument();
  });

  it("requests refresh when token exists but user is absent", async () => {
    const refresh = vi.fn().mockResolvedValue(null);
    mockedUseAuth.mockReturnValue({
      token: "token",
      user: null,
      loading: false,
      refreshing: false,
      error: null,
      refresh,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={["/eventos"]}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route
            path="/eventos"
            element={
              <ProtectedRoute>
                <div>Private content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(refresh).toHaveBeenCalledTimes(1);
    });
  });

  it("renders children when session is valid", () => {
    mockedUseAuth.mockReturnValue({
      token: "token",
      user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin" },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={["/eventos"]}>
        <Routes>
          <Route
            path="/eventos"
            element={
              <ProtectedRoute>
                <div>Private content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Private content")).toBeInTheDocument();
  });
});
