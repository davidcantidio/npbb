import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";

import { DASHBOARD_MANIFEST } from "../../../config/dashboardManifest";
import DashboardHome, { DASHBOARD_HOME_GRID_COLUMNS } from "../DashboardHome";

function renderDashboardHome() {
  return render(
    <MemoryRouter>
      <DashboardHome />
    </MemoryRouter>,
  );
}

describe("DashboardHome", () => {
  it("renders the dashboard title, description, and one card per manifesto entry", () => {
    renderDashboardHome();

    expect(screen.getByRole("heading", { name: /painel de analises/i })).toBeInTheDocument();
    expect(
      screen.getByText("Selecione uma trilha analitica para navegar pelos dashboards disponiveis."),
    ).toBeInTheDocument();

    const grid = screen.getByTestId("dashboard-home-card-grid");
    const cards = within(grid).getAllByTestId(/^dashboard-card-root-/);

    expect(cards).toHaveLength(DASHBOARD_MANIFEST.length);

    for (const entry of DASHBOARD_MANIFEST) {
      expect(within(grid).getByTestId(`dashboard-card-root-${entry.id}`)).toBeInTheDocument();
    }
  });

  it("keeps the responsive grid contract as 1/2/3 columns across breakpoints", () => {
    expect(DASHBOARD_HOME_GRID_COLUMNS).toEqual({
      xs: "1fr",
      sm: "repeat(2, minmax(0, 1fr))",
      lg: "repeat(3, minmax(0, 1fr))",
    });
  });
});
