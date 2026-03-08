import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { KpiCard } from "../KpiCard";

describe("KpiCard", () => {
  it("renders icon, primary value, secondary value, and helper text", () => {
    render(
      <KpiCard
        title="Base Total"
        value="1.234"
        subtitle="Leads no filtro aplicado."
        helperText="Atualizado agora"
        icon={<span data-testid="kpi-icon">icon</span>}
      />,
    );

    expect(screen.getByText("Base Total")).toBeInTheDocument();
    expect(screen.getByText("1.234")).toBeInTheDocument();
    expect(screen.getByText("Leads no filtro aplicado.")).toBeInTheDocument();
    expect(screen.getByText("Atualizado agora")).toBeInTheDocument();
    expect(screen.getByTestId("kpi-icon")).toBeInTheDocument();
  });

  it("renders normalized coverage indicator when progress is provided", () => {
    render(
      <KpiCard
        title="Clientes BB"
        value="234"
        subtitle="Percentual da base: 40,0%"
        icon={<span>icon</span>}
        progressValue={135}
        progressLabel="Cobertura BB"
      />,
    );

    expect(screen.getByText("Cobertura BB")).toBeInTheDocument();
    expect(screen.getByText("100.0%")).toBeInTheDocument();
  });

  it("renders optional trend information", () => {
    render(
      <KpiCard
        title="Eventos"
        value="8"
        subtitle="Eventos retornados para os filtros aplicados."
        icon={<span>icon</span>}
        trend={{ direction: "up", label: "Tendencia", value: "5,0%" }}
      />,
    );

    expect(screen.getByText("Tendencia")).toBeInTheDocument();
    expect(screen.getByText("+")).toBeInTheDocument();
    expect(screen.getByText("5,0%")).toBeInTheDocument();
  });
});
