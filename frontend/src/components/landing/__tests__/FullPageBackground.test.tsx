import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { LandingPageData } from "../../../services/landing_public";
import { getTemplateBackgroundGradient, getTemplateOverlayOpacity } from "../landingStyle";
import FullPageBackground from "../FullPageBackground";

const EXPECTED_TEMPLATE_GRADIENTS = [
  ["corporativo", "linear-gradient(135deg, #1A237E 0%, #3333BD 60%, #465EFF 100%)"],
  ["esporte_convencional", "linear-gradient(160deg, #3333BD 0%, #1A237E 50%, #3333BD 100%)"],
  ["esporte_radical", "linear-gradient(145deg, #3333BD 0%, #FF6E91 55%, #FCFC30 100%)"],
  ["evento_cultural", "linear-gradient(150deg, #BDB6FF 0%, #E8E4FF 50%, #83FFEA 100%)"],
  ["show_musical", "linear-gradient(160deg, #0D0D1A 0%, #2D1B4E 50%, #4A1942 100%)"],
  ["tecnologia", "linear-gradient(135deg, #0D1B2E 0%, #0A2440 40%, #0B3340 100%)"],
  ["generico", "linear-gradient(150deg, #3333BD 0%, #465EFF 100%)"],
] as const;

function createLandingData(categoria: string): LandingPageData {
  return {
    ativacao_id: 1,
    ativacao: {
      id: 1,
      nome: "Stand Principal",
      descricao: "Descricao da ativacao",
      mensagem_qrcode: "Mensagem QR code",
    },
    evento: {
      id: 10,
      nome: "BB Summit 2026",
      cta_personalizado: null,
      descricao: "Descricao completa",
      descricao_curta: "Resumo",
      data_inicio: "2026-04-10",
      data_fim: "2026-04-12",
      cidade: "Brasilia",
      estado: "DF",
    },
    template: {
      categoria,
      tema: "Tema",
      mood: "mood",
      cta_text: "Quero participar",
      color_primary: "#3333BD",
      color_secondary: "#FCFC30",
      color_background: "#F7F8FF",
      color_text: "#111827",
      hero_layout: "split",
      cta_variant: "filled",
      graphics_style: "grid",
      tone_of_voice: "attention",
      cta_experiment_enabled: false,
      cta_variants: [],
    },
    formulario: {
      event_id: 10,
      ativacao_id: 1,
      submit_url: "/landing/ativacoes/1/submit",
      campos: [],
      campos_obrigatorios: [],
      campos_opcionais: [],
      mensagem_sucesso: "Ok",
      lgpd_texto: "LGPD",
      privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
    },
    marca: {
      tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
    },
    acesso: {
      landing_url: "https://npbb.example/landing/ativacoes/1",
      qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
      url_promotor: "https://npbb.example/landing/ativacoes/1",
    },
    gamificacoes: [],
  };
}

describe("FullPageBackground", () => {
  it.each(EXPECTED_TEMPLATE_GRADIENTS)("resolve o gradiente correto para template %s", (categoria, expectedGradient) => {
    const gradient = getTemplateBackgroundGradient(createLandingData(categoria));
    expect(gradient).toBe(expectedGradient);
  });

  it("usa fallback de gradiente para categoria desconhecida", () => {
    const gradient = getTemplateBackgroundGradient(createLandingData("desconhecida"));
    expect(gradient).toBe("linear-gradient(150deg, #3333BD 0%, #465EFF 100%)");
  });

  it("renderiza camada fixa cobrindo viewport e slot de children", () => {
    const { container } = render(
      <FullPageBackground data={createLandingData("corporativo")}>
        <div data-testid="background-child">conteudo</div>
      </FullPageBackground>,
    );

    expect(screen.getByTestId("background-child")).toBeInTheDocument();

    const backgroundLayer = screen.getByTestId("full-page-background-layer");
    expect(backgroundLayer).toHaveStyle({
      position: "fixed",
      inset: "0",
      width: "100vw",
      minHeight: "100vh",
      zIndex: "0",
    });

    const overlayLayer = screen.getByTestId("full-page-overlay-layer");
    expect(overlayLayer).toHaveStyle({
      position: "fixed",
      inset: "0",
      width: "100vw",
      minHeight: "100vh",
      pointerEvents: "none",
      zIndex: "1",
    });

    const contentLayer = screen.getByTestId("full-page-background-content");
    expect(contentLayer).toHaveStyle({
      position: "relative",
      zIndex: "2",
      minHeight: "100vh",
    });
    expect(container.querySelectorAll("img")).toHaveLength(0);
  });

  it.each([
    ["corporativo", 0.1],
    ["esporte_convencional", 0.1],
    ["esporte_radical", 0.15],
    ["evento_cultural", 0.12],
    ["show_musical", 0.2],
    ["tecnologia", 0.15],
    ["generico", 0.05],
  ])("resolve opacidade de overlay para %s", (categoria, expectedOpacity) => {
    const opacity = getTemplateOverlayOpacity(createLandingData(categoria));
    expect(opacity).toBe(expectedOpacity);
  });

  it("usa fallback de opacidade para categoria desconhecida", () => {
    const opacity = getTemplateOverlayOpacity(createLandingData("desconhecida"));
    expect(opacity).toBe(0.05);
  });
});
