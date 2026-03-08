import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { InfoTooltip } from "../InfoTooltip";

describe("InfoTooltip", () => {
  it("is focusable and exposes tooltip content", async () => {
    const user = userEvent.setup();

    render(
      <InfoTooltip
        label="Cobertura BB"
        description="Percentual de leads com informação de vínculo BB disponível"
      />,
    );

    const trigger = screen.getByRole("button", { name: /saiba mais sobre cobertura bb/i });
    await user.tab();
    expect(trigger).toHaveFocus();
    expect(trigger).toHaveTextContent("ℹ️");

    const tooltip = await screen.findByRole("tooltip");
    expect(tooltip).toHaveTextContent("Percentual de leads com informação de vínculo BB disponível");
  });
});
