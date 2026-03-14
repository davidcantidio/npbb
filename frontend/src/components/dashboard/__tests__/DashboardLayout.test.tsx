import type { ReactElement } from "react";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import DashboardLayout from "../DashboardLayout";
import AppLayout from "../../layout/AppLayout";
import { useAuth } from "../../../store/auth";
import { useThemeMode } from "../../../theme/ThemeModeProvider";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../../theme/ThemeModeProvider", () => ({
  useThemeMode: vi.fn(),
}));

const theme = createTheme();
const mockedUseAuth = vi.mocked(useAuth);
const mockedUseThemeMode = vi.mocked(useThemeMode);

function renderWithTheme(ui: ReactElement) {
  return render(
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {ui}
    </ThemeProvider>,
  );
}

function renderDashboardRoute({
  initialEntry = "/dashboard",
  withSlot = false,
}: {
  initialEntry?: string;
  withSlot?: boolean;
} = {}) {
  return renderWithTheme(
    <>
      {withSlot ? <div id="app-sidebar-slot" data-testid="app-sidebar-slot" /> : null}
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<div>Dashboard outlet</div>} />
            <Route path="leads/analise-etaria" element={<div>Age page content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </>,
  );
}

function renderDashboardWithinAppLayout(initialEntry = "/dashboard") {
  return renderWithTheme(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<div>Dashboard outlet</div>} />
          </Route>
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

function mockMatchMedia(matches: boolean) {
  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation(() => ({
      matches,
      media: "",
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  );
}

describe("DashboardLayout", () => {
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
    mockedUseThemeMode.mockReturnValue({
      mode: "light",
      resolvedMode: "light",
      setMode: vi.fn(),
      toggleMode: vi.fn(),
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the sidebar inside the shared app sidebar slot and preserves outlet content", async () => {
    renderDashboardRoute({ withSlot: true });

    const sidebarSlot = await screen.findByTestId("app-sidebar-slot");

    expect(
      within(sidebarSlot).getByRole("navigation", { name: /navegacao do dashboard/i }),
    ).toBeInTheDocument();
    expect(within(sidebarSlot).getByText("Painel de analises")).toBeInTheDocument();
    expect(screen.getByText("Dashboard outlet")).toBeInTheDocument();
    expect(screen.getAllByText("Painel de analises")).toHaveLength(1);
  });

  it("renders an inline fallback when the shared sidebar slot is unavailable", async () => {
    renderDashboardRoute();

    expect(await screen.findByRole("complementary", { name: /sidebar do dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: /navegacao do dashboard/i })).toBeInTheDocument();
    expect(screen.getByText("Dashboard outlet")).toBeInTheDocument();
  });

  it("highlights the active manifesto route and keeps backlog items disabled with tooltip", async () => {
    const user = userEvent.setup();

    renderDashboardRoute({
      initialEntry: "/dashboard/leads/analise-etaria",
      withSlot: true,
    });

    const sidebarSlot = await screen.findByTestId("app-sidebar-slot");
    const activeLink = within(sidebarSlot).getByRole("link", {
      name: /analise etaria por evento/i,
    });

    expect(activeLink).toHaveAttribute("href", "/dashboard/leads/analise-etaria");
    expect(activeLink).toHaveAttribute("aria-current", "page");
    expect(
      within(sidebarSlot).queryByRole("link", { name: /relatorio de fechamento/i }),
    ).not.toBeInTheDocument();

    await user.hover(
      within(sidebarSlot).getByTestId("dashboard-sidebar-disabled-events-closure-report"),
    );

    expect(await screen.findByRole("tooltip")).toHaveTextContent("Em breve");
  });

  it("reuses the AppLayout drawer slot on mobile without rendering a second sidebar", async () => {
    mockMatchMedia(false);

    renderDashboardWithinAppLayout();

    const sidebarSlot = document.getElementById("app-sidebar-slot");

    expect(sidebarSlot).not.toBeNull();
    expect(screen.getByRole("button", { name: /abrir filtros/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(within(sidebarSlot as HTMLElement).getByText("Painel de analises")).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getAllByText("Painel de analises")).toHaveLength(1);
    });
    expect(screen.getByText("Dashboard outlet")).toBeInTheDocument();
  });
});
