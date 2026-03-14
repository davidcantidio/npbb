import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import AppLayout from "../AppLayout";
import AppThemeShell from "../../../theme/AppThemeShell";
import { ThemeModeProvider } from "../../../theme/ThemeModeProvider";
import { APP_THEME_MODE_STORAGE_KEY } from "../../../theme";
import { useAuth } from "../../../store/auth";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

function mockMatchMedia(matches: boolean) {
  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation(() => ({
      matches,
      media: "(prefers-color-scheme: dark)",
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  );
}

function renderAppLayout() {
  return render(
    <ThemeModeProvider>
      <MemoryRouter initialEntries={["/success"]}>
        <Routes>
          <Route element={<AppThemeShell />}>
            <Route element={<AppLayout />}>
              <Route path="/success" element={<div>Success content</div>} />
            </Route>
          </Route>
        </Routes>
      </MemoryRouter>
    </ThemeModeProvider>,
  );
}

describe("AppLayout theme toggle", () => {
  beforeEach(() => {
    window.localStorage.clear();
    mockMatchMedia(false);
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
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("expõe o toggle no menu do usuário e persiste a escolha", async () => {
    const user = userEvent.setup();

    renderAppLayout();

    await user.click(screen.getByRole("button", { name: /qa@npbb.com.br/i }));
    await user.click(screen.getByRole("menuitem", { name: /usar tema escuro/i }));

    expect(window.localStorage.getItem(APP_THEME_MODE_STORAGE_KEY)).toBe("dark");

    await user.click(screen.getByRole("button", { name: /qa@npbb.com.br/i }));
    expect(screen.getByRole("menuitem", { name: /usar tema claro/i })).toBeInTheDocument();
    expect(screen.getByText("Tema atual: escuro")).toBeInTheDocument();
  });
});
