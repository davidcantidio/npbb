import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import LegacyLeadStepRedirect from "../leads/LegacyLeadStepRedirect";

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{`${location.pathname}${location.search}`}</div>;
}

function renderRedirect(initialEntry: string, step: "mapping" | "pipeline") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/leads/mapeamento" element={<LegacyLeadStepRedirect step={step} />} />
        <Route path="/leads/pipeline" element={<LegacyLeadStepRedirect step={step} />} />
        <Route path="/leads/importar" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("LegacyLeadStepRedirect", () => {
  it("redirects the legacy mapping route to the canonical shell", () => {
    renderRedirect("/leads/mapeamento?batch_id=10", "mapping");

    expect(screen.getByTestId("location")).toHaveTextContent(
      "/leads/importar?step=mapping&batch_id=10",
    );
  });

  it("redirects the legacy pipeline route to the canonical shell", () => {
    renderRedirect("/leads/pipeline?batch_id=11", "pipeline");

    expect(screen.getByTestId("location")).toHaveTextContent(
      "/leads/importar?step=pipeline&batch_id=11",
    );
  });
});
