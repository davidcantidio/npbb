import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";

import { DASHBOARD_MANIFEST } from "../../../config/dashboardManifest";
import { DashboardCard } from "../DashboardCard";

function renderDashboardCard(entryId: string) {
  const entry = DASHBOARD_MANIFEST.find((item) => item.id === entryId);

  if (!entry) {
    throw new Error(`Dashboard entry ${entryId} not found`);
  }

  return render(
    <MemoryRouter>
      <DashboardCard entry={entry} />
    </MemoryRouter>,
  );
}

describe("DashboardCard", () => {
  it("renders enabled cards as navigable links with icon, name, and description", () => {
    const enabledEntry = DASHBOARD_MANIFEST.find((entry) => entry.enabled);

    if (!enabledEntry) {
      throw new Error("Expected at least one enabled dashboard entry");
    }

    renderDashboardCard(enabledEntry.id);

    const card = screen.getByTestId(`dashboard-card-root-${enabledEntry.id}`);

    expect(within(card).getByTestId(`dashboard-card-icon-${enabledEntry.id}`)).toBeInTheDocument();
    expect(within(card).getByText(enabledEntry.name)).toBeInTheDocument();
    expect(within(card).getByText(enabledEntry.description)).toBeInTheDocument();
    expect(within(card).getByTestId(`dashboard-card-link-${enabledEntry.id}`)).toHaveAttribute(
      "href",
      enabledEntry.route,
    );
    expect(within(card).queryByText("Em breve")).not.toBeInTheDocument();
  });

  it('renders disabled cards with an "Em breve" badge and without navigation', () => {
    const disabledEntry = DASHBOARD_MANIFEST.find((entry) => !entry.enabled);

    if (!disabledEntry) {
      throw new Error("Expected at least one disabled dashboard entry");
    }

    renderDashboardCard(disabledEntry.id);

    const card = screen.getByTestId(`dashboard-card-root-${disabledEntry.id}`);

    expect(within(card).getByTestId(`dashboard-card-icon-${disabledEntry.id}`)).toBeInTheDocument();
    expect(within(card).getByText(disabledEntry.name)).toBeInTheDocument();
    expect(within(card).getByText(disabledEntry.description)).toBeInTheDocument();
    expect(within(card).getByText("Em breve")).toBeInTheDocument();
    expect(within(card).queryByRole("link")).not.toBeInTheDocument();
    expect(screen.queryByTestId(`dashboard-card-link-${disabledEntry.id}`)).not.toBeInTheDocument();
  });
});
