import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MinimalFooter from "../MinimalFooter";

describe("MinimalFooter", () => {
  it("renderiza tagline fixa e link de privacidade", () => {
    render(
      <MinimalFooter
        tagline="Banco do Brasil. Pra tudo que voce imaginar."
        textColor="rgba(255, 255, 255, 0.75)"
        privacyPolicyUrl="https://www.bb.com.br/site/privacidade-e-lgpd/"
      />,
    );

    expect(screen.getByText("Banco do Brasil. Pra tudo que voce imaginar.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Politica de privacidade e LGPD/i })).toHaveAttribute(
      "href",
      "https://www.bb.com.br/site/privacidade-e-lgpd/",
    );
  });

  it("aplica variant body2 nos dois elementos textuais", () => {
    render(
      <MinimalFooter
        tagline="Banco do Brasil. Pra tudo que voce imaginar."
        textColor="rgba(255, 255, 255, 0.75)"
        privacyPolicyUrl="https://www.bb.com.br/site/privacidade-e-lgpd/"
      />,
    );

    expect(screen.getByTestId("minimal-footer-tagline")).toHaveClass("MuiTypography-body2");
    expect(screen.getByTestId("minimal-footer-link")).toHaveClass("MuiTypography-body2");
  });

  it("não renderiza img nem svg", () => {
    const { container } = render(
      <MinimalFooter
        tagline="Banco do Brasil. Pra tudo que voce imaginar."
        textColor="rgba(255, 255, 255, 0.75)"
        privacyPolicyUrl="https://www.bb.com.br/site/privacidade-e-lgpd/"
      />,
    );

    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("svg")).toBeNull();
  });

  it("aplica a cor recebida por prop no container do rodape", () => {
    render(
      <MinimalFooter
        tagline="Banco do Brasil. Pra tudo que voce imaginar."
        textColor="rgba(51, 51, 189, 0.75)"
        privacyPolicyUrl="https://www.bb.com.br/site/privacidade-e-lgpd/"
      />,
    );

    expect(screen.getByTestId("minimal-footer")).toHaveStyle({ color: "rgba(51, 51, 189, 0.75)" });
  });
});
