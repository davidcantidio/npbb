import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { CoverageBanner } from "../CoverageBanner";

describe("CoverageBanner", () => {
  it("does not render when coverage is at or above the warning threshold", () => {
    const { container } = render(<CoverageBanner coverage={80} />);

    expect(container).toBeEmptyDOMElement();
  });

  it("renders the warning copy with operator action in the consolidated banner", () => {
    render(<CoverageBanner coverage={65} />);

    expect(screen.getByTestId("coverage-banner-warning-default")).toBeInTheDocument();
    expect(
      screen.getByText("Dados parcialmente disponiveis. Realize o cruzamento completo com a base do Banco."),
    ).toBeInTheDocument();
  });

  it("renders the consolidated danger copy for the default banner", () => {
    render(<CoverageBanner coverage={12} />);

    expect(screen.getByTestId("coverage-banner-danger-default")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Dados de vinculo BB indisponiveis neste recorte - realize o cruzamento com a base de dados do Banco.",
      ),
    ).toBeInTheDocument();
  });

  it("renders the event danger copy for the compact banner", () => {
    render(<CoverageBanner coverage={12} variant="compact" scope="event" />);

    expect(screen.getByTestId("coverage-banner-danger-compact")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Dados de vinculo BB indisponiveis para este evento - realize o cruzamento com a base de dados do Banco.",
      ),
    ).toBeInTheDocument();
  });

  it("shows dismiss control only for the default variant", async () => {
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    const { rerender } = render(<CoverageBanner coverage={65} dismissible onDismiss={onDismiss} />);

    await user.click(screen.getByRole("button", { name: /close/i }));
    expect(onDismiss).toHaveBeenCalledTimes(1);

    rerender(<CoverageBanner coverage={65} variant="compact" dismissible onDismiss={onDismiss} />);

    expect(screen.queryByRole("button", { name: /close/i })).not.toBeInTheDocument();
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});
